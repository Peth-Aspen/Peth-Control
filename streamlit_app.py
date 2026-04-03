import streamlit as st
import pandas as pd
import math
from datetime import datetime, timedelta

st.set_page_config(page_title="Peth-Control", page_icon="📊", layout="wide")

# Custom CSS for modern design inspired by Lemonade
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        color: #333;
    }
    .stButton>button {
        background-color: #ff6b35;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #e55a2b;
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stSuccess, .stError, .stInfo {
        border-radius: 10px;
        padding: 10px;
    }
    h1, h2, h3 {
        color: #ff6b35;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

st.title("Welcome to Peth-Control")
st.write(
    "Fyll i dina uppgifter först, ange sedan vad du drack och när. "
    "När allt är ifyllt trycker du på **Utvärdera** för att se din prognos."
)

# --- INSTÄLLNINGAR ---
HALVERINGSTID = 7.0
GRANSVARDE_HOG = 0.30
GRANSVARDE_LAG = 0.05

# Definition av drycker och deras relativa alkoholmängd (standardenheter)
DRYCKER = {
    "Starköl 50cl (5.0%)": 1.4,
    "Starköl 33cl (5.0%)": 0.9,
    "Glas vin 15cl (12%)": 1.0,
    "Flaska vin 75cl (12%)": 5.0,
    "Sprit 4cl (40%)": 0.9,
    "Sprit 6cl (40%)": 1.35,
    "Lättöl/Folköl 33cl (2.8%)": 0.5
}

# --- SIDEBAR: ANVÄNDARDATA ---
st.sidebar.header("⚙️ Din profil")
kon = st.sidebar.selectbox("Kön:", ["Man", "Kvinna"])
alder = st.sidebar.number_input("Ålder:", min_value=16, max_value=120, value=30, step=1)
vikt = st.sidebar.number_input("Vikt (kg):", min_value=40, max_value=200, value=70, step=1)
langd = st.sidebar.number_input("Längd (cm):", min_value=120, max_value=230, value=170, step=1)
start_varde = st.sidebar.number_input("Senaste uppmätta PEth-värde:", min_value=0.0, value=0.0, step=0.05)

st.sidebar.write("\nAnge alltid profilinformation innan du utvärderar din prognos.")

# --- SESSIONSTATE ---
if 'logg' not in st.session_state:
    st.session_state.logg = []
if 'evaluated' not in st.session_state:
    st.session_state.evaluated = False

# --- MAIN: LOGGBOK ---
st.write("---")
st.header("1. Registrera dina dryckestillfällen")
with st.form("drink_form"):
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        valda_datum = st.date_input("Vilket datum?", value=datetime.now(), max_value=datetime.now())
        dryck_typ = st.selectbox("Vad drack du?", list(DRYCKER.keys()))
    with col_d2:
        antal = st.number_input("Antal:", min_value=1, step=1)
        valda_enheter = DRYCKER[dryck_typ] * antal
        st.caption(f"Motsvarar ca {valda_enheter:.1f} standardenheter.")

    if st.form_submit_button("➕ Lägg till i loggen"):
        st.session_state.logg.append({
            'datum': valda_datum,
            'enheter': valda_enheter,
            'beskrivning': f"{antal} st {dryck_typ}"
        })
        st.success("Tillagt till logg!")
        st.session_state.evaluated = False

# --- HISTORIK ---
st.write("---")
st.header("2. Din historik")
if st.session_state.logg:
    for item in st.session_state.logg:
        st.write(f"- {item['datum']}: {item['beskrivning']}")
else:
    st.info("Lägg till minst ett dryckestillfälle innan du utvärderar.")

# --- EVALUATE BUTTON ---
st.write("---")
if st.button("▶️ Utvärdera"):
    if st.session_state.logg:
        st.session_state.evaluated = True
    else:
        st.warning("Ingen logg att utvärdera. Lägg till minst ett dryckestillfälle.")

# --- BERÄKNING OCH RESULTAT ---
if st.session_state.evaluated:
    total_peth_idag = start_varde
    for item in st.session_state.logg:
        dagar_sedan = (datetime.now().date() - item['datum']).days
        r = 0.68 if kon == "Man" else 0.55
        peth_okning = (item['enheter'] * 0.22) / (vikt * r / 10)
        total_peth_idag += peth_okning * (0.5 ** (max(0, dagar_sedan) / HALVERINGSTID))

    st.write("---")
    st.header("3. Resultat")
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric(label="Beräknat värde idag", value=f"{total_peth_idag:.3f}")
    with col_res2:
        if total_peth_idag < GRANSVARDE_HOG:
            st.success("✅ Under gränsen 0.30")
        else:
            st.error("🚨 Över gränsen 0.30")

    st.write("---")
    st.subheader("Prognos för kommande 30 dagar")
    framtids_data = []
    for i in range(31):
        datum = datetime.now() + timedelta(days=i)
        varde = total_peth_idag * (0.5 ** (i / HALVERINGSTID))
        framtids_data.append({"Datum": datum, "PEth": varde})
    df = pd.DataFrame(framtids_data)
    st.line_chart(df.set_index("Datum"))

    if total_peth_idag > GRANSVARDE_HOG:
        dagar_till_mal = HALVERINGSTID * (math.log(GRANSVARDE_HOG / total_peth_idag) / math.log(0.5))
        datum_mal = datetime.now() + timedelta(days=dagar_till_mal)
        st.info(f"Beräknat datum under **0.30**: {datum_mal.date()}")

# --- RENSNING OCH SPARA ---
st.write("---")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("🗑️ Rensa loggen"):
        st.session_state.logg = []
        st.session_state.evaluated = False
        st.rerun()
with col_b:
    if st.button("💾 Spara logg som CSV"):
        if st.session_state.logg:
            df_logg = pd.DataFrame(st.session_state.logg)
            csv = df_logg.to_csv(index=False)
            st.download_button(
                label="📥 Ladda ner CSV",
                data=csv,
                file_name="peth_logg.csv",
                mime="text/csv"
            )
            st.success("Logg sparad! Klicka på knappen ovan för att ladda ner.")
        else:
            st.warning("Ingen logg att spara.")
