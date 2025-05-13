import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Ler lista de freguesias
with open("C:\\Projects\\POI-s_LonduBlis\\Scraping\\multibanco\\freguesias_portugal.txt", "r", encoding="utf-8") as f:
    freguesias = [line.strip() for line in f.readlines()]

# Preparar driver
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# URL base
base_url = "https://ind.millenniumbcp.pt/pt/Particulares/Pages/Onde_Estamos.aspx"
output_file = "agencias_millennium.xlsx"

# Armazenar os dados
dados = []

for freguesia in freguesias:
    try:
        driver.get(base_url)
        time.sleep(random.uniform(2, 4))

        # Campo de pesquisa
        campo_input = wait.until(EC.presence_of_element_located(
            (By.ID, "ctl00_ctl00_PlaceHolderMainBase_PlaceHolderMain_bls_vSearchSearch_tbKeyword")
        ))
        campo_input.clear()
        campo_input.send_keys(freguesia)
        campo_input.send_keys(Keys.ENTER)
        time.sleep(random.uniform(3, 5))

        # Verificar se há resultados
        resultados = driver.find_elements(By.CSS_SELECTOR, ".results ul li a")
        if not resultados:
            print(f"Nenhum resultado para: {freguesia}")
            continue

        for i in range(len(resultados)):
            try:
                resultados = driver.find_elements(By.CSS_SELECTOR, ".results ul li a")
                link = resultados[i]
                link_text = link.text

                link.click()
                time.sleep(random.uniform(2, 4))

                outer = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Outer")))
                nome = outer.find_element(By.CSS_SELECTOR, "h2.head").text.strip()
                colunas = outer.find_elements(By.CLASS_NAME, "BranchDetailColumn")

                # Coluna da esquerda
                morada_bloco = colunas[0].find_elements(By.TAG_NAME, "p")
                morada1 = morada_bloco[0].text.strip() if len(morada_bloco) > 0 else ""
                morada2 = morada_bloco[1].text.strip() if len(morada_bloco) > 1 else ""
                morada3 = morada_bloco[2].text.strip() if len(morada_bloco) > 2 else ""
                pais = morada_bloco[3].text.strip() if len(morada_bloco) > 3 else ""
                telefone = morada_bloco[4].text.strip() if len(morada_bloco) > 4 else ""
                fax = morada_bloco[5].text.strip() if len(morada_bloco) > 5 else ""
                email = morada_bloco[6].text.strip() if len(morada_bloco) > 6 else ""
                gps = morada_bloco[7].text.strip() if len(morada_bloco) > 7 else ""

                # Coluna da direita
                coluna_direita = colunas[1].find_elements(By.TAG_NAME, "p")
                responsavel = coluna_direita[0].text.strip() if len(coluna_direita) > 0 else ""
                horario = coluna_direita[1].text.strip() if len(coluna_direita) > 1 else ""
                tesouraria = coluna_direita[2].text.strip() if len(coluna_direita) > 2 else ""
                almoco = coluna_direita[3].text.strip() if len(coluna_direita) > 3 else ""
                servicos = coluna_direita[4].text.strip() if len(coluna_direita) > 4 else ""

                dados.append({
                    "Freguesia pesquisada": freguesia,
                    "Nome Agência": nome,
                    "Morada 1": morada1,
                    "Morada 2": morada2,
                    "Morada 3": morada3,
                    "País": pais,
                    "Telefone": telefone,
                    "Fax": fax,
                    "Email": email,
                    "Coordenadas GPS": gps,
                    "Responsável": responsavel,
                    "Horário": horario,
                    "Tesouraria Encerra": tesouraria,
                    "Almoço": almoco,
                    "Serviços Automáticos": servicos,
                })

                pd.DataFrame(dados).to_excel(output_file, index=False)
                print(f"[OK] Agência salva: {nome}")

                try:
                    driver.back()
                    time.sleep(random.uniform(2, 3))
                except Exception as e:
                    print(f"⚠️ Não foi possível voltar para a lista: {e}")
                    break

            except Exception as e:
                print(f"[ERRO] Ao processar link '{link_text}': {e}")
                try:
                    driver.back()
                except:
                    pass
                time.sleep(2)
                continue

    except Exception as e:
        print(f"[ERRO] Geral com freguesia '{freguesia}': {e}")

# Finalização
df = pd.DataFrame(dados)
df.to_excel(output_file, index=False)
driver.quit()
print("✅ Scraping completo!")
