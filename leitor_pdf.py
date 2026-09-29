import pdfplumber
import re


def extrair_dados(caminho_pdf):

    produtos = []

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text(
                x_tolerance=2,
                y_tolerance=3
            )

            if not texto:
                continue

            linhas = texto.splitlines()

            for i, linha in enumerate(linhas):

                # ==================================================
                # PROCURA O CÓDIGO DO PRODUTO
                # ==================================================

                match_codigo = re.match(
                    r"^\s*(\d{1,10})\s+",
                    linha
                )

                if not match_codigo:
                    continue

                codigo = match_codigo.group(1)

                # ==================================================
                # JUNTA A LINHA ATUAL COM AS PRÓXIMAS
                # ==================================================

                bloco = linha

                for j in range(1, 4):

                    if i + j < len(linhas):

                        bloco += " " + linhas[i + j]

                # ==================================================
                # PROCURA PREÇO E QUANTIDADE
                #
                # Exemplo:
                # R$283,91 40 PEC
                # ==================================================

                match_quantidade = re.search(
                    r"R\$\s*[\d.,]+\s+(\d+(?:[.,]\d+)?)\s+PEC",
                    bloco,
                    re.IGNORECASE
                )

                if not match_quantidade:
                    continue

                quantidade_texto = match_quantidade.group(1)

                quantidade_texto = (
                    quantidade_texto.replace(",", ".")
                )

                try:

                    quantidade = float(
                        quantidade_texto
                    )

                except ValueError:

                    continue

                # ==================================================
                # TENTA IDENTIFICAR A DESCRIÇÃO
                # ==================================================

                descricao = ""

                # Remove o código do início da linha
                restante = re.sub(
                    r"^\s*\d{1,10}\s+",
                    "",
                    linha
                ).strip()

                # Remove preço, quantidade e PEC da linha
                descricao = re.sub(
                    r"R\$\s*[\d.,]+\s+\d+(?:[.,]\d+)?\s+PEC.*$",
                    "",
                    restante,
                    flags=re.IGNORECASE
                ).strip()

                # Se a descrição ficou vazia, procura nas linhas seguintes
                if not descricao:

                    for j in range(1, 4):

                        if i + j >= len(linhas):
                            break

                        proxima_linha = linhas[i + j].strip()

                        # Ignora linhas vazias
                        if not proxima_linha:
                            continue

                        # Não utiliza outra linha que começa com código
                        if re.match(
                            r"^\s*\d{1,10}\s+",
                            proxima_linha
                        ):
                            break

                        # Se encontrou preço, para
                        if re.search(
                            r"R\$\s*[\d.,]+",
                            proxima_linha,
                            re.IGNORECASE
                        ):
                            break

                        descricao = proxima_linha

                        break

                # ==================================================
                # CRIA O PRODUTO
                # ==================================================

                produto = {
                    "codigo": codigo,
                    "descricao": descricao,
                    "quantidade": quantidade
                }

                # ==================================================
                # EVITA DUPLICIDADE
                # ==================================================

                if produto not in produtos:

                    produtos.append(
                        produto
                    )

    return produtos