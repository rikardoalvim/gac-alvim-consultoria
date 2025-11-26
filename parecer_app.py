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
from modules.ui_style import inject_global_css  # <<< CSS agora vem daqui

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
# NAV PRINCIPAL (Dashboard, Cadastros, R&S, Sistemas, Financeiro + Sair)
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
    cols = st.columns(len(items) + 1)  # +1 para o botão Sair fixo à direita

    # Botões principais
    for idx, (key, label) in enumerate(items):
        active = (key == main)
        btn_key = f"main_{key}"
        with cols[idx]:
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

    # Botão SAIR fixo na barra (sempre visível no topo)
    with cols[-1]:
        if st.button("⏏ Sair", key="btn_logout_main", use_container_width=True):
            keys = list(st.session_state.keys())
            for k in keys:
                if k != "_is_running_with_streamlit":
                    del st.session_state[k]
            st.experimental_rerun()

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
        cols = st.columns(len(subs))

        # botões dos submódulos (todos com mesmo tamanho)
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

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        cur_sub = ""

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








