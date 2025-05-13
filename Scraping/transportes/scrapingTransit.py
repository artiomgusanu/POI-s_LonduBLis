import requests
import pandas as pd
import time

API_KEY = 'k1aBgCRTTg0iQfMyeZlRi98WNzuU6YZB'
BASE_URL = 'https://transit.land/api/v2/rest'

# Função genérica para buscar dados paginados da API
def fetch_all(url, key):
    all_results = []
    while url:
        res = requests.get(url)
        if res.status_code != 200:
            print(f"Erro: {res.status_code} - {res.text}")
            break
        data = res.json()
        all_results.extend(data.get(key, []))
        url = data.get('meta', {}).get('next')
        time.sleep(0.2)  # evitar sobrecarga da API
    return all_results

# Passo 1: Buscar operadores de Portugal
operators_url = f'{BASE_URL}/operators?country=PT&apikey={API_KEY}'
operators = fetch_all(operators_url, 'operators')

# Preparar DataFrames
routes_df = pd.DataFrame()
stops_df = pd.DataFrame()
trips_df = pd.DataFrame()
departures_df = pd.DataFrame()

# Passo 2: Buscar dados por operador
for operator in operators:
    operator_id = operator['onestop_id']
    print(f"Processando operador: {operator_id}")

    # Rotas
    routes_url = f'{BASE_URL}/routes?operated_by={operator_id}&apikey={API_KEY}'
    routes = fetch_all(routes_url, 'routes')
    if routes:
        routes_df = pd.concat([routes_df, pd.json_normalize(routes)], ignore_index=True)

    # Paragens
    stops_url = f'{BASE_URL}/stops?served_by={operator_id}&apikey={API_KEY}'
    stops = fetch_all(stops_url, 'stops')
    if stops:
        stops_df = pd.concat([stops_df, pd.json_normalize(stops)], ignore_index=True)

    # Viagens
    trips_url = f'{BASE_URL}/trips?operated_by={operator_id}&apikey={API_KEY}'
    trips = fetch_all(trips_url, 'trips')
    if trips:
        trips_df = pd.concat([trips_df, pd.json_normalize(trips)], ignore_index=True)

    # Partidas
    departures_url = f'{BASE_URL}/departures?operated_by={operator_id}&apikey={API_KEY}'
    departures = fetch_all(departures_url, 'departures')
    if departures:
        departures_df = pd.concat([departures_df, pd.json_normalize(departures)], ignore_index=True)

# Passo 3: Exportar para Excel
with pd.ExcelWriter('transportes_publicos_portugal.xlsx') as writer:
    routes_df.to_excel(writer, sheet_name='Routes', index=False)
    stops_df.to_excel(writer, sheet_name='Stops', index=False)
    trips_df.to_excel(writer, sheet_name='Trips', index=False)
    departures_df.to_excel(writer, sheet_name='Departures', index=False)

print("Exportação concluída com sucesso!")
