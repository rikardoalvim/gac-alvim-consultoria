import streamlit as st
import pandas as pd
from datetime import datetime

from .core import (
    carregar_clientes,
    carregar_candidatos,
    carregar_vagas,
)


def run():
    st.header("📊 Dashboard Geral")

    # Carregar dados
    df_cli = carregar_clientes()
    df_cand = carregar_candidatos()
    df_vagas = carregar_vagas()

    # ============================
    # MÉTRICAS PRINCIPAIS
    # ============================
    st.subheader("🔢 Indicadores gerais")

    qtd_clientes = 0 if df_cli.empty else len(df_cli)
    qtd_candidatos = 0 if df_cand.empty else len(df_cand)
    qtd_vagas = 0 if df_vagas.empty else len(df_vagas)

    if df_vagas.empty:
        vagas_abertas = vagas_andamento = vagas_fechadas = 0
    else:
        vagas_abertas = (df_vagas["status"] == "Aberta").sum()
        vagas_andamento = (df_vagas["status"] == "Em andamento").sum()
        vagas_fechadas = (df_vagas["status"] == "Encerrada").sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Clientes", qtd_clientes)
    with col2:
        st.metric("Candidatos", qtd_candidatos)
    with col3:
        st.metric("Vagas totais", qtd_vagas)
    with col4:
        st.metric("Vagas abertas", vagas_abertas)

    st.markdown("---")

    # ============================
    # DISTRIBUIÇÃO DE VAGAS POR STATUS
    # ============================
    st.subheader("📌 Vagas por status")

    if df_vagas.empty:
        st.info("Nenhuma vaga cadastrada ainda.")
    else:
        dist_status = pd.DataFrame(
            {
                "Status": ["Aberta", "Em andamento", "Encerrada"],
                "Quantidade": [vagas_abertas, vagas_andamento, vagas_fechadas],
            }
        )
        st.bar_chart(dist_status.set_index("Status"))

    st.markdown("---")

    # ============================
    # ÚLTIMAS VAGAS
    # ============================
    st.subheader("🧩 Últimas vagas cadastradas")

    if df_vagas.empty:
        st.info("Nenhuma vaga cadastrada.")
    else:
        df_vagas_view = (
            df_vagas[["id_vaga", "nome_cliente", "cargo", "status", "data_abertura"]]
            .sort_values("id_vaga", ascending=False)
            .head(5)
        )
        st.dataframe(df_vagas_view, use_container_width=True)

    st.markdown("---")

    # ============================
    # ÚLTIMOS CANDIDATOS
    # ============================
    st.subheader("👤 Últimos candidatos cadastrados")

    if df_cand.empty:
        st.info("Nenhum candidato cadastrado.")
    else:
        col_data = "data_cadastro" if "data_cadastro" in df_cand.columns else None
        cols_show = ["id_candidato", "nome", "telefone", "cidade", "cargo_pretendido"]
        cols_show = [c for c in cols_show if c in df_cand.columns]

        df_cand_view = df_cand.copy()
        if col_data:
            df_cand_view = df_cand_view.sort_values(col_data, ascending=False)
        else:
            df_cand_view = df_cand_view.sort_values("id_candidato", ascending=False)

        st.dataframe(df_cand_view[cols_show].head(10), use_container_width=True)

    st.markdown("---")

    # ============================
    # RESUMO CLIENTES
    # ============================
    st.subheader("🏢 Clientes cadastrados (resumo)")

    if df_cli.empty:
        st.info("Nenhum cliente cadastrado.")
    else:
        df_cli_view = df_cli[["id_cliente", "nome_cliente", "cidade", "telefone"]].head(10) \
            if all(col in df_cli.columns for col in ["cidade", "telefone"]) \
            else df_cli[["id_cliente", "nome_cliente"]].head(10)

        st.dataframe(df_cli_view, use_container_width=True)
