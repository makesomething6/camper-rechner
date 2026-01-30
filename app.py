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
        "🚲 E-Bike laden": {"power": 250.0, "hours": 2.0, "desc": "500Wh Akku"},
        "❄️ Kühlschrank": {"power": 45.0, "hours": 8.0, "desc": "Kompressor 40L"},
        "🚿 Wasserpumpe": {"power": 40.0, "hours": 0.2, "desc": "12V Pumpe"},
        "📺 TV": {"power": 30.0, "hours": 2.0, "desc": "24\" LED"},
        "☕ Kaffeemaschine": {"power": 800.0, "hours": 0.2, "desc": "Camping 12V"}
    }
    
    st.subheader("➕ Gerät hinzufügen")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        preset_name = st.selectbox("🎛️ Schnellwahl", ["-- frei --"] + list(presets.keys()))
    
    with col2:
        if preset_name != "-- frei --" and preset_name in presets:
            default_power = float(presets[preset_name]["power"])
            power = st.number_input("Leistung (W)", value=default_power, min_value=0.0)
        else:
            power = st.number_input("Leistung (W)", value=50.0, min_value=0.0)
    
    with col3:
        if preset_name != "-- frei --" and preset_name in presets:
            default_hours = float(presets[preset_name]["hours"])
            hours = st.number_input("Std/Tag", value=default_hours, min_value=0.0, step=0.1)
        else:
            hours = st.number_input("Std/Tag", value=1.0, min_value=0.0, step=0.1)
    
    with col4:
        if st.button("➕ Hinzufügen", use_container_width=True):
            if power > 0 and hours > 0:
                name = preset_name if preset_name != "-- frei --" else f"Gerät {len(st.session_state.devices)+1}"
                st.session_state.devices.append({"name": name, "power": float(power), "hours": float(hours)})
                st.success(f"✅ {name} hinzugefügt!")
                st.rerun()
    
    if st.session_state.devices:
        st.subheader("📋 Deine Geräte")
        df = pd.DataFrame(st.session_state.devices)
        df["Wh/Tag"] = df["power"] * df["hours"]
        df["Ah/Tag"] = df["Wh/Tag"] / 12
        st.dataframe(df[["name", "power", "hours", "Wh/Tag", "Ah/Tag"]], use_container_width=True)
        
        total_wh, total_ah = calculate_power_consumption(st.session_state.devices)
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("**Tagesverbrauch**", f"{total_wh:.0f} Wh")
        with col2: st.metric("**12V System**", f"{total_ah:.1f} Ah")
        with col3: st.metric("**Batterie nötig**", f"{total_ah*2.5:.0f} Ah")
    else:
        st.info("ℹ️ Füge Geräte hinzu für Berechnung")
    
    st.subheader("☀️ Solaranlage")
    col_sol1, col_sol2 = st.columns(2)
    
    with col_sol1:
        dach_flaeche = st.slider("🚗 Freie Dachfläche (m²)", 1.0, 10.0, 4.0, 0.5)
        wp_pro_m2 = st.slider("📏 Wp/m²", 120.0, 200.0, 175.0, 25.0)
        solar_wp = dach_flaeche * wp_pro_m2
        st.info(f"**Max Solarleistung: {solar_wp:.0f} Wp**")
    
    with col_sol2:
        ort = st.selectbox("🌍 Reiseziel", ["Norwegen (Sommer)", "Südeuropa (Sommer)", "Deutschland (Sommer)", "Skandinavien (Winter)"])
        sonnenstunden = {"Norwegen (Sommer)": 5.0, "Südeuropa (Sommer)": 7.0, "Deutschland (Sommer)": 5.0, "Skandinavien (Winter)": 1.5}[ort]
    
    solar_yield_wh = calculate_solar_yield(solar_wp, sonnenstunden)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: st.metric("**Solarleistung**", f"{solar_wp:.0f} Wp")
    with col_s2: st.metric("**Tägl. Ertrag**", f"{solar_yield_wh:.0f} Wh")
    
    if st.session_state.devices:
        total_wh, _ = calculate_power_consumption(st.session_state.devices)
        autarkie = min(100.0, solar_yield_wh/total_wh*100)
        with col_s3: st.metric("**Autarkie**", f"{autarkie:.0f} %")
        
        if autarkie > 120:
            st.success("✅ Voll autark!")
        elif autarkie > 80:
            st.info("ℹ️ Fast autark – Generator Backup")
        else:
            st.error("❌ Generator/Powerbank nötig!")
    else:
        with col_s3: st.metric("**Autarkie**", "–")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🗑️ Alle löschen", use_container_width=True):
            st.session_state.devices = []
            st.rerun()

st.markdown("---")
st.caption("🎉 Camper Ausbau Plattform v2.0 | Automatisches Speichern")

# VERERWEITERTE SOLARANLAGE + LICHTMASCHINE
    st.subheader("☀️⚡ Energiequellen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # SIMPLIFIED SOLAR - NUR Dachfläche!
        dach_flaeche = st.slider("🚗 Freie Dachfläche (m²)", 1.0, 12.0, 4.0, 0.5)
        solar_wp = dach_flaeche * 175.0  # Camper-Standard
        st.info(f"**Solarleistung: {solar_wp:.0f} Wp** (175 Wp/m²)")
    
    with col2:
        # 30+ Europa Ziele + alle Jahreszeiten
        sonnenstunden = {
            "🇩🇪 Deutschland - Sommer": 6.0,
            "🇩🇪 Deutschland - Frühling": 4.5,
            "🇩🇪 Deutschland - Herbst": 3.5,
            "🇩🇪 Deutschland - Winter": 1.8,
            
            "🇪🇸 Spanien - Sommer": 9.0,
            "🇪🇸 Spanien - Frühling": 7.5,
            "🇪🇸 Spanien - Herbst": 6.5,
            "🇪🇸 Spanien - Winter": 5.5,
            
            "🇵🇹 Portugal - Sommer": 8.5,
            "🇵🇹 Portugal - Frühling": 7.0,
            "🇵🇹 Portugal - Herbst": 6.0,
            "🇵🇹 Portugal - Winter": 5.0,
            
            "🇮🇹 Italien - Sommer": 8.5,
            "🇮🇹 Italien - Frühling": 6.5,
            "🇮🇹 Italien - Herbst": 5.5,
            "🇮🇹 Italien - Winter": 4.0,
            
            "🇬🇷 Griechenland - Sommer": 10.0,
            "🇬🇷 Griechenland - Frühling": 8.0,
            "🇬🇷 Griechenland - Herbst": 7.0,
            "🇬🇷 Griechenland - Winter": 5.0,
            
            "🇫🇷 Frankreich - Sommer": 8.0,
            "🇫🇷 Frankreich - Frühling": 6.0,
            "🇫🇷 Frankreich - Herbst": 5.0,
            "🇫🇷 Frankreich - Winter": 3.0,
            
            "🇳🇱 Niederlande - Sommer": 6.5,
            "🇳🇱 Niederlande - Frühling": 4.5,
            "🇳🇱 Niederlande - Herbst": 3.0,
            "🇳🇱 Niederlande - Winter": 1.5,
            
            "🇦🇹 Österreich - Sommer": 7.0,
            "🇦🇹 Österreich - Frühling": 5.0,
            "🇦🇹 Österreich - Herbst": 4.0,
            "🇦🇹 Österreich - Winter": 2.5,
            
            "🇨🇭 Schweiz - Sommer": 7.0,
            "🇨🇭 Schweiz - Frühling": 5.0,
            "🇨🇭 Schweiz - Herbst": 4.0,
            "🇨🇭 Schweiz - Winter": 2.0,
            
            "🇪🇸 Kanaren - ganzjährig": 6.2,
            "🏝️ Mallorca - Sommer": 9.5,
            "🇲🇹 Malta - Sommer": 10.5
        }
        
        ort = st.selectbox("🌍 Reiseziel + Jahreszeit", list(sonnenstunden.keys()))
        sonnenstunden_tag = sonnenstunden[ort]
    
    # LICHTMASCHINE NEU!
    st.subheader("🚗 Lichtmaschine Laden")
    col_lm1, col_lm2 = st.columns(2)
    
    with col_lm1:
        ladeleistung_a = st.slider("🔋 Ladeleistung Lichtmaschine (A)", 10.0, 70.0, 30.0, 5.0)
    
    with col_lm2:
        fahrzeit_h = st.slider("🛣️ Tägliche Fahrzeit (h)", 0.0, 8.0, 2.0, 0.5)
    
    lichtmaschine_wh = ladeleistung_a * 12.0 * fahrzeit_h * 0.85  # 85% Wirkungsgrad
    
    # GESAMT-ERGEBNIS
    st.subheader("📊 Gesamte Energiebilanz")
    solar_yield_wh = calculate_solar_yield(solar_wp, sonnenstunden_tag)
    gesamte_erzeugung = solar_yield_wh + lichtmaschine_wh
    
    col_total1, col_total2, col_total3, col_total4 = st.columns(4)
    
    with col_total1:
        st.metric("☀️ Solar", f"{solar_yield_wh:.0f} Wh")
    with col_total2:
        st.metric("🚗 Lichtmaschine", f"{lichtmaschine_wh:.0f} Wh")
    with col_total3:
        st.metric("⚡ **GESAMT**", f"{gesamte_erzeugung:.0f} Wh")
    
    # Autarkie mit Lichtmaschine
    if st.session_state.devices:
        total_wh, _ = calculate_power_consumption(st.session_state.devices)
        autarkie_gesamt = min(100.0, gesamte_erzeugung/total_wh*100)
        
        with col_total4:
            st.metric("**Autarkie**", f"{autarkie_gesamt:.0f} %")
        
        col_status1, col_status2 = st.columns(2)
        if autarkie_gesamt > 120:
            col_status1.success("✅ Voll autark!")
            col_status2.success(f"💰 Überschuss: +{gesamte_erzeugung-total_wh:.0f} Wh")
        elif autarkie_gesamt > 90:
            col_status1.success("✅ Perfekt!")
            col_status2.info(f"📈 Reserve: {autarkie_gesamt:.0f}%")
        elif autarkie_gesamt > 70:
            col_status1.info("ℹ️ Sehr gut")
            col_status2.warning(f"⚠️ Generator für Regen")
        else:
            col_status1.error("❌ Ergänzung nötig")
            col_status2.error(f"⚡ Fehl: {total_wh-gesamte_erzeugung:.0f} Wh")
    else:
        with col_total4:
            st.metric("**Autarkie**", "–")
    
    # Delete Button
    if st.button("🗑️ Alle Geräte löschen", use_container_width=True):
        st.session_state.devices = []
        st.rerun()
