# modules/ui_style.py

import streamlit as st


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

        /* Botões GLASS – base (submenus + botões normais) */
        .stButton>button {
            border-radius: 999px !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            padding: 0.45rem 1.35rem !important;
            font-size: 0.92rem !important;
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

        /* Botões do MENU PRINCIPAL um pouco menores */
        .main-nav-wrapper .stButton>button {
            font-size: 0.86rem !important;
            padding: 0.35rem 1.0rem !important;
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

        /* Inputs / textareas claros (principalmente para o Parecer) */
        textarea,
        input[type="text"],
        input[type="number"],
        input[type="password"],
        input[type="email"] {
            background: rgba(255, 255, 255, 0.98) !important;
            color: #0f172a !important;
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

        /* Labels mais visíveis */
        label {
            color: #111827 !important;
            font-weight: 600 !important;
        }

        /* ===============================
           AJUSTE DE COR DOS TEXTOS (CINZA ELEGANTE)
        ================================ */

        /* Texto geral da app */
        html, body, [class*="css"] {
            color: #111827;
            font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        }

        /* Títulos (reforço) */
        h1, h2, h3, h4, h5, h6 {
            color: #111827 !important;
        }

        /* Labels e textos padrão (inputs, selects, etc.) */
        .stMarkdown, .stText, .stRadio label, .stCheckbox label,
        .stSelectbox label, .stMultiSelect label, .stDateInput label,
        .stFileUploader label, label {
            color: #111827 !important;
        }

        /* Placeholders um pouco mais escuros (cinza médio) */
        ::placeholder {
            color: #6B7280 !important;
            opacity: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
