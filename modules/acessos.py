from datetime import date

import pandas as pd
import streamlit as st

from .database import (
    listar_clientes,
    listar_candidatos,
    listar_acessos,
    obter_acesso,
    inserir_acesso,
    atualizar_acesso,
)


def render_tabela_html(df, columns, headers):
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    html = ["<table>"]
    html.append("<thead><tr>")
    for h in headers:
        html.append(f"<th>{h}</th>")
    html.append("</tr></thead><tbody>")

    for _, row in df[columns].iterrows():
        html.append("<tr>")
        for col in columns:
            html.append(f"<td>{row[col]}</td>")
        html.append("</tr>")

    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)


def run():
    st.header("🔑 Acessos a Sistemas")

    if "acesso_edit_id" not in st.session_state:
        st.session_state["acesso_edit_id"] = None

    colL, colR = st.columns([1.1, 1.4])

    # =========================
    # Lado esquerdo: lista
    # =========================
    with colL:
        st.subheader("Registros de acesso")

        dados = listar_acessos()
        if dados:
            df = pd.DataFrame(dados).fillna("")
            render_tabela_html(
                df,
                columns=["id_acesso", "nome_cliente", "nome_usuario", "sistema", "status"],
                headers=["ID", "Cliente", "Usuário", "Sistema", "Status"],
            )

            st.markdown("---")
            ids = [int(r["id_acesso"]) for r in dados]
            labels = {
                int(r["id_acesso"]): f"{r['id_acesso']} - {r.get('nome_cliente','')} ({r.get('sistema','')})"
                for r in dados
            }
            id_sel = st.selectbox(
                "Carregar acesso existente:",
                ["(Novo)"] + ids,
                format_func=lambda x: labels.get(x, "(Novo)") if x != "(Novo)" else "(Novo)",
                key="acesso_sel",
            )
            if id_sel != "(Novo)":
                st.session_state["acesso_edit_id"] = int(id_sel)
            else:
                st.session_state["acesso_edit_id"] = None
        else:
            st.info("Nenhum acesso cadastrado ainda.")
            st.session_state["acesso_edit_id"] = None

    # =========================
    # Lado direito: formulário
    # =========================
    with colR:
        st.subheader("Cadastro / edição de acesso")

        clientes = listar_clientes()
        candidatos = listar_candidatos()

        df_cli = pd.DataFrame(clientes).fillna("") if clientes else pd.DataFrame(columns=["id_cliente", "nome_cliente"])
        df_cand = pd.DataFrame(candidatos).fillna("") if candidatos else pd.DataFrame(
            columns=["id_candidato", "nome"]
        )

        op_cli = {int(r["id_cliente"]): r["nome_cliente"] for _, r in df_cli.iterrows()} if not df_cli.empty else {}
        op_cand = {int(r["id_candidato"]): r["nome"] for _, r in df_cand.iterrows()} if not df_cand.empty else {}

        registro = None
        if st.session_state["acesso_edit_id"]:
            registro = obter_acesso(st.session_state["acesso_edit_id"])

        # valores iniciais
        id_cliente_ini = None
        id_candidato_ini = None
        nome_cliente_ini = ""
        nome_usuario_ini = ""
        sistema_ini = "Senior"
        tipo_ini = ""
        status_ini = "Ativo"
        data_ini_ini = date.today()
        data_fim_ini = None
        obs_ini = ""

        if registro:
            id_cliente_ini = registro.get("id_cliente")
            id_candidato_ini = registro.get("id_candidato")
            nome_cliente_ini = registro.get("nome_cliente", "")
            nome_usuario_ini = registro.get("nome_usuario", "")
            sistema_ini = registro.get("sistema", "") or "Senior"
            tipo_ini = registro.get("tipo_acesso", "") or ""
            status_ini = registro.get("status", "") or "Ativo"
            try:
                if registro.get("data_inicio"):
                    data_ini_ini = date.fromisoformat(registro["data_inicio"])
            except Exception:
                data_ini_ini = date.today()
            try:
                if registro.get("data_fim"):
                    data_fim_ini = date.fromisoformat(registro["data_fim"])
            except Exception:
                data_fim_ini = None
            obs_ini = registro.get("observacoes", "")

        # Cliente
        col1, col2 = st.columns(2)
        with col1:
            if op_cli:
                id_cliente_sel = st.selectbox(
                    "Cliente",
                    list(op_cli.keys()),
                    index=list(op_cli.keys()).index(int(id_cliente_ini))
                    if id_cliente_ini in op_cli
                    else 0,
                    format_func=lambda x: op_cli[x],
                )
                nome_cliente_sel = op_cli[id_cliente_sel]
            else:
                id_cliente_sel = None
                nome_cliente_sel = st.text_input("Cliente (texto livre)", value=nome_cliente_ini)

        with col2:
            if op_cand:
                id_cand_sel = st.selectbox(
                    "Candidato / usuário (opcional)",
                    ["(Nenhum)"] + list(op_cand.keys()),
                    index=(
                        ["(Nenhum)"] + list(op_cand.keys())
                    ).index(id_candidato_ini)
                    if id_candidato_ini in op_cand
                    else 0,
                    format_func=lambda x: op_cand.get(x, "(Nenhum)") if x != "(Nenhum)" else "(Nenhum)",
                )
                if id_cand_sel == "(Nenhum)":
                    id_cand_sel = None
            else:
                id_cand_sel = None

        nome_usuario = st.text_input("Nome do usuário / login", value=nome_usuario_ini)
        sistema = st.text_input("Sistema (ex.: Senior, TOTVS, VPN)", value=sistema_ini)
        tipo_acesso = st.text_input("Tipo de acesso (ex.: Admin, Consulta)", value=tipo_ini)

        colD1, colD2, colD3 = st.columns(3)
        with colD1:
            data_inicio = st.date_input("Data início", value=data_ini_ini)
        with colD2:
            data_fim = st.date_input("Data fim (opcional)", value=data_fim_ini) if data_fim_ini else st.date_input(
                "Data fim (opcional)", value=None
            )
        with colD3:
            status = st.selectbox("Status", ["Ativo", "Inativo", "Revogado"], index=["Ativo", "Inativo", "Revogado"].index(status_ini) if status_ini in ["Ativo", "Inativo", "Revogado"] else 0)

        st.markdown("**Detalhes / acessos (blocão):**")
        observacoes = st.text_area(
            "",
            height=260,
            value=obs_ini,
            placeholder="Cole aqui os acessos, URLs, login/senha (se for ambiente controlado), observações etc.",
        )

        colB1, colB2 = st.columns(2)
        with colB1:
            if st.button("🆕 Novo registro", use_container_width=True):
                st.session_state["acesso_edit_id"] = None
                st.experimental_rerun()

        with colB2:
            if st.button("💾 Salvar", use_container_width=True):
                data_inicio_str = data_inicio.isoformat() if data_inicio else None
                data_fim_str = data_fim.isoformat() if isinstance(data_fim, date) else None

                if st.session_state["acesso_edit_id"]:
                    atualizar_acesso(
                        id_acesso=int(st.session_state["acesso_edit_id"]),
                        id_cliente=int(id_cliente_sel) if id_cliente_sel else None,
                        nome_cliente=nome_cliente_sel,
                        id_candidato=int(id_cand_sel) if id_cand_sel else None,
                        nome_usuario=nome_usuario,
                        sistema=sistema,
                        tipo_acesso=tipo_acesso,
                        data_inicio=data_inicio_str,
                        data_fim=data_fim_str,
                        status=status,
                        observacoes=observacoes,
                    )
                    st.success("Acesso atualizado com sucesso.")
                else:
                    novo_id = inserir_acesso(
                        id_cliente=int(id_cliente_sel) if id_cliente_sel else None,
                        nome_cliente=nome_cliente_sel,
                        id_candidato=int(id_cand_sel) if id_cand_sel else None,
                        nome_usuario=nome_usuario,
                        sistema=sistema,
                        tipo_acesso=tipo_acesso,
                        data_inicio=data_inicio_str,
                        data_fim=data_fim_str,
                        status=status,
                        observacoes=observacoes,
                    )
                    st.success(f"Acesso cadastrado (ID {novo_id}).")
                    st.session_state["acesso_edit_id"] = novo_id

                st.experimental_rerun()
