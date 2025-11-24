import streamlit as st

from .core import carregar_clientes, registrar_cliente, LOG_CLIENTES


def run():
    st.header("🏢 Cadastro de Clientes")

    # ============================
    # NOVO CLIENTE
    # ============================
    st.subheader("➕ Novo cliente")

    col1, col2 = st.columns(2)
    with col1:
        nome_cliente = st.text_input("Nome do cliente (fantasia)")
        razao_social = st.text_input("Razão social")
        cnpj = st.text_input("CNPJ")
        cidade = st.text_input("Cidade / UF")
    with col2:
        contato = st.text_input("Contato principal")
        telefone = st.text_input("Telefone")
        email = st.text_input("E-mail")
        observacoes = st.text_area("Observações gerais", height=80)

    if st.button("💾 Salvar cliente"):
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
            st.rerun()

    st.markdown("---")

    # ============================
    # LISTA DE CLIENTES
    # ============================
    st.subheader("📋 Clientes cadastrados")

    df = carregar_clientes()
    if df.empty:
        st.info("Nenhum cliente cadastrado ainda.")
        return

    df_view = df.sort_values("id_cliente")
    st.dataframe(df_view, use_container_width=True)

    st.markdown("---")

    # ============================
    # EDIÇÃO DE CLIENTE EXISTENTE
    # ============================
    st.subheader("✏️ Editar cliente existente")

    opcoes = {
        row["id_cliente"]: f"{row['id_cliente']} - {row['nome_cliente']}"
        for _, row in df_view.iterrows()
    }

    id_sel = st.selectbox(
        "Selecione o cliente para editar:",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
    )

    row_sel = df_view[df_view["id_cliente"] == id_sel].iloc[0]

    col3, col4 = st.columns(2)
    with col3:
        nome_edit = st.text_input("Nome do cliente (fantasia)", value=row_sel["nome_cliente"])
        razao_edit = st.text_input("Razão social", value=row_sel["razao_social"])
        cnpj_edit = st.text_input("CNPJ", value=row_sel["cnpj"])
        cidade_edit = st.text_input("Cidade / UF", value=row_sel["cidade"])
    with col4:
        contato_edit = st.text_input("Contato principal", value=row_sel["contato_principal"])
        telefone_edit = st.text_input("Telefone", value=row_sel["telefone"])
        email_edit = st.text_input("E-mail", value=row_sel["email"])
        observ_edit = st.text_area("Observações gerais", value=row_sel["observacoes"], height=80)

    if st.button("💾 Salvar alterações do cliente selecionado"):
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
            st.rerun()
