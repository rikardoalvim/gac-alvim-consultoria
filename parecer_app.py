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
    usuarios,
)

# ============================================
# CSS GLOBAL – LIQUID GLASS / iOS STYLE
# ============================================

GLOBAL_CSS = '''
<style>
/* ============================================
   GLOBAL LIQUID GLASS UI - iOS STYLE
   ============================================ */

html, body, [class*="css"] {
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Fundo geral da aplicação */
.stApp {
    background: linear-gradient(
        135deg,
        rgba(203, 235, 255, 0.9) 0%,
        rgba(222, 255, 245, 0.9) 45%,
        rgba(246, 222, 255, 0.9) 100%
    ) !important;
    background-attachment: fixed !important;
}

/* Conteúdo principal em card glass */
.main .block-container {
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(22px) saturate(170%);
    -webkit-backdrop-filter: blur(22px) saturate(170%);
    border-radius: 26px;
    padding: 2.2rem 3rem;
    box-shadow:
        0 24px 50px rgba(15,23,42,0.25),
        inset 0 0 36px rgba(255,255,255,0.75);
    border: 1px solid rgba(255,255,255,0.6);
}

/* remove margens exageradas */
.block-container {
    padding-top: 1.5rem !important;
}

/* ============================================
   LOGIN PAGE
   ============================================ */

.login-card {
    max-width: 420px;
    margin: 4rem auto 2rem auto;
    padding: 2.5rem 2.8rem;
    border-radius: 28px;
    background: radial-gradient(circle at top left, rgba(255,255,255,0.95), rgba(255,255,255,0.85));
    backdrop-filter: blur(26px) saturate(180%);
    -webkit-backdrop-filter: blur(26px) saturate(180%);
    box-shadow:
        0 28px 60px rgba(15,23,42,0.35),
        inset 0 0 32px rgba(255,255,255,0.85);
    border: 1px solid rgba(255,255,255,0.75);
}

/* título principal do login */
.login-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
    background: linear-gradient(120deg, #0f172a, #1f2937);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}

/* subtítulo do login */
.login-subtitle {
    font-size: 0.95rem;
    color: #4b5563;
    text-align: center;
    margin-bottom: 1.8rem;
}

/* Powered by */
.login-powered {
    font-size: 0.85rem;
    color: #6b7280;
    text-align: center;
    margin-top: 1.8rem;
    font-style: italic;
}

/* pequeno raiozinho */
.login-powered span.icon {
    font-size: 1rem;
    margin-right: 0.35rem;
}

/* Campos do login */
.login-card input {
    border-radius: 999px !important;
    padding: 0.55rem 1.0rem !important;
    border: 1px solid rgba(148,163,184,0.8) !important;
    background: rgba(255,255,255,0.95) !important;
    color: #0f172a !important;
}

/* botão login */
.login-card .stButton > button {
    width: 100%;
    border-radius: 999px !important;
    padding: 0.55rem 1.0rem !important;
    background: linear-gradient(135deg,#0f172a,#1e293b) !important;
    color: #f9fafb !important;
    border: none !important;
    box-shadow:
        0 16px 30px rgba(15,23,42,0.45),
        inset 0 0 12px rgba(255,255,255,0.45) !important;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
}
.login-card .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow:
        0 20px 38px rgba(15,23,42,0.58),
        inset 0 0 18px rgba(255,255,255,0.60) !important;
}

/* ============================================
   MENU SUPERIOR – TAGS / TABS PRINCIPAIS
   ============================================ */

.top-nav-bar {
    margin: -0.3rem 0 1.6rem 0;
}

.top-nav-bar .menu-wrap {
    background: rgba(255,255,255,0.35);
    border-radius: 16px;
    padding: 0.4rem 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    box-shadow:
        0 16px 38px rgba(15,23,42,0.25),
        inset 0 0 18px rgba(255,255,255,0.65) !important;
    backdrop-filter: blur(22px) saturate(150%);
    -webkit-backdrop-filter: blur(22px) saturate(150%);
    border: 1px solid rgba(255,255,255,0.75);
}

/* grupo dos botões de módulo */
.top-nav-bar .menu-buttons {
    display: flex;
    gap: 0.55rem;
    overflow-x: auto;
    padding-bottom: 0.15rem;
}

/* grupo usuário + logout */
.top-nav-bar .menu-user {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: #111827;
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.75);
}

/* badge do usuário logado */
.top-nav-bar .menu-user span.user-label {
    font-weight: 600;
}

/* ============================================
   BOTÕES GLASS – MENU SUPERIOR
   ============================================ */

.menu-chip button {
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,0.8) !important;
    padding: 0.35rem 0.95rem !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #0f172a !important;
    background: radial-gradient(circle at top, rgba(255,255,255,0.95), rgba(241,245,249,0.85)) !important;
    box-shadow:
        0 10px 20px rgba(15,23,42,0.20),
        inset 0 0 18px rgba(255,255,255,0.85) !important;
    backdrop-filter: blur(18px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(170%) !important;
    transition: transform 0.12s ease-out, box-shadow 0.12s ease-out, background 0.12s ease-out !important;
}

/* estado "ativo" – quando esse módulo está selecionado */
.menu-chip button.selected {
    background: radial-gradient(circle at top, #0f172a, #111827) !important;
    color: #e5e7eb !important;
    box-shadow:
        0 14px 28px rgba(15,23,42,0.40),
        inset 0 0 18px rgba(255,255,255,0.20) !important;
    border-color: rgba(15,23,42,0.9) !important;
}

/* animação de bounce sutil */
.menu-chip button:active {
    transform: translateY(1px) scale(0.98) !important;
    box-shadow:
        0 8px 14px rgba(15,23,42,0.35),
        inset 0 0 14px rgba(255,255,255,0.55) !important;
}

/* Usuário / logout botão minimalista */
.menu-user .stButton > button {
    border-radius: 999px !important;
    padding: 0.2rem 0.8rem !important;
    font-size: 0.78rem !important;
    background: rgba(248,250,252,0.9) !important;
    border: 1px solid rgba(148,163,184,0.7) !important;
    box-shadow: none !important;
    color: #0f172a !important;
}
.menu-user .stButton > button:hover {
    background: rgba(241,245,249,1) !important;
}

/* =========================
   BOTÕES GERAIS – LIQUID GLASS
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

/* Botões de ação do módulo (Listar / Nova / Editar etc.) */
.top-actions .stButton > button {
    padding: 0.8rem 1.9rem;
    font-size: 1.0rem;
}

/* ============================================
   CAMPOS DE FORMULÁRIO – INPUTS / TEXTAREAS
   ============================================ */

input, textarea, select {
    color: #0f172a !important;
}

/* dropdown das opções */
div[role="listbox"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 14px 30px rgba(15,23,42,0.35);
}
div[role="option"] {
    color: #0f172a !important;
}

/* Alertas */
div[data-testid="stAlert"] {
    border-radius: 14px;
    background: #f9fafb !important;
}

/* ============================================
   Tabelas HTML simples (listas) – candidatos, vagas, etc.
   Aplica globalmente, pra garantir.
   ============================================ */

table {
    width: 100%;
    border-collapse: collapse;
    background-color: #ffffff !important;
    border-radius: 18px;
    overflow: hidden;
    box-shadow:
        0 10px 28px rgba(15,23,42,0.18),
        inset 0 0 16px rgba(255,255,255,0.75);
    margin-top: 0.8rem;
}

th, td {
    padding: 0.55rem 0.85rem;
    text-align: left;
}

thead {
    background: #f1f5f9;
}
thead th {
    font-size: 0.80rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6b7280;
}

tbody tr:nth-child(even) {
    background: #f9fafb;
}

tbody tr:hover {
    background: #eff6ff;
}

/* linhas mais "macias" */
td {
    border-bottom: 1px solid #e5e7eb;
    font-size: 0.95rem;
}

/* cabeçalho em negrito */
th {
    font-weight: 700;
}

/* última linha sem borda embaixo */
tr:last-child td {
    border-bottom: none;
}

/* ============================================
   DataFrames / DataEditors – estilo glass unificado
   ============================================ */

div[data-testid="stDataFrame"],
div[data-testid="stDataEditor"] {
    background: rgba(255,255,255,0.92) !important;
    backdrop-filter: blur(20px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(170%) !important;
    border-radius: 18px !important;
    box-shadow:
        0 18px 40px rgba(15,23,42,0.20),
        inset 0 0 14px rgba(255,255,255,0.65) !important;
    padding: 4px 6px !important;
}

/* remove barras muito escuras */
div[data-testid="stDataFrame"] table,
div[data-testid="stDataEditor"] table {
    background: transparent !important;
}

/* células internas */
div[data-testid="stDataFrame"] table td,
div[data-testid="stDataFrame"] table th,
div[data-testid="stDataEditor"] table td,
div[data-testid="stDataEditor"] table th {
    background-color: transparent !important;
    color: #0f172a !important;
    border-bottom: 1px solid rgba(148,163,184,0.45) !important;
}


</style>
'''

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
)

# aplica o CSS global
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def main():
    # controle de usuário logado
    if "usuario_logado" not in st.session_state:
        st.session_state["usuario_logado"] = None

    # se não estiver logado, mostra apenas tela de login
    if not st.session_state["usuario_logado"]:
        auth.run()
        return

    # se estiver logado, mostra o app principal
    usuario = st.session_state["usuario_logado"]

    # =========================
    # BARRA SUPERIOR CUSTOM
    # =========================
    with st.container():
        st.markdown('<div class="top-nav-bar">', unsafe_allow_html=True)
        col_menu, = st.columns(1)
        with col_menu:
            st.markdown('<div class="menu-wrap">', unsafe_allow_html=True)

            # lado esquerdo – botões de módulos
            st.markdown('<div class="menu-buttons">', unsafe_allow_html=True)

            # definindo módulo atual na sessão
            if "modulo_atual" not in st.session_state:
                st.session_state["modulo_atual"] = "Dashboard"

            def menu_button(label, modulo_nome, icon):
                selected = (st.session_state["modulo_atual"] == modulo_nome)
                key = f"menu_{modulo_nome.replace(' ', '_').lower()}"
                btn = st.button(
                    f"{icon} {label}",
                    key=key,
                    help=modulo_nome,
                    use_container_width=False,
                )
                # aplicar classe de selecionado via HTML wrapper
                class_attr = "menu-chip"
                if selected:
                    st.markdown(
                        f"""
                        <script>
                        const btn = window.parent.document.querySelector('button[kind="{key}"]')
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )
                if btn:
                    st.session_state["modulo_atual"] = modulo_nome

            # Botões principais – em linha
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                with st.container():
                    st.markdown('<div class="menu-chip">', unsafe_allow_html=True)
                    if st.button("📊 Dashboard", key="mod_dashboard"):
                        st.session_state["modulo_atual"] = "Dashboard"
                    st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                with st.container():
                    st.markdown('<div class="menu-chip">', unsafe_allow_html=True)
                    if st.button("🏢 Clientes", key="mod_clientes"):
                        st.session_state["modulo_atual"] = "Clientes"
                    st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                with st.container():
                    st.markdown('<div class="menu-chip">', unsafe_allow_html=True)
                    if st.button("👤 Candidatos", key="mod_candidatos"):
                        st.session_state["modulo_atual"] = "Candidatos"
                    st.markdown('</div>', unsafe_allow_html=True)
            with col4:
                with st.container():
                    st.markdown('<div class="menu-chip">', unsafe_allow_html=True)
                    if st.button("🧩 Vagas", key="mod_vagas"):
                        st.session_state["modulo_atual"] = "Vagas"
                    st.markdown('</div>', unsafe_allow_html=True)
            with col5:
                with st.container():
                    st.markdown('<div class="menu-chip">', unsafe_allow_html=True)
                    if st.button("📌 Pipeline", key="mod_pipeline"):
                        st.session_state["modulo_atual"] = "Pipeline"
                    st.markdown('</div>', unsafe_allow_html=True)
            with col6:
                with st.container():
                    st.markdown('<div class="menu-chip">', unsafe_allow_html=True)
                    if st.button("🔐 Acessos", key="mod_acessos"):
                        st.session_state["modulo_atual"] = "Acessos"
                    st.markdown('</div>', unsafe_allow_html=True)
            with col7:
                with st.container():
                    st.markdown('<div class="menu-chip">', unsafe_allow_html=True)
                    if st.button("💰 Financeiro", key="mod_financeiro"):
                        st.session_state["modulo_atual"] = "Financeiro"
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # fecha .menu-buttons

            # lado direito – usuário logado + logout
            st.markdown('<div class="menu-user">', unsafe_allow_html=True)
            st.markdown(
                f'<span class="user-label">👤 {usuario}</span>',
                unsafe_allow_html=True,
            )
            col_u1, col_u2 = st.columns([1,1])
            with col_u1:
                if st.button("📄 Parecer", key="mod_parecer_top"):
                    st.session_state["modulo_atual"] = "Parecer"
            with col_u2:
                if st.button("🚪 Sair", key="logout_button"):
                    st.session_state["usuario_logado"] = None
                    st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)  # fecha .menu-user

            st.markdown('</div>', unsafe_allow_html=True)  # fecha .menu-wrap

        st.markdown('</div>', unsafe_allow_html=True)  # fecha .top-nav-bar

    # =========================
    # NAVEGAÇÃO ENTRE MÓDULOS
    # =========================

    modulo = st.session_state["modulo_atual"]

    if modulo == "Dashboard":
        dashboard.run()

    elif modulo == "Clientes":
        clientes.run()

    elif modulo == "Candidatos":
        candidatos.run()

    elif modulo == "Vagas":
        vagas.run()

    elif modulo == "Pipeline":
        pipeline_mod.run()

    elif modulo == "Acessos":
        acessos.run()

    elif modulo == "Financeiro":
        financeiro.run()

    elif modulo == "Parecer":
        parecer_mod.run()

    elif modulo == "Usuários":
        usuarios.run()

    else:
        st.write("Módulo não reconhecido.")


if __name__ == "__main__":
    main()




