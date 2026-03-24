import re
import time

import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine

from settings import (
    BASE_URL, HEADERS, MAX_PAGINAS, ESPERA_ENTRE_PAGINAS,
    DB_URL, TABELA_RAW, get_logger,
)

logger = get_logger(__name__)


def _parsear_preco(texto: str) -> float:
    limpo = texto.replace("R$", "").strip().replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return 0.0


def _parsear_km(texto: str) -> float:
    limpo = texto.replace("Km", "").replace(".", "").strip()
    try:
        return float(limpo)
    except ValueError:
        return 0.0


def raspar_pagina(pagina: int) -> list[dict]:
    url = f"{BASE_URL}&pag={pagina}"
    logger.info(f"Raspando página {pagina}: {url}")

    try:
        resposta = requests.get(url, headers=HEADERS, timeout=10)
        resposta.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Falha na requisição da página {pagina}: {e}")
        return []

    sopa  = BeautifulSoup(resposta.text, "html.parser")
    cards = sopa.find_all("li", class_="offer-card")

    if not cards:
        logger.warning(f"Página {pagina}: nenhum card encontrado. Fim da paginação.")
        return []

    registros = []
    for i, card in enumerate(cards):
        try:
            anuncio_id = card.get("data-anuncioid")
            if not anuncio_id:
                logger.debug(f"Página {pagina}, card {i}: sem anuncio_id — ignorado.")
                continue

            el_titulo = card.find("p", class_="label__neutral")
            el_preco  = card.find("p", string=re.compile(r"R\$"))
            el_ano    = card.find("p", class_="label__neutral-variant")
            el_km     = card.find("p", string=re.compile(r"Km"))

            if not el_titulo:
                continue

            registros.append({
                "anuncio_id": anuncio_id,
                "modelo":     el_titulo.text.strip(),
                "preco":      _parsear_preco(el_preco.text) if el_preco else 0.0,
                "ano":        el_ano.text.strip() if el_ano else "N/I",
                "km":         _parsear_km(el_km.text) if el_km else 0.0,
            })

        except Exception as e:
            logger.error(f"Página {pagina}, card {i}: erro inesperado — {e}")
            continue

    logger.info(f"Página {pagina}: {len(registros)} registros extraídos.")
    return registros


def buscar_existentes(engine) -> dict[str, float]:
    try:
        df = pd.read_sql(f"SELECT anuncio_id, preco FROM {TABELA_RAW}", con=engine)
        return df.set_index("anuncio_id")["preco"].to_dict()
    except Exception:
        logger.info("Tabela ainda não existe. Primeira execução — lookup vazio.")
        return {}


def filtrar_novos(anuncios: list[dict], lookup: dict[str, float]) -> list[dict]:
    novos = []
    for anuncio in anuncios:
        aid   = anuncio["anuncio_id"]
        preco = anuncio["preco"]

        if aid not in lookup or lookup[aid] != preco:
            novos.append(anuncio)
        else:
            logger.debug(f"Duplicata ignorada: {aid}")

    return novos


def salvar_dados(registros: list[dict], engine) -> None:
    df = pd.DataFrame(registros)
    df["data_coleta"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    df.to_sql(name=TABELA_RAW, con=engine, if_exists="append", index=False)
    logger.info(f"{len(df)} registros salvos em '{TABELA_RAW}'.")


def main() -> None:
    logger.info("=== INICIANDO EXTRAÇÃO ===")
    engine = create_engine(DB_URL)
    todos: list[dict] = []

    for pagina in range(1, MAX_PAGINAS + 1):
        registros = raspar_pagina(pagina)
        if not registros:
            logger.info("Paginação encerrada — sem mais resultados.")
            break
        todos.extend(registros)
        time.sleep(ESPERA_ENTRE_PAGINAS)

    if not todos:
        logger.warning("Nenhum dado coletado. Verifique a URL ou o seletor HTML.")
        return

    lookup = buscar_existentes(engine)
    novos  = filtrar_novos(todos, lookup)

    if novos:
        salvar_dados(novos, engine)
        logger.info(f"Extração finalizada. {len(novos)} novos de {len(todos)} raspados.")
    else:
        logger.info("Nenhum registro novo. Tudo já estava no banco.")

    logger.info("=== EXTRAÇÃO CONCLUÍDA ===")


if __name__ == "__main__":
    main()
