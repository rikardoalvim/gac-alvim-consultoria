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

GLOBAL_CSS = """
<style>

    /* ====== RESET ====== */
    html, body, [class*="main"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Fundo líquido iOS */
    body {
        background: linear-gradient(135deg, #d9e6ff 0%, #d2f7ff 50%, #ffd4f3 100%);
        background-attachment: fixed;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ========== LIQUID GLASS BLOCKS ========== */
    .glass-block {
        backdrop-filter: blur(18px) saturate(180%);
        -webkit-backdrop-filter: blur(18px) saturate(180%);
        background: rgba(255, 255, 255, 0.38);
        border-radius: 32px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        padding: 18px 26px;
    }

    /* ========== BOTÕES iOS ========== */
    .ios-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: rgba(255,255,255,0.55);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 28px;
        padding: 12px 26px;
        font-size: 18px;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 4px 18px rgba(0,0,0,0.15);
        transition: all 0.17s ease-out;
        cursor: pointer;
    }

    .ios-btn:hover {
        transform: translateY(-2px) scale(1.03);
        background: rgba(255,255,255,0.72);
        box-shadow: 0 6px 20px rgba(0,0,0,0.20);
    }

    /* ========== MENU SUPERIOR (TABS) ========== */

    /* Container */
    div[role="tablist"] {
        background: rgba(255,255,255,0.22) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 50px !important;
        padding: 10px 14px !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        margin-bottom: 25px !important;
        overflow-x: auto;
        white-space: nowrap;
    }

    /* Cada aba */
    button[role="tab"] {
        margin-right: 10px !important;
        border-radius: 30px !important;
        padding: 12px 28px !important;
        background: rgba(255,255,255,0.35) !important;
        backdrop-filter: blur(12px) !important;
        font-size: 17px !important;
        transition: all .25s ease;
        border: 1px solid rgba(255,255,255,0.45) !important;
    }

    /* Aba ativa */
    button[role="tab"][aria-selected="true"] {
        background: white !important;
        color: #222 !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.14);
        border: 1px solid rgba(255,255,255,0.8) !important;
        transform: translateY(-2px);
    }

    /* ===== Bounce Animation iOS ===== */

    @keyframes iosTabBounce {
        0%   { transform: translateY(0) scale(1); }
        40%  { transform: translateY(-4px) scale(1.05); }
        100% { transform: translateY(-2px) scale(1); }
    }

    button[role="tab"][aria-selected="true"] {
        animation: iosTabBounce 0.22s ease-out;
    }

    /* Esconde linha vermelha do Streamlit */
    button[role="tab"]:after {
        display: none !important;
    }

    /* ====== TABLE iOS (Dataframe) ====== */
    .stDataFrame table {
        border-radius: 22px !important;
        overflow: hidden !important;
        background: rgba(0,0,0,0.85) !important;
    }

    .stDataFrame th {
        background: rgba(255,255,255,0.12) !important;
        color: #fff !important;
        font-weight: 600 !important;
        padding: 14px !important;
    }

    .stDataFrame td {
        background: rgba(0,0,0,0.55) !important;
        color: #fff !important;
        padding: 12px !important;
    }

    .stDataFrame tbody tr:hover td {
        background: rgba(255,255,255,0.12) !important;
    }

</style>
"""


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

