import streamlit as st
from datetime import datetime
import pytz
import requests # UUSI: Mahdollistaa API-haut ulkomaailmaan

# --- KONFIGURAATIO ---
st.set_page_config(page_title="TH Agentti", page_icon="🚕", layout="centered", initial_sidebar_state="collapsed")
HELSINKI_TZ = pytz.timezone('Europe/Helsinki')

# --- TILANHALLINTA (KUSKIN INTERAKTIO) ---
if 'event_states' not in st.session_state:
    st.session_state.event_states = {
        "Messukeskus": "NORMAALI",
        "Jäähalli": "NORMAALI",
        "Ooppera": "NORMAALI"
    }

if 'selected_station' not in st.session_state:
    st.session_state.selected_station = "HELSINKI"

def update_status(event_name, new_status):
    st.session_state.event_states[event_name] = new_status

# --- DIGITRAFFIC API (LIVE-JUNAT) ---
@st.cache_data(ttl=60) # Koodi tallentaa datan minuutiksi muistiin, ettei API ylikuormitu joka painalluksella
def fetch_live_trains(station_name):
    """
    Hakee Fintrafficin avoimesta rajapinnasta saapuvat kaukojunat.
    """
    station_codes = {"HELSINKI": "HKI", "PASILA": "PSL", "TIKKURILA": "TKL"}
    code = station_codes.get(station_name, "HKI")
    
    # Haetaan 20 seuraavaa saapuvaa junaa
    url = f"https://rata.digitraffic.fi/api/v1/live-trains/station/{code}?arriving_trains=20&departing_trains=0&include_nonstopping=false"
    
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return [{"id": "Virhe", "route": "API alhaalla", "time": "--:--", "status": f"Koodi {res.status_code}"}]
            
        trains = res.json()
        results = []
        
        for t in trains:
            # Suodatetaan vain kaukoliikenne
            if t.get('trainCategory') == 'Long-distance':
                # Etsitään oikea rivi aseman kohdalta
                for row in t.get('timeTableRows', []):
                    if row.get('stationShortCode') == code and row.get('type') == 'ARRIVAL':
                        # Aikaleimat ovat muodossa 2026-03-10T15:30:00.000Z (UTC), muutetaan Helsinki-aikaan
                        scheduled_utc = datetime.fromisoformat(row['scheduledTime'].replace('Z', '+00:00'))
                        scheduled_hel = scheduled_utc.astimezone(HELSINKI_TZ)
                        
                        # Tutkitaan onko juna myöhässä (LiveEstimate)
                        live_estimate = row.get('liveEstimateTime')
                        if live_estimate:
                            est_utc = datetime.fromisoformat(live_estimate.replace('Z', '+00:00'))
                            est_hel = est_utc.astimezone(HELSINKI_TZ)
                            
                            # Jos myöhässä yli 2 min, näytetään punaisella
                            diff_minutes = (est_hel - scheduled_hel).total_seconds() / 60
                            if diff_minutes > 2:
                                status = f"<span style='color: #F87171;'>Myöhässä (Arvio {est_hel.strftime('%H:%M')})</span>"
                            else:
                                status = "Aikataulussa"
                        else:
                            status = "Aikataulussa"
                            
                        results.append({
                            "id": f"{t.get('trainType', '')} {t.get('trainNumber', '')}",
                            "route": "Saapuu",
                            "time": scheduled_hel.strftime('%H:%M'),
                            "status": status,
                            "sort_time": scheduled_hel
                        })
                        break # Siirrytään seuraavaan junaan
                        
        # Järjestetään aikataulun mukaan ja otetaan 4 seuraavaa
        results.sort(key=lambda x: x['sort_time'])
        return results[:4]
        
    except Exception as e:
        return [{"id": "Yhteysvirhe", "route": "Ei dataa", "time": "--:--", "status": "Fintraffic yhteys poikki"}]

# --- CSS INJEKTIO ---
st.markdown("""
<style>
    .stApp { background-color: #0F111A; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    #MainMenu, header, footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }

    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .time-display { font-size: 2.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; }
    .time-display span { color: #4ADE80; }
    .weather-widget { background: rgba(255,255,255,0.05); padding: 8px 12px; border-radius: 8px; text-align: right; }
    .weather-temp { font-size: 1.2rem; font-weight: 700; color: #FFFFFF; }
    .weather-desc { font-size: 0.7rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;}

    .th-card {
        background: #191B24; border: 1px solid #2D313E; border-radius: 12px;
        padding: 16px; margin-bottom: 12px; position: relative;
    }
    .th-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: #4ADE80; border-radius: 12px 0 0 12px; }
    .th-card.red-border::before { background: #F87171; }
    .th-card.yellow-border::before { background: #FBBF24; }

    .card-title { font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; z-index: 2; position: relative;}
    .card-subtitle { font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px; z-index: 2; position: relative;}
    .card-time { position: absolute; right: 16px; top: 16px; font-size: 1.8rem; font-weight: 800; color: #4ADE80; letter-spacing: -1px; z-index: 2;}
    .card-time.red-text { color: #F87171; }
    .card-time.yellow-text { color: #FBBF24; }
    
    .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-top: 8px; z-index: 2; position: relative;}
    .badge-premium { background: rgba(251, 191, 36, 0.15); color: #FBBF24; }
    .badge-fire { background: rgba(248, 113, 113, 0.15); color: #F87171; }
    .badge-info { background: rgba(148, 163, 184, 0.15); color: #94A3B8; }

    .live-dot { height: 8px; width: 8px; background-color: #4ADE80; border-radius: 50%; display: inline-block; margin-right: 4px; animation: pulse 2s infinite;}
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    
    .card-link { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; text-decoration: none; }
    .link-icon { position: absolute; right: 16px; bottom: 16px; color: #64748B; font-size: 1.2rem; z-index: 2;}

    .section-title { font-size: 0.85rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; margin: 24px 0 12px 0; letter-spacing: 1px; display: flex; align-items: center;}
</style>
""", unsafe_allow_html=True)

# --- 1. YLÄPALKKI & SÄÄ ---
now = datetime.now(HELSINKI_TZ)
time_str = now.strftime("%H") + "<span>:</span>" + now.strftime("%M")
weather_status = "SADE ALKAMASSA" 
demand_multiplier = "1.4x"

st.markdown(f"""
<div class="top-bar">
    <div class="time-display">{time_str}</div>
    <div class="weather-widget">
        <div class="weather-temp">🌦️ +5°</div>
        <div class="weather-desc">{weather_status} (Kysyntä {demand_multiplier})</div>
        <div class="weather-desc" style="font-size: 0.55rem; opacity: 0.7;">TUTKA AKTIVOITU</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<a href="https://ilmatieteenlaitos.fi/sade-ja-pilvialueet?area=etela-suomi" target="_blank" style="color: #4ADE80; font-size: 0.8rem; text-decoration: none; z-index: 3; position: relative;">Avaa Sadetutka ↗</a>', unsafe_allow_html=True)

# --- 2. LIVE-JUNAT (FINTRAFFIC API) ---
st.markdown('<div class="section-title">🚆 JUNAT (KAUKO)</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("HELSINKI", use_container_width=True, type="primary" if st.session_state.selected_station == "HELSINKI" else "secondary"):
        st.session_state.selected_station = "HELSINKI"
        st.rerun()
with col2:
    if st.button("PASILA", use_container_width=True, type="primary" if st.session_state.selected_station == "PASILA" else "secondary"):
        st.session_state.selected_station = "PASILA"
        st.rerun()
with col3:
    if st.button("TIKKURILA", use_container_width=True, type="primary" if st.session_state.selected_station == "TIKKURILA" else "secondary"):
        st.session_state.selected_station = "TIKKURILA"
        st.rerun()

station_urls = {
    "HELSINKI": "https://www.vr.fi/radalla?station=HKI&direction=ARRIVAL&stationFilters=%7B%22trainCategory%22%3A%22Long-distance%22%7D",
    "PASILA": "https://www.vr.fi/radalla?station=PSL&direction=ARRIVAL&stationFilters=%7B%22trainCategory%22%3A%22Long-distance%22%7D",
    "TIKKURILA": "https://www.vr.fi/radalla?station=TKL&direction=ARRIVAL&stationFilters=%7B%22trainCategory%22%3A%22Long-distance%22%7D"
}
active_url = station_urls[st.session_state.selected_station]

# Datahaku (Reaaliaikainen)
st.markdown(f"<p style='color: #94A3B8; font-size: 0.8rem;'>Haetaan livenä: <strong>{st.session_state.selected_station}</strong></p>", unsafe_allow_html=True)

live_trains = fetch_live_trains(st.session_state.selected_station)

if not live_trains:
    st.markdown("<p style='color:#94A3B8'>Ei saapuvaa kaukoliikennettä seuraavan 2 tunnin sisällä.</p>", unsafe_allow_html=True)
else:
    for train in live_trains:
        # Pieni visuaalinen hienosäätö myöhästymisille
        border_class = "red-border" if "Myöhässä" in train['status'] else ""
        time_class = "red-text" if "Myöhässä" in train['status'] else ""
        
        st.markdown(f"""
        <div class="th-card {border_class}">
            <a href="{active_url}" target="_blank" class="card-link"></a>
            <div class="card-title">{train['id']} {train['route']} <span class="live-dot" style="margin-left: 8px;"></span><span style="font-size: 0.6rem; color: #4ADE80;">LIVE</span></div>
            <div class="card-subtitle">{train['status']}</div>
            <div class="card-time {time_class}">{train['time']}</div>
            <div class="link-icon">↗</div>
        </div>
        """, unsafe_allow_html=True)


# --- 3. SATAMAT (MERILIIKENNE) ---
st.markdown('<div class="section-title">⛴️ SATAMAT (LAIVAT)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="th-card">
    <a href="https://averio.fi/laivat/" target="_blank" class="card-link"></a>
    <div class="card-title">MyStar <span class="live-dot" style="margin-left: 8px;"></span><span style="font-size: 0.6rem; color: #4ADE80;">LIVE</span></div>
    <div class="card-subtitle">Tulossa: ~2000 hlö<br>Tallink • Länsiterminaali T2</div>
    <div class="card-time">18:30</div>
    <div class="badge badge-info">LÄHDE: AVERIO.FI</div>
    <div class="link-icon">↗</div>
</div>
""", unsafe_allow_html=True)

# --- 4. TAPAHTUMAT TÄNÄÄN ---
st.markdown('<div class="section-title">🎫 TAPAHTUMAT TÄNÄÄN</div>', unsafe_allow_html=True)

events = [
    {
        "id": "Messukeskus",
        "title": "Kevätmessut",
        "location": "Messukeskus",
        "time": "17:00",
        "duration": "Ovet sulkeutuvat",
        "badge_class": "badge-info",
        "badge_text": "SUURI TAPAHTUMA",
        "border_class": "",
        "time_class": "",
        "url": "https://messukeskus.com/kavijalle/tapahtumat/tapahtumakalenteri"
    },
    {
        "id": "Jäähalli",
        "title": "Jääkiekko: HIFK - Kärpät",
        "location": "Helsingin Jäähalli",
        "time": "18:30",
        "duration": "150 min",
        "badge_class": "badge-fire",
        "badge_text": "KORKEA KYSYNTÄ 🔥",
        "border_class": "red-border",
        "time_class": "red-text",
        "url": "https://liiga.fi/fi/ohjelma?kausi=2025-2026&sarja=runkosarja&joukkue=hifk&kotiVieras=koti"
    },
    {
        "id": "Ooppera",
        "title": "Oopperaesitys (Tosca)",
        "location": "Kansallisooppera",
        "time": "19:00",
        "duration": "180 min",
        "badge_class": "badge-premium",
        "badge_text": "PREMIUM (PUKU PÄÄLLÄ)",
        "border_class": "yellow-border",
        "time_class": "yellow-text",
        "url": "https://oopperabaletti.fi/kalenteri/"
    }
]

for ev in events:
    current_state = st.session_state.event_states[ev["id"]]
    
    state_display = ""
    if current_state == "JONO!":
        state_display = '<span style="color: #F87171; font-weight: bold; margin-left: 10px;">[🚕 JONOA]</span>'
    elif current_state == "OHI":
        state_display = '<span style="color: #64748B; font-weight: bold; margin-left: 10px;">[✓ PURETTU]</span>'
        
    st.markdown(f"""
    <div class="th-card {ev['border_class']}">
        <a href="{ev['url']}" target="_blank" class="card-link" style="height: 60%;"></a>
        <div class="card-subtitle" style="text-transform: uppercase;">AJOITUS: PURKU</div>
        <div class="card-title">{ev['title']} {state_display}</div>
        <div class="card-subtitle">{ev['location']}<br>Loppuu: {ev['time']} ({ev['duration']})</div>
        <div class="card-time {ev['time_class']}">{ev['time']}</div>
        <div class="badge {ev['badge_class']}">{ev['badge_text']}</div>
        <div class="link-icon" style="top: 16px; bottom: auto;">↗</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✓ OHI", key=f"btn_ohi_{ev['id']}", use_container_width=True, type="secondary" if current_state != "OHI" else "primary"):
            update_status(ev["id"], "OHI")
            st.rerun()
    with c2:
        if st.button("➖ NORMAALI", key=f"btn_norm_{ev['id']}", use_container_width=True, type="secondary" if current_state != "NORMAALI" else "primary"):
            update_status(ev["id"], "NORMAALI")
            st.rerun()
    with c3:
        if st.button("⚠️ JONO!", key=f"btn_jono_{ev['id']}", use_container_width=True, type="secondary" if current_state != "JONO!" else "primary"):
            update_status(ev["id"], "JONO!")
            st.rerun()
            
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

st.divider()
