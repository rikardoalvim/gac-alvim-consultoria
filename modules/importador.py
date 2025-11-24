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


def _importar_um_pdf(caminho: str):
    """Lê um PDF de parecer, extrai campos e registra no histórico/candidatos."""
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


def run():
    st.header("📥 Importar Pareceres Antigos")

    st.write(
        "Use esta aba para importar PDFs de pareceres antigos, ler os dados da primeira página "
        "e registrar no histórico, criando também o cadastro do candidato, se necessário."
    )

    # ============================================
    # 1) UPLOAD DIRETO DA SUA MÁQUINA
    # ============================================
    st.subheader("1️⃣ Upload de PDFs (da sua máquina)")

    uploaded_files = st.file_uploader(
        "Selecione os PDFs de parecer para importar",
        type=["pdf"],
        accept_multiple_files=True,
        key="imp_upload_files",
    )

    if uploaded_files:
        st.write("Arquivos selecionados:")
        for f in uploaded_files:
            st.markdown(f"- `{f.name}`")

        if st.button("📥 Importar PDFs enviados", key="imp_btn_upload"):
            try:
                dest_dir = os.path.join(BASE_DIR, "importados_upload")
                os.makedirs(dest_dir, exist_ok=True)

                for f in uploaded_files:
                    dest_path = os.path.join(dest_dir, f.name)
                    # salva arquivo no servidor
                    with open(dest_path, "wb") as out:
                        out.write(f.read())

                    # importa esse PDF
                    _importar_um_pdf(dest_path)

                st.success("Importação concluída a partir dos PDFs enviados! Verifique o Histórico e o Pipeline.")
            except Exception as e:
                st.error(f"Erro ao importar PDFs enviados: {e}")

    st.markdown("---")

    # ============================================
    # 2) IMPORTAR A PARTIR DE UMA PASTA NO SERVIDOR
    # (para uso local ou se você já tiver PDFs no filesystem do app)
    # ============================================
    st.subheader("2️⃣ Importar PDFs de uma pasta do servidor (opcional)")

    pasta_import = st.text_input(
        "Pasta onde estão os pareceres antigos (no servidor)",
        value=BASE_DIR,
        key="imp_pasta_servidor",
    )

    if "pdfs_para_importar" not in st.session_state:
        st.session_state["pdfs_para_importar"] = []

    if st.button("🔍 Listar PDFs para importação", key="imp_btn_listar"):
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

    if pdfs_encontrados:
        st.write(f"Foram encontrados {len(pdfs_encontrados)} PDFs novos na pasta do servidor:")
        for c in pdfs_encontrados:
            st.markdown(f"- `{c}`")

        if st.button("📥 Importar PDFs listados (servidor)", key="imp_btn_importar_pasta"):
            try:
                for caminho in pdfs_encontrados:
                    _importar_um_pdf(caminho)

                st.session_state["pdfs_para_importar"] = []
                st.success("Importação concluída a partir da pasta do servidor! Verifique o Histórico e o Pipeline.")
            except Exception as e:
                st.error(f"Erro ao importar PDFs da pasta: {e}")
    else:
        st.info("Nenhum PDF novo listado na pasta do servidor (ou você ainda não clicou em 'Listar PDFs').")


            st.session_state["pdfs_para_importar"] = []
            st.success("Importação concluída! Verifique o Histórico e Pipeline.")
        except Exception as e:
            st.error(f"Erro ao importar PDFs: {e}")
