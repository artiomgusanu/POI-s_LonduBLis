import pandas as pd
from thefuzz import process, fuzz

# Carregar os arquivos
file1_path = "C:\\projects\\POI-s_LonduBlis\\data\\limpo\\3Ciclo\\3Ciclo.xlsx"
file2_path = "C:\\projects\\POI-s_LonduBlis\\ENEB2023.xlsx"

# Carregar as abas relevantes
df_3ciclo = pd.read_excel(file1_path, sheet_name="escolas_info")
df_eneb = pd.read_excel(file2_path, sheet_name="tblEscolas")

# Converter colunas para string e remover espaços extras
df_3ciclo['CODIGO'] = df_3ciclo['CODIGO'].astype(str).str.strip()
df_eneb['Escola'] = df_eneb['Escola'].astype(str).str.strip()

# Verificar se as colunas de nome da escola existem
if 'NOME' in df_3ciclo.columns and 'Descr' in df_eneb.columns:
    df_3ciclo['NOME'] = df_3ciclo['NOME'].astype(str).str.lower().str.strip()
    df_eneb['Descr'] = df_eneb['Descr'].astype(str).str.lower().str.strip()

    # Remover valores nulos antes do fuzzy matching
    df_3ciclo = df_3ciclo.dropna(subset=['NOME'])
    df_eneb = df_eneb.dropna(subset=['Descr'])

    # Criar um dicionário de correspondência usando fuzzy matching
    mapping = []
    for nome_3ciclo in df_3ciclo['NOME'].unique():
        match, score = process.extractOne(nome_3ciclo, df_eneb['Descr'].unique(), scorer=fuzz.token_sort_ratio)
        if score > 80:  # Ajuste do limiar conforme necessário
            mapping.append({'Nome_3Ciclo': nome_3ciclo, 'Nome_ENEB': match, 'Score': score})

    # Criar um dataframe com as correspondências encontradas
    df_mapping = pd.DataFrame(mapping)
    print(df_mapping.head())  # Mostrar algumas correspondências

    # Unir os dados baseando-se nas correspondências de nome
    df_merged = df_3ciclo.merge(df_mapping, left_on='NOME', right_on='Nome_3Ciclo', how='left')
    df_merged = df_merged.merge(df_eneb, left_on='Nome_ENEB', right_on='Descr', how='left')

    # Exibir algumas correspondências para validação
    print(df_merged[['CODIGO', 'Escola', 'NOME', 'Descr', 'Score']].head())

    # Salvar os resultados em um arquivo Excel
    with pd.ExcelWriter("dados_fusionados.xlsx") as writer:
        df_mapping.to_excel(writer, sheet_name="Mapeamento", index=False)
        df_merged.to_excel(writer, sheet_name="Dados Unificados", index=False)

    print("Processo concluído! Arquivo salvo como 'dados_fusionados.xlsx'.")

else:
    print("Coluna de nome da escola não encontrada em uma das tabelas.")
