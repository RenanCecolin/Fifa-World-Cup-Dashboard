import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Carregar CSV
df = pd.read_csv("WorldCupMatches_1930_2014_PT_BR.csv")

# Estádios únicos
estadios = df["Estadio"].dropna().unique()

geolocator = Nominatim(user_agent="worldcup-dashboard")

dados_estadios = []

for estadio in estadios:
    try:
        print(f"🔍 Buscando localização: {estadio}")
        location = geolocator.geocode(estadio, timeout=10)

        if location:
            dados_estadios.append({
                "Estadio": estadio,
                "Latitude": location.latitude,
                "Longitude": location.longitude
            })
        else:
            dados_estadios.append({
                "Estadio": estadio,
                "Latitude": None,
                "Longitude": None
            })

        time.sleep(1)  # evita bloqueio da API

    except (GeocoderTimedOut, GeocoderUnavailable):
        print(f"⚠️ Timeout no estádio: {estadio}")
        dados_estadios.append({
            "Estadio": estadio,
            "Latitude": None,
            "Longitude": None
        })

# Criar DataFrame
df_estadios = pd.DataFrame(dados_estadios)

# Salvar CSV
df_estadios.to_csv("estadios_lat_long.csv", index=False, encoding="utf-8-sig")

print("✅ Arquivo 'estadios_lat_long.csv' criado com sucesso!")
