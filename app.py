import streamlit as st
import json
import os
from datetime import datetime

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Wolf Life Team-Management",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 15 OPTIMIERTE DESIGN-THEMES (FARBVARIANTEN) ---
THEMES = {
    "1. Wolf Life Dark (Rot-Dunkel Standard)": {
        "BG_MAIN": "#0D0D11", "BG_SIDEBAR": "#14141A", "BG_CARD": "#1C1C24", "BG_INPUT": "#22222D", "ACCENT": "#EF4444", "ACCENT_HOVER": "#DC2626", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#9CA3AF"
    },
    "2. Midnight Blue (Blau-Taktisch)": {
        "BG_MAIN": "#090D16", "BG_SIDEBAR": "#111827", "BG_CARD": "#1E293B", "BG_INPUT": "#2A3748", "ACCENT": "#3B82F6", "ACCENT_HOVER": "#2563EB", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#94A3B8"
    },
    "3. Blood Moon (Rot-Karmesin)": {
        "BG_MAIN": "#120808", "BG_SIDEBAR": "#1F0D0D", "BG_CARD": "#2C1515", "BG_INPUT": "#381B1B", "ACCENT": "#EF4444", "ACCENT_HOVER": "#DC2626", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#B89999"
    },
    "4. Cyberpunk Neon (Pink-Violett)": {
        "BG_MAIN": "#0A0814", "BG_SIDEBAR": "#131022", "BG_CARD": "#1F1A38", "BG_INPUT": "#29224A", "ACCENT": "#F43F5E", "ACCENT_HOVER": "#E11D48", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#A89EC9"
    },
    "5. Emerald Syndicate (Grün-Smaragd)": {
        "BG_MAIN": "#05100C", "BG_SIDEBAR": "#0A1C15", "BG_CARD": "#132E23", "BG_INPUT": "#1A3E31", "ACCENT": "#10B981", "ACCENT_HOVER": "#059669", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#9CA3AF"
    },
    "6. Matrix Terminal (Grün-Neon)": {
        "BG_MAIN": "#030A05", "BG_SIDEBAR": "#07170B", "BG_CARD": "#0F2914", "BG_INPUT": "#14361C", "ACCENT": "#22C55E", "ACCENT_HOVER": "#16A34A", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#9CA3AF"
    },
    "7. Golden Royalty (Gold-Gelb)": {
        "BG_MAIN": "#12100B", "BG_SIDEBAR": "#1C1912", "BG_CARD": "#2B261A", "BG_INPUT": "#363022", "ACCENT": "#EAB308", "ACCENT_HOVER": "#CA8A04", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#B3AB94"
    },
    "8. Purple Haze (Lila-Mystic)": {
        "BG_MAIN": "#0D0A14", "BG_SIDEBAR": "#161124", "BG_CARD": "#221A38", "BG_INPUT": "#2D2447", "ACCENT": "#A855F7", "ACCENT_HOVER": "#9333EA", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#B4ADC9"
    },
    "9. Steel Gray (Grau-Neutral)": {
        "BG_MAIN": "#0F0F10", "BG_SIDEBAR": "#18181B", "BG_CARD": "#27272A", "BG_INPUT": "#333338", "ACCENT": "#71717A", "ACCENT_HOVER": "#52525B", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#A1A1AA"
    },
    "10. Deep Ocean (Blau-Ozean)": {
        "BG_MAIN": "#060E17", "BG_SIDEBAR": "#0F1E2E", "BG_CARD": "#172F47", "BG_INPUT": "#203D5C", "ACCENT": "#0EA5E9", "ACCENT_HOVER": "#0284C7", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#93C5FD"
    },
    "11. Sunset Orange (Orange-Warm)": {
        "BG_MAIN": "#120B07", "BG_SIDEBAR": "#1F130B", "BG_CARD": "#301D11", "BG_INPUT": "#3D2719", "ACCENT": "#F97316", "ACCENT_HOVER": "#EA580C", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#D1B5A3"
    },
    "12. Coffee Dark (Braun-Kaffee)": {
        "BG_MAIN": "#110C0A", "BG_SIDEBAR": "#1C1411", "BG_CARD": "#2B1E1A", "BG_INPUT": "#362723", "ACCENT": "#D97706", "ACCENT_HOVER": "#B45309", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#C4B5A5"
    },
    "13. Arctic Frost (Türkis-Eis)": {
        "BG_MAIN": "#091217", "BG_SIDEBAR": "#0F1E26", "BG_CARD": "#172E3B", "BG_INPUT": "#1F3D4D", "ACCENT": "#06B6D4", "ACCENT_HOVER": "#0891B2", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#A5F3FC"
    },
    "14. Vampire Rose (Rosa-Beeren)": {
        "BG_MAIN": "#140A0F", "BG_SIDEBAR": "#210F17", "BG_CARD": "#331824", "BG_INPUT": "#40202E", "ACCENT": "#FB7185", "ACCENT_HOVER": "#F43F5E", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#E2B8C9"
    },
    "15. Hacker Acid (Limette-Giftgrün)": {
        "BG_MAIN": "#0E1009", "BG_SIDEBAR": "#171A0F", "BG_CARD": "#252B17", "BG_INPUT": "#30381F", "ACCENT": "#84CC16", "ACCENT_HOVER": "#65A30D", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#CBD5E1"
    }
}

DATA_FILE = "wolflife_team_data.json"

RANKS = [
    "Owner", "Projektleitung", "stellvertretende Projektleitung",
    "Teamleitung", "stellvertretende Teamleitung",
    "Administrator", "Test-Administrator",
    "Moderator 3", "Moderator 2", "Moderator 1", "Test-Moderator",
    "Supporter 3", "Supporter 2", "Supporter 1", "Test-Supporter"
]

RANK_COLORS = {
    "Owner": "#A855F7",                          # Lila
    "Projektleitung": "#FF69B4",                 # Pink
    "stellvertretende Projektleitung": "#FF69B4", # Pink
    "Teamleitung": "#FF7B00",                    # Neon-Orange
    "stellvertretende Teamleitung": "#FF7B00",    # Neon-Orange
    "Administrator": "#FF2A2A",                  # Signalrot
    "Test-Administrator": "#FF2A2A",             # Signalrot
    "Moderator 3": "#3B82F6",                    # Blau
    "Moderator 2": "#3B82F6",                    # Blau
    "Moderator 1": "#3B82F6",                    # Blau
    "Test-Moderator": "#3B82F6",                 # Blau
    "Supporter 3": "#EAB308",                    # Gelb
    "Supporter 2": "#EAB308",                    # Gelb
    "Supporter 1": "#EAB308",                    # Gelb
    "Test-Supporter": "#EAB308"                  # Gelb
}

def load_data():
    default_data = {
        "members": [], "applicants": [], "warnings": [],
        "absences": [], "tasks": [], "protocols": [],
        "notes": "", "users": [],
        "settings": {"theme": "1. Wolf Life Dark (Rot-Dunkel Standard)"}
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                for key in default_data:
                    if key not in loaded:
                        loaded[key] = default_data[key]
                return loaded
        except Exception:
            pass
    return default_data

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")

data = load_data()

current_theme_name = data.get("settings", {}).get("theme", "1. Wolf Life Dark (Rot-Dunkel Standard)")
if current_theme_name not in THEMES:
    current_theme_name = "1. Wolf Life Dark (Rot-Dunkel Standard)"
t = THEMES[current_theme_name]

# --- KOMPLETTES CSS (INKL. FIX FÜR DROP-DOWN & SELECTIONS) ---
st.markdown(f"""
<style>
    .stApp {{
        background-color: {t["BG_MAIN"]};
        color: {t["TEXT_MAIN"]};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {t["BG_SIDEBAR"]};
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        min-width: 280px !important;
    }}
    
    [data-testid="stSidebar"] .stRadio label {{
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 6px 0px !important;
        color: {t["TEXT_MAIN"]} !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
        gap: 8px;
    }}

    /* Allgemeine Texte weiß, AUSSER Elemente mit expliziten Rangfarben */
    h1, h2, h3, h4, h5, h6, p, span:not([style*="color"]), label, div {{
        color: {t["TEXT_MAIN"]} !important;
    }}
    
    /* Expander dauerhaft dunkel-grau */
    [data-testid="stExpander"],
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] details[open],
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details[open] > summary,
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] summary:focus,
    [data-testid="stExpander"] summary:active,
    [data-testid="stExpanderDetails"] {{
        background-color: {t["BG_CARD"]} !important;
        color: {t["TEXT_MAIN"]} !important;
    }}
    [data-testid="stExpander"] {{
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }}
    [data-testid="stExpander"] summary {{
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    }}
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {{
        color: {t["TEXT_MAIN"]} !important;
        fill: {t["TEXT_MAIN"]} !important;
        font-weight: 600 !important;
    }}

    .metric-card, .content-box {{
        background-color: {t["BG_CARD"]};
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 10px;
    }}
    .metric-title {{
        font-size: 13px;
        color: {t["TEXT_MUTED"]} !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: 700;
        color: {t["TEXT_MAIN"]} !important;
    }}

    [data-testid="stNotification"] {{
        background-color: {t["BG_CARD"]} !important;
        color: {t["TEXT_MAIN"]} !important;
        border: 1px solid {t["ACCENT"]} !important;
        border-radius: 10px;
    }}
    [data-testid="stNotification"] p {{
        color: {t["TEXT_MAIN"]} !important;
    }}

    /* INPUTS, SELECTBOXEN & DROPDOWNS (Komplett dunkel, kein weißer Bildschirm mehr) */
    input, textarea, select, 
    div[data-baseweb="input"], div[data-baseweb="select"], 
    div[data-baseweb="base-input"], span[data-baseweb="tag"],
    ul[data-baseweb="menu"], li[data-baseweb="option"],
    div[data-baseweb="popover"] {{
        background-color: {t["BG_INPUT"]} !important;
        color: {t["TEXT_MAIN"]} !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }}
    
    .stTextInput input, .stTextArea textarea, .stSelectbox select {{
        background-color: {t["BG_INPUT"]} !important;
        color: {t["TEXT_MAIN"]} !important;
    }}
    
    /* Dropdown Menü-Einträge beim Öffnen zwingend dunkel */
    li[role="option"] {{
        background-color: {t["BG_INPUT"]} !important;
        color: {t["TEXT_MAIN"]} !important;
    }}
    li[role="option"]:hover {{
        background-color: {t["ACCENT"]} !important;
        color: #FFFFFF !important;
    }}

    .stTextInput div[data-baseweb="input"] {{
        background-color: {t["BG_INPUT"]} !important;
        border-radius: 8px !important;
    }}
    
    .stTextInput button, [data-testid="stTextInput"] button,
    div[data-baseweb="input"] > div:last-child {{
        background-color: transparent !important;
        border: none !important;
    }}
    
    button[kind="header"] svg, [data-baseweb="icon"] svg, [data-testid="stTextInput"] button svg {{
        fill: {t["TEXT_MUTED"]} !important;
        color: {t["TEXT_MUTED"]} !important;
    }}

    .stButton>button, button[kind="secondaryFormSubmit"], button[kind="primary"] {{
        background-color: {t["ACCENT"]} !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
    }}
    .stButton>button:hover, button[kind="secondaryFormSubmit"]:hover, button[kind="primary"]:hover {{
        background-color: {t["ACCENT_HOVER"]} !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.is_superadmin = False
    st.session_state.permissions = {}

tabs_meta = [
    ("dashboard", "📊 Dashboard"),
    ("team", "👥 Team-Übersicht"),
    ("applicants", "📋 Bewerber"),
    ("warnings", "⚠️ Verwarnungen"),
    ("absences", "📅 Abmeldungen"),
    ("tasks", "✅ Aufgaben"),
    ("protocols", "📝 Protokolle"),
    ("notes", "📌 Notizen"),
    ("settings", "⚙️ Einstellungen"),
    ("accounts", "🔑 Benutzer & Rechte")
]

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("### 🐺 WOLF LIFE")

if st.session_state.logged_in:
    st.sidebar.markdown(f"<span style='color:{t['TEXT_MUTED']}; font-size:14px;'>Eingeloggt als:</span><br><strong style='font-size:16px;'>{st.session_state.username}</strong>", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    if st.sidebar.button("🔒 Abmelden", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("---")

    available_tabs = []
    tab_keys = []
    tab_modes = []

    for key, label in tabs_meta:
        mode = "full" if st.session_state.is_superadmin else st.session_state.permissions.get(key, "full")
        if key == "settings": mode = "full"
        if mode != "hidden":
            available_tabs.append(label)
            tab_keys.append(key)
            tab_modes.append(mode)

    selected_tab_label = st.sidebar.radio("Navigation", available_tabs)
    current_index = available_tabs.index(selected_tab_label)
    active_key = tab_keys[current_index]
    active_mode = tab_modes[current_index]

    is_readonly = (active_mode == "readonly")
    if is_readonly:
        st.sidebar.info("ℹ️ Modus: Nur-Lesen")
else:
    st.sidebar.markdown("<span style='color:#9CA3AF;'>Bitte zuerst anmelden.</span>", unsafe_allow_html=True)
    active_key = "login"

def check_write():
    if is_readonly and not st.session_state.is_superadmin:
        st.warning("Zugriff verweigert: Account hat nur Lese-Rechte in diesem Tab.")
        return False
    return True

def get_member_choices():
    members = data.get("members", [])
    if not members: return ["Kein Mitglied eingetragen"]
    return [f"{m['name']} ({m['rank']})" for m in members]

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(f"""
        <div style="background-color: {t['BG_CARD']}; padding: 40px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 10px 25px rgba(0,0,0,0.4);">
            <h2 style='text-align: center; margin-bottom: 0px;'>🐺 WOLF LIFE</h2>
            <p style='text-align: center; color: {t['ACCENT']}; font-weight: bold; font-size: 14px; margin-bottom: 25px;'>TEAM MANAGEMENT SUITE</p>
        """, unsafe_allow_html=True)
        
        username_input = st.text_input("Benutzername")
        password_input = st.text_input("Passwort", type="password")
        
        if st.button("Anmelden", use_container_width=True):
            if username_input == "Admin" and password_input == "wolf123":
                st.session_state.logged_in = True
                st.session_state.username = "Admin"
                st.session_state.is_superadmin = True
                st.session_state.permissions = {k: "full" for k in ["dashboard", "team", "applicants", "warnings", "absences", "tasks", "protocols", "notes", "accounts", "settings"]}
                st.rerun()
            else:
                user_found = next((u for u in data.get("users", []) if u["username"] == username_input and u["password"] == password_input), None)
                if user_found:
                    st.session_state.logged_in = True
                    st.session_state.username = user_found["username"]
                    st.session_state.is_superadmin = False
                    st.session_state.permissions = user_found.get("permissions", {})
                    st.rerun()
                else:
                    st.error("Falscher Benutzername oder falsches Passwort!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 1. DASHBOARD ---
if active_key == "dashboard":
    st.title("📊 Dashboard & Live-Statistiken")
    st.markdown(f"<span style='color:{t['TEXT_MUTED']};'>Übersicht über den aktuellen Status des Wolf Life Server-Teams.</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    total_members = len(data["members"])
    total_applicants = len([a for a in data["applicants"] if a.get("status") not in ["Angenommen", "Abgelehnt"]])
    active_warnings = len(data["warnings"])
    open_tasks = len([t for t in data["tasks"] if t.get("status") != "Erledigt"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Teammitglieder</div><div class='metric-value'>{total_members}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Offene Bewerbungen</div><div class='metric-value'>{total_applicants}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Aktive Verwarnungen</div><div class='metric-value'>{active_warnings}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Offene Aufgaben</div><div class='metric-value'>{open_tasks}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🛡️ Rang-Verteilung")
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        has_ranks = False
        for r in RANKS:
            count = len([m for m in data["members"] if m["rank"] == r])
            if count > 0:
                has_ranks = True
                color = RANK_COLORS.get(r, "#FFFFFF")
                st.markdown(f"- <span style='color:{color}; font-weight:bold;'>● {r}</span>: **{count}**", unsafe_allow_html=True)
        if not has_ranks:
            st.markdown(f"<span style='color:{t['TEXT_MUTED']};'>Noch keine Teammitglieder eingetragen.</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.subheader("📅 Aktuelle Abmeldungen")
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        if not data["absences"]:
            st.markdown(f"<span style='color:{t['TEXT_MUTED']};'>Keine aktuellen Abmeldungen vorhanden.</span>", unsafe_allow_html=True)
        else:
            for ab in data["absences"][-4:]:
                st.markdown(f"- **{ab['name']}** ({ab['from_date']} ➔ {ab['to_date']}): *{ab['reason']}*")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 2. TEAM-ÜBERSICHT ---
elif active_key == "team":
    st.title("👥 Team-Übersicht & Kader")
    with st.expander("➕ Neues Teammitglied hinzufügen"):
        with st.form("add_member_form"):
            r1, r2, r3, r4 = st.columns(4)
            m_name = r1.text_input("Discord Name / Tag")
            m_discord_id = r2.text_input("Discord-ID (Optional)")
            m_rank = r3.selectbox("Rang", RANKS)
            m_status = r4.selectbox("Status", ["Aktiv", "Probezeit", "Abgemeldet"])
            submit_m = st.form_submit_button("Mitglied hinzufügen", use_container_width=True)
            if submit_m and check_write():
                if m_name:
                    data["members"].append({"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "name": m_name, "discord_id": m_discord_id or "-", "rank": m_rank, "status": m_status, "joined": datetime.now().strftime("%d.%m.%Y")})
                    save_data(data)
                    st.rerun()

    st.markdown("---")
    search_query = st.text_input("🔍 Mitglied suchen...")
    filtered = [m for m in data["members"] if search_query.lower() in m["name"].lower()]
    for member in sorted(filtered, key=lambda m: RANKS.index(m["rank"]) if m["rank"] in RANKS else 99):
        rank_col = RANK_COLORS.get(member['rank'], '#FFFFFF')
        st.markdown(f"""
        <div class='content-box' style='display: flex; justify-content: space-between; align-items: center;'>
            <div><strong>{member['name']}</strong><br><span style='color:{t['TEXT_MUTED']}; font-size:12px;'>ID: {member['discord_id']} | Status: {member['status']}</span></div>
            <div>Rang: <span style='color:{rank_col}; font-weight:bold;'>{member['rank']}</span></div>
        </div>
        """, unsafe_allow_html=True)

# --- 3. BEWERBER ---
elif active_key == "applicants":
    st.title("📋 Bewerber & Testphase")
    with st.expander("➕ Neue Bewerbung erfassen"):
        with st.form("add_app_form"):
            c1, c2, c3 = st.columns(3)
            app_name = c1.text_input("Discord Name / Tag")
            app_role = c2.selectbox("Rolle", ["Supporter (Bewerbung)", "Moderator (Bewerbung)", "Administrator (Bewerbung)"])
            app_status = c3.selectbox("Status", ["Bewerbung eingegangen", "Im Testgespräch", "Testphase läuft", "Angenommen", "Abgelehnt"])
            app_notes = st.text_area("Notizen")
            if st.form_submit_button("Speichern", use_container_width=True) and check_write():
                if app_name:
                    data["applicants"].append({"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "name": app_name, "role": app_role, "status": app_status, "notes": app_notes, "date": datetime.now().strftime("%d.%m.%Y")})
                    save_data(data)
                    st.rerun()
    st.markdown("---")
    for app in reversed(data["applicants"]):
        st.markdown(f"""
        <div class='content-box'>
            <h3>{app['name']} <span style='font-size:14px; color:{t['ACCENT']};'>({app['status']})</span></h3>
            <p><strong>Rolle:</strong> {app['role']} | <strong>Datum:</strong> {app['date']}</p>
            {f"<p><em>Notiz: {app['notes']}</em></p>" if app.get('notes') else ""}
        </div>
        """, unsafe_allow_html=True)

# --- 4. VERWARNUNGEN ---
elif active_key == "warnings":
    st.title("⚠️ Verwarnungen & Strikes")
    with st.expander("➕ Verwarnung eintragen"):
        with st.form("add_warn_form"):
            w_member = st.selectbox("Mitglied", get_member_choices())
            w_level = st.selectbox("Stufe", ["Mündliche Verwarnung", "1. Verwarnung (Strike 1)", "2. Verwarnung (Strike 2)", "Letzte Warnung (Strike 3)"])
            w_reason = st.text_input("Grund")
            w_issuer = st.text_input("Von")
            if st.form_submit_button("Eintragen", use_container_width=True) and check_write():
                data["warnings"].append({"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "member": w_member, "level": w_level, "reason": w_reason, "issuer": w_issuer or "Team", "date": datetime.now().strftime("%d.%m.%Y")})
                save_data(data)
                st.rerun()
    st.markdown("---")
    for w in reversed(data["warnings"]):
        st.markdown(f"<div class='content-box'><strong>{w['member']}</strong> | <code>{w['level']}</code> (Von: {w['issuer']})<br>Grund: {w['reason']}</div>", unsafe_allow_html=True)

# --- 5. ABMELDUNGEN ---
elif active_key == "absences":
    st.title("📅 Abmeldungen & Urlaub")
    with st.expander("➕ Abmeldung erfassen"):
        with st.form("add_abs_form"):
            ab_member = st.selectbox("Mitglied", get_member_choices())
            ab_from = st.text_input("Von (z.B. 14.11.2026)")
            ab_to = st.text_input("Bis (z.B. 20.11.2026)")
            ab_reason = st.text_input("Grund")
            if st.form_submit_button("Speichern", use_container_width=True) and check_write():
                data["absences"].append({"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "name": ab_member, "from_date": ab_from, "to_date": ab_to, "reason": ab_reason})
                save_data(data)
                st.rerun()
    st.markdown("---")
    for ab in reversed(data["absences"]):
        st.markdown(f"<div class='content-box'><strong>{ab['name']}</strong> ({ab['from_date']} ➔ {ab['to_date']})<br>Grund: {ab['reason']}</div>", unsafe_allow_html=True)

# --- 6. AUFGABEN ---
elif active_key == "tasks":
    st.title("✅ Aufgaben-Board")
    with st.expander("➕ Neue Aufgabe erstellen"):
        with st.form("add_task_form"):
            t_title = st.text_input("Beschreibung")
            t_prio = st.selectbox("Priorität", ["Hoch", "Mittel", "Niedrig"])
            selected = [mc for mc in get_member_choices() if st.checkbox(mc, key=f"task_{mc}")]
            if st.form_submit_button("Erstellen", use_container_width=True) and check_write():
                data["tasks"].append({"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "title": t_title, "assignee": ", ".join(selected) or "Team", "priority": t_prio, "status": "Offen"})
                save_data(data)
                st.rerun()
    st.markdown("---")
    for task in reversed(data["tasks"]):
        st.markdown(f"<div class='content-box'><strong>{task['title']}</strong> (Prio: {task['priority']})<br>Zuständig: {task['assignee']} | Status: {task['status']}</div>", unsafe_allow_html=True)

# --- 7. PROTOKOLLE ---
elif active_key == "protocols":
    st.title("📝 Teamsitzungs-Protokolle")
    with st.expander("➕ Neues Protokoll"):
        with st.form("add_proto_form"):
            p_title = st.text_input("Titel")
            p_part = st.text_input("Teilnehmer")
            p_cont = st.text_area("Inhalt", value="1. Begrüßung:\n\n2. Themen:\n\n3. Beschlüsse:")
            if st.form_submit_button("Speichern", use_container_width=True) and check_write():
                data["protocols"].append({"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "title": p_title, "date": datetime.now().strftime("%d.%m.%Y %H:%M"), "participants": p_part, "content": p_cont})
                save_data(data)
                st.rerun()
    st.markdown("---")
    for p in reversed(data["protocols"]):
        st.markdown(f"<div class='content-box'><h3>{p['title']}</h3><p style='color:{t['TEXT_MUTED']}; font-size:12px;'>Erstellt: {p['date']} | Teilnehmer: {p['participants']}</p><pre style='background:transparent; color:{t['TEXT_MAIN']}; border:none;'>{p['content']}</pre></div>", unsafe_allow_html=True)

# --- 8. NOTIZEN ---
elif active_key == "notes":
    st.title("📌 Notizen")
    notes_val = st.text_area("Notizblock", value=data.get("notes", ""), height=350)
    if not is_readonly and st.button("💾 Speichern"):
        data["notes"] = notes_val
        save_data(data)
        st.success("Gespeichert!")

# --- 9. EINSTELLUNGEN ---
elif active_key == "settings":
    st.title("⚙️ Einstellungen & Design")
    st.markdown("Wähle hier dein bevorzugtes Farb-Theme:")
    selected_theme = st.selectbox("Farbschema / Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(current_theme_name))
    if st.button("🎨 Theme anwenden"):
        if "settings" not in data: data["settings"] = {}
        data["settings"]["theme"] = selected_theme
        save_data(data)
        st.rerun()

# --- 10. BENUTZER & RECHTE ---
elif active_key == "accounts":
    st.title("🔑 Benutzer & Rechte")
    if not st.session_state.is_superadmin:
        st.error("Nur für den Administrator.")
        st.stop()
    with st.form("add_user"):
        u_name = st.text_input("Benutzername")
        u_pass = st.text_input("Passwort", type="password")
        u_perms = {k: st.selectbox(f"{l}", ["full", "readonly", "hidden"]) for k, l in tabs_meta if k not in ["accounts", "settings"]}
        u_perms["accounts"] = "hidden"
        u_perms["settings"] = "full"
        if st.form_submit_button("Anlegen", use_container_width=True):
            if u_name and u_pass:
                data["users"].append({"username": u_name, "password": u_pass, "permissions": u_perms})
                save_data(data)
                st.rerun()
