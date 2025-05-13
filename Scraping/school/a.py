import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # Importação corrigida

# Configuração do Selenium para Chrome
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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

# Ler arquivo Excel, pulando a primeira linha (linha de cabeçalho)
file_path = "C:\\projects\\POI-s_LonduBlis\\aaxlsx.xlsx"
df = pd.read_excel(file_path, skiprows=1)  # Pula a primeira linha
nome_escolas = df.iloc[:, 0].tolist()

dados = []

for escola in nome_escolas:
    try:
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "search_keyword[text]"))
        )

        search_box.clear()
        search_box.send_keys(escola, Keys.RETURN)  # Insere nova pesquisa

        # Esperar carregamento dos resultados
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-name='entity_field_post_title'] a"))
        )

        driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.6);")
        time.sleep(1)

        link_escola = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-name='entity_field_post_title'] a"))
        )
        driver.execute_script("arguments[0].click();", link_escola)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "drts-location-address"))
        )

        endereco_elemento = driver.find_element(By.CLASS_NAME, "drts-location-address")
        endereco = endereco_elemento.text.split(", ")
        morada = endereco[0] if len(endereco) > 0 else "-"
        freguesia = endereco[1] if len(endereco) > 1 else "-"
        cod_postal = endereco[2] if len(endereco) > 2 else "-"

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

        num_agrupamento = "-"
        agrupamento = "-"
        sede_escola = "-"
        num_escolas_agrupadas = "-"

        try:
            num_agrupamento = driver.find_element(By.CSS_SELECTOR, "div[data-name='entity_field_field_n_do_agrupamento'] .drts-entity-field-value").text
            agrupamento = driver.find_element(By.CSS_SELECTOR, "div[data-name='entity_field_field_agrupamento'] .drts-entity-field-value").text
            sede_escola = driver.find_element(By.CSS_SELECTOR, "div[data-name='entity_field_field_escola_sede'] .drts-entity-field-value").text
            num_escolas_agrupadas = driver.find_element(By.CSS_SELECTOR, "div[data-name='entity_field_field_numero_escolas_agrupadas'] .drts-entity-field-value").text
        except Exception as e:
            print(f"Erro ao pegar os campos adicionais: {e}")

        dados.append([escola, morada, freguesia, cod_postal, telefone, email, num_agrupamento, agrupamento, sede_escola, num_escolas_agrupadas])

        driver.get(url)  # Voltar para a página inicial
        time.sleep(3)
    
    except Exception as e:
        print(f"Erro ao processar {escola}: {e}")

# Salvar os dados em um arquivo CSV
csv_path = "C:\\projects\\POI-s_LonduBlis\\data\\escolas_info(3).csv"
df_resultado = pd.DataFrame(dados, columns=["Escola", "Morada", "Freguesia", "Código Postal", "Telefone", "Email", "Número Agrupamento", "Agrupamento", "Sede Escola", "Número Escolas Agrupadas"])
df_resultado.to_csv(csv_path, index=False, encoding="utf-8-sig")

driver.quit()
print(f"Processo concluído! Dados salvos em {csv_path}")
