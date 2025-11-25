import streamlit as st
from .core import carregar_clientes, registrar_cliente, LOG_CLIENTES


def run():
    st.header("🏢 Cadastro de Clientes")

    # ============================
    # CONTROLE DE MODO
    # ============================
    if "clientes_modo" not in st.session_state:
        st.session_state["clientes_modo"] = "Listar"

    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        if st.button("📋 Listar", use_container_width=True):
            st.session_state["clientes_modo"] = "Listar"
    with col_a2:
        if st.button("➕ Inserir", use_container_width=True):
            st.session_state["clientes_modo"] = "Inserir"
    with col_a3:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state["clientes_modo"] = "Editar"

    modo = st.session_state["clientes_modo"]
    st.markdown(f"**Modo atual:** {modo}")
    st.markdown("---")

    # Carrega clientes uma vez
    df = carregar_clientes()

    # ============================
    # MODO: LISTAR
    # ============================
    if modo == "Listar":
        st.subheader("📋 Clientes cadastrados")

        if df.empty:
            st.info("Nenhum cliente cadastrado ainda.")
            return

        df_view = df.sort_values("id_cliente")
        st.dataframe(df_view, use_container_width=True)

        # Detalhe opcional de um cliente
        st.markdown("### 🔍 Detalhes do cliente")
        opcoes = {
            row["id_cliente"]: f"{row['id_cliente']} - {row['nome_cliente']}"
            for _, row in df_view.iterrows()
        }

        id_sel = st.selectbox(
            "Selecione para visualizar detalhes:",
            options=list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
            key="cliente_det_sel",
        )

        row_sel = df_view[df_view["id_cliente"] == id_sel].iloc[0]
        st.markdown(
            f"""
            **Nome:** {row_sel['nome_cliente']}  
            **Razão social:** {row_sel['razao_social']}  
            **CNPJ:** {row_sel['cnpj']}  
            **Cidade:** {row_sel['cidade']}  
            **Contato principal:** {row_sel['contato_principal']}  
            **Telefone:** {row_sel['telefone']}  
            **E-mail:** {row_sel['email']}  
            **Observações:** {row_sel['observacoes']}
            """
        )
        return

    # ============================
    # MODO: INSERIR (NOVO CLIENTE)
    # ============================
    if modo == "Inserir":
        st.subheader("➕ Novo cliente")

        col1, col2 = st.columns(2)
        with col1:
            nome_cliente = st.text_input(
                "Nome do cliente (fantasia)",
                key="nome_cliente_novo",
            )
            razao_social = st.text_input(
                "Razão social",
                key="razao_social_novo",
            )
            cnpj = st.text_input(
                "CNPJ",
                key="cnpj_novo",
            )
            cidade = st.text_input(
                "Cidade / UF",
                key="cidade_novo",
            )
        with col2:
            contato = st.text_input(
                "Contato principal",
                key="contato_principal_novo",
            )
            telefone = st.text_input(
                "Telefone",
                key="telefone_novo",
            )
            email = st.text_input(
                "E-mail",
                key="email_novo",
            )
            observacoes = st.text_area(
                "Observações gerais",
                height=80,
                key="observacoes_novo",
            )

        col_b1, col_b2 = st.columns([1, 1])
        with col_b1:
            if st.button("💾 Salvar cliente", key="btn_salvar_cliente_novo", use_container_width=True):
                if not nome_cliente.strip():
                    st.error("Informe ao menos o nome do cliente.")
                else:
                    novo_id = registrar_cliente(
                        nome_cliente.strip(),
                        razao_social.strip(),
                        cnpj.strip(),
                        cidade.strip(),
                        contato.strip(),
                        telefone.strip(),
                        email.strip(),
                        observacoes.strip(),
                    )
                    st.success(f"Cliente cadastrado com ID {novo_id}.")
                    st.session_state["clientes_modo"] = "Listar"
                    st.rerun()
        with col_b2:
            if st.button("⬅ Voltar para lista", use_container_width=True):
                st.session_state["clientes_modo"] = "Listar"
                st.rerun()

        return

    # ============================
    # MODO: EDITAR
    # ============================
    if modo == "Editar":
        st.subheader("✏️ Editar cliente existente")

        if df.empty:
            st.info("Nenhum cliente cadastrado para editar.")
            return

        df_view = df.sort_values("id_cliente")
        opcoes = {
            row["id_cliente"]: f"{row['id_cliente']} - {row['nome_cliente']}"
            for _, row in df_view.iterrows()
        }

        id_sel = st.selectbox(
            "Selecione o cliente para editar:",
            options=list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
            key="cliente_edit_sel",
        )

        row_sel = df_view[df_view["id_cliente"] == id_sel].iloc[0]

        col3, col4 = st.columns(2)
        with col3:
            nome_edit = st.text_input(
                "Nome do cliente (fantasia)",
                value=row_sel["nome_cliente"],
                key=f"nome_cliente_edit_{id_sel}",
            )
            razao_edit = st.text_input(
                "Razão social",
                value=row_sel["razao_social"],
                key=f"razao_social_edit_{id_sel}",
            )
            cnpj_edit = st.text_input(
                "CNPJ",
                value=row_sel["cnpj"],
                key=f"cnpj_edit_{id_sel}",
            )
            cidade_edit = st.text_input(
                "Cidade / UF",
                value=row_sel["cidade"],
                key=f"cidade_edit_{id_sel}",
            )
        with col4:
            contato_edit = st.text_input(
                "Contato principal",
                value=row_sel["contato_principal"],
                key=f"contato_principal_edit_{id_sel}",
            )
            telefone_edit = st.text_input(
                "Telefone",
                value=row_sel["telefone"],
                key=f"telefone_edit_{id_sel}",
            )
            email_edit = st.text_input(
                "E-mail",
                value=row_sel["email"],
                key=f"email_edit_{id_sel}",
            )
            observ_edit = st.text_area(
                "Observações gerais",
                value=row_sel["observacoes"],
                height=80,
                key=f"observacoes_edit_{id_sel}",
            )

        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            if st.button(
                "💾 Salvar alterações do cliente selecionado",
                key=f"btn_salvar_cliente_edit_{id_sel}",
                use_container_width=True,
            ):
                df_total = carregar_clientes()
                mask = df_total["id_cliente"] == id_sel
                if not mask.any():
                    st.error("Cliente não encontrado para atualização.")
                else:
                    df_total.loc[mask, "nome_cliente"] = nome_edit
                    df_total.loc[mask, "razao_social"] = razao_edit
                    df_total.loc[mask, "cnpj"] = cnpj_edit
                    df_total.loc[mask, "cidade"] = cidade_edit
                    df_total.loc[mask, "contato_principal"] = contato_edit
                    df_total.loc[mask, "telefone"] = telefone_edit
                    df_total.loc[mask, "email"] = email_edit
                    df_total.loc[mask, "observacoes"] = observ_edit

                    df_total.to_csv(LOG_CLIENTES, sep=";", index=False, encoding="utf-8")
                    st.success("Cliente atualizado com sucesso!")
                    st.session_state["clientes_modo"] = "Listar"
                    st.rerun()
        with col_c2:
            if st.button("⬅ Voltar para lista", use_container_width=True):
                st.session_state["clientes_modo"] = "Listar"
                st.rerun()


