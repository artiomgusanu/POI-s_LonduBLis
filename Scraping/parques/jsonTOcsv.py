import json
import csv

# Caminho do arquivo JSON exportado da Overpass
input_file = 'C:\\Users\\artio\\Downloads\\export (3).json'
output_file = 'parques_estacionamento_portugal.csv'

# Abrir e carregar os dados JSON
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Abrir arquivo CSV para escrita
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'type', 'name', 'latitude', 'longitude', 'capacity', 'access']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for element in data['elements']:
        tags = element.get('tags', {})
        writer.writerow({
            'id': element.get('id'),
            'type': element.get('type'),
            'name': tags.get('name', ''),
            'latitude': element.get('lat') or element.get('center', {}).get('lat'),
            'longitude': element.get('lon') or element.get('center', {}).get('lon'),
            'capacity': tags.get('capacity', ''),
            'access': tags.get('access', '')
        })

print(f"Arquivo CSV gerado com sucesso: {output_file}")
