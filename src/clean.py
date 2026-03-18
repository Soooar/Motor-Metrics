import sqlite3
import logging
import os

# --- Configuração de logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/mercado_automotivo.db"
MODELO_FILTRO = "Onix"

# --- Verifica se o banco existe antes de tentar limpar ---
if not os.path.exists(DB_PATH):
    logger.error(f"Banco de dados não encontrado em '{DB_PATH}'. Execute o extrator primeiro.")
    exit(1)

logger.info(f"Conectando ao banco de dados em '{DB_PATH}'...")

try:
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM historico_precos WHERE modelo NOT LIKE ?",
        (f"%{MODELO_FILTRO}%",)
    )
    conexao.commit()
    logger.info(f"Limpeza concluída. Registros removidos: {conexao.total_changes}")

except sqlite3.Error as e:
    logger.error(f"Erro ao acessar o banco de dados: {e}")

finally:
    conexao.close()
    logger.info("Conexão encerrada.")
