import requests
import time
import os
from math import radians, cos, sin, asin, sqrt
from twilio.rest import Client
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

# =========================
# CONFIGURACIÓN
# =========================

INTERVALO = 300
MAG_MIN_USGS = 2.5
MAG_MIN_SSN = 1.5

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
SSN_URL = "https://www.ssn.unam.mx/sismicidad/ultimos/"

ARCHIVO_USGS = "ultimo_usgs.txt"
ARCHIVO_SSN = "ultimo_ssn.txt"

# =========================
# ESTADOS DE MÉXICO
# =========================

ESTADOS_MEXICO = [
    "aguascalientes","baja california","baja california sur","campeche",
    "chiapas","chihuahua","ciudad de mexico","coahuila","colima","durango",
    "estado de mexico","guanajuato","guerrero","hidalgo","jalisco","michoacan",
    "morelos","nayarit","nuevo leon","oaxaca","puebla","queretaro",
    "quintana roo","san luis potosi","sinaloa","sonora","tabasco",
    "tamaulipas","tlaxcala","veracruz","yucatan","zacatecas"
]

# =========================
# MUNICIPIOS DE YUCATÁN
# =========================

MUNICIPIOS_YUCATAN = {
    "Abalá": (20.6489, -89.7133),
    "Acanceh": (20.8136, -89.4525),
    "Akil": (20.2639, -89.3467),
    "Baca": (21.1067, -89.3947),
    "Bokobá": (21.0103, -89.1539),
    "Buctzotz": (21.2031, -88.7931),
    "Cacalchén": (20.9836, -89.2267),
    "Calotmul": (21.0203, -88.2389),
    "Cansahcab": (21.1572, -89.1017),
    "Cantamayec": (20.4611, -89.0839),
    "Celestún": (20.8667, -90.4000),
    "Cenotillo": (20.9669, -88.6042),
    "Chacsinkín": (20.1675, -89.0158),
    "Chankom": (20.6406, -88.5242),
    "Chapab": (20.4569, -89.4625),
    "Chemax": (20.6569, -87.9367),
    "Chichimilá": (20.6247, -88.2169),
    "Chikindzonot": (20.3275, -88.4958),
    "Chocholá": (20.7508, -89.8539),
    "Chumayel": (20.4342, -89.3086),
    "Conkal": (21.0736, -89.5186),
    "Cuncunul": (20.6347, -88.3089),
    "Cuzamá": (20.7364, -89.3164),
    "Dzán": (20.3889, -89.4708),
    "Dzemul": (21.2128, -89.3075),
    "Dzidzantún": (21.2486, -89.0425),
    "Dzilam de Bravo": (21.3922, -88.8986),
    "Dzilam González": (21.2839, -88.9353),
    "Dzitás": (20.8669, -88.5303),
    "Dzoncauich": (21.1019, -88.8461),
    "Espita": (21.0103, -88.3069),
    "Halachó": (20.4814, -90.0806),
    "Hocabá": (20.8156, -89.2503),
    "Hoctún": (20.8675, -89.1997),
    "Homún": (20.7381, -89.2856),
    "Huhí": (20.7083, -89.1489),
    "Hunucmá": (21.0178, -89.8736),
    "Ixil": (21.1522, -89.4781),
    "Izamal": (20.9356, -89.0189),
    "Kanasín": (20.9342, -89.5581),
    "Kantunil": (20.7983, -88.9842),
    "Kaua": (20.6178, -88.4217),
    "Kinchil": (20.9094, -89.9447),
    "Kopomá": (20.6425, -89.9086),
    "Mama": (20.4775, -89.3664),
    "Maní": (20.3869, -89.3944),
    "Maxcanú": (20.5861, -90.0017),
    "Mayapán": (20.4686, -89.2153),
    "Mérida": (20.9674, -89.5926),
    "Mocochá": (21.1064, -89.4558),
    "Motul": (21.0969, -89.2836),
    "Muna": (20.4886, -89.7133),
    "Muxupip": (21.0369, -89.3178),
    "Opichén": (20.5558, -89.8572),
    "Oxkutzcab": (20.3056, -89.4189),
    "Panabá": (21.2928, -88.2697),
    "Peto": (20.1283, -88.9203),
    "Progreso": (21.2833, -89.6667),
    "Quintana Roo": (20.8664, -88.9036),
    "Río Lagartos": (21.5958, -88.1606),
    "Sacalum": (20.5203, -89.5886),
    "Samahil": (20.8819, -89.8872),
    "Sanahcat": (20.7819, -89.2172),
    "San Felipe": (21.6036, -88.2253),
    "Santa Elena": (20.3306, -89.6436),
    "Seyé": (20.8394, -89.3719),
    "Sinanché": (21.2272, -89.1875),
    "Sotuta": (20.5964, -89.0075),
    "Sucilá": (21.1569, -88.3069),
    "Sudzal": (20.8664, -88.9869),
    "Suma": (21.1097, -89.1572),
    "Tahdziú": (20.2442, -88.9506),
    "Tahmek": (20.8811, -89.2594),
    "Teabo": (20.4008, -89.2831),
    "Tecoh": (20.7392, -89.4719),
    "Tekal de Venegas": (21.2003, -88.7983),
    "Tekantó": (20.9242, -89.0897),
    "Tekax": (20.2069, -89.2836),
    "Tekit": (20.5325, -89.3328),
    "Tekom": (20.6058, -88.2656),
    "Telchac Pueblo": (21.2006, -89.2644),
    "Telchac Puerto": (21.3336, -89.2625),
    "Temax": (21.1508, -88.9369),
    "Temozón": (20.8008, -88.2019),
    "Tepakán": (20.9803, -89.0722),
    "Tetiz": (20.9769, -89.9303),
    "Teya": (21.0511, -89.0733),
    "Ticul": (20.3981, -89.5350),
    "Timucuy": (20.8122, -89.5258),
    "Tinum": (20.7483, -88.5814),
    "Tixcacalcupul": (20.4783, -88.3111),
    "Tixkokob": (21.0003, -89.3922),
    "Tixmehuac": (20.2475, -89.0258),
    "Tixpéhual": (20.9853, -89.4647),
    "Tizimín": (21.1431, -88.1519),
    "Tunkás": (20.8847, -88.7458),
    "Tzucacab": (20.0706, -89.0489),
    "Uayma": (20.7419, -88.3258),
    "Ucú": (20.9883, -89.7531),
    "Umán": (20.8825, -89.7461),
    "Valladolid": (20.6883, -88.2011),
    "Xocchel": (20.8331, -89.1839),
    "Yaxcabá": (20.5253, -89.1897),
    "Yaxkukul": (21.0833, -89.4167),
    "Yobaín": (21.1944, -89.0853)
}
# =========================
# TWILIO
# =========================

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

FROM_WA = os.getenv("FROM_WHATSAPP")
TO_WA = os.getenv("TO_WHATSAPP")

# =========================
# UTILIDADES
# =========================

def hora_local(timestamp_ms):
    zona = pytz.timezone("America/Merida")
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=pytz.utc)\
        .astimezone(zona).strftime("%d/%m/%Y %H:%M:%S")

def enviar_whatsapp(mensaje):
    msg = client.messages.create(
        from_=FROM_WA,
        to=TO_WA,
        body=mensaje
    )
    print("📲 Mensaje enviado:", msg.sid)

def cargar_ultimo(path):
    if os.path.exists(path):
        return open(path).read().strip()
    return None

def guardar_ultimo(path, valor):
    with open(path, "w") as f:
        f.write(valor)

def distancia_km(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return 6371 * (2 * asin(sqrt(a)))

def municipio_cercano(lat, lon):
    cercano, menor = None, 999999
    for m, (mlat, mlon) in MUNICIPIOS_YUCATAN.items():
        d = distancia_km(lat, lon, mlat, mlon)
        if d < menor:
            cercano, menor = m, d
    return cercano, round(menor, 2)

def detectar_estado(lugar):
    if not lugar:
        return None
    l = lugar.lower()
    for e in ESTADOS_MEXICO:
        if e in l:
            return e.title()
    return None

# =========================
# USGS
# =========================

def verificar_usgs():
    ultimo = cargar_ultimo(ARCHIVO_USGS)
    data = requests.get(USGS_URL, timeout=15).json()

    for f in data["features"]:
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"][:2]

        if not p["mag"] or p["mag"] < MAG_MIN_USGS:
            continue

        if f["id"] == ultimo:
            continue

        municipio, dist = municipio_cercano(lat, lon)
        estado = detectar_estado(p["place"])

        mensaje = None

        if municipio and dist <= 150:
            mensaje = (
                "🚨 *SISMO EN YUCATÁN (USGS)*\n\n"
                f"📍 Municipio: {municipio}\n"
                f"📏 Distancia: {dist} km\n"
                f"📊 Magnitud: {p['mag']}\n"
                f"🕒 Hora: {hora_local(p['time'])}"
            )
        elif estado:
            mensaje = (
                "🚨 *SISMO EN MÉXICO (USGS)*\n\n"
                f"📍 Estado: {estado}\n"
                f"📊 Magnitud: {p['mag']}\n"
                f"🕒 Hora: {hora_local(p['time'])}"
            )

        if mensaje:
            enviar_whatsapp(mensaje)
            guardar_ultimo(ARCHIVO_USGS, f["id"])
            break

# =========================
# SSN
# =========================

def verificar_ssn():
    ultimo = cargar_ultimo(ARCHIVO_SSN)
    html = requests.get(SSN_URL, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    fila = soup.find("table").find_all("tr")[1]
    cols = fila.find_all("td")

    fecha = cols[0].text.strip()
    hora = cols[1].text.strip()
    mag = float(cols[4].text.strip())
    lugar = cols[7].text.strip()

    sismo_id = fecha + hora + lugar

    if mag < MAG_MIN_SSN or sismo_id == ultimo:
        return

    mensaje = (
        "🇲🇽 *SISMO DETECTADO (SSN)*\n\n"
        f"📍 Lugar: {lugar}\n"
        f"📊 Magnitud: {mag}\n"
        f"🕒 Fecha y hora: {fecha} {hora}"
    )

    enviar_whatsapp(mensaje)
    guardar_ultimo(ARCHIVO_SSN, sismo_id)

# =========================
# EJECUCIÓN
# =========================

print("🟢 Bot sísmico México + Yucatán activo")

while True:
    try:
        verificar_usgs()
        verificar_ssn()
    except Exception as e:
        print("⚠️ Error:", e)

    time.sleep(INTERVALO)




