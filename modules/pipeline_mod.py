import streamlit as st
import pandas as pd

from .core import carregar_pareceres_log, LOG_PAR


def run():
    st.header("📌 Pipeline de Candidatos")

    df_pipe = carregar_pareceres_log()
    if df_pipe.empty:
        st.info("Nenhum parecer registrado para pipeline.")
        return

    for col in ["status_etapa", "status_contratacao", "motivo_decline", "id_candidato"]:
        if col not in df_pipe.columns:
            df_pipe[col] = ""

    cols_ordem = [
        "data_hora", "cliente", "cargo", "nome", "localidade",
        "idade", "pretensao", "id_candidato",
        "status_etapa", "status_contratacao", "motivo_decline",
        "caminho_arquivo",
    ]
    df_pipe = df_pipe[[c for c in cols_ordem if c in df_pipe.columns]]

    df_pipe["motivo_decline"] = df_pipe["motivo_decline"].fillna("").astype(str)

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

    edited_df = st.data_editor(
        df_pipe,
        hide_index=True,
        use_container_width=True,
        column_config={
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
        num_rows="fixed",
        key="pipeline_editor",
    )

    if st.button("💾 Salvar alterações do pipeline"):
        try:
            edited_df.to_csv(LOG_PAR, sep=";", index=False, encoding="utf-8")
            st.success("Pipeline atualizado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar pipeline: {e}")

    st.markdown("### 🔁 Carregar parecer no formulário (módulo Parecer)")

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

    if st.button("Carregar dados no formulário de Parecer"):
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

        st.success("Dados carregados. Vá ao módulo Recrutamento > aba Parecer para gerar novo laudo.")
