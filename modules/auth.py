import os
import hashlib
import pandas as pd
import streamlit as st
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(DATA_DIR, "usuarios.csv")


# ======================================================
# UTILITÁRIOS
# ======================================================
def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def carregar_usuarios() -> pd.DataFrame:
    if not os.path.exists(USERS_FILE):
        return pd.DataFrame(columns=[
            "username", "nome", "senha_hash", "deve_trocar_senha",
            "is_admin", "ativo", "criado_em"
        ])
    try:
        return pd.read_csv(USERS_FILE, sep=";", dtype=str)
    except:
        return pd.DataFrame(columns=[
            "username", "nome", "senha_hash", "deve_trocar_senha",
            "is_admin", "ativo", "criado_em"
        ])


def salvar_usuarios(df: pd.DataFrame):
    df.to_csv(USERS_FILE, sep=";", index=False, encoding="utf-8")


def inicializar_usuarios_padrao():
    if os.path.exists(USERS_FILE):
        return

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    senha_padrao = hash_senha("2025")

    df = pd.DataFrame([
        {
            "username": "rikardo.alvim",
            "nome": "Rikardo Alvim",
            "senha_hash": senha_padrao,
            "deve_trocar_senha": "1",
            "is_admin": "1",
            "ativo": "1",
            "criado_em": agora,
        },
        {
            "username": "stephanie.alvim",
            "nome": "Stephanie Alvim",
            "senha_hash": senha_padrao,
            "deve_trocar_senha": "1",
            "is_admin": "0",
            "ativo": "1",
            "criado_em": agora,
        },
    ])
    salvar_usuarios(df)


def autenticar(username: str, senha: str):
    df = carregar_usuarios()
    if df.empty:
        return None

    linha = df[df["username"] == username]
    if linha.empty:
        return None

    linha = linha.iloc[0]

    if linha["ativo"] != "1":
        return None

    if hash_senha(senha) != linha["senha_hash"]:
        return None

    return {
        "username": linha["username"],
        "nome": linha["nome"],
        "is_admin": linha["is_admin"] == "1",
        "deve_trocar_senha": linha["deve_trocar_senha"] == "1"
    }


def atualizar_senha(username: str, nova_senha: str):
    df = carregar_usuarios()
    mask = df["username"] == username
    if not mask.any():
        return False
    df.loc[mask, "senha_hash"] = hash_senha(nova_senha)
    df.loc[mask, "deve_trocar_senha"] = "0"
    salvar_usuarios(df)
    return True


# ======================================================
# UI ESTILIZADA
# ======================================================

CSS_LOGIN = """
<style>
body {
    background: linear-gradient(135deg, #e6ebf5 0%, #f7f9fc 100%) !important;
}
.login-box {
    background: #ffffffdd;
    backdrop-filter: blur(8px);
    padding: 40px 35px;
    margin: auto;
    width: 380px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    margin-top: 70px;
    animation: fadeIn 0.6s ease-out;
}
.login-title {
    font-size: 28px;
    text-align: center;
    font-weight: 700;
    margin-bottom: 10px;
    color: #1f2d3d;
}
.login-sub {
    font-size: 14px;
    text-align: center;
    color: #5c697a;
    margin-bottom: 25px;
}
.login-input > div > div {
    border-radius: 10px !important;
}
.login-btn button {
    width: 100% !important;
    border-radius: 10px !important;
    padding: 10px !important;
    font-size: 16px !important;
}
.logo-space {
    width: 140px;
    height: 140px;
    margin: auto;
    border-radius: 100%;
    background: #eef1f5;
    margin-bottom: 15px;
    background-size: cover;
    background-position: center;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(12px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
"""


def run():
    st.markdown(CSS_LOGIN, unsafe_allow_html=True)
    inicializar_usuarios_padrao()

    # =============================
    # Se já estiver logado
    # =============================
    if "user" in st.session_state and st.session_state["user"] is not None:
        st.success(f"Você já está logado como **{st.session_state['user']['username']}**.")
        if st.button("Sair", use_container_width=True):
            st.session_state.clear()
            st.experimental_rerun()
        return

    # =============================
    # CARTÃO DE LOGIN
    # =============================
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.markdown('<div class="logo-space"></div>', unsafe_allow_html=True)

        st.markdown('<div class="login-title">Acesso ao Sistema</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">GAC - Gerenciador Alvim Consultoria</div>',
                    unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<div class="login-input">', unsafe_allow_html=True)
            username = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            st.markdown('</div>', unsafe_allow_html=True)

            entrar = st.form_submit_button("Entrar")

        if entrar:
            user = autenticar(username.strip(), senha)
            if not user:
                st.error("Usuário ou senha inválidos.")
            else:
                st.session_state["user"] = user
                if user["deve_trocar_senha"]:
                    st.session_state["forcar_troca_senha"] = True
                st.experimental_rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # fecha card

    # =============================
    # TELA DE TROCA DE SENHA
    # =============================
    if "user" in st.session_state and st.session_state.get("forcar_troca_senha"):
        st.markdown("### 🔒 Alterar senha (Primeiro acesso)")

        with st.form("troca_form"):
            nova = st.text_input("Nova senha", type="password")
            conf = st.text_input("Confirmar nova senha", type="password")
            ok = st.form_submit_button("Atualizar")

        if ok:
            if not nova or not conf:
                st.error("Preencha os dois campos.")
            elif nova != conf:
                st.error("As senhas não conferem.")
            else:
                atualizar_senha(st.session_state["user"]["username"], nova)
                st.success("Senha alterada! Faça login novamente.")
                st.session_state.clear()
                st.experimental_rerun()
