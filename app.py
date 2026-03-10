import streamlit as st
from datetime import datetime, timedelta
import pytz

# --- KONFIGURAATIO ---
st.set_page_config(page_title="TH Agentti", page_icon="🚕", layout="mobile")
HELSINKI_TZ = pytz.timezone('Europe/Helsinki')

# --- SALAUS JA KULUNVALVONTA ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
        
    if st.session_state["password_correct"]:
        return True

    st.warning("Pääsy rajoitettu. Syötä valtuutuskoodi.")
    password = st.text_input("Salasana / Auton numero", type="password")
    
    if password == "152": 
        st.session_state["password_correct"] = True
        st.rerun()
    elif password:
        st.error("Pääsy evätty.")
    return False

if not check_password():
    st.stop()

# --- ÄLYKÄS LOGIIKKA ---
def get_flight_priority(city):
    jackpot_cities = ["Frankfurt", "Lontoo", "Bryssel", "Oulu", "Rovaniemi", "Kittilä"]
    if city in jackpot_cities: return "🔥 JACKPOT"
    return "Normaali"

def calculate_event_alert(start_time_str, duration_minutes):
    try:
        now = datetime.now(HELSINKI_TZ)
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        start = datetime.combine(now.date(), start_time)
        start = HELSINKI_TZ.localize(start)
        
        end_time = start + timedelta(minutes=duration_minutes)
        alert_time = end_time - timedelta(minutes=90)
        
        if now >= alert_time and now < end_time:
            return end_time.strftime("%H:%M"), "🚨 AJA PAIKALLE (Purkuun < 1.5h)", "red"
        elif now > end_time:
            return end_time.strftime("%H:%M"), "Päättynyt", "grey"
        else:
            return end_time.strftime("%H:%M"), f"Odottaa (Hälytys klo {alert_time.strftime('%H:%M')})", "green"
    except Exception:
        return "--:--", "Data lukuongelma.", "grey"

# --- KÄYTTÖLIITTYMÄ ---
st.title("🚕 TH Agentti")
st.caption(f"Status: Lokaali Testiajo | Aika: {datetime.now(HELSINKI_TZ).strftime('%H:%M')}")

st.subheader("🎭 Tapahtumat & Purku")

# Testidata säädetty vastaamaan nykyhetkeä (klo ~13:00) 
# jotta näet kaikki kolme tilaa aktiivisena.
events = [
    {"Event": "Kansallisooppera (Tuleva)", "Start": "14:00", "Duration": 180},
    {"Event": "HKT: Moulin Rouge (Aktiivinen purku)", "Start": "11:30", "Duration": 170},
    {"Event": "Aamukonsertti (Päättynyt)", "Start": "09:00", "Duration": 120}
]

for event in events:
    end_time, status, color = calculate_event_alert(event["Start"], event["Duration"])
    with st.expander(f"{event['Event']} (Loppuu {end_time})", expanded=True):
        if color == "red":
            st.markdown(f":rotating_light: **{status}**")
        else:
            st.markdown(f"**Status:** {status}")

st.subheader("✈️ Saapuvat (TH Prioriteetti)")
flights = [{"Code": "AY123", "From": "Bryssel", "Time": "14:45", "Pax": 160}]
for flight in flights:
    prio = get_flight_priority(flight["From"])
    if prio != "Normaali":
        st.markdown(f"**{flight['Time']} {flight['From']}** ({flight['Code']})")
        st.caption(f"{prio} | {flight['Pax']} matkustajaa")

st.divider()
if st.button("Lopeta vuoro (Kirjaudu ulos)"):
    st.session_state["password_correct"] = False
    st.rerun()
