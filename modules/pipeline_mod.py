import os
import pandas as pd
import streamlit as st

from .core import (
    BASE_DIR,
    carregar_vaga_candidatos,
    carregar_vagas,
    carregar_candidatos,
    carregar_pareceres_log,
)

# Caminho do arquivo onde vamos guardar SOMENTE o status do pipeline
PIPELINE_CSV = os.path.join(BASE_DIR, "pipeline_status.csv")

# =====================================================
# CSS – SELECTBOX / MULTISELECT ESTILO LIQUID GLASS
# =====================================================

SELECT_CSS = """
<style>
/* container geral do select/multiselect */
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background: radial-gradient(circle at 10% 20%, rgba(255,255,255,0.90) 0%, rgba(248,250,252,0.80) 40%, rgba(241,245,249,0.80) 100%) !important;
    border-radius: 999px !important;
    box-shadow: 0 18px 45px rgba(15,23,42,0.25) !important;
    border: 1px solid rgba(148,163,184,0.4) !important;
    backdrop-filter: blur(18px) saturate(130%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(130%) !important;
}

/* texto do valor selecionado */
.stSelectbox div[data-baseweb="select"] span,
.stMultiSelect div[data-baseweb="select"] span {
    color: #0f172a !important;
    font-weight: 500 !important;
}

/* placeholder */
.stSelectbox div[data-baseweb="select"] span[data-baseweb="typo-label"],
.stMultiSelect div[data-baseweb="select"] span[data-baseweb="typo-label"] {
    color: rgba(15,23,42,0.65) !important;
}

/* menu suspenso (lista de opções) */
.stSelectbox div[data-baseweb="select"] div[role="listbox"],
.stMultiSelect div[data-baseweb="select"] div[role="listbox"] {
    background: radial-gradient(circle at 0% 0%, rgba(15,23,42,0.98) 0%, rgba(30,64,175,0.92) 35%, rgba(59,130,246,0.90) 100%) !important;
    color: #f9fafb !important;
    border-radius: 24px !important;
    box-shadow: 0 25px 60px rgba(15,23,42,0.55) !important;
    border: 1px solid rgba(148,163,184,0.65) !important;
    backdrop-filter: blur(22px) saturate(140%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(140%) !important;
}

/* itens da lista */
.stSelectbox div[data-baseweb="select"] div[role="option"],
.stMultiSelect div[data-baseweb="select"] div[role="option"] {
    color: #e5e7eb !important;
}

/* item focado/hover ou selecionado */
.stSelectbox div[data-baseweb="select"] div[role="option"][aria-selected="true"],
.stSelectbox div[data-baseweb="select"] div[role="option"]:hover,
.stMultiSelect div[data-baseweb="select"] div[role="option"][aria-selected="true"],
.stMultiSelect div[data-baseweb="select"] div[role="option"]:hover {
    background: linear-gradient(120deg, rgba(248,250,252,0.18), rgba(248,250,252,0.05)) !important;
    color: #f9fafb !important;
}
</style>
"""


# =====================================================
# HELPERS
# =====================================================

def render_tabela_html(df, columns, headers):
    """Renderiza DataFrame como tabela HTML glass (igual lista de candidatos)."""
    if df.empty:
        st.info("Nenhum registro encontrado.")
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


def carregar_status_pipeline():
    """Lê arquivo de status do pipeline (id_vaga + id_candidato)."""
    if not os.path.isfile(PIPELINE_CSV):
        return pd.DataFrame(
            columns=[
                "id_vaga",
                "id_candidato",
                "status_etapa",
                "status_contratacao",
                "motivo_decline",
            ]
        )
    try:
        df = pd.read_csv(PIPELINE_CSV, sep=";", dtype=str)
        for col in [
            "id_vaga",
            "id_candidato",
            "status_etapa",
            "status_contratacao",
            "motivo_decline",
        ]:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(
            columns=[
                "id_vaga",
                "id_candidato",
                "status_etapa",
                "status_contratacao",
                "motivo_decline",
            ]
        )


def salvar_status_pipeline(df_status):
    """Grava dataframe de status do pipeline em PIPELINE_CSV."""
    df_out = df_status[
        [
            "id_vaga",
            "id_candidato",
            "status_etapa",
            "status_contratacao",
            "motivo_decline",
        ]
    ].copy()
    df_out.to_csv(PIPELINE_CSV, sep=";", index=False, encoding="utf-8")


# =====================================================
# MÓDULO PRINCIPAL
# =====================================================

def run():
    st.header("📌 Pipeline de Candidatos")

    st.markdown(SELECT_CSS, unsafe_allow_html=True)

    # ---- 1) Carrega vínculos (base do pipeline) ----
    df_vinc = carregar_vaga_candidatos()
    df_vagas = carregar_vagas()
    df_cand = carregar_candidatos()

    if df_vinc.empty or df_vagas.empty or df_cand.empty:
        st.info(
            "Para usar o pipeline é necessário ter:\n"
            "- Vínculos vaga x candidato\n"
            "- Vagas cadastradas\n"
            "- Candidatos cadastrados"
        )
        return

    # garante tipos string para merge
    df_vinc["id_vaga"] = df_vinc["id_vaga"].astype(str)
    df_vinc["id_candidato"] = df_vinc["id_candidato"].astype(str)
    df_vagas["id_vaga"] = df_vagas["id_vaga"].astype(str)
    df_cand["id_candidato"] = df_cand["id_candidato"].astype(str)

    # une vínculos com vagas e candidatos
    df_full = (
        df_vinc.merge(
            df_vagas[["id_vaga", "nome_cliente", "cargo"]],
            on="id_vaga",
            how="left",
        )
        .merge(
            df_cand[["id_candidato", "nome", "cidade", "telefone", "idade"]],
            on="id_candidato",
            how="left",
        )
    )

    # ---- 2) Carrega status já salvos e aplica nos vínculos ----
    df_status = carregar_status_pipeline()

    df = df_full.merge(
        df_status,
        on=["id_vaga", "id_candidato"],
        how="left",
        suffixes=("", "_st"),
    )

    for col in ["status_etapa", "status_contratacao", "motivo_decline"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")

    # ordena: cliente, cargo, nome
    df = df.sort_values(["nome_cliente", "cargo", "nome"])

    etapa_opcoes = [
        "Em avaliação",
        "Triagem",
        "Entrevista",
        "Finalista",
        "Não seguiu processo",
    ]
    contratacao_opcoes = [
        "Pendente",
        "Aprovado / Contratado",
        "Reprovado",
        "Desistiu",
    ]

    # ==================================================
    #  A) EDIÇÃO DO PIPELINE (TRABALHO DIÁRIO)
    # ==================================================
    st.subheader("✏️ Atualizar pipeline (somente candidatos vinculados às vagas)")

    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "id_vaga": st.column_config.Column("ID Vaga", disabled=True),
            "id_candidato": st.column_config.Column("ID Cand.", disabled=True),
            "data_vinculo": st.column_config.Column("Data vínculo", disabled=True),
            "nome_cliente": st.column_config.Column("Cliente", disabled=True),
            "cargo": st.column_config.Column("Cargo", disabled=True),
            "nome": st.column_config.Column("Candidato", disabled=True),
            "cidade": st.column_config.Column("Cidade", disabled=True),
            "telefone": st.column_config.Column("Telefone", disabled=True),
            "idade": st.column_config.Column("Idade", disabled=True),
            "observacao": st.column_config.Column("Obs vínculo", disabled=True),
            "status_etapa": st.column_config.SelectboxColumn(
                "Etapa",
                options=etapa_opcoes,
            ),
            "status_contratacao": st.column_config.SelectboxColumn(
                "Status contratação",
                options=contratacao_opcoes,
            ),
            "motivo_decline": st.column_config.TextColumn(
                "Motivo de declínio",
            ),
        },
        key="pipeline_editor",
    )

    if st.button("💾 Salvar alterações do pipeline", use_container_width=True):
        try:
            # extrai apenas colunas de status + chaves
            df_status_new = edited_df[
                ["id_vaga", "id_candidato", "status_etapa", "status_contratacao", "motivo_decline"]
            ].copy()

            # remove duplicados caso exista
            df_status_new = df_status_new.drop_duplicates(
                subset=["id_vaga", "id_candidato"], keep="last"
            )

            salvar_status_pipeline(df_status_new)
            st.success("Pipeline atualizado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar pipeline: {e}")

    st.markdown("---")

    # ==================================================
    #  B) VISUALIZAÇÃO BONITA (TABELA GLASS)
    # ==================================================
    st.subheader("📋 Pipeline registrado (visualização)")

    df_view = edited_df.copy().fillna("").astype(str)

    render_tabela_html(
        df_view,
        columns=[
            "nome_cliente",
            "cargo",
            "nome",
            "cidade",
            "telefone",
            "status_etapa",
            "status_contratacao",
            "motivo_decline",
            "data_vinculo",
        ],
        headers=[
            "Cliente",
            "Cargo",
            "Candidato",
            "Cidade",
            "Telefone",
            "Etapa",
            "Status",
            "Motivo Declínio",
            "Data vínculo",
        ],
    )

    st.markdown("---")

    # ==================================================
    #  C) CARREGAR PARECER NO FORMULÁRIO (OPCIONAL)
    #     continua usando LOG de pareceres, se você quiser.
    # ==================================================
    st.subheader("🔁 Carregar parecer no formulário (módulo Parecer)")

    df_sel = carregar_pareceres_log()
    if df_sel.empty:
        st.info("Nenhum parecer para carregar.")
        return

    df_sel = df_sel.sort_values("data_hora", ascending=False)
    opcoes = {
        idx: f"{row['data_hora']} - {row['nome']} - {row['cargo']} - {row['cliente']}"
        for idx, row in df_sel.iterrows()
    }

    escolha = st.selectbox(
        "Escolha um parecer para carregar:",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
        key="pip_sel_parecer",
    )

    if st.button("Carregar dados no formulário de Parecer", use_container_width=True):
        row = df_sel.loc[escolha]

        st.session_state["cliente"] = row.get("cliente", "")
        st.session_state["cargo"] = row.get("cargo", "")
        st.session_state["nome"] = row.get("nome", "")
        st.session_state["localidade"] = row.get("localidade", "")
        st.session_state["idade"] = str(row.get("idade", ""))
        st.session_state["pretensao"] = row.get("pretensao", "")
        st.session_state["linkedin"] = row.get("linkedin", "")
        st.session_state["resumo_profissional"] = row.get("resumo_profissional", "")
        st.session_state["analise_perfil"] = row.get("analise_perfil", "")
        st.session_state["conclusao_texto"] = row.get("conclusao_texto", "")
        st.session_state["id_candidato_selecionado"] = str(row.get("id_candidato", ""))

        st.success(
            "Dados carregados. Vá ao módulo Recrutamento > aba Parecer para gerar novo laudo."
        )




