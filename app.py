import streamlit as st
import json, os, uuid, time, hmac, hashlib, secrets, threading, shutil, base64, random
from urllib.parse import quote
import re, urllib.request, urllib.error
from contextlib import contextmanager
from datetime import datetime, date, timezone
from html import escape as esc

LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.jpg")
st.set_page_config(page_title="Wolf Life Team-Management", page_icon=LOGO if os.path.exists(LOGO) else "🐺", layout="wide")

DATA_FILE = "wolflife_team_data.json"
DEFAULT_THEME = "1. Wolf Life Dark (Rot-Dunkel Standard)"

# --- THEMES: Name, BG_MAIN, BG_SIDEBAR, BG_CARD, BG_INPUT, ACCENT, ACCENT_HOVER, TEXT_MUTED ---
_T = [
    (DEFAULT_THEME, "#0D0D11", "#14141A", "#1C1C24", "#22222D", "#EF4444", "#DC2626", "#9CA3AF"),
    ("2. Midnight Blue (Blau-Taktisch)", "#090D16", "#111827", "#1E293B", "#2A3748", "#3B82F6", "#2563EB", "#94A3B8"),
    ("3. Blood Moon (Rot-Karmesin)", "#120808", "#1F0D0D", "#2C1515", "#381B1B", "#EF4444", "#DC2626", "#B89999"),
    ("4. Cyberpunk Neon (Pink-Violett)", "#0A0814", "#131022", "#1F1A38", "#29224A", "#F43F5E", "#E11D48", "#A89EC9"),
    ("5. Emerald Syndicate (Grün-Smaragd)", "#05100C", "#0A1C15", "#132E23", "#1A3E31", "#10B981", "#059669", "#9CA3AF"),
    ("6. Matrix Terminal (Grün-Neon)", "#030A05", "#07170B", "#0F2914", "#14361C", "#22C55E", "#16A34A", "#9CA3AF"),
    ("7. Golden Royalty (Gold-Gelb)", "#12100B", "#1C1912", "#2B261A", "#363022", "#EAB308", "#CA8A04", "#B3AB94"),
    ("8. Purple Haze (Lila-Mystic)", "#0D0A14", "#161124", "#221A38", "#2D2447", "#A855F7", "#9333EA", "#B4ADC9"),
    ("9. Steel Gray (Grau-Neutral)", "#0F0F10", "#18181B", "#27272A", "#333338", "#71717A", "#52525B", "#A1A1AA"),
    ("10. Deep Ocean (Blau-Ozean)", "#060E17", "#0F1E2E", "#172F47", "#203D5C", "#0EA5E9", "#0284C7", "#93C5FD"),
    ("11. Sunset Orange (Orange-Warm)", "#120B07", "#1F130B", "#301D11", "#3D2719", "#F97316", "#EA580C", "#D1B5A3"),
    ("12. Coffee Dark (Braun-Kaffee)", "#110C0A", "#1C1411", "#2B1E1A", "#362723", "#D97706", "#B45309", "#C4B5A5"),
    ("13. Arctic Frost (Türkis-Eis)", "#091217", "#0F1E26", "#172E3B", "#1F3D4D", "#06B6D4", "#0891B2", "#A5F3FC"),
    ("14. Vampire Rose (Rosa-Beeren)", "#140A0F", "#210F17", "#331824", "#40202E", "#FB7185", "#F43F5E", "#E2B8C9"),
    ("15. Hacker Acid (Limette-Giftgrün)", "#0E1009", "#171A0F", "#252B17", "#30381F", "#84CC16", "#65A30D", "#CBD5E1"),
]
_KEYS = ["BG_MAIN", "BG_SIDEBAR", "BG_CARD", "BG_INPUT", "ACCENT", "ACCENT_HOVER", "TEXT_MUTED"]
THEMES = {n: dict(zip(_KEYS, v), TEXT_MAIN="#FFFFFF") for n, *v in _T}

# --- FESTE ZUORDNUNG DER 15 HINTERGRUNDBILDER IM ORDNER "themes_bg" ---
THEME_BG_MAP = {
    DEFAULT_THEME: "theme_01_wolflife_dark.jpg",
    "2. Midnight Blue (Blau-Taktisch)": "theme_02_midnight_blue.jpg",
    "3. Blood Moon (Rot-Karmesin)": "theme_03_blood_moon.jpg",
    "4. Cyberpunk Neon (Pink-Violett)": "theme_04_cyberpunk_neon.jpg",
    "5. Emerald Syndicate (Grün-Smaragd)": "theme_05_emerald_syndicate.jpg",
    "6. Matrix Terminal (Grün-Neon)": "theme_06_matrix_terminal.jpg",
    "7. Golden Royalty (Gold-Gelb)": "theme_07_golden_royalty.jpg",
    "8. Purple Haze (Lila-Mystic)": "theme_08_purple_haze.jpg",
    "9. Steel Gray (Grau-Neutral)": "theme_09_steel_gray.jpg",
    "10. Deep Ocean (Blau-Ozean)": "theme_10_deep_ocean.jpg",
    "11. Sunset Orange (Orange-Warm)": "theme_11_sunset_orange.jpg",
    "12. Coffee Dark (Braun-Kaffee)": "theme_12_coffee_dark.jpg",
    "13. Arctic Frost (Türkis-Eis)": "theme_13_arctic_frost.jpg",
    "14. Vampire Rose (Rosa-Beeren)": "theme_14_vampire_rose.jpg",
    "15. Hacker Acid (Limette-Giftgrün)": "theme_15_hacker_acid.jpg",
}

RANKS = [
    "Owner", "Projektleitung", "Developer", "stellvertretende Projektleitung",
    "Teamleitung", "stellvertretende Teamleitung",
    "Administrator", "Test-Administrator",
    "Moderator 3", "Moderator 2", "Moderator 1", "Test-Moderator",
    "Supporter 3", "Supporter 2", "Supporter 1", "Test-Supporter",
]
MEMBER_STATUS = ["Aktiv", "Probezeit", "Abgemeldet"]
APP_STATUS = ["Bewerbung eingegangen", "Im Testgespräch", "Testphase läuft", "Angenommen", "Abgelehnt"]
APP_ROLES = {"Supporter (Bewerbung)": "Test-Supporter", "Moderator (Bewerbung)": "Test-Moderator",
             "Administrator (Bewerbung)": "Test-Administrator"}
PRIOS = ["Hoch", "Mittel", "Niedrig"]
PERM_OPTS = ["full", "readonly", "absence_own", "hidden"]
PERM_LABELS = {"full": "Vollzugriff", "readonly": "Nur-Lesen", "absence_own": "Eigene Abmeldung", "hidden": "Versteckt"}
TASK_APPROVER_RANKS = ["Owner", "Projektleitung", "Developer"]  # dürfen Aufgabenvorschläge übernehmen
DEF_PERM = {"wishes": "readonly"}  # Teamwünsche sind standardmäßig für alle sichtbar
WISH_STATUS = ["Neu", "In Prüfung", "Geplant", "Umgesetzt", "Abgelehnt"]
WISH_OPEN = ("Neu", "In Prüfung", "Geplant")
WISH_COL = {"Neu": "#3B82F6", "In Prüfung": "#F59E0B", "Geplant": "#A855F7", "Umgesetzt": "#22C55E", "Abgelehnt": "#9CA3AF"}
WISH_CATS = ["🎨 Design", "⚙️ Funktion", "🐞 Fehler", "💬 Sonstiges"]
STATUS_COL = {"Aktiv": "#22C55E", "Probezeit": "#F59E0B", "Abgemeldet": "#9CA3AF"}
PRIO_COL = {"Hoch": "#EF4444", "Mittel": "#F59E0B", "Niedrig": "#22C55E"}
TABS = [
    ("dashboard", "📊 Dashboard"), ("team", "👥 Team-Übersicht"), ("archive", "🗄️ Ehemalige"),
    ("applicants", "📋 Bewerber"), ("wishes", "💡 Teamwünsche"),
    ("warnings", "⚠️ Verwarnungen"), ("absences", "📅 Abmeldungen"), ("tasks", "✅ Aufgaben"),
    ("protocols", "📝 Protokolle"), ("notes", "📌 Notizen"), ("settings", "⚙️ Einstellungen"),
    ("accounts", "🔑 Benutzer & Rechte"), ("discord", "🔔 Discord"),
]


def rank_color(r):
    if r == "Owner": return "#A855F7"
    if r == "Developer": return "#FFFFFF"
    if "Projektleitung" in r: return "#FF69B4"
    if "Teamleitung" in r: return "#FF7B00"
    if "Administrator" in r: return "#FF2A2A"
    if "Moderator" in r: return "#3B82F6"
    return "#EAB308"


def uid(): return uuid.uuid4().hex


@st.cache_resource
def _b64(path):
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()


def logo_html(width):
    if not os.path.exists(LOGO): return ""
    return f"<img class='logo' src='data:image/jpeg;base64,{_b64(LOGO)}' style='width:{width}px'>"


def skyline_uri(color):
    """Los-Santos-Skyline mit Palmen als dezenter Hintergrund (wie im Logo)."""
    rnd, parts, x = random.Random(7), [], 0
    while x < 1600:
        w, h = rnd.randint(40, 90), rnd.randint(60, 190)
        parts.append(f"<rect x='{x}' y='{260 - h}' width='{w}' height='{h}'/>")
        for _ in range(3):
            parts.append(f"<rect x='{x + rnd.randint(6, w - 14)}' y='{260 - h + rnd.randint(8, h - 20)}' width='5' height='7' fill-opacity='.55'/>")
        x += w + rnd.randint(2, 10)
    for px in (120, 560, 1010, 1450):
        parts.append(f"<rect x='{px}' y='150' width='6' height='110'/><ellipse cx='{px + 3}' cy='148' rx='38' ry='10'/>"
                     f"<ellipse cx='{px + 3}' cy='142' rx='10' ry='30'/>")
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1600 260' preserveAspectRatio='none'>"
           f"<g fill='{color}' fill-opacity='0.16'>{''.join(parts)}</g></svg>")
    return "data:image/svg+xml;utf8," + quote(svg)


def chip(text, color):
    return f"<span class='chip' style='color:{color};border-color:{color}'>{esc(text)}</span>"


def badge(r):
    c = rank_color(r)
    return (f"<span class='rank-badge' style='color:{c};border:1px solid {c};border-radius:999px;padding:2px 10px;"
            f"font-weight:bold;font-size:13px'>{'👑 ' if r == 'Owner' else ''}{esc(r)}</span>")


def fmt(s):
    try: return date.fromisoformat(s).strftime("%d.%m.%Y")
    except Exception: return s or "-"


# --- DISCORD (Webhooks + Bot für Rollen) ---
DC_CFG_FILE = "discord_config.json"  # getrennt von den Teamdaten, damit Token nicht im Backup landen
DISCORD_API = "https://discord.com/api/v10"
DC_HOOKS = {"team": "👥 Team-Updates", "protocols": "📝 Protokolle", "warnings": "⚠️ Verwarnungen", "absences": "📅 Abmeldungen"}
DC_HOOK_RE = re.compile(r"^https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/(?:v\d+/)?webhooks/\d+/[\w-]+$")
DC_ERR = {0: "Keine Verbindung zu Discord.", 401: "Bot-Token ungültig.",
          403: "Bot darf die Rolle nicht vergeben (Recht „Rollen verwalten“ fehlt oder Bot-Rolle steht nicht über der Zielrolle).",
          404: "Mitglied nicht auf dem Server oder Server-/Rollen-ID falsch."}


@st.cache_resource
def _dc_log(): return []


def dc_cfg():
    cfg = {"webhooks": {}, "bot_token": "", "guild_id": "", "roles": {}, "sync_roles": False}
    try:
        with open(DC_CFG_FILE, encoding="utf-8") as f: cfg.update(json.load(f))
    except Exception: pass
    return cfg


def dc_save(cfg):
    tmp = DC_CFG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=2, ensure_ascii=False)
    try: os.chmod(tmp, 0o600)
    except Exception: pass
    os.replace(tmp, DC_CFG_FILE)


def _dc_request(method, url, payload=None, token=None):
    h = {"Content-Type": "application/json", "User-Agent": "DiscordBot (https://wolflife.local, 1.0)"}
    if token: h["Authorization"] = f"Bot {token}"
    data = json.dumps(payload).encode() if payload is not None else b""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method=method), timeout=8) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")[:150]
    except Exception as e:
        return 0, str(e)[:150]


def dc_embed(title, color, fields=(), desc=""):
    e = {"title": title[:250], "color": color, "timestamp": datetime.now(timezone.utc).isoformat(),
         "footer": {"text": "Wolf Life Team Suite"}}
    if desc: e["description"] = desc[:3500] + ("…" if len(desc) > 3500 else "")
    if fields: e["fields"] = [{"name": n[:250], "value": (str(v) or "-")[:1000], "inline": len(str(v)) < 40} for n, v in fields]
    return e


def dc_post(hook, embed, cfg, log):
    url = cfg["webhooks"].get(hook, "")
    if not url: return None
    code, err = _dc_request("POST", url, {"embeds": [embed], "allowed_mentions": {"parse": []}})
    ok = code in (200, 204)
    log.append((datetime.now().strftime("%d.%m. %H:%M:%S"), DC_HOOKS[hook], "✅ gesendet" if ok else f"❌ {code} {err}"))
    del log[:-30]
    return ok, code, err


def dc_send(hook, title, color, fields=(), desc=""):
    """Nachricht im Hintergrund senden, damit die Seite nicht wartet."""
    cfg, log = dc_cfg(), _dc_log()
    if cfg["webhooks"].get(hook):
        threading.Thread(target=dc_post, args=(hook, dc_embed(title, color, fields, desc), cfg, log), daemon=True).start()


def dc_mention(m):
    d = str(m.get("discord_id", "-"))
    return f"<@{d}> ({m['name']})" if d.isdigit() else m["name"]


def dc_sync_role(discord_id, old, new):
    cfg = dc_cfg()
    tok = os.environ.get("DISCORD_BOT_TOKEN") or cfg["bot_token"]
    if not (cfg["sync_roles"] and tok and cfg["guild_id"]): return None
    if not str(discord_id).isdigit():
        return "⚠️ Rang geändert, aber Discord-Rolle nicht angepasst: Beim Mitglied fehlt eine gültige Discord-ID (Zahl)."
    new_r, old_r = cfg["roles"].get(new, ""), cfg["roles"].get(old, "")
    if not new_r: return f"⚠️ Rang geändert, aber für „{new}“ ist keine Discord-Rolle zugeordnet."
    base, log, errs = f"{DISCORD_API}/guilds/{cfg['guild_id']}/members/{discord_id}/roles", _dc_log(), []
    for method, rid in ([("DELETE", old_r)] if old_r and old_r != new_r else []) + [("PUT", new_r)]:
        code, err = _dc_request(method, f"{base}/{rid}", token=tok)
        ok = code in (200, 204)
        log.append((datetime.now().strftime("%d.%m. %H:%M:%S"), "Rollen-Sync", "✅ ok" if ok else f"❌ {code} {err}"))
        if not ok: errs.append(DC_ERR.get(code, f"Fehler {code}."))
    del log[:-30]
    return "✅ Discord-Rolle angepasst." if not errs else "⚠️ Discord-Rolle nicht (vollständig) angepasst: " + " ".join(dict.fromkeys(errs))


# --- DATEN (atomar speichern, gesperrt, mit Backup) ---
@st.cache_resource
def _lock(): return threading.Lock()


DEFAULTS = {"members": [], "applicants": [], "warnings": [], "absences": [], "tasks": [],
            "protocols": [], "notes": "", "users": [], "log": [], "settings": {}, "archive": [], "wishes": [], "task_ideas": []}


def load_data():
    d = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, encoding="utf-8") as f: d = json.load(f)
        except Exception:
            shutil.copy(DATA_FILE, f"{DATA_FILE}.defekt-{int(time.time())}")
            st.error("Die Datendatei ist beschädigt. Eine Kopie wurde gesichert – bitte Datei prüfen.")
            st.stop()
    for k, v in DEFAULTS.items(): d.setdefault(k, json.loads(json.dumps(v)))
    return d


def save_data(d):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(d, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)
    b = f"{DATA_FILE}.backup-{date.today()}"
    if not os.path.exists(b): shutil.copy(DATA_FILE, b)


@contextmanager
def edit(action=None):
    """Lädt frische Daten, lässt sie ändern und speichert – verhindert überschriebene Änderungen."""
    with _lock():
        d = load_data()
        yield d
        if action:
            u = st.session_state.user["username"] if st.session_state.get("user") else "-"
            d["log"] = (d["log"] + [{"ts": datetime.now().isoformat(timespec="seconds"), "user": u, "action": action}])[-500:]
        save_data(d)


def update(coll, iid, label, **ch):
    with edit(label) as d:
        for x in d[coll]:
            if x["id"] == iid: x.update(ch)
    st.rerun()


def remove(coll, iid, label):
    with edit(label) as d: d[coll] = [x for x in d[coll] if x["id"] != iid]
    st.rerun()


@st.cache_resource
def _fails(): return {}


def locked(name):
    return _fails().get(name.strip().lower(), (0, 0))[1] > time.time()


def register_fail(name):
    k = name.strip().lower()
    n = _fails().get(k, (0, 0))[0] + 1
    _fails()[k] = (0, time.time() + 300) if n >= 5 else (n, 0)


# --- PASSWÖRTER & LOGIN ---
def hash_pw(pw, salt=None):
    salt = salt or secrets.token_bytes(16)
    return salt.hex() + "$" + hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1).hex()


def check_pw(pw, stored):
    try: return hmac.compare_digest(hash_pw(pw, bytes.fromhex(stored.split("$")[0])), stored)
    except Exception: return False


def authenticate(name, pw):
    u = next((x for x in load_data()["users"] if x["username"].lower() == name.strip().lower()), None)
    if not u:
        hash_pw(pw)
        return None
    ok = False
    if u.get("pw_hash"):
        ok = check_pw(pw, u["pw_hash"])
    elif u.get("password") is not None and hmac.compare_digest(str(u["password"]).encode(), pw.encode()):
        ok = True
        with edit() as d:
            for x in d["users"]:
                if x["username"] == u["username"]:
                    x["pw_hash"] = hash_pw(pw)
                    x.pop("password", None)
    return u if ok else None


def set_password(username, new_pw, label):
    with edit(label) as d:
        for x in d["users"]:
            if x["username"] == username:
                x["pw_hash"] = hash_pw(new_pw)
                x.pop("password", None)


# --- SESSION, THEME, CSS ---
ss = st.session_state
ss.setdefault("user", None)
data = load_data()
uname = ss.user["username"] if ss.user else None
tname = data["settings"].get("themes", {}).get(uname) or DEFAULT_THEME
t = dict(THEMES.get(tname, THEMES[DEFAULT_THEME]))
t["ACCENT_RGB"] = ",".join(str(int(t["ACCENT"][i:i + 2], 16)) for i in (1, 3, 5))
t["SKY"] = skyline_uri(t["ACCENT"])

CSS = """
.stApp{background:url("@SKY") bottom center/100% 240px no-repeat fixed,radial-gradient(ellipse 70% 45% at 88% -8%,rgba(@ACCENT_RGB,.20),transparent 60%),radial-gradient(ellipse 60% 40% at 0% 100%,rgba(@ACCENT_RGB,.09),transparent 60%),@BG_MAIN;color:@TEXT_MAIN;font-family:'Segoe UI',Tahoma,sans-serif}
[data-testid=stHeader]{background:transparent}
.block-container{padding-top:2rem;max-width:1400px}
#MainMenu,footer{visibility:hidden}
[data-testid=stSidebar]{background:linear-gradient(180deg,@BG_SIDEBAR,@BG_MAIN);border-right:1px solid rgba(@ACCENT_RGB,.35);box-shadow:4px 0 28px rgba(@ACCENT_RGB,.08);min-width:280px!important}
h1,h2,h3,h4,h5,h6,p,label,span:not([style*="color"]){color:@TEXT_MAIN!important}
.stApp h1{font-weight:900!important;letter-spacing:1px;text-transform:uppercase;text-shadow:0 2px 0 rgba(0,0,0,.6),0 0 24px rgba(@ACCENT_RGB,.55);padding-bottom:8px;border-bottom:3px solid @ACCENT;display:inline-block;margin-bottom:.5rem!important}
.block-container h3::before{content:"◢ ";color:@ACCENT!important;font-size:.8em}
hr{border:none!important;height:1px!important;background:linear-gradient(90deg,transparent,@ACCENT,transparent)!important;opacity:.6}
.logo{display:block;margin:0 auto 10px;max-width:100%;border-radius:18px;box-shadow:0 0 30px rgba(@ACCENT_RGB,.45),0 0 0 1px rgba(255,255,255,.08)}
.tagline{letter-spacing:.35em;font-weight:700;font-size:13px;color:@ACCENT!important;margin:14px 0 18px;text-transform:uppercase}
.metric-card,.content-box{position:relative;overflow:hidden;background:linear-gradient(225deg,rgba(@ACCENT_RGB,.6) 50%,transparent 50%) top right/26px 26px no-repeat,linear-gradient(135deg,rgba(255,255,255,.05),rgba(255,255,255,0) 45%),@BG_CARD;border:1px solid rgba(255,255,255,.08);border-left:4px solid @ACCENT;border-radius:6px 18px 6px 18px;padding:14px 20px;box-shadow:0 4px 12px rgba(0,0,0,.3);margin-bottom:6px;transition:transform .15s,box-shadow .15s}
.content-box:hover,.metric-card:hover{transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,0,0,.4),0 0 18px rgba(@ACCENT_RGB,.18)}
.metric-card{border-left-width:1px;border-top:3px solid @ACCENT}
.metric-card::after{content:"🐺";position:absolute;right:12px;bottom:-8px;font-size:62px;opacity:.08}
.metric-title{font-size:13px;color:@TEXT_MUTED!important;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px}
.metric-value{font-size:34px!important;font-weight:800;text-shadow:0 0 18px rgba(@ACCENT_RGB,.55)}
.content-box .muted,.muted{color:@TEXT_MUTED!important;font-size:12px}
.chip{border:1px solid;border-radius:999px;padding:1px 9px;font-size:12px;font-weight:600;white-space:nowrap}
[data-testid=stExpander],[data-testid=stExpander] details,[data-testid=stExpander] summary,[data-testid=stExpanderDetails]{background:@BG_CARD!important;color:@TEXT_MAIN!important}
[data-testid=stExpander]{border:1px solid rgba(@ACCENT_RGB,.25)!important;border-radius:6px 16px 6px 16px!important;overflow:hidden!important}
[data-testid=stForm]{background:@BG_CARD;border:1px solid rgba(@ACCENT_RGB,.30)!important;border-radius:6px 18px 6px 18px;box-shadow:0 0 30px rgba(@ACCENT_RGB,.10)}
[data-testid=stAlert],[data-testid=stNotification]{background:@BG_CARD!important;border:1px solid rgba(255,255,255,.1)!important;border-left:4px solid @ACCENT!important;border-radius:6px 14px 6px 14px!important}
[data-testid=stAlert] *,[data-testid=stNotification] *{color:@TEXT_MAIN!important;background:transparent!important}
[data-testid=stAlert]:has([data-testid=stAlertContentWarning]){border-left-color:#F59E0B!important}
[data-testid=stAlert]:has([data-testid=stAlertContentError]){border-left-color:#EF4444!important}
[data-testid=stAlert]:has([data-testid=stAlertContentSuccess]){border-left-color:#22C55E!important}
input,textarea,select,div[data-baseweb=input],div[data-baseweb=select],div[data-baseweb=base-input],span[data-baseweb=tag],ul[data-baseweb=menu],li[data-baseweb=option],div[data-baseweb=popover],li[role=option]{background:@BG_INPUT!important;color:@TEXT_MAIN!important;border-color:rgba(255,255,255,.1)!important}
input:focus,textarea:focus{box-shadow:0 0 0 1px @ACCENT!important}
li[role=option]:hover{background:@ACCENT!important}
.stButton>button,[data-testid=stFormSubmitButton] button,[data-testid=stDownloadButton] button,button[kind=secondaryFormSubmit]{background:linear-gradient(180deg,@ACCENT,@ACCENT_HOVER)!important;color:#fff!important;border:none!important;border-radius:4px 12px 4px 12px!important;font-weight:700!important;letter-spacing:.3px;box-shadow:0 2px 10px rgba(@ACCENT_RGB,.35);transition:all .15s}
.stButton>button:hover,[data-testid=stFormSubmitButton] button:hover,[data-testid=stDownloadButton] button:hover{filter:brightness(1.12);transform:translateY(-1px);box-shadow:0 4px 18px rgba(@ACCENT_RGB,.55)}

/* --- POPOVER-BUTTONS (GRAUER HINTERGRUND) --- */
[data-testid=stPopover] button {
    background: @BG_CARD !important;
    color: @TEXT_MAIN !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 6px 14px 6px 14px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,.3) !important;
}
[data-testid=stPopover] button:hover {
    background: @BG_INPUT !important;
    border-color: @ACCENT !important;
    color: @TEXT_MAIN !important;
}

.nav-group{display:flex;align-items:center;gap:8px;font-size:11px;font-weight:800;letter-spacing:.2em;color:@TEXT_MUTED!important;margin:20px 0 6px 6px;text-transform:uppercase}
.nav-group::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,rgba(@ACCENT_RGB,.55),transparent)}
.user-card{display:flex;align-items:center;gap:12px;padding:12px;margin:6px 0 4px;border-radius:6px 16px 6px 16px;background:linear-gradient(135deg,rgba(255,255,255,.06),rgba(255,255,255,0)),@BG_CARD;border:1px solid rgba(@ACCENT_RGB,.30)}
.avatar{width:42px;height:42px;flex:none;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;color:#fff;background:linear-gradient(135deg,@ACCENT,@ACCENT_HOVER);box-shadow:0 0 14px rgba(@ACCENT_RGB,.5)}
[data-testid=stSidebar] .stButton>button{background:transparent!important;box-shadow:none!important;border:1px solid transparent!important;border-radius:4px 14px 4px 14px!important;padding:.55rem .9rem!important;transition:all .15s}
[data-testid=stSidebar] .stButton>button>div{justify-content:flex-start!important;width:100%}
[data-testid=stSidebar] .stButton>button p{text-align:left!important;color:@TEXT_MUTED!important;font-weight:600!important;font-size:15px!important}
[data-testid=stSidebar] .stButton>button:hover{background:rgba(@ACCENT_RGB,.13)!important;border-color:rgba(@ACCENT_RGB,.35)!important;transform:translateX(4px);filter:none!important;box-shadow:none!important}
[data-testid=stSidebar] .stButton>button:hover p{color:@TEXT_MAIN!important}
[data-testid=stSidebar] button[kind=primary],[data-testid=stSidebar] [data-testid=stBaseButton-primary]{background:linear-gradient(90deg,rgba(@ACCENT_RGB,.45),rgba(@ACCENT_RGB,.06))!important;border-left:4px solid @ACCENT!important;box-shadow:0 0 18px rgba(@ACCENT_RGB,.22)!important}
[data-testid=stSidebar] button[kind=primary] p,[data-testid=stSidebar] [data-testid=stBaseButton-primary] p{color:#fff!important;font-weight:800!important}
[data-testid=stSidebar] .st-key-logout button{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.12)!important}
[data-testid=stSidebar] .st-key-logout button>div{justify-content:center!important}
[data-testid=stSidebar] .st-key-logout button p{text-align:center!important}
[data-testid=stSidebar] .st-key-logout button:hover{background:rgba(239,68,68,.25)!important;border-color:#EF4444!important;transform:none}
[data-testid=stPopoverBody]{min-width:360px;background:@BG_CARD!important;color:@TEXT_MAIN!important;border:1px solid rgba(@ACCENT_RGB,.35)!important;border-radius:6px 18px 6px 18px!important}
div[data-baseweb=select] div{background:@BG_INPUT!important;color:@TEXT_MAIN!important}
div[data-baseweb=select] svg{fill:@TEXT_MAIN!important}
::-webkit-scrollbar{width:8px}::-webkit-scrollbar-thumb{background:@BG_INPUT;border-radius:4px}
"""
for k in sorted(t, key=len, reverse=True): CSS = CSS.replace("@" + k, t[k])
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# --- DYNAMISCHE THEME-HINTERGRÜNDE (THEMES_BG ORDNER) ---
THEME_BG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes_bg")

def get_theme_bg_style(current_theme_name):
    if not os.path.exists(THEME_BG_FOLDER):
        return ""
    
    expected_file = THEME_BG_MAP.get(current_theme_name)
    matching_path = None
    
    if expected_file:
        # Prüfe exakten Dateinamen sowie alternative Bildendungen (.png, .jpeg, .webp)
        base_name = os.path.splitext(expected_file)[0]
        for ext in (".jpg", ".png", ".jpeg", ".webp", ".JPG", ".PNG"):
            candidate = os.path.join(THEME_BG_FOLDER, base_name + ext)
            if os.path.exists(candidate):
                matching_path = candidate
                break

    if not matching_path:
        return ""

    encoded = _b64(matching_path)
    ext = os.path.splitext(matching_path)[1].lower()
    mime_type = "image/png" if ext == ".png" else ("image/webp" if ext == ".webp" else "image/jpeg")
    
    return f"""
    .stApp {{
        background: linear-gradient(rgba(13, 13, 17, 0.85), rgba(13, 13, 17, 0.85)), 
                    url("data:{mime_type};base64,{encoded}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}
    """

theme_bg_css = get_theme_bg_style(tname)
if theme_bg_css:
    st.markdown(f"<style>{theme_bg_css}</style>", unsafe_allow_html=True)


def show(h, cls=""): st.markdown(f"<div class='content-box {cls}'>{h}</div>", unsafe_allow_html=True)


# --- ERSTEINRICHTUNG & LOGIN ---
if not any(u.get("is_admin") for u in data["users"]):
    c = st.columns([1, 1.2, 1])[1]
    with c.form("setup"):
        st.subheader("🐺 Ersteinrichtung")
        st.caption("Lege den ersten Administrator an.")
        n = st.text_input("Benutzername")
        p1 = st.text_input("Passwort (min. 3 Zeichen)", type="password")
        p2 = st.text_input("Passwort wiederholen", type="password")
        if st.form_submit_button("Administrator anlegen", use_container_width=True):
            if len(n.strip()) < 3 or len(p1) < 3 or p1 != p2:
                st.error("Benutzername min. 3 Zeichen, Passwort min. 3 Zeichen, beide Passwörter gleich.")
            else:
                with edit("Administrator angelegt") as d:
                    d["users"].append({"username": n.strip(), "pw_hash": hash_pw(p1), "is_admin": True, "permissions": {}})
                st.rerun()
    st.stop()

if not any(u.get("is_owner") for u in data["users"]):
    _first = next(u for u in data["users"] if u.get("is_admin"))
    with edit("Alpha-Owner festgelegt") as d:
        for x in d["users"]:
            if x["username"] == _first["username"]: x["is_owner"] = True
    st.rerun()

if not ss.user:
    c = st.columns([1, 1.2, 1])[1]
    c.markdown(f"<div style='text-align:center'>{logo_html(340) or '<h2>🐺 WOLF LIFE</h2>'}"
               "<div class='tagline'>Team Management Suite</div></div>", unsafe_allow_html=True)
    with c.form("login"):
        n = st.text_input("Benutzername")
        p = st.text_input("Passwort", type="password")
        if st.form_submit_button("Anmelden", use_container_width=True):
            if locked(n):
                st.error("Zu viele Fehlversuche. Bitte 5 Minuten warten.")
            else:
                u = authenticate(n, p)
                if u:
                    ss.user = {"username": u["username"], "is_admin": bool(u.get("is_admin")),
                               "permissions": u.get("permissions") or {}}
                    st.rerun()
                register_fail(n)
                st.error("Falscher Benutzername oder falsches Passwort!")
    st.stop()

# --- SIDEBAR ---
rec = next((x for x in data["users"] if x["username"] == ss.user["username"]), None)
if not rec:  # Benutzer wurde gelöscht
    ss.user = None
    st.rerun()
ss.user["is_admin"] = bool(rec.get("is_admin"))
ss.user["permissions"] = rec.get("permissions") or {}
ss.user["is_owner"] = bool(rec.get("is_owner"))
user = ss.user
is_admin = user["is_admin"]
is_owner = user["is_owner"]


def mode_of(key):
    if key == "discord": return "full" if is_owner else "hidden"  # nur Alpha-Owner
    if is_admin or key == "settings": return "full"
    if key == "accounts": return "hidden"
    return user["permissions"].get(key, DEF_PERM.get(key, "hidden"))


st.sidebar.markdown(f"{logo_html(230) or '<h2>🐺 WOLF LIFE</h2>'}<div class='tagline' style='text-align:center;font-size:11px;margin:4px 0 14px'>Los Santos · Team Suite</div>",
                    unsafe_allow_html=True)
visible = [(k, l) for k, l in TABS if mode_of(k) != "hidden"]
if ss.get("page") not in [k for k, _ in visible]: ss.page = visible[0][0]
st.sidebar.markdown(f"<div class='user-card'><div class='avatar'>{esc(user['username'][:1].upper())}</div>"
                    f"<div><strong>{esc(user['username'])}</strong>"
                    f"<div class='muted'>{'Alpha-Owner' if is_owner else 'Administrator' if is_admin else 'Teammitglied'}</div></div></div>",
                    unsafe_allow_html=True)
counts = {"applicants": sum(x.get("status") not in ("Angenommen", "Abgelehnt") for x in data["applicants"]),
          "tasks": sum(x.get("status") != "Erledigt" for x in data["tasks"]),
          "wishes": sum(w.get("status") == "Neu" for w in data["wishes"])}
NAV_GROUPS = [("Übersicht", ["dashboard"]), ("Team", ["team", "archive", "applicants", "wishes"]),
              ("Verwaltung", ["warnings", "absences", "tasks", "protocols", "notes"]),
              ("System", ["settings", "accounts", "discord"])]
for grp, grp_keys in NAV_GROUPS:
    items = [(k, l) for k, l in visible if k in grp_keys]
    if not items: continue
    st.sidebar.markdown(f"<div class='nav-group'>{grp}</div>", unsafe_allow_html=True)
    for k, l in items:
        n = counts.get(k, 0)
        if st.sidebar.button(f"{l}  ·  {n}" if n else l, key=f"nav_{k}",
                             type="primary" if ss.page == k else "secondary", use_container_width=True):
            ss.page = k
            st.rerun()
key = ss.page
perm_mode = mode_of(key)
can_write = perm_mode in ("full", "absence_own") if key == "absences" else (perm_mode == "full")
if perm_mode == "readonly": st.sidebar.markdown(chip("👁 Nur-Lesen", "#F59E0B"), unsafe_allow_html=True)
elif perm_mode == "absence_own": st.sidebar.markdown(chip("👤 Nur eigene Abmeldungen", "#3B82F6"), unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔒 Abmelden", key="logout", use_container_width=True):
    ss.user = None
    st.rerun()


def delete_btn(coll, iid, what):
    if can_write and st.button("🗑 Löschen", key=f"del_{coll}_{iid}"): remove(coll, iid, f"{what} gelöscht")


member_names = [m["name"] for m in sorted(data["members"], key=lambda m: RANKS.index(m["rank"]) if m["rank"] in RANKS else 99)]
rank_of = {m["name"]: m["rank"] for m in data["members"]}


def mlabel(n): return f"{n} ({rank_of[n]})" if n in rank_of else n


def flash(msg, kind="info"): ss.setdefault("flash", []).append((kind, msg))


def rank_change(m, new, did):
    old = m["rank"]
    up = RANKS.index(new) < RANKS.index(old) if old in RANKS and new in RANKS else None
    title = "⬆️ Uprank" if up else "⬇️ Downrank" if up is False else "🔄 Rangänderung"
    color = 0x22C55E if up else 0xEF4444 if up is False else 0x3B82F6
    dc_send("team", f"{title}: {m['name']}", color, [("Mitglied", dc_mention({**m, "discord_id": did or "-"})),
            ("Alter Rang", old), ("Neuer Rang", new), ("Durchgeführt von", user["username"])])
    res = dc_sync_role(did, old, new)
    if res: flash(res, "success" if res.startswith("✅") else "warning")

for _k, _msg in ss.pop("flash", []): getattr(st, _k)(_msg)

# --- DASHBOARD ---
if key == "dashboard":
    st.title("📊 Dashboard & Live-Statistiken")
    st.caption(f"Willkommen zurück, {user['username']}! Heute ist der {date.today().strftime('%d.%m.%Y')}.")
    open_apps = sum(a.get("status") not in ("Angenommen", "Abgelehnt") for a in data["applicants"])
    open_tasks = sum(x.get("status") != "Erledigt" for x in data["tasks"])
    stats = [("Teammitglieder", len(data["members"])), ("Offene Bewerbungen", open_apps),
             ("Verwarnungen", len(data["warnings"])), ("Offene Aufgaben", open_tasks)]
    for col, (title, val) in zip(st.columns(4), stats):
        col.markdown(f"<div class='metric-card'><div class='metric-title'>{title}</div>"
                     f"<div class='metric-value'>{val}</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🛡️ Rang-Verteilung")
        rows = "".join(f"<div style='margin-bottom:10px'>{badge(r)} <strong>× {len(ms)}</strong><div class='muted' style='margin-top:4px'>{', '.join(esc(m['name']) for m in ms)}</div></div>"
                       for r in RANKS if (ms := [m for m in data["members"] if m["rank"] == r]))
        show(rows or "<span class='muted'>Noch keine Teammitglieder eingetragen.</span>")
    with c2:
        st.subheader("📅 Aktuelle Abmeldungen")

        def still_active(a):
            try: return date.fromisoformat(a["to_date"]) >= date.today()
            except Exception: return True

        act = [a for a in data["absences"] if still_active(a)][-6:]
        show("".join(f"<div><strong>{esc(mlabel(a['name']))}</strong> ({fmt(a['from_date'])} ➔ {fmt(a['to_date'])}): "
                     f"<em>{esc(a['reason'])}</em></div>" for a in act)
             or "<span class='muted'>Keine aktuellen Abmeldungen.</span>")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("✅ Offene Aufgaben")
        ot = sorted([x for x in data["tasks"] if x["status"] != "Erledigt"],
                    key=lambda x: PRIOS.index(x["priority"]) if x["priority"] in PRIOS else 9)[:6]
        show("".join(f"<div style='margin-bottom:6px'>{chip(x['priority'], PRIO_COL.get(x['priority'], '#9CA3AF'))} {esc(x['title'])} "
                     f"<span class='muted'>– {esc(x['assignee'])}</span></div>" for x in ot)
             or "<span class='muted'>Keine offenen Aufgaben. 🎉</span>")
    with c4:
        st.subheader("🧪 In der Probezeit")
        pm = [m for m in data["members"] if m["status"] == "Probezeit"]
        show("".join(f"<div style='margin-bottom:6px'><strong>{esc(m['name'])}</strong> {badge(m['rank'])}</div>" for m in pm)
             or "<span class='muted'>Niemand in der Probezeit.</span>")

# --- TEAM ---
elif key == "team":
    st.title("👥 Team-Übersicht & Kader")
    if can_write:
        with st.expander("➕ Neues Teammitglied hinzufügen"):
            with st.form("add_member", clear_on_submit=True):
                a, b, c, e = st.columns(4)
                n = a.text_input("Discord Name / Tag")
                did = b.text_input("Discord-ID (Zahl, für Rollen-Sync)")
                r = c.selectbox("Rang", RANKS)
                s = e.selectbox("Status", MEMBER_STATUS)
                if st.form_submit_button("Mitglied hinzufügen", use_container_width=True):
                    n = n.strip()
                    if not n: st.warning("Bitte einen Namen eingeben.")
                    elif n.lower() in [x.lower() for x in member_names]: st.warning("Dieses Mitglied existiert bereits.")
                    else:
                        with edit(f"Mitglied {n} hinzugefügt") as d:
                            d["members"].append({"id": uid(), "name": n, "discord_id": did.strip() or "-", "rank": r,
                                                 "status": s, "joined": date.today().isoformat()})
                        st.rerun()
    def warn_txt(n):
        c = sum(w["member"] == n or w["member"].startswith(n + " (") for w in data["warnings"])
        return f" | ⚠️ {c} Verwarnung(en)" if c else ""

    f1, f2 = st.columns([3, 1])
    q = f1.text_input("🔍 Mitglied suchen...").lower()
    sf = f2.selectbox("Status", ["Alle"] + MEMBER_STATUS)
    shown = [m for m in data["members"] if q in m["name"].lower() and sf in ("Alle", m["status"])]

    for m in sorted(shown, key=lambda m: RANKS.index(m["rank"]) if m["rank"] in RANKS else 99):
        card_content = (f"<div style='display:flex;justify-content:space-between;align-items:center;width:100%'>"
                        f"<div><strong>{esc(m['name'])}</strong> {chip(m['status'], STATUS_COL.get(m['status'], '#9CA3AF'))}<br>"
                        f"<span class='muted'>ID: {esc(m['discord_id'])} | Seit: {fmt(m.get('joined'))}{warn_txt(m['name'])}</span></div>"
                        f"<div style='display:flex;align-items:center;gap:12px;'>{badge(m['rank'])}</div></div>")
        
        if can_write:
            col_card, col_btn = st.columns([11, 1])
            with col_card:
                show(card_content, "member-card")
            with col_btn:
                st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
                with st.popover("✏️"):
                    st.markdown(f"### ✏️ {esc(m['name'])} bearbeiten")
                    a, b = st.columns(2)
                    nr = a.selectbox("Rang", RANKS, index=RANKS.index(m["rank"]) if m["rank"] in RANKS else 0, key=f"r{m['id']}")
                    ns = b.selectbox("Status", MEMBER_STATUS, index=MEMBER_STATUS.index(m["status"]) if m["status"] in MEMBER_STATUS else 0, key=f"s{m['id']}")
                    nid = st.text_input("Discord-ID (Zahl, für Rollen-Sync)", value="" if m.get("discord_id", "-") == "-" else m["discord_id"], key=f"did{m['id']}")
                    if st.button("💾 Speichern", key=f"sv{m['id']}"):
                        if nr != m["rank"]: rank_change(m, nr, nid.strip())
                        update("members", m["id"], f"{m['name']}: {nr}/{ns}", rank=nr, status=ns, discord_id=nid.strip() or "-")
                    st.markdown("---")
                    st.markdown("**Aus dem Team entfernen**")
                    why = st.text_input("Grund (Pflicht)", key=f"why{m['id']}")
                    if st.button("🚪 Entfernen & archivieren", key=f"rm{m['id']}"):
                        if not why.strip(): st.warning("Bitte einen Grund angeben.")
                        else:
                            with edit(f"{m['name']} aus dem Team entfernt") as d:
                                d["members"] = [x for x in d["members"] if x["id"] != m["id"]]
                                d["archive"].append({"id": uid(), "name": m["name"], "discord_id": m.get("discord_id", "-"),
                                                     "rank": m["rank"], "joined": m.get("joined", ""),
                                                     "removed": date.today().isoformat(), "reason": why.strip(),
                                                     "removed_by": user["username"]})
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            show(card_content, "member-card")

# --- EHEMALIGE ---
elif key == "archive":
    st.title("🗄️ Ehemalige Teammitglieder")
    st.caption("Hier steht, wer aus dem Team entfernt wurde und warum.")
    qa = st.text_input("🔍 Ehemalige suchen...").lower()
    items = [a for a in data["archive"] if qa in a["name"].lower()]
    if not items: st.info("Keine Einträge vorhanden.")
    for a in reversed(items):
        show(f"<div style='display:flex;justify-content:space-between'><div><strong>{esc(a['name'])}</strong><br>"
             f"<span class='muted'>ID: {esc(a['discord_id'])} | Im Team seit: {fmt(a['joined'])}</span></div>"
             f"<div>{badge(a['rank'])}</div></div>"
             f"<div style='margin-top:12px'><strong>Entfernt am {fmt(a['removed'])}</strong> von {esc(a['removed_by'])}</div>"
             f"<div style='white-space:pre-wrap;margin-top:4px'>{esc(a['reason'])}</div>")
        delete_btn("archive", a["id"], f"Archiv-Eintrag {a['name']}")

# --- BEWERBER ---
elif key == "applicants":
    st.title("📋 Bewerber & Testphase")
    if can_write:
        with st.expander("➕ Neue Bewerbung erfassen"):
            with st.form("add_app", clear_on_submit=True):
                a, b, c = st.columns(3)
                n = a.text_input("Discord Name / Tag")
                role = b.selectbox("Rolle", list(APP_ROLES))
                stat = c.selectbox("Status", APP_STATUS)
                notes = st.text_area("Notizen")
                if st.form_submit_button("Speichern", use_container_width=True):
                    if n.strip():
                        with edit(f"Bewerbung {n.strip()} erfasst") as d:
                            d["applicants"].append({"id": uid(), "name": n.strip(), "role": role, "status": stat,
                                                    "notes": notes, "date": date.today().isoformat()})
                        st.rerun()
                    else: st.warning("Bitte einen Namen eingeben.")
    for ap in reversed(data["applicants"]):
        past = [a for a in data["archive"] if a["name"].lower() == ap["name"].lower()]
        hint = "".join(f"<div style='color:#EF4444;margin-top:6px'>⚠️ Ehemaliges Mitglied – entfernt am {fmt(a['removed'])}: {esc(a['reason'])}</div>" for a in past)
        note = f"<p><em>Notiz: {esc(ap['notes'])}</em></p>" if ap.get("notes") else ""
        show(f"<h3>{esc(ap['name'])} <span style='font-size:14px;color:{t['ACCENT']}'>({esc(ap['status'])})</span></h3>"
             f"<p><strong>Rolle:</strong> {esc(ap['role'])} | <strong>Datum:</strong> {fmt(ap['date'])}</p>{note}{hint}")
        if can_write:
            with st.expander(f"✏️ {ap['name']} bearbeiten"):
                ns = st.selectbox("Status", APP_STATUS, index=APP_STATUS.index(ap["status"]) if ap["status"] in APP_STATUS else 0, key=f"as{ap['id']}")
                if st.button("💾 Status speichern", key=f"asv{ap['id']}"):
                    update("applicants", ap["id"], f"Bewerbung {ap['name']} → {ns}", status=ns)
                if ap["status"] == "Angenommen" and ap["name"].lower() not in [x.lower() for x in member_names]:
                    if st.button("👥 Als Mitglied (Probezeit) übernehmen", key=f"adopt{ap['id']}"):
                        with edit(f"{ap['name']} ins Team übernommen") as d:
                            d["members"].append({"id": uid(), "name": ap["name"], "discord_id": "-",
                                                 "rank": APP_ROLES.get(ap["role"], "Test-Supporter"),
                                                 "status": "Probezeit", "joined": date.today().isoformat()})
                        st.rerun()
                delete_btn("applicants", ap["id"], f"Bewerbung {ap['name']}")

# --- VERWARNUNGEN ---
elif key == "warnings":
    st.title("⚠️ Verwarnungen & Strikes")
    if can_write:
        with st.expander("➕ Verwarnung eintragen"):
            if not member_names: st.info("Zuerst Teammitglieder anlegen.")
            else:
                with st.form("add_warn", clear_on_submit=True):
                    wm = st.selectbox("Mitglied", member_names, format_func=mlabel)
                    wl = st.selectbox("Stufe", ["Mündliche Verwarnung", "1. Verwarnung (Strike 1)", "2. Verwarnung (Strike 2)", "Letzte Warnung (Strike 3)"])
                    wr = st.text_input("Grund")
                    if st.form_submit_button("Eintragen", use_container_width=True):
                        if wr.strip():
                            with edit(f"Verwarnung für {wm}") as d:
                                d["warnings"].append({"id": uid(), "member": wm, "level": wl, "reason": wr.strip(),
                                                      "issuer": user["username"], "date": date.today().isoformat()})
                            dc_send("warnings", f"⚠️ Verwarnung: {wm}", 0xEF4444,
                                    [("Mitglied", dc_mention(next((x for x in data["members"] if x["name"] == wm), {"name": wm}))),
                                     ("Stufe", wl), ("Grund", wr.strip()), ("Ausgestellt von", user["username"])])
                            st.rerun()
                        else: st.warning("Bitte einen Grund angeben.")
    for w in reversed(data["warnings"]):
        show(f"<strong>{esc(mlabel(w['member']))}</strong> | {chip(w['level'], '#EF4444' if 'Strike 3' in w['level'] else '#F97316' if 'Strike' in w['level'] else '#EAB308')} (Von: {esc(w['issuer'])}, {fmt(w.get('date'))})"
             f"<br>Grund: {esc(w['reason'])}")
        delete_btn("warnings", w["id"], "Verwarnung")

# --- ABMELDUNGEN ---
elif key == "absences":
    st.title("📅 Abmeldungen & Urlaub")
    if perm_mode in ("full", "absence_own"):
        with st.expander("➕ Abmeldung erfassen"):
            if not member_names: st.info("Zuerst Teammitglieder anlegen.")
            else:
                with st.form("add_abs", clear_on_submit=True):
                    if perm_mode == "absence_own":
                        match_m = next((m for m in member_names if m.lower() == user["username"].lower()), member_names[0] if member_names else "")
                        am = st.selectbox("Mitglied", [match_m] if match_m else member_names, format_func=mlabel)
                        st.caption(f"ℹ️ Du kannst als '{user['username']}' nur deine eigene Abmeldung eintragen.")
                    else:
                        am = st.selectbox("Mitglied", member_names, format_func=mlabel)
                    
                    c1, c2 = st.columns(2)
                    af = c1.date_input("Von", value=date.today(), format="DD.MM.YYYY")
                    at = c2.date_input("Bis", value=date.today(), format="DD.MM.YYYY")
                    ar = st.text_input("Grund")
                    if st.form_submit_button("Speichern", use_container_width=True):
                        if at < af: st.warning("„Bis“ darf nicht vor „Von“ liegen.")
                        else:
                            with edit(f"Abmeldung {am}") as d:
                                d["absences"].append({"id": uid(), "name": am, "from_date": af.isoformat(),
                                                      "to_date": at.isoformat(), "reason": ar})
                            dc_send("absences", f"📅 Abmeldung: {am}", 0xF59E0B,
                                    [("Mitglied", dc_mention(next((x for x in data["members"] if x["name"] == am), {"name": am}))),
                                     ("Von", fmt(af.isoformat())), ("Bis", fmt(at.isoformat())), ("Grund", ar or "-")])
                            st.rerun()
                            
    for a in reversed(data["absences"]):
        show(f"<strong>{esc(mlabel(a['name']))}</strong> ({fmt(a['from_date'])} ➔ {fmt(a['to_date'])})<br>Grund: {esc(a['reason'])}")
        can_del_this = (perm_mode == "full") or (perm_mode == "absence_own" and a['name'].lower() == user['username'].lower())
        if can_del_this:
            if st.button("🗑 Löschen", key=f"del_abs_{a['id']}"): 
                remove("absences", a["id"], "Abmeldung gelöscht")

# --- AUFGABEN ---
elif key == "tasks":
    st.title("✅ Aufgaben-Board")
    if can_write:
        with st.expander("➕ Neue Aufgabe erstellen"):
            with st.form("add_task", clear_on_submit=True):
                tt = st.text_input("Beschreibung")
                tp = st.selectbox("Priorität", PRIOS)
                who = st.multiselect("Zuständig", member_names, format_func=mlabel)
                if st.form_submit_button("Erstellen", use_container_width=True):
                    if tt.strip():
                        with edit("Aufgabe erstellt") as d:
                            d["tasks"].append({"id": uid(), "title": tt.strip(), "assignee": ", ".join(who) or "Team",
                                               "priority": tp, "status": "Offen"})
                        st.rerun()
                    else: st.warning("Bitte eine Beschreibung eingeben.")
    order = lambda x: (x["status"] == "Erledigt", PRIOS.index(x["priority"]) if x["priority"] in PRIOS else 9)
    for x in sorted(data["tasks"], key=order):
        done = x["status"] == "Erledigt"
        who_txt = ", ".join(mlabel(n.strip()) for n in x["assignee"].split(","))
        title = f"<s>{esc(x['title'])}</s>" if done else esc(x["title"])
        show(f"{chip(x['priority'], PRIO_COL.get(x['priority'], '#9CA3AF'))} <strong>{title}</strong><br>Zuständig: {esc(who_txt)} | Status: {esc(x['status'])}")
        if can_write:
            a, b, _ = st.columns([1, 1, 4])
            if a.button("↩ Wieder öffnen" if done else "✔ Erledigt", key=f"tg{x['id']}"):
                update("tasks", x["id"], f"Aufgabe „{x['title']}“", status="Offen" if done else "Erledigt")
            if b.button("🗑 Löschen", key=f"del_tasks_{x['id']}"): remove("tasks", x["id"], "Aufgabe gelöscht")

    st.markdown("---")
    st.subheader("💡 Aufgabenvorschläge")
    linked = rec.get("member") or next((n for n in rank_of if n.lower() == user["username"].lower()), "")
    can_approve = is_owner or rank_of.get(linked) in TASK_APPROVER_RANKS
    st.caption("Jeder kann Aufgaben vorschlagen. Übernehmen oder ablehnen dürfen: " + ", ".join(TASK_APPROVER_RANKS) + ".")
    with st.expander("➕ Aufgabe vorschlagen"):
        with st.form("add_idea", clear_on_submit=True):
            it = st.text_input("Vorschlag (kurz und knapp)")
            idesc = st.text_area("Beschreibung (optional)", height=90)
            if st.form_submit_button("Vorschlag einreichen", use_container_width=True):
                if it.strip():
                    with edit(f"Aufgabenvorschlag „{it.strip()}“") as d:
                        d["task_ideas"].append({"id": uid(), "title": it.strip(), "description": idesc.strip(),
                                                "author": user["username"], "date": date.today().isoformat(),
                                                "status": "Offen", "handled_by": "", "note": ""})
                    st.rerun()
                else: st.warning("Bitte einen Titel eingeben.")
    open_ideas = [i for i in data["task_ideas"] if i["status"] == "Offen"]
    if not open_ideas: st.info("Keine offenen Vorschläge.")
    for i in reversed(open_ideas):
        desc = f"<div style='white-space:pre-wrap;margin-top:8px'>{esc(i['description'])}</div>" if i.get("description") else ""
        show(f"<strong>{esc(i['title'])}</strong> {chip('Vorschlag', '#3B82F6')}<br>"
             f"<span class='muted'>von {esc(i['author'])} | {fmt(i['date'])}</span>{desc}")
        b1, b2, b3, _ = st.columns([2, 2, 2, 4])
        if can_approve:
            with b1.popover("✅ Übernehmen"):
                pr = st.selectbox("Priorität", PRIOS, index=1, key=f"ip{i['id']}")
                who = st.multiselect("Zuständig", member_names, format_func=mlabel, key=f"iw{i['id']}")
                if st.button("Als Aufgabe anlegen", key=f"ia{i['id']}"):
                    with edit(f"Vorschlag „{i['title']}“ übernommen") as d:
                        d["tasks"].append({"id": uid(), "title": i["title"], "assignee": ", ".join(who) or "Team",
                                           "priority": pr, "status": "Offen"})
                        for x in d["task_ideas"]:
                            if x["id"] == i["id"]: x.update(status="Angenommen", handled_by=user["username"])
                    st.rerun()
            with b2.popover("❌ Ablehnen"):
                nt = st.text_input("Grund (optional)", key=f"in{i['id']}")
                if st.button("Vorschlag ablehnen", key=f"ir{i['id']}"):
                    update("task_ideas", i["id"], f"Vorschlag „{i['title']}“ abgelehnt", status="Abgelehnt",
                           handled_by=user["username"], note=nt.strip())
        if (can_approve or i["author"] == user["username"]) and b3.button("🗑 Löschen", key=f"id{i['id']}"):
            remove("task_ideas", i["id"], "Aufgabenvorschlag")
    handled = [i for i in data["task_ideas"] if i["status"] != "Offen"][-8:]
    if handled:
        show("<strong>Zuletzt bearbeitet</strong>" + "".join(
            f"<div style='margin-top:6px'>{chip(i['status'], '#22C55E' if i['status'] == 'Angenommen' else '#9CA3AF')} {esc(i['title'])} "
            f"<span class='muted'>– von {esc(i['author'])}, bearbeitet von {esc(i['handled_by'])}"
            f"{(' · ' + esc(i['note'])) if i.get('note') else ''}</span></div>" for i in reversed(handled)))

# --- PROTOKOLLE ---
elif key == "protocols":
    st.title("📝 Teamsitzungs-Protokolle")
    if can_write:
        with st.expander("➕ Neues Protokoll"):
            with st.form("add_proto", clear_on_submit=True):
                pt = st.text_input("Titel")
                pp = st.text_input("Teilnehmer")
                pc = st.text_area("Inhalt", value="1. Begrüßung:\n\n2. Themen:\n\n3. Beschlüsse:", height=200)
                if st.form_submit_button("Speichern", use_container_width=True):
                    if pt.strip():
                        with edit(f"Protokoll „{pt.strip()}“") as d:
                            d["protocols"].append({"id": uid(), "title": pt.strip(), "participants": pp,
                                                   "date": datetime.now().strftime("%d.%m.%Y %H:%M"), "content": pc})
                        dc_send("protocols", f"📝 Neues Protokoll: {pt.strip()}", 0x3B82F6,
                                [("Teilnehmer", pp or "-"), ("Erstellt von", user["username"])], pc)
                        st.rerun()
                    else: st.warning("Bitte einen Titel eingeben.")
    for p in reversed(data["protocols"]):
        show(f"<h3>{esc(p['title'])}</h3><p class='muted'>Erstellt: {esc(p['date'])} | Teilnehmer: {esc(p['participants'])}</p>"
             f"<pre style='white-space:pre-wrap;background:transparent;border:none;color:{t['TEXT_MAIN']}'>{esc(p['content'])}</pre>")
        delete_btn("protocols", p["id"], "Protokoll")

# --- TEAMWÜNSCHE ---
elif key == "wishes":
    st.title("💡 Teamwünsche")
    st.caption("Was soll an dieser Seite besser werden? Reiche Wünsche ein und stimme für Ideen anderer ab.")
    manage, me = perm_mode == "full", user["username"]
    with st.expander("➕ Neuen Wunsch einreichen"):
        with st.form("add_wish", clear_on_submit=True):
            wt = st.text_input("Titel (kurz und knapp)")
            wc = st.selectbox("Kategorie", WISH_CATS)
            wd = st.text_area("Beschreibung (optional)", height=100)
            if st.form_submit_button("Wunsch einreichen", use_container_width=True):
                if wt.strip():
                    with edit(f"Wunsch „{wt.strip()}“ eingereicht") as d:
                        d["wishes"].append({"id": uid(), "title": wt.strip(), "category": wc, "description": wd.strip(),
                                            "author": me, "date": date.today().isoformat(), "status": "Neu",
                                            "votes": [me], "answer": ""})
                    st.rerun()
                else: st.warning("Bitte einen Titel eingeben.")
    f1, f2 = st.columns(2)
    sf = f1.selectbox("Status", ["Alle", "Offen"] + WISH_STATUS)
    cf = f2.selectbox("Kategorie ", ["Alle"] + WISH_CATS)
    ws = [w for w in data["wishes"] if (sf == "Alle" or w["status"] == sf or (sf == "Offen" and w["status"] in WISH_OPEN))
          and cf in ("Alle", w["category"])]
    ws.sort(key=lambda w: (w["status"] not in WISH_OPEN, -len(w["votes"])))
    if not ws: st.info("Noch keine Wünsche vorhanden – sei der Erste! 💡")
    for w in ws:
        mine = me in w["votes"]
        desc = f"<div style='white-space:pre-wrap;margin-top:8px'>{esc(w['description'])}</div>" if w.get("description") else ""
        ans = (f"<div style='margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,.12)'>"
               f"<strong>Antwort vom Team:</strong> {esc(w['answer'])}</div>") if w.get("answer") else ""
        show(f"<div style='display:flex;justify-content:space-between;gap:12px'><div>"
             f"<strong style='font-size:17px'>{esc(w['title'])}</strong> {chip(w['status'], WISH_COL.get(w['status'], '#9CA3AF'))} "
             f"{chip(w['category'], '#9CA3AF')}<br><span class='muted'>von {esc(w['author'])} | {fmt(w['date'])}</span></div>"
             f"<div style='text-align:center;min-width:60px;margin-right:18px'><div class='metric-value' style='font-size:26px!important'>{len(w['votes'])}</div>"
             f"<div class='muted'>Stimmen</div></div></div>{desc}{ans}")
        b1, b2, _ = st.columns([2, 2, 6])
        if b1.button("↩ Stimme zurückziehen" if mine else "👍 Dafür", key=f"vote_{w['id']}"):
            with edit() as d:
                for x in d["wishes"]:
                    if x["id"] == w["id"]:
                        x["votes"] = [v for v in x["votes"] if v != me] if mine else x["votes"] + [me]
            st.rerun()
        if manage or (w["author"] == me and w["status"] == "Neu"):
            with b2.popover("✏️ Verwalten"):
                if manage:
                    ns = st.selectbox("Status", WISH_STATUS, index=WISH_STATUS.index(w["status"]) if w["status"] in WISH_STATUS else 0, key=f"ws{w['id']}")
                    na = st.text_area("Antwort vom Team", value=w.get("answer", ""), key=f"wa{w['id']}", height=90)
                    if st.button("💾 Speichern", key=f"wsv{w['id']}"):
                        update("wishes", w["id"], f"Wunsch „{w['title']}“ → {ns}", status=ns, answer=na.strip())
                if st.button("🗑 Wunsch löschen", key=f"wdel{w['id']}"): remove("wishes", w["id"], f"Wunsch „{w['title']}“")

# --- DISCORD ---
elif key == "discord":
    st.title("🔔 Discord-Anbindung")
    if not is_owner:
        st.error("Kein Zugriff.")
        st.stop()
    cfg = dc_cfg()
    st.caption("Webhooks schicken Nachrichten in je einen Channel. Für das automatische Ändern von Discord-Rollen wird zusätzlich ein Bot benötigt.")
    with st.expander("📖 Einrichtung"):
        st.markdown("""
**Webhook:** Channel → Einstellungen → Integrationen → Webhooks → Neuer Webhook → URL kopieren (pro Bereich ein Channel möglich).

**Bot (nur für Rollen):** [Developer Portal](https://discord.com/developers/applications) → Neue Application → *Bot* → Token kopieren.
Bot mit dem Recht **Rollen verwalten** auf den Server einladen. Seine Rolle muss in der Rollenliste **über** allen Rängen stehen, die er vergeben soll.

**IDs:** In Discord unter Einstellungen → Erweitert den *Entwicklermodus* aktivieren. Dann Rechtsklick auf Server, Rolle oder Person → *ID kopieren*.

Tipp: Den Token kannst du statt hier auch als Umgebungsvariable `DISCORD_BOT_TOKEN` setzen.
""")
    with st.form("dc_cfg"):
        st.subheader("Webhooks")
        hooks = {k: st.text_input(lbl, value=cfg["webhooks"].get(k, ""), placeholder="https://discord.com/api/webhooks/…") for k, lbl in DC_HOOKS.items()}
        st.subheader("Bot & Rollen-Sync")
        sync = st.checkbox("Discord-Rolle bei Rangänderung automatisch anpassen", value=bool(cfg["sync_roles"]))
        c1, c2 = st.columns(2)
        gid = c1.text_input("Server-ID", value=cfg["guild_id"])
        tok = c2.text_input("Bot-Token" + (" (gespeichert, leer lassen = behalten)" if cfg["bot_token"] else ""), type="password")
        st.subheader("Rang → Discord-Rollen-ID")
        rc = st.columns(3)
        roles = {r: rc[i % 3].text_input(r, value=cfg["roles"].get(r, ""), key=f"dcr_{i}") for i, r in enumerate(RANKS)}
        if st.form_submit_button("💾 Speichern", use_container_width=True):
            hooks = {k: v.strip() for k, v in hooks.items()}
            roles = {k: v.strip() for k, v in roles.items()}
            if any(v and not DC_HOOK_RE.match(v) for v in hooks.values()):
                st.error("Ungültige Webhook-URL. Sie muss eine discord.com-Webhook-Adresse sein.")
            elif any(v and not v.isdigit() for v in [gid.strip(), *roles.values()]):
                st.error("Server- und Rollen-IDs bestehen nur aus Ziffern.")
            else:
                cfg.update(webhooks=hooks, sync_roles=sync, guild_id=gid.strip(), roles=roles)
                if tok.strip(): cfg["bot_token"] = tok.strip()
                dc_save(cfg)
                st.success("Gespeichert.")
    st.subheader("🧪 Testnachricht senden")
    for col, (k, lbl) in zip(st.columns(4), DC_HOOKS.items()):
        if col.button(lbl, key=f"dct_{k}", use_container_width=True):
            r = dc_post(k, dc_embed("🧪 Testnachricht", 0x3B82F6, [("Von", user["username"])]), cfg, _dc_log())
            if r is None: st.warning(f"Für „{lbl}“ ist noch keine Webhook-URL gespeichert.")
            elif r[0]: st.success(f"„{lbl}“: Nachricht gesendet.")
            else: st.error(f"„{lbl}“: {DC_ERR.get(r[1], 'Fehler')} ({r[1]})")
    st.subheader("📜 Letzte Sendungen")
    show("".join(f"<div class='muted'>{esc(t)} – <strong>{esc(w)}</strong>: {esc(r)}</div>" for t, w, r in reversed(_dc_log()[-15:]))
         or "<span class='muted'>Noch nichts gesendet.</span>")

# --- NOTIZEN ---
elif key == "notes":
    st.title("📌 Notizen")
    val = st.text_area("Notizblock", value=data["notes"], height=350, disabled=not can_write)
    if can_write and st.button("💾 Speichern"):
        with edit("Notizen aktualisiert") as d: d["notes"] = val
        st.success("Gespeichert!")

# --- EINSTELLUNGEN ---
elif key == "settings":
    st.title("⚙️ Einstellungen & Design")
    names = list(THEMES)
    sel = st.selectbox("Dein Farbschema", names, index=names.index(tname) if tname in names else 0)
    if st.button("🎨 Theme anwenden"):
        with edit() as d: d["settings"].setdefault("themes", {})[user["username"]] = sel
        st.rerun()
    st.markdown("---")
    st.subheader("🔐 Passwort ändern")
    with st.form("pw"):
        old = st.text_input("Aktuelles Passwort", type="password")
        new = st.text_input("Neues Passwort (min. 3 Zeichen)", type="password")
        if st.form_submit_button("Passwort ändern"):
            if authenticate(user["username"], old) and len(new) >= 3:
                set_password(user["username"], new, "Passwort geändert")
                st.success("Passwort geändert.")
            else: st.error("Aktuelles Passwort falsch oder neues Passwort zu kurz (min. 3 Zeichen).")

# --- BENUTZER & RECHTE ---
elif key == "accounts":
    st.title("🔑 Benutzer & Rechte")
    if not is_admin:
        st.error("Nur für Administratoren.")
        st.stop()
    with st.expander("➕ Benutzer anlegen"):
        with st.form("add_user", clear_on_submit=True):
            un = st.text_input("Benutzername")
            up = st.text_input("Start-Passwort (min. 3 Zeichen)", type="password")
            ua = st.checkbox("Administrator (voller Zugriff)")
            uo = st.checkbox("Alpha-Owner (Zugriff auf den Discord-Reiter)") if is_owner else False
            cols = st.columns(3)
            perms = {k: cols[i % 3].selectbox(l, PERM_OPTS, format_func=lambda x: PERM_LABELS[x], index=1, key=f"p_{k}")
                     for i, (k, l) in enumerate(TABS) if k not in ("accounts", "settings", "discord")}
            if st.form_submit_button("Anlegen", use_container_width=True):
                if len(un.strip()) < 3 or len(up) < 3: st.error("Benutzername min. 3, Passwort min. 3 Zeichen.")
                elif un.strip().lower() in [u["username"].lower() for u in data["users"]]: st.error("Benutzername existiert bereits.")
                else:
                    with edit(f"Benutzer {un.strip()} angelegt") as d:
                        d["users"].append({"username": un.strip(), "pw_hash": hash_pw(up), "is_admin": ua or uo, "is_owner": uo, "permissions": perms})
                    st.rerun()
    for u in data["users"]:
        with st.expander(f"{u['username']} {'(Alpha-Owner)' if u.get('is_owner') else '(Administrator)' if u.get('is_admin') else ''}"):
            if u.get("is_owner") and not is_owner:
                st.info("🔒 Alpha-Owner-Konto: kann nur von einem Alpha-Owner verwaltet werden.")
                continue
            new_uname = st.text_input("Benutzername ändern", value=u["username"], key=f"nu_{u['username']}")
            if st.button("✏️ Namen speichern", key=f"su_{u['username']}"):
                new_clean = new_uname.strip()
                if len(new_clean) < 3:
                    st.error("Benutzername muss mindestens 3 Zeichen lang sein.")
                elif new_clean.lower() != u["username"].lower() and new_clean.lower() in [x["username"].lower() for x in data["users"]]:
                    st.error("Dieser Benutzername ist bereits vergeben.")
                else:
                    with edit(f"Benutzername von {u['username']} in {new_clean} geändert") as d:
                        for x in d["users"]:
                            if x["username"] == u["username"]:
                                x["username"] = new_clean
                    if ss.user["username"] == u["username"]:
                        ss.user["username"] = new_clean
                    st.success("Benutzername erfolgreich aktualisiert!")
                    st.rerun()

            st.markdown("---")
            is_self = u["username"] == user["username"]
            adm = st.checkbox("Administrator (voller Zugriff)", value=bool(u.get("is_admin")),
                              disabled=is_self, key=f"adm_{u['username']}")
            ow = (st.checkbox("Alpha-Owner (übergeordnet, einziger Zugriff auf den Discord-Reiter)", value=bool(u.get("is_owner")),
                              disabled=is_self, key=f"own_{u['username']}") if is_owner else bool(u.get("is_owner")))
            lm_opts = ["–"] + member_names
            lm = st.selectbox("Verknüpftes Teammitglied (für rangabhängige Rechte)", lm_opts,
                              index=lm_opts.index(u["member"]) if u.get("member") in lm_opts else 0,
                              format_func=lambda n: n if n == "–" else mlabel(n), key=f"lm_{u['username']}")
            cur = u.get("permissions") or {}
            pc = st.columns(3)
            newp = {k: pc[i % 3].selectbox(l, PERM_OPTS, format_func=lambda x: PERM_LABELS[x],
                                           index=PERM_OPTS.index(cur.get(k, DEF_PERM.get(k, "hidden"))) if cur.get(k, DEF_PERM.get(k, "hidden")) in PERM_OPTS else 2,
                                           key=f"ep_{u['username']}_{k}")
                    for i, (k, l) in enumerate(TABS) if k not in ("accounts", "settings", "discord")}
            if st.button("💾 Rechte speichern", key=f"sp_{u['username']}"):
                with edit(f"Rechte von {u['username']} geändert") as d:
                    for x in d["users"]:
                        if x["username"] == u["username"]:
                            x["permissions"] = newp
                            x["is_admin"] = adm or ow
                            x["member"] = "" if lm == "–" else lm
                            if is_owner: x["is_owner"] = ow
                st.success("Rechte gespeichert.")
            st.markdown("---")
            np_ = st.text_input("Neues Passwort setzen (min. 3 Zeichen)", type="password", key=f"np_{u['username']}")
            if st.button("🔑 Passwort zurücksetzen", key=f"rp_{u['username']}"):
                if len(np_) >= 3:
                    set_password(u["username"], np_, f"Passwort von {u['username']} zurückgesetzt")
                    st.success("Passwort gesetzt.")
                else: st.error("Mindestens 3 Zeichen.")
            if u["username"] != user["username"] and st.button("🗑 Benutzer löschen", key=f"du_{u['username']}"):
                with edit(f"Benutzer {u['username']} gelöscht") as d:
                    d["users"] = [x for x in d["users"] if x["username"] != u["username"]]
                st.rerun()
    bk = {k: v for k, v in data.items() if k != "users"}
    st.download_button("💾 Backup herunterladen (ohne Benutzerkonten)", json.dumps(bk, indent=2, ensure_ascii=False),
                       file_name=f"wolflife_backup_{date.today()}.json", mime="application/json")
    st.subheader("🧾 Aktivitätslog (letzte 30)")
    show("".join(f"<div class='muted'>{esc(e['ts'].replace('T', ' '))} – <strong>{esc(e['user'])}</strong>: {esc(e['action'])}</div>"
                 for e in reversed(data["log"][-30:])) or "<span class='muted'>Noch keine Einträge.</span>")
