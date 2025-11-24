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

    # ============================================
    # 1) GERADOR DE BUSCA NO LINKEDIN
    # ============================================
    st.subheader("1️⃣ Gerador de busca no LinkedIn")

    col1, col2, col3 = st.columns(3)
    with col1:
        cargo_busca = st.text_input("Cargo", placeholder="Ex.: Analista Financeiro")
    with col2:
        local_busca = st.text_input("Localidade", placeholder="Ex.: Curitiba, Paraná")
    with col3:
        extras_busca = st.text_input("Palavras-chave extras", placeholder="Ex.: Senior Sapiens, HCM")

    termos = " ".join([t for t in [cargo_busca, local_busca, extras_busca] if t.strip()])
    if termos:
        query = urllib.parse.quote_plus(termos)
        url_linkedin = f"https://www.linkedin.com/search/results/people/?keywords={query}"
        st.markdown(f"[🔗 Abrir busca no LinkedIn]({url_linkedin})")
        st.caption("Clique no link acima para abrir a busca já filtrada no LinkedIn (você usa manualmente).")
    else:
        st.info("Preencha ao menos um dos campos para gerar o link de busca.")

    st.markdown("---")

    # ============================================
    # 2) MENSAGENS PADRÃO DE ABORDAGEM
    # ============================================
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
        )
    with colm2:
        seu_nome = st.text_input("Seu nome (recrutador)", value="Rikardo")
        nome_consultoria = st.text_input("Nome da consultoria", value="Alvim Consultoria")

    nome_candidato_msg = st.text_input("Nome do candidato (para personalizar a mensagem)", value="")
    titulo_vaga_msg = st.text_input("Título da vaga", placeholder="Ex.: Analista Administrativo Financeiro")

    if tipo_vaga == "Analista Administrativo/Financeiro":
        base_msg = f"""
Olá {{nome_candidato}}, tudo bem?

Meu nome é {seu_nome} e atuo na {nome_consultoria}. Estou conduzindo um processo seletivo para a posição de **{titulo_vaga_msg or 'Analista Administrativo/Financeiro'}** em um cliente nosso, e seu perfil chamou minha atenção pelo histórico na área administrativa/financeira.

Gostaria de saber se você está aberto(a) para conversar rapidamente sobre a oportunidade. 
Se fizer sentido, podemos alinhar expectativas, contexto da vaga e próximos passos.

Se preferir, pode me chamar por aqui mesmo ou compartilhar um telefone para contato. 🙂
"""
    elif tipo_vaga == "Suporte ao Cliente / Sistema":
        base_msg = f"""
Olá {{nome_candidato}}, tudo bem?

Sou {seu_nome}, da {nome_consultoria}. Estou conduzindo uma vaga de **{titulo_vaga_msg or 'Analista de Suporte ao Cliente / Sistemas'}** em uma empresa de tecnologia, com foco em atendimento ao usuário, suporte funcional e treinamentos.

Vi que você possui experiência com atendimento/suporte e acredito que possa ter aderência à oportunidade.

Você teria interesse em conhecer melhor a vaga? Se sim, posso compartilhar mais detalhes e alinhar uma conversa rápida.
"""
    elif tipo_vaga == "Desenvolvedor (Flutter / Mobile)":
        base_msg = f"""
Olá {{nome_candidato}}, tudo bem?

Me chamo {seu_nome} e atuo na {nome_consultoria}. Estou com uma oportunidade para **{titulo_vaga_msg or 'Desenvolvedor(a) Mobile (Flutter)'}** em uma empresa de tecnologia, com foco em apps modernos e boas práticas de desenvolvimento.

Pelo que vi do seu perfil, sua experiência com mobile/Flutter pode se encaixar bem nessa posição.

Você está aberto(a) para conversar rapidamente sobre a vaga? Posso te passar o contexto, modelo de contratação e stack utilizada.
"""
    elif tipo_vaga == "Desenvolvedor (Frontend / Vue.js)":
        base_msg = f"""
Olá {{nome_candidato}}, tudo bem?

Sou {seu_nome}, da {nome_consultoria}. Estou conduzindo uma seleção para **{titulo_vaga_msg or 'Desenvolvedor(a) Frontend (Vue.js)'}** em uma empresa de tecnologia que trabalha com projetos desafiadores e foco em UX.

Seu perfil com frontend e frameworks modernos chamou atenção para avaliarmos um possível fit.

Você teria interesse em conhecer melhor a oportunidade? Se sim, posso compartilhar mais detalhes e alinhar uma conversa rápida.
"""
    else:  # Genérica
        base_msg = f"""
Olá {{nome_candidato}}, tudo bem?

Meu nome é {seu_nome} e atuo na {nome_consultoria}. Estou conduzindo um processo seletivo e, ao analisar seu perfil, achei interessante avaliar um possível fit com uma oportunidade em aberto.

Você estaria aberto(a) para uma conversa rápida para eu te apresentar a vaga e entender melhor seus interesses e momento de carreira?

Se preferir, pode me responder por aqui mesmo ou compartilhar um telefone para contato.
"""

    msg_final = base_msg.replace("{nome_candidato}", nome_candidato_msg or "tudo bem")

    st.markdown("**Mensagem sugerida para copiar e colar no LinkedIn:**")
    st.text_area("Mensagem de abordagem", value=msg_final, height=220, key="hunting_msg")

    st.caption("💡 Dica: personalize sempre o início da mensagem com algo específico do perfil da pessoa.")

    st.markdown("---")

    # ============================================
    # 3) CADASTRAR CANDIDATO A PARTIR DO LINKEDIN
    # ============================================
    st.subheader("3️⃣ Cadastrar candidato a partir do perfil do LinkedIn")

    st.write(
        "Com o perfil aberto no LinkedIn, copie as informações básicas e cadastre rapidamente "
        "o candidato aqui no GAC."
    )

    colc1, colc2 = st.columns(2)
    with colc1:
        nome_cad = st.text_input("Nome completo do candidato")
        cidade_cad = st.text_input("Cidade / UF")
        telefone_cad = st.text_input("Telefone (com DDD)", placeholder="Opcional")
        idade_cad = st.text_input("Idade (opcional)")
    with colc2:
        cargo_cad = st.text_input("Cargo pretendido / Perfil principal")
        linkedin_cad = st.text_input("URL do LinkedIn", placeholder="https://www.linkedin.com/in/...")

        data_cad = st.date_input("Data do cadastro", value=datetime.today()).strftime("%Y-%m-%d")

    if st.button("💾 Cadastrar candidato a partir do LinkedIn"):
        if not nome_cad.strip():
            st.error("Informe ao menos o nome do candidato.")
        else:
            # registra candidato base
            novo_id = registrar_candidato(
                nome=nome_cad.strip(),
                idade=idade_cad.strip(),
                telefone=telefone_cad.strip(),
                cidade=cidade_cad.strip(),
                cargo_pretendido=cargo_cad.strip(),
                data_cadastro=data_cad,
            )
            # atualiza linkedin no CSV
            df = carregar_candidatos()
            mask = df["id_candidato"] == str(novo_id)
            if mask.any():
                df.loc[mask, "linkedin"] = linkedin_cad.strip()
                df.to_csv(LOG_CAND, sep=";", index=False, encoding="utf-8")

            st.success(f"Candidato cadastrado com ID {novo_id}. Você pode complementar na aba Candidatos.")
