import os
import pandas as pd
import streamlit as st

# Arquivo de status na raiz do projeto (mesmo nível do parecer_app.py)
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(MODULE_DIR, ".."))
STATUS_FILE = os.path.join(ROOT_DIR, "status_pipeline.csv")

# -------------------------------------------------
# CSS LOCAL – deixa títulos em cinza e quadros bonitos
# -------------------------------------------------
LOCAL_CSS = """
<style>
.status-wrapper {
    display: flex;
    gap: 1.2rem;
    align-items: flex-start;
    margin-top: 0.5rem;
}

/* card glass dos formulários de status */
.status-card {
    flex: 1 1 0;
    padding: 0.85rem 1.0rem 1.0rem 1.0rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.92);
    box-shadow: 0 18px 45px rgba(15,23,42,0.20);
    border: 1px solid rgba(226,232,240,0.9);
}

/* título interno do card em cinza */
.status-title {
    color: #374151 !important;
    font-weight: 700;
    font-size: 0.98rem;
    margin-bottom: 0.35rem;
}

/* separador suave */
.status-divider {
    height: 1px;
    background: rgba(148,163,184,0.45);
    margin: 0.35rem 0 0.45rem 0;
    border-radius: 999px;
}

/* tabelas reaproveitam o CSS global <table>, só suavizamos fontes */
.status-table-wrapper {
    margin-top: 0.4rem;
}
.status-table-wrapper table th,
.status-table-wrapper table td {
    font-size: 0.83rem;
}

/* textos cinza dentro dessa página */
.status-card label {
    color: #374151 !important;
}
.status-card p, .status-card span {
    color: #374151 !important;
}
</style>
"""


# -------------------------------------------------
# Defaults
# -------------------------------------------------
DEFAULT_ETAPAS = [
    ("TRIAGEM", "Triagem", 1),
    ("ENTREVISTA", "Entrevista", 2),
    ("FINALISTA", "Finalista", 3),
    ("NAO_SEGUIU", "Não seguiu processo", 99),
]

DEFAULT_CONTRAT = [
    ("PENDENTE", "Pendente", 1),
    ("APROVADO", "Aprovado / Contratado", 2),
    ("REPROVADO", "Reprovado", 3),
    ("DESISTIU", "Desistiu", 4),
]


# -------------------------------------------------
# Load / Save
# -------------------------------------------------
def _create_default_df() -> pd.DataFrame:
    rows = []
    for cod, desc, ordem in DEFAULT_ETAPAS:
        rows.append(
            {
                "tipo": "ETAPA",
                "codigo": cod,
                "descricao": desc,
                "ordem": ordem,
                "ativo": 1,
            }
        )
    for cod, desc, ordem in DEFAULT_CONTRAT:
        rows.append(
            {
                "tipo": "CONTRATACAO",
                "codigo": cod,
                "descricao": desc,
                "ordem": ordem,
                "ativo": 1,
            }
        )
    return pd.DataFrame(rows)


def load_status_df() -> pd.DataFrame:
    """Carrega status do CSV, criando defaults se não existir."""
    if not os.path.exists(STATUS_FILE):
        df = _create_default_df()
        df.to_csv(STATUS_FILE, index=False, encoding="utf-8")
        return df

    df = pd.read_csv(STATUS_FILE, dtype=str).fillna("")
    for col in ["tipo", "codigo", "descricao"]:
        if col not in df.columns:
            df[col] = ""

    if "ordem" not in df.columns:
        df["ordem"] = "0"
    if "ativo" not in df.columns:
        df["ativo"] = "1"

    df["ordem"] = df["ordem"].replace("", "0").astype(int)
    df["ativo"] = df["ativo"].replace("", "1").astype(int)

    return df


def save_status_df(df: pd.DataFrame) -> None:
    df.to_csv(STATUS_FILE, index=False, encoding="utf-8")


# -------------------------------------------------
# API usada pelo pipeline_mod
# -------------------------------------------------
def get_status_lists():
    """
    Retorna (lista_etapas, lista_contratacao) apenas com registros ativos.
    Usado no módulo pipeline_mod.
    """
    df = load_status_df()

    etapas = (
        df[(df["tipo"] == "ETAPA") & (df["ativo"] == 1)]
        .sort_values("ordem")
        .get("descricao", pd.Series(dtype=str))
        .tolist()
    )

    contratacao = (
        df[(df["tipo"] == "CONTRATACAO") & (df["ativo"] == 1)]
        .sort_values("ordem")
        .get("descricao", pd.Series(dtype=str))
        .tolist()
    )

    # fallback se estiverem vazios
    if not etapas:
        etapas = [d for _, d, _ in DEFAULT_ETAPAS]
    if not contratacao:
        contratacao = [d for _, d, _ in DEFAULT_CONTRAT]

    return etapas, contratacao


# -------------------------------------------------
# Render de tabela glass (mesmo padrão das outras)
# -------------------------------------------------
def render_tabela_html(df_tipo: pd.DataFrame, titulo: str):
    if df_tipo.empty:
        st.info(f"Nenhum status cadastrado em **{titulo}**.")
        return

    df_tipo = df_tipo.sort_values("ordem").copy()
    df_tipo["Ativo"] = df_tipo["ativo"].apply(lambda x: "Sim" if int(x) == 1 else "Não")

    html = ["<div class='status-table-wrapper'><table>"]
    # Cabeçalho
    html.append("<thead><tr>")
    for h in ["Código", "Descrição", "Ordem", "Ativo"]:
        html.append(f"<th>{h}</th>")
    html.append("</tr></thead>")

    # Corpo
    html.append("<tbody>")
    for _, row in df_tipo.iterrows():
        html.append("<tr>")
        html.append(f"<td>{row['codigo']}</td>")
        html.append(f"<td>{row['descricao']}</td>")
        html.append(f"<td>{row['ordem']}</td>")
        html.append(f"<td>{row['Ativo']}</td>")
        html.append("</tr>")
    html.append("</tbody></table></div>")

    st.markdown("".join(html), unsafe_allow_html=True)


# -------------------------------------------------
# UPsert helpers
# -------------------------------------------------
def upsert_status(
    df: pd.DataFrame,
    tipo: str,
    codigo: str,
    descricao: str,
    ordem: int,
    ativo: bool,
) -> pd.DataFrame:
    """Insere ou atualiza um status (ETAPA/CONTRATACAO) baseado em tipo+codigo."""
    codigo = codigo.strip().upper()
    descricao = descricao.strip()

    if not codigo or not descricao:
        st.error("Informe código e descrição.")
        return df

    mask = (df["tipo"] == tipo) & (df["codigo"] == codigo)
    if not mask.any():
        # novo
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    [
                        {
                            "tipo": tipo,
                            "codigo": codigo,
                            "descricao": descricao,
                            "ordem": int(ordem),
                            "ativo": 1 if ativo else 0,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    else:
        # update
        df.loc[mask, "descricao"] = descricao
        df.loc[mask, "ordem"] = int(ordem)
        df.loc[mask, "ativo"] = 1 if ativo else 0

    save_status_df(df)
    st.success("Status salvo/atualizado com sucesso.")
    return df


def delete_status(df: pd.DataFrame, tipo: str, codigo: str) -> pd.DataFrame:
    codigo = codigo.strip().upper()
    mask = (df["tipo"] == tipo) & (df["codigo"] == codigo)
    if not mask.any():
        st.warning("Código não encontrado para exclusão.")
        return df

    df = df[~mask].reset_index(drop=True)
    save_status_df(df)
    st.success("Status excluído.")
    return df


# -------------------------------------------------
# UI principal
# -------------------------------------------------
def run():
    st.markdown(LOCAL_CSS, unsafe_allow_html=True)
    st.header("📌 Cadastro de Status do Pipeline")

    df = load_status_df()

    st.write(
        "Configure aqui as **Etapas do processo** e os **Status de contratação** "
        "que serão usados no módulo de Pipeline."
    )

    # Layout side-by-side
    st.markdown("<div class='status-wrapper'>", unsafe_allow_html=True)

    # ---------------------- ETAPAS ----------------------
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='status-card'>", unsafe_allow_html=True)
        st.markdown("<div class='status-title'>Etapas do processo</div>", unsafe_allow_html=True)
        st.markdown("<div class='status-divider'></div>", unsafe_allow_html=True)

        df_etapas = df[df["tipo"] == "ETAPA"].copy()

        st.caption("Cadastro / edição")
        cod_etapa = st.text_input("Código da etapa (interno)", key="st_cod_etapa")
        desc_etapa = st.text_input("Descrição da etapa", key="st_desc_etapa")
        ordem_etapa = st.number_input(
            "Ordem de exibição",
            min_value=1,
            max_value=999,
            value=1,
            step=1,
            key="st_ord_etapa",
        )
        ativo_etapa = st.checkbox("Ativo", value=True, key="st_ativo_etapa")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Salvar etapa", key="btn_save_etapa", use_container_width=True):
                df = upsert_status(
                    df,
                    tipo="ETAPA",
                    codigo=cod_etapa,
                    descricao=desc_etapa,
                    ordem=int(ordem_etapa),
                    ativo=ativo_etapa,
                )
                df_etapas = df[df["tipo"] == "ETAPA"].copy()

        with c2:
            if st.button("🗑 Excluir etapa", key="btn_del_etapa", use_container_width=True):
                if not cod_etapa.strip():
                    st.error("Informe o código da etapa que deseja excluir.")
                else:
                    df = delete_status(df, "ETAPA", cod_etapa)
                    df_etapas = df[df["tipo"] == "ETAPA"].copy()

        st.markdown("<br/>", unsafe_allow_html=True)
        st.caption("Etapas cadastradas")
        render_tabela_html(df_etapas, "Etapas")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- STATUS DE CONTRATAÇÃO ----------------
    with col2:
        st.markdown("<div class='status-card'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='status-title'>Status de contratação</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='status-divider'></div>", unsafe_allow_html=True)

        df_contr = df[df["tipo"] == "CONTRATACAO"].copy()

        st.caption("Cadastro / edição")
        cod_contr = st.text_input("Código do status", key="st_cod_contr")
        desc_contr = st.text_input("Descrição do status", key="st_desc_contr")
        ordem_contr = st.number_input(
            "Ordem de exibição",
            min_value=1,
            max_value=999,
            value=1,
            step=1,
            key="st_ord_contr",
        )
        ativo_contr = st.checkbox("Ativo", value=True, key="st_ativo_contr")

        d1, d2 = st.columns(2)
        with d1:
            if st.button("💾 Salvar status", key="btn_save_contr", use_container_width=True):
                df = upsert_status(
                    df,
                    tipo="CONTRATACAO",
                    codigo=cod_contr,
                    descricao=desc_contr,
                    ordem=int(ordem_contr),
                    ativo=ativo_contr,
                )
                df_contr = df[df["tipo"] == "CONTRATACAO"].copy()

        with d2:
            if st.button("🗑 Excluir status", key="btn_del_contr", use_container_width=True):
                if not cod_contr.strip():
                    st.error("Informe o código do status que deseja excluir.")
                else:
                    df = delete_status(df, "CONTRATACAO", cod_contr)
                    df_contr = df[df["tipo"] == "CONTRATACAO"].copy()

        st.markdown("<br/>", unsafe_allow_html=True)
        st.caption("Status cadastrados")
        render_tabela_html(df_contr, "Status de contratação")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
