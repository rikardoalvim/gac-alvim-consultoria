import urllib.parse
from datetime import datetime

import streamlit as st

from .core import (
    carregar_candidatos,
    registrar_candidato,
    LOG_CAND,
)


def run():
    st.header("🔎 Hunting / LinkedIn")

    st.markdown(
        "Aqui você monta buscas no LinkedIn, gera mensagens de abordagem e "
        "cadastra rapidamente candidatos a partir de um perfil."
    )

    # ============================
    # 1) BUSCA NO LINKEDIN
    # ============================
    st.subheader("1️⃣ Gerador de busca no LinkedIn")

    col1, col2, col3 = st.columns(3)
    with col1:
        cargo_busca = st.text_input(
            "Cargo",
            placeholder="Ex.: Analista Financeiro",
            key="hunt_busca_cargo",
        )
    with col2:
        local_busca = st.text_input(
            "Localidade",
            placeholder="Ex.: Curitiba, Paraná",
            key="hunt_busca_local",
        )
    with col3:
        extras_busca = st.text_input(
            "Palavras-chave extras",
            placeholder="Ex.: Senior Sapiens, HCM",
            key="hunt_busca_extras",
        )

    termos = " ".join([t for t in [cargo_busca, local_busca, extras_busca] if t.strip()])
    if termos:
        query = urllib.parse.quote_plus(termos)
        url_linkedin = f"https://www.linkedin.com/search/results/people/?keywords={query}"
        st.markdown(f"[🔗 Abrir busca no LinkedIn]({url_linkedin})")
    else:
        st.info("Preencha ao menos um termo para montar a busca.")

    st.markdown("---")

    # ============================
    # 2) MENSAGENS DE ABORDAGEM
    # ============================
    st.subheader("2️⃣ Mensagens padrão de abordagem")

    colm1, colm2 = st.columns(2)
    with colm1:
        tipo_vaga = st.selectbox(
            "Tipo de vaga",
            [
                "Genérica",
                "Analista Administrativo/Financeiro",
                "Suporte ao Cliente / Sistema",
                "Desenvolvedor (Flutter / Mobile)",
                "Desenvolvedor (Frontend / Vue.js)",
            ],
            key="hunt_tipo_vaga",
        )
    with colm2:
        seu_nome = st.text_input(
            "Seu nome",
            value="Rikardo",
            key="hunt_seu_nome",
        )
        nome_consultoria = st.text_input(
            "Nome da consultoria",
            value="Alvim Consultoria",
            key="hunt_nome_consultoria",
        )

    nome_candidato_msg = st.text_input(
        "Nome do candidato (para personalizar)",
        key="hunt_nome_candidato_msg",
    )
    titulo_vaga_msg = st.text_input(
        "Título da vaga",
        placeholder="Ex.: Analista Administrativo Financeiro",
        key="hunt_titulo_vaga",
    )

    # Seleciona modelo
    if tipo_vaga == "Analista Administrativo/Financeiro":
        base_msg = f"""Olá {{nome}}, tudo bem?

Meu nome é {seu_nome}, da {nome_consultoria}. Estou conduzindo um processo seletivo para **{titulo_vaga_msg or 'Analista Administrativo/Financeiro'}**, e seu perfil chamou atenção pelo histórico na área.

Você estaria aberto(a) para uma conversa rápida?"""
    elif tipo_vaga == "Suporte ao Cliente / Sistema":
        base_msg = f"""Olá {{nome}}, tudo bem?

Sou {seu_nome}, da {nome_consultoria}. Temos uma vaga de **{titulo_vaga_msg or 'Suporte ao Cliente / Sistemas'}** que pode ter forte aderência ao seu perfil.

Gostaria de conversar rapidamente sobre a oportunidade?"""
    elif tipo_vaga == "Desenvolvedor (Flutter / Mobile)":
        base_msg = f"""Olá {{nome}}, tudo bem?

Sou {seu_nome}, da {nome_consultoria}. Estamos com uma oportunidade para **{titulo_vaga_msg or 'Desenvolvedor(a) Mobile (Flutter)'}**.

Podemos conversar rapidamente sobre a vaga?"""
    elif tipo_vaga == "Desenvolvedor (Frontend / Vue.js)":
        base_msg = f"""Olá {{nome}}, tudo bem?

Meu nome é {seu_nome}, da {nome_consultoria}. Temos vaga para **{titulo_vaga_msg or 'Desenvolvedor(a) Frontend Vue.js'}** e seu perfil pode se encaixar.

Você tem interesse em conversar?"""
    else:
        base_msg = f"""Olá {{nome}}, tudo bem?

Meu nome é {seu_nome}, da {nome_consultoria}. Gostaria de falar com você sobre uma oportunidade em avaliação.

Você teria alguns minutos para conversarmos?"""

    msg_final = base_msg.replace("{nome}", nome_candidato_msg or "tudo bem")

    st.text_area(
        "Mensagem gerada:",
        value=msg_final,
        height=180,
        key="hunt_msg_final",
    )

    st.markdown("---")

    # ============================
    # 3) CADASTRAR RAPIDAMENTE
    # ============================
    st.subheader("3️⃣ Cadastrar candidato a partir do LinkedIn")

    colc1, colc2 = st.columns(2)
    with colc1:
        nome_cad = st.text_input(
            "Nome completo",
            key="hunt_nome_cad",
        )
        cidade_cad = st.text_input(
            "Cidade / UF",
            key="hunt_cidade_cad",
        )
        telefone_cad = st.text_input(
            "Telefone (DDD)",
            key="hunt_tel_cad",
        )
        idade_cad = st.text_input(
            "Idade",
            key="hunt_idade_cad",
        )
    with colc2:
        cargo_cad = st.text_input(
            "Cargo pretendido",
            key="hunt_cargo_cad",
        )
        linkedin_cad = st.text_input(
            "URL do LinkedIn",
            key="hunt_link_cad",
        )

        data_cad = st.date_input(
            "Data do cadastro",
            value=datetime.today(),
            key="hunt_data_cad",
        ).strftime("%Y-%m-%d")

    if st.button("💾 Cadastrar candidato", key="hunt_btn_salvar"):
        if not nome_cad.strip():
            st.error("Informe o nome do candidato.")
        else:
            novo_id = registrar_candidato(
                nome=nome_cad,
                idade=idade_cad,
                telefone=telefone_cad,
                cidade=cidade_cad,
                cargo_pretendido=cargo_cad,
                data_cadastro=data_cad,
            )

            df = carregar_candidatos()
            mask = df["id_candidato"] == str(novo_id)
            if mask.any():
                df.loc[mask, "linkedin"] = linkedin_cad
                df.to_csv(LOG_CAND, sep=";", index=False, encoding="utf-8")

            st.success(f"Candidato cadastrado com ID {novo_id}.")
