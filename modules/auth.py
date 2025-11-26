import os
import hashlib
from typing import Optional

import pandas as pd
import streamlit as st

# Caminho do arquivo de usuários: raiz do projeto (mesmo nível do parecer_app.py)
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(MODULE_DIR, ".."))
USERS_FILE = os.path.join(ROOT_DIR, "usuarios.csv")

REQUIRED_COLS = ["username", "nome", "senha_hash", "must_change", "perfil", "ativo"]


# -----------------------------
# Utilitários de senha / arquivo
# -----------------------------
def hash_password(senha: str) -> str:
    """Gera hash SHA256 para a senha."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def _create_default_users_df() -> pd.DataFrame:
    """Cria DataFrame com usuários padrão."""
    data = [
        {
            "username": "rikardo.alvim",
            "nome": "Rikardo Alvim",
            "senha_hash": hash_password("2025"),
            "must_change": 1,  # precisa trocar ao primeiro login
            "perfil": "MASTER",
            "ativo": 1,
        },
        {
            "username": "stephanie.alvim",
            "nome": "Stephanie Alvim",
            "senha_hash": hash_password("2025"),
            "must_change": 1,
            "perfil": "OPERACOES_RS",
            "ativo": 1,
        },
    ]
    return pd.DataFrame(data, columns=REQUIRED_COLS)


def _save_df(df: pd.DataFrame) -> None:
    """Grava o DataFrame de usuários no CSV com ; como separador."""
    df.to_csv(USERS_FILE, sep=";", index=False, encoding="utf-8")


def _recreate_users_file_with_defaults(msg: Optional[str] = None) -> pd.DataFrame:
    """Recria o arquivo de usuários com os padrões."""
    df = _create_default_users_df()
    _save_df(df)
    if msg:
        st.warning(msg)
    return df


def load_users() -> pd.DataFrame:
    """
    Carrega usuários do CSV.
    - Se não existir, cria com usuários padrão.
    - Se estiver corrompido ou sem colunas obrigatórias, recria com padrão.
    """
    if not os.path.exists(USERS_FILE):
        df = _create_default_users_df()
        _save_df(df)
        return df

    try:
        df = pd.read_csv(USERS_FILE, sep=";", dtype=str)
    except Exception:
        return _recreate_users_file_with_defaults(
            "Arquivo de usuários estava inválido. Foi recriado com usuários padrão."
        )

    # Garante colunas obrigatórias
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return _recreate_users_file_with_defaults(
            "Estrutura de usuários inconsistente. Arquivo recriado com usuários padrão."
        )

    # Normaliza tipos
    df["must_change"] = df["must_change"].fillna("0").astype(int)
    df["ativo"] = df["ativo"].fillna("1").astype(int)
    df["perfil"] = df["perfil"].fillna("OPERACOES_GERAL").astype(str)

    df["username"] = df["username"].astype(str)
    df["nome"] = df["nome"].astype(str)
    df["senha_hash"] = df["senha_hash"].astype(str)

    return df


def save_users(df: pd.DataFrame) -> None:
    """Grava o DataFrame de usuários no CSV."""
    # Garante ordem das colunas
    for col in REQUIRED_COLS:
        if col not in df.columns:
            if col == "must_change":
                df[col] = 0
            elif col == "ativo":
                df[col] = 1
            elif col == "perfil":
                df[col] = "OPERACOES_GERAL"
            else:
                df[col] = ""
    df = df[REQUIRED_COLS]
    _save_df(df)


# -----------------------------
# Tela de troca de senha
# -----------------------------
def _render_change_password(username: str, df: pd.DataFrame) -> None:
    st.title("🔐 Definir nova senha")
    st.write(f"Usuário: **{username}**")

    new1 = st.text_input("Nova senha", type="password")
    new2 = st.text_input("Confirme a nova senha", type="password")

    if st.button("Salvar nova senha"):
        if not new1.strip():
            st.error("Informe uma senha.")
        elif new1 != new2:
            st.error("As senhas não coincidem.")
        else:
            df.loc[df["username"] == username, "senha_hash"] = hash_password(new1)
            df.loc[df["username"] == username, "must_change"] = 0
            save_users(df)
            st.success("Senha alterada com sucesso! Faça login novamente.")
            # Limpa sessão de auth e volta pra tela de login
            for k in ["auth_username", "auth_role", "auth_need_change"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.stop()


# -----------------------------
# Tela de login
# -----------------------------
def _render_login(df: pd.DataFrame) -> None:
    st.title("🔑 GAC - Alvim Consultoria")
    st.write("Faça login para acessar o sistema.")

    col1, col2 = st.columns([1, 1])

    with col1:
        username_inp = st.text_input("Usuário (login)")
        password_inp = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            row = df[df["username"] == username_inp]
            if row.empty:
                st.error("Usuário não encontrado.")
            else:
                row = row.iloc[0]
                if int(row.get("ativo", 1)) != 1:
                    st.error("Usuário inativo.")
                elif row["senha_hash"] != hash_password(password_inp):
                    st.error("Senha inválida.")
                else:
                    st.session_state["auth_username"] = row["username"]
                    st.session_state["auth_role"] = row.get("perfil", "OPERACOES_GERAL")
                    st.session_state["auth_need_change"] = bool(int(row.get("must_change", 0)))
                    st.rerun()

    with col2:
        st.markdown(
            """
            ##### Acessos iniciais
            - **Usuário:** `rikardo.alvim` / **Senha:** `2025`  
            - **Usuário:** `stephanie.alvim` / **Senha:** `2025`  

            No primeiro acesso, será solicitado que a senha seja redefinida.
            """
        )


# -----------------------------
# Função principal usada pelo parecer_app
# -----------------------------
def run() -> Optional[str]:
    """
    Desenha tela de login ou troca de senha.
    Retorna o username logado (quando já autenticado) ou None.
    O parecer_app decide se segue ou não.
    """
    df = load_users()

    # Se já tem usuário na sessão, verifica se precisa trocar senha
    username = st.session_state.get("auth_username")
    if username:
        row = df[df["username"] == username]
        if row.empty:
            # Usuário apagado do arquivo -> volta pra login
            for k in ["auth_username", "auth_role", "auth_need_change"]:
                st.session_state.pop(k, None)
            _render_login(df)
            return None

        row = row.iloc[0]
        st.session_state["auth_role"] = row.get("perfil", "OPERACOES_GERAL")
        must_change = int(row.get("must_change", 0)) == 1

        if must_change:
            _render_change_password(username, df)
            return None

        # Usuário logado OK
        return username

    # Caso não haja usuário na sessão, mostra login
    _render_login(df)
    return None




