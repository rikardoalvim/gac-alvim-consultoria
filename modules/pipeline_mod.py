import streamlit as st
import pandas as pd
from .core import carregar_pareceres_log, LOG_PAR
from datetime import datetime


# =========================================
# Função padrão para tabela HTML (igual candidatos)
# =========================================
def render_tabela_html(df, columns, headers):
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    html = ["<div class='glass-container'><table class='ios-table'>"]

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
    html.append("</tbody></table></div>")

    st.markdown("".join(html), unsafe_allow_html=True)


# =========================================
# Módulo principal
# =========================================
def run():

    st.markdown("<h1 class='titulo-modulo'>📌 Pipeline de Candidatos</h1>", unsafe_allow_html=True)

    # -------------------------------------
    # Botões de modo
    # -------------------------------------
    modo = st.radio(
        "Selecione a ação:",
        ["Listar pipeline", "Editar pipeline", "Carregar parecer"],
        horizontal=True
    )

    # -------------------------------------
    # Carrega o pipeline
    # -------------------------------------
    df_pipe = carregar_pareceres_log()
    if df_pipe.empty:
        st.info("Nenhum registro encontrado no pipeline.")
        return

    # Garante colunas
    obrigatorias = ["status_etapa", "status_contratacao", "motivo_decline", "id_candidato"]
    for c in obrigatorias:
        if c not in df_pipe.columns:
            df_pipe[c] = ""

    # Ordenação
    cols_ordem = [
        "data_hora", "cliente", "cargo", "nome", "localidade",
        "idade", "pretensao", "id_candidato",
        "status_etapa", "status_contratacao", "motivo_decline",
        "caminho_arquivo"
    ]
    df_pipe = df_pipe[[c for c in cols_ordem if c in df_pipe.columns]]
    df_pipe = df_pipe.fillna("").astype(str)

    # -------------------------------------
    # MODO 1 — LISTAR PIPELINE (HTML)
    # -------------------------------------
    if modo == "Listar pipeline":

        st.markdown("### 📋 Pipeline registrado")

        render_tabela_html(
            df_pipe,
            columns=[
                "data_hora", "cliente", "cargo", "nome", "localidade",
                "status_etapa", "status_contratacao", "motivo_decline"
            ],
            headers=[
                "Data/Hora", "Cliente", "Cargo", "Nome", "Cidade",
                "Etapa", "Status", "Motivo Declínio"
            ]
        )

        return

    # -------------------------------------
    # MODO 2 — EDITAR PIPELINE (formulário iOS)
    # -------------------------------------
    if modo == "Editar pipeline":

        st.markdown("### ✏️ Editar registro do pipeline")

        # lista para escolher
        opcoes = {
            i: f"{row['data_hora']} - {row['nome']} - {row['cargo']} ({row['cliente']})"
            for i, row in df_pipe.iterrows()
        }

        sel = st.selectbox("Escolha o registro:", list(opcoes.keys()), format_func=lambda x: opcoes[x])

        row = df_pipe.loc[sel]

        etapa_opcoes = [
            "Em avaliação", "Triagem", "Entrevista",
            "Finalista", "Não seguiu processo"
        ]
        contratacao_opcoes = [
            "Pendente", "Aprovado / Contratado",
            "Reprovado", "Desistiu"
        ]

        st.markdown("#### Informações do processo")

        col1, col2 = st.columns(2)
        with col1:
            new_etapa = st.selectbox("Etapa do processo", etapa_opcoes, index=etapa_opcoes.index(row["status_etapa"]) if row["status_etapa"] in etapa_opcoes else 0)
        with col2:
            new_status = st.selectbox("Status de contratação", contratacao_opcoes, index=contratacao_opcoes.index(row["status_contratacao"]) if row["status_contratacao"] in contratacao_opcoes else 0)

        motivo = st.text_area("Motivo de declínio (opcional)", value=row["motivo_decline"], height=100)

        if st.button("💾 Salvar alterações"):
            df_pipe.loc[sel, "status_etapa"] = new_etapa
            df_pipe.loc[sel, "status_contratacao"] = new_status
            df_pipe.loc[sel, "motivo_decline"] = motivo

            df_pipe.to_csv(LOG_PAR, sep=";", index=False, encoding="utf-8")
            st.success("Registro atualizado com sucesso!")
            st.rerun()

        return

    # -------------------------------------
    # MODO 3 — CARREGAR PARECER
    # -------------------------------------
    if modo == "Carregar parecer":

        st.markdown("### 🔁 Carregar informações no módulo Parecer")

        df_sel = df_pipe.sort_values("data_hora", ascending=False)

        opcoes = {
            idx: f"{row['data_hora']} - {row['nome']} - {row['cargo']} - {row['cliente']}"
            for idx, row in df_sel.iterrows()
        }

        escolha = st.selectbox(
            "Escolha o parecer:",
            list(opcoes.keys()),
            format_func=lambda x: opcoes[x]
        )

        if st.button("Carregar no módulo Parecer"):
            row = df_sel.loc[escolha]

            st.session_state["cliente"] = row.get("cliente", "")
            st.session_state["cargo"] = row.get("cargo", "")
            st.session_state["nome"] = row.get("nome", "")
            st.session_state["localidade"] = row.get("localidade", "")
            st.session_state["idade"] = row.get("idade", "")
            st.session_state["pretensao"] = row.get("pretensao", "")
            st.session_state["linkedin"] = row.get("linkedin", "")
            st.session_state["resumo_profissional"] = row.get("resumo_profissional", "")
            st.session_state["analise_perfil"] = row.get("analise_perfil", "")
            st.session_state["conclusao_texto"] = row.get("conclusao_texto", "")
            st.session_state["id_candidato_selecionado"] = row.get("id_candidato", "")

            st.success("Dados carregados! Abra o módulo Parecer.")



