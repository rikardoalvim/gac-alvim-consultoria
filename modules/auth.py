import streamlit as st

# ============================================
# "Banco" simples de usuários em memória
# (se quiser depois a gente persiste em arquivo)
# ============================================

DEFAULT_USERS = {
    "rikardo.alvim": {
        "nome": "Rikardo Alvim",
        "senha": "2025",
        "force_change": True,  # precisa trocar no 1º acesso
        "is_admin": True,
    },
    "stephanie.alvim": {
        "nome": "Stephanie Alvim",
        "senha": "2025",
        "force_change": True,
        "is_admin": False,
    },
}


def get_users():
    """
    Carrega o dicionário de usuários na session_state.
    (por enquanto fica só em memória mesmo)
    """
    if "usuarios_db" not in st.session_state:
        # cópia para não mexer no DEFAULT_USERS original
        st.session_state["usuarios_db"] = {k: v.copy() for k, v in DEFAULT_USERS.items()}
    return st.session_state["usuarios_db"]


def run():
    users = get_users()

    usuario_atual = st.session_state.get("usuario_logado")
    precisa_trocar = st.session_state.get("trocar_senha_obrigatorio", False)

    # ====================================================
    # 1) Se já está logado e NÃO precisa trocar senha:
    #    não mostra nada de login, deixa o parecer_app cuidar
    # ====================================================
    if usuario_atual and not precisa_trocar:
        return

    st.title("🔐 GAC - Autenticação")

    # ====================================================
    # 2) Usuário logado MAS precisa trocar senha
    # ====================================================
    if usuario_atual and precisa_trocar:
        st.info(f"Olá, **{usuario_atual}**. Defina uma nova senha para continuar.")

        nova = st.text_input("Nova senha", type="password")
        nova2 = st.text_input("Confirme a nova senha", type="password")

        if st.button("Salvar nova senha"):
            if not nova:
                st.error("Informe uma senha.")
            elif nova != nova2:
                st.error("As senhas não conferem.")
            else:
                users[usuario_atual]["senha"] = nova
                users[usuario_atual]["force_change"] = False
                st.session_state["trocar_senha_obrigatorio"] = False
                st.success("Senha alterada com sucesso! Entrando no sistema...")
                st.rerun()

        return

    # ====================================================
    # 3) Tela de login (ninguém logado ainda)
    # ====================================================
    st.subheader("Acesse o GAC - Gerenciador Alvim Consultoria")

    col1, col2 = st.columns(2)
    with col1:
        login = st.text_input("Usuário (ex.: rikardo.alvim)")
    with col2:
        senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if login in users and senha == users[login]["senha"]:
            # Login OK
            st.session_state["usuario_logado"] = login
            st.session_state["trocar_senha_obrigatorio"] = users[login].get("force_change", False)
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")


