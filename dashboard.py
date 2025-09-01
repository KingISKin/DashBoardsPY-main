"""
Dashboard NOC - Streamlit
Configurações de página, estilo global, sidebar, footer e funções auxiliares.
"""

import os
import base64
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import warnings
from pathlib import Path

warnings.filterwarnings(
    "ignore", category=UserWarning, message="pandas only supports SQLAlchemy.*"
)

# =========================================================
# CONFIGURAÇÃO DE PÁGINA
# =========================================================
ICON_PNG = "img/chart_icon.png"
ICON_SVG = "img/chart_icon.svg"

def _pick_page_icon():
    if os.path.exists(ICON_PNG):
        return ICON_PNG
    if os.path.exists(ICON_SVG):
        return ICON_SVG
    return None

PAGE_ICON = _pick_page_icon()
st.set_page_config(
    page_title="NOC DASHBOARDS",
    layout="wide",
    page_icon=PAGE_ICON
)

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def get_base64_file(path: str) -> str:
    """Retorna o conteúdo do arquivo codificado em base64."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_data
def carregar_dados(path: str) -> pd.DataFrame:
    """Carrega Excel e converte coluna Data_Referencia em datetime."""
    df = pd.read_excel(path)
    if "Data_Referencia" in df.columns:
        df["Data_Referencia"] = pd.to_datetime(df["Data_Referencia"], errors="coerce")
    return df

def obter_data_util_anterior(base_date=None) -> datetime:
    """Retorna a última data útil (não domingo)."""
    if base_date is None:
        base_date = datetime.now()
    data = base_date - timedelta(days=1)
    while data.weekday() == 6:
        data -= timedelta(days=1)
    return data

# =========================================================
# ESTILO GLOBAL + SIDEBAR
# =========================================================
def aplicar_estilo_css(logo_path="img/KrownCode.png", pagina_ativa: str = "Home"):
    logo_b64 = get_base64_file(logo_path) if os.path.exists(logo_path) else None
    svg_favicon_tag = ""
    if os.path.exists(ICON_SVG):
        svg_b64 = get_base64_file(ICON_SVG)
        svg_favicon_tag = f"""<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{svg_b64}">"""

    st.markdown(f"""
        <style>
        header[data-testid="stHeader"] {{ background: transparent; }}
        .block-container {{ padding-top: 1rem; }}
        .stApp {{
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: #e2e8f0;
        }}
        h1, h2, h3 {{
            color: #e2e8f0;
            font-weight: 700;
        }}
        h1 {{ font-size: 2.2rem; }}
        h2 {{ font-size: 1.6rem; margin-top: 14px; }}
        h3 {{ font-size: 1.2rem; }}

        section[data-testid="stSidebar"] {{
            background: #1e293b;
            padding: 18px 12px 70px 12px;
        }}
        .sidebar-logo {{
            text-align: center;
            margin-bottom: 14px;
        }}
        .sidebar-logo img {{ width: 160px; }}
        .sidebar-title {{
            text-align: center;
            font-size: 1.2rem;
            letter-spacing: .5px;
            color: #e2e8f0;
            margin-bottom: 10px;
        }}

        .nav-item {{
            display: block;
            width: 100%;
            text-align: left;
            padding: 8px 10px;
            margin: 2px 0;
            background: transparent;
            border: none;
            color: #e2e8f0;
            font-weight: 500;
            cursor: pointer;
            border-radius: 6px;
        }}
        .nav-item:hover {{
            background: rgba(255,255,255,0.06);
        }}
        .nav-item.active {{
            color: #ef4444;
            text-decoration: underline;
        }}

        div[data-testid="stDataFrame"], div[data-testid="stPlotlyChart"] {{
            background: rgba(30,41,59,0.85);
            border-radius: 14px;
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 4px 18px rgba(0,0,0,0.35);
        }}

        .global-footer {{
            position: fixed;
            bottom: 10px;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 0.9rem;
            color: #94a3b8;
            pointer-events: none;
        }}
        </style>
        {svg_favicon_tag}
    """, unsafe_allow_html=True)

    with st.sidebar:
        if logo_b64:
            st.markdown(
                f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_b64}" /></div>',
                unsafe_allow_html=True
            )
        st.markdown('<div class="sidebar-title">Menu</div>', unsafe_allow_html=True)

def footer_global():
    st.markdown('<div class="global-footer">© JoãoVictor 2025</div>', unsafe_allow_html=True)

# =========================================================
#  NAVEGAÇÃO (botões transparentes, sem bolinha)
# =========================================================
MENU_ITEMS = [
    ("Home", "Home"),
    ("Checklist", "Checklist Diário"),
    ("Consorcio", "Coletas Consórcio"),
    ("Coletas", "Coletas Bancárias"),
    ("Hora", "Hora a Hora"),
    ("Help", "Help")
]

def sidebar_menu():
    # Estado inicial
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    # Renderiza os botões no sidebar
    for key, label in MENU_ITEMS:
        ativo = (st.session_state.page == key)
        btn_label = f"✅ {label}" if ativo else label

        if st.sidebar.button(btn_label, key=f"navbtn_{key}"):
            st.session_state.page = key
            # 🔄 força a atualização da página imediatamente
            st.rerun()


# =========================================================
#  PÁGINAS
# =========================================================
def pagina_home():
    st.set_page_config(page_title="NOC Dashboards - Home", layout="wide")

    # ======== Cabeçalho ========
    st.markdown(
        """
        <div style="text-align:center; padding:10px; border-radius:10px; color:#004080;">
            <h1 style="margin-bottom:5px; color:#004080;">Bem-vindo ao NOC Dashboards</h1>
            <p style="margin-top:0; color:#004080;">Tela inicial de monitoramento e análise prática de dados</p>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("\n")

    # ======== Introdução ========
    st.markdown(
        """
        <div style="background-color:#ffffff; padding:15px; border-radius:8px; border:1px solid #d9d9d9; color:#111111;">
        Esta aplicação foi desenvolvida para consolidar dados obtidos de um banco de dados, 
        gerar backups em planilhas para relatórios solicitados pelos clientes e permitir 
        que os dados sejam analisados de forma prática e eficiente.  
        
        O objetivo principal é fornecer visibilidade rápida de pendências, inconsistências ou falhas, 
        permitindo que o usuário identifique erros de forma imediata e tome ações corretivas rapidamente.
        </div>
        """, unsafe_allow_html=True
    )

    st.write("\n")

    # ======== Funcionamento do Código ========
    st.markdown("### ⚙️ Como o código funciona")
    st.markdown(
        """
        <div style="padding:10px; border-left: 5px solid #008000; background-color:#f9f9f9; border-radius:5px; color:#111111;">
        <ol>
            <li>Os dados são obtidos diretamente do banco de dados principal, garantindo consistência.</li>
            <li>Diariamente, backups são gerados em planilhas Excel para registro histórico e relatórios.</li>
            <li>As planilhas são usadas para análises rápidas e para atender demandas de relatórios ad hoc dos clientes.</li>
            <li>O código consolida dados de auditorias, volumetria e acionamentos horários, padronizando informações por empresa e layout.</li>
            <li>Todos os registros são tratados para identificar valores inconsistentes ou ausentes, permitindo filtrar rapidamente problemas.</li>
            <li>A interface do dashboard exibe alertas e informações de forma clara, priorizando eficiência e praticidade.</li>
        </ol>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("\n")

    # ======== Objetivo da Tela ========
    st.markdown("### 🎯 Objetivo desta Tela")
    st.markdown(
        """
        <div style="padding:10px; border-left: 5px solid #004080; background-color:#f9f9f9; border-radius:5px; color:#111111;">
        <ul>
            <li>Servir como uma tela de boas-vindas e explicativa do dashboard.</li>
            <li>Informar ao usuário como os dados são processados e disponibilizados.</li>
            <li>Reforçar a finalidade prática: identificar pendências e inconsistências de forma rápida.</li>
            <li>Orientar sobre o fluxo de dados: banco → planilhas → análise visual no dashboard.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )

    # ======== Rodapé ========
    st.write("\n")
    st.markdown(
        """
        <div style="text-align:center; font-size:12px; color:#555555; padding:10px; border-top:1px solid #d9d9d9;">
        Desenvolvido por João Victor
        </div>
        """, unsafe_allow_html=True
    )


    
def pagina_help():
    st.set_page_config(page_title="NOC Dashboards - Documentação", layout="wide")

    # ======== Cabeçalho ========
    st.markdown(
        """
        <div style="text-align:center; padding:10px; border-radius:10px; color:#fff;">
            <h1 style="margin-bottom:5px; color:#fff;">NOC DASHBOARDS</h1>
            <p style="margin-top:0; color:#fff;">Central de indicadores, auditorias e acompanhamento operacional</p>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("\n")

    # ======== Introdução ========
    st.markdown(
        """
        <div style="background-color:#ffffff; padding:15px; border-radius:8px; border:1px solid #d9d9d9; color:#111111;">
        <h3 style="color:#004080;">Bem-vindo ao portal de dashboards do NOC</h3>
        Esta aplicação acompanha e consolida dados de auditoria e volumetria simulados em banco SQLite profissional.
        Os dados são gerados desde o início de julho, contemplando regras específicas para consórcios e demais layouts.
        </div>
        """, unsafe_allow_html=True
    )

    st.write("\n")

    # ======== Estrutura do Banco ========
    st.markdown("### 🗄 Estrutura do Banco de Dados")
    st.markdown(
        """
        <div style="padding:10px; border-left: 5px solid #004080; background-color:#f9f9f9; border-radius:5px; color:#111111;">
        <ul>
            <li><b>__Consolidado_Hist:</b> histórico consolidado de consórcio (4 empresas fixas) e demais layouts (12 empresas), com quantidade de registros por dia e layout.</li>
            <li><b>Auditoria_LayoutNew:</b> registros de auditoria por empresa e layout, com datas diárias.</li>
            <li><b>input_Auditoria:</b> logs de auditoria diária, indicando se o valor está <b>Igual</b>, <b>Aumentou</b> ou <b>Reduziu</b>.</li>
            <li><b>__Empresa_X_input_Acionamentos:</b> tabelas horárias por empresa, com volumes por hora (08h-23h).</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("\n")

    # ======== Fluxo do ETL ========
    st.markdown("### ⚙️ Fluxo de ETL de Dados Fictícios")
    st.markdown(
        """
        <div style="padding:10px; border-left: 5px solid #008000; background-color:#f9f9f9; border-radius:5px; color:#111111;">
        <ol>
            <li>O ETL gera dados diariamente desde 01/07, ignorando domingos.</li>
            <li>Para consórcios, sempre são geradas 4 empresas fixas com volumes aleatórios.</li>
            <li>Para demais layouts, 12 empresas recebem volumes aleatórios.</li>
            <li>Alguns valores são propositalmente 0 para simular falhas ou ausência de dados.</li>
            <li>Auditoria é registrada em <b>Auditoria_LayoutNew</b> e <b>input_Auditoria</b> com diferença entre registros: Igual, Aumentou ou Reduziu.</li>
            <li>Acionamentos horários são gravados por empresa, com contagem de 08h até 23h.</li>
            <li>O ETL é executado centralmente, mantendo consistência e histórico no banco SQLite.</li>
        </ol>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("\n")

    # ======== Boas Práticas ========
    st.markdown("### ✅ Boas Práticas para Análise")
    st.markdown(
        """
        <div style="padding:10px; border-left: 5px solid #ff9900; background-color:#f9f9f9; border-radius:5px; color:#111111;">
        <ul>
            <li>Verifique que os filtros de empresa, layout e período estejam corretos.</li>
            <li>Valores 0 podem indicar ausência de dados; use filtros para identificar padrões.</li>
            <li>Use gráficos interativos para explorar variações horárias e diárias.</li>
            <li>Auditoria deve ser revisada periodicamente para identificar inconsistências.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("\n")

    # ======== FAQ ========
    st.markdown("### ❓ FAQ - Perguntas Frequentes")
    st.markdown(
        """
        <div style="padding:10px; border-left: 5px solid #cc0000; background-color:#f9f9f9; border-radius:5px; color:#111111;">
        <ul>
            <li><b>Não encontro uma empresa no filtro:</b> verifique se há registros para o período selecionado ou se a nomenclatura está padronizada (Empresa_1 a Empresa_12 e Empresa_A a D).</li>
            <li><b>Gráfico aparece vazio:</b> valores podem ser 0 ou filtro sem interseção entre datas e layouts.</li>
            <li><b>Como reportar inconsistências:</b> documente empresa, layout, data e evidências, e acione o fluxo do NOC.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )

    # ======== Rodapé ========
    st.write("\n")
    st.markdown(
        """
        <div style="text-align:center; font-size:12px; color:#555555; padding:10px; border-top:1px solid #d9d9d9;">
        Desenvolvido por João Victor
        </div>
        """, unsafe_allow_html=True
    )

def pagina_checklist():
    st.title("Checklist Diário")

    HISTORICO_PATH = "Relatorios_Checklist/historico_checklist.xlsx"
    if not os.path.exists(HISTORICO_PATH):
        st.warning(f"Arquivo de histórico não encontrado em '{HISTORICO_PATH}'.")
        return

    df = carregar_dados(HISTORICO_PATH)

    # Garantir que Data_Referencia é datetime
    df["Data_Referencia"] = pd.to_datetime(df["Data_Referencia"], errors="coerce")

    # ===========================
    # Filtros
    # ===========================
    st.subheader("Filtros")
    with st.container():
        c1, c2, c3 = st.columns(3, gap="small")
        filtro_selecionado = {}

        for idx, (col, nome, valores) in enumerate(zip(
            [c1, c2, c3],
            ["Empresa", "Layout", "Data"],
            [df["Empresa"], df["Layout"], df["Data_Referencia"].dt.date]
        )):
            with col:
                unique_vals = sorted(valores.dropna().astype(str).unique())
                with st.expander(nome):
                    selecionados = st.multiselect(
                        nome,
                        unique_vals,
                        default=unique_vals,
                        key=f"multiselect_{nome}_{idx}"
                    )
                    filtro_selecionado[nome] = selecionados

    # ===========================
    # Aplicar filtros
    # ===========================
    df_filtrado = df[
        (df["Empresa"].astype(str).isin(filtro_selecionado["Empresa"])) &
        (df["Layout"].astype(str).isin(filtro_selecionado["Layout"])) &
        (df["Data_Referencia"].dt.date.astype(str).isin(filtro_selecionado["Data"]))
    ]

    st.subheader("Dados em Análise")
    st.dataframe(df_filtrado, width='stretch')

    # ===========================
    # Pendências Diárias
    # ===========================
    st.subheader("Pendências Diárias")
    problemas_diario = df_filtrado[df_filtrado["Check Diario"] == "VALIDAR"]
    if not problemas_diario.empty:
        edited_diario = st.data_editor(
            problemas_diario[["Data_Referencia", "Empresa", "Layout", "Obs Check Diario", "Check Diario"]],
            width='stretch')
    else:
        st.success("✅ Tudo Feito! Sem erros nas Pendências Diárias.")
        edited_diario = pd.DataFrame()

    # ===========================
    # Pendências de Volumetria
    # ===========================
    st.subheader("Pendências de Volumetria")
    problemas_volum = df_filtrado[df_filtrado["Check Vol Cumulativa"] == "VALIDAR"]
    if not problemas_volum.empty:
        edited_volum = st.data_editor(
            problemas_volum[["Data_Referencia", "Empresa", "Layout", "Obs Vol Cumulativa", "Qnt_Ontem", "Qnt_Hoje", "Check Vol Cumulativa"]],
            width='stretch')
    else:
        st.success("✅ Tudo Feito! Sem erros nas Pendências de Volumetria.")
        edited_volum = pd.DataFrame()

    # ===========================
    # Botão para salvar alterações
    # ===========================
    if st.button("💾 Salvar alterações"):
        # Atualiza df original
        if not edited_diario.empty:
            for idx, row in edited_diario.iterrows():
                df_idx = df[
                    (df["Data_Referencia"] == row["Data_Referencia"]) &
                    (df["Empresa"] == row["Empresa"]) &
                    (df["Layout"] == row["Layout"])
                ].index
                df.loc[df_idx, ["Obs Check Diario", "Check Diario"]] = row[["Obs Check Diario", "Check Diario"]].values

        if not edited_volum.empty:
            for idx, row in edited_volum.iterrows():
                df_idx = df[
                    (df["Data_Referencia"] == row["Data_Referencia"]) &
                    (df["Empresa"] == row["Empresa"]) &
                    (df["Layout"] == row["Layout"])
                ].index
                df.loc[df_idx, ["Obs Vol Cumulativa", "Qnt_Ontem", "Qnt_Hoje", "Check Vol Cumulativa"]] = \
                    row[["Obs Vol Cumulativa", "Qnt_Ontem", "Qnt_Hoje", "Check Vol Cumulativa"]].values

        # Salva de volta no Excel
        df.to_excel(HISTORICO_PATH, index=False)
        st.success("✅ Alterações salvas com sucesso!")

    # ===========================
    # Observadas finais (não OK nem VALIDAR)
    # ===========================
    mask_obs_diario = ~df_filtrado["Check Diario"].isin(["OK", "VALIDAR"])
    mask_obs_volum = ~df_filtrado["Check Vol Cumulativa"].isin(["OK", "VALIDAR"])

    df_obs_diario = df_filtrado.loc[mask_obs_diario, ["Data_Referencia", "Empresa", "Layout", "Obs Check Diario", "Check Diario"]]
    df_obs_volum = df_filtrado.loc[mask_obs_volum, ["Data_Referencia", "Empresa", "Layout", "Obs Vol Cumulativa", "Check Vol Cumulativa"]]

    st.subheader("Observadas (Check Diario e Volumetria)")
    if not df_obs_diario.empty or not df_obs_volum.empty:
        st.dataframe(pd.concat([df_obs_diario, df_obs_volum], ignore_index=True), width='stretch')
    else:
        st.success("Nenhuma observação encontrada. Tudo OK ou VALIDAR!")

def carregar_dados(caminho_excel):
    if os.path.exists(caminho_excel):
        return pd.read_excel(caminho_excel)
    return pd.DataFrame()

def pagina_consorcio():
    st.title("Coletas Consórcio")

    HISTORICO_PATH = "Relatorios_validacao/tabela_consorcio.xlsx"
    if not os.path.exists(HISTORICO_PATH):
        st.info("Página em preparação. Arquivo 'Relatorios_validacao/tabela_consorcio.xlsx' não encontrado.")
        return

    df = carregar_dados(HISTORICO_PATH)
    if df.empty:
        st.warning("Nenhum dado disponível.")
        return

    # ===========================
    # Filtros dinâmicos
    # ===========================
    st.subheader("Filtros")
    with st.container():
        c1, c2 = st.columns(2, gap="small")
        filtro_selecionado = {}

        for col, nome, valores in zip([c1, c2], ["Layout", "Empresa"], [df["Layout"], df["dsNomeAssessoria"]]):
            with col:
                unique_vals = sorted(valores.dropna().astype(str).unique())
                with st.expander(nome):
                    selecionados = st.multiselect(nome, unique_vals, default=unique_vals)
                    filtro_selecionado[nome] = selecionados

    # Aplica filtros
    df_filtrado = df[
        (df["Layout"].astype(str).isin(filtro_selecionado["Layout"])) &
        (df["dsNomeAssessoria"].astype(str).isin(filtro_selecionado["Empresa"]))
    ]

    st.subheader("Tabela de Coletas (Filtrada)")
    st.dataframe(df_filtrado, width='stretch')

    # ===========================
    # Transformação para análise
    # ===========================
    colunas_datas = [c for c in df_filtrado.columns if c not in ["dsNomeAssessoria", "Layout"]]
    df_melted = df_filtrado.melt(
        id_vars=["dsNomeAssessoria", "Layout"],
        value_vars=colunas_datas,
        var_name="Data",
        value_name="Valor"
    )

    # Converte Valor para string para permitir edição livre
    df_melted["Valor"] = df_melted["Valor"].astype(str)
    df_melted["Data_str"] = df_melted["Data"].astype(str)

    # ===========================
    # Tabelas separadas por Layout
    # ===========================
    for layout in filtro_selecionado["Layout"]:
        st.subheader(f"Layout: {layout}")
        tabela_layout = df_filtrado[df_filtrado["Layout"] == layout].copy()
        st.dataframe(tabela_layout, width='stretch')

    # ===========================
    # Pendências (Valores Igual a 0)
    # ===========================
    st.subheader("Pendências (Valores Igual a 0)")
    df_zeros = df_melted[df_melted["Valor"] == "0"].copy()  # Apenas "0" exato

    if not df_zeros.empty:
        edited_zeros = st.data_editor(
            df_zeros[["dsNomeAssessoria", "Layout", "Data_str", "Valor"]].reset_index(drop=True),
            width='stretch',
            disabled=[]
        )
    else:
        st.success("Tudo certo por aqui, todas pendências encontradas")

def obter_data_util_hoje(base_date=None) -> datetime:
    if base_date is None:
        base_date = datetime.now()
    data = base_date
    if data.weekday() == 6:  # domingo
        data -= timedelta(days=2)  # volta para sexta
    return data

def pagina_hora():
    st.title("Hora a Hora")

    # Obtém a data de hoje como string YYYY-MM-DD
    hoje = obter_data_util_hoje().strftime("%Y-%m-%d")
    arquivo_excel = Path(f"./Relatorios_hora/Acionamentos_hora_{hoje}.xlsx")
    
    if not arquivo_excel.exists():
        st.info(f"Arquivo do dia {hoje} não encontrado: {arquivo_excel}")
        return

    st.success(f"Arquivo encontrado: {arquivo_excel}")

    # Carrega os dados
    df = pd.read_excel(arquivo_excel)
    if df.empty:
        st.warning("Nenhum dado disponível na planilha de hoje.")
        return

    # Normaliza nomes de colunas
    df.columns = df.columns.str.strip()

    # ===========================
    # Filtros dinâmicos
    # ===========================
    st.subheader("Filtros")
    filtro_selecionado = {}

    # Filtro Empresa
    c1, c2 = st.columns(2, gap="small")
    with c1:
        unique_empresas = sorted(df["Empresa"].dropna().astype(str).unique())
        with st.expander("Empresa"):
            selecionados = st.multiselect("Empresa", unique_empresas, default=unique_empresas)
            filtro_selecionado["Empresa"] = selecionados

    # Filtro Hora (colunas de 08 a 23)
    horas = [col for col in df.columns if col != "Empresa"]
    with c2:
        with st.expander("Hora"):
            selecionadas = st.multiselect("Hora", horas, default=horas)
            filtro_selecionado["Hora"] = selecionadas

    # ===========================
    # Monta DataFrame filtrado
    # ===========================
    df_filtrado = df[df["Empresa"].astype(str).isin(filtro_selecionado["Empresa"])]
    
    # Seleciona apenas as colunas de hora escolhidas
    df_filtrado = df_filtrado[["Empresa"] + filtro_selecionado["Hora"]]

    st.subheader(f"Tabela Hora a Hora ({hoje})")
    st.dataframe(df_filtrado, width='stretch')

    # ===========================
    # Pendências (Qtde igual a 0)
    # ===========================
    st.subheader("Pendências (Qtde = 0)")
    # Aqui assumindo que cada coluna de hora é uma quantidade
    colunas_qtde = [col for col in df_filtrado.columns if col != "Empresa"]
    df_zeros = df_filtrado[df_filtrado[colunas_qtde].eq(0).any(axis=1)]
    
    if not df_zeros.empty:
        edited_zeros = st.data_editor(
            df_zeros.reset_index(drop=True),
            width='stretch',
            disabled=[]
        )
    else:
        st.success("Tudo certo! Nenhum valor zero encontrado.")

def carregar_dados(caminho_excel):
    if os.path.exists(caminho_excel):
        return pd.read_excel(caminho_excel)
    return pd.DataFrame()

def pagina_coleta():
    st.title("Coletas Bancárias")

    HISTORICO_PATH = "Relatorios_validacao/tabela_bancaria_coleta.xlsx"
    if not os.path.exists(HISTORICO_PATH):
        st.info(f"Arquivo '{HISTORICO_PATH}' não encontrado.")
        return

    df = carregar_dados(HISTORICO_PATH)
    if df.empty:
        st.warning("Nenhum dado disponível.")
        return

    # ===========================
    # Filtros dinâmicos
    # ===========================
    st.subheader("Filtros")
    with st.container():
        c1, c2 = st.columns(2, gap="small")
        filtro_selecionado = {}

        for col, nome, valores in zip([c1, c2], ["Layout", "Empresa"], [df["Layout"], df["dsNomeAssessoria"]]):
            with col:
                unique_vals = sorted(valores.dropna().astype(str).unique())
                with st.expander(nome):
                    selecionados = st.multiselect(nome, unique_vals, default=unique_vals)
                    filtro_selecionado[nome] = selecionados

    # Aplica filtros
    df_filtrado = df[
        (df["Layout"].astype(str).isin(filtro_selecionado["Layout"])) &
        (df["dsNomeAssessoria"].astype(str).isin(filtro_selecionado["Empresa"]))
    ]

    st.subheader("Tabela de Coletas (Filtrada)")
    st.dataframe(df_filtrado, width='stretch')

    # ===========================
    # Tabelas separadas por Layout
    # ===========================
    for layout in filtro_selecionado["Layout"]:
        st.subheader(f"Layout: {layout}")
        tabela_layout = df_filtrado[df_filtrado["Layout"] == layout].copy()
        st.dataframe(tabela_layout, width='stretch', height=600)

    # Transformação para análise de pendências
    colunas_datas = [c for c in df_filtrado.columns if c not in ["dsNomeAssessoria", "Layout"]]
    df_melted = df_filtrado.melt(
        id_vars=["dsNomeAssessoria", "Layout"],
        value_vars=colunas_datas,
        var_name="Data",
        value_name="Valor"
    )
    df_melted["Data_str"] = df_melted["Data"].astype(str)

    # ===========================
    # Pendências (Valores 0)
    # ===========================
    st.subheader("Pendências (Valores Igual a 0)")
    df_zeros = df_melted[df_melted["Valor"] == 0].copy()
    df_zeros["Valor"] = df_zeros["Valor"].astype(str)

    if not df_zeros.empty:
        edited_zeros = st.data_editor(
            df_zeros[["dsNomeAssessoria", "Layout", "Data_str", "Valor"]].reset_index(drop=True),
            width='stretch',
            disabled=[]
        )
    else:
        st.success("Nenhum valor 0 encontrado para os filtros atuais.")
        edited_zeros = pd.DataFrame()

    # ===========================
    # Ausências / Valores de texto
    # ===========================
    st.subheader("Ausências Justificadas")
    df_ausencias = df_melted[(df_melted["Valor"].isna()) | (df_melted["Valor"].apply(lambda x: isinstance(x, str)))].copy()
    df_ausencias["Valor"] = df_ausencias["Valor"].astype(str) 

    if not df_ausencias.empty:
        edited_ausencias = st.data_editor(
            df_ausencias[["dsNomeAssessoria", "Layout", "Data_str", "Valor"]].reset_index(drop=True),
            width='stretch',
            disabled=[]
        )
    else:
        st.success("Nenhum valor de texto encontrado para os filtros atuais.")
        edited_ausencias = pd.DataFrame()

    # ===========================
    # Botão para salvar alterações
    # ===========================
    if st.button("💾 Salvar alterações"):
        # Atualiza df original com valores editados de zeros
        if not edited_zeros.empty:
            for idx, row in edited_zeros.iterrows():
                df_idx = df[
                    (df["Layout"] == row["Layout"]) &
                    (df["dsNomeAssessoria"] == row["dsNomeAssessoria"])
                ].index
                if row["Data_str"] in colunas_datas:
                    df.loc[df_idx, row["Data_str"]] = row["Valor"]

        # Atualiza df original com valores editados de ausências
        if not edited_ausencias.empty:
            for idx, row in edited_ausencias.iterrows():
                df_idx = df[
                    (df["Layout"] == row["Layout"]) &
                    (df["dsNomeAssessoria"] == row["dsNomeAssessoria"])
                ].index
                if row["Data_str"] in colunas_datas:
                    df.loc[df_idx, row["Data_str"]] = row["Valor"]

        # Salva no Excel
        df.to_excel(HISTORICO_PATH, index=False)
        st.success("✅ Alterações salvas com sucesso!")


def pagina_dts():
    st.title("Coletas DTS")
    st.info("Em desenvolvimento.")

# =========================================================
#  EXECUÇÃO
# =========================================================

def main():
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    # Estilo global + logo e título do sidebar
    aplicar_estilo_css(pagina_ativa=st.session_state.page)

    # Menu lateral (botões transparentes, sem bolinha)
    sidebar_menu()

    # Render da página
    page = st.session_state.page
    if page == "Ajuda":
        pagina_help()
    elif page == "Checklist":
        pagina_checklist()
    elif page == "Home":
        pagina_home()
    elif page == "Consorcio":
        pagina_consorcio()
    elif page == "Hora":
        pagina_hora()
    elif page == "Coletas":
        pagina_coleta()
    elif page == "DTS":
        pagina_dts()
    else:
        pagina_help()

    # Footer global
    footer_global()

if __name__ == "__main__":
    main()
