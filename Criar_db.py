"""
Banco SQLite profissional para protótipo de auditoria e consórcio.
Todas as datas em formato YYYY-MM-DD.
Estrutura limpa, tipos corretos, sem campos desnecessários.
Serve como base para alimentar todos os ETLs futuros.
"""

import sqlite3
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

# ==========================================
# CONFIGURAÇÃO DO BANCO
# ==========================================
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
DB_PATH = BASE_DIR / "banco_exp.sqlite"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ==========================================
# CRIAÇÃO DAS TABELAS
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Auditoria_LayoutNew (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    IdCompany INTEGER NOT NULL,
    Layout TEXT NOT NULL,
    dtDataReferencia DATE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS input_Auditoria (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    idCompanyDeep INTEGER NOT NULL,
    LayoutDeep TEXT NOT NULL,
    dtDataReferenciaEPS DATE NOT NULL,
    diferenca TEXT NOT NULL CHECK(diferenca IN ('Igual','Aumentou','Reduziu')),
    DeepInsert DATETIME NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS __Consolidado_Hist (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    dtDataReferencia DATE NOT NULL,
    dsNomeAssessoria TEXT NOT NULL,
    IdCompany INTEGER NOT NULL,
    Qtd INTEGER NOT NULL,
    Layout TEXT NOT NULL,
    Data_Coleta DATE NOT NULL
)
""")

EMPRESAS_HORA = [f"Empresa_{i}" for i in range(1, 13)]
for empresa in EMPRESAS_HORA:
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS __{empresa}_input_Acionamentos (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        dtDataReferencia DATE NOT NULL,
        hrHoraInicio TEXT NOT NULL,
        Qtde INTEGER NOT NULL
    )
    """)

conn.commit()
conn.close()
logging.info(f"Banco profissional criado com sucesso: {DB_PATH}")
