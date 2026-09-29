import os
import streamlit as st

from leitor_pdf import extrair_dados
from regra_negocio import calcular_litros


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="CALCULE SUA LITRAGEM - ANALISTA SÁVIO",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CAMINHOS DOS ARQUIVOS
# ============================================================

PASTA_PROJETO = os.path.dirname(
    os.path.abspath(__file__)
)

CAMINHO_EXCEL = os.path.join(
    PASTA_PROJETO,
    "produtos.xlsx"
)

CAMINHO_LOGO = os.path.join(
    PASTA_PROJETO,
    "logo_suvinil.png"
)


# ============================================================
# CABEÇALHO
# ============================================================

col_logo, col_titulo = st.columns(
    [1, 5]
)

with col_logo:

    if os.path.exists(CAMINHO_LOGO):

        st.image(
            CAMINHO_LOGO,
            width=140
        )

    else:

        st.markdown(
            "# 🎨"
        )


with col_titulo:

    st.title(
        "CALCULE SUA LITRAGEM"
    )

    st.markdown(
        "### Analista Sávio"
    )

    st.caption(
        "Cálculo automático de litragem a partir de pedidos e orçamentos em PDF."
    )


st.divider()


# ============================================================
# VERIFICAÇÃO DO EXCEL
# ============================================================

if not os.path.exists(CAMINHO_EXCEL):

    st.error(
        "O arquivo produtos.xlsx não foi encontrado."
    )

    st.info(
        f"Verifique se o arquivo está nesta pasta: {PASTA_PROJETO}"
    )

    st.stop()


# ============================================================
# ENVIO DO PDF
# ============================================================

st.subheader(
    "📄 Envie o pedido ou orçamento"
)

arquivo_pdf = st.file_uploader(
    "Selecione um arquivo PDF",
    type=["pdf"]
)


# ============================================================
# PROCESSAMENTO
# ============================================================

if arquivo_pdf is not None:

    st.success(
        f"Arquivo selecionado: {arquivo_pdf.name}"
    )

    st.divider()

    if st.button(
        "CALCULAR LITRAGEM",
        type="primary",
        use_container_width=True
    ):

        caminho_pdf_temp = os.path.join(
            PASTA_PROJETO,
            "_pedido_temp.pdf"
        )

        try:

            # ==================================================
            # SALVA O PDF TEMPORARIAMENTE
            # ==================================================

            with open(
                caminho_pdf_temp,
                "wb"
            ) as arquivo:

                arquivo.write(
                    arquivo_pdf.getbuffer()
                )


            # ==================================================
            # LEITURA DO PDF
            # ==================================================

            with st.spinner(
                "Lendo o pedido..."
            ):

                dados_pdf = extrair_dados(
                    caminho_pdf_temp
                )


            # ==================================================
            # VERIFICA SE ENCONTROU PRODUTOS
            # ==================================================

            if not dados_pdf:

                st.warning(
                    "Nenhum produto foi identificado no PDF."
                )

                st.info(
                    "Verifique se o PDF possui os códigos, preços e quantidades esperados."
                )

                st.stop()


            # ==================================================
            # CALCULA A LITRAGEM
            # ==================================================

            with st.spinner(
                "Calculando a litragem..."
            ):

                total_litros, detalhes = calcular_litros(
                    dados_pdf,
                    CAMINHO_EXCEL
                )


            # ==================================================
            # RESULTADO PRINCIPAL
            # ==================================================

            st.success(
                "Cálculo realizado com sucesso!"
            )

            st.divider()

            st.subheader(
                "📊 Resultado"
            )


            # ==================================================
            # CARDS
            # ==================================================

            col1, col2, col3 = st.columns(
                3
            )

            with col1:

                st.metric(
                    "TOTAL DE LITROS",
                    f"{total_litros:,.2f} L"
                )


            with col2:

                st.metric(
                    "PRODUTOS IDENTIFICADOS",
                    len(dados_pdf)
                )


            with col3:

                produtos_ok = len(
                    detalhes[
                        detalhes["Status"] == "OK"
                    ]
                )

                st.metric(
                    "PRODUTOS CALCULADOS",
                    produtos_ok
                )


            st.divider()


            # ==================================================
            # DETALHAMENTO
            # ==================================================

            st.subheader(
                "🔎 Detalhamento dos produtos"
            )

            st.dataframe(
                detalhes,
                use_container_width=True,
                hide_index=True
            )


            # ==================================================
            # PRODUTOS NÃO ENCONTRADOS
            # ==================================================

            produtos_nao_encontrados = detalhes[
                detalhes["Status"] != "OK"
            ]


            if not produtos_nao_encontrados.empty:

                st.warning(
                    f"{len(produtos_nao_encontrados)} produto(s) precisam de verificação."
                )


            # ==================================================
            # DOWNLOAD DO RESULTADO
            # ==================================================

            st.divider()

            st.subheader(
                "⬇️ Exportar resultado"
            )

            csv = detalhes.to_csv(
                index=False,
                encoding="utf-8-sig"
            )

            st.download_button(
                label="BAIXAR RESULTADO EM CSV",
                data=csv,
                file_name="resultado_litragem.csv",
                mime="text/csv",
                use_container_width=True
            )


        except Exception as erro:

            st.error(
                "Ocorreu um erro durante o processamento."
            )

            st.exception(
                erro
            )


        finally:

            # ==================================================
            # REMOVE PDF TEMPORÁRIO
            # ==================================================

            if os.path.exists(
                caminho_pdf_temp
            ):

                try:

                    os.remove(
                        caminho_pdf_temp
                    )

                except Exception:

                    pass


# ============================================================
# MENSAGEM INICIAL
# ============================================================

else:

    st.info(
        "Selecione um pedido ou orçamento em PDF para começar."
    )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "CALCULE SUA LITRAGEM • Analista Sávio"
)