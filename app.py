import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Wolf Life Team-Management",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATEN & PFADE ---
DATA_FILE = "wolflife_team_data.json"
LOGO_FILE = "Wolf Life LOGO.jpg"

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
        "notes": "", "users": []
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

# Initialisiere Session State für Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.is_superadmin = False
    st.session_state.permissions = {}

data = load_data()

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🐺 WOLF LIFE ROLEPLAY</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #D91616;'>Team Management Suite</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
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
                    "protocols": "full", "notes": "full", "accounts": "full"
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

# --- HAUPTAPP NACH LOGIN ---
st.sidebar.markdown(f"### 🐺 WOLF LIFE")
st.sidebar.markdown(f"Eingeloggt als: **{st.session_state.username}**")

if st.sidebar.button("🔒 Abmelden"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# Navigation basierend auf Berechtigungen
tabs_meta = [
    ("dashboard", "📊 Dashboard"),
    ("team", "👥 Team-Übersicht"),
    ("applicants", "📋 Bewerber"),
    ("warnings", "⚠️ Verwarnungen"),
    ("absences", "📅 Abmeldungen"),
    ("tasks", "✅ Aufgaben"),
    ("protocols", "📝 Protokolle"),
    ("notes", "📌 Notizen"),
    ("accounts", "🔑 Benutzer & Rechte")
]

available_tabs = []
tab_keys = []
tab_modes = []

for key, label in tabs_meta:
    mode = "full" if st.session_state.is_superadmin else st.session_state.permissions.get(key, "full")
    if mode != "hidden":
        available_tabs.append(label)
        tab_keys.append(key)
        tab_modes.append(mode)

if not available_tabs:
    st.warning("Dein Account hat aktuell für keinen Bereich Zugriff.")
    st.stop()

selected_tab_label = st.sidebar.radio("Navigation", available_tabs)
current_index = available_tabs.index(selected_tab_label)
active_key = tab_keys[current_index]
active_mode = tab_modes[current_index]

is_readonly = (active_mode == "readonly")
if is_readonly:
    st.info("ℹ️ Du hast für diesen Bereich den Modus **Nur-Lesen** (keine Bearbeitungen möglich).")

def check_write():
    if is_readonly and not st.session_state.is_superadmin:
        st.warning("Zugriff verweigert: Account hat nur Lese-Rechte in diesem Tab.")
        return False
    return True

# Hilfsfunktion für Mitgliederauswahl
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
        st.subheader("Rang-Verteilung")
        for r in RANKS:
            count = len([m for m in data["members"] if m["rank"] == r])
            if count > 0:
                st.markdown(f"- **{r}**: {count}")
    with c2:
        st.subheader("Aktuelle Abmeldungen")
        if not data["absences"]:
            st.text("Keine Abmeldungen vorhanden.")
        else:
            for ab in data["absences"][-4:]:
                st.markdown(f"- **{ab['name']}** ({ab['from_date']} bis {ab['to_date']}): {ab['reason']}")

# --- 2. TEAM-ÜBERSICHT ---
elif active_key == "team":
    st.title("👥 Team-Übersicht & Kader")
    
    with st.expander("➕ Neues Teammitglied hinzufügen"):
        with st.form("add_member_form"):
            m_name = st.text_input("Discord Name / Tag")
            m_discord_id = st.text_input("Discord-ID (Optional)")
            m_rank = st.selectbox("Rang", RANKS)
            m_status = st.selectbox("Status", ["Aktiv", "Probezeit", "Abgemeldet"])
            submit_m = st.form_submit_button("Hinzufügen")
            
            if submit_m:
                if check_write():
                    if m_name:
                        data["members"].append({
                            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            "name": m_name,
                            "discord_id": m_discord_id or "-",
                            "rank": m_rank,
                            "status": m_status,
                            "joined": datetime.now().strftime("%d.%m.%Y")
                        })
                        save_data(data)
                        st.success("Mitglied hinzugefügt!")
                        st.rerun()
                    else:
                        st.error("Bitte Namen eingeben.")

    st.markdown("---")
    search_query = st.text_input("🔍 Mitglied suchen...")
    
    filtered_members = [m for m in data["members"] if search_query.lower() in m["name"].lower() or search_query.lower() in m["discord_id"].lower()]
    sorted_members = sorted(filtered_members, key=lambda m: RANKS.index(m["rank"]) if m["rank"] in RANKS else 99)
    
    for member in sorted_members:
        cols = st.columns([2, 2, 2, 1, 1])
        cols[0].markdown(f"**{member['name']}**")
        cols[1].markdown(f"Rang: `{member['rank']}`")
        cols[2].markdown(f"Status: {member['status']}")
        
        if not is_readonly:
            if cols[3].button("Löschen", key=f"del_m_{member['id']}"):
                if check_write():
                    data["members"].remove(member)
                    save_data(data)
                    st.rerun()
        st.markdown("---")

# --- 3. BEWERBER ---
elif active_key == "applicants":
    st.title("📋 Bewerber & Testphase")
    
    with st.expander("➕ Neue Bewerbung erfassen"):
        with st.form("add_app_form"):
            app_name = st.text_input("Discord Name / Tag")
            app_role = st.selectbox("Angestrebte Rolle", ["Supporter (Bewerbung)", "Moderator (Bewerbung)", "Administrator (Bewerbung)"])
            app_status = st.selectbox("Status", ["Bewerbung eingegangen", "Im Testgespräch", "Testphase läuft", "Angenommen", "Abgelehnt"])
            app_notes = st.text_area("Notizen zur Bewerbung")
            submit_app = st.form_submit_button("Speichern")
            
            if submit_app:
                if check_write():
                    if app_name:
                        data["applicants"].append({
                            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            "name": app_name,
                            "role": app_role,
                            "status": app_status,
                            "notes": app_notes,
                            "date": datetime.now().strftime("%d.%m.%Y")
                        })
                        save_data(data)
                        st.success("Bewerbung eingetragen!")
                        st.rerun()
                    else:
                        st.error("Bitte Namen eingeben.")

    st.markdown("---")
    for app in reversed(data["applicants"]):
        st.markdown(f"### {app['name']} ({app['status']})")
        st.markdown(f"**Rolle:** {app['role']} | **Datum:** {app['date']}")
        if app.get("notes"):
            st.markdown(f"📝 *Notiz:* {app['notes']}")
        
        if not is_readonly:
            c1, c2 = st.columns(2)
            if app["status"] != "Angenommen":
                if c1.button("➔ Als Test-Rang übernehmen", key=f"promote_{app['id']}"):
                    if check_write():
                        target_rank = "Test-Supporter"
                        if "Administrator" in app["role"]: target_rank = "Test-Administrator"
                        elif "Moderator" in app["role"]: target_rank = "Test-Moderator"
                        
                        data["members"].append({
                            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            "name": app["name"],
                            "discord_id": "-",
                            "rank": target_rank,
                            "status": "Probezeit",
                            "joined": datetime.now().strftime("%d.%m.%Y")
                        })
                        app["status"] = "Angenommen"
                        save_data(data)
                        st.success(f"{app['name']} wurde als {target_rank} übernommen!")
                        st.rerun()
            if c2.button("Löschen", key=f"del_app_{app['id']}"):
                if check_write():
                    data["applicants"].remove(app)
                    save_data(data)
                    st.rerun()
        st.markdown("---")

# --- 4. VERWARNUNGEN ---
elif active_key == "warnings":
    st.title("⚠️ Verwarnungen & Strikes")
    
    with st.expander("➕ Verwarnung eintragen"):
        with st.form("add_warn_form"):
            member_choices = get_member_choices()
            w_member = st.selectbox("Teammitglied", member_choices)
            w_level = st.selectbox("Stufe", ["Mündliche Verwarnung", "1. Verwarnung (Strike 1)", "2. Verwarnung (Strike 2)", "Letzte Warnung (Strike 3)"])
            w_reason = st.text_input("Grund")
            w_issuer = st.text_input("Ausgestellt von")
            submit_w = st.form_submit_button("Eintragen")
            
            if submit_w:
                if check_write():
                    if w_reason:
                        data["warnings"].append({
                            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            "member": w_member,
                            "level": w_level,
                            "reason": w_reason,
                            "issuer": w_issuer or "Teamleitung",
                            "date": datetime.now().strftime("%d.%m.%Y")
                        })
                        save_data(data)
                        st.success("Verwarnung eingetragen!")
                        st.rerun()
                    else:
                        st.error("Bitte Grund angeben.")

    st.markdown("---")
    for w in reversed(data["warnings"]):
        st.markdown(f"**{w['member']}** – `{w['level']}` (Von: {w['issuer']} am {w['date']})")
        st.markdown(f"Grund: {w['reason']}")
        if not is_readonly:
            if st.button("Löschen", key=f"del_w_{w['id']}"):
                if check_write():
                    data["warnings"].remove(w)
                    save_data(data)
                    st.rerun()
        st.markdown("---")

# --- 5. ABMELDUNGEN ---
elif active_key == "absences":
    st.title("📅 Abmeldungen & Urlaub")
    
    with st.expander("➕ Abmeldung erfassen"):
        with st.form("add_abs_form"):
            member_choices = get_member_choices()
            ab_member = st.selectbox("Mitglied", member_choices)
            ab_from = st.text_input("Von (z.B. 14.11.2026)")
            ab_to = st.text_input("Bis (z.B. 20.11.2026)")
            ab_reason = st.text_input("Grund")
            submit_ab = st.form_submit_button("Speichern")
            
            if submit_ab:
                if check_write():
                    if ab_from and ab_to:
                        data["absences"].append({
                            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            "name": ab_member,
                            "from_date": ab_from,
                            "to_date": ab_to,
                            "reason": ab_reason or "Privat"
                        })
                        save_data(data)
                        st.success("Abmeldung gespeichert!")
                        st.rerun()
                    else:
                        st.error("Daten angeben.")

    st.markdown("---")
    for ab in reversed(data["absences"]):
        st.markdown(f"**{ab['name']}** ({ab['from_date']} bis {ab['to_date']}) – Grund: {ab['reason']}")
        if not is_readonly:
            if st.button("Löschen", key=f"del_ab_{ab['id']}"):
                if check_write():
                    data["absences"].remove(ab)
                    save_data(data)
                    st.rerun()
        st.markdown("---")

# --- 6. AUFGABEN ---
elif active_key == "tasks":
    st.title("✅ Aufgaben-Board")
    
    with st.expander("➕ Neue Aufgabe erstellen"):
        with st.form("add_task_form"):
            t_title = st.text_input("Aufgabenbeschreibung")
            t_prio = st.selectbox("Priorität", ["Hoch", "Mittel", "Niedrig"])
            
            st.markdown("Zuständige Teammitglieder:")
            member_choices = get_member_choices()
            selected_assignees = []
            for mc in member_choices:
                if st.checkbox(mc, key=f"task_m_{mc}"):
                    selected_assignees.append(mc)
            
            submit_t = st.form_submit_button("Erstellen")
            
            if submit_t:
                if check_write():
                    if t_title:
                        assignee_str = ", ".join(selected_assignees) if selected_assignees else "Alle / Team"
                        data["tasks"].append({
                            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            "title": t_title,
                            "assignee": assignee_str,
                            "priority": t_prio,
                            "status": "Offen"
                        })
                        save_data(data)
                        st.success("Aufgabe erstellt!")
                        st.rerun()
                    else:
                        st.error("Bitte Titel eingeben.")

    st.markdown("---")
    for task in reversed(data["tasks"]):
        cols = st.columns([3, 2, 2, 1])
        cols[0].markdown(f"**{task['title']}** (Prio: {task['priority']})")
        cols[1].markdown(f"Zuständig: {task['assignee']}")
        cols[2].markdown(f"Status: {task['status']}")
        
        if not is_readonly:
            if cols[3].button("Löschen", key=f"del_t_{task['id']}"):
                if check_write():
                    data["tasks"].remove(task)
                    save_data(data)
                    st.rerun()
        st.markdown("---")

# --- 7. PROTOKOLLE ---
elif active_key == "protocols":
    st.title("📝 Teamsitzungs-Protokolle")
    
    with st.expander("➕ Neues Protokoll anlegen"):
        with st.form("add_proto_form"):
            p_title = st.text_input("Titel (z.B. Teamsitzung KW 46)")
            p_participants = st.text_input("Teilnehmer")
            p_content = st.text_area("Inhalt / Beschlüsse", value="1. Begrüßung:\n\n2. Themen:\n\n3. Beschlüsse:")
            submit_p = st.form_submit_button("Speichern")
            
            if submit_p:
                if check_write():
                    if p_title:
                        data["protocols"].append({
                            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            "title": p_title,
                            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                            "participants": p_participants or "-",
                            "content": p_content
                        })
                        save_data(data)
                        st.success("Protokoll gespeichert!")
                        st.rerun()
                    else:
                        st.error("Titel angeben.")

    st.markdown("---")
    for p in reversed(data["protocols"]):
        st.markdown(f"### {p['title']}")
        st.markdown(f"Erstellt: {p['date']} | Teilnehmer: {p['participants']}")
        st.text(p['content'])
        if not is_readonly:
            if st.button("Löschen", key=f"del_p_{p['id']}"):
                if check_write():
                    data["protocols"].remove(p)
                    save_data(data)
                    st.rerun()
        st.markdown("---")

# --- 8. NOTIZEN ---
elif active_key == "notes":
    st.title("📌 Notizen")
    notes_val = st.text_area("Schneller Notizblock", value=data.get("notes", ""), height=300)
    if not is_readonly:
        if st.button("Notizen speichern"):
            if check_write():
                data["notes"] = notes_val
                save_data(data)
                st.success("Gespeichert!")

# --- 9. BENUTZER & RECHTE ---
elif active_key == "accounts":
    st.title("🔑 Benutzer & Rechteverwaltung")
    
    if not st.session_state.is_superadmin:
        st.error("Nur der Admin hat Zugriff auf diese Verwaltung.")
        st.stop()
        
    with st.form("add_user_form"):
        u_name = st.text_input("Neuer Benutzername")
        u_pass = st.text_input("Passwort", type="password")
        
        st.markdown("**Rechte je Tab einstellen:**")
        u_perms = {}
        for key, label in tabs_meta:
            if key == "accounts": continue
            u_perms[key] = st.selectbox(f"{label}", ["full", "readonly", "hidden"], key=f"perm_{key}")
        u_perms["accounts"] = "hidden"
        
        submit_user = st.form_submit_button("Account anlegen")
        if submit_user:
            if u_name and u_pass:
                data["users"].append({
                    "username": u_name,
                    "password": u_pass,
                    "permissions": u_perms
                })
                save_data(data)
                st.success(f"Account {u_name} erstellt!")
                st.rerun()
            else:
                st.error("Bitte Name und Passwort eingeben.")
                
    st.markdown("---")
    st.subheader("Bestehende Accounts")
    for u in data["users"]:
        cols = st.columns([2, 4, 1])
        cols[0].markdown(f"**{u['username']}**")
        cols[1].markdown(f"Rechte: `{u.get('permissions', {})}`")
        if cols[2].button("Löschen", key=f"del_u_{u['username']}"):
            data["users"] = [x for x in data["users"] if x["username"] != u["username"]]
            save_data(data)
            st.rerun()
