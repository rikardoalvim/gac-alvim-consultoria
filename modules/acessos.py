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
    """Renderiza DataFrame como tabela HTML no estilo glass (usa CSS global)."""
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

    # ==============================
    # Carrega dados base
    # ==============================
    df_cli = carregar_clientes()
    df_acessos = carregar_acessos()

    # ==============================
    # FORMULÁRIO: CLIENTE + BLOCÃO
    # ==============================
    st.subheader("➕ Cadastro / edição de acesso")

    nome_cliente = ""
    id_cliente = ""
    existing_row = None  # acesso já existente para o cliente

    col1, col2 = st.columns(2)

    with col1:
        if df_cli.empty:
            st.info("Nenhum cliente cadastrado. Informe o nome manualmente.")
            nome_cliente = st.text_input("Cliente / Empresa")
        else:
            # Mapa id_cliente -> nome
            opcoes_cli = {}
            for _, row in df_cli.iterrows():
                opcoes_cli[str(row["id_cliente"])] = row["nome_cliente"]

            # Select de cliente
            id_cli_sel = st.selectbox(
                "Cliente",
                options=list(opcoes_cli.keys()) + ["(Manual)"],
                format_func=lambda x: opcoes_cli[x] if x in opcoes_cli else "Outro (manual)",
                key="acess_cli_sel",
            )

            if id_cli_sel in opcoes_cli:
                id_cliente = str(id_cli_sel)
                nome_cliente = opcoes_cli[id_cli_sel]

                # 🔴 AQUI ERA O PROBLEMA: comparação sem cast
                if (
                    df_acessos is not None
                    and not df_acessos.empty
                    and "id_cliente" in df_acessos.columns
                ):
                    # Sempre compara como STRING
                    df_acessos["id_cliente"] = df_acessos["id_cliente"].astype(str)
                    df_cli_acessos = df_acessos[
                        df_acessos["id_cliente"] == str(id_cliente)
                    ]
                    if not df_cli_acessos.empty:
                        # Pega o último registro (poderia ordenar por data se quiser)
                        existing_row = df_cli_acessos.iloc[-1]
            else:
                # opção manual
                nome_cliente = st.text_input("Cliente / Empresa (manual)")
                id_cliente = ""

    with col2:
        nome_usuario_default = ""
        if existing_row is not None and "nome_usuario" in existing_row.index:
            nome_usuario_default = str(existing_row["nome_usuario"])

        nome_usuario = st.text_input(
            "Usuário / Responsável (opcional)",
            placeholder="Ex.: Rikardo, Stephanie, time financeiro...",
            value=nome_usuario_default,
        )

    # Bloco de notas grande – se já houver cadastro, preenche com o texto atual
    texto_inicial = ""
    if existing_row is not None and "observacoes" in existing_row.index:
        texto_inicial = str(existing_row["observacoes"])

    observacoes = st.text_area(
        "Bloco de notas de acessos (URLs, logins, senhas, observações)",
        height=350,
        value=texto_inicial,
        placeholder="Cole aqui todos os acessos deste cliente/usuário...",
        key="acess_blocao",
    )

    colb1, colb2 = st.columns([1, 1])
    with colb1:
        if st.button("💾 Salvar acesso", use_container_width=True, key="btn_salvar_acesso"):
            if not nome_cliente.strip() and not observacoes.strip():
                st.error("Informe ao menos o cliente/empresa ou o bloco de notas.")
            else:
                try:
                    # Já existe registro para esse cliente? -> ATUALIZA
                    if existing_row is not None and "id_acesso" in existing_row.index:
                        df_total = carregar_acessos()
                        df_total["id_acesso"] = df_total["id_acesso"].astype(str)
                        id_acesso_atual = str(existing_row["id_acesso"])

                        mask = df_total["id_acesso"] == id_acesso_atual
                        if not mask.any():
                            st.error("Registro de acesso não encontrado para atualização.")
                        else:
                            df_total.loc[mask, "nome_cliente"] = nome_cliente.strip()
                            df_total.loc[mask, "id_cliente"] = str(id_cliente)
                            df_total.loc[mask, "nome_usuario"] = (
                                nome_usuario.strip() or nome_cliente.strip()
                            )
                            df_total.loc[mask, "observacoes"] = observacoes.strip()
                            # Mantém demais campos (sistema, tipo_acesso, datas, status)
                            df_total.to_csv(LOG_ACESSOS, sep=";", index=False, encoding="utf-8")
                            st.success("Acesso atualizado com sucesso!")
                    else:
                        # Não havia ainda um acesso para esse cliente -> cria novo
                        hoje = datetime.today().strftime("%Y-%m-%d")
                        novo_id = registrar_acesso(
                            id_cliente=str(id_cliente),
                            nome_cliente=nome_cliente.strip(),
                            id_candidato="",
                            nome_usuario=nome_usuario.strip() or nome_cliente.strip(),
                            sistema="Geral",
                            tipo_acesso="Usuário",
                            data_inicio=hoje,
                            data_fim="",
                            status="Ativo",
                            observacoes=observacoes.strip(),
                        )
                        st.success(f"Acesso registrado com ID {novo_id}.")
                except Exception as e:
                    st.error(f"Erro ao salvar acesso: {e}")

    with colb2:
        if st.button("🧹 Limpar formulário", use_container_width=True, key="btn_limpar_acesso"):
            for k in ["acess_cli_sel", "acess_blocao"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.experimental_rerun()

    st.markdown("---")

    # ==============================
    # LISTA DE ACESSOS (RESUMO)
    # ==============================
    st.subheader("📋 Acessos cadastrados (resumo)")

    df = carregar_acessos()
    if df.empty:
        st.info("Nenhum acesso registrado ainda.")
        return

    df_view = df.copy().fillna("")

    # Filtro por cliente / texto
    filtro_cli = st.text_input(
        "Filtrar por cliente ou texto (contém)",
        key="acess_filtro_cli",
        placeholder="Digite parte do nome do cliente ou palavra chave...",
    )

    if filtro_cli.strip():
        low = filtro_cli.strip().lower()
        nome_cli_col = df_view.get("nome_cliente", "")
        obs_col = df_view.get("observacoes", "")

        df_view = df_view[
            nome_cli_col.astype(str).str.lower().str.contains(low)
            | obs_col.astype(str).str.lower().str.contains(low)
        ]

    if df_view.empty:
        st.info("Nenhum acesso encontrado com esse filtro.")
        return

    # Garante colunas
    for col in ["id_acesso", "nome_cliente", "nome_usuario", "observacoes"]:
        if col not in df_view.columns:
            df_view[col] = ""

    df_view["observ_preview"] = df_view["observacoes"].astype(str).str.slice(0, 140) + "..."

    df_view = df_view.astype(str)

    render_tabela_html(
        df_view,
        columns=["id_acesso", "nome_cliente", "nome_usuario", "observ_preview"],
        headers=["ID", "Cliente", "Usuário", "Resumo do bloco de notas"],
    )

        df_view,
        columns=["id_acesso", "nome_cliente", "nome_usuario", "observ_preview"],
        headers=["ID", "Cliente", "Usuário", "Resumo do bloco de notas"],
    )

