from datetime import datetime
import os

import pandas as pd
import streamlit as st

from .core import CV_DIR, montar_link_whatsapp
from .database import (
    listar_candidatos,
    inserir_candidato,
    obter_candidato,
    atualizar_candidato,
)


def render_tabela_html(df, columns, headers):
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    html = ["<table>"]
    html.append("<thead><tr>")
    for h in headers:
        html.append(f"<th>{h}</th>")
    html.append("</tr></thead><tbody>")

    for _, row in df[columns].iterrows():
        html.append("<tr>")
        for col in columns:
            html.append(f"<td>{row[col]}</td>")
        html.append("</tr>")

    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)


def run():
    st.header("👤 Gestão de Candidatos")

    if "cand_modo" not in st.session_state:
        st.session_state["cand_modo"] = "Listar"

    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("📋 Listar", use_container_width=True, key="btn_cand_listar"):
            st.session_state["cand_modo"] = "Listar"
    with colB:
        if st.button("➕ Novo", use_container_width=True, key="btn_cand_novo"):
            st.session_state["cand_modo"] = "Novo"
            st.session_state["cand_edit_id"] = None
    with colC:
        if st.button("✏️ Editar", use_container_width=True, key="btn_cand_editar"):
            st.session_state["cand_modo"] = "Editar"

    st.markdown("---")
    modo = st.session_state["cand_modo"]

    # =========================
    # LISTAR
    # =========================
    if modo == "Listar":
        st.subheader("📋 Candidatos cadastrados")

        dados = listar_candidatos()
        if not dados:
            st.info("Nenhum candidato cadastrado.")
            return

        df = pd.DataFrame(dados).fillna("")
        df["whatsapp"] = df["telefone"].apply(montar_link_whatsapp)

        render_tabela_html(
            df,
            columns=["id_candidato", "nome", "cidade", "telefone", "pretensao", "linkedin", "caminho_cv"],
            headers=["ID", "Nome", "Cidade", "Telefone", "Pretensão / Cargo", "LinkedIn", "CV (caminho)"],
        )
        return

    # =========================
    # NOVO
    # =========================
    if modo == "Novo":
        st.subheader("➕ Novo candidato")

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo")
            idade = st.text_input("Idade (opcional)")
            cidade = st.text_input("Cidade")
            telefone = st.text_input("Telefone")
        with col2:
            email = st.text_input("E-mail")
            linkedin = st.text_input("LinkedIn (opcional)")
            pretensao = st.text_input("Cargo / Pretensão (opcional)")
            data_cadastro = datetime.now().strftime("%Y-%m-%d")

        cv_file = st.file_uploader("Anexar CV (PDF)", type=["pdf"], key="cand_novo_cv")

        if st.button("💾 Salvar candidato", use_container_width=True, key="btn_salvar_cand_novo"):
            if not nome.strip():
                st.error("Informe o nome do candidato.")
                return

            novo_id = inserir_candidato(
                nome=nome.strip(),
                idade=idade.strip() or None,
                cidade=cidade.strip() or None,
                telefone=telefone.strip() or None,
                email=email.strip() or None,
                linkedin=linkedin.strip() or None,
                pretensao=pretensao.strip() or None,
                caminho_cv=None,
            )

            caminho_cv_final = None
            if cv_file is not None:
                os.makedirs(CV_DIR, exist_ok=True)
                filename = f"cv_{novo_id}_{cv_file.name}"
                caminho_cv_final = os.path.join(CV_DIR, filename)
                with open(caminho_cv_final, "wb") as f:
                    f.write(cv_file.read())
                atualizar_candidato(
                    id_candidato=novo_id,
                    nome=nome.strip(),
                    idade=idade.strip() or None,
                    cidade=cidade.strip() or None,
                    telefone=telefone.strip() or None,
                    email=email.strip() or None,
                    linkedin=linkedin.strip() or None,
                    pretensao=pretensao.strip() or None,
                    caminho_cv=caminho_cv_final,
                )

            st.success(f"Candidato cadastrado (ID {novo_id}).")
            st.session_state["cand_modo"] = "Listar"
            st.experimental_rerun()
        return

    # =========================
    # EDITAR
    # =========================
    if modo == "Editar":
        st.subheader("✏️ Editar candidato")

        dados = listar_candidatos()
        if not dados:
            st.info("Nenhum candidato para editar.")
            return

        df = pd.DataFrame(dados).fillna("")

        opcoes = {int(r["id_candidato"]): f"{r['id_candidato']} - {r['nome']}" for _, r in df.iterrows()}
        id_sel = st.selectbox(
            "Selecione o candidato:",
            list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
            key="cand_edit_select",
        )

        cand = obter_candidato(int(id_sel))
        if not cand:
            st.error("Candidato não encontrado.")
            return

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo", value=cand.get("nome", ""))
            idade = st.text_input("Idade", value=str(cand.get("idade") or ""))
            cidade = st.text_input("Cidade", value=cand.get("cidade", ""))
            telefone = st.text_input("Telefone", value=cand.get("telefone", ""))
        with col2:
            email = st.text_input("E-mail", value=cand.get("email", ""))
            linkedin = st.text_input("LinkedIn", value=cand.get("linkedin", ""))
            pretensao = st.text_input("Cargo / Pretensão", value=cand.get("pretensao", ""))

        st.markdown("**CV atual:**")
        caminho_cv_atual = cand.get("caminho_cv") or ""
        if caminho_cv_atual:
            st.code(caminho_cv_atual, language="bash")
        else:
            st.write("Nenhum CV anexado.")

        novo_cv = st.file_uploader("Substituir / anexar CV (PDF)", type=["pdf"], key="cand_edit_cv")

        if st.button("💾 Salvar alterações", use_container_width=True, key="btn_salvar_cand_edit"):
            if not nome.strip():
                st.error("Informe o nome.")
                return

            caminho_cv_final = caminho_cv_atual
            if novo_cv is not None:
                os.makedirs(CV_DIR, exist_ok=True)
                filename = f"cv_{id_sel}_{novo_cv.name}"
                caminho_cv_final = os.path.join(CV_DIR, filename)
                with open(caminho_cv_final, "wb") as f:
                    f.write(novo_cv.read())

            atualizar_candidato(
                id_candidato=int(id_sel),
                nome=nome.strip(),
                idade=idade.strip() or None,
                cidade=cidade.strip() or None,
                telefone=telefone.strip() or None,
                email=email.strip() or None,
                linkedin=linkedin.strip() or None,
                pretensao=pretensao.strip() or None,
                caminho_cv=caminho_cv_final,
            )

            st.success("Candidato atualizado com sucesso.")
            st.session_state["cand_modo"] = "Listar"
            st.experimental_rerun()
        return
