from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import csv
import re

# Configuração do Selenium
options = Options()
options.headless = False  # Altere para True se quiser rodar sem interface gráfica
service = Service("C:\\projects\\POI-s_LonduBlis\\Scraping\\geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)
wait = WebDriverWait(driver, 10)

def safe_find_element(by, value, timeout=10):
    """ Tenta encontrar um elemento e garantir que está visível antes de interagir """
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except:
        return None

def safe_find_elements(by, value, timeout=10):
    """ Tenta encontrar vários elementos garantindo que estão visíveis antes da interação """
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
    except:
        return []

# Acessar página principal
driver.get("https://infoescolas.medu.pt/Secundario/")
time.sleep(5)

driver.execute_script("abr('dPav');")
time.sleep(5)

with open("escolas_secundarias.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["nome", "distrito", "municipio", "tipo_curso", "privado/publico"])

    select_distrito = safe_find_element(By.CLASS_NAME, "lstDistrito")
    if select_distrito:
        select_distrito = Select(select_distrito)
    else:
        print("Erro ao carregar os distritos.")
        driver.quit()

    for distrito_index in range(1, len(select_distrito.options)):
        select_distrito = Select(safe_find_element(By.CLASS_NAME, "lstDistrito"))
        distrito_option = select_distrito.options[distrito_index]
        distrito_text = distrito_option.text
        distrito_option.click()
        time.sleep(3)
        print(f"\n🌍 Mudando para o distrito: {distrito_text}")

        select_municipio = safe_find_element(By.CLASS_NAME, "lstConcelho")
        if select_municipio:
            select_municipio = Select(select_municipio)
        else:
            print("Erro ao carregar os municípios.")
            continue

        for municipio_index in range(1, len(select_municipio.options)):
            select_municipio = Select(safe_find_element(By.CLASS_NAME, "lstConcelho"))
            municipio_option = select_municipio.options[municipio_index]
            municipio_text = municipio_option.text
            municipio_option.click()
            time.sleep(5)
            print(f"📌 Município: {municipio_text}")

            while True:
                linhas = safe_find_elements(By.XPATH, "//tr[td/div[contains(@onclick, 'pavDet')]]")
                if not linhas:
                    print("⚠️ Nenhuma linha encontrada, tentando novamente...")
                    time.sleep(3)
                    continue

                for i in range(len(linhas)):
                    try:
                        linhas = safe_find_elements(By.XPATH, "//tr[td/div[contains(@onclick, 'pavDet')]]")
                        linha = linhas[i]

                        colunas = linha.find_elements(By.TAG_NAME, "td")
                        if len(colunas) < 3:
                            continue

                        nome_escola = colunas[0].text.strip()
                        curso_ch = colunas[1].text.strip()
                        curso_cp = colunas[2].text.strip()

                        if not nome_escola:
                            continue

                        tipos_curso = []
                        if curso_ch:
                            tipos_curso.append("Científico-Humanísticos")
                        if curso_cp:
                            tipos_curso.append("Profissionais")
                        tipos_curso_str = " e ".join(tipos_curso) if tipos_curso else "Desconhecido"

                        botao_detalhes = linha.find_element(By.XPATH, ".//td/div[contains(@onclick, 'pavDet')]")

                        driver.execute_script("arguments[0].style.border='3px solid red';", botao_detalhes)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", botao_detalhes)
                        time.sleep(3)
                        
                        tipo_escola = "Desconhecido"
                        detalhes_texto = safe_find_element(By.CLASS_NAME, "titEstCur")
                        if detalhes_texto:
                            match = re.search(r'\[(.*?)\]', detalhes_texto.text)
                            if match:
                                tipo_escola = match.group(1)
                        
                        writer.writerow([nome_escola, distrito_text, municipio_text, tipos_curso_str, tipo_escola])
                        print(f"🏫 {nome_escola} | 📖 {tipos_curso_str} | 🏛 {tipo_escola}")
                        
                        driver.back()
                        time.sleep(5)

                        safe_find_element(By.CLASS_NAME, "lstDistrito")
                        safe_find_element(By.CLASS_NAME, "lstConcelho")

                    except Exception as e:
                        print(f"⚠️ Erro ao processar linha {i}: {e}")
                        continue
                break

driver.quit()