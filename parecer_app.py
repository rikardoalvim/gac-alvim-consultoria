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
# CSS GLOBAL – ESTILO iOS / GLASSMORPHISM
# ============================================================

GLOBAL_CSS = """
<style>

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #e3e9f8 0%, #f5f7fa 50%, #e1e7f0 100%) !important;
}

/* REMOVE FUNDO PRETO DO STREAMLIT */
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}

/* CONTAINER PRINCIPAL EM GLASS */
.main .block-container {
    background: rgba(255,255,255,0.50);
    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
    border-radius: 24px;
    padding: 2rem 3rem;
    margin-top: 2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.08);
}

/* SIDEBAR GLASS REAL */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.25) !important;
    backdrop-filter: blur(22px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(160%) !important;
    border-right: 1px solid rgba(255,255,255,0.45);
}

/* BOTÕES iOS */
.stButton > button {
    background: rgba(255,255,255,0.35);
    backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 0.6rem 1.2rem;
    color: #1e293b;
    border: 1px solid rgba(255,255,255,0.45);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.25s ease;
    font-weight: 600;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.55);
    transform: scale(1.03) translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

/* INPUTS GLASS */
input, textarea, select, div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.45) !important;
    backdrop-filter: blur(14px) saturate(180%) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.55) !important;
}

/* DATAFRAME EM CARD GLASS */
div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.45) !important;
    backdrop-filter: blur(12px);
    border-radius: 18px !important;
    padding: 0.5rem;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}

/* TABS iOS */
div[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.25);
    border-radius: 999px;
    padding: 5px;
    backdrop-filter: blur(10px);
}
button[role="tab"] {
    border-radius: 999px !important;
    padding: 6px 18px !important;
    color: #475569 !important;
}
button[role="tab"][aria-selected="true"] {
    background: rgba(255,255,255,0.55) !important;
    color: #1e293b !important;
    font-weight: 700 !important;
    border: 1px solid rgba(255,255,255,0.65);
    box-shadow: 0 4px 10px rgba(0,0,0,0.10);
}

/* ALERTAS */
div[data-testid="stAlert"] {
    background: rgba(255,255,255,0.55) !important;
    backdrop-filter: blur(10px);
    border-radius: 16px;
}

/* TÍTULOS */
h1, h2, h3, h4 {
    color: #1e293b;
    letter-spacing: -0.3px;
}

/* LABELS */
label, span, p, div {
    color: #334155 !important;
}

</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ============================================================
# AUTENTICAÇÃO
# ============================================================

# Se não estiver logado OU precisa trocar senha, fica no fluxo do auth
if (
    "user" not in st.session_state
    or st.session_state["user"] is None
    or st.session_state.get("forcar_troca_senha", False)
):
    auth.run()
    st.stop()

# Info do usuário logado no sidebar
st.sidebar.markdown(
    f"👤 Usuário: **{st.session_state['user']['username']}**"
)
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


elif modulo == "Financeiro":
    financeiro.run()

elif modulo == "Admin - Usuários":
    usuarios.run()
