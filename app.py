import streamlit as st
from datetime import datetime, timedelta
import pytz

# --- KONFIGURAATIO JA TYYLIT ---
st.set_page_config(page_title="TH Agentti", page_icon="🚕", layout="centered")
HELSINKI_TZ = pytz.timezone('Europe/Helsinki')

# --- CSS-TYYLIT (LOVABLE UI IMITAATIO) ---
# Tämä blokki pakottaa Streamlitin näyttämään "Lovable"-sovellukselta.
st.markdown("""
    <style>
    /* Pakotetaan tumma tausta ja vaalea teksti */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Pääotsikoiden tyyli */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* KORTTIEN TYYLI - Tämä tekee pyöristetyt laatikot */
    .lovable-card {
        background-color: #262730; /* Hieman vaaleampi tummanharmaa */
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #3F3F46; /* Hienovarainen reunus */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Kortin sisäiset otsikot (esim. lennon numero tai tapahtuma) */
    .card-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 8px;
        color: #FFFFFF;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Tietokenttien otsikot (esim. "Lähtömaa:") */
    .data-label {
        font-size: 0.85rem;
        color: #A1A1AA;
        margin-right: 6px;
        font-weight: 500;
    }

    /* Itse tietoarvot */
    .data-value {
        font-size: 0.95rem;
        color: #FAFAFA;
        font-weight: 500;
    }
    
    /* Tietorivi */
    .data-row {
        margin-bottom: 4px;
    }

    /* Statusvärit */
    .status-green { color: #4CAF50; font-weight: 700; }
    .status-yellow { color: #FFC107; font-weight: 700; }
    .status-red { color: #EF4444; font-weight: 700; }
    .status-grey { color: #A1A1AA; font-weight: 700; }

    /* Piilotetaan Streamlitin oletusvalikko ja footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SALAUS JA KULUNVALVONTA ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
        
    if st.session_state["password_correct"]:
        return True

    # Yksinkertainen kirjautumiskortti
    st.markdown('<div class="lovable-card"><div class="card-header">Kirjaudu sisään</div>', unsafe_allow_html=True)
    password = st.text_input("Syötä valtuutuskoodi", type="password", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if password == "152": 
        st.session_state["password_correct"] = True
        st.rerun()
    elif password:
        st.error("Pääsy evätty.")
    return False

if not check_password():
    st.stop()

# --- ÄLYKÄS LOGIIKKA JA UI-KOMPONENTIT ---

def calculate_event_status(start_time_str, duration_minutes):
    """Laskee tapahtuman tilan ja edistymisen (0.0 - 1.0)"""
    try:
        now = datetime.now(HELSINKI_TZ)
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        start = datetime.combine(now.date(), start_time)
        start = HELSINKI_TZ.localize(start)
        
        end_time = start + timedelta(minutes=duration_minutes)
        alert_time = end_time - timedelta(minutes=90)
        
        # Lasketaan edistyminen
        total_duration = (end_time - start).total_seconds()
        elapsed = (now - start).total_seconds()
        progress = max(0.0, min(1.0, elapsed / total_duration)) if total_duration > 0 else 0

        status_text = ""
        status_class = ""

        if now < start:
            status_text = "Ei alkanut"
            status_class = "status-grey"
        elif now >= alert_time and now < end_time:
             status_text = "🚨 PURKU ALKAMASSA (<1.5h)"
             status_class = "status-red"
        elif now >= start and now < alert_time:
            status_text = "Käynnissä (Odottaa)"
            status_class = "status-green"
        else:
            status_text = "Päättynyt"
            status_class = "status-grey"
            
        return end_time.strftime("%H:%M"), status_text, status_class, progress
    except Exception:
        return "--:--", "Virhe datassa", "status-grey", 0.0

def draw_flight_card(flight):
    """Piirtää yhden lentokortin Lovable-tyylillä"""
    # Määritellään statusväri (simulaatio)
    status_class = "status-green" if flight['Status'] == "Ajallaan" else "status-yellow"
    
    html = f"""
    <div class="lovable-card">
        <div class="card-header">
            <span>✈️ {flight['Code']}</span>
            <span class="{status_class}">{flight['Status']}</span>
        </div>
        <div class="data-row">
            <span class="data-label">Lähtömaa:</span>
            <span class="data-value">{flight['From']}</span>
        </div>
        <div class="data-row">
            <span class="data-label">Saapumisaika:</span>
            <span class="data-value">{flight['Time']}</span>
        </div>
        <div class="data-row">
            <span class="data-label">Matkustajat (arvio):</span>
            <span class="data-value">{flight['Pax']} pax</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def draw_event_card(event):
    """Piirtää yhden tapahtumakortin edistymispalkilla"""
    end_time, status_text, status_class, progress = calculate_event_status(event["Start"], event["Duration"])
    
    html = f"""
    <div class="lovable-card">
        <div class="card-header">
            <span>🎭 {event['Event']}</span>
        </div>
        <div class="data-row">
            <span class="data-label">Paikka:</span>
            <span class="data-value">{event.get('Location', 'Helsinki')}</span>
        </div>
        <div class="data-row">
            <span class="data-label">Aika:</span>
            <span class="data-value">{event['Start']} - {end_time} ({event['Duration']} min)</span>
        </div>
        <div class="data-row">
            <span class="data-label">Tila:</span>
            <span class="{status_class}">{status_text}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    # Streamlitin natiivi progress bar toimii paremmin kuin HTML-versio tässä
    st.progress(progress)

# --- PÄÄKÄYTTÖLIITTYMÄ (MAIN UI) ---

# Yläpalkin aika ja status
current_time = datetime.now(HELSINKI_TZ).strftime('%H:%M')
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2 style="margin: 0;">TH Agentti</h2>
        <div style="text-align: right;">
            <div style="font-size: 1.5rem; font-weight: 700;">{current_time}</div>
            <div style="color: #A1A1AA; font-size: 0.9rem;">Helsinki UTC+2/3</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# OSIDIO 1: LENNOT (SEURAAVA ASKEL: FINAVIA INTEGRAATIO)
st.subheader("✈️ Saapuvat Lennot (Finavia Data)")
# Tämä on nyt "dummy-dataa", joka näyttää miltä oikea Finavia-data näyttäisi tässä UI:ssa.
flights_data = [
    {"Code": "AY123", "From": "Bryssel (BRU)", "Time": "20:45", "Pax": 160, "Status": "Ajallaan"},
    {"Code": "LH850", "From": "Frankfurt (FRA)", "Time": "21:15", "Pax": 180, "Status": "Myöhässä (Est. 21:45)"},
    {"Code": "D8456", "From": "Oulu (OUL)", "Time": "22:00", "Pax": 150, "Status": "Ajallaan"}
]

for flight in flights_data:
    draw_flight_card(flight)

st.markdown("---") # Erotinviiva

# OSIO 2: TAPAHTUMAT
st.subheader("🎭 Tapahtumat & Purku")

# Testidata säädetty nykyhetkeen, jotta näet palkit toiminnassa
events_data = [
    {"Event": "Kansallisooppera: Tosca", "Location": "Ooppera, Töölö", "Start": "19:00", "Duration": 180},
    {"Event": "HKT: Moulin Rouge", "Location": "Kaupunginteatteri", "Start": "18:30", "Duration": 170}
]

for event in events_data:
    draw_event_card(event)

# Uloskirjautuminen
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Kirjaudu ulos"):
    st.session_state["password_correct"] = False
    st.rerun()
