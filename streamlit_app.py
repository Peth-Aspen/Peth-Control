import streamlit as st
import pandas as pd
import math
from datetime import datetime, timedelta

st.set_page_config(page_title="Peth-Control", page_icon="📊")

st.title("📊 Peth-Control Pro")
st.subheader("Logga din konsumtion")

# --- INSTÄLLNINGAR ---
HALVERINGSTID = 7.0 
GRANSVARDE_HOG = 0.30  
GRANSVARDE_LAG = 0.05  

# Definiton av drycker och deras relativa alkoholmängd (standardenheter)
DRYCKER = {
    "Starköl 50cl (5.0%)": 1.4,
    "Starköl 33cl (5.0%)": 0.9,
    "Glas vin 15cl (12%)": 1.0,
    "Flaska vin 75cl (12%)": 5.0,
    "Sprit 4cl (40%)": 0.9,
    "Sprit 6cl (40%)": 1.35,
    "Lättöl/Folköl 33cl (2.8%)": 0.5
}

# --- INPUT: ANVÄNDARDATA ---
col_user1, col_user2 = st.columns(2)

with col_user1:
    vikt = st.selectbox("Din vikt (kg):", list(range(40, 201)), index=40)
    kon = st.radio("Kön:", ["Man", "Kvinna"])

with col_user2:
    start_varde = st.number_input("Senaste uppmätta PEth-värde:", min_value=0.0, value=0.0, step=0.05)

# --- INPUT: LOGGBOK ---
st.write("---")
st.write("### Registrera dryckestillfälle")

col_d1, col_d2 = st.columns(2)
with col_d1:
    valda_datum = st.date_input("Vilket datum?", value=datetime.now(), max_value=datetime.now())
    dryck_typ = st.selectbox("Vad drack du?", list(DRYCKER.keys()))

with col_d2:
    antal = st.number_input("Antal:", min_value=1, step=1)
    # Beräkna hur många "standard-enheter" detta blir
    valda_enheter = DRYCKER[dryck_typ] * antal
    st.caption(f"Motsvarar ca {valda_enheter:.1f} standardenheter.")

if 'logg' not in st.session_state:
    st.session_state.logg = []

if st.button("➕ Lägg till i loggen"):
    st.session_state.logg.append({
        'datum': valda_datum, 
        'enheter': valda_enheter,
        'beskrivning': f"{antal} st {dryck_typ}"
    })
    st.success("Tillagt!")

# --- BERÄKNING ---
total_peth_idag = start_varde 

if st.session_state.logg:
    st.write("### Din historik")
    for item in st.session_state.logg:
        dagar_sedan = (datetime.now().date() - item['datum']).days
        r = 0.68 if kon == "Man" else 0.55
        # Formel för PEth-påslag per enhet (justerad för vikt och kön)
        peth_okning = (item['enheter'] * 0.22) / (vikt * r / 10) 
        total_peth_idag += peth_okning * (0.5 ** (max(0, dagar_sedan) / HALVERINGSTID))
        st.write(f"- {item['datum']}: {item['beskrivning']}")

# --- RESULTAT OCH MÅL ---
st.divider()
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.metric(label="Beräknat värde idag", value=f"{total_peth_idag:.3f}")

with col_res2:
    if total_peth_idag < GRANSVARDE_HOG:
        st.success("✅ Under gränsen 0.30")
    else:
        st.error("🚨 Över gränsen 0.30")

# --- GRAF OCH PROGNOS ---
if total_peth_idag > 0:
    st.write("### Prognos för kommande 30 dagar")
    framtids_data = []
    for i in range(31):
        datum = datetime.now() + timedelta(days=i)
        varde = total_peth_idag * (0.5 ** (i / HALVERINGSTID))
        framtids_data.append({"Datum": datum, "PEth": varde, "Gräns (0.30)": 0.30})
    
    df = pd.DataFrame(framtids_data)
    st.line_chart(df.set_index("Datum"))
    
    if total_peth_idag > GRANSVARDE_HOG:
        dagar_till_mal = HALVERINGSTID * (math.log(GRANSVARDE_HOG / total_peth_idag) / math.log(0.5))
        datum_mal = datetime.now() + timedelta(days=dagar_till_mal)
        st.info(f"Beräknat datum under **0.30**: {datum_mal.date()}")

if st.button("🗑️ Rensa loggen"):
    st.session_state.logg = []
    st.rerun()
