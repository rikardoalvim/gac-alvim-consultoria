import os
from datetime import datetime

import pandas as pd
import streamlit as st

from .core import (
    BASE_DIR,
    build_parecer_pdf_to_bytes,
    build_parecer_docx_to_bytes,
    merge_pdfs_bytes,
    registrar_parecer_log,
    carregar_candidatos,
    carregar_clientes,
    gerar_campos_via_openai,
    extract_text_from_pdf,
    carregar_vagas,
    carregar_vaga_candidatos,
    carregar_pareceres_log,  # usado na parte de "carregar parecer" se você quiser manter
    LOG_PAR,                  # mantido só por compatibilidade, não é obrigatório usar aqui
)


def _descobrir_caminho_cv(row_cand: pd.Series) -> str:
    """
    Tenta achar o caminho do currículo dentro do cadastro do candidato.
    Ajuste a lista de nomes de coluna se o seu layout for diferente.
    """
    possiveis_colunas = [
        "arquivo_cv",
        "caminho_cv",
        "caminho_curriculo",
        "curriculo_pdf",
        "arquivo_curriculo",
    ]
    for col in possiveis_colunas:
        if col in row_cand and str(row_cand[col]).strip():
            return str(row_cand[col]).strip()
    return ""


def run():
    st.header("📝 Parecer de Triagem")

    # Carrega bases que podem ser usadas em mais de um ponto
    df_cand = carregar_candidatos()
    df_vinc = carregar_vaga_candidatos()
    df_vagas = carregar_vagas()

    # ============================================================
    # 1. Inicializa session_state (campos do formulário)
    # ============================================================
    for campo, padrao in {
        "cliente": "",
        "cargo": "",
        "nome": "",
        "localidade": "",
        "idade": "",
        "pretensao": "",
        "linkedin": "",
        "resumo_profissional": "",
        "analise_perfil": "",
        "conclusao_texto": "",
        "id_candidato_selecionado": "",
        "cv_caminho_candidato": "",
    }.items():
        if campo not in st.session_state:
            st.session_state[campo] = padrao

    # ============================================================
    # 2. Vínculo com candidato (carrega TUDO de uma vez)
    # ============================================================
    st.subheader("Vincular a um candidato (opcional)")
    id_candidato_escolhido = ""

    if df_cand.empty:
        st.info("Nenhum candidato cadastrado ainda.")
    else:
        op_cand = {int(row["id_candidato"]): row["nome"] for _, row in df_cand.iterrows()}
        id_candidato_escolhido = st.selectbox(
            "Selecione um candidato:",
            options=["(Nenhum)"] + list(op_cand.keys()),
            format_func=lambda x: op_cand[x] if x != "(Nenhum)" else x,
            key="parecer_cand_sel",
        )

        if id_candidato_escolhido != "(Nenhum)":
            if st.button("🔄 Carregar dados completos", use_container_width=True):
                try:
                    # ---------- Dados do CANDIDATO ----------
                    row_cand = df_cand[df_cand["id_candidato"] == str(id_candidato_escolhido)].iloc[0]

                    st.session_state["nome"] = row_cand.get("nome", "")
                    st.session_state["idade"] = str(row_cand.get("idade", ""))
                    st.session_state["localidade"] = row_cand.get("cidade", "")
                    st.session_state["pretensao"] = row_cand.get("pretensao", "")
                    st.session_state["linkedin"] = row_cand.get("linkedin", "")
                    st.session_state["id_candidato_selecionado"] = str(row_cand.get("id_candidato", ""))

                    # ---------- Descobrir caminho do CV ----------
                    cv_path = _descobrir_caminho_cv(row_cand)
                    if cv_path:
                        # Se veio só o nome, assume BASE_DIR
                        if not os.path.isabs(cv_path):
                            cv_path_abs = os.path.join(BASE_DIR, cv_path)
                        else:
                            cv_path_abs = cv_path
                        st.session_state["cv_caminho_candidato"] = cv_path_abs
                    else:
                        st.session_state["cv_caminho_candidato"] = ""

                    # ---------- Vaga vinculada mais recente ----------
                    if not df_vinc.empty and not df_vagas.empty:
                        df_vinc["id_candidato"] = df_vinc["id_candidato"].astype(str)
                        df_vagas["id_vaga"] = df_vagas["id_vaga"].astype(str)

                        df_cand_vinc = df_vinc[df_vinc["id_candidato"] == str(id_candidato_escolhido)]
                        if not df_cand_vinc.empty:
                            df_cand_vinc = df_cand_vinc.copy()
                            if "data_vinculo" in df_cand_vinc.columns:
                                try:
                                    df_cand_vinc["__dt"] = pd.to_datetime(
                                        df_cand_vinc["data_vinculo"], errors="coerce"
                                    )
                                    df_cand_vinc = df_cand_vinc.sort_values("__dt")
                                except Exception:
                                    df_cand_vinc = df_cand_vinc.reset_index(drop=True)

                            row_vinc = df_cand_vinc.iloc[-1]
                            id_vaga = str(row_vinc["id_vaga"])
                            row_vaga = df_vagas[df_vagas["id_vaga"] == id_vaga]

                            if not row_vaga.empty:
                                vaga = row_vaga.iloc[0]
                                st.session_state["cliente"] = vaga.get("nome_cliente", st.session_state["cliente"])
                                st.session_state["cargo"] = vaga.get("cargo", st.session_state["cargo"])
                    st.success("Dados completos carregados (candidato + vaga vinculada + currículo).")
                except Exception as e:
                    st.error(f"Erro ao carregar dados completos: {e}")

    # ============================================================
    # 3. Vínculo com cliente (caso queira trocar manualmente)
    # ============================================================
    st.subheader("Vincular a um cliente (opcional)")
    df_cli = carregar_clientes()
    if df_cli.empty:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        op_cli = {int(row["id_cliente"]): row["nome_cliente"] for _, row in df_cli.iterrows()}
        id_cli_sel = st.selectbox(
            "Selecione o cliente:",
            options=["(Nenhum)"] + list(op_cli.keys()),
            format_func=lambda x: op_cli[x] if x != "(Nenhum)" else x,
            key="parecer_cli_sel",
        )
        if id_cli_sel != "(Nenhum)" and st.button("Carregar nome do cliente", use_container_width=True):
            st.session_state["cliente"] = op_cli[id_cli_sel]
            st.success("Cliente carregado no formulário.")

    st.markdown("---")

    # ============================================================
    # 4. IA opcional para gerar textos
    # ============================================================
    with st.expander("🤖 IA - Preencher campos automaticamente (opcional)", expanded=False):
        col_ia, _ = st.columns(2)
        with col_ia:
            if st.button("🔌 Testar conexão OpenAI"):
                from .core import get_openai_client

                client = get_openai_client()
                if not client:
                    st.error("OpenAI não configurado (biblioteca ou OPENAI_API_KEY).")
                else:
                    try:
                        _ = client.responses.create(model="gpt-4.1-mini", input="OK?")
                        st.success("Conexão OK.")
                    except Exception as e:
                        st.error(f"Erro na conexão: {e}")

        uploaded_pdf = st.file_uploader("📎 PDF do currículo (opcional)", type=["pdf"], key="parecer_pdf_ia")
        obs_ia = st.text_area("Observações para IA (opcional)", height=100)

        if st.button("✨ Gerar campos via IA"):
            if not uploaded_pdf and not obs_ia.strip():
                st.warning("Envie um PDF ou escreva observações para usar a IA.")
            else:
                try:
                    texto_pdf = extract_text_from_pdf(uploaded_pdf) if uploaded_pdf else ""
                    texto_base = (texto_pdf or "") + "\n\n" + (obs_ia or "")
                    nome_ai, resumo_ai, analise_ai, concl_ai = gerar_campos_via_openai(texto_base)
                    if nome_ai:
                        st.session_state["nome"] = nome_ai
                    if resumo_ai:
                        st.session_state["resumo_profissional"] = resumo_ai
                    if analise_ai:
                        st.session_state["analise_perfil"] = analise_ai
                    if concl_ai:
                        st.session_state["conclusao_texto"] = concl_ai
                    st.success("Campos preenchidos pela IA.")
                except Exception as e:
                    st.error(f"Erro ao usar IA: {e}")

    st.markdown("---")

    # ============================================================
    # 5. Formulário principal do parecer
    # ============================================================
    st.subheader("Formulário do parecer")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Cliente", key="cliente")
        st.text_input("Nome do candidato", key="nome")
        st.text_input("Idade", key="idade")
    with col2:
        st.text_input("Cargo", key="cargo")
        st.text_input("Localidade", key="localidade")
        st.text_input("Pretensão Salarial (ex.: R$ 4.500,00)", key="pretensao")

    st.text_input("LinkedIn (opcional)", key="linkedin")

    st.subheader("Resumo profissional")
    st.text_area(
        "Resumo profissional",
        key="resumo_profissional",
        height=150,
        placeholder="Descreva de forma objetiva o perfil profissional do candidato...",
    )

    st.subheader("Análise de perfil")
    st.text_area(
        "Análise de perfil",
        key="analise_perfil",
        height=150,
        placeholder="Postura, comunicação, senioridade, aderência à vaga...",
    )

    st.subheader("Conclusão")
    st.text_area(
        "Conclusão",
        key="conclusao_texto",
        height=120,
        placeholder="Conclusão geral e recomendação...",
    )

    # ============================================================
    # 6. Arquivos e saída (usando CV do candidato por padrão)
    # ============================================================
    st.markdown("---")
    st.subheader("Arquivos e saída")

    formato = st.radio("Formato do parecer", ["PDF", "DOCX"], index=0)

    cv_path_candidato = st.session_state.get("cv_caminho_candidato", "")
    usar_cv_candidato = False
    pasta_cv = ""
    selected_cv = "(Não anexar)"

    if cv_path_candidato:
        if os.path.isfile(cv_path_candidato):
            st.success(
                f"Currículo cadastrado encontrado: **{os.path.basename(cv_path_candidato)}**"
            )
            usar_cv_candidato = st.checkbox(
                "Anexar automaticamente o currículo do cadastro do candidato",
                value=True,
            )
        else:
            st.warning(
                "Há um caminho de currículo no cadastro do candidato, "
                "mas o arquivo não foi encontrado no disco. "
                "Verifique o caminho ou selecione manualmente abaixo."
            )
            st.session_state["cv_caminho_candidato"] = ""
            cv_path_candidato = ""

    # Se NÃO for usar o CV cadastrado, abre o modo manual antigo
    if not usar_cv_candidato:
        pasta_cv = st.text_input("Pasta com currículos (PDF)", value=BASE_DIR)
        lista_cv = []
        if os.path.isdir(pasta_cv):
            lista_cv = [f for f in os.listdir(pasta_cv) if f.lower().endswith(".pdf")]
        selected_cv = st.selectbox(
            "Anexar currículo PDF ao parecer (opcional)",
            ["(Não anexar)"] + lista_cv,
        )

    output_folder = st.text_input("Pasta de saída dos pareceres", value=BASE_DIR)

    nome_para_base = st.session_state["nome"] if st.session_state["nome"] else "Candidato"
    nome_base = f"Parecer_{nome_para_base.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"

    # ============================================================
    # 7. Geração do parecer + registro em LOG
    # ============================================================
    if st.button("💾 Gerar parecer e registrar histórico", use_container_width=True):
        nome = st.session_state["nome"]
        if not nome.strip():
            st.error("Informe o nome do candidato.")
            return

        try:
            os.makedirs(output_folder, exist_ok=True)
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cliente = st.session_state["cliente"]
            cargo = st.session_state["cargo"]
            localidade = st.session_state["localidade"]
            idade = st.session_state["idade"]
            pretensao = st.session_state["pretensao"]
            linkedin = st.session_state["linkedin"]
            resumo_prof = st.session_state["resumo_profissional"]
            analise_prof = st.session_state["analise_perfil"]
            conclusao_txt = st.session_state["conclusao_texto"]
            id_cand_log = st.session_state.get("id_candidato_selecionado", "")

            # ----------------- PDF -----------------
            if formato == "PDF":
                parecer_bytes = build_parecer_pdf_to_bytes(
                    cliente,
                    cargo,
                    nome,
                    localidade,
                    idade,
                    pretensao,
                    resumo_prof,
                    analise_prof,
                    conclusao_txt,
                    linkedin,
                )

                # Anexa CV do candidato (preferencial)
                if usar_cv_candidato and cv_path_candidato and os.path.isfile(cv_path_candidato):
                    parecer_bytes = merge_pdfs_bytes(parecer_bytes, cv_path_candidato)
                # ou CV selecionado manualmente
                elif (not usar_cv_candidato) and selected_cv != "(Não anexar)":
                    resume_path = os.path.join(pasta_cv, selected_cv)
                    if os.path.isfile(resume_path):
                        parecer_bytes = merge_pdfs_bytes(parecer_bytes, resume_path)

                filename = nome_base + ".pdf"
                caminho_final = os.path.join(output_folder, filename)
                with open(caminho_final, "wb") as f:
                    f.write(parecer_bytes)

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
                    caminho_arquivo=caminho_final,
                    id_candidato=id_cand_log,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                st.success(f"Parecer gerado: {caminho_final}")
                st.download_button(
                    "⬇️ Baixar PDF",
                    data=parecer_bytes,
                    file_name=filename,
                    mime="application/pdf",
                )

            # ----------------- DOCX -----------------
            else:
                parecer_bytes = build_parecer_docx_to_bytes(
                    cliente,
                    cargo,
                    nome,
                    localidade,
                    idade,
                    pretensao,
                    resumo_prof,
                    analise_prof,
                    conclusao_txt,
                    linkedin,
                )
                filename = nome_base + ".docx"
                caminho_final = os.path.join(output_folder, filename)
                with open(caminho_final, "wb") as f:
                    f.write(parecer_bytes)

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
                    formato="DOCX",
                    caminho_arquivo=caminho_final,
                    id_candidato=id_cand_log,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                st.success(f"Parecer gerado: {caminho_final}")
                st.download_button(
                    "⬇️ Baixar DOCX",
                    data=parecer_bytes,
                    file_name=filename,
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                )

        except Exception as e:
            st.error(f"Erro ao gerar parecer: {e}")


