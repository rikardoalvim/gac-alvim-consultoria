# ================================
# GAC - Gerenciador Alvim Consultoria
# Aplicação principal
# ================================

import streamlit as st

from modules import (
    dashboard,
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
    auth,
    usuarios,
)

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
)

# ============================================================
# CSS GLOBAL – ESTILO iOS / LIQUID GLASS + LEGÍVEL
# ============================================================

GLOBAL_CSS = """
/* ============================================
   GLOBAL LIQUID GLASS UI - iOS 17/18 STYLE
   ============================================ */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Background geral */
.stApp {
    background: linear-gradient(
        135deg,
        rgba(203, 235, 255, 0.85) 0%,
        rgba(222, 255, 245, 0.85) 50%,
        rgba(246, 222, 255, 0.85) 100%
    ) !important;
    background-attachment: fixed !important;
}

/* Glass card */
.glass-card {
    background: rgba(255, 255, 255, 0.22);
    border-radius: 22px;
    padding: 20px;
    box-shadow:
        0 8px 32px rgba(31, 38, 135, 0.20),
        inset 0 0 25px rgba(255, 255, 255, 0.35);
    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
}

/* Botões glass */
.stButton > button {
    background: rgba(255,255,255,0.25) !important;
    color: #222 !important;
    padding: 12px 26px !important;
    border-radius: 28px !important;
    border: 1px solid rgba(255,255,255,0.45) !important;
    font-weight: 600 !important;
    backdrop-filter: blur(12px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(12px) saturate(180%) !important;
    transition: 0.18s ease-in-out !important;
    box-shadow:
        0 8px 24px rgba(0,0,0,0.15),
        inset 0 0 18px rgba(255,255,255,0.45);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow:
        0 12px 32px rgba(0,0,0,0.22),
        inset 0 0 22px rgba(255,255,255,0.55);
}

/* Inputs glass */
input, textarea, select, .stTextInput > div > div > input {
    background: rgba(255,255,255,0.25) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.45) !important;
    padding: 12px !important;
    font-size: 16px !important;
    box-shadow:
        inset 0 0 12px rgba(255,255,255,0.3) !important;
    backdrop-filter: blur(14px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
}

/* DataFrame glass */
div[data-testid="dataframe"] {
    border-radius: 26px !important;
    padding: 12px !important;
    background: rgba(255,255,255,0.25) !important;
    backdrop-filter: blur(18px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
    box-shadow:
        0 10px 32px rgba(0,0,0,0.15),
        inset 0 0 22px rgba(255,255,255,0.45) !important;
}

/* Menu superior / tabs */
div[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.22) !important;
    border-radius: 999px !important;
    padding: 10px 14px !important;
    width: 100% !important;
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 0.50rem !important;
    overflow-x: auto !important;
    scroll-behavior: smooth !important;
    box-shadow:
        0 8px 28px rgba(15,23,42,0.25),
        inset 0 0 18px rgba(255,255,255,0.55) !important;
    backdrop-filter: blur(22px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(170%) !important;
}

/* Remove scrollbar */
div[data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
div[data-baseweb="tab-list"] { 
    -ms-overflow-style: none; 
    scrollbar-width: none; 
}

/* Tab padrão */
button[role="tab"] {
    background: rgba(255,255,255,0.35) !important;
    padding: 12px 24px !important;
    border-radius: 24px !important;
    font-weight: 600 !important;
    color: #222 !important;
    transition: 0.20s ease-in-out;
    border: 1px solid rgba(255,255,255,0.50) !important;
    box-shadow:
        0 6px 22px rgba(0,0,0,0.18),
        inset 0 0 18px rgba(255,255,255,0.45) !important;
}

/* Tab selecionada */
button[role="tab"][aria-selected="true"] {
    background: rgba(255,255,255,0.90) !important;
    color: #000 !important;
    transform: translateY(-2px);
    box-shadow:
        0 12px 32px rgba(0,0,0,0.22),
        inset 0 0 22px rgba(255,255,255,0.70) !important;
}

/* Títulos */
h1, h2, h3, h4 {
    text-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.25) !important;
    border-radius: 16px !important;
    box-shadow: inset 0 0 12px rgba(255,255,255,0.4);
}
"""


# ============================================================
# ROTEAMENTO DOS MÓDULOS
# ============================================================

if modulo == "Dashboard":
    dashboard.run()

elif modulo == "Cadastros Gerais (Clientes)":
    clientes.run()

elif modulo == "Recrutamento & Seleção":
    abas = st.tabs(
        [
            "👤 Candidatos",
            "📂 Vagas",
            "📝 Parecer",
            "📁 Histórico",
            "📌 Pipeline",
            "📥 Importar antigos",
            "🔎 Hunting / LinkedIn",
        ]
    )
    with abas[0]:
        candidatos.run()
    with abas[1]:
        vagas.run()
    with abas[2]:
        parecer_mod.run()
    with abas[3]:
        historico.run()
    with abas[4]:
        pipeline_mod.run()
    with abas[5]:
        importador.run()
    with abas[6]:
        hunting.run()

elif modulo == "Sistemas / Acessos":
    acessos.run()

elif modulo == "Financeiro":
    financeiro.run()

elif modulo == "Admin - Usuários":
    usuarios.run()

    financeiro.run()

elif modulo == "Admin - Usuários":
    usuarios.run()

