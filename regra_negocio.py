import pandas as pd


def normalizar_codigo(codigo):

    if pd.isna(codigo):

        return ""

    codigo = str(codigo).strip()

    # Corrige códigos que o Excel transforma em 123456.0
    if codigo.endswith(".0"):

        codigo = codigo[:-2]

    return codigo


def calcular_litros(dados_pdf, caminho_excel):

    # ==========================================================
    # LÊ O ARQUIVO EXCEL
    # ==========================================================

    df = pd.read_excel(
        caminho_excel
    )

    # ==========================================================
    # COLUNA A = CÓDIGO
    # COLUNA C = LITROS
    # ==========================================================

    coluna_codigo = df.columns[0]

    coluna_litros = df.columns[2]

    # ==========================================================
    # PADRONIZA OS CÓDIGOS DO EXCEL
    # ==========================================================

    df["CODIGO_PADRONIZADO"] = (
        df[coluna_codigo]
        .apply(normalizar_codigo)
    )

    total_litros = 0

    detalhes = []

    # ==========================================================
    # PERCORRE OS PRODUTOS ENCONTRADOS NO PDF
    # ==========================================================

    for produto in dados_pdf:

        codigo = normalizar_codigo(
            produto["codigo"]
        )

        descricao = produto.get(
            "descricao",
            ""
        )

        quantidade = produto["quantidade"]

        # ======================================================
        # PROCURA O CÓDIGO NA COLUNA A
        # ======================================================

        resultado = df[
            df["CODIGO_PADRONIZADO"] == codigo
        ]

        # ======================================================
        # CÓDIGO NÃO ENCONTRADO
        # ======================================================

        if resultado.empty:

            detalhes.append({
                "Código": codigo,
                "Descrição": descricao,
                "Quantidade": quantidade,
                "Litros por unidade": None,
                "Total Litros": None,
                "Status": "Não encontrado"
            })

            continue

        # ======================================================
        # PEGA A LITRAGEM DA COLUNA C
        # ======================================================

        litros = resultado.iloc[0][
            coluna_litros
        ]

        try:

            litros = float(
                litros
            )

        except (
            ValueError,
            TypeError
        ):

            detalhes.append({
                "Código": codigo,
                "Descrição": descricao,
                "Quantidade": quantidade,
                "Litros por unidade": None,
                "Total Litros": None,
                "Status": "Litragem inválida"
            })

            continue

        # ======================================================
        # CÁLCULO
        # ======================================================

        total_produto = (
            quantidade * litros
        )

        total_litros += total_produto

        # ======================================================
        # DETALHES
        # ======================================================

        detalhes.append({
            "Código": codigo,
            "Descrição": descricao,
            "Quantidade": quantidade,
            "Litros por unidade": litros,
            "Total Litros": total_produto,
            "Status": "OK"
        })

    return (
        total_litros,
        pd.DataFrame(detalhes)
    )