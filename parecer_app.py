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
# CSS GLOBAL – ESTILO iOS 18 / GLASSMORPHISM
# ============================================================

GLOBAL_CSS = """
<style>

/* Fundo geral com gradiente estilo iOS */
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #e3e9f8 0%, #f5f7fa 50%, #e1e7f0 100%) !important;
}

/* Remove qualquer fundo sólido do container root */
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}

/* Container principal como card de vidro */
.main .block-container {
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-radius: 24px;
    padding: 2rem 3rem;
    margin-top: 1.5rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 40px rgba(15,23,42,0.18);
}

/* SIDEBAR em glass */
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.35) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border-right: 1px solid rgba(148,163,184,0.4);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* RADIO da sidebar mais bonitinho */
section[data-testid="stSidebar"] .stRadio label {
    font-weight: 600;
}

/* BOTÕES estilo iOS, com animação */
.stButton > button {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 0.55rem 1.25rem;
    color: #111827 !important;
    border: 1px solid rgba(209,213,219,0.8);
    box-shadow: 0 4px 14px rgba(15,23,42,0.18);
    transition: all 0.22s ease-out;
    font-weight: 600;
    font-size: 0.92rem;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.9);
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 10px 26px rgba(15,23,42,0.24);
}

/* INPUTS / SELECTS – caixas claras com texto escuro (iOS) */
input, textarea, select {
    color: #0f172a !important;
}

/* wrappers dos inputs do Streamlit (BaseWeb) */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background: rgba(255,255,255,0.85) !important;
    backdrop-filter: blur(14px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(14px) saturate(180%) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(148,163,184,0.8) !important;
    box-shadow: 0 2px 7px rgba(15,23,42,0.05);
}

/* textarea nativo */
textarea {
    background: rgba(255,255,255,0.9) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(148,163,184,0.8) !important;
}

/* Dropdown das listas (selectbox options) */
div[role="listbox"] {
    background: rgba(255,255,255,0.96) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(148,163,184,0.7) !important;
    box-shadow: 0 8px 22px rgba(15,23,42,0.20);
}
div[role="option"] {
    color: #0f172a !important;
}

/* DataFrame: card claro, texto escuro */
div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.9) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 18px !important;
    padding: 0.45rem;
    box-shadow: 0 8px 24px rgba(15,23,42,0.18);
}

/* Tenta clarear as células internas do grid */
div[data-testid="stDataFrame"] * {
    color: #0f172a !important;
}
div[data-testid="stDataFrame"] .ag-root-wrapper,
div[data-testid="stDataFrame"] .ag-header,
div[data-testid="stDataFrame"] .ag-row {
    background-color: rgba(248,250,252,0.98) !important;
}

/* Títulos */
h1, h2, h3 {
    color: #0f172a;
    letter-spacing: -0.03em;
}

/* Tabs estilo iOS (pill) */
div[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 999px;
    padding: 4px;
}
button[role="tab"] {
    border-radius: 999px !important;
    padding: 0.35rem 0.95rem !important;
    color: #475569 !important;
}
button[role="tab"][aria-selected="true"] {
    background: rgba(255,255,255,0.98) !important;
    color: #111827 !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(15,23,42,0.18);
}

/* Alertas arredondados em vidro */
div[data-testid="stAlert"] {
    border-radius: 16px;
    background: rgba(255,255,255,0.9) !important;
    backdrop-filter: blur(10px);
}

/* Pequeno ajuste nos parágrafos */
.stMarkdown p {
    color: #1f2933;
}

</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ============================================================
# AUTENTICAÇÃO
# ============================================================

# Se não estiver logado ou precisa trocar senha, fica no fluxo do auth
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

# Admin vê o módulo de usuários
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

