import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Peth-Control", page_icon="📊")

st.title("📊 Peth-Control Pro")
st.subheader("Logga din konsumtion")

# --- INSTÄLLNINGAR ---
HALVERINGSTID = 7.0  # Dagar
MAX_DAGAR_BAKÅT = 45 # Allt äldre än 45 dagar anses försumbart

# --- INPUT: BASDATA ---
vikt = st.selectbox("Välj din vikt (kg):", list(range(1, 201)), index=79)

# --- INPUT: LOGGBOK ---
st.write("---")
st.write("### Registrera dryckestillfälle")

# Begränsa datumval till rimlig tid bakåt
min_date = datetime.now() - timedelta(days=MAX_DAGAR_BAKÅT)
valda_datum = st.date_input("Vilket datum drack du?", 
                            value=datetime.now(), 
                            min_value=min_date, 
                            max_value=datetime.now())

col1, col2 = st.columns(2)
with col1:
    antal_ol = st.number_input("Antal starköl (50cl 5%) eller motsvarande:", min_value=0, step=1)
with col2:
    timmar = st.number_input("Under hur många timmar?", min_value=1, step=1)

# Sessionslista för att spara flera tillfällen (temporärt i webbläsaren)
if 'logg' not in st.session_state:
    st.session_state.logg = []

if st.button("Lägg till i loggen"):
    st.session_state.logg.append({
        'datum': valda_datum,
        'enheter': antal_ol,
        'timmar': timmar
    })
    st.success(f"Loggat: {antal_ol} enheter den {valda_datum}")

# --- BERÄKNING ---
total_peth = 0.0

if st.session_state.logg:
    st.write("### Din logg")
    for item in st.session_state.logg:
        # Räkna ut dagar sedan detta tillfälle
        dagar_sedan = (datetime.now().date() - item['datum']).days
        
        # Förenklad modell: 1 starköl ökar PEth med ca 0.03-0.05 (individuellt!)
        # Vi använder en formel som påverkas något av vikt
        peth_okning = (item['enheter'] * 0.4) / (vikt / 10) 
        
        # Räkna ut restvärdet idag baserat på halveringstid
        restvarde = peth_okning * (0.5 ** (dagar_sedan / HALVERINGSTID))
        
        total_peth += restvarde
        st.write(f"- {item['datum']}: {item['enheter']} st öl ({restvarde:.3f} bidrag idag)")

# --- RESULTAT ---
st.divider()
st.metric(label="Ditt uppskattade totala PEth-värde idag", value=f"{total_peth:.3f}")

if total_peth < 0.05:
    st.success("Sannolikt under detektionsgränsen.")
elif total_peth < 0.30:
    st.warning("Indikerar måttlig konsumtion.")
else:
    st.error("Indikerar hög konsumtion.")

if st.button("Rensa loggen"):
    st.session_state.logg = []
    st.rerun()

st.caption("---")
st.caption("Modellen räknar med att en enhet ger ett initialt påslag som sedan avtar med 7 dagars halveringstid.")
