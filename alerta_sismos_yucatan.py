import requests
import time
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from twilio.rest import Client

# =============================
# CONFIGURACIÓN GENERAL
# =============================

# Intervalo de verificación (segundos)
INTERVALO = 300  # 5 minutos

# Magnitud mínima
MAG_MIN = 2.5

# Centro de Yucatán + radio
LAT_YUC = 20.7099
LON_YUC = -89.0943
RADIO_KM = 350

# =============================
# TWILIO (WHATSAPP)
# =============================
ACCOUNT_SID = "ACfeb0374be1bd8921d13d111a7409ce84"
AUTH_TOKEN = "df19909b4a1e98f1d481da108ff82fd7"
FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+5219999001029"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# =============================
# MUNICIPIOS DE YUCATÁN (106)
# Coordenadas aproximadas (centro municipal)
# =============================

municipios = {
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

# =============================
# FUNCIONES
# =============================

def distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def municipio_mas_cercano(lat, lon):
    cercano = None
    min_d = float("inf")
    for m, (mlat, mlon) in municipios.items():
        d = distancia_km(lat, lon, mlat, mlon)
        if d < min_d:
            min_d = d
            cercano = m
    return cercano, round(min_d, 2)

def enviar_whatsapp(mensaje):
    client.messages.create(
        body=mensaje,
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP
    )

# =============================
# LOOP PRINCIPAL 24/7
# =============================

ultimo_evento = None


while True:
    try:
        fin = datetime.utcnow()
        inicio = fin - timedelta(minutes=10)

        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "starttime": inicio.isoformat(),
            "endtime": fin.isoformat(),
            "latitude": LAT_YUC,
            "longitude": LON_YUC,
            "maxradiuskm": RADIO_KM,
            "minmagnitude": MAG_MIN
        }

        data = requests.get(url, params=params).json()

        for sismo in data["features"]:
            sid = sismo["id"]
            if sid == ultimo_evento:
                continue

            ultimo_evento = sid
            lat, lon = sismo["geometry"]["coordinates"][1], sismo["geometry"]["coordinates"][0]
            mag = sismo["properties"]["mag"]
            hora = datetime.utcfromtimestamp(sismo["properties"]["time"] / 1000)

            muni, dist = municipio_mas_cercano(lat, lon)

            mensaje = (
                "🚨 SISMO DETECTADO EN YUCATÁN\n"
                f"Magnitud: {mag}\n"
                f"Municipio cercano: {muni}\n"
                f"Distancia: {dist} km\n"
                f"Hora UTC: {hora}"
            )

            enviar_whatsapp(mensaje)

    except Exception as e:
        print("Error:", e)

    time.sleep(INTERVALO)
