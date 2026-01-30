import streamlit as st
import math
import pandas as pd

# Heizungs-Funktionen (bleiben gleich)
@st.cache_data
def calculate_u_value(thickness_mm, lambda_value):
    return lambda_value / (thickness_mm / 1000)

@st.cache_data
def calculate_heating_power(surface_m2, u_value, delta_t):
    return (surface_m2 * u_value * delta_t) / 1000

# Stromrechner Funktionen
@st.cache_data
def calculate_power_consumption(device_list):
    total_wh = sum(device["power_w"] * device["hours"] for device in device_list)
    total_ah = total_wh / 12  # 12V System
    return total_wh, total_ah

@st.cache_data
def calculate_solar_yield(panel_wp, sun_hours):
    efficiency = 0.8  # Systemverluste
    return panel_wp * sun_hours * efficiency

st.set_page_config(page_title="Camper Ausbau Rechner", layout="wide")

st.title("🚐 Camper Ausbau Plattform")
tab1, tab2 = st.tabs(["🔥 Heizung", "⚡ Strom & Solar"])

# HEIZUNGS-RECHNER (oben unverändert)
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
            "1️⃣ Schlecht (Blech)": {"dicke": 10, "lambda": 0.040},
            "2️⃣ Normal (Armaflex)": {"dicke": 19, "lambda": 0.035},
            "3️⃣ Gut (Doppeldämmung)": {"dicke": 30, "lambda": 0.034},
            "4️⃣ Sehr gut": {"dicke": 50, "lambda": 0.033}
        }
        daemm_wahl = st.selectbox("Dämmklasse", list(daemm_klassen.keys()))
        daemm_data = daemm_klassen[daemm_wahl]
    
    # Berechnungen
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

# STROM-RECHNER (NEU!)
with tab2:
    st.header("⚡ Strombedarf & Solar")
    
    # Standardgeräte Presets
    presets = {
        "📱 Handy laden": {"power": 20, "hours": 1},
        "💻 Laptop laden": {"power": 80, "hours": 1},
        "💡 LED Licht": {"power": 8, "hours": 4},
        "🔥 Standheizung": {"power": 50, "hours": 2},
        "🍳 Elektrokocher": {"power": 1000, "hours": 0.5},
        "🚲 E-Bike laden": {"power": 250, "hours": 2},
        "❄️ Kühlschrank": {"power": 50, "hours": 24/3}  # 1/3 Einschaltquote
    }
    
    # Dynamische Geräte-Liste
    if 'devices' not in st.session_state:
        st.session_state.devices = [{"name": "", "power": 0, "hours": 0}]
    
    st.subheader("Geräte hinzufügen")
    col_add1, col_add2, col_add3 = st.columns(3)
    
    with col_add1:
        preset = st.selectbox("Schnellwahl", ["Benutzerdefiniert"] + list(presets.keys()))
        if preset != "Benutzerdefiniert":
            st.session_state.devices[-1] = presets[preset].copy()
            st.session_state.devices[-1]["name"] = preset
    
    with col_add2:
        st.session_state.devices[-1]["power"] = st.number_input("Leistung (W)", 
            value=st.session_state.devices[-1]["power"], min_value=0.0)
    
    with col_add3:
        st.session_state.devices[-1]["hours"] = st.number_input("Std/Tag", 
            value=st.session_state.devices[-1]["hours"], min_value=0.0, step=0.1)
        if st.button("➕ Gerät hinzufügen"): 
            st.session_state.devices.append({"name": "", "power": 0, "hours": 0})
    
    # Geräte-Tabelle
    st.subheader("Deine Geräte")
    df_devices = pd.DataFrame(st.session_state.devices)
    df_devices["Wh/Tag"] = df_devices["power"] * df_devices["hours"]
    st.dataframe(df_devices[["name", "power", "hours", "Wh/Tag"]], use_container_width=True)
    
    total_wh, total_ah = calculate_power_consumption(st.session_state.devices)
    
    col1, col2, col3 = st.columns(3)
    with
