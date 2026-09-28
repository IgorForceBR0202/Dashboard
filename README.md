# Dashboard EMEDI — Capacitações e Eventos

Dashboard web interativo (Python + Dash + Plotly) para acompanhamento de
cursos, capacitações e eventos da EMEDI, construído a partir da planilha
`Relatorio_Capacitacoes_EMEDI.xlsx`.

Todos os indicadores e gráficos são calculados **diretamente** a partir da
aba `RT Capacitações e Eventos` da planilha — nenhum número é fixo no
código.

---

## 1. Estrutura do projeto

```
dashboard_emedi/
│
├── app.py                # Ponto de entrada da aplicação Dash
├── data_loader.py         # Leitura e tratamento/normalização dos dados
├── filters.py              # Lógica de aplicação dos filtros globais
├── charts.py                # Construção dos gráficos Plotly
├── layout.py                 # Estrutura visual (HTML/Bootstrap) da página
├── callbacks.py                # Callbacks (interatividade) do dashboard
├── utils.py                     # Formatação numérica no padrão brasileiro
│
├── data/
│   └── Relatorio_Capacitacoes_EMEDI.xlsx   # Fonte de dados
│
├── assets/
│   └── style.css          # Estilização (carregada automaticamente pelo Dash)
│
├── requirements.txt
└── README.md
```

O código foi separado por responsabilidade (dados, filtros, gráficos,
layout, callbacks) para facilitar manutenção futura.

---

## 2. Como executar localmente

Pré-requisitos: Python 3.10 ou superior.

```bash
# 1. Entre na pasta do projeto
cd dashboard_emedi

# 2. (Recomendado) crie um ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python app.py
```

A aplicação ficará disponível em `http://127.0.0.1:8050`.

---

## 3. Como o dashboard funciona

- **Gráfico principal — "Inscrições por Curso / Evento":** barras horizontais,
  uma por curso/evento, ordenadas cronologicamente pela data de início (o
  mais antigo no topo). O tamanho da barra representa o total de inscrições;
  o tooltip mostra nome completo, data, tipo, status, modalidade e
  investimento. Clicar em uma barra seleciona aquele curso/evento
  especificamente (ver "drill-down" abaixo).

- **Filtros (topo da página):** período (data de início), tipo, status,
  modalidade e investimento. Qualquer alteração atualiza automaticamente
  os cards, gráficos e a tabela. O botão **"Limpar filtros"** volta à
  visão geral.
- **Cards de indicadores:** total de inscrições, total de cursos/eventos,
  cursos abertos, cursos fechados e média de inscrições — todos recalculados
  conforme os filtros aplicados.
- **Interação entre gráficos (drill-down):** clicar em uma barra do gráfico
  principal ou do "Comparativo de Inscrições por Curso" seleciona aquele
  curso/evento; clicar em uma barra de "Inscrições por tipo de curso", em
  uma fatia de "Status dos cursos" ou "Cursos Pagos x Gratuitos", ou em uma
  barra de "Inscrições por modalidade", filtra o restante do dashboard
  (cards, demais gráficos e tabela) por aquela categoria. Clicar novamente
  na mesma categoria remove a seleção. Um aviso azul aparece no topo
  indicando quando esse filtro por seleção está ativo.
- **Tabela detalhada:** possui ordenação por coluna (inclusive por
  "Inscrições", do maior para o menor), busca/filtro por coluna,
  paginação e seleção de linha. Nomes longos de curso mostram um tooltip
  com o texto completo.

---

## 4. Tratamento e normalização dos dados

Aplicados apenas no DataFrame em memória (o arquivo Excel original nunca é
alterado):

- Espaços extras removidos dos nomes de colunas (ex.: `"Status "` → `"Status"`).
- Coluna auxiliar `"Unnamed: 8"` descartada — não é usada em nenhum indicador.
- `"Inscrições"` convertida para número inteiro.
- `"data de inicio"` convertida para data (datetime).
- `"Status"` e `"Investimento"` padronizados (espaços/maiúsculas).
- `"Modalidade"`: grafias equivalentes são unificadas —
  `"Híbrida"` e `"Híbrido"` → **"Híbrido"**;
  `"Online (Ao vivo)"` e `"Online ao vivo"` → **"Online ao vivo"**;
  `"Telepresencial"` e `"Presencial"` permanecem como categorias próprias,
  pois representam modalidades distintas na planilha.

Essa lógica está centralizada em `data_loader.py`, na função `load_data()`.

---

## 5. Como atualizar a planilha (dados novos)

O dashboard lê o Excel **dinamicamente** a cada inicialização — nenhum
valor fica fixo no código.

Para atualizar os dados:

1. Substitua o arquivo em `data/Relatorio_Capacitacoes_EMEDI.xlsx` por uma
   nova versão, **mantendo o mesmo nome de arquivo e a mesma aba**
   (`RT Capacitações e Eventos`) com as mesmas colunas.
2. Reinicie a aplicação (`python app.py`, ou reinicie o serviço no servidor
   de publicação).
3. O campo "Atualizado em" no cabeçalho passa a refletir a data de
   modificação do novo arquivo automaticamente.

Se quiser permitir upload de um novo Excel diretamente pela interface web
(sem precisar reiniciar o servidor), isso pode ser adicionado depois com um
componente `dcc.Upload` — não foi incluído nesta primeira versão para manter
o projeto simples, conforme prioridade de manutenção definida no escopo.

---

## 6. Publicação (link para o e-mail)

O objetivo final é ter uma URL fixa para incluir no e-mail
("Acessar Dashboard"). Algumas opções, da mais simples à mais flexível:

### Opção recomendada para este projeto: **Render**
- Gratuito para começar, simples de configurar, e gera uma URL pública
  estável (ex.: `https://dashboard-emedi.onrender.com`).
- Passos gerais:
  1. Suba este projeto para um repositório Git (GitHub/GitLab).
  2. Crie um novo **Web Service** no Render, apontando para o repositório.
  3. Comando de build: `pip install -r requirements.txt`
  4. Comando de start: `gunicorn app:server`
  5. O Render fornece a URL pública automaticamente.

### Railway
- Também muito simples, funciona de forma parecida ao Render (deploy a
  partir do Git, comando de start `gunicorn app:server`). Boa alternativa
  caso o Render não atenda alguma necessidade específica.

### PythonAnywhere
- Bom para instituições que preferem um plano pago fixo e mais controle
  manual sobre o servidor. Exige configurar manualmente a aplicação Flask
  (WSGI) apontando para o objeto `server` de `app.py`.

### Servidor próprio (institucional)
- Caso a EMEDI tenha infraestrutura própria (servidor Linux), a aplicação
  pode rodar com `gunicorn app:server` atrás de um Nginx como proxy
  reverso, com HTTPS via Let's Encrypt.

**Recomendação:** para o cenário descrito (link enviado por e-mail, sem
exigir que o destinatário instale nada), o **Render** é a opção mais
simples: deploy direto do repositório Git, sem necessidade de gerenciar
servidor, e com URL pública em poucos minutos.

Em qualquer uma dessas opções, o e-mail enviado pode conter apenas:

```
Visualize o relatório completo aqui:
[ACESSAR DASHBOARD] → https://SEU-DOMINIO-AQUI
```

---

## 7. Performance

- O Excel é lido e tratado **uma única vez**, na inicialização do
  processo (`data_loader.py`, variável `DF`), e reaproveitado por todos os
  callbacks — não há releitura do arquivo a cada interação do usuário.
- Os callbacks recalculam apenas os agregados necessários (filtragem em
  memória com pandas), o que é bastante rápido mesmo com o crescimento da
  planilha.

---

## 8. Próximos passos possíveis (fora do escopo desta entrega)

- Upload de nova planilha pela própria interface web.
- Autenticação/controle de acesso ao link do dashboard.
- Exportação da tabela filtrada para Excel/PDF diretamente pela interface.
