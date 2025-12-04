# modules/database.py
import os
import sqlite3
import hashlib
from datetime import datetime

# Caminho do banco: na raiz do projeto (um nível acima de /modules)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "gac.db")


def get_conn():
    """
    Abre conexão com o banco SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(senha: str) -> str:
    """
    Gera hash SHA256 para armazenar senha.
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def init_db():
    """
    Cria as tabelas principais, se não existirem.
    Também garante a existência do usuário inicial 'rikardo'.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente      INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente    TEXT NOT NULL,
            contato         TEXT,
            telefone        TEXT,
            email           TEXT,
            cidade          TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS candidatos (
            id_candidato    INTEGER PRIMARY KEY AUTOINCREMENT,
            nome            TEXT NOT NULL,
            idade           INTEGER,
            cidade          TEXT,
            telefone        TEXT,
            email           TEXT,
            linkedin        TEXT,
            pretensao       TEXT,
            caminho_cv      TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS vagas (
            id_vaga         INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente      INTEGER,
            cargo           TEXT NOT NULL,
            modalidade      TEXT,
            data_abertura   TEXT,
            data_fechamento TEXT,
            status          TEXT,
            descricao       TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );

        -- vínculo N:N vaga x candidato
        CREATE TABLE IF NOT EXISTS vaga_candidato (
            id_vinculo      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_vaga         INTEGER NOT NULL,
            id_candidato    INTEGER NOT NULL,
            data_vinculo    TEXT DEFAULT (datetime('now')),
            observacao      TEXT,
            UNIQUE (id_vaga, id_candidato),
            FOREIGN KEY(id_vaga) REFERENCES vagas(id_vaga),
            FOREIGN KEY(id_candidato) REFERENCES candidatos(id_candidato)
        );

        -- status configuráveis do pipeline
        CREATE TABLE IF NOT EXISTS status_pipeline (
            id_status       INTEGER PRIMARY KEY AUTOINCREMENT,
            nome            TEXT NOT NULL,
            tipo            TEXT NOT NULL DEFAULT 'ETAPA' -- ou 'CONTRATACAO'
        );

        -- parecer: 1:1 vaga x candidato x parecer
        CREATE TABLE IF NOT EXISTS pareceres (
            id_parecer          INTEGER PRIMARY KEY AUTOINCREMENT,
            id_vaga             INTEGER,
            id_candidato        INTEGER,
            data_hora           TEXT NOT NULL,
            cliente             TEXT,
            cargo               TEXT,
            nome_candidato      TEXT,
            localidade          TEXT,
            idade               TEXT,
            pretensao           TEXT,
            linkedin            TEXT,
            resumo_profissional TEXT,
            analise_perfil      TEXT,
            conclusao_texto     TEXT,
            formato             TEXT,
            caminho_arquivo     TEXT,
            status_etapa        TEXT,
            status_contratacao  TEXT,
            motivo_decline      TEXT,
            FOREIGN KEY(id_vaga) REFERENCES vagas(id_vaga),
            FOREIGN KEY(id_candidato) REFERENCES candidatos(id_candidato)
        );

        -- Acessos (Sistemas)
        CREATE TABLE IF NOT EXISTS acessos (
            id_acesso      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente     INTEGER,
            nome_cliente   TEXT,
            id_candidato   INTEGER,
            nome_usuario   TEXT,
            sistema        TEXT,
            tipo_acesso    TEXT,
            data_inicio    TEXT,
            data_fim       TEXT,
            status         TEXT,
            observacoes    TEXT,
            FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente),
            FOREIGN KEY(id_candidato) REFERENCES candidatos(id_candidato)
        );

        -- Usuários do sistema (login)
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario   INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT NOT NULL UNIQUE,
            nome         TEXT,
            senha_hash   TEXT NOT NULL,
            perfil       TEXT NOT NULL DEFAULT 'MASTER',
            ativo        INTEGER NOT NULL DEFAULT 1,
            created_at   TEXT DEFAULT (datetime('now'))
        );
        """
    )

    conn.commit()

    # Garantir usuário inicial 'rikardo' / '2025' (perfil MASTER)
    try:
        cur.execute("SELECT COUNT(*) AS qtd FROM usuarios;")
        row = cur.fetchone()
        qtd = row["qtd"] if row else 0

        if qtd == 0:
            cur.execute(
                """
                INSERT INTO usuarios (username, nome, senha_hash, perfil, ativo)
                VALUES (?, ?, ?, ?, 1)
                """,
                (
                    "rikardo",
                    "Rikardo Alvim",
                    hash_password("2025"),
                    "MASTER",
                ),
            )
            conn.commit()
    except Exception:
        # Se der qualquer erro nessa checagem, não queremos travar o app
        pass

    conn.close()


# =========================================================
# AUTENTICAÇÃO
# =========================================================

def autenticar(username: str, senha: str):
    """
    Autentica usuário na tabela 'usuarios'.
    Retorna dict com dados do usuário ou None se falhar.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM usuarios
        WHERE username = ? AND ativo = 1
        """,
        (username,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    user = dict(row)
    if user.get("senha_hash") != hash_password(senha):
        return None

    return user


def inserir_usuario(username: str, nome: str, senha: str, perfil: str = "OPERACOES_GERAL", ativo: int = 1) -> int:
    """
    Helper opcional para criar novos usuários via código (se quiser usar depois).
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO usuarios (username, nome, senha_hash, perfil, ativo)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, nome, hash_password(senha), perfil, ativo),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


# =========================================================
# CANDIDATOS
# =========================================================

def inserir_candidato(
    nome,
    idade=None,
    cidade=None,
    telefone=None,
    email=None,
    linkedin=None,
    pretensao=None,
    caminho_cv=None,
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO candidatos (nome, idade, cidade, telefone, email, linkedin, pretensao, caminho_cv)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (nome, idade, cidade, telefone, email, linkedin, pretensao, caminho_cv),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_candidatos(order_by: str = "id_candidato"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM candidatos ORDER BY {order_by};")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obter_candidato(id_candidato: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidatos WHERE id_candidato = ?;", (id_candidato,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_candidato(
    id_candidato: int,
    nome: str,
    idade=None,
    cidade=None,
    telefone=None,
    email=None,
    linkedin=None,
    pretensao=None,
    caminho_cv=None,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE candidatos
        SET nome = ?, idade = ?, cidade = ?, telefone = ?, email = ?,
            linkedin = ?, pretensao = ?, caminho_cv = ?
        WHERE id_candidato = ?
        """,
        (nome, idade, cidade, telefone, email, linkedin, pretensao, caminho_cv, id_candidato),
    )
    conn.commit()
    conn.close()


def buscar_candidato_por_nome(nome: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM candidatos
        WHERE lower(nome) = lower(?)
        """,
        (nome,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_or_create_candidato_por_nome_localidade(
    nome: str,
    localidade: str | None = None,
    idade: str | None = None,
) -> int:
    existentes = buscar_candidato_por_nome(nome)
    if existentes:
        return existentes[0]["id_candidato"]

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO candidatos (nome, idade, cidade)
        VALUES (?, ?, ?)
        """,
        (nome or "Sem nome", idade, localidade),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


# =========================================================
# CLIENTES
# =========================================================

def inserir_cliente(nome_cliente, contato=None, telefone=None, email=None, cidade=None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clientes (nome_cliente, contato, telefone, email, cidade)
        VALUES (?, ?, ?, ?, ?)
        """,
        (nome_cliente, contato, telefone, email, cidade),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_clientes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes ORDER BY nome_cliente;")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# VAGAS
# =========================================================

def inserir_vaga(
    id_cliente,
    cargo,
    modalidade,
    data_abertura,
    data_fechamento,
    status,
    descricao,
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO vagas (
            id_cliente, cargo, modalidade, data_abertura,
            data_fechamento, status, descricao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (id_cliente, cargo, modalidade, data_abertura, data_fechamento, status, descricao),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_vagas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.*, c.nome_cliente
        FROM vagas v
        LEFT JOIN clientes c ON c.id_cliente = v.id_cliente
        ORDER BY v.id_vaga;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obter_vaga(id_vaga: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.*, c.nome_cliente
        FROM vagas v
        LEFT JOIN clientes c ON c.id_cliente = v.id_cliente
        WHERE v.id_vaga = ?
        """,
        (id_vaga,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_vaga(
    id_vaga: int,
    id_cliente,
    cargo,
    modalidade,
    data_abertura,
    data_fechamento,
    status,
    descricao,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE vagas
        SET id_cliente = ?, cargo = ?, modalidade = ?, data_abertura = ?,
            data_fechamento = ?, status = ?, descricao = ?
        WHERE id_vaga = ?
        """,
        (id_cliente, cargo, modalidade, data_abertura, data_fechamento, status, descricao, id_vaga),
    )
    conn.commit()
    conn.close()


# =========================================================
# VÍNCULO VAGA x CANDIDATO
# =========================================================

def vincular_vaga_candidato(id_vaga: int, id_candidato: int, observacao: str = ""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO vaga_candidato (id_vaga, id_candidato, observacao)
        VALUES (?, ?, ?)
        """,
        (id_vaga, id_candidato, observacao),
    )
    conn.commit()
    conn.close()


def listar_vinculos_vaga(id_vaga: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT vc.*, c.nome, c.telefone, c.cidade
        FROM vaga_candidato vc
        JOIN candidatos c ON c.id_candidato = vc.id_candidato
        WHERE vc.id_vaga = ?
        ORDER BY vc.data_vinculo DESC;
        """,
        (id_vaga,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def atualizar_vinculos_vaga(id_vaga: int, ids_candidatos: list[int]):
    """
    Remove vínculos antigos da vaga e recria com os IDs informados.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM vaga_candidato WHERE id_vaga = ?;", (id_vaga,))
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for idc in ids_candidatos:
        cur.execute(
            """
            INSERT INTO vaga_candidato (id_vaga, id_candidato, data_vinculo, observacao)
            VALUES (?, ?, ?, ?)
            """,
            (id_vaga, idc, agora, ""),
        )
    conn.commit()
    conn.close()


# =========================================================
# STATUS PIPELINE
# =========================================================

def inserir_status_pipeline(nome: str, tipo: str = "ETAPA") -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO status_pipeline (nome, tipo)
        VALUES (?, ?)
        """,
        (nome, tipo),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_status_pipeline(tipo: str | None = None):
    conn = get_conn()
    cur = conn.cursor()
    if tipo:
        cur.execute(
            "SELECT * FROM status_pipeline WHERE tipo = ? ORDER BY nome;",
            (tipo,),
        )
    else:
        cur.execute("SELECT * FROM status_pipeline ORDER BY tipo, nome;")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# PARECERES
# =========================================================

def registrar_parecer_db(
    id_vaga: int | None,
    id_candidato: int | None,
    cliente: str,
    cargo: str,
    nome: str,
    localidade: str,
    idade: str,
    pretensao: str,
    linkedin: str,
    resumo_prof: str,
    analise_prof: str,
    conclusao_txt: str,
    formato: str,
    caminho_arquivo: str,
    status_etapa: str = "Em avaliação",
    status_contratacao: str = "Pendente",
    motivo_decline: str = "",
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO pareceres (
            id_vaga, id_candidato, data_hora, cliente, cargo, nome_candidato,
            localidade, idade, pretensao, linkedin, resumo_profissional,
            analise_perfil, conclusao_texto, formato, caminho_arquivo,
            status_etapa, status_contratacao, motivo_decline
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_vaga,
            id_candidato,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cliente,
            cargo,
            nome,
            localidade,
            idade,
            pretensao,
            linkedin,
            resumo_prof,
            analise_prof,
            conclusao_txt,
            formato,
            caminho_arquivo,
            status_etapa,
            status_contratacao,
            motivo_decline,
        ),
    )
    conn.commit()
    conn.close()


def listar_pareceres():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.*, c.nome as nome_cand_real, v.cargo as cargo_vaga
        FROM pareceres p
        LEFT JOIN candidatos c ON c.id_candidato = p.id_candidato
        LEFT JOIN vagas v       ON v.id_vaga      = p.id_vaga
        ORDER BY p.data_hora DESC;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# ACESSOS
# =========================================================

def inserir_acesso(
    id_cliente: int | None,
    nome_cliente: str | None,
    id_candidato: int | None,
    nome_usuario: str | None,
    sistema: str | None,
    tipo_acesso: str | None,
    data_inicio: str | None,
    data_fim: str | None,
    status: str | None,
    observacoes: str | None,
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO acessos (
            id_cliente, nome_cliente, id_candidato, nome_usuario,
            sistema, tipo_acesso, data_inicio, data_fim, status, observacoes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_cliente,
            nome_cliente,
            id_candidato,
            nome_usuario,
            sistema,
            tipo_acesso,
            data_inicio,
            data_fim,
            status,
            observacoes,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_acessos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM acessos
        ORDER BY id_acesso DESC;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obter_acesso(id_acesso: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM acessos WHERE id_acesso = ?;", (id_acesso,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_acesso(
    id_acesso: int,
    id_cliente: int | None,
    nome_cliente: str | None,
    id_candidato: int | None,
    nome_usuario: str | None,
    sistema: str | None,
    tipo_acesso: str | None,
    data_inicio: str | None,
    data_fim: str | None,
    status: str | None,
    observacoes: str | None,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE acessos
        SET id_cliente = ?, nome_cliente = ?, id_candidato = ?, nome_usuario = ?,
            sistema = ?, tipo_acesso = ?, data_inicio = ?, data_fim = ?, status = ?, observacoes = ?
        WHERE id_acesso = ?
        """,
        (
            id_cliente,
            nome_cliente,
            id_candidato,
            nome_usuario,
            sistema,
            tipo_acesso,
            data_inicio,
            data_fim,
            status,
            observacoes,
            id_acesso,
        ),
    )
    conn.commit()
    conn.close()


# =========================================================
# LIMPAR / RESETAR DADOS (se precisar zerar tudo)
# =========================================================

def limpar_dados_principais(confirmar: bool = False):
    """
    Apaga dados de candidatos, vagas, vínculos, pareceres, clientes,
    status_pipeline e acessos.
    Use confirmar=True pra não apagar sem querer.
    """
    if not confirmar:
        raise ValueError("Para limpar dados, chame limpar_dados_principais(confirmar=True).")

    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        DELETE FROM pareceres;
        DELETE FROM vaga_candidato;
        DELETE FROM vagas;
        DELETE FROM candidatos;
        DELETE FROM clientes;
        DELETE FROM status_pipeline;
        DELETE FROM acessos;
        VACUUM;
        """
    )
    conn.commit()
    conn.close()
