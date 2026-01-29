import requests
import time
import os
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
import pytz

# =========================
# CONFIGURACIÓN GENERAL
# =========================

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
INTERVALO = 300  # 5 minutos
MAG_MINIMA = 2.5
ARCHIVO_ULTIMO = "ultimo_sismo_usgs.txt"

# =========================
# TELEGRAM
# =========================

TELEGRAM_TOKEN = os.getenv("8349059546:AAGvF0oBTuath6yuWvWbvt1C2ejcG929egQ")
TELEGRAM_CHAT_ID = os.getenv("6185819291")

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot8349059546:AAGvF0oBTuath6yuWvWbvt1C2ejcG929egQ/sendMessage"
        payload = {
            "chat_id": 6185819291,
            "text": mensaje,
            "parse_mode": "Markdown"
        }
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print("❌ Error Telegram:", r.text)
    except Exception as e:
        print("❌ Error enviando Telegram:", e)

# =========================
# PRUEBA AUTOMÁTICA (NO BORRES)
# =========================

enviar_telegram("🟢 Bot sísmico INICIADO correctamente\n📡 Esperando sismos en México y Yucatán")

# =========================
# ESTADOS DE MÉXICO
# =========================

ESTADOS_MEXICO = [
    "Aguascalientes","Baja California","Baja California Sur","Campeche","Chiapas",
    "Chihuahua","Ciudad de Mexico","Coahuila","Colima","Durango","Estado de Mexico",
    "Guanajuato","Guerrero","Hidalgo","Jalisco","Michoacan","Morelos","Nayarit",
    "Nuevo Leon","Oaxaca","Puebla","Queretaro","Quintana Roo","San Luis Potosi",
    "Sinaloa","Sonora","Tabasco","Tamaulipas","Tlaxcala","Veracruz","Yucatan","Zacatecas"
]

# =========================
# MUNICIPIOS DE YUCATÁN (CENTROIDES)
# =========================

MUNICIPIOS_YUCATAN = {
    "Merida": (20.9674, -89.5926),
    "Kanasin": (20.9342, -89.5581),
    "Progreso": (21.2833, -89.6667),
    "Valladolid": (20.6883, -88.2011),
    "Tizimin": (21.1431, -88.1519),
    "Ticul": (20.3981, -89.5350),
    "Umán": (20.8825, -89.7461),
    "Motul": (21.0969, -89.2836),
    "Oxkutzcab": (20.3056, -89.4189),
    "Peto": (20.1283, -88.9203)
    # (suficiente para detección regional; no falla el bot)
}

# =========================
# FUNCIONES
# =========================

def formatear_hora(timestamp_ms):
    tz = pytz.timezone("America/Merida")
    return datetime.fromtimestamp(timestamp_ms / 1000, tz).strftime("%d/%m/%Y %H:%M:%S")

def distancia_km(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return 6371 * (2 * asin(sqrt(a)))

def municipio_yucatan_cercano(lat, lon):
    cercano = None
    menor = 999999
    for m, (mlat, mlon) in MUNICIPIOS_YUCATAN.items():
        d = distancia_km(lat, lon, mlat, mlon)
        if d < menor:
            menor = d
            cercano = m
    return cercano, round(menor, 1)

def obtener_estado(lugar):
    if not lugar:
        return None
    lugar = lugar.lower()
    for e in ESTADOS_MEXICO:
        if e.lower() in lugar:
            return e
    return None

def cargar_ultimo():
    if os.path.exists(ARCHIVO_ULTIMO):
        return open(ARCHIVO_ULTIMO).read().strip()
    return None

def guardar_ultimo(id_sismo):
    with open(ARCHIVO_ULTIMO, "w") as f:
        f.write(id_sismo)

# =========================
# VERIFICACIÓN USGS
# =========================

def verificar_usgs():
    ultimo = cargar_ultimo()
    data = requests.get(USGS_URL, timeout=15).json()

    for f in data["features"]:
        p = f["properties"]
        g = f["geometry"]["coordinates"]

        if not p["mag"] or p["mag"] < MAG_MINIMA:
            continue

        if f["id"] == ultimo:
            continue

        lat, lon = g[1], g[0]
        lugar = p["place"]
        hora = formatear_hora(p["time"])

        estado = obtener_estado(lugar)
        municipio, dist = municipio_yucatan_cercano(lat, lon)

        mensaje = (
            "🚨 *SISMO DETECTADO*\n\n"
            f"🌍 Lugar: {lugar}\n"
            f"📊 Magnitud: {p['mag']}\n"
            f"🕒 Hora: {hora}\n"
        )

        if municipio and dist <= 150:
            mensaje += f"📍 Municipio Yucatán: {municipio} ({dist} km)\n"

        if estado:
            mensaje += f"🇲🇽 Estado: {estado}"

        enviar_telegram(mensaje)
        guardar_ultimo(f["id"])
        break

# =========================
# EJECUCIÓN CONTINUA
# =========================

print("🟢 Bot sísmico activo (Telegram)")
while True:
    try:
        verificar_usgs()
    except Exception as e:
        print("⚠️ Error:", e)
    time.sleep(INTERVALO)

