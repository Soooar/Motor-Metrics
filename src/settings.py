import os
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "mercado_automotivo.db"))
DB_URL  = f"sqlite:///{DB_PATH}"

TABELA_RAW   = "historico_precos"
TABELA_CLEAN = "historico_precos_limpo"

BASE_URL = (
    "https://www.icarros.com.br/ache/listaanuncios.jsp?bid=1&sop=esc_4.1_-rai_50.1_-kmm_1.1_-"
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
MAX_PAGINAS          = int(os.getenv("MAX_PAGINAS", 10))
ESPERA_ENTRE_PAGINAS = float(os.getenv("ESPERA_ENTRE_PAGINAS", 2.0))

MODELO_FILTRO = os.getenv("MODELO_FILTRO", "")

LOG_LEVEL  = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    return logging.getLogger(name)
