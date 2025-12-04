# importar_pareceres_pdf.py
import os
import re
import pdfplumber

from modules.database import (
    init_db,
    get_conn,
    get_or_create_candidato_por_nome_localidade,
    inserir_cliente,
    inserir_vaga,
    vincular_vaga_candidato,
    registrar_parecer_db,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_PDFS = os.path.join(BASE_DIR, "pareceres_antigos")


# -------------------------------------------------
# EXTRATOR DE CAMPOS
# -------------------------------------------------
def extrair_campos(texto: str, nome_arquivo: str) -> dict:
    """
    Extrai campos básicos do texto do parecer.
    1) tenta regex nos rótulos do PDF
    2) se não achar NOME/CLIENTE, tenta extrair do nome do arquivo:
       Ex.: Parecer_Smartcitizen_Hendrik_Szeletzki_20251114_1719.pdf
           -> cliente = Smartcitizen
           -> nome   = Hendrik Szeletzki
    """

    def pega(label_regex: str) -> str:
        padrao = rf"{label_regex}\s*:?\s*(.+)"
        m = re.search(padrao, texto, re.IGNORECASE)
        if not m:
            return ""
        valor = m.group(1)
        if valor is None:
            return ""
        return valor.strip()

    def bloco(inicio_regex: str, fim_regex: str | None) -> str:
        """
        Pega o texto entre um título e o próximo.
        Ex.: de 'Análise de Perfil' até 'Conclusão'.
        """
        flags = re.IGNORECASE | re.DOTALL

        m_ini = re.search(inicio_regex, texto, flags)
        if not m_ini:
            return ""

        start_idx = m_ini.end()

        if fim_regex:
            m_fim = re.search(fim_regex, texto[start_idx:], flags)
            if m_fim:
                end_idx = start_idx + m_fim.start()
            else:
                end_idx = len(texto)
        else:
            end_idx = len(texto)

        trecho = texto[start_idx:end_idx]
        if trecho is None:
            return ""
        return trecho.strip()

    dados: dict[str, str] = {}

    # Campos de linha única
    dados["cliente"] = pega(r"Cliente")
    dados["cargo"] = pega(r"Cargo")
    dados["nome"] = pega(r"Nome do candidato|Candidato|Nome")
    dados["localidade"] = pega(r"Localidade|Cidade")
    dados["idade"] = pega(r"Idade")
    dados["pretensao"] = pega(r"Pretens[aã]o")
    dados["linkedin"] = pega(r"LinkedIn")

    # Blocos (títulos dos pareceres antigos)
    dados["resumo_profissional"] = bloco(
        r"Resumo\s+Profissional",
        r"An[aá]lise\s+de\s+Perfil|Analise\s+de\s+Perfil|Conclus[aã]o|Conclusao",
    )

    dados["analise_perfil"] = bloco(
        r"An[aá]lise\s+de\s+Perfil|Analise\s+de\s+Perfil",
        r"Conclus[aã]o|Conclusao|Inform[açc][õo]es\s+de\s+Remunera[cç][aã]o",
    )

    dados["conclusao_texto"] = bloco(
        r"Conclus[aã]o|Conclusao",
        r"Inform[açc][õo]es\s+de\s+Remunera[cç][aã]o|Idade|Pretens[aã]o",
    )

    # -----------------------------------------
    # FALLBACK: PEGAR CLIENTE/NOME DO ARQUIVO
    # -----------------------------------------
    if not dados.get("nome") or not dados.get("cliente"):
        basename = os.path.splitext(os.path.basename(nome_arquivo))[0]
        # ex.: Parecer_Smartcitizen_Hendrik_Szeletzki_20251114_1719
        if basename.lower().startswith("parecer_"):
            basename = basename[len("parecer_") :]

        partes = basename.split("_")
        if len(partes) >= 2:
            cliente_from_file = partes[0]

            if len(partes) >= 4:
                nome_tokens = partes[1:-2]
            else:
                nome_tokens = partes[1:]

            nome_from_file = " ".join(nome_tokens).strip().replace("-", " ")

            if not dados.get("cliente"):
                dados["cliente"] = cliente_from_file
            if not dados.get("nome"):
                dados["nome"] = nome_from_file

    return dados


# -------------------------------------------------
# IMPORTAÇÃO DE UM ÚNICO PDF
# -------------------------------------------------
def importar_parecer(pdf_path: str):
    print(f"\n=== Importando: {os.path.basename(pdf_path)} ===")

    # 1) Ler texto do PDF
    with pdfplumber.open(pdf_path) as pdf:
        texto_total = ""
        for page in pdf.pages:
            txt_page = page.extract_text() or ""
            texto_total += txt_page + "\n"

    # 2) Extrair campos
    campos = extrair_campos(texto_total, pdf_path)

    # Debug básico dos campos (primeiros 80 chars de cada)
    for k, v in campos.items():
        snippet = (v or "")[:80]
        sufixo = "..." if v and len(v) > 80 else ""
        print(f"  {k}: {repr(snippet)}{sufixo}")

    cliente = (campos.get("cliente") or "").strip()
    cargo = (campos.get("cargo") or "").strip()
    nome = (campos.get("nome") or "").strip()
    localidade = (campos.get("localidade") or "").strip()
    idade = (campos.get("idade") or "").strip()
    pretensao = (campos.get("pretensao") or "").strip()
    linkedin = (campos.get("linkedin") or "").strip()
    resumo = (campos.get("resumo_profissional") or "").strip()
    analise = (campos.get("analise_perfil") or "").strip()
    conclusao = (campos.get("conclusao_texto") or "").strip()

    if not nome:
        print("  ⚠ Não foi possível identificar o nome do candidato (nem pelo arquivo). Pulando esse PDF.")
        return

    # 3) Garantir candidato
    try_idade = None
    if idade.isdigit():
        try_idade = int(idade)

    id_candidato = get_or_create_candidato_por_nome_localidade(
        nome=nome,
        localidade=localidade or None,
        idade=str(try_idade) if try_idade is not None else None,
    )
    print(f"  → Candidato id = {id_candidato}")

    # 4) Cliente (pode ser None)
    conn = get_conn()
    cur = conn.cursor()

    id_cliente = None
    if cliente:
        cur.execute(
            "SELECT id_cliente FROM clientes WHERE nome_cliente = ?",
            (cliente,),
        )
        r_cli = cur.fetchone()
        if r_cli:
            id_cliente = r_cli["id_cliente"]
            print(f"  → Cliente já existe (id {id_cliente})")
        else:
            id_cliente = inserir_cliente(
                nome_cliente=cliente,
                contato=None,
                telefone=None,
                email=None,
                cidade=None,
            )
            print(f"  → Cliente criado (id {id_cliente})")

    # 5) Vaga (cliente + cargo)
    id_vaga = None
    if cargo:
        if id_cliente is not None:
            cur.execute(
                """
                SELECT id_vaga FROM vagas
                WHERE cargo = ? AND id_cliente = ?
                """,
                (cargo, id_cliente),
            )
        else:
            cur.execute(
                """
                SELECT id_vaga FROM vagas
                WHERE cargo = ? AND id_cliente IS NULL
                """,
                (cargo,),
            )
        r_v = cur.fetchone()
        if r_v:
            id_vaga = r_v["id_vaga"]
            print(f"  → Vaga já existe (id {id_vaga})")
        else:
            id_vaga = inserir_vaga(
                id_cliente=id_cliente,
                cargo=cargo,
                modalidade=None,
                data_abertura=None,
                data_fechamento=None,
                status="Recuperada",
                descricao="Vaga criada automaticamente a partir de parecer importado.",
            )
            print(f"  → Vaga criada (id {id_vaga})")

    conn.close()

    # 6) Vínculo vaga × candidato
    if id_vaga and id_candidato:
        vincular_vaga_candidato(id_vaga, id_candidato)
        print(f"  → Vínculo vaga {id_vaga} x candidato {id_candidato} criado/garantido.")

    # 7) Apagar parecer antigo com mesmo caminho_arquivo (se houver) e registrar novo
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM pareceres WHERE caminho_arquivo = ?", (pdf_path,))
        conn.commit()
        print("  → Parecer antigo (mesmo caminho_arquivo) removido, se existia.")
    except Exception as e:
        print(f"  ⚠ Erro ao tentar limpar parecer antigo: {e}")
    finally:
        conn.close()

    registrar_parecer_db(
        id_vaga=id_vaga,
        id_candidato=id_candidato,
        cliente=cliente,
        cargo=cargo,
        nome=nome,
        localidade=localidade,
        idade=idade,
        pretensao=pretensao,
        linkedin=linkedin,
        resumo_prof=resumo,
        analise_prof=analise,
        conclusao_txt=conclusao,
        formato="PDF",
        caminho_arquivo=pdf_path,
        status_etapa="Em avaliação",
        status_contratacao="Pendente",
        motivo_decline="Importado de parecer antigo",
    )

    print("  → Parecer registrado no banco com sucesso.")


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    init_db()

    if not os.path.isdir(PASTA_PDFS):
        print(f"Pasta {PASTA_PDFS} não encontrada. Crie e coloque os PDFs lá.")
        return

    arquivos = [f for f in os.listdir(PASTA_PDFS) if f.lower().endswith(".pdf")]
    if not arquivos:
        print("Nenhum PDF encontrado na pasta pareceres_antigos.")
        return

    for arq in arquivos:
        caminho = os.path.join(PASTA_PDFS, arq)
        try:
            print(f"\nImportando {arq}")
            importar_parecer(caminho)
        except Exception as e:
            print(f"Erro ao importar {arq}: {e}")


if __name__ == "__main__":
    main()
