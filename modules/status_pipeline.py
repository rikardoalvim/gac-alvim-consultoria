import os
import unicodedata
from typing import Tuple

import pandas as pd
import streamlit as st

# Arquivo de catálogo de status/etapas do pipeline
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(MODULE_DIR, ".."))
STATUS_FILE = os.path.join(ROOT_DIR, "status_pipeline.csv")


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = "".join(c if c.isalnum() else "-" for c in text)
    while "--" in text:
        text = text.replace("--", "-")
    return text.strip("-") or "status"


def _default_status_df() -> pd.DataFrame:
    data = [
        # Etapas de pipeline
        {"tipo": "etapa", "codigo": "em-avaliacao", "descricao": "Em avaliação", "ativo": 1},
        {"tipo": "etapa", "codigo": "triagem", "descricao": "Triagem", "ativo": 1},
        {"tipo": "etapa", "codigo": "entrevista", "descricao": "Entrevista", "ativo": 1},
        {"tipo": "etapa", "codigo": "finalista", "descricao": "Finalista", "ativo": 1},
        {"tipo": "etapa", "codigo": "nao-seguiu-processo", "descricao": "Não seguiu processo", "ativo": 1},
        # Status de contratação
        {"tipo": "contratacao", "codigo": "pendente", "descricao": "Pendente", "ativo": 1},
        {"tipo": "contratacao", "codigo": "aprovado-contratado", "descricao": "Aprovado / Contratado", "ativo": 1},
        {"tipo": "contratacao", "codigo": "reprovado", "descricao": "Reprovado", "ativo": 1},
        {"tipo": "contratacao", "codigo": "desistiu", "descricao": "Desistiu", "ativo": 1},
    ]
    return pd.DataFrame(data)


def load_status_df() -> pd.DataFrame:
    """Carrega (ou cria) o catálogo de status/etapas do pipeline."""
    if not os.path.exists(STATUS_FILE):
        df = _default_status_df()
        df.to_csv(STATUS_FILE, index=False, encoding="utf-8")
        return df

    df = pd.read_csv(STATUS_FILE, dtype={"tipo": str, "codigo": str, "descricao": str, "ativo": int})

    for col in ["tipo", "codigo", "descricao"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)

    if "ativo" not in df.columns:
        df["ativo"] = 1
    else:
        df["ativo"] = df["ativo"].fillna(1).astype(int)

    return df


def save_status_df(df: pd.DataFrame) -> None:
    df.to_csv(STATUS_FILE, index=False, encoding="utf-8")


def get_pipeline_status_options() -> Tuple[list, list]:
    """
    Retorna duas listas:
    - etapas de pipeline
    - status de contratação
    apenas com registros ativos.
    """
    df = load_status_df()
    etapas = (
        df[(df["tipo"] == "etapa") & (df["ativo"] == 1)]["descricao"]
        .dropna()
        .astype(str)
        .tolist()
    )
    contratos = (
        df[(df["tipo"] == "contratacao") & (df["ativo"] == 1)]["descricao"]
        .dropna()
        .astype(str)
        .tolist()
    )
    return etapas, contratos


def run():
    st.header("📌 Catálogo de Status do Pipeline")

    df = load_status_df()

    df_etapas = df[df["tipo"] == "etapa"].copy()
    df_contr = df[df["tipo"] == "contratacao"].copy()

    st.subheader("Etapas do pipeline")
    st.write("Edite as descrições e o campo 'ativo'. Linhas em branco serão ignoradas.")

    et_cols = ["descricao", "ativo"]
    df_etapas_view = df_etapas[et_cols].reset_index(drop=True)
    edited_etapas = st.data_editor(
        df_etapas_view,
        num_rows="dynamic",
        use_container_width=True,
        key="status_etapas_editor",
    )

    st.subheader("Status de contratação")
    st.write("Edite as descrições e o campo 'ativo'. Linhas em branco serão ignoradas.")

    ct_cols = ["descricao", "ativo"]
    df_contr_view = df_contr[ct_cols].reset_index(drop=True)
    edited_contr = st.data_editor(
        df_contr_view,
        num_rows="dynamic",
        use_container_width=True,
        key="status_contr_editor",
    )

    if st.button("💾 Salvar catálogo de status"):
        rows = []

        def _collect_rows(edited_df, tipo_const):
            for _, r in edited_df.iterrows():
                desc = str(r.get("descricao", "") or "").strip()
                if not desc:
                    continue
                ativo_val = r.get("ativo", 1)
                try:
                    ativo_int = int(ativo_val)
                except Exception:
                    ativo_int = 1
                rows.append(
                    {
                        "tipo": tipo_const,
                        "codigo": _slugify(desc),
                        "descricao": desc,
                        "ativo": ativo_int,
                    }
                )

        _collect_rows(edited_etapas, "etapa")
        _collect_rows(edited_contr, "contratacao")

        if not rows:
            st.error("Nenhum status válido informado. Catálogo não foi alterado.")
        else:
            new_df = pd.DataFrame(rows)
            save_status_df(new_df)
            st.success("Catálogo de status do pipeline salvo com sucesso!")
            st.rerun()
