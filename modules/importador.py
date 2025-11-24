import os
import streamlit as st

from .core import (
    BASE_DIR,
    parse_parecer_pdf_arquivo,
    carregar_pareceres_log,
    registrar_parecer_log,
    get_or_create_candidato_por_nome_localidade,
    inferir_nome_data_de_arquivo,
)


def run():
    st.header("📥 Importar Pareceres Antigos")

    st.write(
        "Use esta aba para importar PDFs de pareceres antigos, ler os dados da primeira página "
        "e registrar no histórico, criando também o cadastro do candidato, se necessário."
    )

    pasta_import = st.text_input(
        "Pasta onde estão os pareceres antigos (PDF)",
        value=BASE_DIR,
    )

    if "pdfs_para_importar" not in st.session_state:
        st.session_state["pdfs_para_importar"] = []

    if st.button("🔍 Listar PDFs para importação"):
        if not os.path.isdir(pasta_import):
            st.error("Pasta inválida.")
            st.session_state["pdfs_para_importar"] = []
        else:
            df_atual = carregar_pareceres_log()
            caminhos_existentes = set(df_atual["caminho_arquivo"].tolist()) if not df_atual.empty else set()

            pdfs = []
            for f in os.listdir(pasta_import):
                if f.lower().endswith(".pdf"):
                    caminho = os.path.join(pasta_import, f)
                    if caminho not in caminhos_existentes:
                        pdfs.append(caminho)

            st.session_state["pdfs_para_importar"] = pdfs

    pdfs_encontrados = st.session_state.get("pdfs_para_importar", [])

    if not pdfs_encontrados:
        st.info("Nenhum PDF novo para importar (ou todos já estão no histórico).")
        return

    st.write(f"Foram encontrados {len(pdfs_encontrados)} PDFs:")
    for c in pdfs_encontrados:
        st.markdown(f"- `{c}`")

    if st.button("📥 Importar PDFs listados"):
        try:
            for caminho in pdfs_encontrados:
                parsed = parse_parecer_pdf_arquivo(caminho)
                nome = parsed["nome"]
                cliente = parsed["cliente"]
                cargo = parsed["cargo"]
                localidade = parsed["localidade"]
                idade = parsed["idade"]
                pretensao = parsed["pretensao"]
                linkedin = parsed["linkedin"]
                resumo_prof = parsed["resumo_profissional"]
                analise_prof = parsed["analise_perfil"]
                conclusao_txt = parsed["conclusao_texto"]

                data_hora = ""
                nome, data_hora = inferir_nome_data_de_arquivo(caminho, nome, data_hora)

                id_candidato = get_or_create_candidato_por_nome_localidade(
                    nome=nome,
                    localidade=localidade,
                    idade=idade,
                    data_hora=data_hora,
                )

                registrar_parecer_log(
                    data_hora=data_hora,
                    cliente=cliente,
                    cargo=cargo,
                    nome=nome,
                    localidade=localidade,
                    idade=idade,
                    pretensao=pretensao,
                    linkedin=linkedin,
                    resumo_profissional=resumo_prof,
                    analise_perfil=analise_prof,
                    conclusao_texto=conclusao_txt,
                    formato="PDF",
                    caminho_arquivo=caminho,
                    id_candidato=id_candidato,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

            st.session_state["pdfs_para_importar"] = []
            st.success("Importação concluída! Verifique o Histórico e Pipeline.")
        except Exception as e:
            st.error(f"Erro ao importar PDFs: {e}")
