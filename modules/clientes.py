import streamlit as st
import pandas as pd

from .core import carregar_clientes, registrar_cliente, LOG_CLIENTES


def run():
    st.header("🏢 Cadastro de Clientes")

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
    st.subheader("📋 Clientes cadastrados")

    df = carregar_clientes()
    if df.empty:
        st.info("Nenhum cliente cadastrado ainda.")
        return

    df = df.sort_values("id_cliente")
    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "id_cliente": st.column_config.Column("ID", disabled=True),
        },
        key="clientes_editor",
    )

    if st.button("💾 Salvar alterações de clientes"):
        try:
            edited.to_csv(LOG_CLIENTES, sep=";", index=False, encoding="utf-8")
            st.success("Clientes atualizados com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar clientes: {e}")
