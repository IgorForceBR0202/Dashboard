# 📊 Dashboard EMEDI - Capacitações e Eventos

<p align="center">
  <strong>Dashboard web interativo para análise e acompanhamento de capacitações e eventos.</strong>
</p>

<p align="center">
  Desenvolvido com Python, Dash, Plotly e Pandas.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow?style=for-the-badge)

</p>

---

## 🖥️ Demonstração

<p align="center">
  <img src="assets/dashboard-preview.png" alt="Dashboard EMEDI" width="900">
</p>

> Dashboard desenvolvido para centralizar, organizar e visualizar dados de cursos, capacitações e eventos de forma interativa.

---

## ✨ Funcionalidades

### 📈 Visualização de dados

- Gráficos interativos utilizando Plotly
- Indicadores atualizados dinamicamente
- Comparação de inscrições por curso/evento
- Distribuição por tipo, status e modalidade
- Análise de cursos pagos e gratuitos

### 🔎 Filtros interativos

- 📅 Período
- 📚 Tipo de curso
- 📌 Status
- 🖥️ Modalidade
- 💰 Investimento

Os filtros atualizam automaticamente os indicadores, gráficos e tabela.

### 🖱️ Interação entre gráficos

O dashboard possui interação entre os componentes.

Ao clicar em um elemento de um gráfico, os demais componentes podem ser filtrados automaticamente.

Isso permite realizar análises em diferentes níveis sem precisar recarregar a página.

### 📋 Tabela detalhada

- Pesquisa
- Ordenação por coluna
- Paginação
- Filtros
- Seleção de registros
- Visualização completa de nomes longos

---

# 🛠️ Tecnologias

| Tecnologia | Utilização |
|---|---|
| 🐍 Python | Linguagem principal |
| 📊 Pandas | Tratamento e análise dos dados |
| 📈 Plotly | Visualização interativa |
| 🌐 Dash | Desenvolvimento da aplicação web |
| 🎨 Dash Bootstrap Components | Componentes da interface |
| 📑 OpenPyXL | Leitura da planilha Excel |
| 🚀 Gunicorn | Servidor de aplicação |
| ☁️ PythonAnywhere | Publicação da aplicação |

---

# 📁 Estrutura do projeto

```text
dashboard_emedi/
│
├── 📄 app.py
├── 📄 callbacks.py
├── 📄 charts.py
├── 📄 data_loader.py
├── 📄 filters.py
├── 📄 layout.py
├── 📄 utils.py
│
├── 📂 assets/
│   └── style.css
│
├── 📂 data/
│   └── exemplo_dados_EMEDI_ficticios.xlsx
│
├── 📄 requirements.txt
└── 📄 README.md
