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

# Autenticação e estilo global
from modules import auth
from modules.ui_style import inject_global_css

# Módulos opcionais (cada um precisa ter uma função run())
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

try:
    from modules import usuarios
except Exception:
    usuarios = None


# ---------------------------------------------------------
# CONFIG GERAL STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# MAPA DE MÓDULOS E SUBMÓDULOS
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

# Perfis de acesso X o que cada um enxerga
ROLE_ACCESS = {
    "MASTER": {
        "main": ["dashboard", "cadastros", "rs", "sistemas", "financeiro"],
        "subs": {
            "cadastros": ["clientes", "usuarios"],
            "rs": ["candidatos", "vagas", "pipeline", "parecer"],
            "sistemas": ["acessos", "chamados"],
            "financeiro": ["financeiro"],
        },
    },
    "OPERACOES_GERAL": {
        "main": ["dashboard", "cadastros", "rs", "sistemas", "financeiro"],
        "subs": {
            "cadastros": ["clientes"],
            "rs": ["candidatos", "vagas", "pipeline", "parecer"],
            "sistemas": ["acessos"],
            "financeiro": ["financeiro"],
        },
    },
    "OPERACOES_RS": {
        "main": ["dashboard", "rs"],
        "subs": {
            "rs": ["candidatos", "vagas", "pipeline", "parecer"],
        },
    },
    "OPERACOES_SISTEMAS": {
        "main": ["dashboard", "sistemas"],
        "subs": {
            "sistemas": ["acessos", "chamados"],
        },
    },
    "FINANCEIRO": {
        "main": ["dashboard", "financeiro"],
        "subs": {
            "financeiro": ["financeiro"],
        },
    },
}


def get_role_config() -> dict:
    """Retorna o dicionário de acesso para o perfil atual."""
    role = st.session_state.get("auth_role", "MASTER")
    return ROLE_ACCESS.get(role, ROLE_ACCESS["MASTER"])


# ---------------------------------------------------------
# LOGIN – garante que só mostra o sistema depois de logar
# ---------------------------------------------------------
def ensure_login() -> str:
    """
    Chama auth.run(), que desenha tela de login ou troca de senha.
    Se não houver usuário logado, o próprio auth.run() segura na tela.
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

    if username == "Usuário":
        # Ainda não tem login válido; auth.run() já mostrou tela de login
        st.stop()

    return username


# ---------------------------------------------------------
# ESTADO DE NAVEGAÇÃO
# ---------------------------------------------------------
def init_nav_state() -> None:
    if "main_module" not in st.session_state:
        st.session_state["main_module"] = "rs"
    if "sub_module" not in st.session_state:
        st.session_state["sub_module"] = "candidatos"


# ---------------------------------------------------------
# NAV PRINCIPAL (Dashboard, Cadastros, R&S, Sistemas, Financeiro + Sair)
# ---------------------------------------------------------
def render_main_nav() -> str:
    role_cfg = get_role_config()
    allowed_main = set(role_cfg.get("main", []))

    # Ordem fixa dos módulos
    items_all = [
        ("dashboard", "📊 Dashboard"),
        ("cadastros", "📁 Cadastros"),
        ("rs", "🤝 R&S"),
        ("sistemas", "🖥️ Sistemas"),
        ("financeiro", "💰 Financeiro"),
    ]

    # Apenas os módulos permitidos para o perfil
    visible_items = [item for item in items_all if item[0] in allowed_main]

    # Garante que o main_module atual é permitido
    main = st.session_state.get("main_module", "rs")
    if main not in allowed_main and visible_items:
        main = visible_items[0][0]
        st.session_state["main_module"] = main

    st.markdown('<div class="main-nav-wrapper"><div class="main-nav-row">', unsafe_allow_html=True)
    cols = st.columns(len(visible_items) + 1)  # +1 para o botão Sair na barra

    # Botões principais
    for idx, (key, label) in enumerate(visible_items):
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
                subs = SUBMODULES.get(key, [])
                # Ajusta sub_module pro primeiro sub permitido
                role_cfg_local = get_role_config()
                allowed_subs_map = role_cfg_local.get("subs", {})
                allowed_for_module = allowed_subs_map.get(
                    key, [sid for sid, _ in subs]
                )
                for sid, _ in subs:
                    if sid in allowed_for_module:
                        st.session_state["sub_module"] = sid
                        break
                main = key

    # Botão SAIR (sempre na barra)
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
# SUB NAV (depende do módulo principal e do perfil)
# ---------------------------------------------------------
def render_sub_nav(main_module: str) -> str:
    subs_all = SUBMODULES.get(main_module, [])
    role_cfg = get_role_config()
    allowed_subs_map = role_cfg.get("subs", {})
    allowed_for_module = set(
        allowed_subs_map.get(main_module, [sid for sid, _ in subs_all])
    )

    # Filtra submódulos pelo perfil
    subs = [(sid, label) for sid, label in subs_all if sid in allowed_for_module]

    cur_sub = st.session_state.get("sub_module", "")

    if subs:
        valid_ids = [sid for sid, _ in subs]
        if cur_sub not in valid_ids:
            cur_sub = valid_ids[0]
            st.session_state["sub_module"] = cur_sub

        st.markdown('<div class="glass-actions-row">', unsafe_allow_html=True)
        cols = st.columns(len(subs))

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
# USER BADGE (nome do usuário no canto)
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
# TELAS PLACEHOLDER
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


def render_chamados_placeholder() -> None:
    st.header("📨 Chamados / Suporte (em breve)")
    st.info("Módulo de chamados ainda será desenvolvido.")


# ---------------------------------------------------------
# ROUTER – CHAMA OS MÓDULOS CORRETOS
# ---------------------------------------------------------
def route_section(main_module: str, sub_module: str, username: str) -> None:
    # DASHBOARD
    if main_module == "dashboard":
        if dashboard is not None and hasattr(dashboard, "run"):
            dashboard.run()
        else:
            render_dashboard(username)
        return

    # CADASTROS
    if main_module == "cadastros":
        if sub_module in ("clientes", ""):
            if clientes is not None and hasattr(clientes, "run"):
                clientes.run()
            else:
                st.error("Módulo de clientes não encontrado.")
        elif sub_module == "usuarios":
            if usuarios is not None and hasattr(usuarios, "run"):
                usuarios.run()
            else:
                st.error("Módulo de usuários não encontrado.")
        return

    # R&S
    if main_module == "rs":
        if sub_module in ("candidatos", ""):
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

    # SISTEMAS
    if main_module == "sistemas":
        if sub_module in ("acessos", ""):
            if acessos is not None and hasattr(acessos, "run"):
                acessos.run()
            else:
                st.error("Módulo de acessos não encontrado.")
        elif sub_module == "chamados":
            render_chamados_placeholder()
        return

    # FINANCEIRO
    if main_module == "financeiro":
        if financeiro is not None and hasattr(financeiro, "run"):
            financeiro.run()
        else:
            st.error("Módulo financeiro não encontrado.")
        return

    # Fallback
    render_dashboard(username)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main() -> None:
    # Aplica o CSS / tema liquid glass
    inject_global_css()

    # Login (se não logar, a app é interrompida pelo auth)
    username = ensure_login()

    # Estado de navegação
    init_nav_state()

    # Navegação
    main_module = render_main_nav()
    sub_module = render_sub_nav(main_module)

    # Conteúdo principal
    route_section(main_module, sub_module, username)

    # Badge com usuário logado
    render_user_badge(username)


if __name__ == "__main__":
    main()








