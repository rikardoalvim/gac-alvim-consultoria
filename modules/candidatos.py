import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from .core import (
    carregar_candidatos,
    registrar_candidato,
    CV_DIR,
    LOG_CAND,
    montar_link_whatsapp,
)


def render_tabela_html(df, columns, headers):
    """Renderiza DataFrame como tabela HTML no estilo glass."""
    if df.empty:
        st.info("Nenhum candidato cadastrado ainda.")
        return

    html = ["<table>"]
    # Cabeçalho
    html.append("<thead><tr>")
    for h in headers:
        html.append(f"<th>{h}</th>")
    html.append("</tr></thead>")

    # Corpo
    html.append("<tbody>")
    for _, row in df[columns].iterrows():
        html.append("<tr>")
        for col in columns:
            valor = row[col]
            html.append(f"<td>{valor}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")

    st.markdown("".join(html), unsafe_allow_html=True)


def run():
    st.header("👤 Cadastro de Candidatos")

    # Garante diretório de CV
    os.makedirs(CV_DIR, exist_ok=True)

    # Controle de modo
    if "cand_modo" not in st.session_state:
        st.session_state["cand_modo"] = "Listar"

    st.markdown('<div class="glass-actions-row">', unsafe_allow_html=True)
    colA, colB, colC, colD = st.columns(4)
    with colA:
        if st.button("📋 Listar", use_container_width=True, key="cand_listar"):
            st.session_state["cand_modo"] = "Listar"
    with colB:
        if st.button("➕ Novo", use_container_width=True, key="cand_novo"):
            st.session_state["cand_modo"] = "Novo"
    with colC:
        if st.button("✏️ Editar", use_container_width=True, key="cand_editar"):
            st.session_state["cand_modo"] = "Editar"
    with colD:
        if st.button("📲 WhatsApp", use_container_width=True, key="cand_whats"):
            st.session_state["cand_modo"] = "Whats"
    st.markdown("</div>", unsafe_allow_html=True)

    modo = st.session_state["cand_modo"]
    st.markdown(f"**Modo atual:** {modo}")
    st.markdown("---")

    # =========================
    # MODO 1 – LISTAR
    # =========================
    if modo == "Listar":
        df = carregar_candidatos()
        if df.empty:
            st.info("Nenhum candidato cadastrado ainda.")
            return

        df_view = df.copy().fillna("")
        # Flag CV
        if "cv_arquivo" not in df_view.columns:
            df_view["cv_arquivo"] = ""
        df_view["CV"] = df_view["cv_arquivo"].apply(
            lambda x: "📎 Sim" if str(x).strip() else "—"
        )

        # Converte para string
        df_view = df_view.astype(str)

        render_tabela_html(
            df_view,
            columns=["id_candidato", "nome", "idade", "telefone", "cidade", "cargo_pretendido", "CV"],
            headers=["ID", "Nome", "Idade", "Telefone", "Cidade", "Cargo pretendido", "CV"],
        )
        return

    # =========================
    # MODO 2 – NOVO
    # =========================
    if modo == "Novo":
        st.subheader("➕ Novo candidato")

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo do candidato")
            idade = st.text_input("Idade")
            telefone = st.text_input("Telefone (com DDD)")
        with col2:
            cidade = st.text_input("Cidade / UF")
            cargo_pret = st.text_input("Cargo pretendido")
            data_cad = st.date_input(
                "Data do cadastro", value=datetime.today()
            ).strftime("%Y-%m-%d")

        # Upload de CV já no cadastro
        uploaded_cv_new = st.file_uploader(
            "📎 Anexar CV (PDF) – opcional",
            type=["pdf"],
            key="cand_novo_cv",
        )

        colb1, colb2 = st.columns([1, 1])
        with colb1:
            if st.button("💾 Salvar candidato", use_container_width=True, key="btn_salvar_cand_novo"):
                if not nome.strip():
                    st.error("Informe o nome do candidato.")
                else:
                    novo_id = registrar_candidato(
                        nome.strip(),
                        idade.strip(),
                        telefone.strip(),
                        cidade.strip(),
                        cargo_pret.strip(),
                        data_cad,
                    )
                    # Se CV foi anexado, grava no disco e atualiza CSV
                    if uploaded_cv_new is not None:
                        base_nome = re.sub(r"\W+", "_", nome.strip()) or "candidato"
                        cv_nome = f"cv_{novo_id}_{base_nome}.pdf"
                        cv_path = os.path.join(CV_DIR, cv_nome)
                        with open(cv_path, "wb") as f:
                            f.write(uploaded_cv_new.read())

                        df_all = carregar_candidatos()
                        mask = df_all["id_candidato"] == str(novo_id)
                        if "cv_arquivo" not in df_all.columns:
                            df_all["cv_arquivo"] = ""
                        df_all.loc[mask, "cv_arquivo"] = cv_path
                        df_all.to_csv(LOG_CAND, sep=";", index=False, encoding="utf-8")

                    st.success(f"Candidato cadastrado com ID {novo_id}.")
                    st.session_state["cand_modo"] = "Listar"
                    st.experimental_rerun()
        with colb2:
            if st.button("⬅ Voltar para lista", use_container_width=True, key="btn_voltar_cand_novo"):
                st.session_state["cand_modo"] = "Listar"
                st.experimental_rerun()

        return

    # =========================
    # MODO 3 – EDITAR
    # =========================
    if modo == "Editar":
        st.subheader("✏️ Editar candidato")

        df = carregar_candidatos()
        if df.empty:
            st.info("Nenhum candidato para editar.")
            return

        df = df.fillna("")

        opcoes = {
            int(row["id_candidato"]): f"{row['id_candidato']} - {row['nome']}"
            for _, row in df.iterrows()
        }

        id_sel = st.selectbox(
            "Selecione o candidato:",
            options=list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
            key="cand_edit_sel",
        )

        row_sel = df[df["id_candidato"] == str(id_sel)].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            nome_f = st.text_input("Nome", value=row_sel["nome"])
            idade_f = st.text_input("Idade", value=str(row_sel.get("idade", "")))
            tel_f = st.text_input("Telefone", value=row_sel.get("telefone", ""))
            cidade_f = st.text_input("Cidade", value=row_sel.get("cidade", ""))
        with col2:
            cargo_f = st.text_input("Cargo pretendido", value=row_sel.get("cargo_pretendido", ""))
            data_cad_f = st.text_input(
                "Data cadastro (YYYY-MM-DD)",
                value=row_sel.get("data_cadastro", ""),
            )
            linkedin_f = st.text_input("LinkedIn", value=row_sel.get("linkedin", ""))

        st.markdown("**Currículo (CV) do candidato**")
        cv_atual = row_sel.get("cv_arquivo", "") or ""
        if cv_atual and os.path.exists(cv_atual):
            st.write(f"Arquivo atual: `{os.path.basename(cv_atual)}`")
            with open(cv_atual, "rb") as f:
                cv_bytes = f.read()
            st.download_button(
                "⬇️ Baixar CV",
                data=cv_bytes,
                file_name=os.path.basename(cv_atual),
                mime="application/pdf",
                key=f"cand_cv_down_{id_sel}",
            )
        else:
            st.write("Nenhum CV anexado.")

        uploaded_cv = st.file_uploader(
            "📎 Anexar/atualizar CV (PDF)",
            type=["pdf"],
            key=f"cand_cv_up_{id_sel}",
        )

        colb1, colb2 = st.columns([1, 1])
        with colb1:
            if st.button("💾 Salvar alterações", use_container_width=True, key="btn_salvar_cand_edit"):
                df_all = carregar_candidatos()
                mask = df_all["id_candidato"] == str(id_sel)
                if not mask.any():
                    st.error("Candidato não encontrado para salvar.")
                else:
                    df_all.loc[mask, "nome"] = nome_f
                    df_all.loc[mask, "idade"] = idade_f
                    df_all.loc[mask, "telefone"] = tel_f
                    df_all.loc[mask, "cidade"] = cidade_f
                    df_all.loc[mask, "cargo_pretendido"] = cargo_f
                    df_all.loc[mask, "data_cadastro"] = data_cad_f
                    df_all.loc[mask, "linkedin"] = linkedin_f

                    if uploaded_cv is not None:
                        base_nome = re.sub(r"\W+", "_", nome_f.strip()) or "candidato"
                        cv_nome = f"cv_{id_sel}_{base_nome}.pdf"
                        cv_path = os.path.join(CV_DIR, cv_nome)
                        with open(cv_path, "wb") as f:
                            f.write(uploaded_cv.read())
                        if "cv_arquivo" not in df_all.columns:
                            df_all["cv_arquivo"] = ""
                        df_all.loc[mask, "cv_arquivo"] = cv_path

                    try:
                        df_all.to_csv(LOG_CAND, sep=";", index=False, encoding="utf-8")
                        st.success("Ficha atualizada com sucesso!")
                        st.session_state["cand_modo"] = "Listar"
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar ficha: {e}")
        with colb2:
            if st.button("⬅ Voltar para lista", use_container_width=True, key="btn_voltar_cand_edit"):
                st.session_state["cand_modo"] = "Listar"
                st.experimental_rerun()

        return

    # =========================
    # MODO 4 – WHATSAPP
    # =========================
    if modo == "Whats":
        st.subheader("📲 Contato rápido via WhatsApp")

        df = carregar_candidatos()
        if df.empty:
            st.info("Nenhum candidato cadastrado ainda.")
            return

        df = df.fillna("")
        opcoes2 = {
            int(row["id_candidato"]): row["nome"]
            for _, row in df.iterrows()
        }

        id_sel2 = st.selectbox(
            "Selecione o candidato:",
            options=list(opcoes2.keys()),
            format_func=lambda x: opcoes2[x],
            key="cand_whats_sel",
        )
        row2 = df[df["id_candidato"] == str(id_sel2)].iloc[0]
        telefone = row2.get("telefone", "")
        st.write(f"**Telefone:** {telefone}  |  **Cidade:** {row2.get('cidade', '')}")
        link = montar_link_whatsapp(telefone)
        if not link:
            st.warning("Telefone inválido ou não informado.")
        else:
            st.markdown(f"[💬 Abrir conversa no WhatsApp]({link})")

        return

