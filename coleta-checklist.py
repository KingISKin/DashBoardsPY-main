"""
Checklist diário de auditoria usando SQLite local existente.
Extrai dados do banco centralizado e gera relatórios diários e cumulativos.
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import sys

# ==========================
# Configurações iniciais
# ==========================

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Diretório base (funciona no exe e no script)
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

PASTA_RELATORIOS = BASE_DIR / "Relatorios_Checklist"
PASTA_RELATORIOS.mkdir(exist_ok=True)
HISTORICO_PATH = PASTA_RELATORIOS / "historico_checklist.xlsx"

# Layouts e empresas fictícias
LAYOUTS = ["Acionamentos", "Carteira", "Tempos"]
EMPRESAS = ['Empresa_1','Empresa_2','Empresa_3','Empresa_4','Empresa_5','Empresa_6',
            'Empresa_7','Empresa_8','Empresa_9','Empresa_10','Empresa_11','Empresa_12']

# Banco SQLite existente
DB_PATH = BASE_DIR / "banco_exp.sqlite"

# ==========================
# Funções auxiliares
# ==========================

def obter_data_util_anterior() -> datetime:
    """Retorna a última data útil (não domingo)."""
    data = datetime.now() - timedelta(days=1)
    while data.weekday() == 6:
        data -= timedelta(days=1)
    return data


def montar_checklist(conn: sqlite3.Connection, data_sql: str, data_sql_ontem: str) -> pd.DataFrame:
    """Gera DataFrame do checklist diário e cumulativo a partir de tabelas existentes."""
    checklist = []
    cursor = conn.cursor()

    for empresa_id, empresa_nome in enumerate(EMPRESAS, start=1):
        for layout in LAYOUTS:
            # Verifica status diário
            cursor.execute("""
                SELECT diferenca
                FROM input_Auditoria
                WHERE dtDataReferenciaEPS = ?
                  AND idCompanyDeep = ?
                  AND LayoutDeep = ?
                ORDER BY DeepInsert DESC
                LIMIT 1
            """, (data_sql, empresa_id, layout))
            row = cursor.fetchone()
            if row:
                status_input = "OK"
                status_hoje = "OK"
                diferenca = row[0]
                obs_input = "Dados encontrados"
            else:
                status_input = "VALIDAR"
                status_hoje = "VALIDAR"
                diferenca = "Igual"
                obs_input = f"Nenhum dado em {data_sql}"

            # Cumulativo
            cursor.execute("""
                SELECT COUNT(*) FROM Auditoria_LayoutNew
                WHERE IdCompany = ? AND layout = ? AND dtDataReferencia <= ?
            """, (empresa_id, layout, data_sql))
            cumulativo_hoje = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM Auditoria_LayoutNew
                WHERE IdCompany = ? AND layout = ? AND dtDataReferencia <= ?
            """, (empresa_id, layout, data_sql_ontem))
            cumulativo_ontem = cursor.fetchone()[0]

            if cumulativo_hoje == 0:
                status_cum = "VALIDAR"
                obs_cum = "Nenhum dado cumulativo na data referência"
            elif cumulativo_hoje > cumulativo_ontem:
                status_cum = "OK"
                obs_cum = f"Crescimento cumulativo: {cumulativo_ontem} -> {cumulativo_hoje}"
            else:
                status_cum = "VALIDAR"
                obs_cum = f"Sem crescimento cumulativo: {cumulativo_ontem} -> {cumulativo_hoje}"

            checklist.append({
                "Data_Referencia": data_sql,
                "Empresa": empresa_nome,
                "Layout": layout,
                "Obs Check Diario": obs_input,
                "Check Diario": status_hoje,
                "Obs Vol Cumulativa": obs_cum,
                "Qnt_Ontem": cumulativo_ontem,
                "Qnt_Hoje": cumulativo_hoje,
                "Diferenca": diferenca,
                "Check Vol Cumulativa": status_cum
            })

    df_checklist = pd.DataFrame(checklist)
    logging.info(f"Checklist diário gerado com {len(df_checklist)} registros.")
    return df_checklist


def atualizar_historico(df_dia: pd.DataFrame) -> pd.DataFrame:
    """Atualiza histórico em Excel, removendo duplicados do dia."""
    colunas_cumulativo = [
        "Data_Referencia", "Empresa", "Layout", "Obs Check Diario",
        "Check Diario", "Obs Vol Cumulativa", "Qnt_Ontem",
        "Qnt_Hoje", "Diferenca", "Check Vol Cumulativa"
    ]
    df_dia_filtrado = df_dia[colunas_cumulativo].copy()

    if HISTORICO_PATH.exists():
        df_hist = pd.read_excel(HISTORICO_PATH)
        df_hist = df_hist[df_hist['Data_Referencia'] != df_dia_filtrado['Data_Referencia'].iloc[0]]
        df_hist = pd.concat([df_hist, df_dia_filtrado], ignore_index=True)
    else:
        df_hist = df_dia_filtrado.copy()

    df_hist.to_excel(HISTORICO_PATH, index=False)
    logging.info(f"Histórico atualizado: {HISTORICO_PATH}")
    return df_hist


def gerar_relatorios(df_dia: pd.DataFrame, data_nome_arquivo: str) -> None:
    """Gera relatórios diários e cumulativos formatados em Excel."""
    relatorio_cumulativo = PASTA_RELATORIOS / f"relatorio_cumulativo_{data_nome_arquivo}.xlsx"
    relatorio_diario = PASTA_RELATORIOS / f"relatorio_diario_{data_nome_arquivo}.xlsx"

    # Relatório cumulativo
    colunas_cumulativo = [
        "Data_Referencia", "Empresa", "Layout", "Obs Vol Cumulativa",
        "Qnt_Ontem", "Qnt_Hoje", "Check Vol Cumulativa"
    ]
    with pd.ExcelWriter(relatorio_cumulativo, engine='xlsxwriter') as writer:
        df_dia.to_excel(writer, sheet_name='Checklist', index=False, columns=colunas_cumulativo)
        workbook = writer.book
        worksheet = writer.sheets['Checklist']
        formato_header = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
        worksheet.set_row(0, None, formato_header)

    # Relatório diário
    colunas_diario = ["Data_Referencia", "Empresa", "Layout", "Obs Check Diario", "Check Diario"]
    with pd.ExcelWriter(relatorio_diario, engine='xlsxwriter') as writer:
        df_dia.to_excel(writer, sheet_name='Checklist', index=False, columns=colunas_diario)
        workbook = writer.book
        worksheet = writer.sheets['Checklist']
        worksheet.set_row(0, None, formato_header)

    logging.info(f"Relatórios gerados: {relatorio_cumulativo} | {relatorio_diario}")


# ==========================
# Fluxo principal
# ==========================

def main():
    data_atual = obter_data_util_anterior()
    data_sql = data_atual.strftime('%Y-%m-%d')
    data_sql_ontem = (data_atual - timedelta(days=1)).strftime('%Y-%m-%d')
    data_nome_arquivo = data_atual.strftime('%d_%m_%Y')

    with sqlite3.connect(DB_PATH) as conn:
        df_dia = montar_checklist(conn, data_sql, data_sql_ontem)
        atualizar_historico(df_dia)
        gerar_relatorios(df_dia, data_nome_arquivo)


if __name__ == "__main__":
    main()
