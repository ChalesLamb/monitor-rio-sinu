# fews_core.py
import requests
import pandas as pd
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://fews.ideam.gov.co/visorfews/data/series/jsonH/0013067020.json"

ALERTA_ROJA = 5.9
ALERTA_NARANJA = 5.4

def cargar_json():
    r = requests.get(URL, timeout=15, verify=False)
    r.raise_for_status()
    return r.json()

def construir_df(data, variable, campo):
    registros = data[variable]["data"]
    filas = []

    for r in registros:
        if "Fecha" not in r or campo not in r:
            continue
        if r[campo] is None:
            continue
        filas.append((r["Fecha"], r[campo]))

    df = pd.DataFrame(filas, columns=["fecha", campo])
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df[campo] = pd.to_numeric(df[campo], errors="coerce")
    return df.dropna().sort_values("fecha")

def obtener_datos():
    data = cargar_json()

    df_hobs = construir_df(data, "Hobs", "Hobs")
    df_hsen = construir_df(data, "Hsen", "Hsen")
    df_pobs = construir_df(data, "Pobs", "Pobs")

    if not df_hobs.empty:
        df_nivel = df_hobs.rename(columns={"Hobs": "nivel"})
        fuente = "Hobs (Observado)"
    else:
        df_nivel = df_hsen.rename(columns={"Hsen": "nivel"})
        fuente = "Hsen (Sensor)"

    df_nivel["delta_m"] = df_nivel["nivel"].diff()
    df_nivel["delta_h"] = df_nivel["fecha"].diff().dt.total_seconds() / 3600
    df_nivel["vel_m_h"] = df_nivel["delta_m"] / df_nivel["delta_h"]

    return df_nivel, df_pobs, fuente

def estado_actual(df):
    ultimo = df.iloc[-1]
    nivel = ultimo["nivel"]
    vel = ultimo["vel_m_h"]

    if nivel >= ALERTA_ROJA:
        alerta = "🔴 ALERTA ROJA"
    elif nivel >= ALERTA_NARANJA:
        alerta = "🟠 ALERTA NARANJA"
    else:
        alerta = "🟢 NORMAL"

    if vel > 0.005:
        tendencia = "📈 SUBIENDO"
    elif vel < -0.005:
        tendencia = "📉 BAJANDO"
    else:
        tendencia = "➖ ESTABLE"

    return {
        "fecha": ultimo["fecha"],
        "nivel": nivel,
        "velocidad": vel,
        "alerta": alerta,
        "tendencia": tendencia
    }
