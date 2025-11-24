from datetime import datetime

import streamlit as st
import pandas as pd

from .core import (
    carregar_clientes,
    carregar_vagas,
    registrar_vaga,
    LOG_VAGAS,
    carregar_candidatos,
    carregar_vaga_candidatos,
    salvar_vaga_candidatos,
)


def run():
    st.header("📂 Cadastro de Vagas")

    df_cli = carregar_clientes()
    if df_cli.empty:
        st.warning("Cadastre ao menos um cliente na aba de Clientes.")
        id_cliente_sel = ""
        nome_cliente_sel = ""
    else:
        opcoes_cli = {
            int(row["id_cliente"]): row["nome_cliente"]
            for _, row in df_cli.iterrows()
        }
        id_cliente_sel = st.selectbox(
            "Cliente da vaga:",
            options=list(opcoes_cli.keys()),
            format_func=lambda x: opcoes_cli[x],
            key="vaga_cli_sel",
        )
        nome_cliente_sel = opcoes_cli[id_cliente_sel]

    col1, col2 = st.columns(2)
    with col1:
        cargo = st.text_input("Cargo da vaga")
        modalidade = st.selectbox(
            "Modalidade de contratação",
            ["CLT", "PJ", "Aprendiz", "Estatutário", "Estagiário"],
        )
    with col2:
        data_abertura = st.date_input("Data de abertura", value=datetime.today()).strftime("%Y-%m-%d")
        data_fechamento = st.date_input("Data de fechamento (pode ajustar depois)", value=datetime.today()).strftime("%Y-%m-%d")
        status = st.selectbox("Status da vaga", ["Aberta", "Em andamento", "Encerrada"])

    descricao = st.text_area(
        "Descrição detalhada da vaga",
        height=200,
        placeholder="Cole aqui a descrição da vaga (responsabilidades, requisitos, benefícios etc.)",
    )

    if st.button("💾 Salvar vaga"):
        if not nome_cliente_sel or not cargo.strip():
            st.error("Selecione um cliente e informe o cargo.")
        else:
            novo_id = registrar_vaga(
                id_cliente=str(id_cliente_sel),
                nome_cliente=nome_cliente_sel,
                cargo=cargo.strip(),
                modalidade=modalidade,
                data_abertura=data_abertura,
                data_fechamento=data_fechamento,
                status=status,
                descricao_vaga=descricao,
            )
            st.success(f"Vaga cadastrada com ID {novo_id}.")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Vagas cadastradas (edição rápida)")

    df_vagas = carregar_vagas()
    if df_vagas.empty:
        st.info("Nenhuma vaga cadastrada ainda.")
    else:
        df_vagas = df_vagas.sort_values("id_vaga")
        edited = st.data_editor(
            df_vagas,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "id_vaga": st.column_config.Column("ID Vaga", disabled=True),
            },
            key="vagas_editor",
        )
        if st.button("💾 Salvar alterações das vagas"):
            try:
                edited.to_csv(LOG_VAGAS, sep=";", index=False, encoding="utf-8")
                st.success("Vagas atualizadas com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar vagas: {e}")

    st.markdown("---")
    st.subheader("📝 Texto da vaga para LinkedIn / WhatsApp")

    df_vagas = carregar_vagas()
    if df_vagas.empty:
        st.info("Cadastre uma vaga para gerar o texto.")
    else:
        opcoes_txt = {
            int(row["id_vaga"]): f"{row['nome_cliente']} - {row['cargo']}"
            for _, row in df_vagas.iterrows()
        }
        id_v_sel = st.selectbox(
            "Selecione a vaga:",
            options=list(opcoes_txt.keys()),
            format_func=lambda x: opcoes_txt[x],
            key="vaga_txt_sel",
        )
        row_v = df_vagas[df_vagas["id_vaga"] == str(id_v_sel)].iloc[0]
        cliente_txt = row_v["nome_cliente"]
        cargo_txt = row_v["cargo"]
        modalidade_txt = row_v["modalidade"]
        desc_txt = row_v["descricao_vaga"]

        texto_linkedin = (
            f"**Vaga: {cargo_txt}**\n"
            f"**Cliente: {cliente_txt}**\n"
            f"*Modalidade de contratação: {modalidade_txt}*\n\n"
            f"{desc_txt}\n"
        )
        texto_whats = (
            f"*Vaga: {cargo_txt}*\n"
            f"*Cliente: {cliente_txt}*\n"
            f"_Modalidade de contratação: {modalidade_txt}_\n\n"
            f"{desc_txt}\n"
        )

        st.markdown("**Texto sugerido para LinkedIn:**")
        st.text_area("LinkedIn", value=texto_linkedin, height=200, key="vaga_txt_linkedin")

        st.markdown("**Texto sugerido para WhatsApp:**")
        st.text_area("WhatsApp", value=texto_whats, height=200, key="vaga_txt_whats")

    st.markdown("---")
    st.subheader("🔗 Vincular candidatos à vaga")

    df_vagas = carregar_vagas()
    df_cand = carregar_candidatos()
    if df_vagas.empty or df_cand.empty:
        st.info("É necessário ter ao menos uma vaga e um candidato.")
        return

    opcoes_vinc = {
        int(row["id_vaga"]): f"{row['id_vaga']} - {row['nome_cliente']} - {row['cargo']}"
        for _, row in df_vagas.iterrows()
    }
    id_vaga_vinc = st.selectbox(
        "Selecione a vaga:",
        options=list(opcoes_vinc.keys()),
        format_func=lambda x: opcoes_vinc[x],
        key="vaga_vinc_sel",
    )

    df_vinc = carregar_vaga_candidatos()
    vinculados = df_vinc[df_vinc["id_vaga"] == str(id_vaga_vinc)] if not df_vinc.empty else pd.DataFrame(columns=["id_vaga", "id_candidato", "data_vinculo", "observacao"])
    ids_exist = set(vinculados["id_candidato"].tolist())

    opcoes_cand = {str(row["id_candidato"]): row["nome"] for _, row in df_cand.iterrows()}
    multi = st.multiselect(
        "Candidatos da vaga:",
        options=list(opcoes_cand.keys()),
        default=list(ids_exist),
        format_func=lambda x: opcoes_cand.get(x, x),
        key="vaga_cand_multi",
    )

    if st.button("💾 Salvar vínculos candidato x vaga"):
        df_todos = carregar_vaga_candidatos()
        if not df_todos.empty:
            df_todos = df_todos[df_todos["id_vaga"] != str(id_vaga_vinc)]

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        novos = []
        for id_c in multi:
            novos.append({
                "id_vaga": str(id_vaga_vinc),
                "id_candidato": str(id_c),
                "data_vinculo": agora,
                "observacao": "",
            })

        df_novos = pd.DataFrame(novos)
        df_final = pd.concat([df_todos, df_novos], ignore_index=True) if not df_todos.empty else df_novos
        salvar_vaga_candidatos(df_final)
        st.success("Vínculos atualizados.")
        st.rerun()

    st.markdown("**Candidatos vinculados à vaga (atual):**")
    df_vinc_atual = carregar_vaga_candidatos()
    df_vinc_atual = df_vinc_atual[df_vinc_atual["id_vaga"] == str(id_vaga_vinc)]
    if df_vinc_atual.empty:
        st.info("Nenhum candidato vinculado ainda.")
    else:
        df_show = df_vinc_atual.merge(
            df_cand[["id_candidato", "nome", "telefone", "cidade"]],
            on="id_candidato",
            how="left",
        )
        st.dataframe(df_show, use_container_width=True)
