# modules/database.py
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "gac.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Cria as tabelas principais, se não existirem.
    Pode rodar no início do parecer_app.py.
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
            caminho_cv      TEXT,       -- aqui você guarda o caminho do PDF do CV
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
            formato             TEXT,   -- PDF / DOCX
            caminho_arquivo     TEXT,   -- caminho do parecer salvo
            status_etapa        TEXT,
            status_contratacao  TEXT,
            motivo_decline      TEXT,
            FOREIGN KEY(id_vaga) REFERENCES vagas(id_vaga),
            FOREIGN KEY(id_candidato) REFERENCES candidatos(id_candidato)
        );
        """
    )

    conn.commit()
    conn.close()


# Helpers simples de insert (você pode evoluir depois)
def inserir_candidato(nome, idade=None, cidade=None, telefone=None,
                      email=None, linkedin=None, pretensao=None,
                      caminho_cv=None) -> int:
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


def inserir_vaga(id_cliente, cargo, modalidade, data_abertura,
                 data_fechamento, status, descricao) -> int:
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


def registrar_parecer_db(
    id_vaga: int,
    id_candidato: int,
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
