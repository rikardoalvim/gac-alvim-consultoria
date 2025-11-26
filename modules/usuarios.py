import os
import streamlit as st
import pandas as pd

from .auth import load_users, save_users, hash_password

PERFIS = [
    ("MASTER", "MASTER - Acesso total"),
    ("OPERACOES_GERAL", "Operações Geral"),
    ("OPERACOES_RS", "Operações R&S"),
    ("OPERACOES_SISTEMAS", "Operações Sistemas"),
    ("FINANCEIRO", "Financeiro"),
]


def _perfil_label_to_code(label: str) -> str:
    for code, desc in PERFIS:
        if desc == label or code == label:
            return code
    return "OPERACOES_GERAL"


def _perfil_code_to_label(code: str) -> str:
    for c, desc in PERFIS:
        if c == code:
            return desc
    return "Operações Geral"


def _render_table(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Nenhum usuário cadastrado.")
        return

    df_view = df.copy()
    df_view["Ativo"] = df_view["ativo"].map({1: "Sim", 0: "Não"})
    df_view["Perfil"] = df_view["perfil"].apply(_perfil_code_to_label)
    df_view["Precisa trocar senha"] = df_view["must_change"].map({1: "Sim", 0: "Não"})

    df_view = df_view[["username", "nome", "Perfil", "Ativo", "Precisa trocar senha"]]

    # Usa o CSS global de <table> (liquid glass)
    html = ["<table><thead><tr>"]
    for col in df_view.columns:
        html.append(f"<th>{col}</th>")
    html.append("</tr></thead><tbody>")
    for _, row in df_view.iterrows():
        html.append("<tr>")
        for col in df_view.columns:
            html.append(f"<td>{row[col]}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)


def run():
    # Somente MASTER pode acessar
    role = st.session_state.get("auth_role", "OPERACOES_GERAL")
    if role != "MASTER":
        st.error("Apenas usuários com perfil MASTER podem acessar o cadastro de usuários.")
        return

    st.header("👥 Cadastro de Usuários")

    if "usuarios_modo" not in st.session_state:
        st.session_state["usuarios_modo"] = "Listar"

    colA, colB, colC, colD = st.columns(4)
    with colA:
        if st.button("📋 Listar", use_container_width=True):
            st.session_state["usuarios_modo"] = "Listar"
    with colB:
        if st.button("➕ Novo usuário", use_container_width=True):
            st.session_state["usuarios_modo"] = "Novo"
    with colC:
        if st.button("✏️ Editar usuário", use_container_width=True):
            st.session_state["usuarios_modo"] = "Editar"
    with colD:
        if st.button("🗑 Excluir usuário", use_container_width=True):
            st.session_state["usuarios_modo"] = "Excluir"

    st.markdown("---")

    modo = st.session_state["usuarios_modo"]
    df = load_users()

    # ---------------------------
    # LISTAR
    # ---------------------------
    if modo == "Listar":
        st.subheader("📋 Usuários cadastrados")
        _render_table(df)
        return

    # ---------------------------
    # NOVO USUÁRIO
    # ---------------------------
    if modo == "Novo":
        st.subheader("➕ Novo usuário")

        username = st.text_input("Login (username)")
        nome = st.text_input("Nome completo")
        perfil_label = st.selectbox(
            "Perfil de acesso",
            [desc for _, desc in PERFIS],
        )
        ativo = st.checkbox("Usuário ativo", value=True)
        senha1 = st.text_input("Senha inicial", type="password")
        senha2 = st.text_input("Confirme a senha inicial", type="password")

        if st.button("💾 Salvar novo usuário", use_container_width=True):
            if not username.strip():
                st.error("Informe o login (username).")
            elif not senha1.strip():
                st.error("Informe a senha inicial.")
            elif senha1 != senha2:
                st.error("As senhas não coincidem.")
            elif (df["username"].str.lower() == username.strip().lower()).any():
                st.error("Já existe um usuário com esse login.")
            else:
                perfil_code = _perfil_label_to_code(perfil_label)
                novo = {
                    "username": username.strip(),
                    "nome": nome.strip() or username.strip(),
                    "senha_hash": hash_password(senha1),
                    "must_change": 1,  # novo usuário troca senha no primeiro login
                    "perfil": perfil_code,
                    "ativo": 1 if ativo else 0,
                }
                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                save_users(df)
                st.success("Usuário criado com sucesso!")
                st.session_state["usuarios_modo"] = "Listar"
                st.experimental_rerun()
        return

    # ---------------------------
    # EDITAR USUÁRIO
    # ---------------------------
    if modo == "Editar":
        st.subheader("✏️ Editar usuário")

        if df.empty:
            st.info("Nenhum usuário cadastrado.")
            return

        usuarios_list = df["username"].tolist()
        usuario_sel = st.selectbox("Selecione o usuário:", usuarios_list)

        row = df[df["username"] == usuario_sel].iloc[0]

        nome_edit = st.text_input("Nome completo", value=row["nome"])
        perfil_label_edit = st.selectbox(
            "Perfil de acesso",
            [desc for _, desc in PERFIS],
            index=[c for c, _ in PERFIS].index(row["perfil"]) if row["perfil"] in [c for c, _ in PERFIS] else 1,
        )
        ativo_edit = st.checkbox("Usuário ativo", value=bool(row["ativo"]))
        reset_senha = st.checkbox("Redefinir senha (obrigar troca no próximo login?)")

        nova_senha1 = ""
        nova_senha2 = ""
        if reset_senha:
            nova_senha1 = st.text_input("Nova senha inicial", type="password")
            nova_senha2 = st.text_input("Confirme a nova senha", type="password")

        if st.button("💾 Salvar alterações", use_container_width=True):
            perfil_code = _perfil_label_to_code(perfil_label_edit)

            df.loc[df["username"] == usuario_sel, "nome"] = nome_edit.strip() or usuario_sel
            df.loc[df["username"] == usuario_sel, "perfil"] = perfil_code
            df.loc[df["username"] == usuario_sel, "ativo"] = 1 if ativo_edit else 0

            if reset_senha:
                if not nova_senha1.strip():
                    st.error("Informe a nova senha.")
                    return
                if nova_senha1 != nova_senha2:
                    st.error("As senhas não coincidem.")
                    return
                df.loc[df["username"] == usuario_sel, "senha_hash"] = hash_password(nova_senha1)
                df.loc[df["username"] == usuario_sel, "must_change"] = 1
            save_users(df)
            st.success("Usuário atualizado com sucesso!")
            st.session_state["usuarios_modo"] = "Listar"
            st.experimental_rerun()
        return

    # ---------------------------
    # EXCLUIR USUÁRIO
    # ---------------------------
    if modo == "Excluir":
        st.subheader("🗑 Excluir usuário")

        if df.empty:
            st.info("Nenhum usuário cadastrado.")
            return

        usuarios_list = df["username"].tolist()
        usuario_sel = st.selectbox("Selecione o usuário para excluir:", usuarios_list)

        st.warning(
            f"Tem certeza que deseja excluir o usuário **{usuario_sel}**? "
            "Essa ação não poderá ser desfeita."
        )
        confirma = st.text_input('Digite "EXCLUIR" para confirmar')

        if st.button("⚠ Confirmar exclusão", use_container_width=True):
            if confirma.strip().upper() != "EXCLUIR":
                st.error('Digite exatamente "EXCLUIR" para confirmar.')
            else:
                df = df[df["username"] != usuario_sel]
                save_users(df)
                st.success(f"Usuário {usuario_sel} excluído com sucesso.")
                st.session_state["usuarios_modo"] = "Listar"
                st.experimental_rerun()
        return

