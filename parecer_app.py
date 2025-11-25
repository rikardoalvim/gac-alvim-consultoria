# ================================
# GAC - Gerenciador Alvim Consultoria
# Aplicação principal
# ================================

import os
import sys
import streamlit as st

from modules import (
    dashboard,          # ← ADICIONADO
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

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
)

modulo = st.sidebar.radio(
    "Selecione o módulo:",
    [
        "Dashboard",
        "Cadastros Gerais (Clientes)",
        "Recrutamento & Seleção",
        "Sistemas / Acessos",
        "Financeiro",
    ]
)

# DASHBOARD
if modulo == "Dashboard":
    dashboard.run()

# CLIENTES
elif modulo == "Cadastros Gerais (Clientes)":
    clientes.run()

# RECRUTAMENTO & SELEÇÃO
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

# ACESSOS
elif modulo == "Sistemas / Acessos":
    acessos.run()

# FINANCEIRO
elif modulo == "Financeiro":
    financeiro.run()


elif modulo == "Financeiro":
    financeiro.run()
