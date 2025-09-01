"""
Coleta e pivotagem de dados de layouts de auditoria usando SQLite local existente.
Extrai dados do banco 'banco_exp.sqlite' e gera Excel de pivotagem.
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import sqlite3
import sys

# ==========================
# Configurações iniciais
# ==========================

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Diretório base (funciona no exe e no script)
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

# Diretório e arquivo Excel
PASTA_RELATORIOS: Path = BASE_DIR / "Relatorios_validacao"
PASTA_RELATORIOS.mkdir(exist_ok=True)
CAMINHO_EXCEL: Path = PASTA_RELATORIOS / "tabela_bancaria_coleta.xlsx"

# Banco SQLite existente
DB_PATH = BASE_DIR / "banco_exp.sqlite"

# Layouts e empresas fictícias
LAYOUTS: List[str] = ["Acionamentos", "Carteira", "Tempos"]

# ==========================
# Funções auxiliares
# ==========================

def obter_datas_referencia(dias: int = 7) -> tuple[str, str]:
    """Retorna data de início e fim para filtro (últimos 'dias' dias, exceto hoje)."""
    hoje = datetime.now()
    data_inicio = (hoje - timedelta(days=dias)).strftime('%Y-%m-%d')
    data_fim = (hoje - timedelta(days=1)).strftime('%Y-%m-%d')
    logging.info(f"Período de análise: {data_inicio} até {data_fim}")
    return data_inicio, data_fim

def extrair_dados_sqlite(layouts: List[str], data_inicio: str, data_fim: str) -> pd.DataFrame:
    """Extrai dados do banco SQLite existente para os layouts e período especificados."""
    df_final = pd.DataFrame()
    with sqlite3.connect(DB_PATH) as conn:
        for layout in layouts:
            query = f"""
                SELECT *
                FROM __Consolidado_Hist
                WHERE dtDataReferencia >= '{data_inicio}'
                  AND dtDataReferencia <= '{data_fim}'
                  AND Layout = '{layout}'
            """
            df_layout = pd.read_sql(query, conn)
            df_final = pd.concat([df_final, df_layout], ignore_index=True)
    logging.info(f"{len(df_final)} registros extraídos do SQLite.")
    return df_final

def processar_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Cria pivot table: linhas = Empresa, Layout; colunas = dtDataReferencia; valores = Qtd."""
    if df.empty:
        logging.warning("DataFrame vazio. Nenhum dado para processar.")
        return df
    tabela = df.pivot_table(
        index=["dsNomeAssessoria", "Layout"],
        columns="dtDataReferencia",
        values="Qtd",
        aggfunc="sum"
    ).fillna(0).astype(int)
    tabela_reset = tabela.reset_index()
    logging.info("Pivot realizado com sucesso.")
    return tabela_reset

def salvar_excel(df: pd.DataFrame, caminho: Path) -> None:
    """Salva DataFrame em Excel, caso não esteja vazio."""
    if df.empty:
        logging.warning("DataFrame vazio. Nenhum arquivo gerado.")
        return
    df.to_excel(caminho, index=False)
    logging.info(f"Tabela salva em: {caminho}")

# ==========================
# Fluxo principal
# ==========================

def main():
    data_inicio, data_fim = obter_datas_referencia()
    df = extrair_dados_sqlite(LAYOUTS, data_inicio, data_fim)
    if df.empty:
        logging.info("Nenhum dado retornado. Encerrando script.")
        return
    tabela_final = processar_pivot(df)
    salvar_excel(tabela_final, CAMINHO_EXCEL)

if __name__ == "__main__":
    main()
