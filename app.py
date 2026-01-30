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
