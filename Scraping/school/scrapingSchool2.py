from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
import re
from selenium.common.exceptions import (
    TimeoutException, StaleElementReferenceException, 
    ElementClickInterceptedException, ElementNotInteractableException
)

# Configuração do Selenium
options = Options()
options.headless = False  # Mude para True para rodar sem abrir o navegador
service = Service("C:\\projects\\POI-s_LonduBlis\\Scraping\\geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)
wait = WebDriverWait(driver, 10)
actions = ActionChains(driver)

driver.get("https://infoescolas.medu.pt/2Ciclo/")
time.sleep(5)

# Clicar no link '1º Ciclo'
driver.execute_script("abr('dPav');")
time.sleep(5)

# Abrir arquivo CSV para salvar os dados
with open("escolas2.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "nome", "distrito", "municipio", "ano de escolaridade", "privado/publico"])

    # Loop pelos distritos
    select_distrito = Select(driver.find_element(By.CLASS_NAME, "lstDistrito"))
    for distrito_index in range(1, len(select_distrito.options)):  
        driver.execute_script("window.scrollTo(0, 0);")  # Rolar para o topo antes de mudar de distrito
        time.sleep(2)

        select_distrito = Select(driver.find_element(By.CLASS_NAME, "lstDistrito"))
        distrito_option = select_distrito.options[distrito_index]
        distrito_text = distrito_option.text
        distrito_option.click()
        time.sleep(3)

        print(f"\n🌍 Mudando para o distrito: {distrito_text}")

        # Loop pelos municípios
        select_municipio = Select(driver.find_element(By.CLASS_NAME, "lstConcelho"))
        for municipio_index in range(1, len(select_municipio.options)):
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)

            select_municipio = Select(driver.find_element(By.CLASS_NAME, "lstConcelho"))
            municipio_option = select_municipio.options[municipio_index]
            
            municipio_text = municipio_option.text
            municipio_option.click()
            time.sleep(5)

            print(f"📌 Município: {municipio_text}")

            # Esperar até que as escolas sejam carregadas
            try:
                escolas = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//tr[contains(@onclick, 'pavDet')]")))
            except TimeoutException:
                print(f"❌ Erro ao carregar escolas em {municipio_text}. Pulando...")
                continue

            index = 0
            while index < len(escolas):
                try:
                    escolas = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//tr[contains(@onclick, 'pavDet')]")))
                    if index >= len(escolas):
                        break
                    escola = escolas[index]
                    nome_escola = escola.text.strip()
                except (TimeoutException, StaleElementReferenceException):
                    print("❌ Erro ao recarregar a lista de escolas. Tentando novamente...")
                    driver.refresh()
                    time.sleep(5)
                    break

                # 🔹 Rolar até a escola antes de clicar
                try:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", escola)
                    time.sleep(1)
                    actions.move_to_element(escola).perform()  # Forçar o foco no elemento antes de clicar
                    escola.click()
                except (ElementClickInterceptedException, ElementNotInteractableException):
                    print(f"⚠️ Escola {index} não estava visível, tentando novamente...")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", escola)
                    time.sleep(1)
                    actions.move_to_element(escola).perform()
                    escola.click()

                time.sleep(3)

                # Capturar se é público ou privado
                try:
                    detalhe_texto = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
                    match_tipo = re.search(r"\[(Privado|Público)\]", detalhe_texto)
                    privado_publico = match_tipo.group(1) if match_tipo else "Desconhecido"
                except TimeoutException:
                    privado_publico = "Desconhecido"

                # Capturar o ano de escolaridade
                try:
                    ano_escolaridade = driver.find_element(By.CLASS_NAME, "alguma_classe").text
                except:
                    ano_escolaridade = "2º Ciclo"

                if nome_escola:
                    writer.writerow(["id", nome_escola, distrito_text, municipio_text, ano_escolaridade, privado_publico])
                    print(f"🏫 Escola: {nome_escola} | 🏛 Tipo: {privado_publico} | 📍 {distrito_text} - {municipio_text}")
                else:
                    print("⚠️ Nome da escola não encontrado, pulando...")

                # 🔹 Voltar para a lista de escolas
                driver.back()
                time.sleep(3)  # Aumentado para garantir que a página carregue antes de clicar na próxima escola
                index += 1

# Fechar navegador
driver.quit()
