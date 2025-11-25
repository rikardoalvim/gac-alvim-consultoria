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

/* FUNDO GERAL – LIQUID GLASS APPLE STYLE */
html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 0% 0%, #9bb5ff 0, transparent 45%),
        radial-gradient(circle at 100% 0%, #fbc2ff 0, transparent 40%),
        radial-gradient(circle at 50% 100%, #a5f3fc 0, #e5f0ff 55%);
}

/* container raiz sem fundo */
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}

/* CONTEÚDO PRINCIPAL – CARD LIQUID GLASS */
.main .block-container {
    background: rgba(255,255,255,0.86);
    backdrop-filter: blur(22px) saturate(170%);
    -webkit-backdrop-filter: blur(22px) saturate(170%);
    border-radius: 26px;
    padding: 2.2rem 3rem;
    margin-top: 1.8rem;
    margin-bottom: 2.4rem;
    border: 1px solid rgba(255,255,255,0.9);
    box-shadow:
        0 18px 55px rgba(15,23,42,0.22),
        0 0 0 1px rgba(148,163,184,0.25);
}

/* SIDEBAR – GLASS ESCURO */
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.92) !important;
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border-right: 1px solid rgba(15,23,42,0.8);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-weight: 600;
}

/* TÍTULOS E TEXTOS */
h1, h2, h3, h4 {
    color: #0f172a !important;
    letter-spacing: -0.03em;
}
.stMarkdown p {
    color: #1f2933 !important;
}

/* BOTÕES – CAPSULA iOS COM AZUL #0A84FF */
.stButton > button {
    background: linear-gradient(135deg, #ffffff, #e0ebff);
    color: #0f172a !important;
    padding: 0.6rem 1.4rem;
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.7);
    box-shadow: 0 8px 24px rgba(15,23,42,0.22);
    font-weight: 600;
    font-size: 0.94rem;
    transition: all 0.18s ease-out;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #e5f0ff, #c7ddff);
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 14px 32px rgba(15,23,42,0.3);
    border-color: rgba(59,130,246,0.8);
}

/* CAMPOS – INPUT / TEXTAREA / SELECT – ESTILO CAMPO iOS */
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

/* remove bordas/caixa preta do wrapper baseweb */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* selectbox “capsula clara” */
.stSelectbox > div > div {
    background-color: #f9fafb !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: inset 0 0 0 1px rgba(148,163,184,0.35);
}

/* foco azul iOS */
.stTextInput input:focus,
.stTextArea textarea:focus,
.stSelectbox > div > div:focus-within {
    outline: none !important;
    border-color: #0a84ff !important;
    box-shadow: 0 0 0 2px rgba(10,132,255,0.35) !important;
}

/* texto sempre escuro nos campos */
input, textarea, select {
    color: #0f172a !important;
}

/* DROPDOWN DAS LISTAS (options) */
div[role="listbox"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 14px 30px rgba(15,23,42,0.35);
}
div[role="option"] {
    color: #0f172a !important;
}

/* TABELAS / DATAFRAMES – LIGHT THEME */
div[data-testid="stDataFrame"] {
    background: #ffffff !important;
    border-radius: 18px !important;
    padding: 0.45rem;
    box-shadow: 0 10px 28px rgba(15,23,42,0.25);
}

/* força claro dentro da AG-Grid */
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

/* TABS EM FORMATO PILL */
div[data-baseweb="tab-list"] {
    background: rgba(226,232,240,0.9);
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
    box-shadow: 0 4px 14px rgba(15,23,42,0.25);
}

/* ALERTAS MAIS SUAVES */
div[data-testid="stAlert"] {
    border-radius: 14px;
    background: #f9fafb !important;
}

/* radio sidebar */
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

