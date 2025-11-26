import os
from datetime import datetime

import pandas as pd
import streamlit as st

from .core import (
    BASE_DIR,
    build_parecer_pdf_to_bytes,
    build_parecer_docx_to_bytes,
    merge_pdfs_bytes,
    registrar_parecer_log,
    carregar_candidatos,
    carregar_clientes,
    gerar_campos_via_openai,
    extract_text_from_pdf,
    carregar_vagas,
    carregar_vaga_candidatos,
)

# Diretório interno onde os pareceres ficam guardados no servidor
PARECER_DIR = os.path.join(BASE_DIR, "pareceres")


def _garantir_pasta_parecer():
    try:
        os.makedirs(PARECER_DIR, exist_ok=True)
    except Exception:
        # Se der erro, deixa seguir – o download ainda funciona pela memória
        pass


def run():
    st.header("📝 Parecer de Triagem")

    _garantir_pasta_parecer()

    # ----------------------------------------
    # Valores padrão em session_state
    # ----------------------------------------
    defaults = {
        "cliente": "",
        "cargo": "",
        "nome": "",
        "localidade": "",
        "idade": "",
        "pretensao": "",
        "linkedin": "",
        "resumo_profissional": "",
        "analise_perfil": "",
        "conclusao_texto": "",
        "id_candidato_selecionado": "",
        "id_vaga_selecionada": "",
        "cv_caminho_auto": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ----------------------------------------
    # 1) Vincular candidato + vaga automaticamente
    # ----------------------------------------
    st.subheader("Vínculos (candidato / vaga / cliente)")

    df_cand = carregar_candidatos()
    df_vagas = carregar_vagas()
    df_vinc = carregar_vaga_candidatos()

    id_candidato_escolhido = "(Nenhum)"

    col_v1, col_v2 = st.columns(2)

    with col_v1:
        if df_cand.empty:
            st.info("Nenhum candidato cadastrado ainda.")
        else:
            op_cand = {
                int(row["id_candidato"]): row["nome"]
                for _, row in df_cand.iterrows()
            }
            id_candidato_escolhido = st.selectbox(
                "Selecione um candidato:",
                options=["(Nenhum)"] + list(op_cand.keys()),
                format_func=lambda x: op_cand[x] if x != "(Nenhum)" else x,
                key="parecer_cand_sel",
            )

    with col_v2:
        # Vaga vinculada (se existir vínculo)
        id_vaga_escolhida = "(Nenhuma)"
        vaga_label = "(Nenhuma vaga vinculada)"

        if (
            df_vinc is not None
            and not df_vinc.empty
            and id_candidato_escolhido != "(Nenhum)"
        ):
            # vínculos desse candidato
            vinc_cand = df_vinc[df_vinc["id_candidato"] == str(id_candidato_escolhido)]
            if not vinc_cand.empty and (df_vagas is not None and not df_vagas.empty):
                # pega última vaga vinculada
                ultima = vinc_cand.sort_values("data_vinculo").iloc[-1]
                id_vaga_escolhida = ultima["id_vaga"]

                row_v = df_vagas[df_vagas["id_vaga"] == str(id_vaga_escolhida)]
                if not row_v.empty:
                    rv = row_v.iloc[0]
                    vaga_label = f"{rv['nome_cliente']} - {rv['cargo']}"
                    st.info(f"Vaga vinculada automaticamente: **{vaga_label}**")
                    # guarda em session_state
                    st.session_state["id_vaga_selecionada"] = str(id_vaga_escolhida)
        if id_vaga_escolhida == "(Nenhuma)":
            st.info("Nenhuma vaga vinculada automaticamente para este candidato.")

    # Botão para carregar todos os dados relacionados (candidato + vaga + CV)
    if id_candidato_escolhido != "(Nenhum)":
        if st.button("📥 Carregar dados do candidato / vaga / CV"):
            row_c = df_cand[df_cand["id_candidato"] == str(id_candidato_escolhido)].iloc[0]

            st.session_state["nome"] = row_c["nome"]
            st.session_state["idade"] = str(row_c.get("idade", ""))
            st.session_state["localidade"] = row_c.get("cidade", "")
            st.session_state["linkedin"] = row_c.get("linkedin", "")
            st.session_state["id_candidato_selecionado"] = str(row_c["id_candidato"])

            # CV vinculado ao candidato
            cv_caminho = row_c.get("cv_arquivo", "") or ""
            if cv_caminho and os.path.isfile(cv_caminho):
                st.session_state["cv_caminho_auto"] = cv_caminho
            else:
                st.session_state["cv_caminho_auto"] = ""

            # Se tiver vaga vinculada, preenche cliente e cargo
            id_vaga_selecionada = st.session_state.get("id_vaga_selecionada", "")
            if id_vaga_selecionada and (df_vagas is not None and not df_vagas.empty):
                row_v = df_vagas[df_vagas["id_vaga"] == str(id_vaga_selecionada)]
                if not row_v.empty:
                    rv = row_v.iloc[0]
                    st.session_state["cliente"] = rv.get("nome_cliente", "")
                    st.session_state["cargo"] = rv.get("cargo", "")

            st.success("Dados de candidato / vaga / CV carregados no formulário.")

    st.markdown("---")

    # ----------------------------------------
    # 2) Vincular cliente manualmente (opcional)
    # ----------------------------------------
    st.subheader("Vincular / ajustar cliente (opcional)")
    df_cli = carregar_clientes()
    if df_cli.empty:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        op_cli = {int(row["id_cliente"]): row["nome_cliente"] for _, row in df_cli.iterrows()}
        id_cli_sel = st.selectbox(
            "Selecionar cliente para sobrescrever ou ajustar:",
            options=["(Nenhum)"] + list(op_cli.keys()),
            format_func=lambda x: op_cli[x] if x != "(Nenhum)" else x,
            key="parecer_cli_sel",
        )
        if id_cli_sel != "(Nenhum)":
            if st.button("🔁 Usar este cliente no formulário"):
                st.session_state["cliente"] = op_cli[id_cli_sel]
                st.success("Cliente atualizado no formulário.")

    st.markdown("---")

    # ----------------------------------------
    # 3) IA opcional
    # ----------------------------------------
    with st.expander("🤖 IA - Preencher campos automaticamente (opcional)", expanded=False):
        col_ia, _ = st.columns(2)
        with col_ia:
            if st.button("🔌 Testar conexão OpenAI"):
                from .core import get_openai_client
                client = get_openai_client()
                if not client:
                    st.error("OpenAI não configurado (biblioteca ou OPENAI_API_KEY).")
                else:
                    try:
                        _ = client.responses.create(model="gpt-4.1-mini", input="OK?")
                        st.success("Conexão OK.")
                    except Exception as e:
                        st.error(f"Erro na conexão: {e}")

        uploaded_pdf = st.file_uploader("📎 PDF do currículo (opcional)", type=["pdf"], key="parecer_pdf_ia")
        obs_ia = st.text_area("Observações para IA (opcional)", height=100)

        if st.button("✨ Gerar campos via IA"):
            if not uploaded_pdf and not obs_ia.strip():
                st.warning("Envie um PDF ou escreva observações para usar a IA.")
            else:
                try:
                    texto_pdf = extract_text_from_pdf(uploaded_pdf) if uploaded_pdf else ""
                    texto_base = (texto_pdf or "") + "\n\n" + (obs_ia or "")
                    nome_ai, resumo_ai, analise_ai, concl_ai = gerar_campos_via_openai(texto_base)
                    if nome_ai:
                        st.session_state["nome"] = nome_ai
                    if resumo_ai:
                        st.session_state["resumo_profissional"] = resumo_ai
                    if analise_ai:
                        st.session_state["analise_perfil"] = analise_ai
                    if concl_ai:
                        st.session_state["conclusao_texto"] = concl_ai
                    st.success("Campos preenchidos pela IA.")
                except Exception as e:
                    st.error(f"Erro ao usar IA: {e}")

    st.markdown("---")

    # ----------------------------------------
    # 4) Formulário do parecer
    # ----------------------------------------
    st.subheader("Formulário do parecer")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Cliente", key="cliente")
        st.text_input("Nome do candidato", key="nome")
        st.text_input("Idade", key="idade")
    with col2:
        st.text_input("Cargo", key="cargo")
        st.text_input("Localidade", key="localidade")
        st.text_input("Pretensão Salarial (ex.: R$ 4.500,00)", key="pretensao")

    st.text_input("LinkedIn (opcional)", key="linkedin")

    st.subheader("Resumo profissional")
    st.text_area(
        "Resumo profissional",
        key="resumo_profissional",
        height=150,
        placeholder="Descreva de forma objetiva o perfil profissional do candidato...",
    )

    st.subheader("Análise de perfil")
    st.text_area(
        "Análise de perfil",
        key="analise_perfil",
        height=150,
        placeholder="Postura, comunicação, senioridade, aderência à vaga...",
    )

    st.subheader("Conclusão")
    st.text_area(
        "Conclusão",
        key="conclusao_texto",
        height=120,
        placeholder="Conclusão geral e recomendação...",
    )

    st.markdown("---")

    # ----------------------------------------
    # 5) Arquivos e saída
    # ----------------------------------------
    st.subheader("Arquivos e saída")

    formato = st.radio("Formato do parecer", ["PDF", "DOCX"], index=0, horizontal=True)

    # Info sobre onde a cópia interna será salva
    st.markdown(
        f"📁 **Cópias internas dos pareceres serão salvas em:** `{PARECER_DIR}`"
    )

    # CV automático do candidato, se existir
    cv_auto = st.session_state.get("cv_caminho_auto", "") or ""
    usar_cv_auto = False
    if cv_auto and os.path.isfile(cv_auto):
        st.markdown(f"📎 **CV vinculado ao candidato:** `{os.path.basename(cv_auto)}`")
        usar_cv_auto = st.checkbox("Anexar automaticamente este CV ao parecer (recomendado)", value=True)
    else:
        st.info("Nenhum CV vinculado automaticamente ao candidato. Você pode anexar manualmente no histórico, se preferir.")
        usar_cv_auto = False

    st.markdown(
        "> 💡 Para salvar o arquivo em uma pasta específica da **sua máquina**, "
        "use o botão de download abaixo depois de gerar o parecer e escolha o local na janela do navegador."
    )

    # Nome base do arquivo
    nome_para_base = st.session_state["nome"] if st.session_state["nome"] else "Candidato"
    nome_base = f"Parecer_{nome_para_base.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"

    if st.button("💾 Gerar parecer e registrar histórico"):
        nome = st.session_state["nome"]
        if not nome.strip():
            st.error("Informe o nome do candidato.")
            return

        try:
            _garantir_pasta_parecer()
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cliente = st.session_state["cliente"]
            cargo = st.session_state["cargo"]
            localidade = st.session_state["localidade"]
            idade = st.session_state["idade"]
            pretensao = st.session_state["pretensao"]
            linkedin = st.session_state["linkedin"]
            resumo_prof = st.session_state["resumo_profissional"]
            analise_prof = st.session_state["analise_perfil"]
            conclusao_txt = st.session_state["conclusao_texto"]
            id_cand_log = st.session_state.get("id_candidato_selecionado", "")
            # id_vaga_log = st.session_state.get("id_vaga_selecionada", "")

            if formato == "PDF":
                parecer_bytes = build_parecer_pdf_to_bytes(
                    cliente, cargo, nome, localidade, idade, pretensao,
                    resumo_prof, analise_prof, conclusao_txt, linkedin
                )

                # Anexa CV automático se houver e se marcado
                if usar_cv_auto and cv_auto and os.path.isfile(cv_auto):
                    parecer_bytes = merge_pdfs_bytes(parecer_bytes, cv_auto)

                filename = nome_base + ".pdf"
                caminho_final = os.path.join(PARECER_DIR, filename)

                # Salva cópia interna
                with open(caminho_final, "wb") as f:
                    f.write(parecer_bytes)

                # Registra no log
                registrar_parecer_log(
                    data_hora=data_hora,
                    cliente=cliente,
                    cargo=cargo,
                    nome=nome,
                    localidade=localidade,
                    idade=idade,
                    pretensao=pretensao,
                    linkedin=linkedin,
                    resumo_profissional=resumo_prof,
                    analise_perfil=analise_prof,
                    conclusao_texto=conclusao_txt,
                    formato="PDF",
                    caminho_arquivo=caminho_final,
                    id_candidato=id_cand_log,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                st.success(f"Parecer PDF gerado e salvo em: {caminho_final}")
                st.download_button(
                    "⬇️ Baixar PDF para minha máquina",
                    data=parecer_bytes,
                    file_name=filename,
                    mime="application/pdf",
                )

            else:  # DOCX
                parecer_bytes = build_parecer_docx_to_bytes(
                    cliente, cargo, nome, localidade, idade, pretensao,
                    resumo_prof, analise_prof, conclusao_txt, linkedin
                )
                filename = nome_base + ".docx"
                caminho_final = os.path.join(PARECER_DIR, filename)

                with open(caminho_final, "wb") as f:
                    f.write(parecer_bytes)

                registrar_parecer_log(
                    data_hora=data_hora,
                    cliente=cliente,
                    cargo=cargo,
                    nome=nome,
                    localidade=localidade,
                    idade=idade,
                    pretensao=pretensao,
                    linkedin=linkedin,
                    resumo_profissional=resumo_prof,
                    analise_perfil=analise_prof,
                    conclusao_texto=conclusao_txt,
                    formato="DOCX",
                    caminho_arquivo=caminho_final,
                    id_candidato=id_cand_log,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                st.success(f"Parecer DOCX gerado e salvo em: {caminho_final}")
                st.download_button(
                    "⬇️ Baixar DOCX para minha máquina",
                    data=parecer_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

        except Exception as e:
            st.error(f"Erro ao gerar parecer: {e}")



