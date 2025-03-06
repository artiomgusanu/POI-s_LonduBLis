from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import time
import pandas as pd

# Carregar a planilha
file_path = "C:\\Projects\\POI-s_LonduBlis\\escolasScraping1.xlsx"
df = pd.read_excel(file_path, sheet_name="Folha1")

# Configurar o Selenium
options = webdriver.FirefoxOptions()
service = Service("C:\\projects\\POI-s_LonduBlis\\Scraping\\geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)

def buscar_dados_google_maps(nome_escola):
    try:
        print(f"Buscando dados para a escola: {nome_escola}")
        driver.get("https://www.google.pt/maps")
        time.sleep(3)

        try:
            botao_cookies = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Aceitar tudo"]')
            print(f"Botão encontrado: {botao_cookies.text}")  # Verificar se foi encontrado
        
            botao_cookies.click()
            print("Cookies aceites.")
            time.sleep(5)
        except Exception as e:
            print(f"Erro ao aceitar cookies")
        
        # Encontrar a barra de pesquisa
        search_box = driver.find_element(By.CLASS_NAME, "searchboxinput")
        search_box.send_keys(nome_escola)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)
        
        # Obter endereço
        try:
            endereco_element = driver.find_element(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc")
            endereco = endereco_element.text
            print(f"Endereço encontrado: {endereco}")
        except:
            endereco = "-"
            print("Endereço não encontrado.")
        
        # Obter coordenadas da URL
        try:
            url = driver.current_url
            coords_part = url.split('@')[1].split(',')
            latitude, longitude = coords_part[0], coords_part[1]
            print(f"Coordenadas encontradas: {latitude}, {longitude}")
        except:
            latitude, longitude = "-", "-"
            print("Coordenadas não encontradas.")
        
        return endereco, latitude, longitude
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return "-", "-", "-"

# Criar novas colunas
df["morada_escola"] = ""
df["codigo_postal"] = ""
df["freguesia"] = ""
df["latitude"] = ""
df["longitude"] = ""

# Iterar sobre as escolas
for index, row in df.iterrows():
    if index == 0:
        continue  # Ignorar a primeira linha
    
    nome_escola = row["nome_escola"]
    endereco, latitude, longitude = buscar_dados_google_maps(nome_escola)
    
    # Separar morada, código postal e freguesia
    partes = endereco.rsplit(',', 2)
    if len(partes) == 3:
        df.at[index, "morada_escola"] = partes[0]
        df.at[index, "codigo_postal"] = partes[1].strip()
        df.at[index, "freguesia"] = partes[2].strip()
    else:
        df.at[index, "morada_escola"] = endereco
        df.at[index, "codigo_postal"] = "-"
        df.at[index, "freguesia"] = "-"
    
    df.at[index, "latitude"] = latitude
    df.at[index, "longitude"] = longitude
    
# Salvar o resultado
df.to_excel("C:\\Projects\\POI-s_LonduBlis\\escolasScraping1_resultado.xlsx", index=False)

# Fechar o navegador
driver.quit()
