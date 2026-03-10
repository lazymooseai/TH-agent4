import streamlit as st
from datetime import datetime
import pytz

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

def update_status(event_name, new_status):
    st.session_state.event_states[event_name] = new_status

# --- CSS INJEKTIO (LOVABLE UI PAKOTUS) ---
st.markdown("""
<style>
    /* Päätausta ja fontti */
    .stApp { background-color: #0F111A; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    #MainMenu, header, footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }

    /* Yläpalkki (Aika ja Sää) */
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .time-display { font-size: 2.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; }
    .time-display span { color: #4ADE80; }
    .weather-widget { background: rgba(255,255,255,0.05); padding: 8px 12px; border-radius: 8px; text-align: right; }
    .weather-temp { font-size: 1.2rem; font-weight: 700; color: #FFFFFF; }
    .weather-desc { font-size: 0.7rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;}

    /* Korttien perusrakenne */
    .th-card {
        background: #191B24;
        border: 1px solid #2D313E;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        position: relative;
    }
    .th-card::before {
        content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
        background: #4ADE80; border-radius: 12px 0 0 12px;
    }
    .th-card.red-border::before { background: #F87171; }
    .th-card.yellow-border::before { background: #FBBF24; }

    /* Korttien typografia */
    .card-title { font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; z-index: 2; position: relative;}
    .card-subtitle { font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px; z-index: 2; position: relative;}
    .card-time { position: absolute; right: 16px; top: 16px; font-size: 1.8rem; font-weight: 800; color: #4ADE80; letter-spacing: -1px; z-index: 2;}
    .card-time.red-text { color: #F87171; }
    .card-time.yellow-text { color: #FBBF24; }
    
    /* Tagit ja Badget */
    .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-top: 8px; z-index: 2; position: relative;}
    .badge-premium { background: rgba(251, 191, 36, 0.15); color: #FBBF24; }
    .badge-fire { background: rgba(248, 113, 113, 0.15); color: #F87171; }
    .badge-info { background: rgba(148, 163, 184, 0.15); color: #94A3B8; }

    /* Live-indikaattori */
    .live-dot { height: 8px; width: 8px; background-color: #4ADE80; border-radius: 50%; display: inline-block; margin-right: 4px; }
    
    /* Ulkoinen linkki (Nappula koko kortin päällä) */
    .card-link { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; text-decoration: none; }
    .link-icon { position: absolute; right: 16px; bottom: 16px; color: #64748B; font-size: 1.2rem; z-index: 2;}

    /* Alueen Otsikot */
    .section-title { font-size: 0.85rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; margin: 24px 0 12px 0; letter-spacing: 1px; }
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

# Tutkalinkki: Ilmatieteen laitos, tutka Etelä-Suomi
st.markdown('<a href="https://ilmatieteenlaitos.fi/sade-ja-pilvialueet?area=etela-suomi" target="_blank" style="color: #4ADE80; font-size: 0.8rem; text-decoration: none; z-index: 3; position: relative;">Avaa Sadetutka ↗</a>', unsafe_allow_html=True)

# --- 2. SATAMAT (MERILIIKENNE) ---
st.markdown('<div class="section-title">⛴️ Satamat (Laivat)</div>', unsafe_allow_html=True)

# Linkki Averio-laivakarttaan
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

# --- 3. TAPAHTUMAT TÄNÄÄN ---
st.markdown('<div class="section-title">🎫 Tapahtumat Tänään & Tilanne</div>', unsafe_allow_html=True)

# Tarkat linkit tapahtumiin
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
        "url": "https://liiga.fi/fi/ottelut"
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
    
    # Kuskin ohjauspainikkeet tilan päivittämiseen
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
