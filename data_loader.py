# -*- coding: utf-8 -*-
"""
data_loader.py
----------------
Responsável por carregar o arquivo Excel "Relatorio_Capacitacoes_EMEDI.xlsx"
e aplicar todo o tratamento/normalização necessário para o dashboard.

IMPORTANTE:
- O arquivo Excel original NUNCA é alterado.
- Toda a padronização ocorre apenas no DataFrame em memória usado pelo dashboard.
- Nenhum valor é inventado: apenas normalizamos grafias diferentes do mesmo
  conceito (ex.: "Híbrida" e "Híbrido") e tipos de dados (texto -> número/data).
"""

import os
from datetime import datetime

import pandas as pd

# Caminho do arquivo de dados. Pode ser substituído por uma versão atualizada
# mantendo o mesmo nome e local, sem necessidade de alterar o código.
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "exemplo_dados_EMEDI_ficticios.xlsx")
SHEET_NAME = "RT Capacitações e Eventos"

# Coluna auxiliar que NÃO deve ser usada como indicador.
COLUNA_AUXILIAR_IGNORAR = "Unnamed: 8"

# Mapas de normalização (apenas grafias diferentes do mesmo valor).
MODALIDADE_MAP = {
    "híbrida": "Híbrido",
    "híbrido": "Híbrido",
    "online (ao vivo)": "Online ao vivo",
    "online ao vivo": "Online ao vivo",
    "telepresencial": "Telepresencial",
    "presencial": "Presencial",
}

STATUS_MAP = {
    "aberto": "ABERTO",
    "fechado": "FECHADO",
}

INVESTIMENTO_MAP = {
    "gratuito": "GRATUITO",
    "pago": "PAGO",
}


def _normalize_text_series(serie: pd.Series, mapping: dict, default_upper: bool = True) -> pd.Series:
    """Normaliza uma série de texto usando um dicionário de mapeamento.

    A comparação é feita ignorando espaços extras e maiúsculas/minúsculas,
    mas o valor final exibido segue o padrão definido no `mapping`.
    """
    def _map_value(v):
        if pd.isna(v):
            return v
        key = str(v).strip().lower()
        if key in mapping:
            return mapping[key]
        # Se não houver mapeamento explícito, apenas limpa espaços.
        cleaned = str(v).strip()
        return cleaned.upper() if default_upper else cleaned

    return serie.apply(_map_value)


def get_file_last_modified() -> datetime:
    """Retorna a data/hora de última modificação do arquivo Excel."""
    try:
        ts = os.path.getmtime(DATA_PATH)
        return datetime.fromtimestamp(ts)
    except OSError:
        return datetime.now()


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Carrega e trata os dados da aba 'RT Capacitações e Eventos'.

    Passos de tratamento (todos aplicados apenas no DataFrame em memória):
      1. Remoção de espaços extras dos nomes das colunas.
      2. Remoção da coluna auxiliar "Unnamed: 8".
      3. Conversão de "Inscrições" para número inteiro.
      4. Conversão de "data de inicio" para datetime.
      5. Normalização de Status, Investimento e Modalidade.
      6. Remoção de espaços extras em campos de texto.
    """
    df = pd.read_excel(path, sheet_name=SHEET_NAME)

    # 1. Remove espaços extras dos nomes das colunas.
    df.columns = [str(c).strip() for c in df.columns]

    # 2. Remove a coluna auxiliar, se existir.
    if COLUNA_AUXILIAR_IGNORAR in df.columns:
        df = df.drop(columns=[COLUNA_AUXILIAR_IGNORAR])

    # Garante que as colunas essenciais existam.
    colunas_esperadas = [
        "Tipo", "Título do Curso / Evento", "Inscrições", "Status",
        "Modalidade", "Datas Detalhadas", "Investimento", "data de inicio",
    ]
    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = pd.NA

    # 3. Inscrições -> número inteiro (valores ausentes viram 0, sem inventar
    #    dados: apenas garante que a coluna seja numérica para soma/gráficos).
    df["Inscrições"] = pd.to_numeric(df["Inscrições"], errors="coerce").fillna(0).astype(int)

    # 4. data de inicio -> datetime.
    df["data de inicio"] = pd.to_datetime(df["data de inicio"], errors="coerce")

    # 5. Normalização de texto.
    for col in ["Tipo", "Título do Curso / Evento", "Datas Detalhadas"]:
        df[col] = df[col].apply(lambda v: str(v).strip() if pd.notna(v) else v)

    df["Status"] = _normalize_text_series(df["Status"], STATUS_MAP)
    df["Investimento"] = _normalize_text_series(df["Investimento"], INVESTIMENTO_MAP)
    df["Modalidade"] = _normalize_text_series(df["Modalidade"], MODALIDADE_MAP, default_upper=False)

    # Coluna auxiliar de ano/mês, útil para agrupamentos temporais.
    df["Ano"] = df["data de inicio"].dt.year
    df["Mes"] = df["data de inicio"].dt.to_period("M").astype(str)

    return df


# Carrega os dados uma única vez na inicialização da aplicação.
DF = load_data()
FILE_LAST_MODIFIED = get_file_last_modified()
