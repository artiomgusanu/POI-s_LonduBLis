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

# Ler arquivo Excel, pulando a primeira linha (linha de cabeçalho)
file_path = "C:\\projects\\POI-s_LonduBlis\\data\\escolasScraping2.xlsx"
df = pd.read_excel(file_path, skiprows=1)  # Pula a primeira linha
nome_escolas = df.iloc[:, 0].tolist()

dados = []

for escola in nome_escolas:
    try:
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "search_keyword[text]"))
        )

        # Verificar se há texto no campo de pesquisa e apagar corretamente
        search_box.send_keys(Keys.CONTROL + "a")  # Seleciona todo o texto
        search_box.send_keys(Keys.DELETE)  # Apaga o texto selecionado
        time.sleep(1)  # Pequena pausa para garantir que o campo está limpo

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
        driver.execute_script("arguments[0].scrollIntoView(true);", link_escola)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", link_escola)

        WebDriverWait(driver, 15).until(
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

        # Agora pegar as informações corretas:
        num_agrupamento = "-"
        agrupamento = "-"
        sede_escola = "-"
        num_escolas_agrupadas = "-"

        try:
            # Número do Agrupamento
            num_agrupamento_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-name='entity_field_field_n_do_agrupamento'] .drts-entity-field-value"))
            )
            num_agrupamento = num_agrupamento_element.text

            # Agrupamento
            agrupamento_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-name='entity_field_field_agrupamento'] .drts-entity-field-value"))
            )
            agrupamento = agrupamento_element.text

            # Sede Escola
            sede_escola_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-name='entity_field_field_escola_sede'] .drts-entity-field-value"))
            )
            sede_escola = sede_escola_element.text

            # Número de Escolas Agrupadas
            num_escolas_agrupadas_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-name='entity_field_field_numero_escolas_agrupadas'] .drts-entity-field-value"))
            )
            num_escolas_agrupadas = num_escolas_agrupadas_element.text

        except Exception as e:
            print(f"Erro ao pegar os campos adicionais: {e}")

        dados.append([escola, morada, freguesia, cod_postal, telefone, email, num_agrupamento, agrupamento, sede_escola, num_escolas_agrupadas])

        driver.get(url)  # Voltar para a página inicial
        time.sleep(3)

        #  Verifica se a página inicial carregou corretamente
        tentativa = 0
        while tentativa <3:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "search_keyword[text]"))
                )
                break
            except:
                print("Falha ao voltar para a página inicial, tentando novamente...")
                driver.get(url)
                time.sleep(3)
                tentativa += 1
    
    except Exception as e:
        print(f"Erro ao processar {escola}: {e}")

# Salvar os dados em um arquivo CSV
csv_path = "C:\\projects\\POI-s_LonduBlis\\data\\escolas_info(2).csv"
df_resultado = pd.DataFrame(dados, columns=["Escola", "Morada", "Freguesia", "Código Postal", "Telefone", "Email", "Número Agrupamento", "Agrupamento", "Sede Escola", "Número Escolas Agrupadas"])
df_resultado.to_csv(csv_path, index=False, encoding="utf-8-sig")

driver.quit()
print(f"Processo concluído! Dados salvos em {csv_path}")