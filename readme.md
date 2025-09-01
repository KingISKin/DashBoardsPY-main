# NOC DASHBOARDS - Sistema de Auditoria e Consórcio

Sistema completo de **auditoria, coleta de dados e relatórios**, desenvolvido em **Python** com **SQLite** e **Streamlit**, que gera dashboards interativos e relatórios automatizados em Excel.

O projeto foi pensado para prototipagem profissional e integração futura com processos ETL e auditorias de consórcios, acionamentos e outros layouts.

---

## **📁 Estrutura do Projeto**

```
.
├── banco_exp.sqlite             # Banco SQLite centralizado
├── Criar_db.py                  # Cria todas as tabelas do banco
├── consolida-dados.py           # ETL que preenche o banco com dados fictícios
├── coleta-consorcio.py          # Extração e pivotagem de consórcio
├── coleta-bancaria.py           # Extração e pivotagem de layouts gerais
├── coleta-checklist.py          # Geração de checklist diário e relatórios cumulativos
├── coleta-hora.py               # Extração horária de acionamentos
├── dashboard.py                 # Interface Streamlit do NOC Dashboards
├── main.py                      # Script principal que chama todos os módulos
├── img/                         # Imagens usadas no dashboard
│   ├── chart_icon.png
│   └── KrownCode.png
├── Relatorios_Checklist/        # Armazena relatórios de checklist diário
├── Relatorios_hora/             # Armazena relatórios de acionamentos por hora
└── Relatorios_validacao/        # Armazena relatórios de consórcio e outros layouts
```

---

## **⚙️ Funcionalidades**

1. **Banco de dados profissional** (`banco_exp.sqlite`):

   * Tabelas de auditoria de layouts por empresa
   * Logs de auditoria diária
   * Histórico consolidado de consórcios e outros layouts
   * Tabelas horárias de acionamentos por empresa

2. **ETL completo** (`consolida-dados.py`):

   * Alimenta todas as tabelas do banco com dados fictícios
   * Simula diferenças de auditoria
   * Insere acionamentos horários e consolida layouts

3. **Extração e pivotagem de dados**:

   * `coleta-consorcio.py` → Pivotagem de dados de consórcio
   * `coleta-bancaria.py` → Pivotagem de layouts gerais
   * `coleta-hora.py` → Relatórios horários de acionamentos
   * `coleta-checklist.py` → Checklist diário e relatórios cumulativos

4. **Dashboard interativo** (`dashboard.py`):

   * Desenvolvido em Streamlit
   * Visualização de gráficos, tabelas e métricas
   * Layout moderno com tema escuro, cards e logotipo
   * Navegação intuitiva pelo sidebar

5. **Executável** (`main.exe`):

   * Abre diretamente no navegador
   * Integra todos os scripts automaticamente
   * Não exibe tela preta do terminal

---

## **🚀 Como usar**
Apenas rodar?
Basta abrir seu terminal no ambiente virtual e utilizar a seguinte
linha de comando:
  ```bash
  python main.py
  ```
### **1. Pré-requisitos**

* Python 3.10 ou superior
* Bibliotecas:

  ```bash
  pip install pandas streamlit plotly openpyxl xlsxwriter
  ```

### **2. Estrutura de pastas**

Certifique-se de que as pastas e arquivos estejam conforme o layout:

```
img/
Relatorios_Checklist/
Relatorios_hora/
Relatorios_validacao/
banco_exp.sqlite
```

### **3. Criar o banco de dados**

```bash
python Criar_db.py
```

### **4. Rodar ETL para popular o banco**

```bash
python consolida-dados.py
```

### **5. Gerar relatórios**

* Consórcio:

```bash
python coleta-consorcio.py
```

* Layouts gerais:

```bash
python coleta-bancaria.py
```

* Checklist diário:

```bash
python coleta-checklist.py
```

* Acionamentos por hora:

```bash
python coleta-hora.py
```

### **6. Abrir o dashboard**

* Com Python:

```bash
python main.py
```

* Com executável:
* Clique no arquivo `main.exe` e aguarde abrir o navegador com o dashboard.

---

## **📌 Observações importantes**

* Certifique-se de manter a estrutura de pastas e nomes dos arquivos conforme descrito.
* Os relatórios são gerados automaticamente nas pastas correspondentes.
* O dashboard funciona melhor com Chrome, Edge ou Firefox.
* Para atualizar dados, execute os scripts ETL antes de abrir o dashboard.

---

## **💡 Contato**

Desenvolvedor: João Victor Nunes
Ano: 2025
GitHub: \[Seu perfil GitHub aqui]
