import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Função para obter rua e código postal com tentativas de repetição
def get_address(lat, lon, geolocator, retries=3):
    for _ in range(retries):
        try:
            location = geolocator.reverse((lat, lon), exactly_one=True)
            if location and "address" in location.raw:
                address = location.raw["address"]
                rua = address.get("road", "Desconhecido")
                codigo_postal = address.get("postcode", "Desconhecido")
                return rua, codigo_postal
        except GeocoderTimedOut:
            time.sleep(2)  # Espera 2 segundos antes de tentar novamente
    return "Erro", "Erro"

# Carregar o ficheiro Excel
file_path = "C:\\projects\\POI-s_LonduBlis\\data\\primaria\\listSchool.xlsx"  # Nome do arquivo Excel
df = pd.read_excel(file_path)

# Configurar o geolocalizador com tempo de espera
geolocator = Nominatim(user_agent="geoapi", timeout=10)

# Criar novas colunas caso não existam
if "Rua" not in df.columns:
    df["Rua"] = ""
if "Código Postal" not in df.columns:
    df["Código Postal"] = ""

# Processar cada linha
for index, row in df.iterrows():
    latitude, longitude = row["Latitude"], row["Longitude"]
    rua, codigo_postal = get_address(latitude, longitude, geolocator)
    df.at[index, "Rua"] = rua
    df.at[index, "Código Postal"] = codigo_postal

    # 🔹 Exibir progresso
    print(f"Processado {index+1}/{len(df)}: ({latitude}, {longitude}) -> {rua}, {codigo_postal}")

    # 🔹 Salvar progresso a cada 50 linhas processadas
    if index % 50 == 0:
        df.to_excel(file_path, index=False)
        print("Progresso salvo no Excel.")

    time.sleep(1)  # Pausa de 1 segundo para evitar bloqueio

# Salvar progresso final
df.to_excel(file_path, index=False)
print(f"Processo concluído! Arquivo salvo como: {file_path}")
