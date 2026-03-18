import sqlite3

print("Abrindo o cofre...")

conexao = sqlite3.connect('mercado_automotivo.db')
cursor = conexao.cursor()

cursor.execute("SELECT * FROM historico_precos")

resultados = cursor.fetchall()

print("\n--- DADOS GUARDADOS NO BANCO ---")

for linha in resultados:
    print(linha)

conexao.close()
