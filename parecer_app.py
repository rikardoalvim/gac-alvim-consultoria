# ================================
# GAC - Gerenciador Alvim Consultoria
# Aplicação principal (parecer_app.py) - versão banco de dados
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

# Banco de dados
from modules.database import init_db, autenticar

# CSS global / tema
from modules.ui_style import inject_global_css

# Módulos de funcionalidade (alguns podem ainda não existir)
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
    from modules import status_pipeline
except Exception:
    status_pipeline = None

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
# LOGIN SIMPLES (direto no banco)
# ---------------------------------------------------------
def ensure_login() -> str:
    """
    Login simples:
      - Usa tabela 'usuarios' do banco
      - Usuário seed: rikardo / 2025 (perfil MASTER)
      - Não obriga troca de senha
    """
    # Já logado?
    if st.session_state.get("logged_user"):
        return st.session_state["logged_user"]

    st.markdown("### 🔑 Login — GAC Alvim Consultoria")

    col1, col2 = st.columns([1, 1])

    with col1:
        username = st.text_input("Usuário", key="login_user")
        password = st.text_input("Senha", type="password", key="login_pass")

        if st.button("Entrar", key="btn_login"):
            user = autenticar(username, password)
            if not user:
                st.error("Usuário ou senha inválidos.")
            else:
                st.session_state["logged_user"] = user.get("nome") or user.get("username") or "Usuário"
                st.session_state["logged_username"] = user.get("username")
                st.session_state["logged_perfil"] = user.get("perfil")
                st.rerun()   # ⬅⬅ AQUI, em vez de st.experimental_rerun()

    with col2:
        st.markdown(
            """
            #### Acesso padrão inicial
            - **Usuário:** `rikardo`  
            - **Senha:** `2025`  

            Depois você poderá criar outros usuários e perfis.
            """
        )

    st.stop()



# ---------------------------------------------------------
# ESTADO DE NAVEGAÇÃO
# ---------------------------------------------------------
SUBMODULES = {
    "dashboard": [],
    "cadastros": [
        ("clientes", "🏢 Clientes"),
        ("usuarios", "👥 Usuários"),
        ("status_pipeline", "📌 Status Pipeline"),
    ],
    "rs": [
        ("candidatos", "👤 Candidatos"),
        ("vagas", "🧩 Vagas"),
        ("pipeline", "📊 Pipeline"),
        ("parecer", "📝 Parecer"),
    ],
    "sistemas": [("acessos", "🔑 Acessos"), ("chamados", "📨 Chamados")],
    "financeiro": [("financeiro", "💰 Financeiro")],
}


def init_nav_state() -> None:
    if "main_module" not in st.session_state:
        st.session_state["main_module"] = "rs"
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

    st.markdown(
        """
        <div class="main-nav-wrapper">
            <div class="main-nav-row">
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(items) + 1)  # +1 para botão Sair

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
                subs = SUBMODULES.get(key, [])
                st.session_state["sub_module"] = subs[0][0] if subs else ""
                main = key

    # Botão SAIR
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
    st.header("📊 Dashboard")
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
    st.header("👥 Cadastro de Usuários")
    if usuarios is not None and hasattr(usuarios, "run"):
        usuarios.run()
    else:
        st.info("Módulo de usuários ainda não foi implementado ou está indisponível.")


def render_status_pipeline_placeholder() -> None:
    st.header("📌 Status do Pipeline")
    if status_pipeline is not None and hasattr(status_pipeline, "run"):
        status_pipeline.run()
    else:
        st.info("Módulo de status do pipeline ainda não foi implementado ou está indisponível.")


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
        if sub_module in ("clientes", ""):
            if clientes is not None and hasattr(clientes, "run"):
                clientes.run()
            else:
                st.error("Módulo de clientes não encontrado.")
        elif sub_module == "usuarios":
            render_usuarios_placeholder()
        elif sub_module == "status_pipeline":
            render_status_pipeline_placeholder()
        return

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

    if main_module == "sistemas":
        if sub_module in ("acessos", ""):
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
    # 1) Garante que o banco exista e tenha as tabelas
    init_db()

    # 2) Aplica o CSS global (tema liquid glass)
    inject_global_css()

    # 3) Login
    username = ensure_login()

    # 4) Navegação
    init_nav_state()
    main_module = render_main_nav()
    sub_module = render_sub_nav(main_module)

    # 5) Conteúdo conforme seção
    route_section(main_module, sub_module, username)

    # 6) Badge com usuário logado
    render_user_badge(username)


if __name__ == "__main__":
    main()
