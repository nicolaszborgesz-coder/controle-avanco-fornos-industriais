
import csv
import json
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

ROOT = Path(__file__).resolve().parent.parent

PASTA_DADOS = ROOT / "dados"
PASTA_RELATORIOS = ROOT / "relatorios"
PASTA_DASHBOARD = ROOT / "dashboard"

ARQUIVO_CSV = PASTA_DADOS / "avanco.csv"
ARQUIVO_EXCEL = PASTA_RELATORIOS / "controle_avanco.xlsx"
ARQUIVO_GRAFICO = PASTA_RELATORIOS / "grafico_avanco.png"
ARQUIVO_JSON = PASTA_DASHBOARD / "data.json"

AZUL = "244062"
BRANCO = "FFFFFF"
VERDE = "C6EFCE"
AMARELO = "FFEB9C"
VERMELHO = "FFC7CE"
CINZA = "D9E2F3"


# ==========================================================
# CURVA S FICTÍCIA PARA DEMONSTRAÇÃO
# ==========================================================

def carregar_curva_s():

    return {
        "semanas": [
            "01", "02", "03", "04",
            "05", "06", "07", "08"
        ],

        "planejado": [
            5, 12, 20, 28,
            38, 45, 48, 50.25
        ],

        "realizado": [
            3, 8, 14, 20,
            28, 34, 38, 39.80
        ]
    }


# ==========================================================
# LEITURA E VALIDAÇÃO DO CSV
# ==========================================================

def carregar_dados():

    if not ARQUIVO_CSV.exists():
        raise FileNotFoundError(
            f"Arquivo CSV não encontrado: {ARQUIVO_CSV}"
        )

    with open(
        ARQUIVO_CSV,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        amostra = arquivo.read(4096)
        arquivo.seek(0)

        # Detecta automaticamente vírgula ou ponto e vírgula
        try:
            delimitador = csv.Sniffer().sniff(
                amostra,
                delimiters=",;"
            ).delimiter

        except csv.Error:
            delimitador = ","

        leitor = csv.DictReader(
            arquivo,
            delimiter=delimitador
        )

        if not leitor.fieldnames:
            raise ValueError(
                "O arquivo CSV está vazio ou sem cabeçalho."
            )

        # Remove espaços e caracteres BOM dos cabeçalhos
        leitor.fieldnames = [
            nome.strip().replace("\ufeff", "").lower()
            for nome in leitor.fieldnames
        ]

        colunas_obrigatorias = {
            "etapa",
            "peso",
            "planejado",
            "realizado"
        }

        colunas_encontradas = set(leitor.fieldnames)

        if not colunas_obrigatorias.issubset(
            colunas_encontradas
        ):
            raise ValueError(
                "Cabeçalhos encontrados: "
                + str(leitor.fieldnames)
                + "\nO CSV precisa conter: "
                + "etapa, peso, planejado e realizado."
            )

        dados = []

        for numero_linha, linha in enumerate(leitor, start=2):

            if not linha.get("etapa"):
                continue

            try:

                etapa = linha["etapa"].strip()

                peso = float(
                    linha["peso"].strip().replace(",", ".")
                )

                planejado = float(
                    linha["planejado"].strip().replace(",", ".")
                )

                realizado = float(
                    linha["realizado"].strip().replace(",", ".")
                )

            except (ValueError, AttributeError, TypeError):
                raise ValueError(
                    f"Erro ao interpretar os números "
                    f"na linha {numero_linha} do CSV."
                )

            if not etapa:
                raise ValueError(
                    f"Nome de etapa vazio na linha {numero_linha}."
                )

            if peso <= 0:
                raise ValueError(
                    f"O peso da etapa '{etapa}' deve ser maior que zero."
                )

            if not 0 <= planejado <= 100:
                raise ValueError(
                    f"O planejado da etapa '{etapa}' "
                    "deve estar entre 0 e 100."
                )

            if not 0 <= realizado <= 100:
                raise ValueError(
                    f"O realizado da etapa '{etapa}' "
                    "deve estar entre 0 e 100."
                )

            dados.append({
                "etapa": etapa,
                "peso": peso,
                "planejado": planejado,
                "realizado": realizado
            })

    if not dados:
        raise ValueError(
            "Nenhuma etapa foi encontrada no arquivo CSV."
        )

    nomes = [item["etapa"].lower() for item in dados]

    if len(nomes) != len(set(nomes)):
        raise ValueError(
            "Existem etapas duplicadas no arquivo CSV."
        )

    soma_pesos = sum(item["peso"] for item in dados)

    if round(soma_pesos, 2) != 100:
        raise ValueError(
            f"A soma dos pesos precisa ser 100%. "
            f"Valor encontrado: {soma_pesos:.2f}%."
        )

    return dados


# ==========================================================
# CÁLCULO DOS INDICADORES
# ==========================================================

def calcular_indicadores(dados):

    planejado = sum(
        item["peso"] * item["planejado"] / 100
        for item in dados
    )

    realizado = sum(
        item["peso"] * item["realizado"] / 100
        for item in dados
    )

    desvio = realizado - planejado

    total_etapas = len(dados)

    concluidas = sum(
        1 for item in dados
        if item["realizado"] >= 100
    )

    return {
        "planejado": round(planejado, 2),
        "realizado": round(realizado, 2),
        "desvio": round(desvio, 2),
        "total_etapas": total_etapas,
        "totalEtapas": total_etapas,
        "concluidas": concluidas
    }


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

def preparar_etapas(dados):

    etapas = []

    for item in dados:

        desvio = item["realizado"] - item["planejado"]

        contribuicao = (
            item["peso"] * item["realizado"] / 100
        )

        etapas.append({
            "etapa": item["etapa"],
            "peso": item["peso"],
            "planejado": item["planejado"],
            "realizado": item["realizado"],
            "desvio": round(desvio, 2),
            "contribuicao": round(contribuicao, 2)
        })

    return etapas


# ==========================================================
# GERAÇÃO DA PLANILHA EXCEL
# ==========================================================

def gerar_excel(indicadores, etapas, curva):

    wb = Workbook()

    # ------------------------------------------------------
    # ABA RESUMO
    # ------------------------------------------------------

    ws = wb.active
    ws.title = "Resumo"

    ws.merge_cells("A1:D1")
    ws["A1"] = "CONTROLE DE AVANÇO FÍSICO"
    ws["A1"].font = Font(
        bold=True,
        color=BRANCO,
        size=16
    )
    ws["A1"].fill = PatternFill(
        "solid",
        fgColor=AZUL
    )
    ws["A1"].alignment = Alignment(
        horizontal="center"
    )

    ws.append([])
    ws.append(["INDICADOR", "RESULTADO"])

    indicadores_excel = [
        ["Avanço Planejado", indicadores["planejado"] / 100],
        ["Avanço Realizado", indicadores["realizado"] / 100],
        ["Desvio", indicadores["desvio"] / 100],
        ["Total de Etapas", indicadores["totalEtapas"]],
        ["Etapas Concluídas", indicadores["concluidas"]]
    ]

    for linha in indicadores_excel:
        ws.append(linha)

    for celula in ws[3]:
        celula.fill = PatternFill(
            "solid",
            fgColor=AZUL
        )
        celula.font = Font(
            bold=True,
            color=BRANCO
        )

    for linha in range(4, 7):
        ws[f"B{linha}"].number_format = "0.00%"

    for coluna in ws.columns:
        tamanho = max(
            len(str(celula.value or ""))
            for celula in coluna
        )
        ws.column_dimensions[
            get_column_letter(coluna[0].column)
        ].width = max(tamanho + 4, 18)

    ws.freeze_panes = "A4"

    # Gráfico de indicadores
    grafico = BarChart()
    grafico.title = "Planejado x Realizado"
    grafico.y_axis.title = "Percentual"
    grafico.x_axis.title = "Indicadores"
    grafico.style = 10

    valores = Reference(
        ws,
        min_col=2,
        min_row=3,
        max_row=5
    )

    categorias = Reference(
        ws,
        min_col=1,
        min_row=4,
        max_row=5
    )

    grafico.add_data(
        valores,
        titles_from_data=True
    )

    grafico.set_categories(categorias)
    grafico.height = 7
    grafico.width = 14

    ws.add_chart(grafico, "D3")

    # ------------------------------------------------------
    # ABA ETAPAS
    # ------------------------------------------------------

    ws_etapas = wb.create_sheet("Etapas")

    cabecalho = [
        "Etapa",
        "Peso (%)",
        "Planejado (%)",
        "Realizado (%)",
        "Desvio (p.p.)",
        "Contribuição (%)"
    ]

    ws_etapas.append(cabecalho)

    for item in etapas:

        ws_etapas.append([
            item["etapa"],
            item["peso"],
            item["planejado"],
            item["realizado"],
            item["desvio"],
            item["contribuicao"]
        ])

    for celula in ws_etapas[1]:

        celula.fill = PatternFill(
            "solid",
            fgColor=AZUL
        )

        celula.font = Font(
            bold=True,
            color=BRANCO
        )

        celula.alignment = Alignment(
            horizontal="center"
        )

    for linha in range(2, ws_etapas.max_row + 1):

        ws_etapas[f"E{linha}"].number_format = '0.00'

        valor = ws_etapas[f"E{linha}"].value

        if valor > 0:
            cor = VERDE
        elif valor < 0:
            cor = VERMELHO
        else:
            cor = AMARELO

        ws_etapas[f"E{linha}"].fill = PatternFill(
            "solid",
            fgColor=cor
        )

    larguras = [32, 15, 20, 20, 18, 22]

    for indice, largura in enumerate(larguras, start=1):
        ws_etapas.column_dimensions[
            get_column_letter(indice)
        ].width = largura

    ws_etapas.freeze_panes = "A2"
    ws_etapas.auto_filter.ref = ws_etapas.dimensions

    # ------------------------------------------------------
    # ABA CURVA S
    # ------------------------------------------------------

    ws_curva = wb.create_sheet("Curva S")

    ws_curva.append([
        "Semana",
        "Planejado (%)",
        "Realizado (%)"
    ])

    for i in range(len(curva["semanas"])):

        ws_curva.append([
            curva["semanas"][i],
            curva["planejado"][i],
            curva["realizado"][i]
        ])

    for celula in ws_curva[1]:

        celula.fill = PatternFill(
            "solid",
            fgColor=AZUL
        )

        celula.font = Font(
            bold=True,
            color=BRANCO
        )

    grafico_linha = LineChart()

    grafico_linha.title = "Curva S - Evolução do Avanço"
    grafico_linha.y_axis.title = "Avanço (%)"
    grafico_linha.x_axis.title = "Semana"
    grafico_linha.style = 13

    valores = Reference(
        ws_curva,
        min_col=2,
        max_col=3,
        min_row=1,
        max_row=ws_curva.max_row
    )

    categorias = Reference(
        ws_curva,
        min_col=1,
        min_row=2,
        max_row=ws_curva.max_row
    )

    grafico_linha.add_data(
        valores,
        titles_from_data=True
    )

    grafico_linha.set_categories(categorias)

    grafico_linha.height = 10
    grafico_linha.width = 20

    ws_curva.add_chart(
        grafico_linha,
        "E2"
    )

    ws_curva.column_dimensions["A"].width = 15
    ws_curva.column_dimensions["B"].width = 22
    ws_curva.column_dimensions["C"].width = 22

    # Salva arquivo
    wb.save(ARQUIVO_EXCEL)


# ==========================================================
# GERAÇÃO DO GRÁFICO PNG
# ==========================================================

def gerar_grafico(indicadores):

    nomes = [
        "Planejado",
        "Realizado"
    ]

    valores = [
        indicadores["planejado"],
        indicadores["realizado"]
    ]

    plt.figure(figsize=(9, 5))

    barras = plt.bar(
        nomes,
        valores
    )

    plt.title(
        "Controle de Avanço Físico"
    )

    plt.ylabel(
        "Percentual (%)"
    )

    plt.ylim(0, 100)

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    for barra, valor in zip(barras, valores):

        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 1,
            f"{valor:.2f}%",
            ha="center"
        )

    plt.tight_layout()

    plt.savefig(
        ARQUIVO_GRAFICO,
        dpi=150
    )

    plt.close()


# ==========================================================
# GERAÇÃO DO JSON PARA O DASHBOARD
# ==========================================================

def gerar_json(indicadores, etapas, curva):

    dados_json = {
        "atualizado_em": datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        ),

        "resumo": indicadores,

        "etapas": etapas,

        "curva": curva
    }

    with open(
        ARQUIVO_JSON,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados_json,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

def main():

    print("=" * 45)
    print(" CONTROLE DE AVANÇO FÍSICO")
    print("=" * 45)

    # Cria pastas caso não existam
    PASTA_DADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True
    )

    PASTA_DASHBOARD.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nLendo arquivo CSV...")

    dados = carregar_dados()

    print("Calculando indicadores...")

    indicadores = calcular_indicadores(dados)

    etapas = preparar_etapas(dados)

    curva = carregar_curva_s()

    print("Gerando planilha Excel...")

    gerar_excel(
        indicadores,
        etapas,
        curva
    )

    print("Gerando gráfico PNG...")

    gerar_grafico(
        indicadores
    )

    print("Gerando dados do dashboard...")

    gerar_json(
        indicadores,
        etapas,
        curva
    )

    print("\n" + "=" * 45)
    print(" PROCESSAMENTO CONCLUÍDO!")
    print("=" * 45)

    print(
        f"\nPlanejado: "
        f"{indicadores['planejado']:.2f}%"
    )

    print(
        f"Realizado: "
        f"{indicadores['realizado']:.2f}%"
    )

    print(
        f"Desvio: "
        f"{indicadores['desvio']:.2f} p.p."
    )

    print(
        f"Etapas monitoradas: "
        f"{indicadores['totalEtapas']}"
    )

    print("\nArquivos gerados:")

    print(ARQUIVO_EXCEL)
    print(ARQUIVO_GRAFICO)
    print(ARQUIVO_JSON)


if __name__ == "__main__":

    try:
        main()

    except Exception as erro:

        print("\nERRO:")
        print(erro)

