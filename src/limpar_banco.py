import sqlite3

conexao = sqlite3.connect('mercado_automotivo.db')
cursor = conexao.cursor()

print("Iniciando faxina no banco de dados...")

# Vamos deletar tudo que NÃO tem a palavra 'Onix' no nome 
# (Já que o robô acabou salvando cidades e KM antes)
cursor.execute("DELETE FROM historico_precos WHERE modelo NOT LIKE '%Onix%'")

# E vamos aproveitar para deletar duplicados se você quiser resetar tudo:
# cursor.execute("DELETE FROM historico_precos")

conexao.commit()
print(f"Limpeza concluída! Linhas removidas: {conexao.total_changes}")
conexao.close()