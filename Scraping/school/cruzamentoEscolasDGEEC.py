import pandas as pd
from difflib import SequenceMatcher

# Carregar o ficheiro Excel
file_path = "C:\\Projects\\POI-s_LonduBlis\\teu_ficheiro.xlsx"  # Substituir pelo nome correto
df_info = pd.read_excel(file_path, sheet_name='escolas_info')
df_tbl = pd.read_excel(file_path, sheet_name='tblEscolas')

# Função para extrair os primeiros 4 dígitos do código postal
def extract_cp(cp):
    return str(cp)[:4] if pd.notna(cp) else ''

# Função para extrair palavras-chave do nome da escola
def extract_keywords(name):
    return set(str(name).lower().split()) if pd.notna(name) else set()

# Função para limpar textos (remover tudo após vírgula ou hífen)
def clean_text(text):
    if pd.isna(text):
        return ''
    return text.split(',')[0].split('-')[0].strip()

# Aplicar transformações nos dados
df_info['CP4'] = df_info['CP'].apply(extract_cp)
df_info['NOME_LIMPO'] = df_info['NOME'].apply(clean_text)
df_info['Keywords'] = df_info['NOME_LIMPO'].apply(extract_keywords)

df_tbl['CP4'] = df_tbl['Distrito'].apply(extract_cp)
df_tbl['Descr_LIMPO'] = df_tbl['Descr'].apply(clean_text)
df_tbl['Keywords'] = df_tbl['Descr_LIMPO'].apply(extract_keywords)

# Cruzamento de dados
matches = []
for index1, row1 in df_tbl.iterrows():
    for index2, row2 in df_info.iterrows():
        if row1['CP4'] == row2['CP4']:  # Verifica código postal
            keyword_match = len(row1['Keywords'].intersection(row2['Keywords']))
            similarity = SequenceMatcher(None, row1['Descr_LIMPO'], row2['NOME_LIMPO']).ratio()
            
            # Se houver alguma correspondência relevante, guarda o match
            if keyword_match > 0 or similarity > 0.5:
                matches.append({
                    'tblEscolas_Nome': row1['Descr'],
                    'tblEscolas_Nome_Limpo': row1['Descr_LIMPO'],
                    'escolas_info_Nome': row2['NOME'],
                    'escolas_info_Nome_Limpo': row2['NOME_LIMPO'],
                    'Codigo_Postal': row1['CP4'],
                    'Keywords_Match': keyword_match,
                    'Similarity_Score': similarity
                })

# Criar DataFrame com os resultados
df_matches = pd.DataFrame(matches)

# Guardar num novo ficheiro Excel
df_matches.to_excel("matches_escolas2.xlsx", index=False)

print("Processo concluído! Resultados guardados em 'matches_escolas.xlsx'.")
