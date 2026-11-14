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
        "BG_MAIN": "#121216", "BG_SIDEBAR": "#1A1A22", "BG_CARD": "#22222D", "BG_INPUT": "#2B2B38", "ACCENT": "#EF4444", "ACCENT_HOVER": "#DC2626", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#A1A5B0"
    },
    "2. Midnight Blue (Blau-Taktisch)": {
        "BG_MAIN": "#0F172A", "BG_SIDEBAR": "#1E293B", "BG_CARD": "#334155", "BG_INPUT": "#475569", "ACCENT": "#3B82F6", "ACCENT_HOVER": "#2563EB", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#94A3B8"
    },
    "3. Blood Moon (Rot-Karmesin)": {
        "BG_MAIN": "#1A0F0F", "BG_SIDEBAR": "#2B1616", "BG_CARD": "#3D2020", "BG_INPUT": "#522B2B", "ACCENT": "#EF4444", "ACCENT_HOVER": "#DC2626", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#B89999"
    },
    "4. Cyberpunk Neon (Pink-Violett)": {
        "BG_MAIN": "#120F24", "BG_SIDEBAR": "#1E183B", "BG_CARD": "#2C2254", "BG_INPUT": "#3B2F6E", "ACCENT": "#F43F5E", "ACCENT_HOVER": "#E11D48", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#A89EC9"
    },
    "5. Emerald Syndicate (Grün-Smaragd)": {
        "BG_MAIN": "#0A1F18", "BG_SIDEBAR": "#113026", "BG_CARD": "#1B4738", "BG_INPUT": "#26614D", "ACCENT": "#10B981", "ACCENT_HOVER": "#059669", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#9CA3AF"
    },
    "6. Matrix Terminal (Grün-Neon)": {
        "BG_MAIN": "#05140A", "BG_SIDEBAR": "#0B2412", "BG_CARD": "#143D1F", "BG_INPUT": "#1F5C2F", "ACCENT": "#22C55E", "ACCENT_HOVER": "#16A34A", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#9CA3AF"
    },
    "7. Golden Royalty (Gold-Gelb)": {
        "BG_MAIN": "#1C1912", "BG_SIDEBAR": "#2C271A", "BG_CARD": "#3D3725", "BG_INPUT": "#524A33", "ACCENT": "#EAB308", "ACCENT_HOVER": "#CA8A04", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#B3AB94"
    },
    "8. Purple Haze (Lila-Mystic)": {
        "BG_MAIN": "#151024", "BG_SIDEBAR": "#211936", "BG_CARD": "#31254F", "BG_INPUT": "#43326B", "ACCENT": "#A855F7", "ACCENT_HOVER": "#9333EA", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#B4ADC9"
    },
    "9. Steel Gray (Grau-Neutral)": {
        "BG_MAIN": "#18181B", "BG_SIDEBAR": "#27272A", "BG_CARD": "#3F3F46", "BG_INPUT": "#52525B", "ACCENT": "#71717A", "ACCENT_HOVER": "#52525B", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#A1A1AA"
    },
    "10. Deep Ocean (Blau-Ozean)": {
        "BG_MAIN": "#0B192C", "BG_SIDEBAR": "#12263F", "BG_CARD": "#1E3E62", "BG_INPUT": "#2A5282", "ACCENT": "#0EA5E9", "ACCENT_HOVER": "#0284C7", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#93C5FD"
    },
    "11. Sunset Orange (Orange-Warm)": {
        "BG_MAIN": "#1F130B", "BG_SIDEBAR": "#301D11", "BG_CARD": "#452A19", "BG_INPUT": "#5E3923", "ACCENT": "#F97316", "ACCENT_HOVER": "#EA580C", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#D1B5A3"
    },
    "12. Coffee Dark (Braun-Kaffee)": {
        "BG_MAIN": "#1C1411", "BG_SIDEBAR": "#2B1E1A", "BG_CARD": "#3D2B26", "BG_INPUT": "#543C35", "ACCENT": "#D97706", "ACCENT_HOVER": "#B45309", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#C4B5A5"
    },
    "13. Arctic Frost (Türkis-Eis)": {
        "BG_MAIN": "#0F1E26", "BG_SIDEBAR": "#172E3B", "BG_CARD": "#224354", "BG_INPUT": "#305C73", "ACCENT": "#06B6D4", "ACCENT_HOVER": "#0891B2", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#A5F3FC"
    },
    "14. Vampire Rose (Rosa-Beeren)": {
        "BG_MAIN": "#210F17", "BG_SIDEBAR": "#331824", "BG_CARD": "#4A2435", "BG_INPUT": "#663149", "ACCENT": "#FB7185", "ACCENT_HOVER": "#F43F5E", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#E2B8C9"
    },
    "15. Hacker Acid (Limette-Giftgrün)": {
        "BG_MAIN": "#171A0F", "BG_SIDEBAR": "#252B17", "BG_CARD": "#374221", "BG_INPUT": "#4D5B2F", "ACCENT": "#84CC16", "ACCENT_HOVER": "#65A30D", "TEXT_MAIN": "#FFFFFF", "TEXT_MUTED": "#CBD5E1"
    }
}

# --- DATEN & PFADE ---
DATA_FILE = "wolflife_team_data.json"

RANKS = [
    "Owner",
    "Projektleitung",
    "stellvertretende Projektleitung",
    "Teamleitung",
    "stellvertretende Teamleitung",
    "Administrator", "Test-Administrator",
    "Moderator 3", "Moderator 2", "Moderator 1", "Test-Moderator",
    "Supporter 3", "Supporter 2", "Supporter 1", "Test-Supporter"
]

RANK_COLORS = {
    "Owner": "#A855F7",
    "Projektleitung": "#FF69B4",
    "stellvertretende Projektleitung": "#FF69B4",
    "Teamleitung": "#FF7B00",
    "stellvertretende Teamleitung": "#FF7B00",
    "Administrator": "#FF2A2A",
    "Test-Administrator": "#FF2A2A",
    "Moderator 3": "#3B82F6",
    "Moderator 2": "#3B82F6",
    "Moderator 1": "#3B82F6",
    "Test-Moderator": "#3B82F6",
    "Supporter 3": "#EAB308",
    "Supporter 2": "#EAB308",
    "Supporter 1": "#EAB308",
    "Test-Supporter": "#EAB308"
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

# Theme-Farben aus den Einstellungen laden
current_theme_name = data.get("settings", {}).get("theme", "1. Wolf Life Dark (Rot-Dunkel Standard)")
if current_theme_name not in THEMES:
    current_theme_name = "1. Wolf Life Dark (Rot-Dunkel Standard)"
t = THEMES[current_theme_name]

# --- DYNAMISCHES CSS (GARANTIERT HELLE SCHRIFT & SICHTBARER BENUTZER) ---
st.markdown(f"""
<style>
    .stApp {{
        background-color: {t["BG_MAIN"]};
        color: {t["TEXT_MAIN"]};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background-color: {t["BG_SIDEBAR"]};
        border-right: 1px solid #3F3F46;
    }}
    /* Alle Texte & Überschriften explizit hell und lesbar */
    h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: {t["TEXT_MAIN"]} !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {t["TEXT_MAIN"]} !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {t["TEXT_MUTED"]} !important;
    }}
    .stButton>button {{
        background-color: {t["ACCENT"]};
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: {t["ACCENT_HOVER"]};
        color: white;
    }}
    input, textarea, select {{
        background-color: {t["BG_INPUT"]} !important;
        color: {t["TEXT_MAIN"]} !important;
    }}
</style>
""", unsafe_allow_html=True)

# Initialisiere Session State für Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.is_superadmin = False
    st.session_state.permissions = {}

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center; color: {t['TEXT_MAIN']};'>🐺 WOLF LIFE ROLEPLAY</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: {t['ACCENT']}; font-weight: bold;'>TEAM MANAGEMENT SUITE</p>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### Bitte einloggen")
            username_input = st.text_input("Benutzername")
            password_input = st.text_input("Passwort", type="password")
            
            if st.button("Anmelden", use_container_width=True):
                if username_input == "Admin" and password_input == "wolf123":
                    st.session_state.logged_in = True
                    st.session_state.username = "Admin"
                    st.session_state.is_superadmin = True
                    st.session_state.permissions = {
                        "dashboard": "full", "team": "full", "applicants": "full",
                        "warnings": "full", "absences": "full", "tasks": "full",
                        "protocols": "full", "notes": "full", "accounts": "full", "settings": "full"
                    }
                    st.rerun()
                else:
                    user_found = None
                    for u in data.get("users", []):
                        if u["username"] == username_input and u["password"] == password_input:
                            user_found = u
                            break
                    if user_found:
                        st.session_state.logged_in = True
                        st.session_state.username = user_found["username"]
                        st.session_state.is_superadmin = False
                        st.session_state.permissions = user_found.get("permissions", {})
                        st.rerun()
                    else:
                        st.error("Falscher Benutzername oder falsches Passwort!")
    st.stop()

# --- HAUPTAPP NACH LOGIN (SIDEBAR) ---
st.sidebar.markdown(f"### 🐺 WOLF LIFE")
st.sidebar.markdown(f"Eingeloggt: **{st.session_state.username}**")

if st.sidebar.button("🔒 Abmelden", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

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

available_tabs = []
tab_keys = []
tab_modes = []

for key, label in tabs_meta:
    mode = "full" if st.session_state.is_superadmin else st.session_state.permissions.get(key, "full")
    if key == "settings": mode = "full" # Einstellungen für jeden erreichbar
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

def check_write():
    if is_readonly and not st.session_state.is_superadmin:
        st.warning("Zugriff verweigert: Account hat nur Lese-Rechte in diesem Tab.")
        return False
    return True

def get_member_choices():
    members = data.get("members", [])
    if not members:
        return ["Kein Mitglied eingetragen"]
    return [f"{m['name']} ({m['rank']})" for m in members]

# --- 1. DASHBOARD ---
if active_key == "dashboard":
    st.title("📊 Dashboard & Live-Statistiken")
    total_members = len(data["members"])
    total_applicants = len([a for a in data["applicants"] if a.get("status") not in ["Angenommen", "Abgelehnt"]])
    active_warnings = len(data["warnings"])
    open_tasks = len([t for t in data["tasks"] if t.get("status") != "Erledigt"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Teammitglieder", total_members)
    col2.metric("Offene Bewerbungen", total_applicants)
    col3.metric("Aktive Verwarnungen", active_warnings)
    col4.metric("Offene Aufgaben", open_tasks)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🛡️ Rang-Verteilung im Team")
        for r in RANKS:
            count = len([m for m in data["members"] if m["rank"] == r])
            if count > 0:
                color = RANK_COLORS.get(r, "#FFFFFF")
                st.markdown(f"- <span style='color:{color}; font-weight:bold;'>● {r}</span>: **{count}** Mitglied(er)", unsafe_allow_html=True)
    with c2:
        st.subheader("📅 Aktuelle Abmeldungen")
        if not data["absences"]:
            st.info("Keine aktuellen Abmeldungen vorhanden.")
        else:
            for ab in data["absences"][-4:]:
                st.markdown(f"- **{ab['name']}** ({ab['from_date']} – {ab['to_date']}): *{ab['reason']}*")

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
                    data["members"].append({
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "name": m_name,
                        "discord_id": m_discord_id or "-", "rank": m_rank, "status": m_status,
                        "joined": datetime.now().strftime("%d.%m.%Y")
                    })
                    save_data(data)
                    st.success("Erfolgreich hinzugefügt!")
                    st.rerun()

    st.markdown("---")
    search_query = st.text_input("🔍 Mitglied suchen...")
    filtered = [m for m in data["members"] if search_query.lower() in m["name"].lower()]
    sorted_members = sorted(filtered, key=lambda m: RANKS.index(m["rank"]) if m["rank"] in RANKS else 99)
    
    for member in sorted_members:
        cols = st.columns([2, 2, 2, 1])
        rank_col = RANK_COLORS.get(member['rank'], '#FFFFFF')
        cols[0].markdown(f"**{member['name']}**")
        cols[1].markdown(f"<span style='color:{rank_col}; font-weight:bold;'>{member['rank']}</span>", unsafe_allow_html=True)
        cols[2].markdown(f"Status: {member['status']}")
        if not is_readonly and cols[3].button("Entfernen", key=f"del_m_{member['id']}"):
            data["members"].remove(member)
            save_data(data)
            st.rerun()
        st.markdown("---")

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
                    data["applicants"].append({
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "name": app_name,
                        "role": app_role, "status": app_status, "notes": app_notes, "date": datetime.now().strftime("%d.%m.%Y")
                    })
                    save_data(data)
                    st.rerun()
    st.markdown("---")
    for app in reversed(data["applicants"]):
        st.markdown(f"### 👤 {app['name']} — `{app['status']}`")
        st.markdown(f"**Rolle:** {app['role']} | **Datum:** {app['date']}")
        if app.get("notes"): st.markdown(f"> 📝 {app['notes']}")
        if not is_readonly and st.button("Löschen", key=f"del_app_{app['id']}"):
            data["applicants"].remove(app)
            save_data(data)
            st.rerun()
        st.markdown("---")

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
        st.markdown(f"**{w['member']}** | `{w['level']}` (Von: {w['issuer']})")
        st.markdown(f"> {w['reason']}")
        if not is_readonly and st.button("Löschen", key=f"del_w_{w['id']}"):
            data["warnings"].remove(w)
            save_data(data)
            st.rerun()
        st.markdown("---")

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
        st.markdown(f"**{ab['name']}** ({ab['from_date']} ➔ {ab['to_date']}) – *{ab['reason']}*")
        if not is_readonly and st.button("Löschen", key=f"del_ab_{ab['id']}"):
            data["absences"].remove(ab)
            save_data(data)
            st.rerun()
        st.markdown("---")

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
        cols = st.columns([3, 2, 2, 1])
        cols[0].markdown(f"**{task['title']}** (Prio: {task['priority']})")
        cols[1].markdown(f"Zuständig: {task['assignee']}")
        cols[2].markdown(f"Status: {task['status']}")
        if not is_readonly and cols[3].button("Löschen", key=f"del_t_{task['id']}"):
            data["tasks"].remove(task)
            save_data(data)
            st.rerun()
        st.markdown("---")

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
        st.markdown(f"### {p['title']}")
        st.text(p['content'])
        if not is_readonly and st.button("Löschen", key=f"del_p_{p['id']}"):
            data["protocols"].remove(p)
            save_data(data)
            st.rerun()
        st.markdown("---")

# --- 8. NOTIZEN ---
elif active_key == "notes":
    st.title("📌 Notizen")
    notes_val = st.text_area("Notizblock", value=data.get("notes", ""), height=350)
    if not is_readonly and st.button("💾 Speichern"):
        data["notes"] = notes_val
        save_data(data)
        st.success("Gespeichert!")

# --- 9. EINSTELLUNGEN (MIT ALLEN 15 FARBVARIANTEN) ---
elif active_key == "settings":
    st.title("⚙️ Einstellungen & Design")
    st.markdown("Wähle hier dein bevorzugtes Farb-Theme für das gesamte Tool:")
    
    selected_theme = st.selectbox("Farbschema / Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(current_theme_name))
    
    if st.button("🎨 Theme anwenden"):
        if "settings" not in data: data["settings"] = {}
        data["settings"]["theme"] = selected_theme
        save_data(data)
        st.success("Theme erfolgreich angewendet! Die Seite lädt neu...")
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
    st.markdown("---")
    for u in data["users"]:
        cols = st.columns([3, 1])
        cols[0].markdown(f"**{u['username']}**")
        if cols[1].button("Löschen", key=f"del_u_{u['username']}"):
            data["users"] = [x for x in data["users"] if x["username"] != u["username"]]
            save_data(data)
            st.rerun()
