# -*- coding: utf-8 -*-
"""
app.py
------
Ponto de entrada da aplicação. Cria a instância do Dash, define o layout
e registra os callbacks. Pode ser executado localmente com:

    python app.py

Para publicação em servidores WSGI (Render, Railway, PythonAnywhere, etc.)
a variável `server` (Flask) exposta neste módulo é o objeto que deve ser
apontado pelo servidor WSGI/Gunicorn (ex.: `gunicorn app:server`).
"""

import dash
import dash_bootstrap_components as dbc

from callbacks import register_callbacks
from layout import build_layout

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="EMEDI | Dashboard de Capacitações e Eventos",
    update_title=None,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# Objeto exigido por servidores WSGI (Gunicorn, etc.) em produção.
server = app.server

app.layout = build_layout()

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
