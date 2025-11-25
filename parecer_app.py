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

/* =========================
   FUNDO GERAL LIQUID GLASS
   ========================= */
html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 0% 0%, #9bb5ff 0, transparent 45%),
        radial-gradient(circle at 100% 0%, #fbc2ff 0, transparent 40%),
        radial-gradient(circle at 50% 100%, #a5f3fc 0, #e5f0ff 55%);
}

/* container principal glass */
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

/* sidebar glass escura */
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

/* =========================
   TIPOGRAFIA
   ========================= */
h1, h2, h3, h4 {
    color: #0f172a !important;
    letter-spacing: -0.03em;
}
.stMarkdown p {
    color: #1f2933 !important;
}

/* =========================
   BOTÕES GERAIS – LIQUID GLASS
   ========================= */
.stButton > button {
    background: radial-gradient(circle at 0% 0%, rgba(255,255,255,0.85), rgba(224,235,255,0.8));
    color: #0f172a !important;
    padding: 0.6rem 1.4rem;
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.7);
    box-shadow:
        0 8px 24px rgba(15,23,42,0.22),
        inset 0 0 22px rgba(255,255,255,0.6);
    font-weight: 600;
    font-size: 0.94rem;
    transition: all 0.18s ease-out;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}
.stButton > button:hover {
    background: radial-gradient(circle at 0% 0%, rgba(255,255,255,0.95), rgba(199,221,255,0.95));
    transform: translateY(-2px) scale(1.01);
    box-shadow:
        0 14px 32px rgba(15,23,42,0.30),
        inset 0 0 30px rgba(255,255,255,0.9);
    border-color: rgba(59,130,246,0.9);
}

/* BOTÕES DE AÇÃO SUPERIORES (Listar / Nova / Editar etc.) */
.top-actions .stButton > button {
    padding: 0.8rem 1.9rem;
    font-size: 1.0rem;
}

/* =========================
   MENU SUPERIOR – TABS
   ========================= */
/* container da lista de tabs */
div[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.22) !important;
    border-radius: 999px;
    padding: 6px;
    margin-bottom: 1.2rem;
    box-shadow:
        0 8px 28px rgba(15,23,42,0.25),
        inset 0 0 18px rgba(255,255,255,0.55);
    backdrop-filter: blur(22px) saturate(170%);
    -webkit-backdrop-filter: blur(22px) saturate(170%);
}

/* tirar barra de destaque padrão (vermelha) */
div[data-baseweb="tab-highlight"] {
    background: transparent !important;
}

/* cada tab como cápsula glass */
button[role="tab"] {
    border-radius: 999px !important;
    padding: 0.55rem 1.4rem !important;
    margin: 0 0.25rem !important;
    border: 1px solid transparent !important;
    background: rgba(255,255,255,0.08) !important;
    color: #1f2933 !important;
    font-weight: 500 !important;
    font-size: 0.96rem !important;
    box-shadow: none !important;
    transition: all 0.16s ease-out !important;
}

/* tab selecionada – botão igual iOS */
button[role="tab"][aria-selected="true"] {
    background: radial-gradient(circle at 0% 0%, rgba(255,255,255,0.98), rgba(232,241,255,0.95)) !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    border-color: rgba(148,163,184,0.9) !important;
    box-shadow:
        0 8px 24px rgba(15,23,42,0.26),
        inset 0 0 26px rgba(255,255,255,0.9) !important;
    transform: translateY(-1px);
}

/* =========================
   INPUTS / TEXTAREAS / SELECTS
   ========================= */
.stTextInput input,
.stTextArea textarea {
    background-color: rgba(249,250,251,0.9) !important;
    color: #0f172a !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: inset 0 0 0 1px rgba(148,163,184,0.35),
                0 0 0 1px rgba(255,255,255,0.8);
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

/* remove borda baseweb */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* selectbox cápsula */
.stSelectbox > div > div {
    background-color: rgba(249,250,251,0.95) !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: inset 0 0 0 1px rgba(148,163,184,0.35),
                0 0 0 1px rgba(255,255,255,0.6);
}

/* foco azul iOS */
.stTextInput input:focus,
.stTextArea textarea:focus,
.stSelectbox > div > div:focus-within {
    outline: none !important;
    border-color: #0a84ff !important;
    box-shadow:
        0 0 0 2px rgba(10,132,255,0.35) !important;
}

/* texto sempre escuro nos campos */
input, textarea, select {
    color: #0f172a !important;
}

/* dropdown das opções */
div[role="listbox"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 14px 30px rgba(15,23,42,0.35);
}
div[role="option"] {
    color: #0f172a !important;
}

/* =========================
   TABELAS / LISTAS HTML
   ========================= */
table {
    width: 100%;
    border-collapse: collapse;
    background: #ffffffee !important;
    border-radius: 18px;
    overflow: hidden;
    box-shadow:
        0 10px 28px rgba(15,23,42,0.22),
        inset 0 0 18px rgba(255,255,255,0.55);
}
table th, table td {
    padding: 10px 14px;
    font-size: 0.90rem;
    color: #0f172a !important;
    border-bottom: 1px solid #e5e7eb;
}
table th {
    background: #f1f5f9;
    font-weight: 700;
}
table tr:last-child td {
    border-bottom: none;
}

/* =========================
   DATAFRAMES (caso ainda use)
   ========================= */
div[data-testid="stDataFrame"] {
    background: #ffffff !important;
    border-radius: 18px !important;
    padding: 0.45rem;
    box-shadow:
        0 10px 28px rgba(15,23,42,0.25),
        inset 0 0 18px rgba(255,255,255,0.55);
}

/* força modo claro no AG-Grid */
div[data-testid="stDataFrame"] .ag-root-wrapper,
div[data-testid="stDataFrame"] .ag-root,
div[data-testid="stDataFrame"] .ag-header,
div[data-testid="stDataFrame"] .ag-row,
div[data-testid="stDataFrame"] .ag-cell,
div[data-testid="stDataFrame"] .ag-header-cell {
    background-color: #f9fafb !important;
    color: #0f172a !important;
    border-color: #e5e7eb !important;
}

/* header mais forte */
div[data-testid="stDataFrame"] .ag-header-cell-label {
    color: #0f172a !important;
    font-weight: 600;
}

/* =========================
   ALERTAS
   ========================= */
div[data-testid="stAlert"] {
    border-radius: 14px;
    background: #f9fafb !important;
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

