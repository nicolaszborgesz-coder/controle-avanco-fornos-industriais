# Controle de Avanço Físico — Reforma de Fornos Industriais

Projeto demonstrativo de Planejamento e Controle de Obras (PCO), desenvolvido com Python, Excel e HTML\CSS\JavaScript.

O sistema calcula o avanço físico ponderado, compara planejado e realizado por etapa e disponibiliza os indicadores em uma planilha Excel e em um dashboard web.

> **Aviso:** este repositório utiliza dados fictícios para demonstração. Não representa uma obra, empresa, contrato ou cronograma real.

## Funcionalidades

- Leitura e validação de dados de avanço a partir de CSV.
- Cálculo do avanço planejado e realizado ponderado pelo peso de cada etapa.
- Cálculo do desvio em pontos percentuais (p.p.).
- Geração de planilha Excel com abas de resumo, etapas e Curva S.
- Geração de gráfico PNG.
- Exportação de dados em JSON para alimentar o dashboard.
- Dashboard responsivo com indicadores, tabela por etapa e gráfico de evolução.

## Tecnologias

- Python 3
- CSV e JSON
- Matplotlib
- OpenPyXL
- HTML5, CSS3 e JavaScript

## Estrutura do projeto

```text
controle-avanco-fornos-industriais/
├── dados/
│   └── avanco.csv
├── dashboard/
│   ├── data.json
│   ├── grafico_avanco.png
│   ├── index.html
│   ├── script.js
│   └── style.css
├── python/
│   └── gerar_relatorios.py
├── relatorios/
│   ├── controle_avanco.xlsx
│   └── grafico_avanco.png
├── painel-de-controle-1.jpeg
├── painel-de-controle-2.jpeg
├── requirements.txt
└── README.md
```

## Como executar no Windows

### 1. Baixe ou clone o repositório

```powershell
git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
cd controle-avanco-fornos-industriais
```

### 2. (Opcional, recomendado) Crie um ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

```powershell
python -m pip install -r requirements.txt
```

### 4. Gere os relatórios

Na pasta raiz do projeto:

```powershell
python .\python\gerar_relatorios.py
```

Os arquivos serão atualizados em `relatorios/` e `dashboard/`.

### 5. Abra o dashboard localmente

Em um segundo terminal, na pasta raiz:

```powershell
python -m http.server 8001 --directory dashboard --bind 127.0.0.1
```

Acesse no navegador:

```text
http://127.0.0.1:8001/
```

O dashboard carrega `dashboard/data.json`. Para refletir alterações no CSV, execute novamente o script Python e atualize a página.

## Como atualizar os dados

Edite `dados/avanco.csv`, mantendo o cabeçalho:

```csv
etapa,peso,planejado,realizado
```

- `etapa`: nome da atividade.
- `peso`: peso percentual da etapa no avanço total. A soma dos pesos deve ser 100.
- `planejado`: percentual planejado de conclusão daquela etapa (0 a 100).
- `realizado`: percentual efetivamente executado daquela etapa (0 a 100).

Os percentuais por etapa são ponderados pelo respectivo peso. Exemplo: uma etapa com peso de 30% e execução de 65% contribui com 19,5 pontos percentuais para o avanço total.

**Desvio (p.p.)** é a diferença entre avanço realizado e planejado, em pontos percentuais: `realizado - planejado`.

## Sobre a Curva S

A série semanal incluída nesta versão é **ilustrativa**, criada para demonstrar o gráfico. Ela não é um histórico diário coletado. Para usar o sistema em um projeto real, substitua a série demonstrativa por registros históricos datados e validados, mantendo os dados de cada período.

## Publicação no GitHub

1. Crie um repositório público no GitHub.
2. Envie o conteúdo desta pasta para a raiz do repositório.
3. Confira se o README aparece corretamente e se os dados continuam identificados como fictícios.

Não publique dados de clientes, nomes de empresas, contratos, cronogramas, fotos de instalações ou informações operacionais sem autorização expressa.
