import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from datetime import datetime

url = 'https://www.icarros.com.br/ache/listaanuncios.jsp?bid=1&sop=esc_4.1_-rai_50.1_-mar_5.1_-mod_2428|2794.1_-'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Infiltrando no iCarros para coleta completa...")
resposta = requests.get(url, headers=headers)

if resposta.status_code == 200:
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    cards = sopa.find_all('li', class_='offer-card')
    
    conexao = sqlite3.connect('data/mercado_automotivo.db')
    cursor = conexao.cursor()

    # UPGRADE DO BANCO: Deletamos a antiga e criamos a nova com mais colunas
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
    
    print(f"Processando {len(cards)} anúncios com BI em mente...\n")
    
    for card in cards:
        el_titulo = card.find('p', class_='label__neutral')
        # TENTATIVA 2: Buscando o preço por uma classe mais genérica ou pelo cifrão
        el_preco  = card.find('p', string=re.compile(r'R\$')) 
        el_ano    = card.find('p', class_='label__neutral-variant')
        el_km     = card.find('p', string=re.compile(r'Km'))

        if el_titulo:
            titulo = el_titulo.text.strip()
            
            # Limpeza do Preço mais robusta
            preco_limpo = 0.0
            if el_preco:
                # Pega só o que é número
                texto_preco = el_preco.text.replace('.', '').replace(',', '.')
                numeros = re.findall(r'\d+', texto_preco)
                if numeros:
                    # Monta o número cheio e converte
                    preco_limpo = float("".join(numeros)) / 100

            ano = el_ano.text.strip() if el_ano else "N/I"
            km = el_km.text.strip() if el_km else "0 Km"
            
            print(f"Inserindo: {titulo} | {ano} | {km} | R$ {preco_limpo:.2f}")
            
            cursor.execute('''
                INSERT INTO historico_precos (modelo, preco, ano, km, data_coleta)
                VALUES (?, ?, ?, ?, ?)
            ''', (titulo, preco_limpo, ano, km, data_hoje))
    
    conexao.commit()
    conexao.close()
    print("\nSistema atualizado! O seu cofre agora é um Banco de BI completo.")
            
else:
    print(f"Erro de conexão: {resposta.status_code}")
