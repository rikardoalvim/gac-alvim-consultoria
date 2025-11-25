# ================================
# GAC - Gerenciador Alvim Consultoria
# Aplicação principal (parecer_app.py)
# ================================

import os
import sys
from typing import Optional

import streamlit as st

# Garante que a pasta "modules" seja encontrada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from modules import (  # type: ignore
    auth,
    dashboard,
    clientes,
    candidatos,
    vagas,
    pipeline_mod,
    acessos,
    financeiro,
    parecer_mod,
)


# ---------------------------------------------------------
# CSS GLOBAL – Liquid Glass + tabelas + selectbox claro
# ---------------------------------------------------------
def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        /* Fundo geral em gradiente pastel */
        .stApp {
            background: radial-gradient(circle at 0% 0%, #e0f7ff 0, #f6e9ff 40%, #fdf2ff 80%);
            color-scheme: light;
        }

        /* Remove barra lateral padrão do Streamlit */
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* Deixa o container principal mais largo */
        .block-container {
            padding-top: 1.3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 1400px;
        }

        /* ---------------- NAV SUPERIOR (fixo) ---------------- */
        .main-nav-wrapper {
            position: sticky;
            top: 0.6rem;
            z-index: 999;
            padding: 0.5rem 0.75rem 0.7rem 0.75rem;
            border-radius: 999px;
            margin-bottom: 0.8rem;
            background: rgba(255, 255, 255, 0.18);
            backdrop-filter: blur(22px);
            -webkit-backdrop-filter: blur(22px);
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.25);
        }

        .main-nav-row {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        /* Botões em estilo “chip” (nav + ações) */
        .stButton>button {
            border-radius: 999px !important;
            border: 1px solid rgba(255, 255, 255, 0.7) !important;
            padding: 0.35rem 1.15rem !important;
            font-size: 0.90rem !important;
            font-weight: 600 !important;
            color: #111827 !important;
            background: linear-gradient(135deg,
                        rgba(255, 255, 255, 0.92),
                        rgba(240, 249, 255, 0.95)) !important;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.22) !important;
            transition: transform 0.14s ease-out,
                        box-shadow 0.14s ease-out,
                        background 0.14s ease-out,
                        border-color 0.14s ease-out;
        }

        .stButton>button:hover {
            transform: translateY(-1px) scale(1.01);
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.30) !important;
            background: linear-gradient(135deg,
                        rgba(255, 255, 255, 0.98),
                        rgba(224, 231, 255, 0.98)) !important;
        }

        /* Botão de nav ativo – leve destaque rosa */
        .nav-active>button {
            border-color: rgba(244, 114, 182, 0.8) !important;
            box-shadow: 0 18px 40px rgba(236, 72, 153, 0.40) !important;
        }

        /* Linha de ações abaixo do menu (Parecer / Sair) */
        .glass-actions-row {
            margin-top: 0.35rem;
            display: flex;
            justify-content: flex-start;
            gap: 0.75rem;
            flex-wrap: wrap;
        }

        /* Badge de usuário no canto inferior direito */
        .user-badge {
            position: fixed;
            right: 1.6rem;
            bottom: 1.2rem;
            z-index: 1000;
            padding: 0.25rem 0.85rem;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.86);
            color: #e5e7eb;
            font-size: 0.80rem;
            display: flex;
            align-items: center;
            gap: 0.35rem;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.9);
        }

        .user-badge span.emoji {
            font-size: 1rem;
        }

        /* TÍTULOS PRINCIPAIS */
        h1, h2, h3 {
            color: #0f172a;
        }

        /* ---------------- TABELAS EM ESTILO GLASS ---------------- */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.4rem;
            background: rgba(255, 255, 255, 0.92);
            border-radius: 22px;
            overflow: hidden;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
        }

        thead tr {
            background: rgba(15, 23, 42, 0.06);
        }

        th, td {
            padding: 0.55rem 0.8rem;
            font-size: 0.85rem;
            color: #111827;
            text-align: left;
        }

        tbody tr:nth-child(even) {
            background: rgba(255, 255, 255, 0.9);
        }

        tbody tr:hover {
            background: rgba(239, 246, 255, 0.98);
        }

        /* Selectbox/dropdown mais claro */
        .stSelectbox div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"] {
            background: rgba(255, 255, 255, 0.92) !important;
            border-radius: 16px !important;
        }

        .stSelectbox div[role="listbox"],
        .stMultiSelect div[role="listbox"] {
            background: #f9fafb !important;
            color: #111827 !important;
        }

        /* Inputs em geral com borda arredondada e glass */
        input, textarea {
            border-radius: 18px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# NAVEGAÇÃO PRINCIPAL
# ---------------------------------------------------------
def render_main_nav() -> str:
    """Desenha o menu superior (Dashboard, Clientes, etc.) e retorna a seção atual."""
    if "main_section" not in st.session_state:
        st.session_state["main_section"] = "candidatos"

    current = st.session_state["main_section"]

    nav_items = [
        ("dashboard", "Dashboard", "📊"),
        ("clientes", "Clientes", "🏙️"),
        ("candidatos", "Candidatos", "👤"),
        ("vagas", "Vagas", "🧩"),
        ("pipeline", "Pipeline", "📌"),
        ("acessos", "Acessos", "🔐"),
        ("financeiro", "Financeiro", "💰"),
    ]

    st.markdown('<div class="main-nav-wrapper"><div class="main-nav-row">', unsafe_allow_html=True)
    cols = st.columns(len(nav_items))

    for col, (key, label, icon) in zip(cols, nav_items):
        btn_key = f"nav_{key}"
        active_class = " nav-active" if key == current else ""
        with col:
            st.markdown(f'<div class="stButton{active_class}">', unsafe_allow_html=True)
            clicked = st.button(f"{icon} {label}", key=btn_key, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if clicked:
                st.session_state["main_section"] = key
                current = key

    st.markdown("</div></div>", unsafe_allow_html=True)
    return current


def render_actions_row() -> None:
    """Linha logo abaixo do menu com atalho para Parecer e botão de Sair."""

    st.markdown('<div class="glass-actions-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 0.5])

    with col1:
        if st.button("📄 Parecer", key="action_parecer", use_container_width=True):
            st.session_state["main_section"] = "parecer"

    with col2:
        if st.button("⏏ Sair", key="action_logout", use_container_width=True):
            # Logout bem simples: limpa sessão e recarrega
            keys = list(st.session_state.keys())
            for k in keys:
                if k != "_is_running_with_streamlit":
                    del st.session_state[k]
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_user_badge(username: str) -> None:
    """Mostra o usuário logado no canto inferior direito (badge pequeno)."""
    st.markdown(
        f"""
        <div class="user-badge">
            <span class="emoji">👤</span>
            <span>{username}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# ROTEADOR DE SEÇÕES
# ---------------------------------------------------------
def route_section(section: str) -> None:
    if section == "dashboard":
        try:
            dashboard.run()
        except Exception:
            st.info("Dashboard ainda não configurado.")
    elif section == "clientes":
        clientes.run()
    elif section == "candidatos":
        candidatos.run()
    elif section == "vagas":
        vagas.run()
    elif section == "pipeline":
        pipeline_mod.run()
    elif section == "acessos":
        acessos.run()
    elif section == "financeiro":
        financeiro.run()
    elif section == "parecer":
        parecer_mod.run()
    else:
        candidatos.run()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main() -> None:
    st.set_page_config(
        page_title="GAC - Gerenciador Alvim Consultoria",
        layout="wide",
    )

    inject_global_css()

    # Autenticação
    username: Optional[str] = auth.run()
    if not username:
        # auth.run() já mostra tela de login se não autenticado
        return

    # Navegação principal
    section = render_main_nav()
    render_actions_row()

    # Indicador textual do módulo atual (discreto)
    titulo_map = {
        "dashboard": "Dashboard Geral",
        "clientes": "Cadastro de Clientes",
        "candidatos": "Cadastro de Candidatos",
        "vagas": "Gestão de Vagas",
        "pipeline": "Pipeline de Candidatos",
        "acessos": "Gerenciador de Acessos",
        "financeiro": "Financeiro",
        "parecer": "Parecer de Triagem",
    }
    titulo_atual = titulo_map.get(section, "Módulo atual")

    st.markdown(f"**Módulo atual:** {titulo_atual}")
    st.markdown("---")

    # Conteúdo da seção
    route_section(section)

    # Badge de usuário no final da página
    render_user_badge(username)


if __name__ == "__main__":
    main()




