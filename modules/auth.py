import os
import hashlib
import pandas as pd
import streamlit as st
from datetime import datetime


# ======================================================
# CONFIGURAÇÃO DE ARQUIVOS
# ======================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(DATA_DIR, "usuarios.csv")


# ======================================================
# FUNÇÕES DE SUPORTE
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

    row = df[df["username"] == username]
    if row.empty:
        return None

    row = row.iloc[0]

    if row["ativo"] != "1":
        return None

    if hash_senha(senha) != row["senha_hash"]:
        return None

    return {
        "username": row["username"],
        "nome": row["nome"],
        "is_admin": row["is_admin"] == "1",
        "deve_trocar_senha": row["deve_trocar_senha"] == "1",
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
# CSS ESTILIZADO DA TELA DE LOGIN
# ======================================================

CSS_LOGIN = """
<style>
body {
    background: linear-gradient(135deg, #dee4ef 0%, #f6f8fc 100%) !important;
}
.login-box {
    background: #ffffffee;
    backdrop-filter: blur(6px);
    padding: 40px 36px;
    margin: auto;
    width: 360px;
    border-radius: 18px;
    box-shadow: 0 6px 26px rgba(0,0,0,0.15);
    margin-top: 80px;
    animation: fadeIn 0.55s ease-out;
}
.login-title {
    font-size: 26px;
    text-align: center;
    font-weight: 700;
    margin-bottom: 6px;
    color: #1c2a38;
}
.login-subtitle {
    font-size: 15px;
    text-align: center;
    color: #64748b;
    margin-bottom: 25px;
}
.login-input > div > div {
    border-radius: 12px !important;
}
.login-btn button {
    width: 100% !important;
    border-radius: 12px !important;
    padding: 10px !important;
    font-size: 16px !important;
}
.powered {
    text-align: center;
    margin-top: 25px;
    font-size: 13px;
    font-style: italic;
    color: #475569;
}
.powered i {
    color: #6366f1;
    font-weight: 700;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(12px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
"""


# ======================================================
# INTERFACE DE LOGIN
# ======================================================

def run():
    st.markdown(CSS_LOGIN, unsafe_allow_html=True)
    inicializar_usuarios_padrao()

    # Se já estiver logado
    if "user" in st.session_state and st.session_state["user"] is not None and not st.session_state.get("forcar_troca_senha", False):
        st.success(f"Você já está logado como **{st.session_state['user']['username']}**.")
        if st.button("Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        return

    # --------------------------------------------------
    # SE PRECISA TROCAR A SENHA (primeiro login)
    # --------------------------------------------------
    if (
        "user" in st.session_state
        and st.session_state["user"] is not None
        and st.session_state.get("forcar_troca_senha", False)
    ):
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
                st.rerun()
        return

    # --------------------------------------------------
    # FORMULÁRIO DE LOGIN
    # --------------------------------------------------
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown('<div class="login-title">GAC - Alvim Consultoria</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Acesso ao Sistema</div>', unsafe_allow_html=True)

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
            st.rerun()

    # Powered by
    st.markdown('<div class="powered">Powered by <i>⚡ Rikardo Alvim</i></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

