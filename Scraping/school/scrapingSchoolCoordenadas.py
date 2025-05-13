import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configurar Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Carregar o Excel
file_path = "C:\\projects\\POI-s_LonduBlis\\data\\basico\\listSchoolS.xlsx"  # Nome do arquivo Excel
sheet_name = "Sheet1"  # Nome da aba

df = pd.read_excel(file_path, sheet_name=sheet_name)

def extract_coordinates(address):
    base_url = "https://www.openstreetmap.org/search?query="
    search_url = base_url + address.replace(" ", "+")
    
    driver.get(search_url)
    time.sleep(3)  # Tempo para carregar a página
    
    try:
        # Pegar a URL final após carregar
        final_url = driver.current_url
        if "#map=" in final_url:
            parts = final_url.split("#map=")[1].split("/")
            latitude = parts[1]
            longitude = parts[2]
        else:
            latitude, longitude = "-", "-"
    except Exception:
        latitude, longitude = "-", "-"
    
    return latitude, longitude

# Criar novas colunas
if "Latitude" not in df.columns:
    df["Latitude"] = "-"
if "Longitude" not in df.columns:
    df["Longitude"] = "-"

# Iterar sobre os endereços e salvar progresso
for index, row in df.iterrows():
    if df.at[index, "Latitude"] == "-":  # Só processa se ainda não tiver coordenadas
        latitude, longitude = extract_coordinates(row["nome_escola"])
        df.at[index, "Latitude"] = latitude
        df.at[index, "Longitude"] = longitude
        df.to_excel(file_path, index=False)  # Salvar progresso
        print(f"Processado {index+1}/{len(df)}: {row['nome_escola']} -> {latitude}, {longitude}")

# Fechar navegador
driver.quit()
print("Finalizado!")