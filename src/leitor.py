import sqlite3

print("Abrindo o cofre...")

# 1. Conectamos no mesmo arquivo
conexao = sqlite3.connect('mercado_automotivo.db')
cursor = conexao.cursor()

# 2. Fazemos o bom e velho SELECT
cursor.execute("SELECT * FROM historico_precos")

# 3. Pegamos todas as linhas que o banco retornar
resultados = cursor.fetchall()

print("\n--- DADOS GUARDADOS NO BANCO ---")
# 4. Imprimimos linha por linha
for linha in resultados:
    print(linha)

conexao.close()