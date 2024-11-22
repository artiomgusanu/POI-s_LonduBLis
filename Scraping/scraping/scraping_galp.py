import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Caminho para o GeckoDriver
geckodriver_path = "C:\\POI-s_LonduBlis\\Scraping\\geckodriver.exe"

# Função para inicializar o WebDriver
def init_driver():
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service)
    return driver

# Inicializar o WebDriver
driver = init_driver()

try:
    # Acessar o site da Galp
    driver.get("https://galp.com/pt/mapa")
    time.sleep(10)  # Esperar a página carregar

    # Fechar o popup de localização
    localization_not_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='localization-not']//a[@href='#']"))
    )
    localization_not_button.click()
    time.sleep(2)

    # Pesquisar por "Alverca"
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "Local"))
    )
    search_input.send_keys("Alverca")
    search_input.send_keys(Keys.RETURN)
    time.sleep(5)  # Aguardar os resultados

    # Lista para armazenar os detalhes das estações
    station_details = []

    # Iniciar o loop para processar cada estação
    while True:
        try:
            # Re-encontrar as estações após cada iteração (recarregando a lista)
            stations = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "station"))
            )

            if not stations:  # Se não houver mais estações, parar
                print("No more stations found.")
                break

            # Processar cada estação da lista
            for station in stations:
                try:
                    # Rolar a estação para visibilidade e clicar
                    driver.execute_script("arguments[0].scrollIntoView();", station)
                    station.click()
                    time.sleep(2)  # Esperar a página carregar os detalhes

                    # Capturar o nome e o endereço da estação
                    name = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "highlightLocation__title"))
                    ).text
                    address = driver.find_element(By.CLASS_NAME, "highlightLocation__address").text

                    # Salvar os detalhes da estação
                    station_details.append({"Name": name, "Address": address})

                    # Fechar o detalhe da estação para voltar à lista
                    close_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.search__desktop button.search__close"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView();", close_button)
                    close_button.click()
                    time.sleep(2)

                except Exception as e:
                    print(f"An error occurred while processing the station: {e}")
                    continue  # Continuar com a próxima estação em caso de erro

        except Exception as e:
            print(f"Error while processing stations: {e}")
            break  # Interromper o loop se houver erro ao tentar encontrar estações

    # Imprimir os resultados
    if station_details:
        print("\nAll Station Details:")
        for detail in station_details:
            print(f"Name: {detail['Name']}")
            print(f"Address: {detail['Address']}")
            print("-" * 40)
    else:
        print("No stations were processed.")

finally:
    # Fechar o navegador
    driver.quit()
