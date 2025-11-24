import os
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

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome completo do candidato")
        idade = st.text_input("Idade")
        telefone = st.text_input("Telefone (com DDD)")
    with col2:
        cidade = st.text_input("Cidade / UF")
        cargo_pret = st.text_input("Cargo pretendido")
        data_cad = st.date_input("Data do cadastro", value=datetime.today()).strftime("%Y-%m-%d")

    if st.button("💾 Salvar candidato"):
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
    st.subheader("📋 Lista de candidatos (edição rápida)")

    df = carregar_candidatos()
    if df.empty:
        st.info("Nenhum candidato cadastrado ainda.")
        return

    df = df.sort_values("id_candidato")
    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "id_candidato": st.column_config.Column("ID", disabled=True),
        },
        key="cand_editor",
    )

    if st.button("💾 Salvar alterações dos candidatos (grid)"):
        try:
            edited.to_csv(LOG_CAND, sep=";", index=False, encoding="utf-8")
            st.success("Candidatos atualizados com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    df = carregar_candidatos()

    st.markdown("---")
    st.subheader("🧾 Ficha detalhada do candidato")

    if df.empty:
        st.info("Nenhum candidato para detalhar.")
    else:
        opcoes = {int(row["id_candidato"]): row["nome"] for _, row in df.iterrows()}
        id_sel = st.selectbox(
            "Selecione o candidato:",
            options=list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
            key="cand_ficha_sel",
        )

        mask = df["id_candidato"] == str(id_sel)
        if not mask.any():
            st.warning("Candidato não encontrado.")
        else:
            row = df[mask].iloc[0]
            colf1, colf2 = st.columns(2)
            with colf1:
                nome_f = st.text_input("Nome", value=row["nome"])
                idade_f = st.text_input("Idade", value=str(row["idade"]))
                tel_f = st.text_input("Telefone", value=row["telefone"])
                cidade_f = st.text_input("Cidade", value=row["cidade"])
            with colf2:
                cargo_f = st.text_input("Cargo pretendido", value=row["cargo_pretendido"])
                data_cad_f = st.text_input("Data cadastro (YYYY-MM-DD)", value=row["data_cadastro"])
                linkedin_f = st.text_input("LinkedIn", value=row.get("linkedin", ""))

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

            if st.button("💾 Salvar ficha do candidato"):
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
    st.subheader("📲 Contato rápido via WhatsApp")

    df = carregar_candidatos()
    if df.empty:
        st.info("Nenhum candidato cadastrado.")
    else:
        opcoes2 = {int(row["id_candidato"]): row["nome"] for _, row in df.iterrows()}
        id_sel2 = st.selectbox(
            "Selecione o candidato:",
            options=list(opcoes2.keys()),
            format_func=lambda x: opcoes2[x],
            key="cand_whats_sel",
        )
        mask2 = df["id_candidato"] == str(id_sel2)
        if not mask2.any():
            st.warning("Candidato não encontrado.")
        else:
            r = df[mask2].iloc[0]
            telefone = r["telefone"]
            st.write(f"**Telefone:** {telefone}  |  **Cidade:** {r['cidade']}")
            link = montar_link_whatsapp(telefone)
            if not link:
                st.warning("Telefone inválido ou não informado.")
            else:
                st.markdown(f"[💬 Abrir conversa no WhatsApp]({link})")
