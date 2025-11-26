import os
from datetime import datetime

import pandas as pd
import streamlit as st

from .core import (
    carregar_pareceres_log,
    carregar_vaga_candidatos,
    carregar_vagas,
    carregar_candidatos,
    salvar_vaga_candidatos,
    montar_link_whatsapp,
)

# Tenta importar catálogo de status
try:
    from . import status_pipeline
except Exception:
    status_pipeline = None


def get_status_options():
    """
    Lê as opções de status/etapas do módulo status_pipeline, se existir.
    Caso contrário, usa defaults.
    """
    if status_pipeline is not None and hasattr(status_pipeline, "get_pipeline_status_options"):
        try:
            return status_pipeline.get_pipeline_status_options()
        except Exception:
            pass

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
    return etapa_opcoes, contratacao_opcoes


def build_pipeline_df():
    """
    Monta o DataFrame do pipeline a partir:
    - vínculos vaga x candidato
    - vagas
    - candidatos
    - último parecer por (id_candidato, id_vaga), se existir
    """
    df_vinc = carregar_vaga_candidatos()
    df_vagas = carregar_vagas()
    df_cand = carregar_candidatos()
    df_par = carregar_pareceres_log()

    if df_vinc.empty or df_vagas.empty or df_cand.empty:
        return pd.DataFrame()

    # Garante colunas de status no vínculo
    for col in ["status_etapa", "status_contratacao", "motivo_decline"]:
        if col not in df_vinc.columns:
            df_vinc[col] = ""

    # Prepara pareceres com id_vaga
    if not df_par.empty and "id_candidato" in df_par.columns:
        df_par = df_par.copy()
        df_par["id_candidato"] = df_par["id_candidato"].astype(str)

        if "id_vaga" in df_par.columns:
            df_par["id_vaga"] = df_par["id_vaga"].astype(str)
        else:
            df_par["id_vaga"] = ""

        df_par = df_par.sort_values("data_hora")

        # Agrupamento por (id_candidato, id_vaga) para último parecer
        df_par_latest = df_par.drop_duplicates(subset=["id_candidato", "id_vaga"], keep="last")
        df_par_latest = df_par_latest[
            [
                "id_candidato",
                "id_vaga",
                "data_hora",
                "cliente",
                "cargo",
                "caminho_arquivo",
            ]
        ]
    else:
        df_par_latest = pd.DataFrame(
            columns=["id_candidato", "id_vaga", "data_hora", "cliente", "cargo", "caminho_arquivo"]
        )

    df_vinc = df_vinc.copy()
    df_vinc["id_vaga"] = df_vinc["id_vaga"].astype(str)
    df_vinc["id_candidato"] = df_vinc["id_candidato"].astype(str)

    df_vagas = df_vagas.copy()
    df_vagas["id_vaga"] = df_vagas["id_vaga"].astype(str)

    df_cand = df_cand.copy()
    df_cand["id_candidato"] = df_cand["id_candidato"].astype(str)

    # Base: vínculos + vaga + candidato
    df_pipe = df_vinc.merge(
        df_vagas[["id_vaga", "nome_cliente", "cargo", "status"]],
        on="id_vaga",
        how="left",
    ).merge(
        df_cand[["id_candidato", "nome", "telefone", "cidade"]],
        on="id_candidato",
        how="left",
    )

    # Join com último parecer por (id_candidato, id_vaga)
    if not df_par_latest.empty:
        df_pipe = df_pipe.merge(
            df_par_latest,
            on=["id_candidato", "id_vaga"],
            how="left",
            suffixes=("", "_parecer"),
        )
    else:
        df_pipe["data_hora"] = ""
        df_pipe["caminho_arquivo"] = ""

    df_pipe.rename(
        columns={
            "data_hora": "ultima_data_parecer",
        },
        inplace=True,
    )

    # Ordena por data de vínculo, se existir
    if "data_vinculo" in df_pipe.columns:
        try:
            df_pipe["data_vinculo_dt"] = pd.to_datetime(df_pipe["data_vinculo"])
            df_pipe = df_pipe.sort_values("data_vinculo_dt", ascending=False)
        except Exception:
            df_pipe = df_pipe.sort_values(["nome_cliente", "cargo", "nome"])
    else:
        df_pipe = df_pipe.sort_values(["nome_cliente", "cargo", "nome"])

    return df_pipe


def run():
    st.header("📌 Pipeline de Candidatos")

    df_pipe = build_pipeline_df()
    if df_pipe.empty:
        st.info(
            "Nenhum vínculo de vaga x candidato encontrado. "
            "Cadastre vínculos na tela de Vagas e gere pareceres no módulo Parecer."
        )
        return

    etapa_opcoes, contratacao_opcoes = get_status_options()

    # ======================================
    # FILTROS – estilo “card”
    # ======================================
    with st.expander("🎯 Filtros do pipeline", expanded=False):
        colf1, colf2, colf3 = st.columns(3)
        with colf1:
            filtro_cliente = st.text_input("Cliente (contém)")
        with colf2:
            filtro_cargo = st.text_input("Cargo (contém)")
        with colf3:
            filtro_candidato = st.text_input("Candidato (contém)")

        colf4, colf5 = st.columns(2)
        with colf4:
            etapa_filter = st.selectbox(
                "Etapa do pipeline",
                options=["(Todas)"] + etapa_opcoes,
            )
        with colf5:
            status_filter = st.selectbox(
                "Status de contratação",
                options=["(Todos)"] + contratacao_opcoes,
            )

    df_view = df_pipe.copy()

    if filtro_cliente.strip():
        df_view = df_view[
            df_view["nome_cliente"].fillna("").str.lower().str.contains(filtro_cliente.strip().lower())
        ]
    if filtro_cargo.strip():
        df_view = df_view[
            df_view["cargo"].fillna("").str.lower().str.contains(filtro_cargo.strip().lower())
        ]
    if filtro_candidato.strip():
        df_view = df_view[
            df_view["nome"].fillna("").str.lower().str.contains(filtro_candidato.strip().lower())
        ]
    if etapa_filter != "(Todas)":
        df_view = df_view[df_view["status_etapa"] == etapa_filter]
    if status_filter != "(Todos)":
        df_view = df_view[df_view["status_contratacao"] == status_filter]

    if df_view.empty:
        st.warning("Nenhum registro encontrado com os filtros informados.")
        return

    # ======================================
    # TABELA RESUMO – ESTILO GLASS
    # ======================================
    def render_tabela_html(df: pd.DataFrame):
        cols = [
            "id_vaga",
            "id_candidato",
            "nome_cliente",
            "cargo",
            "nome",
            "cidade",
            "status_etapa",
            "status_contratacao",
            "ultima_data_parecer",
        ]
        headers = [
            "ID Vaga",
            "ID Cand.",
            "Cliente",
            "Cargo",
            "Candidato",
            "Cidade",
            "Etapa",
            "Status",
            "Último parecer",
        ]

        sub = df[cols].fillna("")
        html = ["<table>"]
        html.append("<thead><tr>")
        for h in headers:
            html.append(f"<th>{h}</th>")
        html.append("</tr></thead>")
        html.append("<tbody>")
        for _, row in sub.iterrows():
            html.append("<tr>")
            for c in cols:
                valor = row[c]
                html.append(f"<td>{valor}</td>")
            html.append("</tr>")
        html.append("</tbody></table>")
        st.markdown("".join(html), unsafe_allow_html=True)

    st.subheader("📋 Visão geral do pipeline")
    render_tabela_html(df_view)

    st.markdown("---")

    # ======================================
    # AÇÕES EM UM REGISTRO
    # ======================================
    st.subheader("⚙️ Ações em um registro do pipeline")

    opcoes = {}
    for idx, row in df_view.iterrows():
        chave = idx
        label = (
            f"[Vaga {row['id_vaga']}] {row['nome_cliente']} - {row['cargo']} | "
            f"Cand.: {row['nome']} ({row['cidade']})"
        )
        opcoes[chave] = label

    idx_sel = st.selectbox(
        "Selecione um registro:",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
    )

    row_sel = df_view.loc[idx_sel]

    colA, colB, colC, colD = st.columns(4)

    # 1) Download do parecer
    with colA:
        caminho = str(row_sel.get("caminho_arquivo", "") or "")
        if caminho and os.path.exists(caminho):
            try:
                with open(caminho, "rb") as f:
                    parecer_bytes = f.read()
                fname = os.path.basename(caminho)
                st.download_button(
                    "⬇️ Baixar parecer",
                    data=parecer_bytes,
                    file_name=fname,
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Erro ao carregar parecer para download: {e}")
        else:
            st.button("⬇️ Baixar parecer", disabled=True, help="Parecer não encontrado")

    # 2) WhatsApp
    with colB:
        telefone = str(row_sel.get("telefone", "") or "")
        link_whats = montar_link_whatsapp(telefone) if telefone else ""
        if link_whats:
            st.markdown(f"[💬 Abrir WhatsApp]({link_whats})")
        else:
            st.button("💬 Abrir WhatsApp", disabled=True, help="Telefone não informado")

    # 3) Label
    with colC:
        st.markdown("**Editar status**")

    # 4) Editar parecer no módulo Parecer
    with colD:
        if st.button("📝 Editar parecer no módulo Parecer"):
            df_par = carregar_pareceres_log()
            if df_par.empty:
                st.warning("Nenhum parecer encontrado para este candidato.")
            else:
                df_par = df_par.copy()
                df_par["id_candidato"] = df_par["id_candidato"].astype(str)
                if "id_vaga" in df_par.columns:
                    df_par["id_vaga"] = df_par["id_vaga"].astype(str)
                else:
                    df_par["id_vaga"] = ""

                registros = df_par[
                    (df_par["id_candidato"] == str(row_sel["id_candidato"]))
                    & (df_par["id_vaga"] == str(row_sel["id_vaga"]))
                ]

                if registros.empty:
                    # fallback: último parecer só por candidato
                    registros = df_par[df_par["id_candidato"] == str(row_sel["id_candidato"])]

                if registros.empty:
                    st.warning("Nenhum parecer encontrado para este candidato/vaga.")
                else:
                    reg = registros.sort_values("data_hora").iloc[-1]

                    st.session_state["cliente"] = reg.get("cliente", "")
                    st.session_state["cargo"] = reg.get("cargo", "")
                    st.session_state["nome"] = reg.get("nome", "")
                    st.session_state["localidade"] = reg.get("localidade", "")
                    st.session_state["idade"] = str(reg.get("idade", ""))
                    st.session_state["pretensao"] = reg.get("pretensao", "")
                    st.session_state["linkedin"] = reg.get("linkedin", "")
                    st.session_state["resumo_profissional"] = reg.get("resumo_profissional", "")
                    st.session_state["analise_perfil"] = reg.get("analise_perfil", "")
                    st.session_state["conclusao_texto"] = reg.get("conclusao_texto", "")
                    st.session_state["id_candidato_selecionado"] = str(reg.get("id_candidato", ""))
                    st.session_state["id_vaga_selecionada"] = str(reg.get("id_vaga", ""))

                    st.success(
                        "Dados carregados no formulário de Parecer. "
                        "Acesse o módulo R&S → Parecer para editar e gerar nova versão."
                    )

    st.markdown("---")

    # ======================================
    # FORM DE EDIÇÃO DO STATUS / MOTIVO
    # ======================================
    st.subheader("✏️ Editar status deste registro")

    etapa_atual = row_sel.get("status_etapa", "") or ""
    status_atual = row_sel.get("status_contratacao", "") or ""
    motivo_atual = row_sel.get("motivo_decline", "") or ""

    col1, col2 = st.columns(2)
    with col1:
        etapa_opts = [""] + etapa_opcoes
        idx_etapa = etapa_opts.index(etapa_atual) if etapa_atual in etapa_opcoes else 0
        etapa_nova = st.selectbox(
            "Etapa do pipeline",
            options=etapa_opts,
            index=idx_etapa,
            key=f"etapa_edit_{idx_sel}",
        )
    with col2:
        status_opts = [""] + contratacao_opcoes
        idx_status = status_opts.index(status_atual) if status_atual in contratacao_opcoes else 0
        status_novo = st.selectbox(
            "Status de contratação",
            options=status_opts,
            index=idx_status,
            key=f"status_edit_{idx_sel}",
        )

    motivo_novo = st.text_area(
        "Motivo de declínio / observações",
        value=motivo_atual,
        height=80,
        key=f"motivo_edit_{idx_sel}",
    )

    if st.button("💾 Salvar status do pipeline"):
        try:
            df_vinc = carregar_vaga_candidatos()
            if df_vinc.empty:
                st.error("Arquivo de vínculos vazio. Nada para atualizar.")
            else:
                df_vinc = df_vinc.copy()
                df_vinc["id_vaga"] = df_vinc["id_vaga"].astype(str)
                df_vinc["id_candidato"] = df_vinc["id_candidato"].astype(str)

                mask = (df_vinc["id_vaga"] == str(row_sel["id_vaga"])) & (
                    df_vinc["id_candidato"] == str(row_sel["id_candidato"])
                )
                if not mask.any():
                    st.error("Registro de vínculo não encontrado para atualização.")
                else:
                    for col, val in [
                        ("status_etapa", etapa_nova),
                        ("status_contratacao", status_novo),
                        ("motivo_decline", motivo_novo),
                    ]:
                        if col not in df_vinc.columns:
                            df_vinc[col] = ""
                        df_vinc.loc[mask, col] = val

                    salvar_vaga_candidatos(df_vinc)
                    st.success("Status do pipeline atualizado com sucesso!")
                    st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar status do pipeline: {e}")




