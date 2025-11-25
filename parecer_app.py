# ================================
# GAC - Gerenciador Alvim Consultoria
# Aplicação principal com navegação glass iOS-like
# ================================

import os
import sys

import streamlit as st

# Garante que o diretório "modules" esteja no path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOD_DIR = os.path.join(BASE_DIR, "modules")
if MOD_DIR not in sys.path:
    sys.path.append(MOD_DIR)

# Importa módulos de forma segura (alguns ainda podem não existir)
from modules import auth         # obrigatório

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

# dashboard é opcional; se não existir, usamos um placeholder
try:
    from modules import dashboard
except Exception:
    dashboard = None


# --------------------------------------------------
# CONFIG GLOBAL DA PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# CSS BASE – TEMA LIQUID GLASS
# --------------------------------------------------
def inject_base_css():
    st.markdown(
        """
<style>
/* Fundo gradiente suave */
body {
  background: radial-gradient(circle at 0% 0%, #e0f7ff 0, #f5e9ff 45%, #f9f1ff 100%);
}

/* Container principal mais amplo */
.block-container {
  padding-top: 1.4rem;
  max-width: 1400px;
}

/* Esconde sidebar padrão do Streamlit */
[data-testid="stSidebar"] {
  display: none;
}

/* Barra principal de navegação (fixa no topo) */
.main-nav {
  position: sticky;
  top: 0;
  z-index: 998;
  padding: 0.6rem 1rem 0.9rem 1rem;
  margin-bottom: 0.8rem;
  border-radius: 999px;
  background: linear-gradient(120deg,
            rgba(226, 245, 255, 0.92),
            rgba(245, 235, 255, 0.9));
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.18);
  backdrop-filter: blur(26px);
  border: 1px solid rgba(255, 255, 255, 0.75);
}

/* Botões GLASS – padrão global */
.stButton>button {
  border-radius: 999px !important;
  border: 1px solid rgba(255, 255, 255, 0.85);
  background: radial-gradient(circle at 0 0,
            rgba(255, 255, 255, 0.97),
            rgba(228, 241, 255, 0.96));
  color: #111827;
  padding: 0.55rem 1.4rem;
  font-weight: 600;
  font-size: 0.94rem;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.22);
  transition:
    transform 0.12s ease-out,
    box-shadow 0.12s ease-out,
    background 0.18s ease-out,
    border-color 0.18s ease-out;
}

/* Efeito hover / active */
.stButton>button:hover {
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.26);
  border-color: rgba(244, 114, 182, 0.6);
}

.stButton>button:active {
  transform: translateY(1px) scale(0.99);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.30);
}

/* Dentro da navbar: botões um pouquinho menores */
.main-nav .stButton>button {
  font-size: 0.9rem;
  padding: 0.45rem 1.1rem;
}

/* Título das seções */
.section-title {
  font-size: 1.9rem;
  font-weight: 800;
  margin-top: 0.8rem;
  margin-bottom: 0.6rem;
  color: #0f172a;
}

/* Chip de usuário – canto inferior esquerdo */
.user-chip {
  position: fixed;
  bottom: 16px;
  left: 16px;
  z-index: 999;
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.68);
  color: #f9fafb;
  font-size: 0.8rem;
  font-weight: 500;
  backdrop-filter: blur(14px);
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.55);
}

/* Pequena legenda abaixo da navbar */
.nav-subtitle {
  margin-top: 0.2rem;
  font-size: 0.9rem;
  color: #111827;
}

/* Alinhamento de ícone + texto, opcional em títulos */
.title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# AUTH – GARANTE LOGIN
# --------------------------------------------------
def ensure_login():
    """
    Usa modules.auth.run() para login.
    Tenta descobrir o nome do usuário a partir de várias chaves
    para ser compatível com versões anteriores.
    """
    # Se já está logado, só retorna
    logged_flags = [
        st.session_state.get("auth_logged_in"),
        st.session_state.get("logged_in"),
        st.session_state.get("is_logged_in"),
    ]
    if not any(logged_flags):
        # Executa tela de login
        auth.run()
        # Se ainda não logado, para a execução aqui
        logged_flags = [
            st.session_state.get("auth_logged_in"),
            st.session_state.get("logged_in"),
            st.session_state.get("is_logged_in"),
        ]
        if not any(logged_flags):
            st.stop()

    # Nome do usuário (tenta várias chaves possíveis)
    username = (
        st.session_state.get("auth_username")
        or st.session_state.get("usuario_logado")
        or st.session_state.get("usuario")
        or st.session_state.get("user")
        or "Usuário"
    )
    return username


# --------------------------------------------------
# CONFIG DE NAVEGAÇÃO
# --------------------------------------------------
NAV_CONFIG = {
    # NÍVEL 1 – PRINCIPAL
    "root": {
        "title": "Menu principal",
        "buttons": [
            {
                "id": "dash",
                "label": "Dashboard",
                "icon": "📊",
                "page": "dashboard",
            },
            {
                "id": "cadastros",
                "label": "Cadastros",
                "icon": "🏗️",
                "goto_group": "cadastros",
            },
            {
                "id": "rs",
                "label": "R&S",
                "icon": "🧩",
                "goto_group": "rs",
            },
            {
                "id": "sistemas",
                "label": "Sistemas",
                "icon": "🔐",
                "goto_group": "sistemas",
            },
            {
                "id": "fin",
                "label": "Financeiro",
                "icon": "💰",
                "page": "fin_main",
            },
        ],
    },
    # NÍVEL 2 – CADASTROS
    "cadastros": {
        "title": "Cadastros gerais",
        "back_to": "root",
        "buttons": [
            {
                "id": "cad_clientes",
                "label": "Clientes",
                "icon": "🏢",
                "page": "cad_clientes",
            },
            {
                "id": "cad_usuarios",
                "label": "Usuários",
                "icon": "👥",
                "page": "cad_usuarios",
            },
        ],
    },
    # NÍVEL 2 – RECRUTAMENTO & SELEÇÃO
    "rs": {
        "title": "Recrutamento & Seleção",
        "back_to": "root",
        "buttons": [
            {
                "id": "rs_candidatos",
                "label": "Candidatos",
                "icon": "👤",
                "page": "rs_candidatos",
            },
            {
                "id": "rs_vagas",
                "label": "Vagas",
                "icon": "🧩",
                "page": "rs_vagas",
            },
            {
                "id": "rs_pipeline",
                "label": "Pipeline",
                "icon": "📌",
                "page": "rs_pipeline",
            },
            {
                "id": "rs_parecer",
                "label": "Parecer",
                "icon": "📝",
                "page": "rs_parecer",
            },
        ],
    },
    # NÍVEL 2 – SISTEMAS
    "sistemas": {
        "title": "Sistemas",
        "back_to": "root",
        "buttons": [
            {
                "id": "sist_acessos",
                "label": "Acessos",
                "icon": "🔑",
                "page": "sist_acessos",
            },
            {
                "id": "sist_chamados",
                "label": "Chamados",
                "icon": "📨",
                "page": "sist_chamados",
            },
        ],
    },
    # NÍVEL 2 – FINANCEIRO (apenas um destino, mas mantemos padrão)
    "financeiro": {
        "title": "Financeiro",
        "back_to": "root",
        "buttons": [
            {
                "id": "fin_main",
                "label": "Financeiro",
                "icon": "💰",
                "page": "fin_main",
            }
        ],
    },
}


# --------------------------------------------------
# NAVBAR – RENDERIZAÇÃO
# --------------------------------------------------
def render_navigation():
    """
    Desenha a barra superior de navegação glass
    e devolve o 'page_id' selecionado.
    """

    # Estado padrão
    if "nav_group" not in st.session_state:
        st.session_state["nav_group"] = "root"
    if "page_id" not in st.session_state:
        st.session_state["page_id"] = "dashboard"

    nav_group = st.session_state["nav_group"]
    config = NAV_CONFIG.get(nav_group, NAV_CONFIG["root"])

    st.markdown('<div class="main-nav">', unsafe_allow_html=True)

    btns = config.get("buttons", [])
    has_back = "back_to" in config

    total_cols = len(btns) + (1 if has_back else 0)
    cols = st.columns(total_cols)

    col_idx = 0
    clicked_page = None

    # Botão VOLTAR se não estiver na root
    if has_back:
        with cols[col_idx]:
            if st.button("⬅ Voltar", key=f"nav_{nav_group}_back", use_container_width=True):
                st.session_state["nav_group"] = config["back_to"]
        col_idx += 1

    # Botões do grupo atual
    for btn in btns:
        with cols[col_idx]:
            btn_key = f"nav_{nav_group}_{btn['id']}"
            label = f"{btn['icon']} {btn['label']}"
            if st.button(label, key=btn_key, use_container_width=True):
                # Se botão leva a outro grupo
                if "goto_group" in btn:
                    st.session_state["nav_group"] = btn["goto_group"]
                # Se botão aponta para página
                if "page" in btn:
                    clicked_page = btn["page"]
                    st.session_state["page_id"] = clicked_page
        col_idx += 1

    st.markdown("</div>", unsafe_allow_html=True)

    # Se nenhum botão foi clicado, mantemos a página atual
    if clicked_page is None:
        clicked_page = st.session_state.get("page_id", "dashboard")

    # Título/legenda abaixo do menu
    subtitle = config.get("title", "")
    if subtitle:
        st.markdown(f"<div class='nav-subtitle'><strong>Módulo atual:</strong> {subtitle}</div>", unsafe_allow_html=True)

    return clicked_page


# --------------------------------------------------
# PLACEHOLDERS DE TELAS SIMPLES
# --------------------------------------------------
def render_dashboard(username: str):
    st.markdown(
        "<div class='section-title title-row'>📊 <span>Dashboard</span></div>",
        unsafe_allow_html=True,
    )
    st.write(
        """
        Aqui você pode, futuramente, colocar cards com:
        - Quantidade de vagas abertas
        - Candidatos no pipeline
        - Clientes ativos
        - Indicadores financeiros etc.
        Por enquanto, esta tela é apenas um placeholder.
        """
    )


def render_usuarios_placeholder():
    st.markdown(
        "<div class='section-title title-row'>👥 <span>Cadastro de Usuários</span></div>",
        unsafe_allow_html=True,
    )
    st.info("Módulo de usuários ainda não foi implementado. Podemos construir depois.")


def render_chamados_placeholder():
    st.markdown(
        "<div class='section-title title-row'>📨 <span>Chamados / Suporte</span></div>",
        unsafe_allow_html=True,
    )
    st.info("Módulo de chamados ainda não foi implementado. Podemos ligar aqui com um CRM / Helpdesk depois.")


# --------------------------------------------------
# ROUTER PRINCIPAL – CHAMA OS MÓDULOS
# --------------------------------------------------
def render_current_page(page_id: str, username: str):
    """
    Encaminha para o módulo correto com base no `page_id`.
    """

    # DASHBOARD
    if page_id == "dashboard":
        if dashboard is not None and hasattr(dashboard, "run"):
            dashboard.run()
        else:
            render_dashboard(username)
        return

    # CADASTROS
    if page_id == "cad_clientes":
        if clientes and hasattr(clientes, "run"):
            st.markdown(
                "<div class='section-title title-row'>🏢 <span>Cadastro de Clientes</span></div>",
                unsafe_allow_html=True,
            )
            clientes.run()
        else:
            st.error("Módulo de clientes não encontrado.")
        return

    if page_id == "cad_usuarios":
        render_usuarios_placeholder()
        return

    # R&S
    if page_id == "rs_candidatos":
        if candidatos and hasattr(candidatos, "run"):
            st.markdown(
                "<div class='section-title title-row'>👤 <span>Cadastro de Candidatos</span></div>",
                unsafe_allow_html=True,
            )
            candidatos.run()
        else:
            st.error("Módulo de candidatos não encontrado.")
        return

    if page_id == "rs_vagas":
        if vagas and hasattr(vagas, "run"):
            st.markdown(
                "<div class='section-title title-row'>🧩 <span>Gestão de Vagas</span></div>",
                unsafe_allow_html=True,
            )
            vagas.run()
        else:
            st.error("Módulo de vagas não encontrado.")
        return

    if page_id == "rs_pipeline":
        if pipeline_mod and hasattr(pipeline_mod, "run"):
            st.markdown(
                "<div class='section-title title-row'>📌 <span>Pipeline</span></div>",
                unsafe_allow_html=True,
            )
            pipeline_mod.run()
        else:
            st.error("Módulo de pipeline não encontrado.")
        return

    if page_id == "rs_parecer":
        if parecer_mod and hasattr(parecer_mod, "run"):
            # O módulo parecer_mod já contém toda a lógica do formulário
            parecer_mod.run()
        else:
            st.error("Módulo de parecer não encontrado.")
        return

    # SISTEMAS
    if page_id == "sist_acessos":
        if acessos and hasattr(acessos, "run"):
            st.markdown(
                "<div class='section-title title-row'>🔑 <span>Gerenciador de Acessos</span></div>",
                unsafe_allow_html=True,
            )
            acessos.run()
        else:
            st.error("Módulo de acessos não encontrado.")
        return

    if page_id == "sist_chamados":
        render_chamados_placeholder()
        return

    # FINANCEIRO
    if page_id == "fin_main":
        if financeiro and hasattr(financeiro, "run"):
            st.markdown(
                "<div class='section-title title-row'>💰 <span>Financeiro</span></div>",
                unsafe_allow_html=True,
            )
            financeiro.run()
        else:
            st.error("Módulo financeiro não encontrado.")
        return

    # DEFAULT – se algo inesperado chegar
    render_dashboard(username)


# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    inject_base_css()
    username = ensure_login()

    # Renderiza a navegação e descobre qual página está ativa
    page_id = render_navigation()

    # Roda a página correspondente
    render_current_page(page_id, username)

    # Exibe chip com usuário no canto inferior esquerdo
    if username:
        st.markdown(
            f"<div class='user-chip'>👤 {username}</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()





