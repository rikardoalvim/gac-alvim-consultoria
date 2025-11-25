import os
import re
from datetime import datetime

import streamlit as st

from .core import (
    carregar_candidatos,
    registrar_candidato,
    CV_DIR,
    LOG_CAND,
    montar_link_whatsapp,
)


def run():
    st.header("👤 Cadastro de Candidatos")

    # ============================
    # CONTROLE DE MODO
    # ============================
    if "candidatos_modo" not in st.session_state:
        st.session_state["candidatos_modo"] = "Listar"

    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        if st.button("📋 Listar", use_container_width=True):
            st.session_state["candidatos_modo"] = "Listar"
    with col_a2:
        if st.button("➕ Inserir", use_container_width=True):
            st.session_state["candidatos_modo"] = "Inserir"
    with col_a3:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state["candidatos_modo"] = "Editar"

    modo = st.session_state["candidatos_modo"]
    st.markdown(f"**Modo atual:** {modo}")
    st.markdown("---")

    df = carregar_candidatos()

    # ============================
    # MODO: LISTAR
    # ============================
    if modo == "Listar":
        st.subheader("📋 Lista de candidatos")

        if df.empty:
            st.info("Nenhum candidato cadastrado ainda.")
            return

        df_view = df.sort_values("id_candidato")

        # ---------- TABELA CUSTOMIZADA COM BOTÃO DE WHATSAPP ----------
        tabela_html = "<table style='width:100%; border-collapse: collapse;'>"
        tabela_html += """
        <tr style='background-color:#f0f0f0;'>
            <th style='padding:8px; text-align:left;'>ID</th>
            <th style='padding:8px; text-align:left;'>Nome</th>
            <th style='padding:8px; text-align:left;'>Telefone</th>
            <th style='padding:8px; text-align:left;'>Cidade</th>
            <th style='padding:8px; text-align:left;'>Cargo</th>
            <th style='padding:8px; text-align:left;'>WhatsApp</th>
        </tr>
        """

        for _, row in df_view.iterrows():
            telefone = row["telefone"]
            nome = row["nome"]
            cidade = row["cidade"]
            cargo = row["cargo_pretendido"]
            idc = row["id_candidato"]

            # Ajusta telefone
            fone_formatado = "".join(filter(str.isdigit, telefone))
            link = f"https://wa.me/55{fone_formatado}"

            tabela_html += f"""
            <tr style='border-bottom:1px solid #ddd;'>
                <td style='padding:6px;'>{idc}</td>
                <td style='padding:6px;'>{nome}</td>
                <td style='padding:6px;'>{telefone}</td>
                <td style='padding:6px;'>{cidade}</td>
                <td style='padding:6px;'>{cargo}</td>
                <td style='padding:6px;'>
                    <a href="{link}" target="_blank" 
                        style='text-decoration:none; font-weight:bold; color:#1b8a5a;'>
                        💬 WhatsApp
                    </a>
                </td>
            </tr>
            """

        tabela_html += "</table>"

        st.markdown(tabela_html, unsafe_allow_html=True)

        return

    # ============================
    # MODO: INSERIR (NOVO CANDIDATO)
    # ============================
    if modo == "Inserir":
        st.subheader("➕ Novo candidato")

        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome completo do candidato", key="nome_novo")
            idade = st.text_input("Idade", key="idade_novo")
            telefone = st.text_input("Telefone (com DDD)", key="telefone_novo")
        with col2:
            cidade = st.text_input("Cidade / UF", key="cidade_novo")
            cargo_pret = st.text_input("Cargo pretendido", key="cargo_pret_novo")
            data_cad = st.date_input(
                "Data do cadastro",
                value=datetime.today(),
                key="data_cad_novo",
            ).strftime("%Y-%m-%d")

        col_b1, col_b2 = st.columns([1, 1])
        with col_b1:
            if st.button("💾 Salvar candidato", key="btn_salvar_cand_novo", use_container_width=True):
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
                    st.success(f"Candidato cadastrado com ID {novo_id}.")
                    st.session_state["candidatos_modo"] = "Listar"
                    st.rerun()

        with col_b2:
            if st.button("⬅ Voltar para lista", use_container_width=True):
                st.session_state["candidatos_modo"] = "Listar"
                st.rerun()

        return

    # ============================
    # MODO: EDITAR
    # ============================
    if modo == "Editar":
        st.subheader("✏️ Editar candidato")

        if df.empty:
            st.info("Nenhum candidato cadastrado para editar.")
            return

        df_view = df.sort_values("id_candidato")

        opcoes = {int(row["id_candidato"]): row["nome"] for _, row in df_view.iterrows()}
        id_sel = st.selectbox(
            "Selecione o candidato para editar:",
            options=list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
            key="cand_edit_sel",
        )

        row = df_view[df_view["id_candidato"] == str(id_sel)].iloc[0]

        colf1, colf2 = st.columns(2)
        with colf1:
            nome_f = st.text_input("Nome", value=row["nome"], key=f"nome_{id_sel}")
            idade_f = st.text_input("Idade", value=str(row["idade"]), key=f"idade_{id_sel}")
            tel_f = st.text_input("Telefone", value=row["telefone"], key=f"tel_{id_sel}")
            cidade_f = st.text_input("Cidade", value=row["cidade"], key=f"cidade_{id_sel}")
        with colf2:
            cargo_f = st.text_input(
                "Cargo pretendido",
                value=row["cargo_pretendido"],
                key=f"cargo_pret_{id_sel}",
            )
            data_cad_f = st.text_input(
                "Data cadastro (YYYY-MM-DD)",
                value=row["data_cadastro"],
                key=f"data_cad_{id_sel}",
            )
            linkedin_f = st.text_input(
                "LinkedIn",
                value=row.get("linkedin", ""),
                key=f"linkedin_{id_sel}",
            )

        st.markdown("**Currículo (CV) do candidato**")
        cv_atual = row.get("cv_arquivo", "") or ""
        if cv_atual and os.path.exists(cv_atual):
            st.write(f"Arquivo atual: `{cv_atual}`")
            with open(cv_atual, "rb") as f:
                cv_bytes = f.read()
            st.download_button(
                "⬇️ Baixar CV",
                data=cv_bytes,
                file_name=os.path.basename(cv_atual),
                mime="application/pdf",
                key=f"cv_down_edit_{id_sel}",
            )
        else:
            st.write("Nenhum CV anexado.")

        uploaded_cv = st.file_uploader(
            "📎 Anexar/atualizar CV (PDF)",
            type=["pdf"],
            key=f"cv_up_{id_sel}",
        )

        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            if st.button("💾 Salvar alterações", key=f"btn_salvar_edit_{id_sel}", use_container_width=True):
                df_edit = carregar_candidatos()
                m2 = df_edit["id_candidato"] == str(id_sel)
                if not m2.any():
                    st.error("Candidato não encontrado para salvar.")
                else:
                    df_edit.loc[m2, "nome"] = nome_f
                    df_edit.loc[m2, "idade"] = idade_f
                    df_edit.loc[m2, "telefone"] = tel_f
                    df_edit.loc[m2, "cidade"] = cidade_f
                    df_edit.loc[m2, "cargo_pretendido"] = cargo_f
                    df_edit.loc[m2, "data_cadastro"] = data_cad_f
                    df_edit.loc[m2, "linkedin"] = linkedin_f

                    if uploaded_cv is not None:
                        base_nome = re.sub(r"\W+", "_", nome_f.strip()) or "candidato"
                        cv_nome = f"cv_{id_sel}_{base_nome}.pdf"
                        cv_path = os.path.join(CV_DIR, cv_nome)
                        with open(cv_path, "wb") as f:
                            f.write(uploaded_cv.read())
                        df_edit.loc[m2, "cv_arquivo"] = cv_path

                    df_edit.to_csv(LOG_CAND, sep=";", index=False, encoding="utf-8")
                    st.success("Ficha atualizada com sucesso!")
                    st.session_state["candidatos_modo"] = "Listar"
                    st.rerun()

        with col_c2:
            if st.button("⬅ Voltar para lista", use_container_width=True):
                st.session_state["candidatos_modo"] = "Listar"
                st.rerun()

