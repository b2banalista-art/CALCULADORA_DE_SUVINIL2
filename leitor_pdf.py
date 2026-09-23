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

                # Procura o código do produto
                # no começo da linha
                match_codigo = re.match(
                    r"^\s*(\d{1,10})\s+",
                    linha
                )

                if not match_codigo:
                    continue

                codigo = match_codigo.group(1)

                # Junta a linha atual com as próximas
                # para lidar com descrições quebradas
                bloco = linha

                for j in range(1, 4):

                    if i + j < len(linhas):

                        bloco += " " + linhas[i + j]

                # Procura o preço e a quantidade
                #
                # Exemplo:
                # R$283,91 40 PEC
                #
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

                produto = {
                    "codigo": codigo,
                    "quantidade": quantidade
                }

                # Evita duplicidade
                if produto not in produtos:

                    produtos.append(produto)

    return produtos