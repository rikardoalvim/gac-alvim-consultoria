# ============================================
# modules/database.py  (VERSÃO COMPLETA E FINAL)
# Banco de Dados Oficial - GAC Alvim Consultoria
# ============================================

import os
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# Caminho do banco: arquivo "gac.db" na raiz do projeto
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "gac.db")


# ---------------------------------------------------------
# Conexão com o banco
# ---------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ---------------------------------------------------------
# Criação de todas as tabelas do sistema
# ---------------------------------------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        ---------------------------------------------------
        -- USUÁRIOS
        ---------------------------------------------------
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario      INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT UNIQUE NOT NULL,
            nome            TEXT,
            senha_hash      TEXT NOT NULL,
            ativo           INTEGER DEFAULT 1,
            must_change     INTEGER DEFAULT 0,
            perfil          TEXT DEFAULT 'OPERACOES_GERAL',
            created_at      TEXT DEFAULT (datetime('now'))
        );

        ---------------------------------------------------
        -- CLIENTES
        ---------------------------------------------------
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente      INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente    TEXT NOT NULL,
            contato         TEXT,
            telefone        TEXT,
            email           TEXT,
            cidade          TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        ---------------------------------------------------
        -- CANDIDATOS
        ---------------------------------------------------
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

        ---------------------------------------------------
        -- VAGAS
        ---------------------------------------------------
        CREATE TABLE IF NOT EXISTS vagas (
            id_vaga         INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente      INTEGER,
            cargo           TEXT NOT NULL,
            modalidade      TEXT,
            data_abertura   TEXT,
            data_fechamento TEXT,
            status          TEXT,
            descricao       TEXT,
            FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL
        );

        ---------------------------------------------------
        -- VÍNCULO VAGA × CANDIDATO
        ---------------------------------------------------
        CREATE TABLE IF NOT EXISTS vaga_candidato (
            id_vinculo      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_vaga         INTEGER NOT NULL,
            id_candidato    INTEGER NOT NULL,
            data_vinculo    TEXT DEFAULT (datetime('now')),
            observacao      TEXT,
            UNIQUE(id_vaga, id_candidato),
            FOREIGN KEY(id_vaga) REFERENCES vagas(id_vaga) ON DELETE CASCADE,
            FOREIGN KEY(id_candidato) REFERENCES candidatos(id_candidato) ON DELETE CASCADE
        );

        ---------------------------------------------------
        -- STATUS DO PIPELINE
        ---------------------------------------------------
        CREATE TABLE IF NOT EXISTS status_pipeline (
            id_status       INTEGER PRIMARY KEY AUTOINCREMENT,
            nome            TEXT NOT NULL,
            tipo            TEXT NOT NULL DEFAULT 'ETAPA'
        );

        ---------------------------------------------------
        -- PARECERES
        ---------------------------------------------------
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
            FOREIGN KEY(id_vaga) REFERENCES vagas(id_vaga) ON DELETE SET NULL,
            FOREIGN KEY(id_candidato) REFERENCES candidatos(id_candidato) ON DELETE SET NULL
        );

        ---------------------------------------------------
        -- ACESSOS A SISTEMAS
        ---------------------------------------------------
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
            FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL,
            FOREIGN KEY(id_candidato) REFERENCES candidatos(id_candidato) ON DELETE SET NULL
        );
        """
    )

    conn.commit()
    conn.close()

    seed_default_data()


# ---------------------------------------------------------
# DADOS PADRÃO (usuário master + status pipeline)
# ---------------------------------------------------------
def seed_default_data():
    conn = get_conn()
    cur = conn.cursor()

    # Usuário Master
    cur.execute("SELECT COUNT(*) AS n FROM usuarios;")
    if cur.fetchone()["n"] == 0:
        cur.execute(
            """
            INSERT INTO usuarios (username, nome, senha_hash, must_change, perfil)
            VALUES ('rikardo', 'Rikardo Alvim', '2025', 0, 'MASTER')
            """
        )

    # Status pipeline padrão
    cur.execute("SELECT COUNT(*) AS n FROM status_pipeline;")
    if cur.fetchone()["n"] == 0:
        defaults = [
            ("Triagem", "ETAPA"),
            ("Entrevista Técnica", "ETAPA"),
            ("Enviado ao Cliente", "ETAPA"),
            ("Stand-by", "ETAPA"),
            ("Aprovado", "CONTRATACAO"),
            ("Reprovado", "CONTRATACAO"),
        ]
        cur.executemany(
            "INSERT INTO status_pipeline (nome, tipo) VALUES (?, ?)", defaults
        )

    conn.commit()
    conn.close()


# =========================================================
# USUÁRIOS
# =========================================================
def autenticar(username, senha):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM usuarios WHERE username = ? AND senha_hash = ? AND ativo = 1",
        (username, senha),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_senha(username, nova_senha):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE usuarios SET senha_hash = ?, must_change = 0 WHERE username = ?",
        (nova_senha, username),
    )
    conn.commit()
    conn.close()


def listar_usuarios():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios ORDER BY username;")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def inserir_usuario(username, nome, senha_hash, perfil="OPERACOES_GERAL"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO usuarios (username, nome, senha_hash, perfil, must_change)
        VALUES (?, ?, ?, ?, 1)
        """,
        (username, nome, senha_hash, perfil),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


# =========================================================
# CLIENTES
# =========================================================
def inserir_cliente(nome_cliente, contato=None, telefone=None, email=None, cidade=None):
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
# CANDIDATOS
# =========================================================
def inserir_candidato(nome, idade=None, cidade=None, telefone=None, email=None,
                      linkedin=None, pretensao=None, caminho_cv=None):
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


def listar_candidatos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidatos ORDER BY id_candidato DESC;")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_candidato_por_nome(nome):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidatos WHERE LOWER(nome) = LOWER(?)", (nome,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_or_create_candidato_por_nome_localidade(nome, localidade=None, idade=None):
    encontrados = buscar_candidato_por_nome(nome)
    if encontrados:
        return encontrados[0]["id_candidato"]

    return inserir_candidato(nome, idade, localidade)


# =========================================================
# VAGAS
# =========================================================
def inserir_vaga(id_cliente, cargo, modalidade, data_abertura, data_fechamento,
                 status, descricao):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO vagas (id_cliente, cargo, modalidade, data_abertura, data_fechamento, status, descricao)
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
        ORDER BY id_vaga DESC;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# VÍNCULO VAGA × CANDIDATO
# =========================================================
def vincular_vaga_candidato(id_vaga, id_candidato, observacao=""):
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


def listar_vinculos_vaga(id_vaga):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT vc.*, c.nome, c.telefone, c.cidade
        FROM vaga_candidato vc
        JOIN candidatos c ON c.id_candidato = vc.id_candidato
        WHERE vc.id_vaga = ?
        ORDER BY vc.data_vinculo DESC
        """,
        (id_vaga,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# STATUS PIPELINE
# =========================================================
def inserir_status_pipeline(nome, tipo="ETAPA"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO status_pipeline (nome, tipo) VALUES (?, ?)",
        (nome, tipo),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_status_pipeline():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM status_pipeline ORDER BY tipo, nome;")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# PARECERES
# =========================================================
def registrar_parecer_db(id_vaga, id_candidato, cliente, cargo, nome, localidade, idade,
                         pretensao, linkedin, resumo_prof, analise_prof, conclusao_txt,
                         formato, caminho_arquivo, status_etapa="Em avaliação",
                         status_contratacao="Pendente", motivo_decline=""):

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
            id_vaga, id_candidato, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cliente, cargo, nome, localidade, idade, pretensao, linkedin,
            resumo_prof, analise_prof, conclusao_txt, formato, caminho_arquivo,
            status_etapa, status_contratacao, motivo_decline,
        ),
    )
    conn.commit()
    conn.close()


# =========================================================
# ACESSOS
# =========================================================
def inserir_acesso(id_cliente, nome_cliente, id_candidato, nome_usuario,
                   sistema, tipo_acesso, data_inicio, data_fim, status, observacoes):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO acessos (
            id_cliente, nome_cliente, id_candidato, nome_usuario, sistema,
            tipo_acesso, data_inicio, data_fim, status, observacoes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_cliente, nome_cliente, id_candidato, nome_usuario,
            sistema, tipo_acesso, data_inicio, data_fim, status, observacoes
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_acessos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM acessos ORDER BY id_acesso DESC;")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# RESET GERAL
# =========================================================
def limpar_dados(confirmar=False):
    if not confirmar:
        raise ValueError("Use limpar_dados(confirmar=True) para executar.")

    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        DELETE FROM pareceres;
        DELETE FROM vaga_candidato;
        DELETE FROM vagas;
        DELETE FROM candidatos;
        DELETE FROM clientes;
        DELETE FROM acessos;
        DELETE FROM status_pipeline;
        DELETE FROM usuarios;
        VACUUM;
        """
    )
    conn.commit()
    conn.close()
