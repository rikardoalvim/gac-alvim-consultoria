import streamlit as st
import pandas as pd
from datetime import datetime

from .core import (
    carregar_vaga_candidatos,
    salvar_vaga_candidatos,
    carregar_vagas,
    carregar_candidatos,
    carregar_pareceres_log,  # opcional, para a parte de "carregar parecer"
)


def run():
    st.header("📌 Pipeline de Candidatos")

    # ============================================================
    # 1) BASE DO PIPELINE: APENAS VÍNCULO VAGA x CANDIDATO
    # ============================================================
    df_vinc = carregar_vaga_candidatos()
    if df_vinc.empty:
        st.info("Nenhum vínculo de vaga x candidato encontrado. Vá em 'Gestão de Vagas' → 'Vincular candidatos'.")
        return

    df_vagas = carregar_vagas()
    df_cand = carregar_candidatos()

    if df_vagas.empty or df_cand.empty:
        st.info("É necessário ter vagas e candidatos cadastrados para montar o pipeline.")
        return

    # Garante tipos compatíveis
    df_vinc["id_vaga"] = df_vinc["id_vaga"].astype(str)
    df_vinc["id_candidato"] = df_vinc["id_candidato"].astype(str)
    df_vagas["id_vaga"] = df_vagas["id_vaga"].astype(str)
    df_cand["id_candidato"] = df_cand["id_candidato"].astype(str)

    # Junta com VAGAS (cliente, cargo)
    df_pipeline = df_vinc.merge(
        df_vagas[["id_vaga", "nome_cliente", "cargo"]],
        on="id_vaga",
        how="left",
    )

    # Junta com CANDIDATOS (nome, cidade, telefone)
    df_pipeline = df_pipeline.merge(
        df_cand[["id_candidato", "nome", "cidade", "telefone"]],
        on="id_candidato",
        how="left",
    )

    # Garante colunas de status do pipeline
    defaults_cols = {
        "status_etapa": "Em avaliação",
        "status_contratacao": "Pendente",
        "motivo_decline": "",
    }
    for col, default in defaults_cols.items():
        if col not in df_pipeline.columns:
            df_pipeline[col] = default
        df_pipeline[col] = df_pipeline[col].fillna(default)

    # Ordena por data de vínculo (se existir)
    if "data_vinculo" in df_pipeline.columns:
        try:
            df_pipeline["__dt"] = pd.to_datetime(df_pipeline["data_vinculo"], errors="ignore")
            df_pipeline = df_pipeline.sort_values("__dt", ascending=False)
        except Exception:
            pass

    # ============================================================
    # 2) EDIÇÃO DO PIPELINE
    # ============================================================
    st.subheader("Pipeline registrado (apenas candidatos vinculados)")

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

    # Colunas que serão mostradas ao usuário
    colunas_visiveis = [
        "data_vinculo",
        "nome_cliente",
        "cargo",
        "nome",
        "cidade",
        "status_etapa",
        "status_contratacao",
        "motivo_decline",
    ]
    colunas_visiveis = [c for c in colunas_visiveis if c in df_pipeline.columns]

    # Mantemos id_vaga e id_candidato para identificar linhas na hora de salvar
    df_edit_base = df_pipeline[colunas_visiveis + ["id_vaga", "id_candidato"]].copy()

    edited_df = st.data_editor(
        df_edit_base,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "id_vaga": st.column_config.Column("id_vaga", disabled=True, width="small"),
            "id_candidato": st.column_config.Column("id_candidato", disabled=True, width="small"),
            "status_etapa": st.column_config.SelectboxColumn(
                "Etapa",
                options=etapa_opcoes,
            ),
            "status_contratacao": st.column_config.SelectboxColumn(
                "Status contratação",
                options=contratacao_opcoes,
            ),
            "motivo_decline": st.column_config.TextColumn("Motivo de declínio"),
        },
        key="pipeline_editor",
    )

    # ============================================================
    # 3) SALVAR DE VOLTA NO CSV DE VÍNCULOS
    # ============================================================
    if st.button("💾 Salvar alterações do pipeline", use_container_width=True):
        try:
            df_save = df_vinc.copy()

            # Garante que as colunas de status existam também no CSV original
            for col in defaults_cols.keys():
                if col not in df_save.columns:
                    df_save[col] = defaults_cols[col]
                df_save[col] = df_save[col].fillna(defaults_cols[col])

            # Índices para bater id_vaga + id_candidato
            df_save["id_vaga"] = df_save["id_vaga"].astype(str)
            df_save["id_candidato"] = df_save["id_candidato"].astype(str)

            for _, row_ed in edited_df.iterrows():
                id_vaga = str(row_ed["id_vaga"])
                id_candidato = str(row_ed["id_candidato"])
                mask = (df_save["id_vaga"] == id_vaga) & (df_save["id_candidato"] == id_candidato)

                for col in defaults_cols.keys():
                    if col in row_ed:
                        df_save.loc[mask, col] = row_ed.get(col, defaults_cols[col])

                # Opcional: registra data/hora da última atualização
                if "data_ultima_atualizacao" not in df_save.columns:
                    df_save["data_ultima_atualizacao"] = ""
                df_save.loc[mask, "data_ultima_atualizacao"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            # Salva tudo no mesmo arquivo de vínculos
            salvar_vaga_candidatos(df_save)
            st.success("Pipeline atualizado com sucesso (somente vínculos vaga x candidato).")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar pipeline: {e}")

    # ============================================================
    # 4) (OPCIONAL) Carregar parecer antigo no formulário de Parecer
    #    — continua usando o LOG de pareceres, mas não interfere no pipeline.
    # ============================================================
    st.markdown("---")
    st.markdown("### 🔁 Carregar parecer no formulário (módulo Parecer)")

    df_sel = carregar_pareceres_log()
    if df_sel.empty:
        st.info("Nenhum parecer registrado no histórico.")
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

        st.success("Dados carregados. Vá ao módulo Recrutamento → aba Parecer para gerar novo laudo.")




