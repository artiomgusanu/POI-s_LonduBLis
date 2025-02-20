import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Caminho para o GeckoDriver
geckodriver_path = "C:\\projects\\POI-s_LonduBlis\\Scraping\\geckodriver.exe"

# Função para inicializar o WebDriver
def init_driver():
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service)
    return driver

# Função para configurar a base de dados
def setup_database():
    conn = sqlite3.connect("stations.db")  # cria o arquivo se não existir
    cursor = conn.cursor()
    # Criar a tabela
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

# Função para salvar os dados no banco de dados
def save_to_database(conn, station_details):
    cursor = conn.cursor()
    for station in station_details:
        cursor.execute("""
            INSERT INTO stations (name, address)
            VALUES (?, ?)
        """, (station["Name"], station["Address"]))
    conn.commit()

# Função para processar uma localidade
def process_locality(driver, locality):
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Local"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", search_input)
        time.sleep(1)

        search_input.clear()
        search_input.send_keys(locality)
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)

        station_details = []
        processed_stations = set()

        stations = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "station"))
        )
        for index, station in enumerate(stations):
            try:
                station = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "station"))
                )[index]
                driver.execute_script("arguments[0].scrollIntoView();", station)
                station.click()
                time.sleep(2)

                name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "highlightLocation__title"))
                ).text
                address = driver.find_element(By.CLASS_NAME, "highlightLocation__address").text
                station_details.append({"Name": name, "Address": address})

                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.search__desktop button.search__close"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", close_button)
                close_button.click()
                time.sleep(2)

            except StaleElementReferenceException:
                print("Stale element encountered. Skipping...")
                continue

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "search__btn.skin--white"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", search_button)
        search_button.click()
        time.sleep(2)

        return station_details

    except Exception as e:
        print(f"Error processing locality {locality}: {e}")
        return []


def main():
    conn = setup_database()
    driver = init_driver()
    results = []

    try:
        driver.get("https://galp.com/pt/mapa")
        time.sleep(10)

        localization_not_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='localization-not']//a[@href='#']"))
        )
        localization_not_button.click()
        time.sleep(2)

        with open("C:\\POI-s_LonduBlis\\scraping\\data\\distritos.txt", "r", encoding="utf-8") as file:
            localities = file.read().splitlines()

        for locality in localities:
            print(f"Processing locality: {locality}")
            result = process_locality(driver, locality)
            save_to_database(conn, result)
            results.extend(result)

    finally:
        driver.quit()
        conn.close()

    if results:
        print("\nAll Station Details:")
        for detail in results:
            print(f"Name: {detail['Name']}")
            print(f"Address: {detail['Address']}")
            print("-" * 40)
    else:
        print("No stations were processed.")

if __name__ == "__main__":
    main()
