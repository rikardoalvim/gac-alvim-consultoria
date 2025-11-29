# importar_pareceres_pdf.py
import os
import re
import pdfplumber

from modules.database import (
    init_db,
    get_conn,
    inserir_candidato,
    inserir_cliente,
    inserir_vaga,
    vincular_vaga_candidato,
    registrar_parecer_db,
    limpar_dados_principais,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_PDFS = os.path.join(BASE_DIR, "pareceres_antigos")


# --------------------------------------------------------------------
# 1) EXTRATOR ROBUSTO DE TEXTO
# --------------------------------------------------------------------
def limpar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.replace("\x00", "").replace("\r", "\n")
    texto = re.sub(r"\n{2,}", "\n", texto)
    return texto.strip()


def extrair_campos(texto_bruto: str, caminho_pdf: str) -> dict:
    texto = limpar_texto(texto_bruto)

    def pega(label):
        padrao = rf"{label}\s*:?\s*(.+)"
        m = re.search(padrao, texto, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    def bloco(inicio, fim=None):
        flags = re.IGNORECASE | re.DOTALL

        m_ini = re.search(inicio, texto, flags)
        if not m_ini:
            return ""

        start = m_ini.end()

        if fim:
            m_fim = re.search(fim, texto[start:], flags)
            end = start + m_fim.start() if m_fim else len(texto)
        else:
            end = len(texto)

        return texto[start:end].strip()

    dados = {}

    dados["cliente"] = pega("Cliente")
    dados["cargo"] = pega("Cargo")
    dados["nome"] = pega("Nome do candidato|Candidato|Nome")
    dados["localidade"] = pega("Localidade|Cidade")
    dados["idade"] = pega("Idade")
    dados["pretensao"] = pega(r"Pretens[aã]o")
    dados["linkedin"] = pega("LinkedIn")

    # Blocos
    dados["resumo_profissional"] = bloco(
        r"Resumo\s+Profissional",
        r"An[aá]lise\s+de\s+Perfil|Conclus"
    )

    dados["analise_perfil"] = bloco(
        r"An[aá]lise\s+de\s+Perfil",
        r"Conclus|Inform"
    )

    dados["conclusao_texto"] = bloco(
        r"Conclus",
        r"Inform|Idade|Pretens"
    )

    # FALLBACK – Nome e cliente do arquivo
    basename = os.path.basename(caminho_pdf).lower()
    if basename.startswith("parecer_"):
        partes = os.path.splitext(os.path.basename(caminho_pdf))[0].split("_")[1:]

        if len(partes) >= 2:
            cliente = partes[0].strip()
            nome = " ".join(partes[1:-2]).replace("-", " ").strip()

            if not dados["cliente"]:
                dados["cliente"] = cliente
            if not dados["nome"]:
                dados["nome"] = nome

    return dados


# --------------------------------------------------------------------
# 2) IMPORTAR UM PDF INDIVIDUAL
# --------------------------------------------------------------------
def importar_parecer(pdf_path: str):
    print(f"\n📄 Importando {os.path.basename(pdf_path)}")

    # -------------------------------------------------
    # Extrair texto do PDF
    # -------------------------------------------------
    try:
        with pdfplumber.open(pdf_path) as pdf:
            texto_total = ""
            for p in pdf.pages:
                parte = p.extract_text() or ""
                texto_total += parte + "\n"
    except Exception as e:
        print(f"❌ Erro ao abrir PDF: {e}")
        return

    campos = extrair_campos(texto_total, pdf_path)

    nome = campos["nome"].strip()
    cliente = campos["cliente"].strip()
    cargo = campos["cargo"].strip()

    resumo = campos["resumo_profissional"]
    analise = campos["analise_perfil"]
    conclusao = campos["conclusao_texto"]

    if not nome:
        print("⚠ Sem nome — ignorando PDF.")
        return

    # -------------------------------------------------
    # Criar ou localizar candidato
    # -------------------------------------------------
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id_candidato FROM candidatos WHERE nome = ?", (nome,))
    row = cur.fetchone()

    if row:
        id_candidato = row["id_candidato"]
        print(f"👤 Candidato já existe (ID {id_candidato})")
    else:
        id_candidato = inserir_candidato(
            nome=nome,
            idade=campos["idade"] or None,
            cidade=campos["localidade"] or None,
            telefone=None,
            email=None,
            linkedin=campos["linkedin"],
            pretensao=campos["pretensao"],
            caminho_cv=None,
        )
        print(f"👤 Candidato criado (ID {id_candidato})")

    # -------------------------------------------------
    # Criar ou localizar cliente
    # -------------------------------------------------
    id_cliente = None
    if cliente:
        cur.execute("SELECT id_cliente FROM clientes WHERE nome_cliente = ?", (cliente,))
        row = cur.fetchone()
        if row:
            id_cliente = row["id_cliente"]
            print(f"🏢 Cliente já existe (ID {id_cliente})")
        else:
            id_cliente = inserir_cliente(cliente)
            print(f"🏢 Cliente criado (ID {id_cliente})")

    # -------------------------------------------------
    # Criar ou localizar vaga
    # -------------------------------------------------
    id_vaga = None
    if cargo:
        cur.execute(
            """
            SELECT id_vaga FROM vagas
            WHERE cargo = ?
              AND (id_cliente = ? OR id_cliente IS NULL)
            """,
            (cargo, id_cliente),
        )
        row = cur.fetchone()

        if row:
            id_vaga = row["id_vaga"]
            print(f"📌 Vaga já existe (ID {id_vaga})")
        else:
            id_vaga = inserir_vaga(
                id_cliente=id_cliente,
                cargo=cargo,
                modalidade="Importada",
                data_abertura=None,
                data_fechamento=None,
                status="Recuperada",
                descricao="Vaga importada automaticamente dos pareceres antigos.",
            )
            print(f"📌 Vaga criada (ID {id_vaga})")

    conn.close()

    # -------------------------------------------------
    # Criar vínculo vaga × candidato
    # -------------------------------------------------
    if id_vaga:
        vincular_vaga_candidato(id_vaga, id_candidato)
        print(f"🔗 Vínculo criado/garantido para vaga {id_vaga} e candidato {id_candidato}")

    # -------------------------------------------------
    # Remover parecer duplicado (se existir)
    # -------------------------------------------------
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM pareceres WHERE caminho_arquivo = ?",
        (pdf_path,)
    )
    conn.commit()
    conn.close()

    # -------------------------------------------------
    # Registrar parecer atual
    # -------------------------------------------------
    registrar_parecer_db(
        id_vaga=id_vaga,
        id_candidato=id_candidato,
        cliente=cliente,
        cargo=cargo,
        nome=nome,
        localidade=campos["localidade"],
        idade=campos["idade"],
        pretensao=campos["pretensao"],
        linkedin=campos["linkedin"],
        resumo_prof=resumo,
        analise_prof=analise,
        conclusao_txt=conclusao,
        formato="PDF",
        caminho_arquivo=pdf_path,
        status_etapa="Importado",
        status_contratacao="Pendente",
        motivo_decline="Importado de parecer antigo",
    )

    print("✅ Parecer importado com sucesso.")


# --------------------------------------------------------------------
# 3) MAIN
# --------------------------------------------------------------------
def main():
    print("🔄 Inicializando banco...")
    init_db()

    print("\n⚠ Deseja limpar TODOS os dados antes de importar?")
    print("   -> Digite 'LIMPAR' para apagar tudo e reconstruir.")
    escolha = input("Resposta: ")

    if escolha.strip().upper() == "LIMPAR":
        print("🧹 Apagando banco...")
        limpar_dados_principais(confirmar=True)
        print("✔ Banco limpo.")

    if not os.path.isdir(PASTA_PDFS):
        print(f"\n❌ Pasta não encontrada: {PASTA_PDFS}")
        return

    arquivos = [f for f in os.listdir(PASTA_PDFS) if f.lower().endswith(".pdf")]
    if not arquivos:
        print("\n⚠ Nenhum PDF encontrado na pasta.")
        return

    print(f"\n📁 {len(arquivos)} PDFs encontrados.")
    for arq in arquivos:
        importar_parecer(os.path.join(PASTA_PDFS, arq))

    print("\n🎉 Importação concluída com sucesso!")


if __name__ == "__main__":
    main()
