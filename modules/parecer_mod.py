import os
from datetime import datetime

import streamlit as st
import pandas as pd

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
    carregar_pareceres_log,
    LOG_PAR,
)


def run():
    st.header("📝 Parecer de Triagem")

    # session_state default
    for campo, padrao in {
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
    }.items():
        if campo not in st.session_state:
            st.session_state[campo] = padrao

    # =========================================================
    # VINCULAR CANDIDATO (APENAS COM VÍNCULO + VAGA ABERTA/EM ANDAMENTO)
    # =========================================================
    st.subheader("Vincular a um candidato (opcional)")

    df_cand = carregar_candidatos()
    df_vagas = carregar_vagas()
    df_vinc = carregar_vaga_candidatos()
    id_candidato_escolhido = ""

    # Situações em que não conseguimos filtrar
    if df_cand.empty:
        st.info("Nenhum candidato cadastrado ainda.")
    elif df_vagas.empty or df_vinc.empty:
        st.info("Nenhuma vaga vinculada encontrada para montar a lista de candidatos.")
    else:
        # Vagas com status Aberta ou Em andamento
        df_vagas_validas = df_vagas[
            df_vagas["status"].isin(["Aberta", "Em andamento"])
        ].copy()

        if df_vagas_validas.empty:
            st.info("Não há vagas em status 'Aberta' ou 'Em andamento'.")
        else:
            # vínculos apenas dessas vagas
            ids_vagas_validas = set(df_vagas_validas["id_vaga"].astype(str).tolist())
            df_vinc_validos = df_vinc[
                df_vinc["id_vaga"].isin(ids_vagas_validas)
            ].copy()

            if df_vinc_validos.empty:
                st.info(
                    "Não há candidatos vinculados a vagas em status 'Aberta' ou 'Em andamento'."
                )
            else:
                # candidatos provenientes desses vínculos
                ids_cand_validos = (
                    df_vinc_validos["id_candidato"].astype(str).unique().tolist()
                )

                df_cand_validos = df_cand[
                    df_cand["id_candidato"].astype(str).isin(ids_cand_validos)
                ].copy()

                if df_cand_validos.empty:
                    st.info(
                        "Nenhum candidato cadastrado corresponde aos vínculos encontrados."
                    )
                else:
                    # monta opções (id int -> descrição)
                    op_cand = {
                        int(row["id_candidato"]): f"{row['nome']} - {row['cidade']} - {row['telefone']}"
                        for _, row in df_cand_validos.iterrows()
                    }

                    id_candidato_escolhido = st.selectbox(
                        "Selecione um candidato:",
                        options=["(Nenhum)"] + list(op_cand.keys()),
                        format_func=lambda x: op_cand[x] if x != "(Nenhum)" else x,
                        key="parecer_cand_sel",
                    )

                    if (
                        id_candidato_escolhido != "(Nenhum)"
                        and st.button("Carregar dados do candidato")
                    ):
                        # linha do candidato selecionado
                        row = df_cand_validos[
                            df_cand_validos["id_candidato"]
                            == str(id_candidato_escolhido)
                        ].iloc[0]

                        st.session_state["nome"] = row["nome"]
                        st.session_state["idade"] = str(row["idade"])
                        st.session_state["localidade"] = row["cidade"]
                        st.session_state["linkedin"] = row.get("linkedin", "")
                        st.session_state["id_candidato_selecionado"] = str(
                            row["id_candidato"]
                        )

                        st.success("Dados do candidato carregados.")

    # =========================================================
    # VINCULAR CLIENTE (OPCIONAL)
    # =========================================================
    st.subheader("Vincular a um cliente (opcional)")
    df_cli = carregar_clientes()
    if df_cli.empty:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        op_cli = {
            int(row["id_cliente"]): row["nome_cliente"] for _, row in df_cli.iterrows()
        }
        id_cli_sel = st.selectbox(
            "Selecione o cliente:",
            options=["(Nenhum)"] + list(op_cli.keys()),
            format_func=lambda x: op_cli[x] if x != "(Nenhum)" else x,
            key="parecer_cli_sel",
        )
        if id_cli_sel != "(Nenhum)" and st.button("Carregar nome do cliente"):
            st.session_state["cliente"] = op_cli[id_cli_sel]
            st.success("Cliente carregado no formulário.")

    st.markdown("---")

    # =========================================================
    # IA OPCIONAL
    # =========================================================
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
                        _ = client.responses.create(
                            model="gpt-4.1-mini", input="OK?"
                        )
                        st.success("Conexão OK.")
                    except Exception as e:
                        st.error(f"Erro na conexão: {e}")

        uploaded_pdf = st.file_uploader(
            "📎 PDF do currículo (opcional)",
            type=["pdf"],
            key="parecer_pdf_ia",
        )
        obs_ia = st.text_area("Observações para IA (opcional)", height=100)

        if st.button("✨ Gerar campos via IA"):
            if not uploaded_pdf and not obs_ia.strip():
                st.warning("Envie um PDF ou escreva observações para usar a IA.")
            else:
                try:
                    texto_pdf = (
                        extract_text_from_pdf(uploaded_pdf) if uploaded_pdf else ""
                    )
                    texto_base = (texto_pdf or "") + "\n\n" + (obs_ia or "")
                    (
                        nome_ai,
                        resumo_ai,
                        analise_ai,
                        concl_ai,
                    ) = gerar_campos_via_openai(texto_base)
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
    st.subheader("Formulário do parecer")

    # =========================================================
    # CAMPOS PRINCIPAIS
    # =========================================================
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Cliente", key="cliente")
        st.text_input("Nome do candidato", key="nome")
        st.text_input("Idade", key="idade")
    with col2:
        st.text_input("Cargo", key="cargo")
        st.text_input("Localidade", key="localidade")
        st.text_input(
            "Pretensão Salarial (ex.: R$ 4.500,00)", key="pretensao"
        )

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
    st.subheader("Arquivos e saída")

    formato = st.radio("Formato do parecer", ["PDF", "DOCX"], index=0)

    pasta_cv = st.text_input("Pasta com currículos (PDF)", value=BASE_DIR)
    lista_cv = []
    if os.path.isdir(pasta_cv):
        lista_cv = [
            f for f in os.listdir(pasta_cv) if f.lower().endswith(".pdf")
        ]

    selected_cv = st.selectbox(
        "Anexar currículo PDF ao parecer (opcional)",
        ["(Não anexar)"] + lista_cv,
    )

    output_folder = st.text_input(
        "Pasta de saída dos pareceres", value=BASE_DIR
    )

    nome_para_base = (
        st.session_state["nome"] if st.session_state["nome"] else "Candidato"
    )
    nome_base = f"Parecer_{nome_para_base.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"

    # =========================================================
    # GERAR PARECER
    # =========================================================
    if st.button("💾 Gerar parecer e registrar histórico"):
        nome = st.session_state["nome"]
        if not nome.strip():
            st.error("Informe o nome do candidato.")
            return

        try:
            os.makedirs(output_folder, exist_ok=True)
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
            id_cand_log = st.session_state.get(
                "id_candidato_selecionado", ""
            )

            if formato == "PDF":
                parecer_bytes = build_parecer_pdf_to_bytes(
                    cliente,
                    cargo,
                    nome,
                    localidade,
                    idade,
                    pretensao,
                    resumo_prof,
                    analise_prof,
                    conclusao_txt,
                    linkedin,
                )
                if selected_cv != "(Não anexar)":
                    resume_path = os.path.join(pasta_cv, selected_cv)
                    parecer_bytes = merge_pdfs_bytes(
                        parecer_bytes, resume_path
                    )

                filename = nome_base + ".pdf"
                caminho_final = os.path.join(output_folder, filename)
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
                    formato="PDF",
                    caminho_arquivo=caminho_final,
                    id_candidato=id_cand_log,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                st.success(f"Parecer gerado: {caminho_final}")
                st.download_button(
                    "⬇️ Baixar PDF",
                    data=parecer_bytes,
                    file_name=filename,
                    mime="application/pdf",
                )

            else:  # DOCX
                parecer_bytes = build_parecer_docx_to_bytes(
                    cliente,
                    cargo,
                    nome,
                    localidade,
                    idade,
                    pretensao,
                    resumo_prof,
                    analise_prof,
                    conclusao_txt,
                    linkedin,
                )
                filename = nome_base + ".docx"
                caminho_final = os.path.join(output_folder, filename)
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

                st.success(f"Parecer gerado: {caminho_final}")
                st.download_button(
                    "⬇️ Baixar DOCX",
                    data=parecer_bytes,
                    file_name=filename,
                    mime=(
                        "application/"
                        "vnd.openxmlformats-officedocument.wordprocessingml.document"
                    ),
                )

        except Exception as e:
            st.error(f"Erro ao gerar parecer: {e}")




