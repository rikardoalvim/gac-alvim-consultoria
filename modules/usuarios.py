import streamlit as st
import pandas as pd
from datetime import datetime

from . import auth  # usamos o mesmo arquivo de usuários do auth


def run():
    st.header("👥 Administração de Usuários")

    # Apenas admin pode acessar
    user = st.session_state.get("user")
    if not user or not user.get("is_admin", False):
        st.error("Apenas usuários administradores podem acessar esta área.")
        return

    df = auth.carregar_usuarios()

    # =======================
    # Cadastro de novo usuário
    # =======================
    st.subheader("➕ Novo usuário")

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Usuário (login)", key="novo_username")
        nome = st.text_input("Nome completo", key="novo_nome")
    with col2:
        is_admin = st.checkbox("Usuário administrador", value=False)
        ativo = st.checkbox("Ativo", value=True)

    if st.button("💾 Criar usuário", use_container_width=True):
        if not username.strip() or not nome.strip():
            st.error("Informe usuário e nome.")
        else:
            if not df.empty and username in df["username"].tolist():
                st.error("Já existe um usuário com esse login.")
            else:
                agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                nova_linha = {
                    "username": username.strip(),
                    "nome": nome.strip(),
                    "senha_hash": auth.hash_senha("2025"),
                    "deve_trocar_senha": "1",  # força troca no 1º acesso
                    "is_admin": "1" if is_admin else "0",
                    "ativo": "1" if ativo else "0",
                    "criado_em": agora,
                }
                df = auth.carregar_usuarios()
                df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
                auth.salvar_usuarios(df)
                st.success(f"Usuário {username} criado com senha padrão '2025' (troca obrigatória no primeiro acesso).")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("📋 Usuários cadastrados")

    df = auth.carregar_usuarios()
    if df.empty:
        st.info("Nenhum usuário cadastrado.")
        return

    # Visualização
    df_view = df.copy()
    df_view["is_admin"] = df_view["is_admin"].map({"1": "Sim", "0": "Não"})
    df_view["ativo"] = df_view["ativo"].map({"1": "Sim", "0": "Não"})

    st.dataframe(
        df_view[["username", "nome", "is_admin", "ativo", "deve_trocar_senha", "criado_em"]],
        use_container_width=True,
    )

    st.markdown("### ✏️ Ações rápidas")

    usuarios_lista = df["username"].tolist()
    if not usuarios_lista:
        return

    colA, colB, colC = st.columns(3)

    with colA:
        user_sel = st.selectbox("Selecione o usuário:", usuarios_lista)

    with colB:
        if st.button("🔁 Resetar senha p/ '2025'", use_container_width=True):
            df = auth.carregar_usuarios()
            mask = df["username"] == user_sel
            if not mask.any():
                st.error("Usuário não encontrado.")
            else:
                df.loc[mask, "senha_hash"] = auth.hash_senha("2025")
                df.loc[mask, "deve_trocar_senha"] = "1"
                auth.salvar_usuarios(df)
                st.success(f"Senha do usuário {user_sel} resetada para '2025' (troca obrigatória no próximo login).")
                st.experimental_rerun()

    with colC:
        colC1, colC2 = st.columns(2)
        with colC1:
            if st.button("Ativar", use_container_width=True):
                df = auth.carregar_usuarios()
                mask = df["username"] == user_sel
                df.loc[mask, "ativo"] = "1"
                auth.salvar_usuarios(df)
                st.success(f"Usuário {user_sel} ativado.")
                st.experimental_rerun()
        with colC2:
            if st.button("Desativar", use_container_width=True):
                df = auth.carregar_usuarios()
                mask = df["username"] == user_sel
                df.loc[mask, "ativo"] = "0"
                auth.salvar_usuarios(df)
                st.success(f"Usuário {user_sel} desativado.")
                st.experimental_rerun()
