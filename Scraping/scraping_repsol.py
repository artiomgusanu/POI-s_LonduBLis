import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

# Inicialização do Selenium WebDriver
driver = webdriver.Chrome()
driver.get("https://www.repsol.pt/localizador-es-e-pontos-carregamento/")

# Aguarde 20 segundos para o carregamento da página
print("Site aberto. Aguardando 20 segundos para carregamento completo...")
time.sleep(20)

# Fechar a janela de cookies
try:
    cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    cookie_button.click()
    print("Janela de cookies fechada.")
except Exception as e:
    print("Nenhuma janela de cookies encontrada ou erro ao fechá-la.")

# Inserir o local na barra de pesquisa e buscar
search_bar = driver.find_element(By.ID, "suggestTxtMap")
search_bar.send_keys("Vila Franca de Xira, Portugal")
print("Busca realizada na barra de pesquisa.")

# Clicar no botão de pesquisa
search_button = driver.find_element(By.CSS_SELECTOR, "button.rp-link-click.buttonSearch")
search_button.click()
print("Botão de busca clicado.")

# Aguardar 10 segundos para carregar os resultados
time.sleep(10)

# Script para interagir com os elementos do mapa
try:
    # Alterar o JavaScript para encontrar e clicar no balão do mapa
    js_script = """
    const potentialMarkers = [];

    // Itera sobre todos os elementos do mapa que possam ser ícones de balões
    const markers = document.querySelectorAll('.marker-dialog, .infoWindow, .gm-style-pbc');

    markers.forEach(marker => {
        const markerType = marker.className;
        if (markerType && (markerType.includes('marker') || markerType.includes('infoWindow') || markerType.includes('gm-style'))) {
            potentialMarkers.push({
                element: marker.outerHTML,
                reason: 'Possível balão no mapa encontrado.',
                className: marker.className
            });
            marker.click();  // Clique no primeiro balão encontrado
            console.log('Balão encontrado e clicado!');
        }
    });

    // Retorna os elementos encontrados e clique no balão
    return JSON.stringify({ potentialMarkers });
    """

    # Executa o script JavaScript no navegador para buscar e clicar no balão
    result = driver.execute_script(js_script)
    data = json.loads(result)
    potential_markers = data.get("potentialMarkers", [])

    if potential_markers:
        print("Elementos encontrados:")
        for marker in potential_markers:
            print(f"ClassName: {marker['className']}, Razão: {marker['reason']}")
    else:
        print("Nenhum balão ou ícone encontrado.")

except Exception as e:
    print(f"Erro ao tentar clicar no balão do mapa: {e}")

finally:
    # Fechar o navegador após o processo
    driver.quit()
    print("Navegador fechado.")
