import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from sqlalchemy import create_engine
import logging
import time
import os

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/mercado_automotivo.db"

# --- Configurações ---
BASE_URL = (
    "https://www.icarros.com.br/ache/listaanuncios.jsp"
    "?ord=35&sop=nta_17|44|51.1_-mar_5.1_-mod_2794|2428.1_-esc_4.1_-sta_1.1_&grupoEspecial="
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
MAX_PAGINAS = 10
ESPERA_ENTRE_PAGINAS = 2

os.makedirs("data", exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}")

# --- Funções ---
def raspar_pagina(pagina: int) -> list[dict]:
    """Raspa uma página do iCarros e retorna lista de dicionários."""
    url = f"{BASE_URL}&pag={pagina}"
    logger.info(f"Raspando página {pagina}: {url}")

    try:
        resposta = requests.get(url, headers=HEADERS, timeout=10)
        resposta.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Falha na requisição da página {pagina}: {e}")
        return []

    sopa = BeautifulSoup(resposta.text, "html.parser")
    cards = sopa.find_all("li", class_="offer-card")

    if not cards:
        logger.warning(f"Página {pagina}: nenhum card encontrado. Fim da paginação.")
        return []

    registros = []
    for i, card in enumerate(cards):
        try:
            el_titulo = card.find("p", class_="label__neutral")
            el_preco  = card.find("p", string=re.compile(r"R\$"))
            el_ano    = card.find("p", class_="label__neutral-variant")
            el_km     = card.find("p", string=re.compile(r"Km"))

            if not el_titulo:
                continue

            titulo = el_titulo.text.strip()

            preco_limpo = 0.0
            if el_preco:
                texto = el_preco.text.replace(".", "").replace(",", ".")
                numeros = re.findall(r"\d+", texto)
                if numeros:
                    preco_limpo = float("".join(numeros)) / 100

            registros.append({
                "anuncio_id": card.get("data-anuncioid"),
                "modelo":     titulo,
                "preco":      preco_limpo,
                "ano":        el_ano.text.strip() if el_ano else "N/I",
                "km":         el_km.text.strip()  if el_km  else "0 Km",
            })

        except Exception as e:
            logger.error(f"Página {pagina}, card {i}: erro inesperado — {e}")
            continue

    logger.info(f"Página {pagina}: {len(registros)} registros extraídos.")
    return registros


def buscar_existentes(engine):
    """Busca anúncios já salvos no banco e retorna dicionário {anuncio_id: preco}."""
    try:
        df = pd.read_sql("SELECT anuncio_id, preco FROM historico_precos", con=engine)
        return df.set_index("anuncio_id")["preco"].to_dict()
    except Exception:
        logger.info("Tabela ainda não existe. Primeira execução — lookup vazio.")
        return {}


def filtrar_novos(anuncios_raspados, lookup):
    """Filtra anúncios, mantendo só os novos ou com preço alterado."""
    novos = []
    for anuncio in anuncios_raspados:
        anuncio_id = anuncio["anuncio_id"]
        preco      = anuncio["preco"]

        if anuncio_id not in lookup:
            # ID novo → inserir
            novos.append(anuncio)
        elif lookup[anuncio_id] != preco:
            # mesmo ID, preço mudou → inserir
            novos.append(anuncio)
        else:
            # duplicata real → ignorar
            logger.info(f"Ignorando duplicata: {anuncio_id}")

    return novos


def salvar_dados(registros: list[dict]) -> None:
    """Converte lista em DataFrame e salva no banco em lote."""
    df = pd.DataFrame(registros)
    df["data_coleta"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    df.to_sql(
        name="historico_precos",
        con=engine,
        if_exists="append",
        index=False
    )
    logger.info(f"{len(df)} registros salvos no banco.")


# --- Execução principal ---
def main():
    todos_registros = []

    for pagina in range(1, MAX_PAGINAS + 1):
        registros = raspar_pagina(pagina)

        if not registros:
            logger.info("Paginação encerrada — sem mais resultados.")
            break

        todos_registros.extend(registros)
        time.sleep(ESPERA_ENTRE_PAGINAS)

    if todos_registros:
        lookup = buscar_existentes(engine)
        novos  = filtrar_novos(todos_registros, lookup)

        if novos:
            salvar_dados(novos)
            logger.info(f"Coleta finalizada. Total: {len(novos)} registros novos.")
        else:
            logger.info("Nenhum registro novo. Tudo já estava no banco.")
    else:
        logger.warning("Nenhum dado coletado.")


if __name__ == "__main__":
    main()
