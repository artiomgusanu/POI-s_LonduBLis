import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://api.carrismetropolitana.pt"

def fetch_data(endpoint):
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 1. Paragens (Stops)
def get_stops():
    data = fetch_data("/stops")
    rows = []
    for stop in data:
        rows.append({
            "ID": stop.get("id"),
            "Nome": stop.get("name"),
            "Latitude": stop.get("lat"),
            "Longitude": stop.get("lon"),
            "Localidade": stop.get("locality"),
            "Município": stop.get("municipality"),
            "Distrito": stop.get("district"),
            "Linhas": ", ".join(stop.get("lines", []))
        })
    return pd.DataFrame(rows)

# 2. Linhas (Lines)
def get_lines():
    data = fetch_data("/lines")
    rows = []
    for line in data:
        rows.append({
            "ID": line.get("id"),
            "Nome Curto": line.get("short_name"),
            "Nome Longo": line.get("long_name"),
            "Cor": line.get("color"),
            "Municípios": ", ".join(str(m) for m in line.get("municipalities", []) if m),
            "Localidades": ", ".join(str(l) for l in line.get("localities", []) if l)
        })
    return pd.DataFrame(rows)


# 3. Veículos em tempo real
def get_vehicles():
    data = fetch_data("/vehicles")
    rows = []
    for vehicle in data:
        rows.append({
            "ID": vehicle.get("vehicle_id"),
            "Latitude": vehicle.get("lat"),
            "Longitude": vehicle.get("lon"),
            "Velocidade (km/h)": vehicle.get("speed"),
            "Direção (°)": vehicle.get("heading"),
            "ID Viagem": vehicle.get("trip_id"),
            "Timestamp": vehicle.get("timestamp")
        })
    return pd.DataFrame(rows)

# 4. Escolas
def get_schools():
    data = fetch_data("/datasets/facilities/schools")
    rows = []
    for school in data:
        rows.append({
            "ID Escola": school.get("id"),
            "Nome": school.get("name"),
            "Latitude": school.get("lat"),
            "Longitude": school.get("lon"),
            "Morada": school.get("address"),
            "Código Postal": school.get("postal_code"),
            "Localidade": school.get("locality"),
            "Município": school.get("municipality"),
            "Paragens Associadas": ", ".join(school.get("stops", []))
        })
    return pd.DataFrame(rows)

# 5. Alertas
def get_alerts():
    data = fetch_data("/alerts")
    rows = []
    for alert in data:
        # Descrição em português
        description = ""
        if "description_text" in alert:
            translations = alert["description_text"].get("translation", [])
            for t in translations:
                if t.get("language") == "pt":
                    description = t.get("text")
                    break

        # IDs das linhas afetadas
        route_ids = [e.get("route_id") for e in alert.get("informed_entity", []) if e.get("route_id")]

        rows.append({
            "Causa": alert.get("cause"),
            "Descrição (pt)": description,
            "Linhas Afetadas": ", ".join(route_ids)
        })
    return pd.DataFrame(rows)

#6. Caracteriticas de Veiculos
def get_vehicle_characteristics():
    data = fetch_data("/v2/vehicles")
    rows = []
    for v in data:
        # Conversão segura da data de matrícula
        reg_date_raw = v.get("registration_date")
        if reg_date_raw and len(reg_date_raw) == 8:
            try:
                reg_date = datetime.strptime(reg_date_raw, "%Y%m%d").strftime("%Y-%m-%d")
            except:
                reg_date = reg_date_raw
        else:
            reg_date = None

        rows.append({
            "ID Veículo": v.get("id"),
            "Matrícula": v.get("license_plate") or "",
            "Marca": v.get("make") or "",
            "Modelo": v.get("model") or "",
            "Tipo de Propulsão": v.get("propulsion") or "",
            "Proprietário": v.get("owner") or "",
            "Lotação Sentados": v.get("capacity_seated") or 0,
            "Lotação em Pé": v.get("capacity_standing") or 0,
            "Lotação Total": v.get("capacity_total") or 0,
            "Acessível a Cadeira de Rodas": v.get("wheelchair_accessible"),
            "Permite Bicicletas": v.get("bikes_allowed"),
            "Data de Matrícula": reg_date,
            "Portas": v.get("door_status") or "",
            "Status Atual": v.get("current_status") or "",
            "Relação com Horário": v.get("schedule_relationship") or "",
            "Latitude": v.get("lat"),
            "Longitude": v.get("lon"),
            "Velocidade (km/h)": v.get("speed"),
            "Bearing (º)": v.get("bearing")
        })

    return pd.DataFrame(rows)

# Salvar tudo em um único Excel
def save_to_excel():
    with pd.ExcelWriter("carris_metropolitana_dados00.xlsx", engine="openpyxl") as writer:
        get_stops().to_excel(writer, sheet_name="Paragens", index=False)
        get_lines().to_excel(writer, sheet_name="Linhas", index=False)
        get_vehicles().to_excel(writer, sheet_name="Veículos", index=False)
        get_vehicle_characteristics().to_excel(writer, sheet_name="Características Veículos", index=False)
        get_schools().to_excel(writer, sheet_name="Escolas", index=False)
        get_alerts().to_excel(writer, sheet_name="Alertas", index=False)
    print("✅ Arquivo Excel criado: carris_metropolitana_dados.xlsx")

# Execução
if __name__ == "__main__":
    save_to_excel()
