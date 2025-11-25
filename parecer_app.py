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
/* Fundo geral estilo iOS */
body {
    background: radial-gradient(circle at top left, #e0e7ff 0, #f1f5f9 40%, #e2e8f0 100%) !important;
}

/* Container principal com "respiro" */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
}

/* Sidebar com leve vidro fosco */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(15,23,42,0.9));
    color: #e5e7eb;
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Título do sidebar */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #e5e7eb !important;
}

/* Botões – estilo pill, glassy e animados */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    color: #ffffff !important;
    padding: 0.45rem 1.1rem;
    border-radius: 999px;
    border: none;
    font-weight: 600;
    font-size: 0.9rem;
    box-shadow: 0 8px 20px rgba(79,70,229,0.35);
    transition: all 0.18s ease-out;
}

.stButton > button:hover {
    transform: translateY(-1px) scale(1.01);
    box-shadow: 0 12px 26px rgba(79,70,229,0.45);
    background: linear-gradient(135deg, #4338ca, #4f46e5);
}

/* Inputs de texto / número / selects – borda iOS */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 1px solid rgba(148,163,184,0.7) !important;
    background-color: rgba(255,255,255,0.85) !important;
    backdrop-filter: blur(12px);
}

/* Text area */
textarea {
    border-radius: 12px !important;
    border: 1px solid rgba(148,163,184,0.7) !important;
    background-color: rgba(255,255,255,0.9) !important;
    backdrop-filter: blur(12px);
}

/* Dataframe dentro de um "card" */
div[data-testid="stDataFrame"] {
    background-color: rgba(255,255,255,0.9) !important;
    border-radius: 16px;
    padding: 0.35rem;
    box-shadow: 0 8px 24px rgba(15,23,42,0.08);
}

/* Títulos */
h1, h2, h3 {
    color: #0f172a;
}

/* Tabs – estilo pill */
div[data-baseweb="tab-list"] {
    background-color: rgba(15,23,42,0.03);
    border-radius: 999px;
    padding: 4px;
}
button[role="tab"] {
    border-radius: 999px !important;
    padding: 0.35rem 0.9rem !important;
}
button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: #ffffff !important;
}

/* Mensagens (success / error / warning) levemente arredondadas */
div[data-testid="stAlert"] {
    border-radius: 14px;
}

/* Ajusta radio do sidebar */
section[data-testid="stSidebar"] .stRadio > label {
    font-weight: 600;
}

/* Pequeno efeito nos títulos principais */
header h1 {
    letter-spacing: 0.02em;
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
