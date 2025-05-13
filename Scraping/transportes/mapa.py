import pandas as pd
import folium

# Lê o Excel
df = pd.read_excel('paragens_autocarros.xlsx', sheet_name='Folha1')

# Cria o mapa centrado em Alcochete (média das coordenadas)
centro_lat = df['Latitude'].mean()
centro_lon = df['Longitude'].mean()
mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=14)

# Adiciona as paragens ao mapa
for _, row in df.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=row['Nome'],
        icon=folium.Icon(color='blue', icon='bus', prefix='fa')
    ).add_to(mapa)

# Guarda o resultado
mapa.save('mapa_paragens_autocarros.html')
