# -*- coding: utf-8 -*-
"""
callbacks.py
------------
Registra todos os callbacks do dashboard:
  - Callback principal: aplica filtros globais + seleção por clique
    (drill-down) e atualiza cards, gráficos e tabela.
  - Callbacks de clique: capturam cliques em "Inscrições por Curso / Evento",
    "Inscrições por tipo", "Status dos cursos", "Inscrições por modalidade",
    "Cursos Pagos x Gratuitos" e "Comparativo de Inscrições por Curso" para
    permitir interação entre gráficos (comportamento estilo BI).
  - Callback do botão "Limpar filtros".
"""

from dash import Input, Output, State, ctx, html, no_update

import charts
from data_loader import DF
from filters import apply_filters
from utils import format_float_br, format_int_br


def _toggle_categoria(click_data, valor_atual, campo_ponto):
    """Lógica de alternância (toggle) para seleção via clique em gráfico.

    Se o usuário clicar na mesma categoria já selecionada, a seleção é
    removida (comportamento de "desfazer"). Caso contrário, a nova
    categoria selecionada substitui a anterior.

    `campo_ponto` pode ser o nome de uma chave do ponto clicado (ex.: "y",
    "x", "label") ou, para os gráficos de curso (onde o eixo mostra um nome
    truncado), a string especial "customdata0", que usa o primeiro valor de
    customdata — o título completo do curso — em vez do label do eixo.
    """
    if not click_data:
        return no_update
    try:
        ponto = click_data["points"][0]
        if campo_ponto == "customdata0":
            categoria = ponto["customdata"][0]
        else:
            categoria = ponto[campo_ponto]
    except (KeyError, IndexError):
        return no_update
    if valor_atual == categoria:
        return None
    return categoria


def register_callbacks(app):

    # 
    # Cliques nos gráficos -> atualizam os "Stores" de seleção (drill-down)
    # 
    @app.callback(
        Output("store-tipo-selecionado", "data"),
        Input("graph-tipo", "clickData"),
        Input("btn-limpar-filtros", "n_clicks"),
        State("store-tipo-selecionado", "data"),
        prevent_initial_call=True,
    )
    def _click_tipo(click_data, n_clicks_limpar, valor_atual):
        if ctx.triggered_id == "btn-limpar-filtros":
            return None
        return _toggle_categoria(click_data, valor_atual, "y")

    @app.callback(
        Output("store-status-selecionado", "data"),
        Input("graph-status", "clickData"),
        Input("btn-limpar-filtros", "n_clicks"),
        State("store-status-selecionado", "data"),
        prevent_initial_call=True,
    )
    def _click_status(click_data, n_clicks_limpar, valor_atual):
        if ctx.triggered_id == "btn-limpar-filtros":
            return None
        return _toggle_categoria(click_data, valor_atual, "label")

    @app.callback(
        Output("store-modalidade-selecionada", "data"),
        Input("graph-modalidade", "clickData"),
        Input("btn-limpar-filtros", "n_clicks"),
        State("store-modalidade-selecionada", "data"),
        prevent_initial_call=True,
    )
    def _click_modalidade(click_data, n_clicks_limpar, valor_atual):
        if ctx.triggered_id == "btn-limpar-filtros":
            return None
        return _toggle_categoria(click_data, valor_atual, "x")

    @app.callback(
        Output("store-investimento-selecionado", "data"),
        Input("graph-investimento", "clickData"),
        Input("btn-limpar-filtros", "n_clicks"),
        State("store-investimento-selecionado", "data"),
        prevent_initial_call=True,
    )
    def _click_investimento(click_data, n_clicks_limpar, valor_atual):
        if ctx.triggered_id == "btn-limpar-filtros":
            return None
        return _toggle_categoria(click_data, valor_atual, "label")

    # O curso selecionado pode vir de dois gráficos diferentes: o principal
    # ("Inscrições por Curso / Evento") e o "Comparativo de Inscrições por
    # Curso". Os dois escrevem no mesmo Store.
    @app.callback(
        Output("store-curso-selecionado", "data"),
        Input("graph-timeline", "clickData"),
        Input("graph-comparativo-cursos", "clickData"),
        Input("btn-limpar-filtros", "n_clicks"),
        State("store-curso-selecionado", "data"),
        prevent_initial_call=True,
    )
    def _click_curso(click_timeline, click_comparativo, n_clicks_limpar, valor_atual):
        if ctx.triggered_id == "btn-limpar-filtros":
            return None
        if ctx.triggered_id == "graph-timeline":
            return _toggle_categoria(click_timeline, valor_atual, "customdata0")
        if ctx.triggered_id == "graph-comparativo-cursos":
            return _toggle_categoria(click_comparativo, valor_atual, "customdata0")
        return no_update

    # 
    # Botão "Limpar filtros" -> reseta filtros globais
    #
    @app.callback(
        Output("filter-date-range", "start_date"),
        Output("filter-date-range", "end_date"),
        Output("filter-tipo", "value"),
        Output("filter-status", "value"),
        Output("filter-modalidade", "value"),
        Output("filter-investimento", "value"),
        Input("btn-limpar-filtros", "n_clicks"),
        prevent_initial_call=True,
    )
    def _limpar_filtros(n_clicks):
        min_date = DF["data de inicio"].min()
        max_date = DF["data de inicio"].max()
        return min_date, max_date, None, None, None, None

    # 
    # Callback principal: aplica filtros e atualiza toda a página
    # 
    @app.callback(
        Output("kpi-total-inscricoes", "children"),
        Output("kpi-total-cursos", "children"),
        Output("kpi-cursos-abertos", "children"),
        Output("kpi-cursos-fechados", "children"),
        Output("kpi-media-inscricoes", "children"),
        Output("graph-timeline", "figure"),
        Output("graph-tipo", "figure"),
        Output("graph-status", "figure"),
        Output("graph-modalidade", "figure"),
        Output("graph-investimento", "figure"),
        Output("graph-comparativo-cursos", "figure"),
        Output("graph-evolucao", "figure"),
        Output("tabela-detalhada", "data"),
        Output("tabela-detalhada", "tooltip_data"),
        Output("drill-banner", "children"),
        Output("drill-banner", "style"),
        Input("filter-date-range", "start_date"),
        Input("filter-date-range", "end_date"),
        Input("filter-tipo", "value"),
        Input("filter-status", "value"),
        Input("filter-modalidade", "value"),
        Input("filter-investimento", "value"),
        Input("store-tipo-selecionado", "data"),
        Input("store-status-selecionado", "data"),
        Input("store-modalidade-selecionada", "data"),
        Input("store-investimento-selecionado", "data"),
        Input("store-curso-selecionado", "data"),
    )
    def _atualizar_dashboard(
        data_inicio, data_fim, tipos, status, modalidades, investimentos,
        tipo_sel, status_sel, modalidade_sel, investimento_sel, curso_sel,
    ):
        df_filtrado = apply_filters(
            DF,
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipos=tipos,
            status=status,
            modalidades=modalidades,
            investimentos=investimentos,
            tipo_selecionado=tipo_sel,
            status_selecionado=status_sel,
            modalidade_selecionada=modalidade_sel,
            investimento_selecionado=investimento_sel,
            curso_selecionado=curso_sel,
        )

        # --- KPIs ---
        total_inscricoes = df_filtrado["Inscrições"].sum()
        total_cursos = len(df_filtrado)
        cursos_abertos = int((df_filtrado["Status"] == "ABERTO").sum())
        cursos_fechados = int((df_filtrado["Status"] == "FECHADO").sum())
        media_inscricoes = df_filtrado["Inscrições"].mean() if total_cursos > 0 else 0

        kpi_1 = format_int_br(total_inscricoes)
        kpi_2 = format_int_br(total_cursos)
        kpi_3 = format_int_br(cursos_abertos)
        kpi_4 = format_int_br(cursos_fechados)
        kpi_5 = format_float_br(media_inscricoes, 1)

        # --- Gráficos ---
        fig_timeline = charts.fig_inscricoes_por_curso(df_filtrado, selecionado=curso_sel)
        fig_tipo = charts.fig_inscricoes_por_tipo(df_filtrado, selecionado=tipo_sel)
        fig_status = charts.fig_status_donut(df_filtrado)
        fig_modalidade = charts.fig_inscricoes_por_modalidade(df_filtrado)
        fig_investimento = charts.fig_pagos_gratuitos(df_filtrado, selecionado=investimento_sel)
        fig_comparativo = charts.fig_comparativo_cursos(df_filtrado, selecionado=curso_sel)
        fig_evolucao = charts.fig_evolucao_temporal(df_filtrado)

        # --- Tabela ---
        df_tabela = df_filtrado.copy()
        df_tabela["Data de início"] = df_tabela["data de inicio"].dt.strftime("%d/%m/%Y")
        colunas_tabela = [
            "Tipo", "Título do Curso / Evento", "Inscrições", "Status",
            "Modalidade", "Datas Detalhadas", "Investimento", "Data de início",
        ]
        df_tabela = df_tabela[colunas_tabela].sort_values("Inscrições", ascending=False)
        dados_tabela = df_tabela.to_dict("records")

        tooltip_data = [
            {
                "Título do Curso / Evento": {"value": row["Título do Curso / Evento"], "type": "text"},
                "Datas Detalhadas": {"value": str(row["Datas Detalhadas"]), "type": "text"},
            }
            for row in dados_tabela
        ]

        # --- Banner de drill-down (seleção ativa via clique) ---
        selecoes = []
        if tipo_sel:
            selecoes.append(f"Tipo: {tipo_sel}")
        if status_sel:
            selecoes.append(f"Status: {status_sel}")
        if modalidade_sel:
            selecoes.append(f"Modalidade: {modalidade_sel}")
        if investimento_sel:
            selecoes.append(f"Investimento: {investimento_sel}")
        if curso_sel:
            selecoes.append(f"Curso/evento: {curso_sel}")

        if selecoes:
            banner = html.Div(
                [
                    html.Span("🔎 Filtro por seleção ativo — ", style={"fontWeight": 600}),
                    html.Span(" | ".join(selecoes)),
                    html.Span("  (clique novamente na categoria ou em 'Limpar filtros' para remover)",
                               style={"opacity": 0.75, "marginLeft": "6px"}),
                ]
            )
            banner_style = {
                "display": "block",
                "background": "#eaf2fb",
                "color": "#1f4e79",
                "padding": "8px 16px",
                "borderRadius": "8px",
                "margin": "0 20px 14px 20px",
                "fontSize": "13px",
            }
        else:
            banner = ""
            banner_style = {"display": "none"}

        return (
            kpi_1, kpi_2, kpi_3, kpi_4, kpi_5,
            fig_timeline, fig_tipo, fig_status, fig_modalidade, fig_investimento,
            fig_comparativo, fig_evolucao,
            dados_tabela, tooltip_data,
            banner, banner_style,
        )
