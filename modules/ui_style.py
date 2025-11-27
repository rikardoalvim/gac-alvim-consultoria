# ============================================
# ui_style.py
# Estilos globais – Liquid Glass (Tema Claro)
# ============================================

import streamlit as st

def inject_global_css():
    st.markdown(
        """
<style>

:root {
    --txt-main: #2f2f35;
    --txt-header: #3c3c44;
    --txt-subtle: #4a4a55;
}

/* Fundo geral */
.stApp {
    background: radial-gradient(circle at 0% 0%, #e0f7ff 0, #f6e9ff 40%, #fdf2ff 80%);
    color-scheme: light;
}

/* Container */
.block-container {
    padding-top: 1.3rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    max-width: 1400px;
}

/* Oculta sidebar */
section[data-testid="stSidebar"] {
    display: none !important;
}

/* NAV PRINCIPAL */
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

/* SUB NAV */
.glass-actions-row {
    margin-top: 0.1rem;
    margin-bottom: 0.6rem;
    display: flex;
    justify-content: flex-start;
    flex-wrap: wrap;
    gap: 0.5rem;
}

/* Botões Globais */
.stButton>button {
    border-radius: 999px !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    padding: 0.45rem 1.35rem !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    color: var(--txt-main) !important;
    background: radial-gradient(
        circle at 0 0,
        rgba(255, 255, 255, 0.96),
        rgba(228, 241, 255, 0.97)
    ) !important;
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
        rgba(224, 231, 255, 0.99)
    ) !important;
}

.stButton>button:active {
    transform: translateY(1px) scale(0.99);
}

/* Botões do MENU PRINCIPAL */
.main-nav-wrapper .stButton>button {
    font-size: 0.86rem !important;
    padding: 0.35rem 1.0rem !important;
}

/* Botão ativo */
.nav-active>button {
    border-color: rgba(244, 114, 182, 0.85) !important;
    box-shadow: 0 18px 40px rgba(236, 72, 153, 0.40) !important;
}

/* Badge de usuário */
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
}

/* Títulos */
h1, h2, h3, h4, h5 {
    color: var(--txt-header) !important;
}

/* Labels */
label {
    color: var(--txt-main) !important;
    font-weight: 600 !important;
}

/* Inputs */
textarea,
input[type="text"],
input[type="number"],
input[type="password"],
input[type="email"] {
    background: rgba(255, 255, 255, 0.98) !important;
    color: var(--txt-main) !important;
    border-radius: 18px !important;
    border: 1px solid rgba(148, 163, 184, 0.7) !important;
}

textarea:focus,
input[type="text"]:focus,
input[type="number"]:focus,
input[type="password"]:focus,
input[type="email"]:focus {
    outline: none !important;
    border-color: rgba(59, 130, 246, 0.9) !important;
    box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.5);
}

/* Tabelas */
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
    color: var(--txt-main);
    text-align: left;
}

tbody tr:nth-child(even) {
    background: rgba(255, 255, 255, 0.9);
}

tbody tr:hover {
    background: rgba(239, 246, 255, 0.98);
}

/* Selects */
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background: rgba(255, 255, 255, 0.96) !important;
    border-radius: 16px !important;
}

</style>
""",
        unsafe_allow_html=True,
    )
