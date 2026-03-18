import sqlite3

conexao = sqlite3.connect('mercado_automotivo.db')
cursor = conexao.cursor()

print("Iniciando faxina no banco de dados...")

cursor.execute("DELETE FROM historico_precos WHERE modelo NOT LIKE '%Onix%'")

conexao.commit()
print(f"Limpeza concluída! Linhas removidas: {conexao.total_changes}")
conexao.close()
