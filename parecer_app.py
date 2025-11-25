# ================================
# GAC - Gerenciador Alvim Consultoria
# App principal (roteamento + layout iOS glass)
# ================================

import streamlit as st

from modules import (
    auth,
    dashboard,
    clientes,
    candidatos,
    vagas,
    pipeline_mod,
    acessos,
    financeiro,
    parecer_mod,
    historico,
    importador,
    hunting,
)

# -------------------------------------------------
# CONFIG GERAL
# -------------------------------------------------

st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
)

# -------------------------------------------------
# CSS GLOBAL – TEMA GLASS / iOS STYLE
# -------------------------------------------------

GLASS_CSS = """
<style>
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    max-width: 1400px;
}

.stApp {
    background: radial-gradient(circle at top left, #e0f7ff 0, #d8f5e9 35%, #f6e6ff 100%);
    color: #0f172a;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                 "Segoe UI", sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

h1, h2, h3, h4 {
    color: #0f172a;
    font-weight: 700;
}

.glass-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.70), rgba(255,255,255,0.35));
    border-radius: 28px;
    padding: 1.0rem 1.4rem;
    box-shadow:
        0 18px 45px rgba(15,23,42,0.22),
        0 0 0 1px rgba(255,255,255,0.60);
    backdrop-filter: blur(24px) saturate(160%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
}

div[data-testid="stButton"] > button {
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.8);
    background: radial-gradient(circle at top left,
        rgba(255,255,255,0.95),
        rgba(255,255,255,0.75)
    );
    color: #0f172a;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    font-size: 0.98rem;
    box-shadow:
        0 14px 35px rgba(15,23,42,0.20),
        0 0 0 1px rgba(255,255,255,0.90);
    backdrop-filter: blur(24px) saturate(160%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
    transition: transform 0.16s ease-out, box-shadow 0.16s ease-out,
                background 0.18s ease-out;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow:
        0 20px 40px rgba(15,23,42,0.26),
        0 0 0 1px rgba(255,255,255,0.95);
}

div[data-testid="stButton"] > button:active {
    transform: translateY(0px) scale(0.98);
    box-shadow:
        0 10px 25px rgba(15,23,42,0.18),
        0 0 0 1px rgba(255,255,255,0.85);
}

/* NAV BAR SUPERIOR */
.app-nav-bar {
    margin-bottom: 0.6rem;
}

.app-nav-inner {
    display: flex;
    gap: 0.9rem;
    justify-content: center;
    align-items: center;
}

.app-nav-inner > div[data-testid="column"] > div {
    width: 100%;
}

/* Linha com usuário, parecer, sair */
.user-row {
    margin-top: 0.1rem;
    margin-bottom: 1.0rem;
}

.user-label {
    font-size: 0.95rem;
    color: #0f172a;
    opacity: 0.85;
}

/* INPUTS: text, number, date, etc */
div[data-testid="stTextInput"] > div > div,
div[data-testid="stNumberInput"] > div > div,
div[data-testid="stDateInput"] > div > div {
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.85),
        rgba(255,255,255,0.60)
    );
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.92);
    box-shadow:
        0 10px 28px rgba(15,23,42,0.20),
        0 0 0 1px rgba(255,255,255,0.85);
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    color: #0f172a;
    font-weight: 500;
}

/* TEXT AREA */
div[data-testid="stTextArea"] textarea {
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.88),
        rgba(255,255,255,0.70)
    );
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.95);
    color: #0f172a;
    box-shadow:
        0 12px 30px rgba(15,23,42,0.20),
        0 0 0 1px rgba(255,255,255,0.88);
}

/* SELECTS / MULTISELECT */
div[data-baseweb="select"] > div {
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.9),
        rgba(255,255,255,0.70)
    );
    border-radius: 18px !important;
    border: 1px solid rgba(255,255,255,0.95);
    box-shadow:
        0 10px 26px rgba(15,23,42,0.20),
        0 0 0 1px rgba(255,255,255,0.90);
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    color: #0f172a;
}

div[data-baseweb="select"] div[role="button"] {
    color: #0f172a;
    font-weight: 500;
}

div[role="listbox"] {
    background: rgba(255,255,255,0.95) !important;
    color: #0f172a !important;
    border-radius: 22px !important;
    box-shadow:
        0 20px 45px rgba(15,23,42,0.35),
        0 0 0 1px rgba(255,255,255,0.95);
    backdrop-filter: blur(22px) saturate(170%);
    -webkit-backdrop-filter: blur(22px) saturate(170%);
}

div[role="option"][aria-selected="true"] {
    background: linear-gradient(135deg, #f97316, #fb7185) !important;
    color: #ffffff !important;
}

/* TABLES – listas de candidatos, vagas, pipeline etc. */
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.4rem;
    margin-bottom: 0.2rem;
    background: linear-gradient(
        135deg,
        rgba(15,23,42,0.87),
        rgba(15,23,42,0.92)
    );
    border-radius: 26px;
    overflow: hidden;
    box-shadow:
        0 26px 60px rgba(15,23,42,0.70),
        0 0 0 1px rgba(255,255,255,0.15);
}

th, td {
    padding: 10px 14px;
    text-align: left;
    font-size: 0.92rem;
}

thead tr {
    background: linear-gradient(135deg, #0f172a, #020617);
}

th {
    color: #e5e7eb;
    font-weight: 600;
    border-bottom: 1px solid rgba(148,163,184,0.55);
}

tbody tr:nth-child(even) {
    background-color: rgba(15,23,42,0.96);
}

tbody tr:nth-child(odd) {
    background-color: rgba(15,23,42,0.90);
}

td {
    color: #f9fafb;
    border-bottom: 1px solid rgba(30,41,59,0.85);
}

tbody tr:last-child td {
    border-bottom: none;
}

.modo-atual-label {
    font-size: 0.95rem;
    margin-top: 0.1rem;
    margin-bottom: 0.8rem;
}
</style>
"""

st.markdown(GLASS_CSS, unsafe_allow_html=True)

# -------------------------------------------------
# NAV ITEMS
# -------------------------------------------------

NAV_ITEMS = [
    {"id": "dashboard",  "label": "Dashboard",  "icon": "📊"},
    {"id": "clientes",   "label": "Clientes",   "icon": "🏙️"},
    {"id": "candidatos", "label": "Candidatos", "icon": "👤"},
    {"id": "vagas",      "label": "Vagas",      "icon": "🧩"},
    {"id": "pipeline",   "label": "Pipeline",   "icon": "📌"},
    {"id": "acessos",    "label": "Acessos",    "icon": "🔐"},
    {"id": "financeiro", "label": "Financeiro", "icon": "💰"},
]


def draw_top_nav(active_id: str) -> str:
    st.markdown('<div class="app-nav-bar"><div class="app-nav-inner">',
                unsafe_allow_html=True)

    cols = st.columns(len(NAV_ITEMS))
    new_active = active_id

    for col, item in zip(cols, NAV_ITEMS):
        label = f"{item['icon']} {item['label']}"
        key = f"nav_{item['id']}"
        with col:
            if st.button(label, use_container_width=True, key=key):
                new_active = item["id"]

    st.markdown("</div></div>", unsafe_allow_html=True)
    return new_active


def main():
    # 1) Autenticação: auth.run cuida do login na tela
    auth.run()

    # 2) Descobre usuário logado via session_state
    usuario = (
        st.session_state.get("usuario_logado")
        or st.session_state.get("user")
        or st.session_state.get("usuario")
        or st.session_state.get("login")
    )

    # Se ainda não tem usuário, significa que estamos só na tela de login
    if not usuario:
        return

    # 3) Guarda para outros módulos se quiser
    st.session_state["usuario_logado"] = usuario

    # 4) Página ativa (navegação principal)
    if "gac_active_page" not in st.session_state:
        st.session_state["gac_active_page"] = "dashboard"

    active_page = st.session_state["gac_active_page"]

    # 5) Barra superior
    active_page = draw_top_nav(active_page)
    st.session_state["gac_active_page"] = active_page

    # 6) Linha com usuário / botão Parecer / sair
    c1, c2, c3 = st.columns([1.4, 1.2, 0.8])

    with c1:
        st.markdown(
            f"""
            <div class="glass-card user-row">
                <div class="user-label">
                    <strong>Usuário:</strong> {usuario}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        if st.button("📄 Parecer", use_container_width=True, key="btn_ir_parecer"):
            st.session_state["gac_active_page"] = "parecer"
            active_page = "parecer"

    with c3:
        if st.button("⏏ Sair", use_container_width=True, key="btn_logout"):
            if hasattr(auth, "logout"):
                auth.logout()
            if "gac_active_page" in st.session_state:
                del st.session_state["gac_active_page"]
            st.rerun()

    # 7) Indicador de módulo atual
    label_map = {
        "dashboard": "Dashboard",
        "clientes": "Cadastro de Clientes",
        "candidatos": "Cadastro de Candidatos",
        "vagas": "Gestão de Vagas",
        "pipeline": "Pipeline de Candidatos",
        "acessos": "Gerenciador de Acessos",
        "financeiro": "Financeiro",
        "parecer": "Parecer de Triagem",
    }
    nome_modo = label_map.get(active_page, active_page)

    st.markdown(
        f'<div class="modo-atual-label"><strong>Módulo atual:</strong> {nome_modo}</div>',
        unsafe_allow_html=True,
    )

    # 8) Roteamento dos módulos
    if active_page == "dashboard":
        try:
            dashboard.run()
        except Exception:
            st.info("Dashboard ainda não implementado.")

    elif active_page == "clientes":
        clientes.run()

    elif active_page == "candidatos":
        candidatos.run()

    elif active_page == "vagas":
        vagas.run()

    elif active_page == "pipeline":
        pipeline_mod.run()

    elif active_page == "acessos":
        acessos.run()

    elif active_page == "financeiro":
        financeiro.run()

    elif active_page == "parecer":
        parecer_mod.run()

    else:
        st.write("Módulo não reconhecido:", active_page)


if __name__ == "__main__":
    main()



