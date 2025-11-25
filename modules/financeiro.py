from datetime import datetime

import streamlit as st

from .core import (
    carregar_clientes,
    carregar_fin_os,
    registrar_fin_os,
    LOG_FIN_OS,
    carregar_fin_orc,
    registrar_fin_orc,
    LOG_FIN_ORC,
    carregar_fin_nf,
    registrar_fin_nf,
    LOG_FIN_NF,
)


def _select_cliente():
    df_cli = carregar_clientes()
    if df_cli.empty:
        st.warning("Cadastre clientes para vincular lançamentos financeiros.")
        return "", ""
    op_cli = {int(row["id_cliente"]): row["nome_cliente"] for _, row in df_cli.iterrows()}
    id_cli_sel = st.selectbox(
        "Cliente:",
        options=list(op_cli.keys()),
        format_func=lambda x: op_cli[x],
    )
    return str(id_cli_sel), op_cli[id_cli_sel]


def run():
    st.header("💼 Financeiro - Alvim Consultoria")

    aba = st.tabs([
        "📄 Ordens de Serviço",
        "📑 Orçamentos",
        "🧾 Notas Fiscais",
    ])

    # ============================
    # OS
    # ============================
    with aba[0]:
        st.subheader("📄 Ordens de Serviço (OS)")

        id_cliente, nome_cliente = _select_cliente()

        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_area("Descrição da OS", height=100)
            tipo_servico = st.text_input("Tipo de serviço (ex.: Consultoria HCM, Implantação Sapiens)")
        with col2:
            data_emissao = st.date_input("Data de emissão", value=datetime.today()).strftime("%Y-%m-%d")
            data_exec = st.date_input("Data de execução (prevista/real)", value=datetime.today()).strftime("%Y-%m-%d")
            valor = st.text_input("Valor (ex.: 3.500,00)")
            status = st.selectbox(
                "Status",
                ["Aberta", "Em andamento", "Finalizada", "Cancelada"],
            )

        obs_os = st.text_area("Observações da OS", height=70)

        if st.button("💾 Registrar OS"):
            if not id_cliente or not descricao.strip():
                st.error("Selecione o cliente e informe a descrição.")
            else:
                novo_id = registrar_fin_os(
                    id_cliente=id_cliente,
                    nome_cliente=nome_cliente,
                    descricao=descricao.strip(),
                    tipo_servico=tipo_servico.strip(),
                    data_emissao=data_emissao,
                    data_execucao=data_exec,
                    valor=valor.strip(),
                    status=status,
                    observacoes=obs_os.strip(),
                )
                st.success(f"OS registrada com ID {novo_id}.")
                st.rerun()

        st.markdown("---")
        st.subheader("📋 OS cadastradas")

        df_os = carregar_fin_os()
        if df_os.empty:
            st.info("Nenhuma OS registrada.")
        else:
            df_os = df_os.sort_values("id_os")
            edited_os = st.data_editor(
                df_os,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "id_os": st.column_config.Column("ID OS", disabled=True),
                },
                key="os_editor",
            )
            if st.button("💾 Salvar alterações das OS"):
                try:
                    edited_os.to_csv(LOG_FIN_OS, sep=";", index=False, encoding="utf-8")
                    st.success("OS atualizadas com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar OS: {e}")

    # ============================
    # ORÇAMENTOS
    # ============================
    with aba[1]:
        st.subheader("📑 Orçamentos")

        id_cliente_o, nome_cliente_o = _select_cliente()

        col1, col2 = st.columns(2)
        with col1:
            desc_orc = st.text_area("Descrição do orçamento", height=100)
        with col2:
            data_emissao_o = st.date_input("Data de emissão", value=datetime.today()).strftime("%Y-%m-%d")
            validade = st.date_input("Validade do orçamento", value=datetime.today()).strftime("%Y-%m-%d")
            valor_o = st.text_input("Valor proposto (ex.: 4.800,00)")
            status_o = st.selectbox(
                "Status",
                ["Enviado", "Aprovado", "Rejeitado", "Em negociação"],
            )

        obs_orc = st.text_area("Observações do orçamento", height=70)

        if st.button("💾 Registrar orçamento"):
            if not id_cliente_o or not desc_orc.strip():
                st.error("Selecione o cliente e informe a descrição.")
            else:
                novo_id = registrar_fin_orc(
                    id_cliente=id_cliente_o,
                    nome_cliente=nome_cliente_o,
                    descricao=desc_orc.strip(),
                    data_emissao=data_emissao_o,
                    validade=validade,
                    valor=valor_o.strip(),
                    status=status_o,
                    observacoes=obs_orc.strip(),
                )
                st.success(f"Orçamento registrado com ID {novo_id}.")
                st.rerun()

        st.markdown("---")
        st.subheader("📋 Orçamentos registrados")

        df_orc = carregar_fin_orc()
        if df_orc.empty:
            st.info("Nenhum orçamento registrado.")
        else:
            df_orc = df_orc.sort_values("id_orc")
            edited_orc = st.data_editor(
                df_orc,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "id_orc": st.column_config.Column("ID Orçamento", disabled=True),
                },
                key="orc_editor",
            )
            if st.button("💾 Salvar alterações dos orçamentos"):
                try:
                    edited_orc.to_csv(LOG_FIN_ORC, sep=";", index=False, encoding="utf-8")
                    st.success("Orçamentos atualizados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar orçamentos: {e}")

    # ============================
    # NOTAS FISCAIS
    # ============================
    with aba[2]:
        st.subheader("🧾 Notas Fiscais")

        id_cliente_nf, nome_cliente_nf = _select_cliente()

        col1, col2 = st.columns(2)
        with col1:
            numero_nf = st.text_input("Número da NF")
            data_nf = st.date_input("Data de emissão da NF", value=datetime.today()).strftime("%Y-%m-%d")
        with col2:
            valor_nf = st.text_input("Valor (ex.: 5.200,00)")
        desc_nf = st.text_area("Descrição / Discriminação dos serviços", height=80)
        obs_nf = st.text_area("Observações da NF", height=60)

        if st.button("💾 Registrar NF"):
            if not id_cliente_nf or not numero_nf.strip():
                st.error("Selecione o cliente e informe o número da NF.")
            else:
                novo_id = registrar_fin_nf(
                    id_cliente=id_cliente_nf,
                    nome_cliente=nome_cliente_nf,
                    numero_nf=numero_nf.strip(),
                    data_emissao=data_nf,
                    valor=valor_nf.strip(),
                    descricao=desc_nf.strip(),
                    observacoes=obs_nf.strip(),
                )
                st.success(f"NF registrada com ID {novo_id}.")
                st.rerun()

        st.markdown("---")
        st.subheader("📋 Notas Fiscais registradas")

        df_nf = carregar_fin_nf()
        if df_nf.empty:
            st.info("Nenhuma NF registrada.")
        else:
            df_nf = df_nf.sort_values("id_nf")
            edited_nf = st.data_editor(
                df_nf,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "id_nf": st.column_config.Column("ID NF", disabled=True),
                },
                key="nf_editor",
            )
            if st.button("💾 Salvar alterações das NFs"):
                try:
                    edited_nf.to_csv(LOG_FIN_NF, sep=";", index=False, encoding="utf-8")
                    st.success("Notas fiscais atualizadas com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar NFs: {e}")