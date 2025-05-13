import requests
import csv
import os
import time

# Cria pastas se não existirem
os.makedirs("output", exist_ok=True)

# 1. Obter lista de estações
STATIONS_URL = "https://www.cp.pt/sites/spring/station-index"
TRAINS_URL = "https://www.cp.pt/sites/spring/station/trains?stationId={}"
TRAIN_DETAIL_URL = "https://www.cp.pt/sites/spring/station/trains/train?trainId={}"

print("🔄 A obter lista de estações...")
stations_resp = requests.get(STATIONS_URL)
stations_data = stations_resp.json()

# Guardar estações
with open("output/stations.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "lat", "lon", "district", "county", "locality"])
    writer.writeheader()
    for name, station_id in stations_data.items():
        writer.writerow({
            "id": station_id,
            "name": name,
            "lat": "",
            "lon": "",
            "district": "",
            "county": "",
            "locality": "",
        })

# Preparar CSVs para comboios
trains_per_station_file = open("output/trains_per_station.csv", "w", newline="", encoding="utf-8")
trains_writer = csv.DictWriter(trains_per_station_file, fieldnames=["station_id", "train_id", "train_service", "departureTime", "arrivalTime", "direction", "destination"])
trains_writer.writeheader()

train_details_set = set()
train_details = []

print("🔄 A recolher comboios por estação...")
# 2. Para cada estação, obter comboios
for name, station_id in stations_data.items():
    url = TRAINS_URL.format(station_id)
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            continue
        trains = resp.json()

        for train in trains:
            train_number = train.get("trainNumber")
            if not train_number:
                continue

            origin = train.get("trainOrigin", {}).get("designation") or "Desconhecido"
            destination = train.get("trainDestination", {}).get("designation") or "Desconhecido"
            direction = f"{origin} → {destination}"

            service_code = train.get("trainService", {}).get("code") or "Desconhecido"
            service_designation = train.get("trainService", {}).get("designation") or "Desconhecido"
            train_service = f"{service_code} - {service_designation}"

            trains_writer.writerow({
                "station_id": station_id,
                "train_id": train_number,
                "train_service": train_service,
                "departureTime": train.get("departureTime"),
                "arrivalTime": train.get("arrivalTime"),
                "direction": direction,
                "destination": destination
            })
            train_details_set.add(train_number)

    except Exception as e:
        print(f"Erro com estação {station_id}: {e}")
    time.sleep(0.2)  # evitar sobrecarga

trains_per_station_file.close()

# 3. Obter detalhes dos comboios
print("🔄 A recolher detalhes de comboios...")
with open("output/train_details.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["train_id", "train_type", "station_code", "station_name",
                  "arrival", "departure", "eta", "etd", "delay", "platform", "latitude", "longitude"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for train_id in train_details_set:
        url = TRAIN_DETAIL_URL.format(train_id)
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                continue
            t = resp.json()

            service_code = t.get("serviceCode", {}).get("code", "Desconhecido")
            service_designation = t.get("serviceCode", {}).get("designation") or "Desconhecido"
            train_type = f"{service_code} - {service_designation}"

            stops = t.get("trainStops", [])
            for stop in stops:
                station = stop.get("station", {})
                writer.writerow({
                    "train_id": t.get("trainNumber"),
                    "train_type": train_type,
                    "station_code": station.get("code", ""),
                    "station_name": station.get("designation", ""),
                    "arrival": stop.get("arrival") or "",
                    "departure": stop.get("departure") or "",
                    "eta": stop.get("eta") or "",
                    "etd": stop.get("etd") or "",
                    "delay": stop.get("delay") or "",
                    "platform": stop.get("platform") or "",
                    "latitude": stop.get("latitude") or "",
                    "longitude": stop.get("longitude") or ""
                })

        except Exception as e:
            print(f"Erro com comboio {train_id}: {e}")
        time.sleep(0.2)

print("✅ Fim da recolha de dados. CSVs gerados na pasta 'output'")
