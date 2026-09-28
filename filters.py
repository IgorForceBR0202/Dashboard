# -*- coding: utf-8 -*-
"""
filters.py
----------
Funções puras responsáveis por aplicar os filtros globais (e a seleção via
clique nos gráficos) sobre o DataFrame carregado pelo data_loader.

Mantidas separadas do restante do código para facilitar manutenção e testes.
"""

import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    data_inicio=None,
    data_fim=None,
    tipos=None,
    status=None,
    modalidades=None,
    investimentos=None,
    tipo_selecionado=None,
    status_selecionado=None,
    modalidade_selecionada=None,
    investimento_selecionado=None,
    curso_selecionado=None,
) -> pd.DataFrame:
    """Retorna uma cópia filtrada do DataFrame conforme os parâmetros informados.

    Parâmetros vindos dos filtros globais (topo da página):
        data_inicio, data_fim: intervalo de "data de inicio".
        tipos, status, modalidades, investimentos: listas de valores aceitos
            (None ou lista vazia = sem filtro nessa dimensão).

    Parâmetros vindos da interação de clique nos gráficos (drill-down):
        tipo_selecionado, status_selecionado, modalidade_selecionada,
        investimento_selecionado, curso_selecionado.
    """
    resultado = df.copy()

    if data_inicio:
        resultado = resultado[resultado["data de inicio"] >= pd.to_datetime(data_inicio)]
    if data_fim:
        resultado = resultado[resultado["data de inicio"] <= pd.to_datetime(data_fim)]

    if tipos:
        resultado = resultado[resultado["Tipo"].isin(tipos)]
    if status:
        resultado = resultado[resultado["Status"].isin(status)]
    if modalidades:
        resultado = resultado[resultado["Modalidade"].isin(modalidades)]
    if investimentos:
        resultado = resultado[resultado["Investimento"].isin(investimentos)]

    # Drill-down (clique em gráfico)
    if tipo_selecionado:
        resultado = resultado[resultado["Tipo"] == tipo_selecionado]
    if status_selecionado:
        resultado = resultado[resultado["Status"] == status_selecionado]
    if modalidade_selecionada:
        resultado = resultado[resultado["Modalidade"] == modalidade_selecionada]
    if investimento_selecionado:
        resultado = resultado[resultado["Investimento"] == investimento_selecionado]
    if curso_selecionado:
        resultado = resultado[resultado["Título do Curso / Evento"] == curso_selecionado]

    return resultado
