import streamlit as st
import math

@st.cache_data
def calculate_u_value(thickness_mm, lambda_value):
    return lambda_value / (thickness_mm / 1000)

@st.cache_data
def calculate_heating_power(surface_m2, u_value, delta_t):
    return (surface_m2 * u_value * delta_t) / 1000

st.set_page_config(page_title="Camper Heizungs-Rechner", layout="wide")

st.title("🔥 Camper Heizleistungs-Rechner")
st.markdown("Gib deine Fahrzeugdaten ein und erhalte sofort die benötigte Heizleistung!")

# Sidebar für Eingaben
st.sidebar.header("📏 Fahrzeugmaße")
laenge = st.sidebar.slider("Länge innen (m)", 2.0, 7.0, 4.2)
breite = st.sidebar.slider("Breite innen (m)", 1.5, 2.2, 1.8)
hoehe = st.sidebar.slider("Höhe innen (m)", 1.6, 2.2, 1.8)

st.sidebar.header("🌡️ Temperaturen")
ausen_temp = st.sidebar.slider("Außentemperatur (°C)", -25.0, 10.0, -10.0)
innen_temp = st.sidebar.slider("Ziel-Innentemperatur (°C)", 15.0, 25.0, 20.0)
delta_t = innen_temp - ausen_temp

st.sidebar.header("🏔️ Dämmung")
daemm_klassen = {
    "1️⃣ Schlecht (Blech, wenig)": {"dicke": 10, "lambda": 0.040},
    "2️⃣ Normal (Armaflex 19mm)": {"dicke": 19, "lambda": 0.035},
    "3️⃣ Gut (Doppeldämmung)": {"dicke": 30, "lambda": 0.034},
    "4️⃣ Sehr gut (Expedition)": {"dicke": 50, "lambda": 0.033}
}
daemm_wahl = st.sidebar.selectbox("Dämmklasse", list(daemm_klassen.keys()))
daemm_data = daemm_klassen[daemm_wahl]

# Berechnungen
volumen = laenge * breite * hoehe
surface = 2 * laenge * hoehe + 2 * breite * hoehe + laenge * breite * 1.2

u_wert = calculate_u_value(daemm_data["dicke"], daemm_data["lambda"])
leistung_kw = calculate_heating_power(surface, u_wert, delta_t)

# Hauptanzeige (3 Spalten)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Volumen", f"{volumen:.1f} m³")
    st.metric("Oberfläche", f"{surface:.1f} m²")

with col2:
    st.metric("ΔT", f"{delta_t} K")
    st.metric("U-Wert", f"{u_wert:.2f} W/m²K")

with col3:
    st.metric("**Benötigte Heizleistung**", f"{leistung_kw:.1f} kW", delta=None)

# Empfehlungen
st.subheader("💡 Heizungs-Empfehlung")
if leistung_kw < 2:
    st.success("✅ 2 kW Diesel/Gas reicht (z.B. Truma Combi 4)")
elif leistung_kw < 4:
    st.warning("⚠️ 4 kW empfohlen (z.B. Webasto Air Top)")
else:
    st.error("❌ 6+ kW nötig (Doppelheizung oder größer)")

st.info(f"""
**Dein Setup:** {laenge:.1f}m × {breite:.1f}m × {hoehe:.1f}m  
**Dämmung:** {daemm_wahl} (d={daemm_data['dicke']}mm, λ={daemm_data['lambda']})  
**Formel:** Q = A × U × ΔT / 1000
""")

# Chart: Leistung vs. Außentemperatur
st.subheader("📈 Leistung bei verschiedenen Außentemperaturen")
temps = list(range(-25, 11, 5))
leistungen = [calculate_heating_power(surface, u_wert, innen_temp - t) for t in temps]

st.bar_chart(dict(zip(temps, leistungen)))
