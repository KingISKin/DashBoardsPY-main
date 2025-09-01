"""
ETL completo para protótipo de auditoria e consórcio.
Alimenta todas as tabelas do banco profissional com dados fictícios.
Inclui alguns erros simulados (0s) e diferenças de auditoria.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# ==========================================
# Caminho do banco
# ==========================================
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
DB_PATH = BASE_DIR / "banco_exp.sqlite"

# Layouts e empresas
LAYOUTS_CONSORCIO = ["Consorcio"]
LAYOUTS_DEMAIS = ["Acionamentos", "Carteira", "Tempos"]
EMPRESAS_CONSORCIO = ["Empresa_A", "Empresa_B", "Empresa_C", "Empresa_D"]
EMPRESAS_DEMAIS = [f"Empresa_{i}" for i in range(1, 13)]

HORAS = [f"{h:02d}:00" for h in range(8, 24)]  # 08h até 23h

# Datas de 01/07 até hoje (ignora domingos)
start_date = datetime(datetime.now().year, 7, 1)
end_date = datetime.now() - timedelta(days=1)
datas = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)
         if (start_date + timedelta(days=i)).weekday() != 6]

# ==========================
# Funções auxiliares
# ==========================

def inserir_consolidado(cursor):
    registros = []
    for dt_ref in datas:
        # Consórcio
        for empresa_id, empresa in enumerate(EMPRESAS_CONSORCIO, start=1):
            qtd = random.choice([0, random.randint(5, 50)])  # Alguns zeros
            registros.append((dt_ref.strftime("%Y-%m-%d"), empresa, empresa_id, qtd, "Consorcio",
                              datetime.now().strftime("%Y-%m-%d")))

        # Demais layouts
        for layout in LAYOUTS_DEMAIS:
            for empresa_id, empresa in enumerate(EMPRESAS_DEMAIS, start=1):
                qtd = random.choice([0, random.randint(0, 30)])
                registros.append((dt_ref.strftime("%Y-%m-%d"), empresa, empresa_id, qtd, layout,
                                  datetime.now().strftime("%Y-%m-%d")))

    cursor.executemany("""
        INSERT INTO __Consolidado_Hist
        (dtDataReferencia, dsNomeAssessoria, IdCompany, Qtd, Layout, Data_Coleta)
        VALUES (?, ?, ?, ?, ?, ?)
    """, registros)
    logging.info(f"{len(registros)} registros inseridos em __Consolidado_Hist.")

def inserir_auditoria_layoutnew(cursor):
    registros = []
    for dt_ref in datas:
        for layout in LAYOUTS_DEMAIS + LAYOUTS_CONSORCIO:
            for empresa_id in range(1, 13):
                registros.append((empresa_id, layout, dt_ref.strftime("%Y-%m-%d")))
    cursor.executemany("""
        INSERT INTO Auditoria_LayoutNew (IdCompany, Layout, dtDataReferencia)
        VALUES (?, ?, ?)
    """, registros)
    logging.info(f"{len(registros)} registros inseridos em Auditoria_LayoutNew.")

def inserir_input_auditoria(cursor):
    registros = []
    for dt_ref in datas:
        for layout in LAYOUTS_DEMAIS + LAYOUTS_CONSORCIO:
            for empresa_id in range(1, 13):
                diferenca = random.choice(["Igual", "Aumentou", "Reduziu"])
                registros.append((empresa_id, layout, dt_ref.strftime("%Y-%m-%d"), diferenca,
                                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    cursor.executemany("""
        INSERT INTO input_Auditoria (idCompanyDeep, LayoutDeep, dtDataReferenciaEPS, diferenca, DeepInsert)
        VALUES (?, ?, ?, ?, ?)
    """, registros)
    logging.info(f"{len(registros)} registros inseridos em input_Auditoria.")

def inserir_acionamentos_hora(cursor):
    for empresa in EMPRESAS_DEMAIS:
        registros = []
        for dt_ref in datas:
            for hora in HORAS:
                qtd = random.choice([0, random.randint(0, 10)])
                registros.append((dt_ref.strftime("%Y-%m-%d"), hora, qtd))

        cursor.executemany(f"""
            INSERT INTO __{empresa}_input_Acionamentos (dtDataReferencia, hrHoraInicio, Qtde)
            VALUES (?, ?, ?)
        """, registros)
        logging.info(f"{len(registros)} registros inseridos em __{empresa}_input_Acionamentos.")

# ==========================
# Execução ETL
# ==========================
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

inserir_consolidado(cursor)
inserir_auditoria_layoutnew(cursor)
inserir_input_auditoria(cursor)
inserir_acionamentos_hora(cursor)

conn.commit()
conn.close()
logging.info("ETL completo concluído com sucesso.")
