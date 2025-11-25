# ================================
# GAC - Gerenciador Alvim Consultoria
# Aplicação principal
# ================================

import streamlit as st

from modules import (
    auth,
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
)

# ============================================
# CSS GLOBAL - LIQUID GLASS / iOS STYLE
# ============================================

GLOBAL_CSS = '''
<style>
/* ============================================
   GLOBAL LIQUID GLASS UI - iOS STYLE
   ============================================ */

html, body, [class*="css"] {
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Background geral */
.stApp {
    background: linear-gradient(
        135deg,
        rgba(203, 235, 255, 0.9) 0%,
        rgba(222, 255, 245, 0.9) 45%,
        rgba(246, 222, 255, 0.9) 100%
    ) !important;
    background-attachment: fixed !important;
}

/* Conteudo principal em card glass */
.main .block-container {
    background: rgba(255,255,255,0.9);
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

/* Sidebar glass escura */
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.96) !important;
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border-right: 1px solid rgba(15,23,42,0.9);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-weight: 600;
}

/* Titulos */
h1, h2, h3, h4 {
    color: #0f172a !important;
    letter-spacing: -0.03em;
    text-shadow: 0 2px 4px rgba(0,0,0,0.15);
}
.stMarkdown p {
    color: #1f2933 !important;
}

/* =========================
   BOTOES GERAIS - LIQUID GLASS
   ========================= */

.stButton > button {
    background: rgba(255,255,255,0.25) !important;
    color: #111827 !important;
    padding: 12px 26px !important;
    border-radius: 28px !important;
    border: 1px solid rgba(255,255,255,0.55) !important;
    font-weight: 600 !important;
    backdrop-filter: blur(16px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
    transition: transform 0.16s ease-out, box-shadow 0.16s ease-out, background 0.16s ease-out !important;
    box-shadow:
        0 8px 24px rgba(15,23,42,0.18),
        inset 0 0 18px rgba(255,255,255,0.55);
}
.stButton > button:hover {
    transform: translateY(-2px);
    background: rgba(255,255,255,0.8) !important;
    box-shadow:
        0 12px 30px rgba(15,23,42,0.24),
        inset 0 0 22px rgba(255,255,255,0.75);
}

/* Botoes de acao do modulo (Listar / Nova / Editar etc.) */
.top-actions .stButton > button {
    padding: 0.8rem 1.9rem;
    font-size: 1.0rem;
}

/* =========================
   MENU SUPERIOR - TABS
   ========================= */

/* remove underline padrao do Streamlit */
.stTabs [data-baseweb="tab"] {
    border-bottom: none !important;
}
.stTabs [aria-selected="true"] {
    border-bottom: none !important;
}

/* container geral das tabs */
.stTabs {
    padding-top: 8px !important;
    padding-bottom: 4px !important;
}

/* barra onde ficam as tabs */
div[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.22) !important;
    border-radius: 40px !important;
    padding: 10px 20px !important;

    width: 100% !important;
    display: flex !important;
    justify-content: flex-start !important;
    gap: 0.8rem !important;

    overflow-x: auto !important;
    overflow-y: hidden !important;
    scroll-behavior: smooth !important;

    box-shadow:
        0 8px 28px rgba(15,23,42,0.25),
        inset 0 0 18px rgba(255,255,255,0.55) !important;
    backdrop-filter: blur(22px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(170%) !important;

    margin-bottom: 20px;
}

/* esconder scrollbar */
div[data-baseweb="tab-list"]::-webkit-scrollbar {
    display: none !important;
}
div[data-baseweb="tab-list"] {
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}

/* animacao leve bounce */
@keyframes iosTabBounce {
    0%   { transform: translateY(0) scale(1); }
    40%  { transform: translateY(-3px) scale(1.03); }
    100% { transform: translateY(-2px) scale(1); }
}

/* estilo das tabs (botoes) */
button[role="tab"] {
    background: rgba(255,255,255,0.43) !important;
    padding: 10px 22px !important;
    border-radius: 18px !important;

    font-weight: 600 !important;
    font-size: 0.98rem !important;

    border: 1px solid rgba(255,255,255,0.55) !important;

    color: #1f2937 !important;

    box-shadow:
        0 6px 22px rgba(0,0,0,0.12),
        inset 0 0 18px rgba(255,255,255,0.40) !important;

    transition: background 0.15s ease-in-out, color 0.15s ease-in-out, box-shadow 0.15s ease-in-out !important;
}

/* tab ativa com bounce */
button[role="tab"][aria-selected="true"] {
    background: rgba(255,255,255,0.96) !important;
    color: #000000 !important;
    box-shadow:
        0 12px 32px rgba(0,0,0,0.16),
        inset 0 0 22px rgba(255,255,255,0.70) !important;
    animation: iosTabBounce 220ms ease-out;
}

/* efeito de clique leve */
button[role="tab"]:active {
    transform: translateY(1px) scale(0.98);
}

/* remove borda superior do painel das tabs */
.stTabs [data-baseweb="tab-panel"] {
    border-top: none !important;
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

/* remove bordas baseweb internas */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* selectbox glass */
.stSelectbox > div > div {
    background-color: rgba(249,250,251,0.95) !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: inset 0 0 0 1px rgba(148,163,184,0.35),
                0 0 0 1px rgba(255,255,255,0.6);
}

/* foco azul estilo iOS */
.stTextInput input:focus,
.stTextArea textarea:focus,
.stSelectbox > div > div:focus-within {
    outline: none !important;
    border-color: #0a84ff !important;
    box-shadow:
        0 0 0 2px rgba(10,132,255,0.35) !important;
}

/* texto escuro em inputs */
input, textarea, select {
    color: #0f172a !important;
}

/* dropdown das opcoes */
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
   TABELAS HTML
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
   DATAFRAMES (st.dataframe)
   ========================= */

div[data-testid="stDataFrame"] {
    background: #ffffff !important;
    border-radius: 18px !important;
    padding: 0.45rem;
    box-shadow:
        0 10px 28px rgba(15,23,42,0.25),
        inset 0 0 18px rgba(255,255,255,0.55);
}

/* modo claro no AG-Grid */
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
div[data-testid="stDataFrame"] .ag-header-cell-label {
    color: #0f172a !important;
    font-weight: 600;
}

/* Alertas */
div[data-testid="stAlert"] {
    border-radius: 14px;
    background: #f9fafb !important;
}
</style>
'''

# ============================================================
# CONFIGURACOES GERAIS
# ============================================================

st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
)

# aplica o CSS global
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def main():
    # controle de usuario logado
    if "usuario_logado" not in st.session_state:
        st.session_state["usuario_logado"] = None

    # se nao estiver logado, chama tela de autenticacao
    if st.session_state["usuario_logado"] is None:
        auth.run()
        return

    # sidebar - info usuario e selecao de modulo
    with st.sidebar:
        st.markdown(f"👤 **Usuário:** {st.session_state['usuario_logado']}")
        st.markdown("---")
        modulo = st.radio(
            "Selecione o módulo:",
            [
                "Dashboard",
                "Cadastros Gerais (Clientes)",
                "Recrutamento & Seleção",
                "Sistemas / Acessos",
                "Financeiro",
            ],
        )
        if st.button("Sair"):
            st.session_state["usuario_logado"] = None
            st.rerun()

    # =========================
    # ROTEAMENTO DOS MODULOS
    # =========================
    if modulo == "Dashboard":
        dashboard.run()

    elif modulo == "Cadastros Gerais (Clientes)":
        clientes.run()

    elif modulo == "Recrutamento & Seleção":
        tabs = st.tabs([
            "👤 Candidatos",
            "📂 Vagas",
            "📝 Parecer",
            "📁 Histórico",
            "📌 Pipeline",
            "📥 Importar antigos",
            "🔎 Hunting / LinkedIn",
        ])
        with tabs[0]:
            candidatos.run()
        with tabs[1]:
            vagas.run()
        with tabs[2]:
            parecer_mod.run()
        with tabs[3]:
            historico.run()
        with tabs[4]:
            pipeline_mod.run()
        with tabs[5]:
            importador.run()
        with tabs[6]:
            hunting.run()

    elif modulo == "Sistemas / Acessos":
        acessos.run()

    elif modulo == "Financeiro":
        financeiro.run()


if __name__ == "__main__":
    main()

