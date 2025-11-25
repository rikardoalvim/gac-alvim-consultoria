import streamlit as st
import pandas as pd
from datetime import datetime

from .core import (
    carregar_clientes,
    carregar_candidatos,
    carregar_vagas,
)


def card_metric(label: str, value, subtitle: str = "", color: str = "#1f6feb"):
    """
    Renderiza um card simples e bonito para métricas.
    """
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            padding: 14px 18px;
            border-radius: 12px;
            color: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            margin-bottom: 8px;
        ">
            <div style="font-size: 13px; opacity: 0.85; font-weight: 500;">
                {label}
            </div>
            <div style="font-size: 24px; font-weight: 700; margin-top: 4px;">
                {value}
            </div>
            <div style="font-size: 11px; opacity: 0.9; margin-top: 2px;">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run():
    st.header("📊 Dashboard Geral - GAC")

    # Carregar dados
    df_cli = carregar_clientes()
    df_cand = carregar_candidatos()
    df_vagas = carregar_vagas()

    # =========================================================
    # CARDS SUPERIORES
    # =========================================================
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
        card_metric("Clientes", qtd_clientes, "cadastros ativos", "#2563eb")
    with col2:
        card_metric("Candidatos", qtd_candidatos, "banco de talentos", "#7c3aed")
    with col3:
        card_metric("Vagas totais", qtd_vagas, "no histórico", "#059669")
    with col4:
        card_metric("Vagas abertas", vagas_abertas, "em andamento", "#d97706")

    st.markdown("---")

    # =========================================================
    # GRÁFICOS DE VAGAS
    # =========================================================
    col_g1, col_g2 = st.columns(2)

    # ---- VAGAS POR STATUS ----
    with col_g1:
        st.subheader("📌 Vagas por status")

        if df_vagas.empty:
            st.info("Nenhuma vaga cadastrada ainda.")
        else:
            dist_status = (
                df_vagas["status"]
                .value_counts()
                .reindex(["Aberta", "Em andamento", "Encerrada"])
                .fillna(0)
                .astype(int)
            )
            df_status = pd.DataFrame(
                {"Status": dist_status.index, "Quantidade": dist_status.values}
            ).set_index("Status")
            st.bar_chart(df_status)

    # ---- VAGAS ABERTAS POR CLIENTE ----
    with col_g2:
        st.subheader("🏢 Vagas abertas por cliente")

        if df_vagas.empty:
            st.info("Nenhuma vaga cadastrada ainda.")
        else:
            df_abertas = df_vagas[df_vagas["status"] == "Aberta"].copy()
            if df_abertas.empty:
                st.info("Nenhuma vaga aberta no momento.")
            else:
                por_cliente = (
                    df_abertas.groupby("nome_cliente")["id_vaga"]
                    .count()
                    .sort_values(ascending=False)
                    .head(10)
                )
                df_cli_vagas = pd.DataFrame(
                    {"Cliente": por_cliente.index, "Vagas abertas": por_cliente.values}
                ).set_index("Cliente")
                st.bar_chart(df_cli_vagas)

    st.markdown("---")

    # =========================================================
    # GRÁFICO DE CANDIDATOS POR CARGO
    # =========================================================
    st.subheader("👤 Candidatos por cargo pretendido (Top 10)")

    if df_cand.empty or "cargo_pretendido" not in df_cand.columns:
        st.info("Ainda não há candidatos com cargo pretendido cadastrado.")
    else:
        cargos = (
            df_cand["cargo_pretendido"]
            .fillna("")
            .replace("", "Não informado")
            .value_counts()
            .head(10)
        )
        df_cargos = pd.DataFrame(
            {"Cargo pretendido": cargos.index, "Quantidade": cargos.values}
        ).set_index("Cargo pretendido")
        st.bar_chart(df_cargos)

    st.markdown("---")

    # =========================================================
    # ÚLTIMAS VAGAS
    # =========================================================
    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.subheader("🧩 Últimas vagas cadastradas")

        if df_vagas.empty:
            st.info("Nenhuma vaga cadastrada.")
        else:
            cols_vagas = [
                "id_vaga",
                "nome_cliente",
                "cargo",
                "status",
                "data_abertura",
                "data_fechamento",
            ]
            cols_vagas = [c for c in cols_vagas if c in df_vagas.columns]

            df_vagas_view = (
                df_vagas[cols_vagas]
                .sort_values("id_vaga", ascending=False)
                .head(10)
            )
            st.dataframe(df_vagas_view, use_container_width=True, height=320)

    # =========================================================
    # ÚLTIMOS CANDIDATOS
    # =========================================================
    with col_l2:
        st.subheader("👤 Últimos candidatos cadastrados")

        if df_cand.empty:
            st.info("Nenhum candidato cadastrado.")
        else:
            df_cand_view = df_cand.copy()

            # tenta ordenar por data_cadastro, se existir
            if "data_cadastro" in df_cand_view.columns:
                try:
                    df_cand_view["data_cadastro_ord"] = pd.to_datetime(
                        df_cand_view["data_cadastro"], errors="coerce"
                    )
                    df_cand_view = df_cand_view.sort_values(
                        "data_cadastro_ord", ascending=False
                    )
                except Exception:
                    df_cand_view = df_cand_view.sort_values(
                        "id_candidato", ascending=False
                    )
            else:
                df_cand_view = df_cand_view.sort_values(
                    "id_candidato", ascending=False
                )

            cols_cand = [
                "id_candidato",
                "nome",
                "telefone",
                "cidade",
                "cargo_pretendido",
                "data_cadastro",
            ]
            cols_cand = [c for c in cols_cand if c in df_cand_view.columns]

            st.dataframe(
                df_cand_view[cols_cand].head(10),
                use_container_width=True,
                height=320,
            )

    st.markdown("---")

    # =========================================================
    # RESUMO DE CLIENTES
    # =========================================================
    st.subheader("🏢 Clientes cadastrados (resumo)")

    if df_cli.empty:
        st.info("Nenhum cliente cadastrado.")
    else:
        cols_cli = ["id_cliente", "nome_cliente"]
        if "cidade" in df_cli.columns:
            cols_cli.append("cidade")
        if "telefone" in df_cli.columns:
            cols_cli.append("telefone")

        df_cli_view = df_cli[cols_cli].sort_values("id_cliente").head(15)
        st.dataframe(df_cli_view, use_container_width=True)

