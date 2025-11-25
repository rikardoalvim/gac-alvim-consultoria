from datetime import datetime
import unicodedata
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from .core import (
    carregar_clientes,
    carregar_vagas,
    registrar_vaga,
    LOG_VAGAS,
    carregar_candidatos,
    carregar_vaga_candidatos,
    salvar_vaga_candidatos,
)

# =============================================
# FUNÇÕES UTILITÁRIAS
# =============================================

def limpar_texto(texto: str) -> str:
    """Remove caracteres invisíveis e normaliza texto para evitar erros no LinkedIn/Whats."""
    if not texto:
        return ""

    texto = unicodedata.normalize("NFKC", str(texto))
    resultado = []

    for ch in texto:
        if ch in "\n\r\t":
            resultado.append(ch)
            continue

        cat = unicodedata.category(ch)
        if cat and cat.startswith("C"):
            continue

        if ord(ch) < 128:
            resultado.append(ch)
            continue

        if ch in "áàãâéêíóôõúçÁÀÃÂÉÊÍÓÔÕÚÇ":
            resultado.append(ch)
            continue

        decomp = unicodedata.normalize("NFKD", ch)
        base = "".join(c for c in decomp if ord(c) < 128 and c.isprintable())
        resultado.append(base)

    return "".join(resultado).strip()


def copiar_para_clipboard(texto: str):
    """Copia texto via JavaScript para clipboard."""
    js = f"""
        <script>
            navigator.clipboard.writeText({json.dumps(texto)});
        </script>
    """
    components.html(js, height=0)


# =============================================
# MÓDULO PRINCIPAL
# =============================================

def run():
    st.header("🧩 Gestão de Vagas")

    # CONTROLE DE MODO
    if "vagas_modo" not in st.session_state:
        st.session_state["vagas_modo"] = "Listar"

    colA, colB, colC, colD, colE = st.columns(5)

    with colA:
        if st.button("📋 Listar vagas", use_container_width=True):
            st.session_state["vagas_modo"] = "Listar"

    with colB:
        if st.button("➕ Nova vaga", use_container_width=True):
            st.session_state["vagas_modo"] = "Inserir"

    with colC:
        if st.button("✏️ Editar vagas", use_container_width=True):
            st.session_state["vagas_modo"] = "Editar"

    with colD:
        if st.button("📝 Texto LinkedIn/Whats", use_container_width=True):
            st.session_state["vagas_modo"] = "Texto"

    with colE:
        if st.button("🔗 Vincular candidatos", use_container_width=True):
            st.session_state["vagas_modo"] = "Vinculo"

    modo = st.session_state["vagas_modo"]

    st.markdown(f"**Modo atual:** {modo}")
    st.markdown("---")

    # =========================================================
    # MODO 1 – LISTAR
    # =========================================================
    if modo == "Listar":
        st.subheader("📋 Vagas cadastradas")

        df = carregar_vagas()
        if df.empty:
            st.info("Nenhuma vaga cadastrada.")
            return

        df_view = df.sort_values("id_vaga")
        st.dataframe(df_view, use_container_width=True)

        return

    # =========================================================
    # MODO 2 – INSERIR (NOVA VAGA)
    # =========================================================
    if modo == "Inserir":
        st.subheader("➕ Nova vaga")

        df_cli = carregar_clientes()
        if df_cli.empty:
            st.warning("Cadastre clientes antes de criar vagas.")
            return

        opcoes_cli = {int(r["id_cliente"]): r["nome_cliente"] for _, r in df_cli.iterrows()}
        id_cliente_sel = st.selectbox(
            "Cliente:", list(opcoes_cli.keys()), format_func=lambda x: opcoes_cli[x]
        )
        nome_cliente_sel = opcoes_cli[id_cliente_sel]

        col1, col2 = st.columns(2)

        with col1:
            cargo = st.text_input("Cargo da vaga")
            modalidade = st.selectbox("Modalidade", ["CLT", "PJ", "Aprendiz", "Estagiário"])

        with col2:
            data_abertura = st.date_input("Abertura", datetime.today()).strftime("%Y-%m-%d")
            data_fechamento = st.date_input("Fechamento", datetime.today()).strftime("%Y-%m-%d")
            status = st.selectbox("Status", ["Aberta", "Em andamento", "Encerrada"])

        descricao = st.text_area("Descrição da vaga", height=200)

        colb1, colb2 = st.columns([1, 1])
        with colb1:
            if st.button("💾 Salvar vaga", use_container_width=True):
                if not cargo.strip():
                    st.error("Informe o cargo.")
                else:
                    novo_id = registrar_vaga(
                        id_cliente=str(id_cliente_sel),
                        nome_cliente=nome_cliente_sel,
                        cargo=cargo.strip(),
                        modalidade=modalidade,
                        data_abertura=data_abertura,
                        data_fechamento=data_fechamento,
                        status=status,
                        descricao_vaga=descricao,
                    )
                    st.success(f"Vaga cadastrada (ID {novo_id}).")
                    st.session_state["vagas_modo"] = "Listar"
                    st.rerun()
        with colb2:
            if st.button("⬅ Voltar para lista", use_container_width=True):
                st.session_state["vagas_modo"] = "Listar"
                st.rerun()

        return

    # =========================================================
    # MODO 3 – EDITAR (FORMULÁRIO, NÃO GRID)
    # =========================================================
    if modo == "Editar":
        st.subheader("✏️ Editar vaga")

        df_vagas = carregar_vagas()
        if df_vagas.empty:
            st.info("Nenhuma vaga para editar.")
            return

        df_cli = carregar_clientes()
        if df_cli.empty:
            st.warning("Não há clientes cadastrados para vincular à vaga.")
            return

        opcoes_vagas = {
            int(r["id_vaga"]): f"{r['id_vaga']} - {r['nome_cliente']} - {r['cargo']}"
            for _, r in df_vagas.iterrows()
        }

        id_vaga_sel = st.selectbox(
            "Selecione a vaga para editar:",
            list(opcoes_vagas.keys()),
            format_func=lambda x: opcoes_vagas[x],
            key="vaga_edit_sel",
        )

        row = df_vagas[df_vagas["id_vaga"] == str(id_vaga_sel)].iloc[0]

        # Cliente da vaga
        opcoes_cli = {int(r["id_cliente"]): r["nome_cliente"] for _, r in df_cli.iterrows()}
        id_cliente_atual = int(row["id_cliente"]) if str(row["id_cliente"]).isdigit() else list(opcoes_cli.keys())[0]

        id_cliente_edit = st.selectbox(
            "Cliente:",
            list(opcoes_cli.keys()),
            index=list(opcoes_cli.keys()).index(id_cliente_atual) if id_cliente_atual in opcoes_cli else 0,
            format_func=lambda x: opcoes_cli[x],
            key="vaga_edit_cli_sel",
        )
        nome_cliente_edit = opcoes_cli[id_cliente_edit]

        # Formulário com dados da vaga
        col1, col2 = st.columns(2)

        with col1:
            cargo_edit = st.text_input("Cargo da vaga", value=row["cargo"])
            modalidade_edit = st.selectbox(
                "Modalidade",
                ["CLT", "PJ", "Aprendiz", "Estagiário"],
                index=["CLT", "PJ", "Aprendiz", "Estagiário"].index(row["modalidade"]) 
                    if row["modalidade"] in ["CLT", "PJ", "Aprendiz", "Estagiário"] else 0,
            )

        with col2:
            try:
                data_abertura_dt = datetime.strptime(row["data_abertura"], "%Y-%m-%d").date()
            except Exception:
                data_abertura_dt = datetime.today().date()

            try:
                data_fechamento_dt = datetime.strptime(row["data_fechamento"], "%Y-%m-%d").date()
            except Exception:
                data_fechamento_dt = datetime.today().date()

            data_abertura_edit = st.date_input("Abertura", value=data_abertura_dt)
            data_fechamento_edit = st.date_input("Fechamento", value=data_fechamento_dt)
            status_edit = st.selectbox(
                "Status",
                ["Aberta", "Em andamento", "Encerrada"],
                index=["Aberta", "Em andamento", "Encerrada"].index(row["status"])
                    if row["status"] in ["Aberta", "Em andamento", "Encerrada"] else 0,
            )

        descricao_edit = st.text_area("Descrição da vaga", value=row["descricao_vaga"], height=200)

        colb1, colb2 = st.columns([1, 1])

        with colb1:
            if st.button("💾 Salvar alterações", use_container_width=True, key="btn_salvar_vaga_edit"):
                df_total = carregar_vagas()
                mask = df_total["id_vaga"] == str(id_vaga_sel)
                if not mask.any():
                    st.error("Vaga não encontrada para atualização.")
                else:
                    df_total.loc[mask, "id_cliente"] = str(id_cliente_edit)
                    df_total.loc[mask, "nome_cliente"] = nome_cliente_edit
                    df_total.loc[mask, "cargo"] = cargo_edit.strip()
                    df_total.loc[mask, "modalidade"] = modalidade_edit
                    df_total.loc[mask, "data_abertura"] = data_abertura_edit.strftime("%Y-%m-%d")
                    df_total.loc[mask, "data_fechamento"] = data_fechamento_edit.strftime("%Y-%m-%d")
                    df_total.loc[mask, "status"] = status_edit
                    df_total.loc[mask, "descricao_vaga"] = descricao_edit

                    df_total.to_csv(LOG_VAGAS, sep=";", index=False, encoding="utf-8")
                    st.success("Vaga atualizada com sucesso!")
                    st.session_state["vagas_modo"] = "Listar"
                    st.rerun()

        with colb2:
            if st.button("⬅ Voltar para lista", use_container_width=True, key="btn_voltar_edit"):
                st.session_state["vagas_modo"] = "Listar"
                st.rerun()

        return

    # =========================================================
    # MODO 4 – TEXTO LINKEDIN / WHATSAPP
    # =========================================================
    if modo == "Texto":
        st.subheader("📝 Gerador de textos para divulgação")

        df = carregar_vagas()
        if df.empty:
            st.info("Cadastre vagas primeiro.")
            return

        opcoes = {int(r["id_vaga"]): f"{r['nome_cliente']} - {r['cargo']}" for _, r in df.iterrows()}
        id_vaga = st.selectbox(
            "Selecione a vaga:", list(opcoes.keys()), format_func=lambda x: opcoes[x]
        )

        row = df[df["id_vaga"] == str(id_vaga)].iloc[0]

        cliente = limpar_texto(row["nome_cliente"])
        cargo = limpar_texto(row["cargo"])
        modalidade = limpar_texto(row["modalidade"])
        desc = limpar_texto(row["descricao_vaga"])

        texto_linkedin = f"""
📌 Oportunidade: **{cargo}**  
🏢 Empresa: **{cliente}**  
📍 Modalidade: *{modalidade}*  

📝 **Sobre a vaga:**  
{desc}

👉 Interessados(as), enviem o currículo atualizado ou chamem no WhatsApp.  
"""

        texto_whats = f"""
*Vaga:* {cargo}  
*Empresa:* {cliente}  
*Modalidade:* {modalidade}  

📝 *Sobre a vaga:*  
{desc}

Se tiver interesse, envie seu *currículo atualizado* ou fale comigo aqui! 🙂  
"""

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📋 Copiar texto LinkedIn", use_container_width=True):
                copiar_para_clipboard(texto_linkedin)
                st.success("Texto para LinkedIn copiado para a área de transferência!")

        with col2:
            if st.button("📋 Copiar texto WhatsApp", use_container_width=True):
                copiar_para_clipboard(texto_whats)
                st.success("Texto para WhatsApp copiado para a área de transferência!")

        with st.expander("Visualizar textos gerados"):
            st.markdown("**LinkedIn:**")
            st.code(texto_linkedin)
            st.markdown("**WhatsApp:**")
            st.code(texto_whats)

        return

    # =========================================================
    # MODO 5 – VÍNCULO VAGA x CANDIDATO
    # =========================================================
    if modo == "Vinculo":
        st.subheader("🔗 Vincular candidatos à vaga")

        df_vagas = carregar_vagas()
        df_cand = carregar_candidatos()

        if df_vagas.empty or df_cand.empty:
            st.info("Necessário ter ao menos uma vaga e um candidato.")
            return

        opcoes_vinc = {
            int(r["id_vaga"]): f"{r['id_vaga']} - {r['nome_cliente']} - {r['cargo']}"
            for _, r in df_vagas.iterrows()
        }

        id_vaga_vinc = st.selectbox(
            "Selecione a vaga:", list(opcoes_vinc.keys()), format_func=lambda x: opcoes_vinc[x]
        )

        df_vinc = carregar_vaga_candidatos()
        if not df_vinc.empty:
            vinculados = df_vinc[df_vinc["id_vaga"] == str(id_vaga_vinc)]
        else:
            vinculados = pd.DataFrame(columns=["id_vaga", "id_candidato", "data_vinculo", "observacao"])

        ids_existentes = set(vinculados["id_candidato"].tolist())
        opcoes_candidatos = {str(r["id_candidato"]): r["nome"] for _, r in df_cand.iterrows()}

        selecionados = st.multiselect(
            "Candidatos vinculados:",
            list(opcoes_candidatos.keys()),
            default=list(ids_existentes),
            format_func=lambda x: opcoes_candidatos.get(x, x),
        )

        if st.button("💾 Salvar vínculos", use_container_width=True):
            df_todos = carregar_vaga_candidatos()
            if not df_todos.empty:
                df_todos = df_todos[df_todos["id_vaga"] != str(id_vaga_vinc)]

            novos = []
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for idc in selecionados:
                novos.append({
                    "id_vaga": str(id_vaga_vinc),
                    "id_candidato": str(idc),
                    "data_vinculo": agora,
                    "observacao": "",
                })

            df_novos = pd.DataFrame(novos)
            df_final = pd.concat([df_todos, df_novos], ignore_index=True) if not df_todos.empty else df_novos
            salvar_vaga_candidatos(df_final)
            st.success("Vínculos atualizados!")
            st.rerun()

        st.markdown("### Candidatos vinculados")
        df_vinc_atual = carregar_vaga_candidatos()
        df_vinc_atual = df_vinc_atual[df_vinc_atual["id_vaga"] == str(id_vaga_vinc)]

        if df_vinc_atual.empty:
            st.info("Nenhum candidato vinculado.")
        else:
            df_show = df_vinc_atual.merge(
                df_cand[["id_candidato", "nome", "telefone", "cidade"]],
                on="id_candidato",
                how="left",
            )
            st.dataframe(df_show, use_container_width=True)

        return

