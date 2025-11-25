import os
import re
from datetime import datetime

import streamlit as st

from .core import (
    carregar_candidatos,
    registrar_candidato,
    CV_DIR,
    LOG_CAND,
    montar_link_whatsapp,
)


def run():
    st.header("👤 Cadastro de Candidatos")

    # ============================
    # NOVO CANDIDATO
    # ============================
    st.subheader("➕ Novo candidato")

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome completo do candidato", key="nome_novo")
        idade = st.text_input("Idade", key="idade_novo")
        telefone = st.text_input("Telefone (com DDD)", key="telefone_novo")
    with col2:
        cidade = st.text_input("Cidade / UF", key="cidade_novo")
        # 👇 KEY EXPLÍCITA PARA NÃO CONFLITAR COM O CAMPO DE EDIÇÃO
        cargo_pret = st.text_input("Cargo pretendido", key="cargo_pret_novo")
        data_cad = st.date_input(
            "Data do cadastro",
            value=datetime.today(),
            key="data_cad_novo"
        ).strftime("%Y-%m-%d")

    if st.button("💾 Salvar candidato", key="btn_salvar_novo"):
        if not nome.strip():
            st.error("Informe o nome do candidato.")
        else:
            novo_id = registrar_candidato(
                nome.strip(),
                idade.strip(),
                telefone.strip(),
                cidade.strip(),
                cargo_pret.strip(),
                data_cad,
            )
            st.success(f"Candidato cadastrado com ID {novo_id}.")
            st.rerun()

    st.markdown("---")

    # ============================
    # LISTA DE CANDIDATOS
    # ============================
    st.subheader("📋 Lista de candidatos")

    df = carregar_candidatos()
    if df.empty:
        st.info("Nenhum candidato cadastrado ainda.")
        return

    df_view = df.sort_values("id_candidato")
    st.dataframe(df_view, use_container_width=True)

    st.markdown("---")

    # ============================
    # FICHA DETALHADA / EDIÇÃO
    # ============================
    st.subheader("✏️ Ficha detalhada do candidato")

    opcoes = {int(row["id_candidato"]): row["nome"] for _, row in df_view.iterrows()}
    id_sel = st.selectbox(
        "Selecione o candidato:",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
        key="cand_ficha_sel",
    )

    row = df_view[df_view["id_candidato"] == str(id_sel)].iloc[0]

    colf1, colf2 = st.columns(2)
    with colf1:
        nome_f = st.text_input("Nome", value=row["nome"], key=f"nome_{id_sel}")
        idade_f = st.text_input("Idade", value=str(row["idade"]), key=f"idade_{id_sel}")
        tel_f = st.text_input("Telefone", value=row["telefone"], key=f"tel_{id_sel}")
        cidade_f = st.text_input("Cidade", value=row["cidade"], key=f"cidade_{id_sel}")
    with colf2:
        # 👇 AQUI TAMBÉM GANHA UMA KEY ÚNICA
        cargo_f = st.text_input(
            "Cargo pretendido",
            value=row["cargo_pretendido"],
            key=f"cargo_pret_{id_sel}",
        )
        data_cad_f = st.text_input(
            "Data cadastro (YYYY-MM-DD)",
            value=row["data_cadastro"],
            key=f"data_cad_{id_sel}",
        )
        linkedin_f = st.text_input(
            "LinkedIn",
            value=row.get("linkedin", ""),
            key=f"linkedin_{id_sel}",
        )

    st.markdown("**Currículo (CV) do candidato**")
    cv_atual = row.get("cv_arquivo", "") or ""
    if cv_atual and os.path.exists(cv_atual):
        st.write(f"Arquivo atual: `{cv_atual}`")
        with open(cv_atual, "rb") as f:
            cv_bytes = f.read()
        st.download_button(
            "⬇️ Baixar CV",
            data=cv_bytes,
            file_name=os.path.basename(cv_atual),
            mime="application/pdf",
            key=f"cv_down_{id_sel}",
        )
    else:
        st.write("Nenhum CV anexado.")

    uploaded_cv = st.file_uploader(
        "📎 Anexar/atualizar CV (PDF)",
        type=["pdf"],
        key=f"cv_up_{id_sel}",
    )

    if st.button("💾 Salvar ficha do candidato selecionado", key=f"btn_salvar_{id_sel}"):
        df_edit = carregar_candidatos()
        m2 = df_edit["id_candidato"] == str(id_sel)
        if not m2.any():
            st.error("Candidato não encontrado para salvar.")
        else:
            df_edit.loc[m2, "nome"] = nome_f
            df_edit.loc[m2, "idade"] = idade_f
            df_edit.loc[m2, "telefone"] = tel_f
            df_edit.loc[m2, "cidade"] = cidade_f
            df_edit.loc[m2, "cargo_pretendido"] = cargo_f
            df_edit.loc[m2, "data_cadastro"] = data_cad_f
            df_edit.loc[m2, "linkedin"] = linkedin_f

            if uploaded_cv is not None:
                base_nome = re.sub(r"\W+", "_", nome_f.strip()) or "candidato"
                cv_nome = f"cv_{id_sel}_{base_nome}.pdf"
                cv_path = os.path.join(CV_DIR, cv_nome)
                with open(cv_path, "wb") as f:
                    f.write(uploaded_cv.read())
                df_edit.loc[m2, "cv_arquivo"] = cv_path

            try:
                df_edit.to_csv(LOG_CAND, sep=";", index=False, encoding="utf-8")
                st.success("Ficha atualizada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar ficha: {e}")

    st.markdown("---")

    # ============================
    # CONTATO RÁPIDO - WHATSAPP
    # ============================
    st.subheader("📲 Contato rápido via WhatsApp")

    opcoes2 = {int(row["id_candidato"]): row["nome"] for _, row in df_view.iterrows()}
    id_sel2 = st.selectbox(
        "Selecione o candidato:",
        options=list(opcoes2.keys()),
        format_func=lambda x: opcoes2[x],
        key="cand_whats_sel",
    )
    row2 = df_view[df_view["id_candidato"] == str(id_sel2)].iloc[0]
    telefone2 = row2["telefone"]
    st.write(f"**Telefone:** {telefone2}  |  **Cidade:** {row2['cidade']}")
    link = montar_link_whatsapp(telefone2)
    if not link:
        st.warning("Telefone inválido ou não informado.")
    else:
        st.markdown(f"[💬 Abrir conversa no WhatsApp]({link})")

    link = montar_link_whatsapp(telefone)
    if not link:
        st.warning("Telefone inválido ou não informado.")
    else:
        st.markdown(f"[💬 Abrir conversa no WhatsApp]({link})")
