import os
import hashlib
from typing import Tuple

import pandas as pd
import streamlit as st


# ==========================================
# CONSTANTES / ARQUIVOS
# ==========================================

# raiz do projeto (mesmo nível do parecer_app.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(BASE_DIR, "usuarios.csv")

# Perfis disponíveis
PERFIS_DISPONIVEIS = [
    "MASTER",
    "OPERACOES_GERAL",
    "OPERACOES_RS",
    "OPERACOES_SISTEMAS",
    "FINANCEIRO",
]


# ==========================================
# UTILITÁRIOS DE SENHA / CSV
# ==========================================

def hash_password(password: str) -> str:
    """Hash simples SHA256 (mesma lógica usada no auth)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def ensure_users_file() -> pd.DataFrame:
    """
    Garante que o usuarios.csv exista.
    Se não existir, cria com Rikardo e Stephanie padrão.
    """
    if not os.path.exists(USERS_FILE):
        data = [
            {
                "username": "rikardo.alvim",
                "nome": "Rikardo Alvim",
                "senha_hash": hash_password("2025"),
                "must_change": 1,
                "perfil": "MASTER",
                "ativo": 1,
            },
            {
                "username": "stephanie.alvim",
                "nome": "Stephanie de Bellis Jalloul Alvim",
                "senha_hash": hash_password("2025"),
                "must_change": 1,
                "perfil": "OPERACOES_RS",
                "ativo": 1,
            },
        ]
        df = pd.DataFrame(data)
        df.to_csv(USERS_FILE, sep=";", index=False, encoding="utf-8")
        return df

    df = pd.read_csv(USERS_FILE, sep=";", encoding="utf-8")

    # Garante colunas mínimas
    for col, default in [
        ("username", ""),
        ("nome", ""),
        ("senha_hash", ""),
        ("must_change", 1),
        ("perfil", "OPERACOES_GERAL"),
        ("ativo", 1),
    ]:
        if col not in df.columns:
            df[col] = default

    # Ajusta tipos básicos
    df["must_change"] = df["must_change"].fillna(1).astype(int)
    df["ativo"] = df["ativo"].fillna(1).astype(int)
    df["perfil"] = df["perfil"].fillna("OPERACOES_GERAL").astype(str)
    df["username"] = df["username"].fillna("").astype(str)
    df["nome"] = df["nome"].fillna("").astype(str)
    df["senha_hash"] = df["senha_hash"].fillna("").astype(str)

    # Salva de volta padronizado
    df.to_csv(USERS_FILE, sep=";", index=False, encoding="utf-8")
    return df


def load_users() -> pd.DataFrame:
    """Carrega usuários (garantindo criação inicial se não existir)."""
    return ensure_users_file()


def save_users(df: pd.DataFrame) -> None:
    """Salva DataFrame de usuários em usuarios.csv."""
    df.to_csv(USERS_FILE, sep=";", index=False, encoding="utf-8")


# ==========================================
# RENDER TABELA GLASS (igual outros módulos)
# ==========================================

def render_tabela_html(df: pd.DataFrame, columns, headers) -> None:
    """Renderiza DataFrame como tabela HTML (glass), igual vagas/candidatos."""
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    df = df.copy().fillna("").astype(str)

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
            html.append(f"<td>{row[col]}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")

    st.markdown("".join(html), unsafe_allow_html=True)


# ==========================================
# FORMULÁRIOS
# ==========================================

def form_novo_usuario() -> None:
    st.subheader("➕ Novo usuário")

    username = st.text_input("Login (username)", placeholder="ex.: nome.sobrenome")
    nome = st.text_input("Nome completo")
    senha_inicial = st.text_input("Senha inicial", type="password")
    perfil = st.selectbox("Perfil de acesso", PERFIS_DISPONIVEIS, index=0)
    must_change = st.checkbox("Solicitar troca de senha no próximo login?", value=True)
    ativo = st.checkbox("Usuário ativo?", value=True)

    colb1, colb2 = st.columns(2)
    with colb1:
        if st.button("💾 Salvar usuário", use_container_width=True, key="btn_salvar_usuario_novo"):
            if not username.strip():
                st.error("Informe o login (username).")
                return
            if not nome.strip():
                st.error("Informe o nome completo.")
                return
            if not senha_inicial.strip():
                st.error("Informe uma senha inicial.")
                return

            df = load_users()
            if username in df["username"].tolist():
                st.error("Já existe um usuário com esse login.")
                return

            novo = {
                "username": username.strip(),
                "nome": nome.strip(),
                "senha_hash": hash_password(senha_inicial.strip()),
                "must_change": 1 if must_change else 0,
                "perfil": perfil,
                "ativo": 1 if ativo else 0,
            }
            df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
            save_users(df)
            st.success("Usuário criado com sucesso!")

    with colb2:
        if st.button("↩ Voltar para lista", use_container_width=True, key="btn_voltar_lista_novo"):
            st.session_state["usuarios_modo"] = "Listar"
            st.experimental_rerun()


def form_editar_usuario() -> None:
    st.subheader("✏️ Editar usuário")

    df = load_users()
    if df.empty:
        st.info("Não há usuários para editar.")
        return

    opcoes = {
        row["username"]: f"{row['username']} - {row['nome']}"
        for _, row in df.iterrows()
    }

    username_sel = st.selectbox(
        "Selecione o usuário:",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes.get(x, x),
        key="usuarios_edit_sel",
    )

    row = df[df["username"] == username_sel].iloc[0]

    st.markdown(f"**Login:** `{row['username']}`")

    nome_edit = st.text_input("Nome completo", value=row["nome"])
    perfil_edit = st.selectbox(
        "Perfil de acesso",
        PERFIS_DISPONIVEIS,
        index=PERFIS_DISPONIVEIS.index(row["perfil"])
        if row["perfil"] in PERFIS_DISPONIVEIS
        else 0,
    )
    ativo_edit = st.checkbox("Usuário ativo?", value=bool(row["ativo"]))
    must_change_edit = st.checkbox(
        "Solicitar troca de senha no próximo login?",
        value=bool(row["must_change"]),
    )
    nova_senha = st.text_input(
        "Nova senha (deixe em branco para manter a atual)",
        type="password",
    )

    colb1, colb2 = st.columns(2)
    with colb1:
        if st.button("💾 Salvar alterações", use_container_width=True, key="btn_salvar_usuario_edit"):
            mask = df["username"] == username_sel
            if not mask.any():
                st.error("Usuário não encontrado para atualização.")
                return

            df.loc[mask, "nome"] = nome_edit.strip()
            df.loc[mask, "perfil"] = perfil_edit
            df.loc[mask, "ativo"] = 1 if ativo_edit else 0
            df.loc[mask, "must_change"] = 1 if must_change_edit else 0

            if nova_senha.strip():
                df.loc[mask, "senha_hash"] = hash_password(nova_senha.strip())
                df.loc[mask, "must_change"] = 1  # força trocar após reset

            save_users(df)
            st.success("Usuário atualizado com sucesso!")

    with colb2:
        if st.button("↩ Voltar para lista", use_container_width=True, key="btn_voltar_lista_edit"):
            st.session_state["usuarios_modo"] = "Listar"
            st.experimental_rerun()


def form_excluir_usuario() -> None:
    st.subheader("🗑️ Excluir usuário")

    df = load_users()
    if df.empty:
        st.info("Não há usuários para excluir.")
        return

    opcoes = {
        row["username"]: f"{row['username']} - {row['nome']}"
        for _, row in df.iterrows()
    }

    username_sel = st.selectbox(
        "Selecione o usuário para excluir:",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes.get(x, x),
        key="usuarios_del_sel",
    )

    st.warning(
        f"Esta ação irá remover definitivamente o usuário **{opcoes[username_sel]}**."
    )
    confirmar = st.checkbox("Confirmo que desejo excluir este usuário.")

    colb1, colb2 = st.columns(2)
    with colb1:
        if st.button("🗑️ Excluir usuário", use_container_width=True, key="btn_excluir_usuario"):
            if not confirmar:
                st.error("Marque a opção de confirmação para excluir.")
                return

            df = df[df["username"] != username_sel]
            save_users(df)
            st.success("Usuário excluído com sucesso!")

    with colb2:
        if st.button("↩ Voltar para lista", use_container_width=True, key="btn_voltar_lista_del"):
            st.session_state["usuarios_modo"] = "Listar"
            st.experimental_rerun()


# ==========================================
# RUN (PONTO DE ENTRADA)
# ==========================================

def run() -> None:
    """
    Tela de manutenção de usuários.
    Apenas perfil MASTER deveria ver este módulo (o menu já restringe),
    mas aqui garantimos mais uma vez.
    """
    role = st.session_state.get("auth_role", "MASTER")
    if role != "MASTER":
        st.error("Apenas usuários com perfil MASTER podem gerenciar usuários.")
        return

    st.header("👥 Cadastro de Usuários")

    # Estado de modo (Listar / Novo / Editar / Excluir)
    if "usuarios_modo" not in st.session_state:
        st.session_state["usuarios_modo"] = "Listar"

    modo = st.session_state["usuarios_modo"]

    # Barra de ações (botões no topo)
    st.markdown('<div class="glass-actions-row">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📋 Listar usuários", use_container_width=True, key="btn_usuarios_listar"):
            st.session_state["usuarios_modo"] = "Listar"
            modo = "Listar"
    with col2:
        if st.button("➕ Novo usuário", use_container_width=True, key="btn_usuarios_novo"):
            st.session_state["usuarios_modo"] = "Novo"
            modo = "Novo"
    with col3:
        if st.button("✏️ Editar usuário", use_container_width=True, key="btn_usuarios_editar"):
            st.session_state["usuarios_modo"] = "Editar"
            modo = "Editar"
    with col4:
        if st.button("🗑️ Excluir usuário", use_container_width=True, key="btn_usuarios_excluir"):
            st.session_state["usuarios_modo"] = "Excluir"
            modo = "Excluir"

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"**Modo atual:** {modo}")
    st.markdown("---")

    # MODO LISTAR
    if modo == "Listar":
        df = load_users()
        if df.empty:
            st.info("Nenhum usuário cadastrado ainda.")
            return

        df_view = df.copy()
        # Exibe sem a coluna de senha_hash
        if "senha_hash" in df_view.columns:
            df_view = df_view.drop(columns=["senha_hash"])

        render_tabela_html(
            df_view,
            columns=["username", "nome", "perfil", "must_change", "ativo"],
            headers=["Login", "Nome", "Perfil", "Trocar senha?", "Ativo"],
        )
        return

    # MODO NOVO
    if modo == "Novo":
        form_novo_usuario()
        return

    # MODO EDITAR
    if modo == "Editar":
        form_editar_usuario()
        return

    # MODO EXCLUIR
    if modo == "Excluir":
        form_excluir_usuario()
        return


