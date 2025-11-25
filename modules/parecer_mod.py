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


# ============================================================
# PARECER APP COMPLETO
# ============================================================

def run():
    st.header("📝 Parecer de Triagem")

    # defaults no session_state
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
        "cv_arquivo": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    # ================================
    # SELEÇÃO DE CANDIDATO
    # ================================
    st.subheader("👤 Vincular a um candidato (opcional)")

    df_cand = carregar_candidatos()
    if df_cand.empty:
        st.info("Nenhum candidato cadastrado.")
        id_candidato_escolhido = "(Nenhum)"
    else:
        opcoes_cand = {
            int(r["id_candidato"]): r["nome"]
            for _, r in df_cand.iterrows()
        }

        id_candidato_escolhido = st.selectbox(
            "Selecione um candidato:",
            ["(Nenhum)"] + list(opcoes_cand.keys()),
            format_func=lambda x: opcoes_cand[x] if x != "(Nenhum)" else x,
            key="cand_sel",
        )

        # BOTÃO CARREGAR DADOS COMPLETOS
        if id_candidato_escolhido != "(Nenhum)" and st.button("🔄 Carregar dados completos"):
            # ============================================
            # 1) Carregar dados do candidato
            # ============================================
            row_cand = df_cand[df_cand["id_candidato"] == str(id_candidato_escolhido)]
            if row_cand.empty:
                st.error("Erro ao localizar candidato.")
                return

            row_cand = row_cand.iloc[0]

            st.session_state["nome"] = row_cand["nome"]
            st.session_state["idade"] = str(row_cand.get("idade", ""))
            st.session_state["localidade"] = row_cand.get("cidade", "")
            st.session_state["pretensao"] = row_cand.get("pretensao", "")
            st.session_state["linkedin"] = row_cand.get("linkedin", "")
            st.session_state["id_candidato_selecionado"] = str(row_cand["id_candidato"])
            st.session_state["cv_arquivo"] = row_cand.get("cv_arquivo", "")

            # ============================================
            # 2) Carregar vaga vinculada automaticamente
            # ============================================
            df_vinc = carregar_vaga_candidatos()
            df_vagas = carregar_vagas()

            vaga_sel = None

            if not df_vinc.empty:
                vincs = df_vinc[df_vinc["id_candidato"] == str(id_candidato_escolhido)]
                if not vincs.empty:
                    vincs = vincs.sort_values("data_vinculo", ascending=False)
                    id_vaga = str(vincs.iloc[0]["id_vaga"])

                    row_vaga = df_vagas[df_vagas["id_vaga"] == id_vaga]
                    if not row_vaga.empty:
                        vaga_sel = row_vaga.iloc[0]

            if vaga_sel is not None:
                # Preencher dados da vaga
                st.session_state["cliente"] = vaga_sel.get("nome_cliente", "")
                st.session_state["cargo"] = vaga_sel.get("cargo", "")

                st.success(
                    f"Dados carregados: candidato + vaga vinculada ({vaga_sel['nome_cliente']} – {vaga_sel['cargo']})."
                )
            else:
                st.warning("Candidato sem vaga vinculada.")

    # ================================
    # SELEÇÃO DE CLIENTE MANUAL (opcional)
    # ================================

    st.subheader("🏢 Vincular a um cliente (opcional)")

    df_cli = carregar_clientes()
    if not df_cli.empty:
        op_cli = {int(r["id_cliente"]): r["nome_cliente"] for _, r in df_cli.iterrows()}

        id_cli = st.selectbox(
            "Selecione o cliente:",
            ["(Nenhum)"] + list(op_cli.keys()),
            format_func=lambda x: op_cli[x] if x != "(Nenhum)" else x,
            key="cli_sel",
        )
        if id_cli != "(Nenhum)" and st.button("📥 Preencher cliente"):
            st.session_state["cliente"] = op_cli[id_cli]
            st.success("Cliente carregado no formulário.")

    st.markdown("---")

    # ======================================================
    # IA
    # ======================================================

    with st.expander("🤖 IA - Preencher automaticamente", expanded=False):
        pdf_file = st.file_uploader("PDF do currículo", type=["pdf"], key="pdf_ia")
        obs = st.text_area("Observações para IA (opcional)", height=120)

        if st.button("✨ Preencher via IA"):
            if not pdf_file and not obs.strip():
                st.warning("Envie PDF ou escreva observações.")
            else:
                try:
                    texto_pdf = extract_text_from_pdf(pdf_file) if pdf_file else ""
                    base = texto_pdf + "\n\n" + obs
                    nome_ai, resumo_ai, analise_ai, concl_ai = gerar_campos_via_openai(base)

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
                    st.error(f"Erro IA: {e}")

    st.markdown("---")

    # ======================================================
    # FORMULÁRIO
    # ======================================================

    st.subheader("📝 Formulário do parecer")
    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Cliente", key="cliente")
        st.text_input("Nome do candidato", key="nome")
        st.text_input("Idade", key="idade")

    with col2:
        st.text_input("Cargo", key="cargo")
        st.text_input("Localidade", key="localidade")
        st.text_input("Pretensão Salarial", key="pretensao")

    st.text_input("LinkedIn", key="linkedin")

    st.subheader("Resumo profissional")
    st.text_area("Resumo profissional", key="resumo_profissional", height=150)

    st.subheader("Análise de perfil")
    st.text_area("Análise", key="analise_perfil", height=150)

    st.subheader("Conclusão")
    st.text_area("Conclusão", key="conclusao_texto", height=130)

    st.markdown("---")

    # ======================================================
    # CV VINDO DO CADASTRO
    # ======================================================

    cv_path = st.session_state.get("cv_arquivo", "")
    if cv_path:
        st.markdown("### 📎 CV do candidato (do cadastro)")
        try:
            with open(cv_path, "rb") as f:
                cv_bytes = f.read()
            st.download_button(
                "⬇️ Baixar CV",
                data=cv_bytes,
                file_name=os.path.basename(cv_path),
                mime="application/pdf",
            )
        except:
            st.warning("Não foi possível carregar o CV salvo no cadastro.")

    # ======================================================
    # SAÍDA
    # ======================================================

    formato = st.radio("Formato", ["PDF", "DOCX"], index=0)
    output_folder = st.text_input("Pasta de saída", value=BASE_DIR)

    # Nome do arquivo
    nome_base = (
        f"Parecer_{st.session_state['nome'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    )

    if st.button("💾 Gerar parecer"):
        nome = st.session_state["nome"]
        if not nome:
            st.error("Informe o nome.")
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
            resumo = st.session_state["resumo_profissional"]
            analise = st.session_state["analise_perfil"]
            conclusao = st.session_state["conclusao_texto"]
            id_cand_log = st.session_state["id_candidato_selecionado"]

            if formato == "PDF":
                parecer_bytes = build_parecer_pdf_to_bytes(
                    cliente, cargo, nome, localidade, idade,
                    pretensao, resumo, analise, conclusao, linkedin
                )

                filename = nome_base + ".pdf"
                caminho = os.path.join(output_folder, filename)
                with open(caminho, "wb") as f:
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
                    resumo_profissional=resumo,
                    analise_perfil=analise,
                    conclusao_texto=conclusao,
                    formato="PDF",
                    caminho_arquivo=caminho,
                    id_candidato=id_cand_log,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                st.success(f"Parecer salvo em: {caminho}")
                st.download_button("⬇️ Baixar PDF", data=parecer_bytes, file_name=filename)

            else:
                parecer_bytes = build_parecer_docx_to_bytes(
                    cliente, cargo, nome, localidade, idade,
                    pretensao, resumo, analise, conclusao, linkedin
                )

                filename = nome_base + ".docx"
                caminho = os.path.join(output_folder, filename)
                with open(caminho, "wb") as f:
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
                    resumo_profissional=resumo,
                    analise_perfil=analise,
                    conclusao_texto=conclusao,
                    formato="DOCX",
                    caminho_arquivo=caminho,
                    id_candidato=id_cand_log,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                st.success(f"Parecer salvo em: {caminho}")
                st.download_button("⬇️ Baixar DOCX", data=parecer_bytes, file_name=filename)

        except Exception as e:
            st.error(f"Erro ao gerar parecer: {e}")

