import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Peth-Control", page_icon="📊")

st.title("📊 Peth-Control Pro")
st.subheader("Din personliga PEth-analys")

# --- INSTÄLLNINGAR ---
HALVERINGSTID = 7.0 
MAX_DAGAR_BAKÅT = 45 

# --- INPUT: ANVÄNDARDATA ---
col_user1, col_user2 = st.columns(2)

with col_user1:
    vikt = st.selectbox("Din vikt (kg):", list(range(40, 201)), index=40) # Startar på 80kg
    kon = st.radio("Kön:", ["Man", "Kvinna"])

with col_user2:
    start_varde = st.number_input("Har du ett nyligen uppmätt PEth-värde?", min_value=0.0, value=0.0, step=0.05, help="Om du vet ditt värde från ett test, skriv in det här.")

# --- INPUT: LOGGBOK ---
st.write("---")
st.write("### Registrera dryckestillfälle")

min_date = datetime.now() - timedelta(days=MAX_DAGAR_BAKÅT)
valda_datum = st.date_input("Vilket datum drack du?", 
                            value=datetime.now(), 
                            min_value=min_date, 
                            max_value=datetime.now())

col1, col2 = st.columns(2)
with col1:
    antal_ol = st.number_input("Antal starköl (50cl 5%) eller motsvarande:", min_value=0, step=1)
with col2:
    # Vi kan använda timmar för framtida mer avancerade förbränningskalkyler
    timmar = st.number_input("Under hur många timmar?", min_value=1, step=1)

if 'logg' not in st.session_state:
    st.session_state.logg = []

if st.button("➕ Lägg till i loggen"):
    if antal_ol > 0:
        st.session_state.logg.append({'datum': valda_datum, 'enheter': antal_ol})
        st.success(f"Loggat!")
    else:
        st.warning("Vänligen ange antal enheter.")

# --- BERÄKNINGSLOGIK ---
total_peth_idag = 0.0

# 1. Lägg till det manuella startvärdet (justerat för tiden som gått)
if start_varde > 0:
    total_peth_idag += start_varde # Här antar vi att värdet är från "idag", men vi kan utveckla detta

# 2. Räkna ut bidrag från loggen
if st.session_state.logg:
    st.write("### Din historik")
    for item in st.session_state.logg:
        dagar_sedan = (datetime.now().date() - item['datum']).days
        
        # Widmark-faktor justering (Kön)
        r = 0.68 if kon == "Man" else 0.55
        
        # Formel som tar hänsyn till vikt och kön för PEth-påslag
        # Baserat på att 1 standardenhet höjer PEth med ca 0.03-0.04 i snitt
        peth_okning = (item['enheter'] * 0.25) / (vikt * r / 10) 
        
        restvarde = peth_okning * (0.5 ** (dagar_sedan / HALVERINGSTID))
        total_peth_idag += restvarde
        st.write(f"- {item['datum']}: {item['enheter']} st enheter")

# --- RESULTAT ---
st.divider()
st.metric(label="Uppskattat totalt PEth-värde idag", value=f"{total_peth_idag:.3f}")

if total_peth_idag < 0.05:
    st.success("✅ Sannolikt under gränsvärdet (0.05)")
elif total_peth_idag < 0.30:
    st.warning("⚠️ Indikerar måttlig konsumtion")
else:
    st.error("🚨 Indikerar hög konsumtion")

# --- GRAF: FRAMTIDSPROGNOS ---
if total_peth_idag > 0:
    st.write("### Vägen till 0.05")
    framtids_data = []
    for i in range(31):
        datum = datetime.now() + timedelta(days=i)
        varde = total_peth_idag * (0.5 ** (i / HALVERINGSTID))
        framtids_data.append({"Datum": datum, "PEth": varde})
    
    df = pd.DataFrame(framtids_data)
    st.line_chart(df.set_index("Datum"))
    
    # Beräkna när man når 0.05
    import math
    if total_peth_idag > 0.05:
        dagar_till_grans = HALVERINGSTID * (math.log(0.05 / total_peth_idag) / math.log(0.5))
        datum_grans = datetime.now() + timedelta(days=dagar_till_grans)
        st.info(f"Beräknat datum under 0.05: **{datum_grans.date()}** (om ca {int(dagar_till_grans)} dagar)")

if st.button("🗑️ Rensa loggen"):
    st.session_state.logg = []
    st.rerun()

st.caption("---")
st.caption("Modellen baseras på genomsnittlig fördelningsvolym (Widmark) och 7 dagars halveringstid. Individuella variationer förekommer.")
