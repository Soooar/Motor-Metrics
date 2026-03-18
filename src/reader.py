import sqlite3
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/mercado_automotivo.db"

if not os.path.exists(DB_PATH):
    logger.error(f"Banco de dados não encontrado em '{DB_PATH}'. Execute o extrator primeiro.")
    exit(1)

logger.info(f"Conectando ao banco de dados em '{DB_PATH}'...")

conexao = None
try:
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM historico_precos ORDER BY data_coleta DESC")
    resultados = cursor.fetchall()

    if not resultados:
        logger.warning("Nenhum registro encontrado na tabela historico_precos.")
    else:
        logger.info(f"{len(resultados)} registros encontrados.\n")
        print(f"{'ID':<5} {'Modelo':<30} {'Preço':>12} {'Ano':<8} {'KM':<15} {'Data Coleta'}")
        print("-" * 80)
        for linha in resultados:
            print(f"{linha['id']:<5} {linha['modelo']:<30} R$ {linha['preco']:>9.2f} {linha['ano']:<8} {linha['km']:<15} {linha['data_coleta']}")

except sqlite3.Error as e:
    logger.error(f"Erro ao acessar o banco de dados: {e}")

finally:
    if conexao:
        conexao.close()
        logger.info("Conexão encerrada.")
