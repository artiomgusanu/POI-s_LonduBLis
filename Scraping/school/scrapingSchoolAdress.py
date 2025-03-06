import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do Selenium
options = webdriver.FirefoxOptions()
service = Service("C:\\projects\\POI-s_LonduBlis\\Scraping\\geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)

driver.maximize_window()
url = "https://escoladevidro.pt"
driver.get(url)

# Aceitar cookies, se necessário
try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "fc-button.fc-cta-consent.fc-primary-button"))
    ).click()
except:
    print("Nenhum botão de cookies encontrado ou já aceito.")

# Ler arquivo Excel
file_path = "C:\\projects\\POI-s_LonduBlis\\teste.xlsx"
df = pd.read_excel(file_path)
nome_escolas = df.iloc[:, 0].tolist()

dados = []

for escola in nome_escolas:
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_keyword[text]"))
        )
        search_box.clear()
        search_box.send_keys(escola, Keys.RETURN)

        # Esperar carregamento dos resultados
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-name='entity_field_post_title'] a"))
        )

        driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.6);")
        time.sleep(1)

        link_escola = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-name='entity_field_post_title'] a"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", link_escola)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", link_escola)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "drts-location-address"))
        )

        time.sleep(1)  # Pequena pausa para evitar erro de elemento obsoleto
        endereco_elemento = driver.find_element(By.CLASS_NAME, "drts-location-address")
        endereco = endereco_elemento.text
        partes = endereco.split(", ")
        morada = partes[0] if len(partes) > 0 else "-"
        freguesia = partes[1] if len(partes) > 1 else "-"
        cod_postal = partes[2] if len(partes) > 2 else "-"

        telefone = "-"
        email = "-"
        try:
            telefone = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-phone-number]"))
            ).text
        except:
            print("Telefone não encontrado.")

        try:
            email = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='mailto']"))
            ).text
        except:
            print("Email não encontrado.")

        campos = driver.find_elements(By.CLASS_NAME, "drts-entity-field-value")
        num_agrupamento = campos[0].text if len(campos) > 0 else "-"
        agrupamento = campos[1].text if len(campos) > 1 else "-"
        sede_escola = campos[2].text if len(campos) > 2 else "-"
        num_escolas_agrupadas = campos[3].text if len(campos) > 3 else "-"

        dados.append([escola, morada, freguesia, cod_postal, telefone, email, num_agrupamento, agrupamento, sede_escola, num_escolas_agrupadas])
        
        driver.get(url)
    except Exception as e:
        print(f"Erro ao processar {escola}: {e}")

csv_path = "C:\\projects\\POI-s_LonduBlis\\escolas_info.csv"
df_resultado = pd.DataFrame(dados, columns=["Escola", "Morada", "Freguesia", "Código Postal", "Telefone", "Email", "Número Agrupamento", "Agrupamento", "Sede Escola", "Número Escolas Agrupadas"])
df_resultado.to_csv(csv_path, index=False, encoding="utf-8-sig")

driver.quit()
print(f"Processo concluído! Dados salvos em {csv_path}")