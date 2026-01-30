import streamlit as st
import pandas as pd

# Heizungs-Funktionen
@st.cache_data
def calculate_u_value(thickness_mm, lambda_value):
    return lambda_value / (thickness_mm / 1000)

@st.cache_data
def calculate_heating_power(surface_m2, u_value, delta_t):
    return (surface_m2 * u_value * delta_t) / 1000

# Stromrechner Funktionen
@st.cache_data
def calculate_power_consumption(device_list):
    total_wh = sum(device["power"] * device["hours"] for device in device_list)
    total_ah = total_wh / 12
    return total_wh, total_ah

@st.cache_data
def calculate_solar_yield(panel_wp, sun_hours):
    efficiency = 0.8
    return panel_wp * sun_hours * efficiency

st.set_page_config(page_title="Camper Ausbau Rechner", layout="wide")

st.title("🚐 Camper Ausbau Plattform")
tab1, tab2 = st.tabs(["🔥 Heizung", "⚡ Strom & Solar"])

with tab1:
    st.header("Heizleistungs-Rechner")
    
    col1, col2, col3 = st.columns(3)
    with col1: 
        laenge = st.slider("Länge innen (m)", 2.0, 7.0, 4.2)
        breite = st.slider("Breite innen (m)", 1.5, 2.2, 1.8)
        hoehe = st.slider("Höhe innen (m)", 1.6, 2.2, 1.8)
    
    with col2:
        ausen_temp = st.slider("Außentemperatur (°C)", -25.0, 10.0, -10.0)
        innen_temp = st.slider("Ziel-Innentemperatur (°C)", 15.0, 25.0, 20.0)
        delta_t = innen_temp - ausen_temp
    
    with col3:
        daemm_klassen = {
            "1️⃣ Schlecht (Blech)": {"dicke": 10.0, "lambda": 0.040},
            "2️⃣ Normal (Armaflex)": {"dicke": 19.0, "lambda": 0.035},
            "3️⃣ Gut (Doppeldämmung)": {"dicke": 30.0, "lambda": 0.034},
            "4️⃣ Sehr gut": {"dicke": 50.0, "lambda": 0.033}
        }
        daemm_wahl = st.selectbox("Dämmklasse", list(daemm_klassen.keys()))
        daemm_data = daemm_klassen[daemm_wahl]
    
    volumen = laenge * breite * hoehe
    surface = 2 * laenge * hoehe + 2 * breite * hoehe + laenge * breite * 1.2
    u_wert = calculate_u_value(daemm_data["dicke"], daemm_data["lambda"])
    leistung_kw = calculate_heating_power(surface, u_wert, delta_t)
    
    col_heiz1, col_heiz2, col_heiz3 = st.columns(3)
    with col_heiz1: st.metric("Volumen", f"{volumen:.1f} m³")
    with col_heiz2: st.metric("U-Wert", f"{u_wert:.2f} W/m²K")
    with col_heiz3: st.metric("**Heizleistung**", f"{leistung_kw:.1f} kW")
    
    if leistung_kw < 2: st.success("✅ 2 kW reicht")
    elif leistung_kw < 4: st.warning("⚠️ 4 kW empfohlen")
    else: st.error("❌ 6+ kW nötig")

with tab2:
    st.header("⚡ Strombedarf & Solar")
    
    if 'devices' not in st.session_state:
        st.session_state.devices = []
    
    presets = {
        "📱 Handy laden": {"power": 15.0, "hours": 2.0, "desc": "USB 12V"},
        "💻 Laptop laden": {"power": 65.0, "hours": 3.0, "desc": "12V Ladegerät"},
        "💡 LED Licht": {"power": 15.0, "hours": 4.0, "desc": "4x 4W Spots"},
        "🔥 Standheizung": {"power": 28.0, "hours": 3.0, "desc": "Webasto/ET"},
        "🍳 Elektrokocher": {"power": 1500.0, "hours": 0.25, "desc": "Induktion 230V"},
        "🚲 E-
