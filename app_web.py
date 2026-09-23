import streamlit as st
from leitor_pdf import extrair_dados
from regra_negocio import calcular_litros

import os
import tempfile


# ==================================================
# CONFIGURAÇÃO
# ==================================================

st.set_page_config(
    page_title="Calculadora de Litros",
    page_icon="📊",
    layout="centered"
)


# ==================================================
# TÍTULO
# ==================================================

st.title("📊 Calculadora de Litros")

st.write(
    "Envie o pedido ou orçamento em PDF "
    "para calcular automaticamente o total "
    "de litros vendidos."
)


# ==================================================
# LOCALIZA O EXCEL
# ==================================================

CAMINHO_EXCEL = os.path.join(
    os.path.dirname(__file__),
    "produtos.xlsx"
)


# ==================================================
# VERIFICA SE O EXCEL EXISTE
# ==================================================

if not os.path.exists(CAMINHO_EXCEL):

    st.error(
        "O arquivo produtos.xlsx não foi encontrado."
    )

    st.stop()


# ==================================================
# UPLOAD DO PDF
# ==================================================

arquivo_pdf = st.file_uploader(
    "📄 Selecione o pedido/orçamento em PDF",
    type=["pdf"]
)


# ==================================================
# PROCESSAMENTO
# ==================================================

if arquivo_pdf is not None:

    st.success(
        f"Arquivo carregado: {arquivo_pdf.name}"
    )

    if st.button(
        "🔎 CALCULAR LITROS",
        use_container_width=True
    ):

        caminho_pdf = None

        try:

            # ==========================================
            # SALVA O PDF TEMPORARIAMENTE
            # ==========================================

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as arquivo_temp:

                arquivo_temp.write(
                    arquivo_pdf.getbuffer()
                )

                caminho_pdf = arquivo_temp.name


            # ==========================================
            # LÊ O PDF
            # ==========================================

            with st.spinner(
                "Lendo o pedido..."
            ):

                dados_pdf = extrair_dados(
                    caminho_pdf
                )


            # ==========================================
            # VERIFICA SE ENCONTROU PRODUTOS
            # ==========================================

            if not dados_pdf:

                st.error(
                    "Nenhum produto foi identificado "
                    "no PDF."
                )

                st.stop()


            # ==========================================
            # CALCULA OS LITROS
            # ==========================================

            with st.spinner(
                "Calculando litros..."
            ):

                total_litros, detalhes = (
                    calcular_litros(
                        dados_pdf,
                        CAMINHO_EXCEL
                    )
                )


            # ==========================================
            # RESULTADO
            # ==========================================

            st.divider()

            st.subheader(
                "Resultado do Pedido"
            )


            # ==========================================
            # CARDS
            # ==========================================

            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "Produtos encontrados",
                    len(dados_pdf)
                )


            with col2:

                st.metric(
                    "Total de Litros",
                    f"{total_litros:,.2f} L"
                )


            # ==========================================
            # DETALHAMENTO
            # ==========================================

            st.divider()

            st.subheader(
                "Detalhamento"
            )

            st.dataframe(
                detalhes,
                use_container_width=True,
                hide_index=True
            )


            # ==========================================
            # PRODUTOS NÃO ENCONTRADOS
            # ==========================================

            nao_encontrados = detalhes[
                detalhes["Status"] != "OK"
            ]


            if not nao_encontrados.empty:

                st.warning(
                    f"{len(nao_encontrados)} "
                    "produto(s) não foram encontrados "
                    "na listagem de produtos."
                )


        except Exception as erro:

            st.error(
                "Ocorreu um erro durante o processamento."
            )

            st.exception(erro)


        finally:

            # ==========================================
            # APAGA O PDF TEMPORÁRIO
            # ==========================================

            if caminho_pdf:

                try:

                    os.remove(
                        caminho_pdf
                    )

                except:

                    pass