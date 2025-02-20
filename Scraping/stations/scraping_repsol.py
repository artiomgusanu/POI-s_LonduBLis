from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import pandas as pd

# Caminho para o GeckoDriver
service = Service('C:\\projects\\POI-s_LonduBlis\\Scraping\\geckodriver.exe')
driver = webdriver.Firefox(service=service)

# Construir o caminho para o arquivo distritos.txt
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../data/distritos.txt')

# Ler as localidades do arquivo distritos.txt
with open(file_path, 'r', encoding='utf-8') as file:
    localidades = [line.strip() for line in file]

# Lista para armazenar os dados
dados_bombas = []

# URL da Repsol
url = 'https://www.repsol.pt/localizador-es-e-pontos-carregamento'

# Percorrer cada localidade
for localidade in localidades:
    # Acessar o site
    driver.get(url)
    time.sleep(3)  # Esperar o carregamento da página

    # Aceitar cookies (caso apareça o botão)
    try:
        cookies_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
        cookies_button.click()
        print("Cookies aceitos.")
        time.sleep(2)
    except Exception:
        print("Botão de cookies não encontrado. Continuando...")

    # Pesquisar a localidade
    search_box = driver.find_element(By.CLASS_NAME, 'suggestTxtMap')
    search_box.send_keys(localidade)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)  # Esperar os resultados carregarem

    # Clicar no botão de lista
    try:
        list_button = driver.find_element(By.CLASS_NAME, 'js-open-advanced-search advanced-search-btn rp-btn rp-btn-secondary')
        list_button.click()
        time.sleep(5)  # Esperar a lista carregar
    except Exception as e:
        print(f"Botão de lista não encontrado para {localidade}. Pulando...")
        continue

    # Encontrar todas as bombas de gasolina
    bombas = driver.find_elements(By.CLASS_NAME, 'row.no-gutters.cards-result')

    for bomba in bombas:
        try:
            # Nome da bomba
            nome = bomba.find_element(By.CLASS_NAME, 'link-titulo-regular.rp-title-2.maptitle').text

            # Morada, latitude e longitude
            morada_element = bomba.find_element(By.CLASS_NAME, 'link-titulo-regular.rp-body-1.mapdescription.mapaddress')
            morada = morada_element.text
            latitude = morada_element.get_attribute('data-lat')
            longitude = morada_element.get_attribute('data-lng')

            # Adicionar aos dados
            dados_bombas.append({
                'Localidade': localidade,
                'Nome': nome,
                'Morada': morada,
                'Latitude': latitude,
                'Longitude': longitude
            })
        except Exception as e:
            print(f"Erro ao processar uma bomba em {localidade}: {e}")

# Fechar o navegador
driver.quit()

# Salvar os dados em um arquivo CSV
df = pd.DataFrame(dados_bombas)
df.to_csv('bombas_repsol.csv', index=False)

print("Informações salvas em 'bombas_repsol.csv'")
