import subprocess
import sys
import os
import logging
from pathlib import Path
from typing import List

# ==========================
# CONFIGURAÇÕES
# ==========================

# Base para caminhos (funciona tanto no script quanto no exe)
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))  # _MEIPASS é do PyInstaller

SCRIPTS: List[Path] = [
    BASE_DIR / "Criar_db.py",
    BASE_DIR / "consolida-dados.py",
    BASE_DIR / "coleta-consorcio.py",
    BASE_DIR / "coleta-bancaria.py",
    BASE_DIR / "coleta-checklist.py",
    BASE_DIR / "coleta-hora.py",
]

DASHBOARD_PATH = BASE_DIR / "dashboard.py"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# ==========================
# FUNÇÕES
# ==========================

def executar_script(script_path: Path) -> bool:
    """Executa um script Python e exibe a saída em tempo real."""
    if not script_path.exists():
        logging.error(f"Arquivo {script_path} não encontrado.")
        return False

    logging.info(f"Iniciando {script_path.name}...")

    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for linha in process.stdout:
        print(linha, end="")

    process.wait()

    if process.returncode != 0:
        logging.error(f"O script {script_path.name} falhou (código {process.returncode}).")
        return False

    logging.info(f"{script_path.name} concluído com sucesso.\n")
    return True

def executar_scripts_em_ordem(scripts: List[Path]) -> bool:
    """Executa uma lista de scripts Python em sequência."""
    for script in scripts:
        if not executar_script(script):
            logging.error("Execução interrompida.")
            return False
    return True

def iniciar_dashboard(dashboard_path: Path) -> None:
    """Inicia o Streamlit apontando para o dashboard."""
    if not dashboard_path.exists():
        logging.error(f"Arquivo {dashboard_path} não encontrado.")
        return

    logging.info("Iniciando dashboard no Streamlit...")
    # Usa cwd=BASE_DIR para que o Streamlit encontre arquivos relativos corretamente
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(dashboard_path)], cwd=BASE_DIR)

# ==========================
# MAIN
# ==========================

def main() -> None:
    """Fluxo principal da aplicação."""
    if executar_scripts_em_ordem(SCRIPTS):
        iniciar_dashboard(DASHBOARD_PATH)

if __name__ == "__main__":
    main()
