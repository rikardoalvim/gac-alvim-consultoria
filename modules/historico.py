import os
import streamlit as st

from .core import carregar_pareceres_log


def run():
    st.header("📁 Histórico de Pareceres")

    df = carregar_pareceres_log()
    if df.empty:
        st.info("Nenhum parecer registrado ainda.")
        return

    filtro = st.text_input("Filtrar por candidato, cliente ou cargo:")

    df_view = df.copy()
    if filtro.strip():
        f = filtro.strip().lower()
        df_view = df_view[
            df_view["nome"].str.lower().str.contains(f)
            | df_view["cliente"].str.lower().str.contains(f)
            | df_view["cargo"].str.lower().str.contains(f)
        ]

    st.write(f"Total de pareceres encontrados: {len(df_view)}")

    for _, row in df_view.sort_values("data_hora", ascending=False).iterrows():
        st.markdown(
            f"""
**Data/Hora:** {row['data_hora']}  
**Cliente:** {row['cliente']}  
**Cargo:** {row['cargo']}  
**Candidato:** {row['nome']}  
**Pretensão:** {row['pretensao']}  
**Formato:** {row['formato']}  
**ID Candidato:** {row.get('id_candidato', '')}  
**Etapa:** {row.get('status_etapa', '')}  
**Status contratação:** {row.get('status_contratacao', '')}  
**Motivo de declínio:** {row.get('motivo_decline', '')}  
**Arquivo:** `{row['caminho_arquivo']}`
"""
        )
        arq = row["caminho_arquivo"]
        if isinstance(arq, str) and os.path.exists(arq):
            with open(arq, "rb") as f:
                dados = f.read()
            st.download_button(
                "⬇️ Baixar arquivo",
                data=dados,
                file_name=os.path.basename(arq),
                mime="application/octet-stream",
                key=f"hist_{row['data_hora']}_{row['nome']}",
            )
        else:
            st.warning("Arquivo não encontrado.")
        st.markdown("---")
