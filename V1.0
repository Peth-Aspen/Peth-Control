import streamlit as st

st.set_page_config(page_title="Peth-Control", page_icon="📊")

st.title("📊 Peth-Control")
st.subheader("Beräkna din PEth-prognos")

# Skapar listan 1-200 direkt i koden istället för Excel
vikt_lista = list(range(1, 201))

# --- INPUT ---
vikt = st.selectbox("Välj din vikt (kg):", vikt_lista, index=79) # 80kg förvalt
start_peth = st.number_input("Ditt senaste PEth-värde (t.ex. 0.45):", min_value=0.0, step=0.01)
dagar = st.slider("Antal dagar utan alkohol:", 0, 60, 7)

# --- LOGIK ---
# Vi använder en säkerhetsmarginal (7 dagars halveringstid)
halveringstid = 7.0 
nuvarande = start_peth * (0.5 ** (dagar / halveringstid))

# --- RESULTAT ---
st.divider()
st.metric(label="Uppskattat värde nu", value=f"{nuvarande:.3f}")

if nuvarande < 0.05:
    st.success("Sannolikt under gränsvärdet (0.05)")
elif nuvarande < 0.30:
    st.warning("Indikerar måttlig konsumtion (0.05 - 0.30)")
else:
    st.error("Indikerar hög konsumtion (över 0.30)")

st.caption("---")
st.caption("VARNING: Detta är en matematisk modell, inte ett medicinskt facit. Resultatet är en uppskattning.")
