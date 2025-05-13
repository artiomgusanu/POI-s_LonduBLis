import pandas as pd
import json

# Carregar dados JSON de um arquivo
with open('C:\\Users\\artio\\Downloads\\export.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Converter para DataFrame
df = pd.json_normalize(dados)

# Salvar como arquivo Excel
df.to_excel('dados.xlsx', index=False)

print("Arquivo Excel salvo com sucesso!")

