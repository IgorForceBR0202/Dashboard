# -*- coding: utf-8 -*-
"""
utils.py
--------
Pequenas funções utilitárias, principalmente de formatação numérica no
padrão brasileiro (separador de milhar "." e decimal ",").
"""


def format_int_br(valor) -> str:
    """Formata um inteiro no padrão brasileiro. Ex.: 2124 -> '2.124'."""
    try:
        valor = int(round(float(valor)))
    except (TypeError, ValueError):
        return "0"
    return f"{valor:,}".replace(",", ".")


def format_float_br(valor, casas: int = 1) -> str:
    """Formata um número decimal no padrão brasileiro. Ex.: 35.4 -> '35,4'."""
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return "0,0"
    texto = f"{valor:,.{casas}f}"
    texto = texto.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    return texto
