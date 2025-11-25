from datetime import datetime

import pandas as pd
import streamlit as st

from .core import (
    carregar_vaga_candidatos,
    salvar_vaga_candidatos,
    carregar_vagas,
    carregar_candidatos,
    carregar_pareceres_log,
)

# usa o mesmo render de tabela glass das vagas
from .vagas import render_tabela_html


def run():
    st.header("📌 Pipeline de Candidatos")

    # ============================================================
    # 0) CARREGAR BASES
    # ============================================================
    df_vinc = carregar_vaga_candidatos()
    if df_vinc.empty:
        st.info("Nenhum vínculo vaga × candidato encontrado. Use a tela de Vagas > Vincular candidatos.")
        return

    df_vagas = carregar_vagas()
    df_cand = carregar_candidatos()

    if df_vagas.empty or df_cand.empty:
        st.info("É necessário ter vagas e candidatos cadastrados para montar o pipeline.")
        return

    df_vinc = df_vinc.copy()
    df_vagas = df_vagas.copy()
    df_cand = df_cand.copy()

    df_vinc["id_vaga"] = df_vinc["id_vaga"].astype(str)
    df_vinc["id_candidato"] = df_vinc["id_candidato"].astype(str)

    df_vagas["id_vaga"] = df_vagas["id_vaga"].astype(str)
    df_cand["id_candidato"] = df_cand["id_candidato"].astype(str)

    # defaults das colunas de pipeline
    defaults_cols = {
        "status_etapa": "Em avaliação",
        "status_contratacao": "Pendente",
        "motivo_decline": "",
    }

    for col, default in defaults_cols.items():
        if col not in df_vinc.columns:
            df_vinc[col] = default
        df_vinc[col] = df_vinc[col].fillna(default)

    # ============================================================
    # 1) MONTAR VISÃO DE PIPELINE (VAGA + CANDIDATO)
    # ============================================================
    df_pipeline = (
        df_vinc
        .merge(
            df_vagas[["id_vaga", "nome_cliente", "cargo"]],
            on="id_vaga",
            how="left",
        )
        .merge(
            df_cand[["id_candidato", "nome", "cidade"]],
            on="id_candidato",
            how="left",
        )
    )

    for col, default in defaults_cols.items():
        if col not in df_pipeline.columns:
            df_pipeline[col] = default
        df_pipeline[col] = df_pipeline[col].fillna(default)

    # ordena pela data de vínculo (se existir)
    if "data_vinculo" in df_pipeline.columns:
        try:
            df_pipeline["_ord_data"] = pd.to_datetime(
                df_pipeline["data_vinculo"], errors="coerce"
            )
            df_pipeline = df_pipeline.sort_values(
                ["_ord_data", "nome_cliente", "cargo", "nome"],
                ascending=[False, True, True, True],
            )
        except Exception:
            df_pipeline = df_pipeline.sort_values("data_vinculo", ascending=False)
    else:
        df_pipeline = df_pipeline.sort_values(["nome_cliente", "cargo", "nome"])

    # ============================================================
    # 1.1) LISTA EM ESTILO GLASS (APENAS VISUAL)
    # ============================================================
    st.subheader("📋 Visão geral do pipeline (vaga × candidato)")

    colunas_lista = [
        "data_vinculo",
        "nome_cliente",
        "cargo",
        "nome",
        "cidade",
        "status_etapa",
        "status_contratacao",
        "motivo_decline",
    ]
    colunas_lista = [c for c in colunas_lista if c in df_pipeline.columns]

    if not df_pipeline.empty and colunas_lista:
        render_tabela_html(
            df_pipeline,
            columns=colunas_lista,
            headers=[
                "Data vínculo",
                "Cliente",
                "Cargo",
                "Candidato",
                "Cidade",
                "Etapa",
                "Status contratação",
                "Motivo de declínio",
            ],
        )
    else:
        st.info("Nenhum registro para exibir na lista.")

    st.markdown("---")

    # ============================================================
    # 2) EDIÇÃO (st.data_editor) – ATUALIZA APENAS NO CSV DE VÍNCULOS
    # ============================================================
    st.subheader("✏️ Atualizar status do pipeline")

    # DataFrame base para edição (mostra só o necessário)
    colunas_edicao = [
        "id_vaga",
        "id_candidato",
        "nome_cliente",
        "cargo",
        "nome",
        "cidade",
        "status_etapa",
        "status_contratacao",
        "motivo_decline",
    ]
    colunas_edicao = [c for c in colunas_edicao if c in df_pipeline.columns]

    df_edit_base = df_pipeline[colunas_edicao].copy()

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
        df_edit_base,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
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
        key="pipeline_editor",
    )

    # ============================================================
    # 3) SALVAR DE VOLTA NO CSV DE VÍNCULOS
    # ============================================================
    if st.button("💾 Salvar alterações do pipeline", use_container_width=True):
        try:
            df_save = df_vinc.copy()

            # garante colunas de pipeline no CSV original
            for col, default in defaults_cols.items():
                if col not in df_save.columns:
                    df_save[col] = default
                df_save[col] = df_save[col].fillna(default)

            df_save["id_vaga"] = df_save["id_vaga"].astype(str)
            df_save["id_candidato"] = df_save["id_candidato"].astype(str)

            for _, row_ed in edited_df.iterrows():
                id_vaga = str(row_ed["id_vaga"])
                id_candidato = str(row_ed["id_candidato"])

                mask = (df_save["id_vaga"] == id_vaga) & (
                    df_save["id_candidato"] == id_candidato
                )

                for col, default in defaults_cols.items():
                    if col in row_ed:
                        df_save.loc[mask, col] = row_ed.get(col, default)

                # data/hora da última atualização (opcional)
                if "data_ultima_atualizacao" not in df_save.columns:
                    df_save["data_ultima_atualizacao"] = ""
                df_save.loc[mask, "data_ultima_atualizacao"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            salvar_vaga_candidatos(df_save)
            st.success("Pipeline atualizado com sucesso (dados gravados no vínculo vaga × candidato).")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar pipeline: {e}")

    # ============================================================
    # 4) CARREGAR PARECER NO FORMULÁRIO (MÓDULO PARECER)
    # ============================================================
    st.markdown("---")
    st.subheader("🔁 Carregar parecer no formulário (módulo Parecer)")

    df_sel = carregar_pareceres_log()
    if df_sel.empty:
        st.info("Nenhum parecer registrado no histórico.")
        return

    df_sel = df_sel.sort_values("data_hora", ascending=False)

    opcoes = {
        idx: f"{row.get('data_hora','')} - {row.get('nome','')} - {row.get('cargo','')} - {row.get('cliente','')}"
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
        st.session_state["idade"] = str(row.get("idade", "") or "")
        st.session_state["pretensao"] = row.get("pretensao", "")
        st.session_state["linkedin"] = row.get("linkedin", "")
        st.session_state["resumo_profissional"] = row.get("resumo_profissional", "")
        st.session_state["analise_perfil"] = row.get("analise_perfil", "")
        st.session_state["conclusao_texto"] = row.get("conclusao_texto", "")
        st.session_state["id_candidato_selecionado"] = str(row.get("id_candidato", "") or "")

        st.success(
            "Dados carregados. Vá até Recrutamento & Seleção → aba **Parecer** para gerar/ajustar o laudo."
        )





