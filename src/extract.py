import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import logging
import os
from datetime import datetime

# --- Configuração de logging profissional ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

URL = 'https://www.icarros.com.br/ache/listaanuncios.jsp?bid=1&sop=esc_4.1_-rai_50.1_-mar_5.1_-mod_2428|2794.1_-'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# --- Garante que a pasta data/ existe ---
os.makedirs("data", exist_ok=True)

logger.info("Iniciando coleta de dados do iCarros...")

resposta = requests.get(URL, headers=HEADERS)

if resposta.status_code == 200:
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    cards = sopa.find_all('li', class_='offer-card')

    conexao = sqlite3.connect('data/mercado_automotivo.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT,
            preco REAL,
            ano TEXT,
            km TEXT,
            data_coleta TEXT
        )
    ''')

    data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{len(cards)} anúncios encontrados. Iniciando processamento...")

    inseridos = 0
    erros = 0

    for i, card in enumerate(cards):
        try:
            el_titulo = card.find('p', class_='label__neutral')
            el_preco  = card.find('p', string=re.compile(r'R\$'))
            el_ano    = card.find('p', class_='label__neutral-variant')
            el_km     = card.find('p', string=re.compile(r'Km'))

            if not el_titulo:
                logger.warning(f"Card {i}: título não encontrado. Pulando.")
                erros += 1
                continue

            titulo = el_titulo.text.strip()

            preco_limpo = 0.0
            if el_preco:
                texto_preco = el_preco.text.replace('.', '').replace(',', '.')
                numeros = re.findall(r'\d+', texto_preco)
                if numeros:
                    preco_limpo = float("".join(numeros)) / 100

            ano = el_ano.text.strip() if el_ano else "N/I"
            km  = el_km.text.strip()  if el_km  else "0 Km"

            cursor.execute('''
                INSERT INTO historico_precos (modelo, preco, ano, km, data_coleta)
                VALUES (?, ?, ?, ?, ?)
            ''', (titulo, preco_limpo, ano, km, data_hoje))

            logger.info(f"Inserido: {titulo} | {ano} | {km} | R$ {preco_limpo:.2f}")
            inseridos += 1

        except Exception as e:
            logger.error(f"Card {i}: erro inesperado — {e}")
            erros += 1
            continue  # segue para o próximo card sem perder os anteriores

    conexao.commit()
    conexao.close()
    logger.info(f"Coleta finalizada. {inseridos} registros inseridos, {erros} erros.")

else:
    logger.error(f"Falha na requisição HTTP: {resposta.status_code}")
