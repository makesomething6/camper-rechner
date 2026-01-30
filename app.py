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
    total_ah = total_wh / 12  # 12V System
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

with tab2:
    st.header("⚡ Strombedarf & Solar")
    
    # Session State
    if 'devices' not in st.session_state:
        st.session_state.devices = []
    
    # REALISTISCHE PRESETS [web:42][web:46]
    presets = {
        "📱 Handy laden": {"power": 15, "hours": 2, "desc": "USB 12V"},
        "💻 Laptop laden": {"power": 65, "hours": 3, "desc": "12V Ladegerät"},
        "💡 LED Licht": {"power": 15, "hours": 4, "desc": "4x 4W Spots"},
        "🔥 Standheizung": {"power": 28, "hours": 3, "desc": "Webasto/ET"},
        "🍳 Elektrokocher": {"power": 1500, "hours": 0.25, "desc": "Induktion 230V"},
        "🚲 E-Bike laden": {"power": 250, "hours": 2, "desc": "500Wh Akku"},
        "❄️ Kühlschrank": {"power": 45, "hours": 8, "desc": "Kompressor 40L"},
        "🚿 Wasserpumpe": {"power": 40, "hours": 0.2, "desc": "12V Pumpe"},
        "📺 TV": {"power": 30, "hours": 2, "desc": "24\" LED"},
        "☕ Kaffeemaschine": {"power": 800, "hours": 0.2, "desc": "Camping 12V"}
    }
    
    # Neues Gerät - AUTO-Werte + EDITIERBAR
    st.subheader("➕ Gerät hinzufügen")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        preset_name = st.selectbox("🎛️ Schnellwahl", ["-- frei --"] + list(presets.keys()))
    
    with col2:
        if preset_name != "-- frei --" and preset_name in presets:
            default_power = presets[preset_name]["power"]
            power = st.number_input("Leistung (W)", value=default_power, min_value=0.0,
                                   help=f"Auto: {default_power}W ({presets[preset_name]['desc']})")
        else:
            power = st.number_input("Leistung (W)", value=50.0, min_value=0.0)
    
    with col3:
        if preset_name != "-- frei --" and preset_name in presets:
            default_hours = presets[preset_name]["hours"]
            hours = st.number_input("Std/Tag", value=default_hours, min_value=0.0, step=0.1,
                                   help=f"Auto: {default_hours}h/Tag")
        else:
            hours = st.number_input("Std/Tag", value=1.0, min_value=0.0, step=0.1)
    
    with col4:
        if st.button("➕ Hinzufügen", use_container_width=True) and power > 0 and hours > 0:
            name = preset_name if preset_name != "-- frei --" else f"Gerät {len(st.session_state.devices)+1}"
            st.session_state.devices.append({"name": name, "power": float(power), "hours": float(hours)})
            st.success(f"✅ {name} hinzugefügt!")
            st.rerun()
    
    # Tabelle + Summen
    if st.session_state.devices:
        st.subheader("📋 Deine Geräte")
        df = pd.DataFrame(st.session_state.devices)
        df["Wh/Tag"] = df["power"] * df["hours"]
        df["Ah/Tag"] = df["Wh/Tag"] / 12
        st.dataframe(df[["name", "power", "hours", "Wh/Tag", "Ah/Tag"]], use_container_width=True)
        
        total_wh, total_ah = calculate_power_consumption(st.session_state.devices)
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("**Tagesverbrauch**",
