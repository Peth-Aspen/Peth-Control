import streamlit as st
import pandas as pd
import math
from datetime import datetime, timedelta

st.set_page_config(page_title="Peth-Control", page_icon="📊", layout="wide")

# Custom CSS for modern design inspired by Lemonade
st.markdown("""
<style>
    /* Bakgrund och typsnitt */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #fcfcfc;
    }

    /* Centrera och snygga till behållaren */
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }

    /* Styla knapparna - Lemonade-rosa/orange */
    .stButton>button {
        background-color: #ff6b35;
        color: white;
        border-radius: 12px;
        padding: 20px;
        font-size: 18px;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.3);
        background-color: #ff8254;
    }

    /* Input-fälten */
    .stNumberInput, .stSelectbox, .stSlider {
        background-color: white;
        border-radius: 15px;
        padding: 10px;
        border: 1px solid #eee;
    }

    /* Resultat-kortet */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #f0f0f0;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        text-align: center;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #ff6b35;
        height: 8px;
    }
</style>
""", unsafe_allow_html=True)

# App constants
HALVERINGSTID = 7.0
GRANSVARDE_HOG = 0.30
TOTAL_STEPS = 7

DRYCKER = {
    "Starköl 50cl (5.0%)": 1.4,
    "Starköl 33cl (5.0%)": 0.9,
    "Glas vin 15cl (12%)": 1.0,
    "Flaska vin 75cl (12%)": 5.0,
    "Sprit 4cl (40%)": 0.9,
    "Sprit 6cl (40%)": 1.35,
    "Lättöl/Folköl 33cl (2.8%)": 0.5
}

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'kon' not in st.session_state:
    st.session_state.kon = 'Man'
if 'alder' not in st.session_state:
    st.session_state.alder = 30
if 'vikt' not in st.session_state:
    st.session_state.vikt = 70
if 'langd' not in st.session_state:
    st.session_state.langd = 170
if 'start_varde' not in st.session_state:
    st.session_state.start_varde = 0.0
if 'logg' not in st.session_state:
    st.session_state.logg = []
if 'evaluated' not in st.session_state:
    st.session_state.evaluated = False

# Helpers
def reset_wizard():
    st.session_state.step = 0
    st.session_state.logg = []
    st.session_state.evaluated = False
    st.session_state.start_varde = 0.0

def compute_peth():
    total = st.session_state.start_varde
    for item in st.session_state.logg:
        dagar_sedan = (datetime.now().date() - item['datum']).days
        r = 0.68 if st.session_state.kon == 'Man' else 0.55
        peth_okning = (item['enheter'] * 0.22) / (st.session_state.vikt * r / 10)
        total += peth_okning * (0.5 ** (max(0, dagar_sedan) / HALVERINGSTID))
    return total

# Page layout
st.markdown("<div class='wizard-card'>", unsafe_allow_html=True)
col_left, col_center, col_right = st.columns([1, 8, 1])
with col_center:
    if st.session_state.step == 0:
        st.title("Welcome to Peth-Control")
        st.write("### Din personliga PEth-uppskattning i en enkel guide.")
        st.write(
            "Stega igenom din profil, ange dina dryckestillfällen och tryck på "
            "**Utvärdera** för att se din prognos."
        )
        st.write("---")
        if st.button("Start Evaluation", key="start_evaluation"):
            st.session_state.step = 1
            st.rerun()
    elif st.session_state.step == 1:
        st.header("Steg 1: Välj kön")
        st.radio("Kön:", ["Man", "Kvinna"], key='kon', horizontal=True)
        st.write("Ange ditt kön så att beräkningen kan använda rätt fördelningsvolym.")
        st.write("---")
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("Back", key="back_1"):
                st.session_state.step = 0
                st.rerun()
        with col_next:
            if st.button("Next", key="next_1"):
                st.session_state.step = 2
                st.rerun()
    elif st.session_state.step == 2:
        st.header("Steg 2: Ange ålder")
        st.slider("Ålder:", min_value=16, max_value=120, value=st.session_state.alder, key='alder')
        st.write("Ålder hjälper till att skapa en bättre profil för dig.")
        st.write("---")
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("Back", key="back_2"):
                st.session_state.step = 1
                st.rerun()
        with col_next:
            if st.button("Next", key="next_2"):
                st.session_state.step = 3
                st.rerun()
    elif st.session_state.step == 3:
        st.header("Steg 3: Ange vikt")
        st.number_input("Vikt (kg):", min_value=40, max_value=200, value=st.session_state.vikt, key='vikt')
        st.write("Vi använder vikten för att uppskatta hur alkoholen fördelas i kroppen.")
        st.write("---")
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("Back", key="back_3"):
                st.session_state.step = 2
                st.rerun()
        with col_next:
            if st.button("Next", key="next_3"):
                st.session_state.step = 4
                st.rerun()
    elif st.session_state.step == 4:
        st.header("Steg 4: Ange längd")
        st.number_input("Längd (cm):", min_value=120, max_value=230, value=st.session_state.langd, key='langd')
        st.write("Detta kompletterar din profil, även om längden inte används i grundberäkningen.")
        st.write("---")
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("Back", key="back_4"):
                st.session_state.step = 3
                st.rerun()
        with col_next:
            if st.button("Next", key="next_4"):
                st.session_state.step = 5
                st.rerun()
    elif st.session_state.step == 5:
        st.header("Steg 5: Lägg till dryckestillfällen")
        st.write("Fyll i datum, dryck och antal. Du kan lägga till flera poster innan du utvärderar.")
        col1, col2 = st.columns(2)
        with col1:
            log_datum = st.date_input("Datum:", value=datetime.now(), max_value=datetime.now())
            log_typ = st.selectbox("Dryckstyp:", list(DRYCKER.keys()))
        with col2:
            log_antal = st.number_input("Antal:", min_value=1, step=1)
            log_enheter = DRYCKER[log_typ] * log_antal
            st.caption(f"Motsvarar ca {log_enheter:.1f} standardenheter.")

        if st.button("➕ Lägg till till logg", key="add_log"):
            st.session_state.logg.append({
                'datum': log_datum,
                'enheter': log_enheter,
                'beskrivning': f"{log_antal} st {log_typ}"
            })
            st.success("Dryckestillfället har lagts till.")
        st.write("---")
        if st.session_state.logg:
            st.subheader("Dina tillagda poster")
            for idx, item in enumerate(st.session_state.logg, 1):
                st.write(f"{idx}. {item['datum']} – {item['beskrivning']}")
        else:
            st.info("Inga poster ännu. Lägg till en dryck innan du utvärderar.")

        st.write("---")
        col_back, col_eval = st.columns(2)
        with col_back:
            if st.button("Back", key="back_5"):
                st.session_state.step = 4
                st.rerun()
        with col_eval:
            if st.button("Evaluate", key="evaluate"):
                if st.session_state.logg:
                    st.session_state.step = 6
                    st.session_state.evaluated = True
                    st.rerun()
                else:
                    st.warning("Lägg till minst ett dryckestillfälle för att utvärdera.")
    elif st.session_state.step == 6:
        st.header("Steg 6: Resultat")
        if not st.session_state.evaluated:
            st.warning("Tryck Evaluate från föregående steg för att se resultat.")
        else:
            total_peth_idag = compute_peth()
            col_metric, col_status = st.columns(2)
            with col_metric:
                st.metric("Beräknat värde idag", f"{total_peth_idag:.3f}")
            with col_status:
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

            st.write("---")
            if st.button("Starta om", key="restart"):
                reset_wizard()
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

display_step = st.session_state.step + 1
progress = display_step / TOTAL_STEPS
progress_text = f"Steg {display_step} av {TOTAL_STEPS}"
st.write(progress_text)
st.progress(progress)
