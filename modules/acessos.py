from datetime import datetime
import pandas as pd
import streamlit as st

from .core import (
    carregar_acessos,
    registrar_acesso,
    LOG_ACESSOS,
    carregar_clientes,
)


def render_tabela_html(df, columns, headers):
    """Renderiza DataFrame como tabela HTML no estilo glass (aproveita CSS global)."""
    if df.empty:
        st.info("Nenhum acesso cadastrado ainda.")
        return

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
            valor = row[col]
            html.append(f"<td>{valor}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")

    st.markdown("".join(html), unsafe_allow_html=True)


def run():
    st.header("🔐 Gerenciador de Acessos")

    # ====================================
    # FORMULÁRIO SIMPLES: CLIENTE + BLOCÃO
    # ====================================
    st.subheader("➕ Novo acesso")

    df_cli = carregar_clientes()
    nome_cliente = ""
    id_cliente = ""

    col1, col2 = st.columns(2)

    with col1:
        if df_cli.empty:
            st.info("Nenhum cliente cadastrado. Informe o nome manualmente.")
            nome_cliente = st.text_input("Cliente / Empresa")
        else:
            opcoes_cli = {
                "": "(Selecione ou deixe em branco)",
            }
            for _, row in df_cli.iterrows():
                opcoes_cli[str(row["id_cliente"])] = row["nome_cliente"]

            id_cli_sel = st.selectbox(
                "Cliente (opcional)",
                options=list(opcoes_cli.keys()),
                format_func=lambda x: opcoes_cli[x],
                key="acess_cli_sel",
            )
            if id_cli_sel:
                id_cliente = id_cli_sel
                nome_cliente = opcoes_cli[id_cli_sel]
            else:
                nome_cliente = st.text_input("Cliente / Empresa (manual)", value="")

    with col2:
        nome_usuario = st.text_input(
            "Usuário / Responsável (opcional)",
            placeholder="Ex.: Rikardo, Stephanie, time financeiro...",
        )

    # Bloco de notas grande
    observacoes = st.text_area(
        "Bloco de notas de acessos (URLs, logins, senhas, observações)",
        height=220,
        placeholder="Cole aqui todos os acessos deste cliente/usuário...",
    )

    if st.button("💾 Salvar acesso", use_container_width=True):
        if not nome_cliente.strip() and not observacoes.strip():
            st.error("Informe ao menos o cliente/empresa ou o bloco de notas.")
        else:
            agora = datetime.today().strftime("%Y-%m-%d")
            # Preenche campos que o registrar_acesso espera
            novo_id = registrar_acesso(
                id_cliente=id_cliente,
                nome_cliente=nome_cliente.strip(),
                id_candidato="",               # sem vínculo direto com candidato aqui
                nome_usuario=nome_usuario.strip() or nome_cliente.strip(),
                sistema="Geral",
                tipo_acesso="Usuário",
                data_inicio=agora,
                data_fim="",
                status="Ativo",
                observacoes=observacoes.strip(),
            )
            st.success(f"Acesso registrado com ID {novo_id}.")

    st.markdown("---")

    # ====================================
    # LISTA DE ACESSOS (TABELA GLASS)
    # ====================================
    st.subheader("📋 Acessos cadastrados")

    df = carregar_acessos()
    if df.empty:
        st.info("Nenhum acesso registrado ainda.")
        return

    df_view = df.copy().fillna("")

    # Pequeno filtro por cliente (contém)
    filtro_cli = st.text_input(
        "Filtrar por cliente (contém)",
        key="acess_filtro_cli",
        placeholder="Digite parte do nome do cliente para filtrar...",
    )

    if filtro_cli.strip():
        df_view = df_view[
            df_view["nome_cliente"].str.lower().str.contains(filtro_cli.strip().lower())
            | df_view["observacoes"].str.lower().str.contains(filtro_cli.strip().lower())
        ]

    if df_view.empty:
        st.info("Nenhum acesso encontrado com esse filtro.")
        return

    # Mostra apenas as colunas principais
    if "id_acesso" not in df_view.columns:
        df_view["id_acesso"] = ""

    for col in ["nome_cliente", "nome_usuario", "observacoes"]:
        if col not in df_view.columns:
            df_view[col] = ""

    # Limita observações a um preview (para tabela)
    df_view["observ_preview"] = df_view["observacoes"].astype(str).str.slice(0, 120) + "..."

    df_view = df_view.astype(str)

    render_tabela_html(
        df_view,
        columns=["id_acesso", "nome_cliente", "nome_usuario", "observ_preview"],
        headers=["ID", "Cliente", "Usuário", "Resumo do bloco de notas"],
    )

