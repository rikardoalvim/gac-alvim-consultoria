# ================================
# GAC - Gerenciador Alvim Consultoria
# Aplicação principal
# ================================

import os
import sys
import streamlit as st

from modules import (
    dashboard,          # ← ADICIONADO
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
    auth,
    usuarios,
)

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

st.set_page_config(
    page_title="GAC - Gerenciador Alvim Consultoria",
    layout="wide",
)

# =========================
# Autenticação
# =========================
if "user" not in st.session_state or st.session_state["user"] is None:
    auth.run()
    st.stop()

# Barra lateral com info do usuário logado
st.sidebar.markdown(f"👤 Usuário: **{st.session_state['user']['username']}**")
if st.sidebar.button("Sair", use_container_width=True):
    st.session_state.clear()
    st.experimental_rerun()

opcoes_menu = [
    "Dashboard",
    "Cadastros Gerais (Clientes)",
    "Recrutamento & Seleção",
    "Sistemas / Acessos",
    "Financeiro",
]

# Se for admin, mostra menu de Administração de Usuários
if st.session_state["user"].get("is_admin", False):
    opcoes_menu.append("Admin - Usuários")

modulo = st.sidebar.radio(
    "Selecione o módulo:",
    opcoes_menu
)

# DASHBOARD
if modulo == "Dashboard":
    dashboard.run()

elif modulo == "Cadastros Gerais (Clientes)":
    clientes.run()

elif modulo == "Recrutamento & Seleção":
    sub = st.tabs([
        "👤 Candidatos",
        "📂 Vagas",
        "📝 Parecer",
        "📁 Histórico",
        "📌 Pipeline",
        "📥 Importar antigos",
        "🔎 Hunting / LinkedIn",
    ])
    with sub[0]:
        candidatos.run()
    with sub[1]:
        vagas.run()
    with sub[2]:
        parecer_mod.run()
    with sub[3]:
        historico.run()
    with sub[4]:
        pipeline_mod.run()
    with sub[5]:
        importador.run()
    with sub[6]:
        hunting.run()

elif modulo == "Sistemas / Acessos":
    acessos.run()

elif modulo == "Financeiro":
    financeiro.run()

elif modulo == "Admin - Usuários":
    usuarios.run()
