import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Função para obter morada completa e código postal
def get_address(lat, lon, geolocator, retries=3):
    for _ in range(retries):
        try:
            location = geolocator.reverse((lat, lon), exactly_one=True)
            if location and "address" in location.raw:
                address = location.raw["address"]
                
                # Capturar mais detalhes da morada
                rua = address.get("road", "Desconhecido")
                numero = address.get("house_number", "Desconhecido")
                bairro = address.get("suburb", address.get("neighbourhood", "Desconhecido"))
                cidade = address.get("city", address.get("town", "Desconhecido"))
                distrito = address.get("state", "Desconhecido")
                codigo_postal = address.get("postcode", "Desconhecido")
                pais = address.get("country", "Desconhecido")

                # Criar uma morada formatada
                morada_completa = f"{rua}, {numero}, {bairro}, {cidade}, {distrito}, {codigo_postal}, {pais}"
                
                return rua, numero, bairro, cidade, distrito, codigo_postal, pais, morada_completa
        
        except GeocoderTimedOut:
            time.sleep(2)  # Espera antes de tentar novamente
    
    return "Erro", "Erro", "Erro", "Erro", "Erro", "Erro", "Erro", "Erro"

# Carregar ficheiro Excel
file_path = "C:\\projects\\POI-s_LonduBlis\\data\\basico\\listSchoolS.xlsx"
df = pd.read_excel(file_path)

# Configurar geolocalizador
geolocator = Nominatim(user_agent="geoapi", timeout=10)

# Criar colunas extras caso não existam
for col in ["Rua", "Número", "Bairro", "Cidade", "Distrito", "Código Postal", "País", "Morada Completa"]:
    if col not in df.columns:
        df[col] = ""

# Processar cada linha
for index, row in df.iterrows():
    latitude, longitude = row["Latitude"], row["Longitude"]
    rua, numero, bairro, cidade, distrito, codigo_postal, pais, morada_completa = get_address(latitude, longitude, geolocator)
    
    df.at[index, "Rua"] = rua
    df.at[index, "Número"] = numero
    df.at[index, "Bairro"] = bairro
    df.at[index, "Cidade"] = cidade
    df.at[index, "Distrito"] = distrito
    df.at[index, "Código Postal"] = codigo_postal
    df.at[index, "País"] = pais
    df.at[index, "Morada Completa"] = morada_completa

    # 🔹 Exibir progresso
    print(f"Processado {index+1}/{len(df)}: ({latitude}, {longitude}) -> {morada_completa}")

    # 🔹 Salvar progresso a cada 50 linhas
    if index % 50 == 0:
        df.to_excel(file_path, index=False)
        print("Progresso salvo no Excel.")

    time.sleep(1)  # Evitar bloqueios

# Salvar progresso final
df.to_excel(file_path, index=False)
print(f"Processo concluído! Arquivo salvo como: {file_path}")
