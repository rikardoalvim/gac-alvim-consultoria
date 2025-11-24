# -*- coding: utf-8 -*-
# GAC - Gerenciador Alvim Consultoria

import streamlit as st

from modules import (
    clientes,
    candidatos,
    vagas,
    acessos,
    parecer_mod,
    historico,
    pipeline_mod,
    importador,
    financeiro,
    hunting,
)

st.set_page_config(page_title="GAC - Gerenciador Alvim Consultoria",
                   page_icon="🧩",
                   layout="wide")

st.title("🧩 GAC - Gerenciador Alvim Consultoria")

modulo = st.sidebar.radio(
    "Selecione o módulo:",
    [
        "Cadastros Gerais (Clientes)",
        "Recrutamento & Seleção",
        "Sistemas / Acessos",
        "Financeiro",
    ]
)

if modulo == "Cadastros Gerais (Clientes)":
    clientes.run()

elif modulo == "Recrutamento & Seleção":
    sub = st.tabs([
        "👤 Candidatos",
        "📂 Vagas",
        "📝 Parecer",
        "📁 Histórico",
        "📌 Pipeline",
        "📥 Importar antigos",
         "🔎 Hunting / LinkedIn",
    ])
    with sub[0]:
        candidatos.run()
    with sub[1]:
        vagas.run()
    with sub[2]:
        parecer_mod.run()
    with sub[3]:
        historico.run()
    with sub[4]:
        pipeline_mod.run()
    with sub[5]:
        importador.run()
    with sub[6]:
        hunting.run()

elif modulo == "Sistemas / Acessos":
    acessos.run()

elif modulo == "Financeiro":
    financeiro.run()
