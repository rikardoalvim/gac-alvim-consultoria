from datetime import datetime
import unicodedata
import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from .database import (
    listar_clientes,
    listar_vagas,
    inserir_vaga,
    atualizar_vaga,
    listar_candidatos,
    listar_vinculos_vaga,
    atualizar_vinculos_vaga,
)


# ================================
# CSS extra para selects glass
# ================================
SELECT_CSS = """
<style>
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background: radial-gradient(circle at 10% 20%, rgba(255,255,255,0.90) 0%, rgba(248,250,252,0.80) 40%, rgba(241,245,249,0.80) 100%) !important;
    border-radius: 999px !important;
    box-shadow: 0 18px 45px rgba(15,23,42,0.25) !important;
    border: 1px solid rgba(148,163,184,0.4) !important;
    backdrop-filter: blur(18px) saturate(130%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(130%) !important;
}
.stSelectbox div[data-baseweb="select"] span,
.stMultiSelect div[data-baseweb="select"] span {
    color: #0f172a !important;
    font-weight: 500 !important;
}
.stSelectbox div[data-baseweb="select"] span[data-baseweb="typo-label"],
.stMultiSelect div[data-baseweb="select"] span[data-baseweb="typo-label"] {
    color: rgba(15,23,42,0.65) !important;
}
.stSelectbox div[data-baseweb="select"] div[role="listbox"],
.stMultiSelect div[data-baseweb="select"] div[role="listbox"] {
    background: radial-gradient(circle at 0% 0%, rgba(15,23,42,0.98) 0%, rgba(30,64,175,0.92) 35%, rgba(59,130,246,0.90) 100%) !important;
    color: #f9fafb !important;
    border-radius: 24px !important;
    box-shadow: 0 25px 60px rgba(15,23,42,0.55) !important;
    border: 1px solid rgba(148,163,184,0.65) !important;
    backdrop-filter: blur(22px) saturate(140%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(140%) !important;
}
.stSelectbox div[data-baseweb="select"] div[role="option"],
.stMultiSelect div[data-baseweb="select"] div[role="option"] {
    color: #e5e7eb !important;
}
.stSelectbox div[data-baseweb="select"] div[role="option"][aria-selected="true"],
.stSelectbox div[data-baseweb="select"] div[role="option"]:hover,
.stMultiSelect div[data-baseweb="select"] div[role="option"][aria-selected="true"],
.stMultiSelect div[data-baseweb="select"] div[role="option"]:hover {
    background: linear-gradient(120deg, rgba(248,250,252,0.18), rgba(248,250,252,0.05)) !important;
    color: #f9fafb !important;
}
.stMultiSelect div[data-baseweb="tag"] {
    background: rgba(15,23,42,0.06) !important;
    border-radius: 999px !important;
    border: 1px solid rgba(148,163,184,0.45) !important;
}
</style>
"""


def limpar_texto(texto: str) -> str:
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
    js = f"""
        <script>
            navigator.clipboard.writeText({json.dumps(texto)});
        </script>
    """
    components.html(js, height=0)


def render_tabela_html(df, columns, headers):
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    html = ["<table>"]
    html.append("<thead><tr>")
    for h in headers:
        html.append(f"<th>{h}</th>")
    html.append("</tr></thead><tbody>")

    for _, row in df[columns].iterrows():
        html.append("<tr>")
        for col in columns:
            html.append(f"<td>{row[col]}</td>")
        html.append("</tr>")

    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)


def run():
    st.header("🧩 Gestão de Vagas")

    st.markdown(SELECT_CSS, unsafe_allow_html=True)

    if "vagas_modo" not in st.session_state:
        st.session_state["vagas_modo"] = "Listar"

    st.markdown("<div class='top-actions'>", unsafe_allow_html=True)
    colA, colB, colC, colD, colE = st.columns(5)

    with colA:
        if st.button("📋 Listar vagas", use_container_width=True, key="btn_vagas_listar"):
            st.session_state["vagas_modo"] = "Listar"
    with colB:
        if st.button("➕ Nova vaga", use_container_width=True, key="btn_vagas_nova"):
            st.session_state["vagas_modo"] = "Inserir"
    with colC:
        if st.button("✏️ Editar vagas", use_container_width=True, key="btn_vagas_editar"):
            st.session_state["vagas_modo"] = "Editar"
    with colD:
        if st.button("📝 Texto LinkedIn/Whats", use_container_width=True, key="btn_vagas_texto"):
            st.session_state["vagas_modo"] = "Texto"
    with colE:
        if st.button("🔗 Vincular candidatos", use_container_width=True, key="btn_vagas_vinculo"):
            st.session_state["vagas_modo"] = "Vinculo"

    st.markdown("</div>", unsafe_allow_html=True)

    modo = st.session_state["vagas_modo"]
    st.markdown(f"**Modo atual:** {modo}")
    st.markdown("---")

    # =========================
    # LISTAR
    # =========================
    if modo == "Listar":
        st.subheader("📋 Vagas cadastradas")

        dados = listar_vagas()
        if not dados:
            st.info("Nenhuma vaga cadastrada.")
            return

        df = pd.DataFrame(dados).fillna("")

        render_tabela_html(
            df,
            columns=[
                "id_vaga",
                "id_cliente",
                "nome_cliente",
                "cargo",
                "modalidade",
                "data_abertura",
                "data_fechamento",
                "status",
            ],
            headers=[
                "ID",
                "ID Cliente",
                "Cliente",
                "Cargo",
                "Modalidade",
                "Abertura",
                "Fechamento",
                "Status",
            ],
        )
        return

    # =========================
    # INSERIR
    # =========================
    if modo == "Inserir":
        st.subheader("➕ Nova vaga")

        clientes = listar_clientes()
        if not clientes:
            st.warning("Cadastre clientes antes de criar vagas.")
            return

        df_cli = pd.DataFrame(clientes).fillna("")
        opcoes_cli = {int(r["id_cliente"]): r["nome_cliente"] for _, r in df_cli.iterrows()}

        id_cliente_sel = st.selectbox(
            "Cliente:",
            list(opcoes_cli.keys()),
            format_func=lambda x: opcoes_cli[x],
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

        colb1, colb2 = st.columns(2)
        with colb1:
            if st.button("💾 Salvar vaga", use_container_width=True):
                if not cargo.strip():
                    st.error("Informe o cargo.")
                else:
                    novo_id = inserir_vaga(
                        id_cliente=id_cliente_sel,
                        cargo=cargo.strip(),
                        modalidade=modalidade,
                        data_abertura=data_abertura,
                        data_fechamento=data_fechamento,
                        status=status,
                        descricao=descricao,
                    )
                    st.success(f"Vaga cadastrada (ID {novo_id}).")
                    st.session_state["vagas_modo"] = "Listar"
                    st.experimental_rerun()
        with colb2:
            if st.button("⬅ Voltar para lista", use_container_width=True):
                st.session_state["vagas_modo"] = "Listar"
                st.experimental_rerun()
        return

    # =========================
    # EDITAR
    # =========================
    if modo == "Editar":
        st.subheader("✏️ Editar vaga")

        dados_vagas = listar_vagas()
        if not dados_vagas:
            st.info("Nenhuma vaga para editar.")
            return

        dados_cli = listar_clientes()
        if not dados_cli:
            st.warning("Não há clientes cadastrados para vincular à vaga.")
            return

        df_v = pd.DataFrame(dados_vagas).fillna("")
        df_cli = pd.DataFrame(dados_cli).fillna("")

        opcoes_vagas = {
            int(r["id_vaga"]): f"{r['id_vaga']} - {r.get('nome_cliente','')} - {r['cargo']}"
            for _, r in df_v.iterrows()
        }

        id_vaga_sel = st.selectbox(
            "Selecione a vaga para editar:",
            list(opcoes_vagas.keys()),
            format_func=lambda x: opcoes_vagas[x],
            key="vaga_edit_sel",
        )

        row = df_v[df_v["id_vaga"] == id_vaga_sel].iloc[0]

        opcoes_cli = {int(r["id_cliente"]): r["nome_cliente"] for _, r in df_cli.iterrows()}
        id_cliente_atual = int(row.get("id_cliente") or list(opcoes_cli.keys())[0])

        id_cliente_edit = st.selectbox(
            "Cliente:",
            list(opcoes_cli.keys()),
            index=list(opcoes_cli.keys()).index(id_cliente_atual)
            if id_cliente_atual in opcoes_cli
            else 0,
            format_func=lambda x: opcoes_cli[x],
            key="vaga_edit_cli_sel",
        )

        col1, col2 = st.columns(2)
        with col1:
            cargo_edit = st.text_input("Cargo da vaga", value=row["cargo"])
            modalidades_lst = ["CLT", "PJ", "Aprendiz", "Estagiário"]
            modalidade_edit = st.selectbox(
                "Modalidade",
                modalidades_lst,
                index=modalidades_lst.index(row["modalidade"])
                if row["modalidade"] in modalidades_lst
                else 0,
            )
        with col2:
            try:
                data_abertura_dt = datetime.strptime(str(row["data_abertura"]), "%Y-%m-%d").date()
            except Exception:
                data_abertura_dt = datetime.today().date()
            try:
                data_fechamento_dt = datetime.strptime(str(row["data_fechamento"]), "%Y-%m-%d").date()
            except Exception:
                data_fechamento_dt = datetime.today().date()

            data_abertura_edit = st.date_input("Abertura", value=data_abertura_dt)
            data_fechamento_edit = st.date_input("Fechamento", value=data_fechamento_dt)
            status_lst = ["Aberta", "Em andamento", "Encerrada"]
            status_edit = st.selectbox(
                "Status",
                status_lst,
                index=status_lst.index(row["status"]) if row["status"] in status_lst else 0,
            )

        descricao_edit = st.text_area("Descrição da vaga", value=row.get("descricao", ""), height=200)

        colb1, colb2 = st.columns(2)
        with colb1:
            if st.button("💾 Salvar alterações", use_container_width=True, key="btn_salvar_vaga_edit"):
                atualizar_vaga(
                    id_vaga=int(id_vaga_sel),
                    id_cliente=int(id_cliente_edit),
                    cargo=cargo_edit.strip(),
                    modalidade=modalidade_edit,
                    data_abertura=data_abertura_edit.strftime("%Y-%m-%d"),
                    data_fechamento=data_fechamento_edit.strftime("%Y-%m-%d"),
                    status=status_edit,
                    descricao=descricao_edit,
                )
                st.success("Vaga atualizada com sucesso!")
                st.session_state["vagas_modo"] = "Listar"
                st.experimental_rerun()
        with colb2:
            if st.button("⬅ Voltar para lista", use_container_width=True, key="btn_voltar_edit"):
                st.session_state["vagas_modo"] = "Listar"
                st.experimental_rerun()
        return

    # =========================
    # TEXTO (LinkedIn / Whats)
    # =========================
    if modo == "Texto":
        st.subheader("📝 Gerador de textos para divulgação")

        dados = listar_vagas()
        if not dados:
            st.info("Cadastre vagas primeiro.")
            return

        df = pd.DataFrame(dados).fillna("")
        opcoes = {
            int(r["id_vaga"]): f"{r.get('nome_cliente','')} - {r['cargo']}"
            for _, r in df.iterrows()
        }

        id_vaga = st.selectbox(
            "Selecione a vaga:",
            list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
        )

        row = df[df["id_vaga"] == id_vaga].iloc[0]
        cliente = limpar_texto(row.get("nome_cliente", ""))
        cargo = limpar_texto(row["cargo"])
        modalidade = limpar_texto(row.get("modalidade", ""))
        desc = limpar_texto(row.get("descricao", ""))

        texto_linkedin = f"""
📌 Oportunidade: **{cargo}**  
🏢 Empresa: **{cliente}**  
📍 Modalidade: *{modalidade}*  

📝 **Sobre a vaga:**  
{desc}
"""
        texto_whats = f"""
*Vaga:* {cargo}  
*Empresa:* {cliente}  
*Modalidade:* {modalidade}  

📝 *Sobre a vaga:*  
{desc}
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

    # =========================
    # VÍNCULO VAGA x CANDIDATOS
    # =========================
    if modo == "Vinculo":
        st.subheader("🔗 Vincular candidatos à vaga")

        dados_vagas = listar_vagas()
        dados_cand = listar_candidatos()

        if not dados_vagas or not dados_cand:
            st.info("Necessário ter ao menos uma vaga e um candidato.")
            return

        df_v = pd.DataFrame(dados_vagas).fillna("")
        df_c = pd.DataFrame(dados_cand).fillna("")

        opcoes_vinc = {
            int(r["id_vaga"]): f"{r['id_vaga']} - {r.get('nome_cliente','')} - {r['cargo']}"
            for _, r in df_v.iterrows()
        }

        id_vaga_vinc = st.selectbox(
            "Selecione a vaga:",
            list(opcoes_vinc.keys()),
            format_func=lambda x: opcoes_vinc[x],
        )

        vinculados = listar_vinculos_vaga(int(id_vaga_vinc))
        ids_existentes = {int(v["id_candidato"]) for v in vinculados}

        opcoes_candidatos = {
            int(r["id_candidato"]): r["nome"] for _, r in df_c.iterrows()
        }

        selecionados = st.multiselect(
            "Candidatos vinculados a esta vaga:",
            list(opcoes_candidatos.keys()),
            default=list(ids_existentes),
            format_func=lambda x: opcoes_candidatos.get(x, str(x)),
        )

        if st.button("💾 Salvar vínculos", use_container_width=True):
            ids = [int(i) for i in selecionados]
            atualizar_vinculos_vaga(int(id_vaga_vinc), ids)
            st.success("Vínculos atualizados!")
            st.experimental_rerun()

        st.markdown("### Candidatos vinculados")

        vinculados = listar_vinculos_vaga(int(id_vaga_vinc))
        if not vinculados:
            st.info("Nenhum candidato vinculado.")
        else:
            df_show = pd.DataFrame(vinculados).fillna("")
            render_tabela_html(
                df_show,
                columns=["id_candidato", "nome", "telefone", "cidade", "data_vinculo"],
                headers=["ID Cand.", "Nome", "Telefone", "Cidade", "Data vínculo"],
            )
        return
