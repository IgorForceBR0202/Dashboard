# -*- coding: utf-8 -*-
"""
layout.py
---------
Monta a estrutura visual (layout) do dashboard: cabeçalho, filtros, cards de
indicadores, gráficos e tabela detalhada. Os componentes que precisam ser
atualizados dinamicamente recebem `id`s, que são usados em callbacks.py.
"""

from datetime import datetime

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from data_loader import DF, FILE_LAST_MODIFIED

# 
# Opções de filtro (calculadas a partir dos dados reais - nada fixo/inventado)
# 
TIPO_OPTIONS = sorted(DF["Tipo"].dropna().unique().tolist())
STATUS_OPTIONS = sorted(DF["Status"].dropna().unique().tolist())
MODALIDADE_OPTIONS = sorted(DF["Modalidade"].dropna().unique().tolist())
INVESTIMENTO_OPTIONS = sorted(DF["Investimento"].dropna().unique().tolist())

MIN_DATE = DF["data de inicio"].min()
MAX_DATE = DF["data de inicio"].max()

TABLE_COLUMNS = [
    {"name": "Tipo", "id": "Tipo"},
    {"name": "Título do Curso / Evento", "id": "Título do Curso / Evento"},
    {"name": "Inscrições", "id": "Inscrições", "type": "numeric"},
    {"name": "Status", "id": "Status"},
    {"name": "Modalidade", "id": "Modalidade"},
    {"name": "Datas Detalhadas", "id": "Datas Detalhadas"},
    {"name": "Investimento", "id": "Investimento"},
    {"name": "Data de início", "id": "Data de início"},
]


def _kpi_card(card_id: str, label: str, icon: str, accent_class: str):
    return dbc.Col(
        html.Div(
            [
                html.Div(icon, className="kpi-icon"),
                html.Div(label, className="kpi-label"),
                html.Div(id=card_id, className="kpi-value"),
            ],
            className=f"kpi-card {accent_class}",
        ),
        xs=12, sm=6, md=4, lg=True,
        className="mb-3",
    )


def _chart_card(title: str, subtitle: str, graph_id: str, extra=None, height=None):
    children = [
        html.Div(title, className="chart-title"),
        html.Div(subtitle, className="chart-subtitle"),
    ]
    if extra is not None:
        children.append(extra)
    children.append(
        dcc.Graph(
            id=graph_id,
            config={
                "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "autoScale2d"],
                "scrollZoom": False,
            },
            style={"height": f"{height}px"} if height else None,
        )
    )
    return html.Div(children, className="chart-card")


def build_layout() -> html.Div:
    updated_str = FILE_LAST_MODIFIED.strftime("%d/%m/%Y %H:%M")

    header = html.Div(
        [
            html.Div("EMEDI", className="header-brand"),
            html.H1("Dashboard de Capacitações e Eventos", className="header-title"),
            html.Div(
                "Visão geral de inscrições, cursos, modalidades e status",
                className="header-subtitle",
            ),
            html.Div(f"Atualizado em: {updated_str}", id="header-updated", className="header-updated"),
        ],
        className="header-container",
    )

    filtros = html.Div(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Período / Data de início", className="filter-label"),
                        dcc.DatePickerRange(
                            id="filter-date-range",
                            min_date_allowed=MIN_DATE,
                            max_date_allowed=MAX_DATE,
                            start_date=MIN_DATE,
                            end_date=MAX_DATE,
                            display_format="DD/MM/YYYY",
                            style={"width": "100%"},
                        ),
                    ],
                    xs=12, md=3, className="mb-2",
                ),
                dbc.Col(
                    [
                        html.Label("Tipo", className="filter-label"),
                        dcc.Dropdown(
                            id="filter-tipo",
                            options=[{"label": t, "value": t} for t in TIPO_OPTIONS],
                            multi=True, placeholder="Todos",
                        ),
                    ],
                    xs=12, md=2, className="mb-2",
                ),
                dbc.Col(
                    [
                        html.Label("Status", className="filter-label"),
                        dcc.Dropdown(
                            id="filter-status",
                            options=[{"label": s, "value": s} for s in STATUS_OPTIONS],
                            multi=True, placeholder="Todos",
                        ),
                    ],
                    xs=12, md=2, className="mb-2",
                ),
                dbc.Col(
                    [
                        html.Label("Modalidade", className="filter-label"),
                        dcc.Dropdown(
                            id="filter-modalidade",
                            options=[{"label": m, "value": m} for m in MODALIDADE_OPTIONS],
                            multi=True, placeholder="Todas",
                        ),
                    ],
                    xs=12, md=2, className="mb-2",
                ),
                dbc.Col(
                    [
                        html.Label("Investimento", className="filter-label"),
                        dcc.Dropdown(
                            id="filter-investimento",
                            options=[{"label": i, "value": i} for i in INVESTIMENTO_OPTIONS],
                            multi=True, placeholder="Todos",
                        ),
                    ],
                    xs=12, md=2, className="mb-2",
                ),
                dbc.Col(
                    [
                        html.Label(" ", className="filter-label d-none d-md-block"),
                        dbc.Button("Limpar filtros", id="btn-limpar-filtros", n_clicks=0, className="clear-filters-btn w-100"),
                    ],
                    xs=12, md=1, className="mb-2 d-flex align-items-end",
                ),
            ],
            className="g-2",
        ),
        className="filters-card",
    )

    drill_banner = html.Div(
        id="drill-banner",
        style={"display": "none"},
        className="mb-2",
    )

    kpis = dbc.Row(
        [
            _kpi_card("kpi-total-inscricoes", "Total de Inscrições", "🧾", "accent-1"),
            _kpi_card("kpi-total-cursos", "Total de Cursos / Eventos", "📚", "accent-2"),
            _kpi_card("kpi-cursos-abertos", "Cursos Abertos", "🟢", "accent-3"),
            _kpi_card("kpi-cursos-fechados", "Cursos Fechados", "⚪", "accent-4"),
            _kpi_card("kpi-media-inscricoes", "Média de Inscrições", "📊", "accent-5"),
        ],
        className="kpi-row g-3",
    )

    row_principal = dbc.Row(
        [
            dbc.Col(
                _chart_card(
                    "Inscrições por Curso / Evento",
                    "Cada barra representa um curso/evento, em ordem cronológica pela data de início — clique para selecionar",
                    "graph-timeline",
                ),
                width=12,
            ),
        ],
        className="charts-row",
    )

    row_tipo_status = dbc.Row(
        [
            dbc.Col(
                _chart_card(
                    "Inscrições por tipo de curso",
                    "Soma de inscrições por tipo — clique em uma barra para filtrar o dashboard",
                    "graph-tipo",
                ),
                xs=12, lg=7, className="mb-0",
            ),
            dbc.Col(
                _chart_card(
                    "Status dos cursos",
                    "Distribuição entre abertos e fechados — clique para filtrar",
                    "graph-status",
                ),
                xs=12, lg=5, className="mb-0",
            ),
        ],
        className="charts-row",
    )

    row_modalidade_investimento = dbc.Row(
        [
            dbc.Col(
                _chart_card(
                    "Inscrições por modalidade",
                    "Total de inscrições e cursos/eventos por modalidade — clique para filtrar",
                    "graph-modalidade",
                ),
                xs=12, lg=7, className="mb-0",
            ),
            dbc.Col(
                _chart_card(
                    "Cursos Pagos x Gratuitos",
                    "Quantidade de cursos/eventos por investimento — clique para filtrar",
                    "graph-investimento",
                ),
                xs=12, lg=5, className="mb-0",
            ),
        ],
        className="charts-row",
    )

    row_comparativo_cursos = dbc.Row(
        [
            dbc.Col(
                _chart_card(
                    "Comparativo de Inscrições por Curso",
                    "Todos os cursos/eventos filtrados, do maior para o menor — clique em uma barra para selecionar um curso",
                    "graph-comparativo-cursos",
                ),
                width=12,
            ),
        ],
        className="charts-row",
    )

    row_evolucao = dbc.Row(
        [
            dbc.Col(
                _chart_card(
                    "Inscrições ao longo do tempo",
                    "Evolução mensal das inscrições, considerando a data de início",
                    "graph-evolucao",
                ),
                width=12,
            ),
        ],
        className="charts-row",
    )

    tabela = html.Div(
        [
            html.Div("Detalhamento dos cursos e eventos", className="chart-title"),
            html.Div(
                "Ordene, pesquise e navegue pelos registros — respeita todos os filtros aplicados acima",
                className="chart-subtitle mb-2",
            ),
            dash_table.DataTable(
                id="tabela-detalhada",
                columns=TABLE_COLUMNS,
                data=[],
                sort_action="native",
                filter_action="native",
                page_action="native",
                page_size=10,
                row_selectable="single",
                selected_rows=[],
                style_table={"overflowX": "auto"},
                style_cell={
                    "fontFamily": "Segoe UI, Inter, Arial, sans-serif",
                    "fontSize": "13px",
                    "padding": "8px",
                    "textAlign": "left",
                    "maxWidth": "280px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                },
                style_header={"fontWeight": "700"},
                style_cell_conditional=[
                    {"if": {"column_id": "Título do Curso / Evento"}, "maxWidth": "340px"},
                ],
                tooltip_duration=None,
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#fafbfd"},
                ],
            ),
        ],
        className="table-card",
    )

    footer = html.Div(
        "EMEDI • Dashboard gerado a partir da planilha Relatorio_Capacitacoes_EMEDI.xlsx",
        className="footer-note",
    )

    return html.Div(
        [
            dcc.Store(id="store-tipo-selecionado", data=None),
            dcc.Store(id="store-status-selecionado", data=None),
            dcc.Store(id="store-modalidade-selecionada", data=None),
            dcc.Store(id="store-investimento-selecionado", data=None),
            dcc.Store(id="store-curso-selecionado", data=None),
            header,
            filtros,
            drill_banner,
            kpis,
            row_principal,
            row_tipo_status,
            row_modalidade_investimento,
            row_comparativo_cursos,
            row_evolucao,
            tabela,
            footer,
        ]
    )
