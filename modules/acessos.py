from datetime import datetime

import streamlit as st

from .core import (
    carregar_acessos,
    registrar_acesso,
    LOG_ACESSOS,
    carregar_clientes,
    carregar_candidatos,
)


def run():
    st.header("🔐 Gerenciador de Acessos (Sistemas)")

    df_cli = carregar_clientes()
    df_cand = carregar_candidatos()

    st.subheader("Novo acesso")

    col1, col2 = st.columns(2)
    with col1:
        if df_cli.empty:
            st.warning("Cadastre clientes para vincular acessos.")
            id_cliente = ""
            nome_cliente = ""
        else:
            op_cli = {
                int(row["id_cliente"]): row["nome_cliente"]
                for _, row in df_cli.iterrows()
            }
            id_cli_sel = st.selectbox(
                "Cliente (opcional):",
                options=["(Sem cliente)"] + list(op_cli.keys()),
                format_func=lambda x: op_cli[x] if x != "(Sem cliente)" else x,
            )
            if id_cli_sel == "(Sem cliente)":
                id_cliente = ""
                nome_cliente = ""
            else:
                id_cliente = str(id_cli_sel)
                nome_cliente = op_cli[id_cli_sel]

        if df_cand.empty:
            id_candidato = ""
            nome_usuario = st.text_input("Nome do usuário")
        else:
            op_cand = {
                int(row["id_candidato"]): row["nome"]
                for _, row in df_cand.iterrows()
            }
            id_cand_sel = st.selectbox(
                "Candidato vinculado (opcional):",
                options=["(Nenhum)"] + list(op_cand.keys()),
                format_func=lambda x: op_cand[x] if x != "(Nenhum)" else x,
            )
            if id_cand_sel == "(Nenhum)":
                id_candidato = ""
                nome_usuario = st.text_input("Nome do usuário")
            else:
                id_candidato = str(id_cand_sel)
                nome_usuario = st.text_input("Nome do usuário", value=op_cand[id_cand_sel])

    with col2:
        sistema = st.selectbox(
            "Sistema / Ferramenta",
            [
                "Senior Sapiens",
                "Senior HCM",
                "Senior Ronda",
                "Power BI",
                "Banco de Dados",
                "Outros",
            ],
        )
        tipo_acesso = st.selectbox(
            "Tipo de acesso",
            ["Usuário", "Administrador", "Temporário", "Consulta"],
        )
        data_inicio = st.date_input("Data de início", value=datetime.today()).strftime("%Y-%m-%d")
        data_fim = st.date_input("Data de término (opcional)", value=datetime.today()).strftime("%Y-%m-%d")
        status = st.selectbox(
            "Status",
            ["Ativo", "Revogado", "Pendente"],
        )

    observacoes = st.text_area("Observações do acesso", height=80)

    if st.button("💾 Registrar acesso"):
        if not nome_usuario.strip():
            st.error("Informe o nome do usuário.")
        else:
            novo_id = registrar_acesso(
                id_cliente=id_cliente,
                nome_cliente=nome_cliente,
                id_candidato=id_candidato,
                nome_usuario=nome_usuario.strip(),
                sistema=sistema,
                tipo_acesso=tipo_acesso,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status,
                observacoes=observacoes.strip(),
            )
            st.success(f"Acesso registrado com ID {novo_id}.")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Acessos cadastrados (com filtros)")

    df = carregar_acessos()
    if df.empty:
        st.info("Nenhum acesso cadastrado ainda.")
        return

    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        cli_filtro = st.text_input("Filtrar por cliente (contém)")
    with colf2:
        sist_filtro = st.text_input("Filtrar por sistema (contém)")
    with colf3:
        status_filtro = st.selectbox(
            "Filtrar por status",
            ["(Todos)", "Ativo", "Revogado", "Pendente"],
        )

    df_view = df.copy()
    if cli_filtro.strip():
        df_view = df_view[df_view["nome_cliente"].str.lower().str.contains(cli_filtro.strip().lower())]
    if sist_filtro.strip():
        df_view = df_view[df_view["sistema"].str.lower().str.contains(sist_filtro.strip().lower())]
    if status_filtro != "(Todos)":
        df_view = df_view[df_view["status"] == status_filtro]

    df_view = df_view.sort_values("id_acesso")

    edited = st.data_editor(
        df_view,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "id_acesso": st.column_config.Column("ID", disabled=True),
        },
        key="acessos_editor",
    )

    if st.button("💾 Salvar alterações dos acessos"):
        try:
            # precisamos unir com os registros não filtrados
            df_total = carregar_acessos()
            # atualiza linha a linha
            for idx, row_e in edited.iterrows():
                mask = df_total["id_acesso"] == str(row_e["id_acesso"])
                df_total.loc[mask, :] = row_e
            df_total.to_csv(LOG_ACESSOS, sep=";", index=False, encoding="utf-8")
            st.success("Acessos atualizados com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar acessos: {e}")
