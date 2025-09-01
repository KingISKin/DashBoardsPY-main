"""
Extração horária de acionamentos usando SQLite existente.
Atualiza Excel incrementalmente apenas com dados reais do banco centralizado.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
import sys

# ==========================
# Configurações iniciais
# ==========================

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Diretório base (funciona no exe e no script)
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

PASTA_RELATORIOS = BASE_DIR / "Relatorios_hora"
PASTA_RELATORIOS.mkdir(exist_ok=True)

EMPRESAS = [f'Empresa_{i}' for i in range(1, 13)]

# Banco SQLite existente (centralizado)
DB_PATH = BASE_DIR / "banco_exp.sqlite"

# ==========================
# Funções auxiliares
# ==========================

def consultar_empresa(conn, empresa, data_referencia):
    """Retorna DataFrame pivotado por hora de acionamentos."""
    df = pd.read_sql(f"""
        SELECT hrHoraInicio AS Hora, SUM(Qtde) AS Qtde
        FROM __{empresa}_input_Acionamentos
        WHERE dtDataReferencia >= '{data_referencia}'
        GROUP BY hrHoraInicio
    """, conn)
    if df.empty:
        return pd.DataFrame()
    df_pivot = df.pivot_table(index=None, columns="Hora", values="Qtde", fill_value=0)
    df_pivot.insert(0, 'Empresa', empresa)
    return df_pivot

def atualizar_excel_incremental(arquivo_excel):
    """Atualiza o Excel incrementando dados do dia."""
    try:
        df_existente = pd.read_excel(arquivo_excel)
    except FileNotFoundError:
        df_existente = pd.DataFrame()

    data_referencia = datetime.today().strftime('%Y-%m-%d')

    with sqlite3.connect(DB_PATH) as conn:
        all_data = []
        for empresa in EMPRESAS:
            try:
                df = consultar_empresa(conn, empresa, data_referencia)
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                logging.error(f"Erro ao consultar {empresa}: {e}")

        if all_data:
            df_novo = pd.concat(all_data, ignore_index=True)
            if not df_existente.empty:
                df_final = pd.concat([df_existente, df_novo], ignore_index=True).drop_duplicates()
            else:
                df_final = df_novo

            df_final.to_excel(arquivo_excel, index=False)
            logging.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Excel atualizado com novos dados.")
        else:
            logging.info("Nenhum dado novo encontrado para atualização.")

# ==========================
# Fluxo principal
# ==========================

def main():
    hoje = datetime.today().strftime('%Y-%m-%d')
    arquivo_excel = PASTA_RELATORIOS / f"Acionamentos_hora_{hoje}.xlsx"
    atualizar_excel_incremental(arquivo_excel)

if __name__ == "__main__":
    main()
