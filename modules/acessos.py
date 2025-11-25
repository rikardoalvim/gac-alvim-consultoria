from datetime import datetime
import streamlit as st
import pandas as pd

from .core import (
    carregar_acessos,
    registrar_acesso,
    LOG_ACESSOS,
    carregar_clientes,
    carregar_candidatos,
)


# --------------------------------------------------------
# Função principal
# --------------------------------------------------------
def run():
    st.header("🔐 Gerenciador de Acessos")

    # ----------------------------------------------------
    # Controle de modo (padrão: listar)
    # ----------------------------------------------------
    if "acessos_modo" not in st.session_state:
        st.session_state["acessos_modo"] = "Listar"

    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("📋 Listar acessos", use_container_width=True):
            st.session_state["acessos_modo"] = "Listar"
    with colB:
        if st.button("➕ Novo acesso", use_container_width=True):
            st.session_state["acessos_modo"] = "Novo"
    with colC:
        if st.button("✏️ Editar acesso", use_container_width=True):
            st.session_state["acessos_modo"] = "Editar"

    st.markdown("---")
    modo = st.session_state["acessos_modo"]

    # ----------------------------------------------------
    # 1) LISTAR ACESSOS
    # ----------------------------------------------------
    if modo == "Listar":
        st.subheader("📋 Lista de acessos")

        df = carregar_acessos()
        if df.empty:
            st.info("Nenhum acesso cadastrado ainda.")
            return

        colf1, colf2, colf3 = st.columns(3)
        with colf1:
            cli_filtro = st.text_input("Filtrar por Cliente (contém)")
        with colf2:
            sist_filtro = st.text_input("Filtrar por Sistema (contém)")
        with colf3:
            status_filtro = st.selectbox(
                "Filtrar por Status",
                ["(Todos)", "Ativo", "Revogado", "Pendente"],
            )

        df_view = df.copy()

        if cli_filtro.strip():
            df_view = df_view[
                df_view["nome_cliente"].str.lower().str.contains(cli_filtro.lower())
            ]

        if sist_filtro.strip():
            df_view = df_view[
                df_view["sistema"].str.lower().str.contains(sist_filtro.lower())
            ]

        if status_filtro != "(Todos)":
            df_view = df_view[df_view["status"] == status_filtro]

        df_view = df_view.sort_values("id_acesso")
        st.dataframe(df_view, use_container_width=True)

        return

    # ----------------------------------------------------
    # 2) NOVO ACESSO
    # ----------------------------------------------------
    if modo == "Novo":
        st.subheader("➕ Registrar novo acesso")

        df_cli = carregar_clientes()
        df_cand = carregar_candidatos()

        col1, col2 = st.columns(2)

        # ---------------------
        # Dados do Cliente
        # ---------------------
        with col1:
            if df_cli.empty:
                st.warning("Nenhum cliente cadastrado.")
                id_cliente = ""
                nome_cliente = ""
            else:
                op = {int(r["id_cliente"]): r["nome_cliente"] for _, r in df_cli.iterrows()}
                escolha = st.selectbox(
                    "Cliente (opcional):",
                    options=["(Sem cliente)"] + list(op.keys()),
                    format_func=lambda x: op[x] if x != "(Sem cliente)" else x,
                )
                if escolha == "(Sem cliente)":
                    id_cliente = ""
                    nome_cliente = ""
                else:
                    id_cliente = str(escolha)
                    nome_cliente = op[escolha]

            # ---------------------
            # Candidato
            # ---------------------
            if df_cand.empty:
                id_candidato = ""
                nome_usuario = st.text_input("Nome do usuário")
            else:
                op2 = {int(r["id_candidato"]): r["nome"] for _, r in df_cand.iterrows()}
                cand_sel = st.selectbox(
                    "Candidato vinculado (opcional):",
                    options=["(Nenhum)"] + list(op2.keys()),
                    format_func=lambda x: op2[x] if x != "(Nenhum)" else x,
                )
                if cand_sel == "(Nenhum)":
                    id_candidato = ""
                    nome_usuario = st.text_input("Nome do usuário")
                else:
                    id_candidato = str(cand_sel)
                    nome_usuario = st.text_input("Nome do usuário", value=op2[cand_sel])

        # ---------------------
        # Dados do Acesso
        # ---------------------
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
            data_inicio = st.date_input("Data início", value=datetime.today()).strftime("%Y-%m-%d")
            data_fim = st.date_input("Data término (opcional)", value=datetime.today()).strftime("%Y-%m-%d")
            status = st.selectbox("Status", ["Ativo", "Revogado", "Pendente"])

        observacoes = st.text_area("Observações do acesso", height=90)

        colb1, colb2 = st.columns(2)
        with colb1:
            if st.button("💾 Registrar acesso", use_container_width=True):
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
                    st.success(f"Acesso registrado (ID {novo_id}).")
                    st.session_state["acessos_modo"] = "Listar"
                    st.rerun()

        with colb2:
            if st.button("⬅ Voltar", use_container_width=True):
                st.session_state["acessos_modo"] = "Listar"
                st.rerun()

        return

    # ----------------------------------------------------
    # 3) EDITAR ACESSO (formulário padrão)
    # ----------------------------------------------------
    if modo == "Editar":
        st.subheader("✏️ Editar acesso")

        df = carregar_acessos()
        df_cli = carregar_clientes()
        df_cand = carregar_candidatos()

        if df.empty:
            st.info("Nenhum acesso para editar.")
            return

        # Escolha do acesso
        opcoes = {
            int(r["id_acesso"]): f"{r['id_acesso']} - {r['nome_usuario']} - {r['sistema']}"
            for _, r in df.iterrows()
        }

        id_sel = st.selectbox(
            "Selecione o acesso:",
            options=list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
        )

        row = df[df["id_acesso"] == str(id_sel)].iloc[0]

        col1, col2 = st.columns(2)

        # ---------------------
        # Cliente
        # ---------------------
        with col1:
            if df_cli.empty:
                id_cliente = ""
                nome_cliente = ""
            else:
                op_cli = {int(r["id_cliente"]): r["nome_cliente"] for _, r in df_cli.iterrows()}
                id_cli_atual = row["id_cliente"] if row["id_cliente"] else "(Sem cliente)"

                id_cli_edit = st.selectbox(
                    "Cliente:",
                    options=["(Sem cliente)"] + list(op_cli.keys()),
                    index=0 if id_cli_atual == "" else list(op_cli.keys()).index(int(id_cli_atual)) + 1,
                    format_func=lambda x: op_cli[x] if x != "(Sem cliente)" else x,
                )

                if id_cli_edit == "(Sem cliente)":
                    id_cliente = ""
                    nome_cliente = ""
                else:
                    id_cliente = str(id_cli_edit)
                    nome_cliente = op_cli[id_cli_edit]

        # ---------------------
        # Candidato
        # ---------------------
        with col2:
            if df_cand.empty:
                id_candidato = ""
                nome_usuario = st.text_input("Nome do usuário", value=row["nome_usuario"])
            else:
                op_c = {int(r["id_candidato"]): r["nome"] for _, r in df_cand.iterrows()}
                id_cand_atual = row["id_candidato"] if row["id_candidato"] else "(Nenhum)"

                id_cand_edit = st.selectbox(
                    "Candidato vinculado:",
                    options=["(Nenhum)"] + list(op_c.keys()),
                    index=0 if id_cand_atual == "" else list(op_c.keys()).index(int(id_cand_atual)) + 1,
                    format_func=lambda x: op_c[x] if x != "(Nenhum)" else x,
                )

                if id_cand_edit == "(Nenhum)":
                    id_candidato = ""
                    nome_usuario = st.text_input("Nome do usuário", value=row["nome_usuario"])
                else:
                    id_candidato = str(id_cand_edit)
                    nome_usuario = st.text_input("Nome do usuário", value=op_c[id_cand_edit])

        # ---------------------
        # Dados do Acesso
        # ---------------------
           

        col2_1, col2_2 = st.columns(2)
        with col2_1:
            sistema = st.selectbox(
                "Sistema",
                [
                    "Senior Sapiens",
                    "Senior HCM",
                    "Senior Ronda",
                    "Power BI",
                    "Banco de Dados",
                    "Outros",
                ],
                index=[
                    "Senior Sapiens",
                    "Senior HCM",
                    "Senior Ronda",
                    "Power BI",
                    "Banco de Dados",
                    "Outros",
                ].index(row["sistema"]),
            )

            tipo_acesso = st.selectbox(
                "Tipo de acesso",
                ["Usuário", "Administrador", "Temporário", "Consulta"],
                index=["Usuário", "Administrador", "Temporário", "Consulta"].index(row["tipo_acesso"]),
            )

        with col2_2:
            try:
                data_inicio_dt = datetime.strptime(row["data_inicio"], "%Y-%m-%d").date()
            except:
                data_inicio_dt = datetime.today().date()

            try:
                data_fim_dt = datetime.strptime(row["data_fim"], "%Y-%m-%d").date()
            except:
                data_fim_dt = datetime.today().date()

            data_inicio = st.date_input("Data início", value=data_inicio_dt)
            data_fim = st.date_input("Data término", value=data_fim_dt)

            status = st.selectbox(
                "Status",
                ["Ativo", "Revogado", "Pendente"],
                index=["Ativo", "Revogado", "Pendente"].index(row["status"]),
            )

        observacoes = st.text_area("Observações", value=row["observacoes"], height=100)

        colb1, colb2 = st.columns(2)

        with colb1:
            if st.button("💾 Salvar alterações", use_container_width=True):
                df_edit = carregar_acessos()
                mask = df_edit["id_acesso"] == str(id_sel)

                df_edit.loc[mask, "id_cliente"] = id_cliente
                df_edit.loc[mask, "nome_cliente"] = nome_cliente
                df_edit.loc[mask, "id_candidato"] = id_candidato
                df_edit.loc[mask, "nome_usuario"] = nome_usuario
                df_edit.loc[mask, "sistema"] = sistema
                df_edit.loc[mask, "tipo_acesso"] = tipo_acesso
                df_edit.loc[mask, "data_inicio"] = data_inicio.strftime("%Y-%m-%d")
                df_edit.loc[mask, "data_fim"] = data_fim.strftime("%Y-%m-%d")
                df_edit.loc[mask, "status"] = status
                df_edit.loc[mask, "observacoes"] = observacoes

                df_edit.to_csv(LOG_ACESSOS, sep=";", index=False, encoding="utf-8")

                st.success("Acesso atualizado!")
                st.session_state["acessos_modo"] = "Listar"
                st.rerun()

        with colb2:
            if st.button("⬅ Voltar", use_container_width=True):
                st.session_state["acessos_modo"] = "Listar"
                st.rerun()
