"""
Extração e pivot de consórcio usando SQLite existente.
Lê dados do banco centralizado e gera Excel final.
"""

import logging
from pathlib import Path
import pandas as pd
import sqlite3
import sys

# ==========================
# Configurações iniciais
# ==========================

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Diretório base (funciona no exe e no script)
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

PASTA_RELATORIOS = BASE_DIR / "Relatorios_validacao"
PASTA_RELATORIOS.mkdir(exist_ok=True)
CAMINHO_EXCEL = PASTA_RELATORIOS / "tabela_consorcio.xlsx"

EMPRESAS_CONSORCIO = ["Empresa_A", "Empresa_B", "Empresa_C", "Empresa_D"]

# Banco SQLite existente (unificado/centralizado)
DB_PATH = BASE_DIR / "banco_exp.sqlite"

# ==========================
# Funções auxiliares
# ==========================

def extrair_dados() -> pd.DataFrame:
    """Extrai dados do banco SQLite apenas das empresas do consórcio."""
    empresas_str = ",".join(f"'{e}'" for e in EMPRESAS_CONSORCIO)  # transforma lista em string SQL
    query = f"""
        SELECT *
        FROM __Consolidado_Hist
        WHERE dsNomeAssessoria IN ({empresas_str})
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(query, conn)
    logging.info(f"{len(df)} registros extraídos do banco local para empresas do consórcio.")
    return df


def processar_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Realiza pivot table."""
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
    tabela_reset['dsNomeAssessoria'] = tabela_reset['dsNomeAssessoria'].ffill()
    tabela_reset['Layout'] = tabela_reset['Layout'].ffill()

    logging.info("Pivot realizado com sucesso.")
    return tabela_reset


def salvar_excel(df: pd.DataFrame, caminho: Path) -> None:
    """Salva DataFrame em Excel."""
    if df.empty:
        logging.warning("DataFrame vazio. Nenhum arquivo gerado.")
        return
    df.to_excel(caminho, index=False)
    logging.info(f"Tabela salva em: {caminho}")


# ==========================
# Fluxo principal
# ==========================

def main() -> None:
    df = extrair_dados()
    if df.empty:
        logging.info("Nenhum dado retornado. Encerrando script.")
        return

    tabela_final = processar_pivot(df)
    salvar_excel(tabela_final, CAMINHO_EXCEL)


if __name__ == "__main__":
    main()
