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
<style>

/* Fundo geral estilo iOS */
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #e5edff 0%, #f5f7fb 45%, #dde6f3 100%) !important;
}

/* Container raiz sem fundo sólido extra */
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}

/* Conteúdo principal: card claro com leve glass */
.main .block-container {
    background: rgba(255,255,255,0.96);
    backdrop-filter: blur(14px) saturate(160%);
    -webkit-backdrop-filter: blur(14px) saturate(160%);
    border-radius: 22px;
    padding: 2rem 3rem;
    margin-top: 1.5rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 32px rgba(15,23,42,0.15);
}

/* SIDEBAR – vidro escuro suave */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(15,23,42,0.9)) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(148,163,184,0.4);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Títulos e textos principais */
h1, h2, h3, h4 {
    color: #0f172a !important;
    letter-spacing: -0.03em;
}
.stMarkdown p {
    color: #1e293b !important;
}

/* =========================
   BOTÕES (iOS style)
   ========================= */
.stButton > button {
    background: linear-gradient(135deg, #f9fafb, #e5edff);
    color: #0f172a !important;
    padding: 0.6rem 1.25rem;
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.8);
    box-shadow: 0 6px 18px rgba(15,23,42,0.18);
    font-weight: 600;
    font-size: 0.94rem;
    transition: all 0.18s ease-out;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #eef2ff, #e0e7ff);
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 10px 26px rgba(15,23,42,0.24);
}

/* =========================
   INPUTS / TEXTAREAS / SELECTS
   ========================= */

/* Caixas de texto iOS: brancas, borda azul clara, texto escuro */
.stTextInput input,
.stTextArea textarea {
    background-color: #f9fafb !important;
    color: #0f172a !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: inset 0 0 0 1px rgba(148,163,184,0.35);
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

/* Wrapper dos inputs (para remover contorno preto grosso) */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: transparent !important;
    border-radius: 14px !important;
    border: none !important;
    box-shadow: none !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: #f9fafb !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: inset 0 0 0 1px rgba(148,163,184,0.35);
}

/* Foco nos campos – borda azul estilo iOS */
.stTextInput input:focus,
.stTextArea textarea:focus,
.stSelectbox > div > div:focus-within {
    outline: none !important;
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.35) !important;
}

/* Texto interno sempre escuro */
input, textarea, select {
    color: #0f172a !important;
}

/* Dropdown das listas (options) */
div[role="listbox"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 10px 26px rgba(15,23,42,0.24);
}
div[role="option"] {
    color: #0f172a !important;
}

/* =========================
   DATAFRAMES (tabelas AG-Grid)
   ========================= */

div[data-testid="stDataFrame"] {
    background: #ffffff !important;
    border-radius: 18px !important;
    padding: 0.45rem;
    box-shadow: 0 8px 24px rgba(15,23,42,0.20);
}

/* Força tema claro dentro do AG-Grid */
div[data-testid="stDataFrame"] .ag-root-wrapper,
div[data-testid="stDataFrame"] .ag-root,
div[data-testid="stDataFrame"] .ag-header,
div[data-testid="stDataFrame"] .ag-row {
    background-color: #f9fafb !important;
    color: #0f172a !important;
}
div[data-testid="stDataFrame"] .ag-header-cell-label {
    color: #0f172a !important;
    font-weight: 600;
}
div[data-testid="stDataFrame"] .ag-cell {
    color: #0f172a !important;
}

/* =========================
   TABS (modo iOS)
   ========================= */
div[data-baseweb="tab-list"] {
    background: rgba(226,232,240,0.8);
    border-radius: 999px;
    padding: 4px;
}
button[role="tab"] {
    border-radius: 999px !important;
    padding: 0.35rem 0.95rem !important;
    color: #475569 !important;
}
button[role="tab"][aria-selected="true"] {
    background: #ffffff !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(15,23,42,0.20);
}

/* Alertas */
div[data-testid="stAlert"] {
    border-radius: 14px;
    background: #f9fafb !important;
}

/* Radio na sidebar */
section[data-testid="stSidebar"] .stRadio label {
    font-weight: 600;
}

</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ============================================================
# AUTENTICAÇÃO
# ============================================================

if (
    "user" not in st.session_state
    or st.session_state["user"] is None
    or st.session_state.get("forcar_troca_senha", False)
):
    auth.run()
    st.stop()

# Info do usuário logado no sidebar
st.sidebar.markdown(f"👤 Usuário: **{st.session_state['user']['username']}**")
if st.sidebar.button("Sair", use_container_width=True):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")

# ============================================================
# MENU LATERAL
# ============================================================

opcoes_menu = [
    "Dashboard",
    "Cadastros Gerais (Clientes)",
    "Recrutamento & Seleção",
    "Sistemas / Acessos",
    "Financeiro",
]

if st.session_state["user"].get("is_admin", False):
    opcoes_menu.append("Admin - Usuários")

modulo = st.sidebar.radio(
    "Selecione o módulo:",
    opcoes_menu,
)

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

