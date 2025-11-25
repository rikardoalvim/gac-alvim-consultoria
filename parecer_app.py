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
MOD_DIR = os.path.join(BASE_DIR, "modules")
if MOD_DIR not in sys.path:
    sys.path.append(MOD_DIR)

from modules import auth  # obrigatório

# Os demais módulos podem ou não existir; tratamos com try/except
try:
    from modules import dashboard
except Exception:
    dashboard = None

try:
    from modules import clientes
except Exception:
    clientes = None

try:
    from modules import candidatos
except Exception:
    candidatos = None

try:
    from modules import vagas
except Exception:
    vagas = None

try:
    from modules import pipeline_mod
except Exception:
    pipeline_mod = None

try:
    from modules import parecer_mod
except Exception:
    parecer_mod = None

try:
    from modules import acessos
except Exception:
    acessos = None

try:
    from modules import financeiro
except Exception:
    financeiro = None


# ---------------------------------------------------------
# CONFIG GERAL STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# CSS GLOBAL – TEMA LIQUID GLASS (CLARO)
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

        /* Esconde a sidebar padrão */
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* Container principal mais amplo */
        .block-container {
            padding-top: 1.3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 1400px;
        }

        /* NAV PRINCIPAL – glass, fixo no topo */
        .main-nav-wrapper {
            position: sticky;
            top: 0.6rem;
            z-index: 999;
            padding: 0.5rem 0.75rem 0.7rem 0.75rem;
            border-radius: 999px;
            margin-bottom: 0.4rem;
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

        /* SUB NAV (abaixo da principal) */
        .glass-actions-row {
            margin-top: 0.1rem;
            margin-bottom: 0.6rem;
            display: flex;
            justify-content: flex-start;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        /* Botões GLASS – todos (principal + sub) */
        .stButton>button {
            border-radius: 999px !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            padding: 0.40rem 1.25rem !important;
            font-size: 0.90rem !important;
            font-weight: 600 !important;
            color: #111827 !important;
            background: radial-gradient(circle at 0 0,
                        rgba(255, 255, 255, 0.96),
                        rgba(228, 241, 255, 0.97)) !important;
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
                        rgba(255, 255, 255, 0.99),
                        rgba(224, 231, 255, 0.99)) !important;
        }

        .stButton>button:active {
            transform: translateY(1px) scale(0.99);
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.35) !important;
        }

        /* Botão ativo (nav) – destaque leve rosa */
        .nav-active>button {
            border-color: rgba(244, 114, 182, 0.85) !important;
            box-shadow: 0 18px 40px rgba(236, 72, 153, 0.40) !important;
        }

        /* Chip de usuário – canto inferior esquerdo */
        .user-badge {
            position: fixed;
            left: 1.2rem;
            bottom: 1.1rem;
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

        /* Títulos */
        h1, h2, h3 {
            color: #0f172a;
        }

        /* Tabelas HTML glass (usadas em listas customizadas) */
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

        /* Selectbox / MultiSelect claros */
        .stSelectbox div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"] {
            background: rgba(255, 255, 255, 0.96) !important;
            border-radius: 16px !important;
        }

        .stSelectbox div[role="listbox"],
        .stMultiSelect div[role="listbox"] {
            background: #f9fafb !important;
            color: #111827 !important;
        }

        /* Inputs arredondados */
        input, textarea {
            border-radius: 18px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
def ensure_login() -> str:
    """
    Delega pro modules.auth.run() controlar o fluxo.
    Se ele quiser segurar na tela de login, ele usa st.stop() lá.
    Aqui só pegamos o nome do usuário depois.
    """
    possible_username: Optional[str] = None
    try:
        possible_username = auth.run()
    except Exception as e:
        st.error(f"Erro no módulo de autenticação: {e}")
        st.stop()

    username = (
        possible_username
        or st.session_state.get("auth_username")
        or st.session_state.get("usuario_logado")
        or st.session_state.get("usuario")
        or st.session_state.get("user")
        or "Usuário"
    )
    return username


# ---------------------------------------------------------
# ESTADO DE NAVEGAÇÃO
# ---------------------------------------------------------
SUBMODULES = {
    "dashboard": [],
    "cadastros": [("clientes", "🏢 Clientes"), ("usuarios", "👥 Usuários")],
    "rs": [
        ("candidatos", "👤 Candidatos"),
        ("vagas", "🧩 Vagas"),
        ("pipeline", "📌 Pipeline"),
        ("parecer", "📝 Parecer"),
    ],
    "sistemas": [("acessos", "🔑 Acessos"), ("chamados", "📨 Chamados")],
    "financeiro": [("financeiro", "💰 Financeiro")],
}


def init_nav_state() -> None:
    if "main_module" not in st.session_state:
        st.session_state["main_module"] = "rs"  # começa em R&S se quiser
    if "sub_module" not in st.session_state:
        st.session_state["sub_module"] = "candidatos"


# ---------------------------------------------------------
# NAV PRINCIPAL (Dashboard, Cadastros, R&S, Sistemas, Financeiro)
# ---------------------------------------------------------
def render_main_nav() -> str:
    main = st.session_state.get("main_module", "rs")

    items = [
        ("dashboard", "📊 Dashboard"),
        ("cadastros", "📁 Cadastros"),
        ("rs", "🤝 R&S"),
        ("sistemas", "🖥️ Sistemas"),
        ("financeiro", "💰 Financeiro"),
    ]

    st.markdown('<div class="main-nav-wrapper"><div class="main-nav-row">', unsafe_allow_html=True)
    cols = st.columns(len(items))

    for col, (key, label) in zip(cols, items):
        active = (key == main)
        btn_key = f"main_{key}"
        with col:
            st.markdown(
                f'<div class="stButton{" nav-active" if active else ""}>',
                unsafe_allow_html=True,
            )
            clicked = st.button(label, key=btn_key, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if clicked:
                st.session_state["main_module"] = key
                # quando troca de módulo principal, reseta sub para o primeiro disponível
                subs = SUBMODULES.get(key, [])
                if subs:
                    st.session_state["sub_module"] = subs[0][0]
                else:
                    st.session_state["sub_module"] = ""
                main = key

    st.markdown("</div></div>", unsafe_allow_html=True)
    return main


# ---------------------------------------------------------
# SUB NAV (depende do módulo principal)
# ---------------------------------------------------------
def render_sub_nav(main_module: str) -> str:
    subs = SUBMODULES.get(main_module, [])
    cur_sub = st.session_state.get("sub_module", "")

    if subs:
        # garante que sub atual é válido
        valid_ids = [sid for sid, _ in subs]
        if cur_sub not in valid_ids:
            cur_sub = valid_ids[0]
            st.session_state["sub_module"] = cur_sub

        st.markdown('<div class="glass-actions-row">', unsafe_allow_html=True)
        cols = st.columns(len(subs) + 1)  # +1 para botão de sair

        # botões dos submódulos
        for i, (sid, label) in enumerate(subs):
            with cols[i]:
                active = (sid == cur_sub)
                btn_key = f"sub_{main_module}_{sid}"
                st.markdown(
                    f'<div class="stButton{" nav-active" if active else ""}>',
                    unsafe_allow_html=True,
                )
                clicked = st.button(label, key=btn_key, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                if clicked:
                    st.session_state["sub_module"] = sid
                    cur_sub = sid

        # botão de sair
        with cols[-1]:
            if st.button("⏏ Sair", key="btn_logout", use_container_width=True):
                keys = list(st.session_state.keys())
                for k in keys:
                    if k != "_is_running_with_streamlit":
                        del st.session_state[k]
                st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # sem submenus, mas ainda mostra botão de sair
        st.markdown('<div class="glass-actions-row">', unsafe_allow_html=True)
        col = st.columns(1)[0]
        with col:
            if st.button("⏏ Sair", key="btn_logout_nosub", use_container_width=True):
                keys = list(st.session_state.keys())
                for k in keys:
                    if k != "_is_running_with_streamlit":
                        del st.session_state[k]
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    return cur_sub


# ---------------------------------------------------------
# USER BADGE
# ---------------------------------------------------------
def render_user_badge(username: str) -> None:
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
# ROUTER – CHAMA OS MÓDULOS
# ---------------------------------------------------------
def render_dashboard(username: str) -> None:
    st.header("📊 Dashboard (placeholder)")
    st.write(
        """
        Aqui podemos colocar cards e indicadores:
        - Vagas abertas
        - Candidatos no pipeline
        - Clientes ativos
        - etc.
        """
    )


def render_usuarios_placeholder() -> None:
    st.header("👥 Cadastro de Usuários (em breve)")
    st.info("Módulo de usuários ainda não foi implementado.")


def render_chamados_placeholder() -> None:
    st.header("📨 Chamados / Suporte (em breve)")
    st.info("Módulo de chamados ainda será desenvolvido.")


def route_section(main_module: str, sub_module: str, username: str) -> None:
    if main_module == "dashboard":
        if dashboard is not None and hasattr(dashboard, "run"):
            dashboard.run()
        else:
            render_dashboard(username)
        return

    if main_module == "cadastros":
        if sub_module == "clientes" or sub_module == "":
            if clientes is not None and hasattr(clientes, "run"):
                clientes.run()
            else:
                st.error("Módulo de clientes não encontrado.")
        elif sub_module == "usuarios":
            render_usuarios_placeholder()
        return

    if main_module == "rs":
        if sub_module == "candidatos" or sub_module == "":
            if candidatos is not None and hasattr(candidatos, "run"):
                candidatos.run()
            else:
                st.error("Módulo de candidatos não encontrado.")
        elif sub_module == "vagas":
            if vagas is not None and hasattr(vagas, "run"):
                vagas.run()
            else:
                st.error("Módulo de vagas não encontrado.")
        elif sub_module == "pipeline":
            if pipeline_mod is not None and hasattr(pipeline_mod, "run"):
                pipeline_mod.run()
            else:
                st.error("Módulo de pipeline não encontrado.")
        elif sub_module == "parecer":
            if parecer_mod is not None and hasattr(parecer_mod, "run"):
                parecer_mod.run()
            else:
                st.error("Módulo de parecer não encontrado.")
        return

    if main_module == "sistemas":
        if sub_module == "acessos" or sub_module == "":
            if acessos is not None and hasattr(acessos, "run"):
                acessos.run()
            else:
                st.error("Módulo de acessos não encontrado.")
        elif sub_module == "chamados":
            render_chamados_placeholder()
        return

    if main_module == "financeiro":
        if financeiro is not None and hasattr(financeiro, "run"):
            financeiro.run()
        else:
            st.error("Módulo financeiro não encontrado.")
        return

    # fallback
    render_dashboard(username)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main() -> None:
    inject_global_css()
    username = ensure_login()
    init_nav_state()

    main_module = render_main_nav()
    sub_module = render_sub_nav(main_module)

    # Conteúdo
    route_section(main_module, sub_module, username)

    # Badge com usuário
    render_user_badge(username)


if __name__ == "__main__":
    main()






