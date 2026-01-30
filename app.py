import streamlit as st
import pandas as pd

# Konfig für modernes Design
st.set_page_config(
    page_title="VanWerkstatt",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für modernes Design
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
    }
    .stMetric > label {
        color: white !important;
        font-size: 0.9rem;
    }
    .stMetric > div > div > div {
        color: white !important;
        font-size: 2rem;
        font-weight: 700;
    }
    .card-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# VanWerkstatt Header
st.markdown('<h1 class="main-header">VanWerkstatt</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Deine Camper-Technik. Perfekt gerechnet.</p>', unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2 = st.tabs(["Heizung", "Strom & Solar"])

# HEIZUNG (modernisiert)
with tab1:
    st.markdown('<div class="card-section"><h3>01 Heizleistung berechnen</h3></div>', unsafe_allow_html=True)
    
    # Eingaben in kompakter 3-Spalten-Layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Fahrzeugmaße**")
        laenge = st.slider("Länge innen (m)", 2.0, 7.0, 4.2, label_visibility="collapsed")
        breite = st.slider("Breite innen (m)", 1.5, 2.2, 1.8, label_visibility="collapsed")
        hoehe = st.slider("Höhe innen (m)", 1.6, 2.2, 1.8, label_visibility="collapsed")
    
    with col2:
        st.markdown("**Temperaturen**")
        ausen_temp = st.slider("Außentemperatur (°C)", -25.0, 10.0, -10.0, label_visibility="collapsed")
        innen_temp = st.slider("Ziel-Innentemperatur (°C)", 15.0, 25.0, 20.0, label_visibility="collapsed")
    
    with col3:
        st.markdown("**Dämmung**")
        daemm_klassen = {
            "Schlecht (Blech)": {"dicke": 10.0, "lambda": 0.040},
            "Normal (Armaflex)": {"dicke": 19.0, "lambda": 0.035},
            "Gut (Doppeldämmung)": {"dicke": 30.0, "lambda": 0.034},
            "Sehr gut": {"dicke": 50.0, "lambda": 0.033}
        }
        daemm_wahl = st.selectbox("Dämmklasse", list(daemm_klassen.keys()), label_visibility="collapsed")
        daemm_data = daemm_klassen[daemm_wahl]
    
    # Ergebnisse als moderne Metric Cards
    volumen = laenge * breite * hoehe
    surface = 2 * laenge * hoehe + 2 * breite * hoehe + laenge * breite * 1.2
    u_wert = lambda_value / (thickness_mm / 1000)
    leistung_kw = (surface * u_wert * (innen_temp - ausen_temp)) / 1000
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1: st.markdown(f'<div class="metric-card"><strong>{volumen:.1f} m³</strong><br><small>Volumen</small></div>', unsafe_allow_html=True)
    with col_m2: st.markdown(f'<div class="metric-card"><strong>{u_wert:.2f} W/m²K</strong><br><small>U-Wert</small></div>', unsafe_allow_html=True)
    with col_m3: st.markdown(f'<div class="metric-card"><strong>{leistung_kw:.1f} kW</strong><br><small>Heizleistung</small></div>', unsafe_allow_html=True)
    
    # Empfehlung
    col_rec1, col_rec2 = st.columns(2)
    if leistung_kw < 2:
        with col_rec1: st.success("2 kW Heizung reicht ✓")
    elif leistung_kw < 4:
        with col
