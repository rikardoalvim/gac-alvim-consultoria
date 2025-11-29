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
    gerar_campos_via_openai,
    extract_text_from_pdf,
)
from .database import (
    get_conn,
    obter_candidato,
    registrar_parecer_db,
)


def _carregar_vinculos_para_parecer():
    """
    Retorna lista de dicts com:
    id_vaga, id_candidato, nome_candidato, cidade, idade, linkedin, pretensao,
    cargo_vaga, nome_cliente, status_vaga
    Apenas vagas Aberta / Em andamento.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            vc.id_vaga,
            vc.id_candidato,
            c.nome        AS nome_candidato,
            c.cidade      AS cidade_candidato,
            c.idade       AS idade_candidato,
            c.linkedin    AS linkedin_candidato,
            c.pretensao   AS pretensao_candidato,
            v.cargo       AS cargo_vaga,
            v.status      AS status_vaga,
            cli.nome_cliente
        FROM vaga_candidato vc
        JOIN candidatos c ON c.id_candidato = vc.id_candidato
        JOIN vagas v      ON v.id_vaga      = vc.id_vaga
        LEFT JOIN clientes cli ON cli.id_cliente = v.id_cliente
        WHERE v.status IN ('Aberta','Em andamento')
        ORDER BY cli.nome_cliente, v.cargo, c.nome;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def run():
    st.header("📝 Parecer de Triagem")

    # defaults de sessão
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
        "id_candidato_selecionado": None,
        "id_vaga_selecionada": None,
    }.items():
        if campo not in st.session_state:
            st.session_state[campo] = padrao

    # =========================
    # Vínculo vaga x candidato
    # =========================
    st.subheader("Vincular a uma vaga e candidato")

    vinculos = _carregar_vinculos_para_parecer()
    if not vinculos:
        st.info(
            "Nenhuma vaga em andamento com candidatos vinculados. "
            "Vincule candidatos às vagas em **Vagas > Vincular candidatos**."
        )
    else:
        df_v = pd.DataFrame(vinculos).fillna("")
        opcoes = {}
        for _, r in df_v.iterrows():
            chave = f"{int(r['id_vaga'])}|{int(r['id_candidato'])}"
            label = (
                f"[{r.get('nome_cliente','-')}] "
                f"{r['cargo_vaga']}  —  {r['nome_candidato']}"
            )
            opcoes[chave] = label

        chave_sel = st.selectbox(
            "Selecione vaga + candidato:",
            list(opcoes.keys()),
            format_func=lambda x: opcoes[x],
            key="parecer_vinculo_sel",
        )

        if st.button("Carregar dados do vínculo"):
            id_vaga_str, id_cand_str = chave_sel.split("|")
            id_vaga = int(id_vaga_str)
            id_candidato = int(id_cand_str)

            linha = df_v[
                (df_v["id_vaga"] == id_vaga) & (df_v["id_candidato"] == id_candidato)
            ].iloc[0]

            st.session_state["cliente"] = linha.get("nome_cliente", "")
            st.session_state["cargo"] = linha.get("cargo_vaga", "")
            st.session_state["nome"] = linha.get("nome_candidato", "")
            st.session_state["localidade"] = linha.get("cidade_candidato", "")
            st.session_state["idade"] = str(linha.get("idade_candidato") or "")
            st.session_state["pretensao"] = linha.get("pretensao_candidato", "")
            st.session_state["linkedin"] = linha.get("linkedin_candidato", "")

            st.session_state["id_candidato_selecionado"] = id_candidato
            st.session_state["id_vaga_selecionada"] = id_vaga

            st.success("Dados do vínculo carregados para o parecer.")

    st.markdown("---")

    # =========================
    # IA opcional
    # =========================
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

        uploaded_pdf = st.file_uploader(
            "📎 PDF do currículo (opcional para IA)",
            type=["pdf"],
            key="parecer_pdf_ia",
        )
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

    # =========================
    # Formulário do parecer
    # =========================
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

    st.markdown("---")
    st.subheader("Arquivos e saída")

    formato = st.radio("Formato do parecer", ["PDF", "DOCX"], index=0)

    pasta_cv_extra = st.text_input(
        "Pasta com currículos (PDF) para anexar manualmente (opcional)",
        value=BASE_DIR,
    )
    lista_cv_extra = []
    if os.path.isdir(pasta_cv_extra):
        lista_cv_extra = [f for f in os.listdir(pasta_cv_extra) if f.lower().endswith(".pdf")]
    selected_cv_extra = st.selectbox(
        "Anexar currículo PDF adicional ao parecer (opcional)",
        ["(Não anexar)"] + lista_cv_extra,
    )

    output_folder = st.text_input("Pasta de saída dos pareceres", value=BASE_DIR)

    nome_para_base = st.session_state["nome"] if st.session_state["nome"] else "Candidato"
    nome_base = f"Parecer_{nome_para_base.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"

    if st.button("💾 Gerar parecer e registrar histórico"):
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

            id_cand_log = st.session_state.get("id_candidato_selecionado")
            id_vaga_log = st.session_state.get("id_vaga_selecionada")

            # =========================
            # Gera o parecer (PDF/DOCX)
            # =========================
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

                # 1) Anexa CV do candidato (se existir em banco)
                if id_cand_log:
                    cand = obter_candidato(int(id_cand_log))
                    if cand:
                        cv_path = cand.get("caminho_cv") or ""
                        if cv_path and os.path.isfile(cv_path):
                            try:
                                parecer_bytes = merge_pdfs_bytes(parecer_bytes, cv_path)
                            except Exception as e:
                                st.warning(f"Não foi possível anexar o CV do candidato: {e}")

                # 2) Anexa CV extra escolhido (opcional)
                if selected_cv_extra != "(Não anexar)":
                    resume_path = os.path.join(pasta_cv_extra, selected_cv_extra)
                    try:
                        parecer_bytes = merge_pdfs_bytes(parecer_bytes, resume_path)
                    except Exception as e:
                        st.warning(f"Não foi possível anexar o CV adicional: {e}")

                filename = nome_base + ".pdf"
                caminho_final = os.path.join(output_folder, filename)
                with open(caminho_final, "wb") as f:
                    f.write(parecer_bytes)

                # CSV (histórico antigo)
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
                    id_candidato=str(id_cand_log or ""),
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                # Banco de dados (novo oficial)
                registrar_parecer_db(
                    id_vaga=int(id_vaga_log) if id_vaga_log else None,
                    id_candidato=int(id_cand_log) if id_cand_log else None,
                    cliente=cliente,
                    cargo=cargo,
                    nome=nome,
                    localidade=localidade,
                    idade=idade,
                    pretensao=pretensao,
                    linkedin=linkedin,
                    resumo_prof=resumo_prof,
                    analise_prof=analise_prof,
                    conclusao_txt=conclusao_txt,
                    formato="PDF",
                    caminho_arquivo=caminho_final,
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

            else:  # DOCX
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
                    id_candidato=str(id_cand_log or ""),
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                registrar_parecer_db(
                    id_vaga=int(id_vaga_log) if id_vaga_log else None,
                    id_candidato=int(id_cand_log) if id_cand_log else None,
                    cliente=cliente,
                    cargo=cargo,
                    nome=nome,
                    localidade=localidade,
                    idade=idade,
                    pretensao=pretensao,
                    linkedin=linkedin,
                    resumo_prof=resumo_prof,
                    analise_prof=analise_prof,
                    conclusao_txt=conclusao_txt,
                    formato="DOCX",
                    caminho_arquivo=caminho_final,
                    status_etapa="Em avaliação",
                    status_contratacao="Pendente",
                    motivo_decline="",
                )

                st.success(f"Parecer gerado: {caminho_final}")
                st.download_button(
                    "⬇️ Baixar DOCX",
                    data=parecer_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

        except Exception as e:
            st.error(f"Erro ao gerar parecer: {e}")
