import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from datetime import datetime

url = 'https://www.icarros.com.br/comprar/cuiaba-mt/chevrolet/onix/2024/d56545198?pos=3&hfv=false&financiamento=true&_gl=1*1ok4158*_up*MQ..*_gs*MQ..&gclid=Cj0KCQjwsdnNBhC4ARIsAA_3heilmJbRr7Jj11mMWh2gisA-G9KgwTxK15pBKtcZhJTPyxmvKgeV7NAaAjvHEALw_wcB&gclsrc=aw.ds&gbraid=0AAAAADpn-tVXUNo1327yAPmucSzK0V3hh'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Infiltrando no site de vendas...")
resposta = requests.get(url, headers=headers)

if resposta.status_code == 200:
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    elemento_preco = sopa.find('h2', class_='preco')
    
    if elemento_preco:
        # --- E: EXTRAÇÃO ---
        preco_bruto = elemento_preco.text.strip()
        
        # --- T: TRANSFORMAÇÃO ---
        apenas_numeros = re.sub(r'[^\d]', '', preco_bruto)
        preco_limpo = float(apenas_numeros) / 100
        
        print(f"Preço limpo: R$ {preco_limpo}")
        
        # --- L: LOAD (CARREGANDO NO BANCO DE DADOS) ---
        print("\nAbrindo o Banco de Dados...")
        
        
        conexao = sqlite3.connect('data/mercado_automotivo.db')
        cursor = conexao.cursor() 
        
       
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_precos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modelo TEXT,
                preco REAL,
                data_coleta TEXT
            )
        ''')
        
        # Preparamos os dados para inserir
        modelo_carro = "Onix LT 1.0 2024"
        data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Inserimos a linha na tabela
        cursor.execute('''
            INSERT INTO historico_precos (modelo, preco, data_coleta)
            VALUES (?, ?, ?)
        ''', (modelo_carro, preco_limpo, data_hoje))
        
        conexao.commit()
        conexao.close()
        
        print(f"Sucesso! O preço do {modelo_carro} foi salvo na tabela 'historico_precos'.")
        print("Ciclo ETL concluído com maestria!")
        
    else:
        print("A página carregou, mas não achei o preço.")
else:
    print(f"Ops! Fomos bloqueados. Status: {resposta.status_code}")
