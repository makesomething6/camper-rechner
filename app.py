import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(
    page_title="VanWerkstatt",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modernes CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .subheader {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0,0, 0.1);
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">VanWerkstatt</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Camper Technik Rechner</p>', unsafe_allow_html=True)

# Sidebar für alle Eingaben
with st.sidebar:
    st.markdown("### Einstellungen")
    
# Tabs
tab1, tab2 = st.tabs([" Heizung ", " Strom & Solar "])

# Funktionen (verkürzt - deine bestehenden)
@st.cache_data
def calculate_heating_power(surface_m2, u_value, delta_t):
    return (surface_m2 * u_value * delta_t) / 1000

@st.cache_data
def calculate_power_consumption(device_list):
    total_wh = sum(device["power"] * device["hours"] for device in device_list)
    total_ah = total_wh / 12
    return total_wh, total_ah

@st.cache_data
def calculate_solar_yield(panel_wp, sun_hours):
    return panel_wp * sun_hours * 0.8

# TAB 1: HEIZUNG
with tab1:
    st.markdown('<h3 class="section-header">Heizleistung berechnen</h3>', unsafe_allow_html=True)
    
    # Eingaben kompakt
    col1, col2, col3 = st.columns(3)
    with col1:
        laenge = st.slider("Länge (m)", 2.0, 7.0, 4.2)
        breite = st.slider("Breite (m)", 1.5, 2.2, 1.8)
        hoehe = st.slider("Höhe (m)", 1.6, 2.2, 1.8)
    
    with col2:
        ausen_temp = st.slider("Außentemperatur", -25.0, 10.0, -10.0)
        innen_temp = st.slider("Ziel-Innentemperatur", 15.0, 25.0, 20.0)
    
    with col3:
        daemm_wahl = st.selectbox("Dämmung", ["Schlecht", "Normal", "Gut", "Sehr gut"])
        daemm_werte = {"Schlecht": 0.040, "Normal": 0.035, "Gut": 0.034, "Sehr gut": 0.033}
        lambda_val = daemm_werte[daemm_wahl]
    
    # Berechnung
    volumen = laenge * breite * hoehe
    surface = 2 * (laenge * hoehe + breite * hoehe) + laenge * breite * 1.2
    u_wert = lambda_val / 0.019  # 19mm Standard
    leistung_kw = calculate_heating_power(surface, u_wert, innen_temp - ausen_temp)
    
    # Moderne Ergebnis-Karten
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f'''
        <div class="metric-container">
            <h4 style="margin: 0; color: #64748b;">Volumen</h4>
            <h2 style="margin: 0; color: #1e293b;">{volumen:.1f} m³</h2>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_m2:
        st.markdown(f'''
        <div class="metric-container">
            <h4 style="margin: 0; color: #64748b;">U-Wert</h4>
            <h2 style="margin: 0; color: #1e293b;">{u_wert:.2f} W/m²K</h2>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_m3:
        st.markdown(f'''
        <div class="metric-container">
            <h4 style="margin: 0; color: #64748b;">Heizleistung</h4>
            <h2 style="margin: 0; color: #3b82f6;">{leistung_kw:.1f} kW</h2>
        </div>
        ''', unsafe_allow_html=True)
    
    # Empfehlung
    if leistung_kw < 2:
        st.success("✅ 2 kW Heizung ausreichend")
    elif leistung_kw < 4:
        st.warning("⚠️ 4 kW Heizung empfohlen")
    else:
        st.error("❌ 6+ kW Heizung erforderlich")

# TAB 2: STROM (dein bestehender Code hier)
with tab2:
    st.markdown('<h3 class="section-header">Strom & Solar berechnen</h3>', unsafe_allow_html=True)
    
    # Dein bestehender Strom-Code hier einfügen...
    st.info("Stromrechner folgt (dein bestehender Code)")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem;'>
    <strong>VanWerkstatt</strong> | Camper Technik Rechner v2.0<br>
    Automatisches Speichern | Teile deinen Link
</div>
""", unsafe_allow_html=True)
