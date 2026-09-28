# -*- coding: utf-8 -*-
"""
charts.py
---------
Funções responsáveis por construir cada gráfico Plotly do dashboard a partir
do DataFrame já filtrado. Nenhuma função aqui filtra dados — isso é
responsabilidade de filters.py. Aqui apenas agregamos e desenhamos.

Todas as figuras usam um layout consistente (fonte, cores, grid) para manter
a aparência de um dashboard de BI profissional.
"""

import pandas as pd
import plotly.graph_objects as go

from utils import format_float_br, format_int_br

#
# Paleta de cores institucional (discreta, poucas cores fortes)
# 
COLOR_PRIMARY = "#1f4e79"
COLOR_PRIMARY_LIGHT = "#2f6ba3"
COLOR_ACCENT = "#2ca9a3"
COLOR_ACCENT_2 = "#7c5cbf"
COLOR_WARNING = "#e2a53a"
COLOR_DANGER = "#d5654a"
COLOR_GREEN = "#3fa34d"
COLOR_MUTED = "#9aa5b1"

CATEGORICAL_PALETTE = [
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_ACCENT_2, COLOR_WARNING,
    COLOR_GREEN, COLOR_DANGER, COLOR_PRIMARY_LIGHT, COLOR_MUTED,
]

STATUS_COLORS = {"ABERTO": COLOR_ACCENT, "FECHADO": COLOR_MUTED}
INVESTIMENTO_COLORS = {"GRATUITO": COLOR_PRIMARY, "PAGO": COLOR_WARNING}

FONT_FAMILY = "Segoe UI, Inter, Arial, sans-serif"

EMPTY_MSG = "Nenhum registro para os filtros selecionados"


def _base_layout(fig: go.Figure, height: int = 360, legend: bool = False) -> go.Figure:
    """Aplica um layout padrão, limpo, a qualquer figura Plotly."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family=FONT_FAMILY, size=12.5, color="#1f2733"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="white", font_size=12.5, font_family=FONT_FAMILY),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0) if legend else None,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eef1f5", zeroline=False)
    return fig


def _empty_figure(height: int = 360) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=EMPTY_MSG, showarrow=False,
        font=dict(family=FONT_FAMILY, size=13, color="#9aa5b1"),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _base_layout(fig, height=height)


def _bar_opacities(categorias, selecionado) -> list:
    """Retorna uma opacidade por barra: destaca a categoria selecionada
    (clique de drill-down) e esmaece as demais. Sem seleção, todas iguais."""
    if not selecionado:
        return [0.92] * len(categorias)
    return [1.0 if c == selecionado else 0.28 for c in categorias]


def _pie_pull(labels, selecionado) -> list:
    """Puxa levemente a fatia selecionada para fora do donut."""
    if not selecionado:
        return [0] * len(labels)
    return [0.06 if lbl == selecionado else 0 for lbl in labels]


# 
# 1. Inscrições por Curso / Evento (barras horizontais, ordenadas
#    cronologicamente pela data de início — uma barra por curso/evento)
# 

def fig_inscricoes_por_curso(df: pd.DataFrame, selecionado: str = None) -> go.Figure:
    if df.empty:
        return _empty_figure(420)

    d = df.dropna(subset=["data de inicio"]).copy()
    if d.empty:
        return _empty_figure(420)

    # Ordena cronologicamente pela data de início (crescente).
    d = d.sort_values("data de inicio", ascending=True)
    d["Label"] = d["Título do Curso / Evento"].apply(_truncate)
    # A primeira barra do eixo Y do Plotly fica embaixo; invertendo a ordem
    # aqui faz o curso mais antigo aparecer no topo do gráfico.
    d = d.iloc[::-1]

    customdata = d[[
        "Título do Curso / Evento", "Tipo", "Status", "Modalidade", "Investimento",
    ]].copy()
    customdata["Data"] = d["data de inicio"].dt.strftime("%d/%m/%Y").fillna("-")
    customdata = customdata.values

    opacities = _bar_opacities(d["Título do Curso / Evento"], selecionado)

    fig = go.Figure(go.Bar(
        x=d["Inscrições"],
        y=d["Label"],
        orientation="h",
        marker=dict(color=COLOR_PRIMARY_LIGHT, opacity=opacities),
        customdata=customdata,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Inscrições: %{x}<br>"
            "Data de início: %{customdata[5]}<br>"
            "Tipo: %{customdata[1]}<br>"
            "Status: %{customdata[2]}<br>"
            "Modalidade: %{customdata[3]}<br>"
            "Investimento: %{customdata[4]}<extra></extra>"
        ),
        text=d["Inscrições"],
        textposition="outside",
    ))
    fig.update_xaxes(title_text="Inscrições")
    fig.update_yaxes(title_text="", automargin=True, categoryorder="array", categoryarray=d["Label"])
    # Altura cresce com a quantidade de cursos, para nunca esmagar as barras.
    altura = max(380, 32 * len(d) + 90)
    return _base_layout(fig, height=altura)


# 
# 2. Inscrições por tipo de curso (barras horizontais)
# 

def fig_inscricoes_por_tipo(df: pd.DataFrame, selecionado: str = None) -> go.Figure:
    if df.empty:
        return _empty_figure(360)

    total_geral = df["Inscrições"].sum()

    agg = (
        df.groupby("Tipo")
        .agg(Total_Inscricoes=("Inscrições", "sum"), Qtd_Cursos=("Tipo", "count"))
        .reset_index()
        .sort_values("Total_Inscricoes", ascending=True)
    )
    agg["Percentual"] = agg["Total_Inscricoes"] / total_geral * 100 if total_geral else 0
    agg["Percentual_Str"] = agg["Percentual"].apply(lambda v: format_float_br(v, 1))
    agg["Total_Str"] = agg["Total_Inscricoes"].apply(format_int_br)

    fig = go.Figure(go.Bar(
        x=agg["Total_Inscricoes"],
        y=agg["Tipo"],
        orientation="h",
        marker=dict(
            color=COLOR_PRIMARY,
            opacity=_bar_opacities(agg["Tipo"], selecionado),
        ),
        customdata=agg[["Qtd_Cursos", "Percentual_Str"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>Inscritos: %{x}<br>"
            "Cursos/eventos: %{customdata[0]}<br>"
            "Participação: %{customdata[1]}% do total<extra></extra>"
        ),
        text=agg["Total_Str"],
        textposition="outside",
    ))
    fig.update_xaxes(title_text="Total de inscrições")
    fig.update_yaxes(title_text="")
    return _base_layout(fig, height=360)


# 
# 3. Status dos cursos (donut)
#

def fig_status_donut(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure(340)

    agg = df.groupby("Status").size().reset_index(name="Quantidade")
    total = agg["Quantidade"].sum()
    colors = [STATUS_COLORS.get(s, COLOR_MUTED) for s in agg["Status"]]

    fig = go.Figure(go.Pie(
        labels=agg["Status"],
        values=agg["Quantidade"],
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:11px'>cursos/eventos</span>",
        showarrow=False, font=dict(family=FONT_FAMILY, size=20, color=COLOR_PRIMARY),
    )
    return _base_layout(fig, height=340, legend=True)


# 
# 4. Inscrições por modalidade (barras verticais)
# 

def fig_inscricoes_por_modalidade(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure(360)

    agg = (
        df.groupby("Modalidade")
        .agg(Total_Inscricoes=("Inscrições", "sum"), Qtd_Cursos=("Modalidade", "count"))
        .reset_index()
        .sort_values("Total_Inscricoes", ascending=False)
    )

    fig = go.Figure(go.Bar(
        x=agg["Modalidade"],
        y=agg["Total_Inscricoes"],
        marker=dict(color=CATEGORICAL_PALETTE[: len(agg)]),
        customdata=agg[["Qtd_Cursos"]].values,
        hovertemplate=(
            "<b>%{x}</b><br>Total de inscrições: %{y}<br>"
            "Cursos/eventos: %{customdata[0]}<extra></extra>"
        ),
        text=agg["Total_Inscricoes"],
        textposition="outside",
    ))
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Total de inscrições")
    return _base_layout(fig, height=360)


# 
# 5. Cursos Pagos x Gratuitos (donut) — quantidade de cursos/eventos por
#    Investimento, com total de inscrições de cada segmento no tooltip.
# 

def fig_pagos_gratuitos(df: pd.DataFrame, selecionado: str = None) -> go.Figure:
    if df.empty:
        return _empty_figure(340)

    agg = (
        df.groupby("Investimento")
        .agg(Qtd_Cursos=("Investimento", "size"), Total_Inscricoes=("Inscrições", "sum"))
        .reset_index()
    )
    total_cursos = agg["Qtd_Cursos"].sum()
    agg["Percentual_Str"] = (agg["Qtd_Cursos"] / total_cursos * 100).apply(lambda v: format_float_br(v, 1)) if total_cursos else "0,0"
    agg["Inscricoes_Str"] = agg["Total_Inscricoes"].apply(format_int_br)

    colors = [INVESTIMENTO_COLORS.get(i, COLOR_MUTED) for i in agg["Investimento"]]

    fig = go.Figure(go.Pie(
        labels=agg["Investimento"],
        values=agg["Qtd_Cursos"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        pull=_pie_pull(agg["Investimento"], selecionado),
        textinfo="label+percent",
        textfont=dict(size=12),
        customdata=agg[["Percentual_Str", "Inscricoes_Str"]].values,
        hovertemplate=(
            "<b>%{label}</b><br>%{value} cursos<br>"
            "%{customdata[0]}% dos cursos<br>"
            "%{customdata[1]} inscritos<extra></extra>"
        ),
    ))
    fig.add_annotation(
        text=f"<b>{total_cursos}</b><br><span style='font-size:11px'>TOTAL DE CURSOS</span>",
        showarrow=False, font=dict(family=FONT_FAMILY, size=20, color=COLOR_PRIMARY),
    )
    return _base_layout(fig, height=340, legend=True)


# 
# 6. Comparativo de Inscrições por Curso (barras horizontais, todos os
#    cursos/eventos filtrados, ordenados do maior para o menor)
# 

def _truncate(texto: str, tamanho: int = 42) -> str:
    texto = str(texto)
    return texto if len(texto) <= tamanho else texto[: tamanho - 1].rstrip() + "…"


def fig_comparativo_cursos(df: pd.DataFrame, top_n: int = None, selecionado: str = None) -> go.Figure:
    if df.empty:
        return _empty_figure(420)

    d = df.sort_values("Inscrições", ascending=False).copy()
    if top_n:
        d = d.head(top_n)
    d["Label"] = d["Título do Curso / Evento"].apply(_truncate)
    d = d.sort_values("Inscrições", ascending=True)  # maior no topo da barra horizontal

    customdata = d[[
        "Título do Curso / Evento", "Tipo", "Status", "Modalidade",
        "Investimento",
    ]].copy()
    customdata["Data"] = d["data de inicio"].dt.strftime("%d/%m/%Y").fillna("-")
    customdata = customdata.values

    # Cor consistente com a paleta do dashboard; barra selecionada em destaque.
    opacities = _bar_opacities(d["Título do Curso / Evento"], selecionado)

    fig = go.Figure(go.Bar(
        x=d["Inscrições"],
        y=d["Label"],
        orientation="h",
        marker=dict(color=COLOR_ACCENT_2, opacity=opacities),
        customdata=customdata,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Inscrições: %{x}<br>"
            "Tipo: %{customdata[1]}<br>"
            "Status: %{customdata[2]}<br>"
            "Modalidade: %{customdata[3]}<br>"
            "Investimento: %{customdata[4]}<br>"
            "Data de início: %{customdata[5]}<extra></extra>"
        ),
        text=d["Inscrições"],
        textposition="outside",
    ))
    fig.update_xaxes(title_text="Inscrições")
    fig.update_yaxes(title_text="", automargin=True)
    # Altura cresce com a quantidade de cursos exibidos, para nunca cortar labels.
    altura = max(380, 30 * len(d) + 80)
    return _base_layout(fig, height=altura)


# 
# 7. Inscrições ao longo do tempo (evolução mensal - área)
# 

def fig_evolucao_temporal(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure(340)

    d = df.dropna(subset=["data de inicio"]).copy()
    if d.empty:
        return _empty_figure(340)

    agg = (
        d.groupby(d["data de inicio"].dt.to_period("M"))
        .agg(Inscricoes=("Inscrições", "sum"), Qtd_Cursos=("Tipo", "count"))
        .reset_index()
    )
    agg["Mes"] = agg["data de inicio"].dt.to_timestamp()
    agg = agg.sort_values("Mes")

    fig = go.Figure(go.Scatter(
        x=agg["Mes"],
        y=agg["Inscricoes"],
        mode="lines+markers",
        line=dict(color=COLOR_ACCENT, width=2.5),
        marker=dict(size=8, color=COLOR_ACCENT),
        fill="tozeroy",
        fillcolor="rgba(44, 169, 163, 0.12)",
        customdata=agg[["Qtd_Cursos"]].values,
        hovertemplate=(
            "Mês: %{x|%m/%Y}<br>Inscrições: %{y}<br>"
            "Cursos/eventos: %{customdata[0]}<extra></extra>"
        ),
    ))
    fig.update_xaxes(title_text="Mês", tickformat="%m/%Y")
    fig.update_yaxes(title_text="Inscrições")
    return _base_layout(fig, height=340)
