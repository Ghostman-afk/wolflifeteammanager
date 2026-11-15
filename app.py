import streamlit as st
import json, os, uuid, time, hmac, hashlib, secrets, threading, shutil, base64, random
import re, urllib.request, urllib.error
from urllib.parse import quote
from contextlib import contextmanager
from datetime import datetime, date, timedelta, timezone
import calendar as _cal
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
SHIFT_TYPES = ["Support-Dienst", "Ticket-Schicht", "Ingame-Präsenz", "Teamsitzung", "Einweisung / Training", "Server-Event"]
SHIFT_COL = {"Support-Dienst": "#3B82F6", "Ticket-Schicht": "#06B6D4", "Ingame-Präsenz": "#22C55E",
             "Teamsitzung": "#A855F7", "Einweisung / Training": "#F59E0B", "Server-Event": "#EF4444"}
PERM_OPTS = ["full", "readonly", "absence_own", "hidden"]
MIN_PW = 8
PERM_LABELS = {"full": "Vollzugriff", "readonly": "Nur-Lesen", "absence_own": "Eigene Abmeldung", "hidden": "Versteckt"}
STATUS_COL = {"Aktiv": "#22C55E", "Probezeit": "#F59E0B", "Abgemeldet": "#9CA3AF"}
PRIO_COL = {"Hoch": "#EF4444", "Mittel": "#F59E0B", "Niedrig": "#22C55E"}

TABS = [
    ("dashboard", "📊 Dashboard"), ("team", "👥 Team-Übersicht"), ("archive", "🗄️ Ehemalige"),
    ("applicants", "📋 Bewerber"), ("calendar", "🗓️ Dienstplan & Kalender"),
    ("warnings", "⚠️ Verwarnungen"), ("absences", "📅 Abmeldungen"), ("tasks", "✅ Aufgaben"),
    ("protocols", "📝 Protokolle"), ("notes", "📌 Notizen"), ("settings", "⚙️ Einstellungen"),
    ("accounts", "🔑 Benutzer & Rechte"),
]

WEBHOOK_CHANNELS = [
    ("absences", "📅 Abmeldungen-Channel"),
    ("applicants", "📋 Bewerber-Channel"),
    ("warnings", "⚠️ Verwarnungen-Channel"),
    ("team", "👥 Team- & Kader-Channel"),
    ("general", "📢 Allgemein (Aufgaben, Protokolle & Dienstplan)"),
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
def _bg_b64(path):
    """Hintergrundbild verkleinern (max. 1600 px, JPEG), damit nicht jede Seite mehrere MB mitschleppt."""
    try:
        import io
        from PIL import Image
        im = Image.open(path).convert("RGB")
        im.thumbnail((1600, 1600))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=70, optimize=True)
        return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"
    except Exception:
        ext = os.path.splitext(path)[1].lower()
        return _b64(path), ("image/png" if ext == ".png" else "image/webp" if ext == ".webp" else "image/jpeg")


@st.cache_resource
def _b64(path):
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()


def logo_html(width):
    if not os.path.exists(LOGO): return ""
    return f"<img class='logo' src='data:image/jpeg;base64,{_b64(LOGO)}' style='width:{width}px'>"


def skyline_uri(color):
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


MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def parse_d(sv, default=None):
    try: return date.fromisoformat(sv)
    except Exception: return default


def prob_days(): return int(data["settings"].get("probation_days", 14))


def prob_start(m): return parse_d(m.get("probation_start") or m.get("joined"), date.today())


def prob_end(m): return parse_d(m.get("probation_end")) or prob_start(m) + timedelta(days=prob_days())


def days_left(m): return (prob_end(m) - date.today()).days


def probation_info(m):
    s0, e0, left = prob_start(m), prob_end(m), days_left(m)
    total, passed = max((e0 - s0).days, 1), max(0, (date.today() - s0).days)
    pct = min(100, int(passed / total * 100))
    if left < 0: col, lbl = "#EF4444", f"⏰ Probezeit seit {-left} Tag(en) überfällig – Entscheidung nötig!"
    elif left == 0: col, lbl = "#F59E0B", "⏳ Probezeit endet heute"
    elif left <= 3: col, lbl = "#F59E0B", f"⏳ Endspurt: noch {left} Tag(e) (bis {fmt(e0.isoformat())})"
    else: col, lbl = "#3B82F6", f"🧪 Tag {passed} von {total} (bis {fmt(e0.isoformat())})"
    return passed, pct, col, lbl


def check_probation():
    """Erinnerung in den Team-Channel, wenn eine Probezeit in ≤ 3 Tagen endet (läuft beim Öffnen der App)."""
    if not _dc_url("team"): return
    due = lambda m: m["status"] == "Probezeit" and days_left(m) <= 3 and not m.get("prob_reminded")
    if not any(due(m) for m in data["members"]): return
    with edit() as dd:
        soon = [m for m in dd["members"] if due(m)]
        for m in soon: m["prob_reminded"] = True
    for m in soon:
        left, e0 = days_left(m), prob_end(m)
        send_discord_embed("team", "⏰ Probezeit abgelaufen" if left < 0 else "⏳ Probezeit endet bald",
                           f"{dc_mention(m)} – bitte entscheiden: Probezeit **bestanden** oder **verlängern**?",
                           color_hex="#EF4444" if left < 0 else "#F59E0B",
                           fields=[{"name": "🛡️ Rang", "value": m["rank"]}, {"name": "📆 Ende", "value": fmt(e0.isoformat())},
                                   {"name": "📅 Im Team seit", "value": fmt(m.get("joined"))}], author_name="System")


def hl(text, terms):
    out = esc(text)
    if terms:
        out = re.sub("(" + "|".join(re.escape(esc(t)) for t in terms) + ")",
                     lambda mo: f"<mark style='background:rgba(255,255,255,.22);color:#fff;border-radius:3px;padding:0 2px'>{mo.group(1)}</mark>",
                     out, flags=re.I)
    return out


# --- DATEN (atomar speichern, gesperrt, mit Backup) ---
@st.cache_resource
def _lock(): return threading.Lock()


DEFAULTS = {"members": [], "applicants": [], "warnings": [], "absences": [], "tasks": [],
            "protocols": [], "schedules": [], "notes": "", "users": [], "log": [], "settings": {}, "archive": []}


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
    import glob
    for old_b in sorted(glob.glob(DATA_FILE + ".backup-*"))[:-14]:  # nur die letzten 14 Tagesbackups behalten
        try: os.remove(old_b)
        except OSError: pass


@contextmanager
def edit(action=None):
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


# --- DISCORD (Webhooks + Bot) – Konfiguration liegt getrennt von den Teamdaten ---
DC_CFG_FILE = "discord_config.json"
DISCORD_API = "https://discord.com/api/v10"
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
    tok = os.environ.get("DISCORD_BOT_TOKEN") or token
    if tok: h["Authorization"] = f"Bot {tok}"
    body = json.dumps(payload).encode() if payload is not None else b""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=h, method=method), timeout=8) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")[:150]
    except Exception as e:
        return 0, str(e)[:150]


def _dc_log_add(log, what, ok, code, err):
    log.append((datetime.now().strftime("%d.%m. %H:%M:%S"), what, "✅ ok" if ok else f"❌ {code} {err}"))
    del log[:-30]


def _dc_payload(title, description, color_hex, fields, author_name):
    try: color = int(str(color_hex).lstrip("#"), 16)
    except Exception: color = 0xEF4444
    e = {"title": str(title)[:256], "description": str(description)[:4000], "color": color,
         "timestamp": datetime.now(timezone.utc).isoformat(),
         "footer": {"text": f"🐺 Wolf Life Team-Suite • Ausgeführt von {author_name or 'System'}"[:2000]}}
    if fields:
        e["fields"] = [{"name": (str(f["name"]) or "-")[:256], "value": (str(f["value"]).strip() or "-")[:1024],
                        "inline": f.get("inline", True)} for f in fields[:25]]
    return {"username": "Wolf Life • Team-Management", "embeds": [e], "allowed_mentions": {"parse": []}}


def _dc_thread(url, payload, label, log):
    code, err = _dc_request("POST", url, payload)
    _dc_log_add(log, label, code in (200, 204), code, err)


def _dc_url(channel_key, cfg=None):
    hooks = (cfg or dc_cfg())["webhooks"]
    url = (hooks.get(channel_key) or hooks.get("general") or "").strip()
    return url if DC_HOOK_RE.match(url) else ""


def send_discord_embed(channel_key, title, description, color_hex="#EF4444", fields=None, author_name=None):
    """Sendet ein Embed im Hintergrund (blockiert die Seite nicht); Ergebnis steht im Sendeprotokoll."""
    url = _dc_url(channel_key)
    if url:
        threading.Thread(target=_dc_thread, args=(url, _dc_payload(title, description, color_hex, fields, author_name),
                                                  f"Kanal „{channel_key}“", _dc_log()), daemon=True).start()


def dc_test(channel_key, author_name):
    url = _dc_url(channel_key)
    if not url: return None
    code, err = _dc_request("POST", url, _dc_payload("🧪 Testnachricht", "Dieser Channel ist mit der **Wolf Life Team-Suite** verbunden.",
                                                     "#3B82F6", [{"name": "📡 Status", "value": "Online & bereit"}], author_name))
    _dc_log_add(_dc_log(), f"Test „{channel_key}“", code in (200, 204), code, err)
    return code in (200, 204), code


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
        code, err = _dc_request(method, f"{base}/{rid}", token=cfg["bot_token"])
        _dc_log_add(log, "Rollen-Sync", code in (200, 204), code, err)
        if code not in (200, 204): errs.append(DC_ERR.get(code, f"Fehler {code}."))
    return "✅ Discord-Rolle angepasst." if not errs else "⚠️ Discord-Rolle nicht (vollständig) angepasst: " + " ".join(dict.fromkeys(errs))


def rank_title(old, new):
    if old == new: return "🔄 Statusänderung", "#3B82F6"
    up = RANKS.index(new) < RANKS.index(old) if old in RANKS and new in RANKS else None
    return ("⬆️ Uprank", "#22C55E") if up else ("⬇️ Downrank", "#EF4444") if up is False else ("🔄 Rangänderung", "#3B82F6")


def perm_opts(k): return PERM_OPTS if k == "absences" else [o for o in PERM_OPTS if o != "absence_own"]


def perm_cur(cur, k):
    v = cur.get(k, "hidden")
    return "readonly" if v == "absence_own" and k != "absences" else v


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
if data["settings"].get("webhooks"):  # Migration: Webhook-URLs raus aus den Teamdaten
    _c = dc_cfg()
    _c["webhooks"] = {**data["settings"]["webhooks"], **_c["webhooks"]}
    dc_save(_c)
    with edit() as _d: _d["settings"].pop("webhooks", None)
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
[data-testid=stSidebar]{background:linear-gradient(180deg,@BG_SIDEBAR,@BG_MAIN);border-right:1px solid rgba(@ACCENT_RGB,.35);box-shadow:4px 0 28px rgba(@ACCENT_RGB,.08);min-width:290px!important}
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
.prob-bar-bg{width:100%;height:8px;background:rgba(255,255,255,.1);border-radius:999px;overflow:hidden;margin-top:6px}
.prob-bar-fill{height:100%;border-radius:999px;transition:width .3s ease}
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
.cal{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px;margin:10px 0 14px}
.cal-h{text-align:center;font-weight:800;font-size:12px;letter-spacing:.1em;color:@TEXT_MUTED;padding:4px 0;text-transform:uppercase}
.cal-d{min-height:96px;background:@BG_CARD;border:1px solid rgba(255,255,255,.08);border-radius:4px 12px 4px 12px;padding:6px 7px;font-size:11.5px;overflow:hidden}
.cal-d.today{border-color:@ACCENT;box-shadow:0 0 14px rgba(@ACCENT_RGB,.45)}
.cal-d.off{opacity:.35}
.cal-n{font-weight:800;color:@TEXT_MUTED;margin-bottom:3px}
.cal-i{background:rgba(255,255,255,.06);border-radius:3px;padding:1px 5px;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
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
        base_name = os.path.splitext(expected_file)[0]
        for ext in (".jpg", ".png", ".jpeg", ".webp", ".JPG", ".PNG"):
            candidate = os.path.join(THEME_BG_FOLDER, base_name + ext)
            if os.path.exists(candidate):
                matching_path = candidate
                break
    if not matching_path:
        return ""
    encoded, mime_type = _bg_b64(matching_path)
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
        p1 = st.text_input(f"Passwort (min. {MIN_PW} Zeichen)", type="password")
        p2 = st.text_input("Passwort wiederholen", type="password")
        if st.form_submit_button("Administrator anlegen", use_container_width=True):
            if len(n.strip()) < 3 or len(p1) < MIN_PW or p1 != p2:
                st.error(f"Benutzername min. 3 Zeichen, Passwort min. {MIN_PW} Zeichen, beide Passwörter gleich.")
            else:
                with edit("Administrator angelegt") as d:
                    d["users"].append({"username": n.strip(), "pw_hash": hash_pw(p1), "is_admin": True, "permissions": {}})
                st.rerun()
    st.stop()

if not any(u.get("is_owner") for u in data["users"]):  # erster Administrator wird Alpha-Owner
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
if time.time() - ss.get("last_seen", time.time()) > 8 * 3600:
    ss.user = None
    ss.pop("last_seen", None)
    st.rerun()
ss["last_seen"] = time.time()
rec = next((x for x in data["users"] if x["username"] == ss.user["username"]), None)
if not rec:
    ss.user = None
    st.rerun()
ss.user["is_admin"] = bool(rec.get("is_admin"))
ss.user["permissions"] = rec.get("permissions") or {}
ss.user["is_owner"] = bool(rec.get("is_owner"))
user = ss.user
is_admin, is_owner = user["is_admin"], user["is_owner"]
my_member = rec.get("member") or next((m["name"] for m in data["members"] if m["name"].lower() == user["username"].lower()), "")
my_rank = next((m["rank"] for m in data["members"] if m["name"] == my_member), None)


def mode_of(key):
    if is_admin or key == "settings": return "full"
    if key == "accounts": return "hidden"
    return user["permissions"].get(key, "hidden")


st.sidebar.markdown(f"{logo_html(230) or '<h2>🐺 WOLF LIFE</h2>'}<div class='tagline' style='text-align:center;font-size:11px;margin:4px 0 14px'>Los Santos · Team Suite</div>",
                    unsafe_allow_html=True)
visible = [(k, l) for k, l in TABS if mode_of(k) != "hidden"]
if ss.get("page") not in [k for k, _ in visible]: ss.page = visible[0][0]
st.sidebar.markdown(f"<div class='user-card'><div class='avatar'>{esc(user['username'][:1].upper())}</div>"
                    f"<div><strong>{esc(user['username'])}</strong>"
                    f"<div class='muted'>{'Alpha-Owner' if is_owner else 'Administrator' if is_admin else 'Teammitglied'}</div></div></div>",
                    unsafe_allow_html=True)

# --- GLOBALE SUCHE IN DER SIDEBAR ---
global_q = st.sidebar.text_input("🔍 Suche über alles...", placeholder="Name, Grund, Aufgabe...", key="global_search_input").strip()

def _nav(k):
    ss.page = k
    ss["global_search_input"] = ""


counts = {"applicants": sum(x.get("status") not in ("Angenommen", "Abgelehnt") for x in data["applicants"]),
          "tasks": sum(x.get("status") != "Erledigt" for x in data["tasks"])}
NAV_GROUPS = [("Übersicht", ["dashboard"]), ("Team", ["team", "archive", "applicants"]),
              ("Verwaltung", ["calendar", "warnings", "absences", "tasks", "protocols", "notes"]),
              ("System", ["settings", "accounts"])]
for grp, grp_keys in NAV_GROUPS:
    items = [(k, l) for k, l in visible if k in grp_keys]
    if not items: continue
    st.sidebar.markdown(f"<div class='nav-group'>{grp}</div>", unsafe_allow_html=True)
    for k, l in items:
        n = counts.get(k, 0)
        st.sidebar.button(f"{l}  ·  {n}" if n else l, key=f"nav_{k}", on_click=_nav, args=(k,),
                          type="primary" if (ss.page == k and not global_q) else "secondary", use_container_width=True)

key = ss.page
perm_mode = mode_of(key)
can_write = perm_mode in ("full", "absence_own") if key == "absences" else (perm_mode == "full")
if perm_mode == "readonly": st.sidebar.markdown(chip("👁 Nur-Lesen", "#F59E0B"), unsafe_allow_html=True)
elif perm_mode == "absence_own": st.sidebar.markdown(chip("👤 Nur eigene Abmeldungen", "#3B82F6"), unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔒 Abmelden", key="logout", use_container_width=True):
    ss.user = None
    st.rerun()


def confirm_delete(coll, iid, label, key):
    ck = f"cf_{key}"
    if ss.get(ck):
        st.warning(f"„{label}“ wirklich endgültig löschen?")
        if st.button("Ja, löschen", key=f"y_{key}"):
            ss[ck] = False
            remove(coll, iid, f"{label} gelöscht")
        if st.button("Abbrechen", key=f"n_{key}"):
            ss[ck] = False
            st.rerun()
    elif st.button("🗑 Löschen", key=f"del_{key}"):
        ss[ck] = True
        st.rerun()


def delete_btn(coll, iid, what):
    if can_write: confirm_delete(coll, iid, what, f"{coll}_{iid}")


member_names = [m["name"] for m in sorted(data["members"], key=lambda m: RANKS.index(m["rank"]) if m["rank"] in RANKS else 99)]
rank_of = {m["name"]: m["rank"] for m in data["members"]}


def mlabel(n): return f"{n} ({rank_of[n]})" if n in rank_of else n


def flash(msg, kind="info"): ss.setdefault("flash", []).append((kind, msg))


def _unrestricted(): return is_owner or (is_admin and my_rank is None)


def assignable_ranks():
    """Nur Ränge unterhalb des eigenen Rangs dürfen vergeben werden."""
    if _unrestricted(): return RANKS
    return RANKS[RANKS.index(my_rank) + 1:] if my_rank in RANKS else []


def can_manage_rank(r):
    return _unrestricted() or (my_rank in RANKS and (r not in RANKS or RANKS.index(r) > RANKS.index(my_rank)))


# =====================================================================
# GLOBALE SUCHE (ÜBER ALLE BEREICHE)
# =====================================================================
for _k, _msg in ss.pop("flash", []): getattr(st, _k)(_msg)
check_probation()

if global_q:
    terms = global_q.lower().split()
    st.title("🔍 Suche")
    st.caption(f"Treffer für: {global_q}  ·  Suchfeld leeren oder links einen Bereich wählen, um zurückzukehren.")

    def hit(*txt):
        blob = " ".join(str(t) for t in txt).lower()
        return all(t in blob for t in terms)

    H = lambda t: hl(str(t), terms)

    def snip(t):
        t = str(t).replace("\n", " ")
        i = min([t.lower().find(x) for x in terms if x in t.lower()] or [0])
        a = max(0, i - 60)
        return ("…" if a else "") + t[a:a + 200] + ("…" if a + 200 < len(t) else "")

    def names_txt(sc):
        v = sc.get("assignees", "")
        return ", ".join(v) if isinstance(v, list) else str(v)

    G = {}
    G["team"] = [f"<strong>{H(m['name'])}</strong> {badge(m['rank'])} {chip(m['status'], STATUS_COL.get(m['status'], '#9CA3AF'))}"
                 f"<br><span class='muted'>Discord-ID: {H(m.get('discord_id', '-'))} | Seit: {fmt(m.get('joined'))}</span>"
                 for m in data["members"] if hit(m["name"], m.get("discord_id", ""), m["rank"], m["status"])]
    G["archive"] = [f"<strong>{H(a['name'])}</strong> {badge(a['rank'])}<br><span class='muted'>Entfernt am {fmt(a['removed'])} von {esc(a['removed_by'])}</span><br>{H(snip(a.get('reason', '')))}"
                    for a in data["archive"] if hit(a["name"], a.get("reason", ""), a.get("rank", ""))]
    G["applicants"] = [f"<strong>{H(a['name'])}</strong> {chip(a['status'], '#3B82F6')}<br><span class='muted'>{esc(a['role'])} · {fmt(a['date'])}</span><br>{H(snip(a.get('notes', '')))}"
                       for a in data["applicants"] if hit(a["name"], a["role"], a.get("notes", ""), a["status"])]
    G["calendar"] = [f"{chip(sc['type'], SHIFT_COL.get(sc['type'], '#3B82F6'))} <strong>{H(sc['title'])}</strong> <span class='muted'>({fmt(sc['date'])}, {esc(sc.get('time_from', ''))}–{esc(sc.get('time_to', ''))})</span>"
                     f"<br><span class='muted'>Eingeteilt: {H(names_txt(sc) or 'Offen / Alle')}</span>"
                     for sc in data["schedules"] if hit(sc.get("title", ""), sc.get("type", ""), names_txt(sc), sc.get("notes", ""))]
    G["warnings"] = [f"<strong>{H(w['member'])}</strong> {chip(w['level'], '#EF4444')}<br>{H(snip(w['reason']))}<br><span class='muted'>von {esc(w['issuer'])} · {fmt(w.get('date'))}</span>"
                     for w in data["warnings"] if hit(w["member"], w["reason"], w["level"], w["issuer"])]
    G["absences"] = [f"<strong>{H(a['name'])}</strong> <span class='muted'>{fmt(a['from_date'])} ➔ {fmt(a['to_date'])}</span><br>{H(snip(a.get('reason', '')))}"
                     for a in data["absences"] if hit(a["name"], a.get("reason", ""))]
    G["tasks"] = [f"{chip(x['priority'], PRIO_COL.get(x['priority'], '#9CA3AF'))} <strong>{H(x['title'])}</strong> ({esc(x['status'])})<br><span class='muted'>Zuständig: {H(x['assignee'])}</span>"
                  for x in data["tasks"] if hit(x["title"], x["assignee"])]
    G["protocols"] = [f"<strong>{H(p['title'])}</strong><br><span class='muted'>{esc(p['date'])} · {H(p.get('participants', ''))}</span><br>{H(snip(p.get('content', '')))}"
                      for p in data["protocols"] if hit(p["title"], p.get("participants", ""), p.get("content", ""))]
    G["notes"] = [H(snip(data["notes"]))] if hit(data["notes"]) else []
    groups = [(k, v) for k, v in G.items() if v and mode_of(k) != "hidden"]
    st.caption(f"{sum(len(v) for _, v in groups)} Treffer in {len(groups)} Bereichen")
    if not groups: st.info("Keine Treffer.")
    labels = dict(TABS)
    for k, v in groups:
        st.subheader(f"{labels[k]} ({len(v)})")
        for h in v[:15]: show(h)
        if len(v) > 15: st.caption(f"… und {len(v) - 15} weitere")
        st.button("Zum Bereich öffnen", key=f"go_{k}", on_click=_nav, args=(k,))

# =====================================================================
# DASHBOARD
# =====================================================================
elif key == "dashboard":
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
        st.subheader(f"🧪 Probezeit-Tracker ({prob_days()} Tage)")
        pm = [m for m in data["members"] if m["status"] == "Probezeit"]
        if pm:
            for m in pm:
                days_passed, pct, col, status_lbl = probation_info(m)
                show(f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                     f"<strong>{esc(m['name'])}</strong> {badge(m['rank'])}</div>"
                     f"<div class='muted' style='margin-top:4px'>{status_lbl}</div>"
                     f"<div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{pct}%;background:{col}'></div></div>")
                if mode_of("team") == "full":
                    pb1, pb2, _ = st.columns([2, 2, 3])
                    if pb1.button("✅ Bestanden", key=f"pp{m['id']}"):
                        send_discord_embed("team", f"🎉 Probezeit bestanden: {m['name']}",
                                           f"{dc_mention(m)} ist ab sofort **fester Teil des Teams**. Glückwunsch! 🐺", color_hex="#22C55E",
                                           fields=[{"name": "🛡️ Rang", "value": m["rank"]}], author_name=user["username"])
                        update("members", m["id"], f"{m['name']}: Probezeit bestanden", status="Aktiv", probation_end="", prob_reminded=False)
                    if pb2.button("➕ 7 Tage", key=f"px{m['id']}"):
                        update("members", m["id"], f"{m['name']}: Probezeit +7 Tage",
                               probation_end=(max(prob_end(m), date.today()) + timedelta(days=7)).isoformat(), prob_reminded=False)
        else:
            show("<span class='muted'>Niemand in der Probezeit.</span>")


# =====================================================================
# TEAM-ÜBERSICHT & PROBEZEIT-TRACKER
# =====================================================================
elif key == "team":
    st.title("👥 Team-Übersicht & Kader")
    if can_write:
        with st.expander("➕ Neues Teammitglied hinzufügen"):
            with st.form("add_member", clear_on_submit=True):
                a, b, c, e = st.columns(4)
                n = a.text_input("Discord Name / Tag")
                did = b.text_input("Discord-ID (optional)")
                r = c.selectbox("Rang", assignable_ranks() or ["–"])
                s = e.selectbox("Status", MEMBER_STATUS)
                if st.form_submit_button("Mitglied hinzufügen", use_container_width=True):
                    n = n.strip()
                    if not n: st.warning("Bitte einen Namen eingeben.")
                    elif n.lower() in [x.lower() for x in member_names]: st.warning("Dieses Mitglied existiert bereits.")
                    elif r not in RANKS: st.warning("Du darfst keinen Rang vergeben. Verknüpfe dein Konto mit einem Teammitglied (Benutzer & Rechte).")
                    elif did.strip() and not did.strip().isdigit(): st.warning("Die Discord-ID besteht nur aus Ziffern.")
                    else:
                        today_iso = date.today().isoformat()
                        with edit(f"Mitglied {n} hinzugefügt") as d:
                            d["members"].append({
                                "id": uid(), "name": n, "discord_id": did.strip() or "-", "rank": r,
                                "status": s, "joined": today_iso,
                                "probation_start": today_iso if s == "Probezeit" else "",
                                "probation_end": (date.today() + timedelta(days=prob_days())).isoformat() if s == "Probezeit" else ""
                            })
                        send_discord_embed(
                            "team",
                            "🆕 Neues Teammitglied im Kader!",
                            f"**{n}** wurde soeben offiziell in das Team von **Wolf Life** aufgenommen.",
                            color_hex=rank_color(r),
                            fields=[
                                {"name": "👤 Mitglied", "value": n, "inline": True},
                                {"name": "🛡️ Rang", "value": r, "inline": True},
                                {"name": "📌 Status", "value": s, "inline": True},
                                {"name": "🆔 Discord-ID", "value": did.strip() or "-", "inline": True},
                            ],
                            author_name=user["username"]
                        )
                        st.rerun()

    def warn_txt(n):
        c = sum(w["member"] == n or w["member"].startswith(n + " (") for w in data["warnings"])
        return f" | ⚠️ {c} Verwarnung(en)" if c else ""

    f1, f2 = st.columns([3, 1])
    q = f1.text_input("🔍 Mitglied suchen...").lower()
    sf = f2.selectbox("Status", ["Alle"] + MEMBER_STATUS)
    shown = [m for m in data["members"] if q in m["name"].lower() and sf in ("Alle", m["status"])]

    for m in sorted(shown, key=lambda m: RANKS.index(m["rank"]) if m["rank"] in RANKS else 99):
        prob_html = ""
        if m["status"] == "Probezeit":
            _, pct, pcol, plbl = probation_info(m)
            prob_html = (f"<div style='margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,.06)'>"
                         f"<span class='muted'>{plbl}</span>"
                         f"<div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{pct}%;background:{pcol}'></div></div></div>")

        card_content = (f"<div style='display:flex;justify-content:space-between;align-items:center;width:100%'>"
                        f"<div><strong>{esc(m['name'])}</strong> {chip(m['status'], STATUS_COL.get(m['status'], '#9CA3AF'))}<br>"
                        f"<span class='muted'>ID: {esc(m.get('discord_id', '-'))} | Seit: {fmt(m.get('joined'))}{warn_txt(m['name'])}</span></div>"
                        f"<div style='display:flex;align-items:center;gap:12px;'>{badge(m['rank'])}</div></div>{prob_html}")
        
        if can_write and can_manage_rank(m["rank"]):
            col_card, col_btn = st.columns([11, 1])
            with col_card:
                show(card_content, "member-card")
            with col_btn:
                with st.popover("✏️"):
                    st.markdown(f"### ✏️ {esc(m['name'])} bearbeiten")
                    a, b = st.columns(2)
                    rk_opts = [r for r in RANKS if r == m["rank"] or r in assignable_ranks()]
                    nr = a.selectbox("Rang", rk_opts, index=rk_opts.index(m["rank"]) if m["rank"] in rk_opts else 0, key=f"r{m['id']}")
                    ns = b.selectbox("Status", MEMBER_STATUS, index=MEMBER_STATUS.index(m["status"]) if m["status"] in MEMBER_STATUS else 0, key=f"s{m['id']}")
                    if ns == "Probezeit":
                        try: def_pstart = date.fromisoformat(m.get("probation_start") or m.get("joined"))
                        except Exception: def_pstart = date.today()
                        pstart_in = st.date_input("Probezeit-Beginn", value=def_pstart, format="DD.MM.YYYY", key=f"ps{m['id']}")
                        pend_in = st.date_input("Probezeit-Ende", value=prob_end(m) if m["status"] == "Probezeit" else def_pstart + timedelta(days=prob_days()),
                                                format="DD.MM.YYYY", key=f"pe{m['id']}")
                    else:
                        pstart_in = pend_in = None

                    old_did = "" if m.get("discord_id", "-") == "-" else m["discord_id"]
                    new_did = st.text_input("Discord-ID (Zahl, für Rollen-Sync)", value=old_did, key=f"did{m['id']}").strip()
                    bad_did = new_did != old_did and new_did != "" and not new_did.isdigit()
                    if bad_did: st.warning("Die Discord-ID besteht nur aus Ziffern.")
                    if st.button("💾 Speichern", key=f"sv{m['id']}", disabled=bad_did):
                        old_r, old_s = m["rank"], m["status"]
                        ch = {"rank": nr, "status": ns, "discord_id": new_did or "-"}
                        if pstart_in:
                            ch["probation_start"] = pstart_in.isoformat()
                            ch["probation_end"] = pend_in.isoformat()
                            if pend_in.isoformat() != (m.get("probation_end") or ""): ch["prob_reminded"] = False
                        elif old_s == "Probezeit":
                            ch["probation_end"] = ""
                            ch["prob_reminded"] = False
                        if old_r != nr or old_s != ns:
                            send_discord_embed(
                                "team",
                                f"{rank_title(old_r, nr)[0]}: {m['name']}",
                                f"{dc_mention({**m, 'discord_id': new_did or '-'})} – Rang oder Status wurden angepasst.",
                                color_hex=rank_title(old_r, nr)[1],
                                fields=[
                                    {"name": "👤 Mitglied", "value": m["name"], "inline": True},
                                    {"name": "🛡️ Rang", "value": f"{old_r} ➔ **{nr}**" if old_r != nr else nr, "inline": True},
                                    {"name": "📌 Status", "value": f"{old_s} ➔ **{ns}**" if old_s != ns else ns, "inline": True},
                                ],
                                author_name=user["username"]
                            )
                        if old_r != nr:
                            _res = dc_sync_role(new_did or "-", old_r, nr)
                            if _res: flash(_res, "success" if _res.startswith("✅") else "warning")
                        update("members", m["id"], f"{m['name']}: {nr}/{ns}", **ch)

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
                            send_discord_embed(
                                "team",
                                "🚪 Teammitglied entfernt & archiviert",
                                f"**{m['name']}** hat das Team verlassen bzw. wurde entfernt.",
                                color_hex="#EF4444",
                                fields=[
                                    {"name": "👤 Ehemaliges Mitglied", "value": m["name"], "inline": True},
                                    {"name": "🛡️ Letzter Rang", "value": m["rank"], "inline": True},
                                    {"name": "📝 Grund", "value": "Intern im Archiv hinterlegt.", "inline": False},
                                ],
                                author_name=user["username"]
                            )
                            st.rerun()
        else:
            show(card_content, "member-card")


# =====================================================================
# EHEMALIGE
# =====================================================================
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


# =====================================================================
# BEWERBER
# =====================================================================
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
                        send_discord_embed(
                            "applicants",
                            "📋 Neue Teambewerbung eingegangen!",
                            f"Es wurde eine neue Bewerbung für das **Wolf Life Team** im System hinterlegt.",
                            color_hex="#3B82F6",
                            fields=[
                                {"name": "👤 Bewerber", "value": n.strip(), "inline": True},
                                {"name": "🎯 Angestrebte Rolle", "value": role, "inline": True},
                                {"name": "📊 Aktueller Status", "value": stat, "inline": True},
                                {"name": "📝 Notizen / Eindruck", "value": notes.strip() or "Keine Notizen hinterlegt.", "inline": False},
                            ],
                            author_name=user["username"]
                        )
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
                    col_st = "#22C55E" if ns == "Angenommen" else ("#EF4444" if ns == "Abgelehnt" else "#F59E0B")
                    send_discord_embed(
                        "applicants",
                        "📌 Bewerbungsstatus aktualisiert",
                        f"Der Status der Bewerbung von **{ap['name']}** wurde geändert.",
                        color_hex=col_st,
                        fields=[
                            {"name": "👤 Bewerber", "value": ap["name"], "inline": True},
                            {"name": "🎯 Rolle", "value": ap["role"], "inline": True},
                            {"name": "🔄 Neuer Status", "value": f"**{ns}**", "inline": True},
                        ],
                        author_name=user["username"]
                    )
                    update("applicants", ap["id"], f"Bewerbung {ap['name']} → {ns}", status=ns)
                if ap["status"] == "Angenommen" and ap["name"].lower() not in [x.lower() for x in member_names]:
                    if st.button("👥 Als Mitglied (Probezeit) übernehmen", key=f"adopt{ap['id']}"):
                        new_rank = APP_ROLES.get(ap["role"], "Test-Supporter")
                        today_iso = date.today().isoformat()
                        with edit(f"{ap['name']} ins Team übernommen") as d:
                            d["members"].append({"id": uid(), "name": ap["name"], "discord_id": "-",
                                                 "rank": new_rank, "status": "Probezeit",
                                                 "joined": today_iso, "probation_start": today_iso,
                                                 "probation_end": (date.today() + timedelta(days=prob_days())).isoformat()})
                        send_discord_embed(
                            "team",
                            "🎉 Bewerber ins Team übernommen!",
                            f"**{ap['name']}** hat die Bewerbungsphase bestanden und startet jetzt in die **14-tägige Probezeit**!",
                            color_hex="#22C55E",
                            fields=[
                                {"name": "👤 Neues Teammitglied", "value": ap["name"], "inline": True},
                                {"name": "🛡️ Einstiegsrang", "value": new_rank, "inline": True},
                                {"name": "🧪 Probezeit", "value": f"{prob_days()} Tage (bis {fmt((date.today() + timedelta(days=prob_days())).isoformat())})", "inline": True},
                            ],
                            author_name=user["username"]
                        )
                        st.rerun()
                delete_btn("applicants", ap["id"], f"Bewerbung {ap['name']}")


# =====================================================================
# DIENSTPLAN & KALENDER
# =====================================================================
elif key == "calendar":
    st.title("🗓️ Dienstplan & Team-Kalender")
    st.caption("Plane Support-Schichten, Teamsitzungen oder Events und sieh auf einen Blick, wer abgemeldet ist.")

    def names_of(sc):
        v = sc.get("assignees", [])
        return [x.strip() for x in v.split(",") if x.strip() and x.strip() != "Offen / Alle"] if isinstance(v, str) else list(v)

    def absent(name, dt):
        return any(a["name"] == name and (parse_d(a.get("from_date")) or date.max) <= dt <= (parse_d(a.get("to_date")) or date.min)
                   for a in data["absences"])

    def t_of(sv, default="18:00"):
        try: return datetime.strptime(str(sv).strip(), "%H:%M").time()
        except Exception: return datetime.strptime(default, "%H:%M").time()

    if can_write:
        with st.expander("➕ Neue Schicht / Termin eintragen"):
            with st.form("add_sched", clear_on_submit=True):
                c1, c2 = st.columns(2)
                stitle = c1.text_input("Titel / Schicht-Bezeichnung", placeholder="z.B. Spätschicht Support")
                stype = c2.selectbox("Kategorie", SHIFT_TYPES)
                c3, c4, c5 = st.columns(3)
                sdate = c3.date_input("Datum", value=date.today(), format="DD.MM.YYYY")
                sfrom = c4.time_input("Von", value=t_of("18:00"))
                sto = c5.time_input("Bis", value=t_of("22:00"))
                swho = st.multiselect("Eingeteilte Teammitglieder", member_names, format_func=mlabel)
                c6, c7 = st.columns([1, 3])
                srep = c6.number_input("Wiederholen (Wochen)", 0, 12, 0)
                snotes = c7.text_input("Hinweise (optional)")
                if st.form_submit_button("Termin im Dienstplan speichern", use_container_width=True):
                    if not stitle.strip():
                        st.warning("Bitte einen Titel eingeben.")
                    else:
                        days = [sdate + timedelta(weeks=k) for k in range(int(srep) + 1)]
                        clash = sorted({f"{n} ({fmt(dt.isoformat())})" for dt in days for n in swho if absent(n, dt)})
                        with edit(f"Dienstplan-Eintrag „{stitle.strip()}“") as d:
                            for dt in days:
                                d["schedules"].append({"id": uid(), "title": stitle.strip(), "type": stype, "date": dt.isoformat(),
                                                       "time_from": sfrom.strftime("%H:%M"), "time_to": sto.strftime("%H:%M"),
                                                       "assignees": list(swho), "notes": snotes.strip()})
                        send_discord_embed(
                            "general", "🗓️ Neuer Eintrag im Dienstplan / Kalender",
                            "Es wurde ein neuer Termin für das Team eingetragen." + (f"\n🔁 Wiederholt für **{int(srep)}** weitere Woche(n)." if srep else ""),
                            color_hex=SHIFT_COL.get(stype, "#3B82F6"),
                            fields=[{"name": "📌 Titel", "value": stitle.strip()}, {"name": "🏷️ Kategorie", "value": stype},
                                    {"name": "📅 Datum & Zeit", "value": f"{fmt(sdate.isoformat())} ({sfrom.strftime('%H:%M')} – {sto.strftime('%H:%M')} Uhr)"},
                                    {"name": "👥 Eingeteilt", "value": ", ".join(swho) or "Offen / Alle", "inline": False}],
                            author_name=user["username"])
                        if clash: flash("⚠️ Eingeteilt, aber abgemeldet: " + ", ".join(clash), "warning")
                        st.rerun()

    # --- Monatsansicht ---
    ss.setdefault("cal_m", date.today().replace(day=1))
    cm = ss.cal_m
    n1, n2, n3 = st.columns([1, 4, 1])
    if n1.button("◀", key="cal_prev", use_container_width=True):
        ss.cal_m = (cm - timedelta(days=1)).replace(day=1)
        st.rerun()
    if n3.button("▶", key="cal_next", use_container_width=True):
        ss.cal_m = (cm + timedelta(days=32)).replace(day=1)
        st.rerun()
    n2.markdown(f"<div style='text-align:center;font-size:24px;font-weight:800'>{MONTHS[cm.month - 1]} {cm.year}</div>", unsafe_allow_html=True)
    cal_items = {}

    def put(dt, color, text):
        if dt: cal_items.setdefault(dt, []).append((color, text))

    for sc in data["schedules"]:
        put(parse_d(sc.get("date")), SHIFT_COL.get(sc.get("type"), "#3B82F6"), f"{sc.get('time_from', '')} {sc.get('title', '')}".strip())
    for ab in data["absences"]:
        a0, a1 = parse_d(ab.get("from_date")), parse_d(ab.get("to_date"))
        if a0 and a1:
            for k in range(min((a1 - a0).days + 1, 400)): put(a0 + timedelta(days=k), "#F59E0B", f"✈ {ab['name']}")
    for m in data["members"]:
        if m["status"] == "Probezeit": put(prob_end(m), "#FFFFFF", f"🧪 Probezeit-Ende {m['name']}")
    cells = "".join(f"<div class='cal-h'>{w}</div>" for w in WEEKDAYS)
    for week in _cal.Calendar(0).monthdatescalendar(cm.year, cm.month):
        for dt in week:
            its = cal_items.get(dt, [])
            body = "".join(f"<div class='cal-i' style='border-left:3px solid {c}'>{esc(t_)}</div>" for c, t_ in its[:4])
            if len(its) > 4: body += f"<div class='muted'>+{len(its) - 4} weitere</div>"
            cls = "cal-d" + (" today" if dt == date.today() else "") + (" off" if dt.month != cm.month else "")
            cells += f"<div class='{cls}'><div class='cal-n'>{dt.day}</div>{body}</div>"
    st.markdown(f"<div class='cal'>{cells}</div>", unsafe_allow_html=True)

    # --- Wochenübersicht ---
    ss.setdefault("cal_offset", 0)
    nav1, nav2, nav3 = st.columns([1, 2, 1])
    if nav1.button("⬅️ Vorherige Woche", use_container_width=True):
        ss.cal_offset -= 1
        st.rerun()
    if nav2.button("📅 Aktuelle Woche anzeigen", use_container_width=True):
        ss.cal_offset = 0
        st.rerun()
    if nav3.button("Nächste Woche ➡️", use_container_width=True):
        ss.cal_offset += 1
        st.rerun()

    today = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=ss.cal_offset)
    st.subheader(f"📆 Wochenübersicht: {monday.strftime('%d.%m.%Y')} – {(monday + timedelta(days=6)).strftime('%d.%m.%Y')}")
    weekdays_de = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    for i in range(7):
        day_dt = monday + timedelta(days=i)
        is_today = day_dt == today
        day_shifts = sorted([x for x in data["schedules"] if x.get("date") == day_dt.isoformat()], key=lambda x: x.get("time_from", ""))
        day_abs = [a for a in data["absences"] if (parse_d(a.get("from_date")) or date.max) <= day_dt <= (parse_d(a.get("to_date")) or date.min)]
        if not (day_shifts or day_abs or is_today): continue
        label = f"{weekdays_de[i]}, {day_dt.strftime('%d.%m.%Y')}" + ("  🟢 (HEUTE)" if is_today else "")
        inner = f"<div style='font-size:15px;font-weight:800;margin-bottom:6px'>{esc(label)}</div>"
        if day_abs:
            inner += f"<div style='margin-bottom:6px'>{chip('🚫 Abgemeldet', '#EF4444')} <span class='muted'>{', '.join(esc(a['name']) for a in day_abs)}</span></div>"
        for sc in day_shifts:
            note = f" · <em>{esc(sc['notes'])}</em>" if sc.get("notes") else ""
            warn = " ".join(chip(f"⚠️ {n} abgemeldet", "#F59E0B") for n in names_of(sc) if absent(n, day_dt))
            inner += (f"<div style='margin-top:4px;padding:6px 10px;background:rgba(255,255,255,.03);border-radius:8px'>"
                      f"{chip(sc['type'], SHIFT_COL.get(sc['type'], '#3B82F6'))} <strong>{esc(sc['title'])}</strong> "
                      f"<span class='muted'>({esc(sc.get('time_from', ''))} – {esc(sc.get('time_to', ''))} Uhr)</span><br>"
                      f"<span class='muted'>👥 Eingeteilt: {esc(', '.join(names_of(sc)) or 'Offen / Alle')}{note}</span> {warn}</div>")
        if not day_shifts: inner += "<div class='muted'>Keine Schichten oder Termine geplant.</div>"
        st.markdown(f"<div class='content-box' style='{'border-left: 5px solid ' + t['ACCENT'] + ';' if is_today else ''}'>{inner}</div>", unsafe_allow_html=True)
        if can_write:
            for sc in day_shifts:
                e1, e2 = st.columns([1, 6])
                with e1.popover("✏️"):
                    st.markdown(f"**{esc(sc['title'])}** bearbeiten")
                    sid = sc["id"]
                    et = st.text_input("Titel", value=sc["title"], key=f"et{sid}")
                    ety = st.selectbox("Kategorie", SHIFT_TYPES, index=SHIFT_TYPES.index(sc["type"]) if sc["type"] in SHIFT_TYPES else 0, key=f"ety{sid}")
                    ed = st.date_input("Datum", value=parse_d(sc.get("date"), date.today()), format="DD.MM.YYYY", key=f"ed{sid}")
                    f1, f2 = st.columns(2)
                    ef = f1.time_input("Von", value=t_of(sc.get("time_from")), key=f"ef{sid}")
                    eto = f2.time_input("Bis", value=t_of(sc.get("time_to"), "22:00"), key=f"eto{sid}")
                    ew = st.multiselect("Eingeteilt", member_names, default=[n for n in names_of(sc) if n in member_names], format_func=mlabel, key=f"ew{sid}")
                    en = st.text_input("Hinweise", value=sc.get("notes", ""), key=f"en{sid}")
                    if st.button("💾 Speichern", key=f"esv{sid}"):
                        update("schedules", sid, f"Dienstplan „{et.strip() or sc['title']}“ bearbeitet", title=et.strip() or sc["title"], type=ety,
                               date=ed.isoformat(), time_from=ef.strftime("%H:%M"), time_to=eto.strftime("%H:%M"), assignees=list(ew), notes=en.strip())
                with e2: confirm_delete("schedules", sc["id"], sc["title"], f"sched_{sc['id']}")

# =====================================================================
# VERWARNUNGEN
# =====================================================================
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
                            total_w = sum(1 for w in load_data()["warnings"] if w["member"] == wm)
                            send_discord_embed(
                                "warnings",
                                "⚠️ Team-Verwarnung / Strike ausgesprochen",
                                f"Gegen das Teammitglied **{wm}** wurde eine Verwarnung im System vermerkt.",
                                color_hex="#EF4444" if "Strike 3" in wl else "#F97316",
                                fields=[
                                    {"name": "👤 Betroffenes Mitglied", "value": mlabel(wm), "inline": True},
                                    {"name": "🚨 Verwarnungsstufe", "value": f"**{wl}**", "inline": True},
                                    {"name": "📊 Gesamtverwarnungen", "value": f"{total_w} Eintrag/Einträge", "inline": True},
                                    {"name": "📝 Begründung", "value": wr.strip(), "inline": False},
                                ],
                                author_name=user["username"]
                            )
                            st.rerun()
                        else: st.warning("Bitte einen Grund angeben.")
    for w in reversed(data["warnings"]):
        show(f"<strong>{esc(mlabel(w['member']))}</strong> | {chip(w['level'], '#EF4444' if 'Strike 3' in w['level'] else '#F97316' if 'Strike' in w['level'] else '#EAB308')} (Von: {esc(w['issuer'])}, {fmt(w.get('date'))})"
             f"<br>Grund: {esc(w['reason'])}")
        delete_btn("warnings", w["id"], "Verwarnung")


# =====================================================================
# ABMELDUNGEN
# =====================================================================
elif key == "absences":
    st.title("📅 Abmeldungen & Urlaub")
    if perm_mode in ("full", "absence_own"):
        with st.expander("➕ Abmeldung erfassen"):
            if not member_names: st.info("Zuerst Teammitglieder anlegen.")
            else:
                with st.form("add_abs", clear_on_submit=True):
                    if perm_mode == "absence_own":
                        if my_member:
                            am = st.selectbox("Mitglied", [my_member], format_func=mlabel)
                            st.caption("ℹ️ Du kannst nur deine eigene Abmeldung eintragen.")
                        else:
                            am = ""
                            st.warning("Dein Konto ist mit keinem Teammitglied verknüpft. Bitte einen Admin, das unter „Benutzer & Rechte“ zu tun.")
                    else:
                        am = st.selectbox("Mitglied", member_names, format_func=mlabel)
                    
                    c1, c2 = st.columns(2)
                    af = c1.date_input("Von", value=date.today(), format="DD.MM.YYYY")
                    at = c2.date_input("Bis", value=date.today(), format="DD.MM.YYYY")
                    ar = st.text_input("Grund")
                    if st.form_submit_button("Speichern", use_container_width=True):
                        if not am: st.warning("Keine Abmeldung möglich, solange dein Konto nicht verknüpft ist.")
                        elif at < af: st.warning("„Bis“ darf nicht vor „Von“ liegen.")
                        else:
                            days_count = (at - af).days + 1
                            with edit(f"Abmeldung {am}") as d:
                                d["absences"].append({"id": uid(), "name": am, "from_date": af.isoformat(),
                                                      "to_date": at.isoformat(), "reason": ar})
                            send_discord_embed(
                                "absences",
                                "📅 Neue Team-Abmeldung eingetragen",
                                f"**{am}** hat sich für den unten genannten Zeitraum vom Dienst abgemeldet.",
                                color_hex="#F59E0B",
                                fields=[
                                    {"name": "👤 Teammitglied", "value": mlabel(am), "inline": True},
                                    {"name": "⏳ Dauer", "value": f"{days_count} Tag(e)", "inline": True},
                                    {"name": "📆 Zeitraum", "value": f"{fmt(af.isoformat())} ➔ {fmt(at.isoformat())}", "inline": True},
                                    {"name": "📝 Grund der Abmeldung", "value": ar.strip() or "Kein Grund angegeben.", "inline": False},
                                ],
                                author_name=user["username"]
                            )
                            st.rerun()
                            
    for a in reversed(data["absences"]):
        show(f"<strong>{esc(mlabel(a['name']))}</strong> ({fmt(a['from_date'])} ➔ {fmt(a['to_date'])})<br>Grund: {esc(a['reason'])}")
        can_del_this = (perm_mode == "full") or (perm_mode == "absence_own" and bool(my_member) and a['name'] == my_member)
        if can_del_this: confirm_delete("absences", a["id"], "Abmeldung", f"abs_{a['id']}")


# =====================================================================
# AUFGABEN
# =====================================================================
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
                        who_str = ", ".join(who) or "Gesamtes Team"
                        with edit("Aufgabe erstellt") as d:
                            d["tasks"].append({"id": uid(), "title": tt.strip(), "assignee": who_str,
                                               "priority": tp, "status": "Offen"})
                        send_discord_embed(
                            "general",
                            "✅ Neue Team-Aufgabe erstellt",
                            f"Im Aufgaben-Board wurde eine neue Aufgabe angelegt.",
                            color_hex=PRIO_COL.get(tp, "#F59E0B"),
                            fields=[
                                {"name": "📋 Aufgabe", "value": tt.strip(), "inline": False},
                                {"name": "🔥 Priorität", "value": tp, "inline": True},
                                {"name": "👥 Zuständig", "value": who_str, "inline": True},
                            ],
                            author_name=user["username"]
                        )
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
            with b: confirm_delete("tasks", x["id"], "Aufgabe", f"tasks_{x['id']}")


# =====================================================================
# PROTOKOLLE
# =====================================================================
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
                        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                        with edit(f"Protokoll „{pt.strip()}“") as d:
                            d["protocols"].append({"id": uid(), "title": pt.strip(), "participants": pp,
                                                   "date": now_str, "content": pc})
                        preview = pc[:900] + ("..." if len(pc) > 900 else "")
                        send_discord_embed(
                            "general",
                            f"📝 Neues Sitzungsprotokoll: {pt.strip()}",
                            f"```\n{preview}\n```",
                            color_hex="#A855F7",
                            fields=[
                                {"name": "📅 Datum", "value": now_str, "inline": True},
                                {"name": "👥 Teilnehmer", "value": pp.strip() or "-", "inline": True},
                            ],
                            author_name=user["username"]
                        )
                        st.rerun()
                    else: st.warning("Bitte einen Titel eingeben.")
    for p in reversed(data["protocols"]):
        show(f"<h3>{esc(p['title'])}</h3><p class='muted'>Erstellt: {esc(p['date'])} | Teilnehmer: {esc(p['participants'])}</p>"
             f"<pre style='white-space:pre-wrap;background:transparent;border:none;color:{t['TEXT_MAIN']}'>{esc(p['content'])}</pre>")
        delete_btn("protocols", p["id"], "Protokoll")


# =====================================================================
# NOTIZEN
# =====================================================================
elif key == "notes":
    st.title("📌 Notizen")
    val = st.text_area("Notizblock", value=data["notes"], height=350, disabled=not can_write)
    if can_write and st.button("💾 Speichern"):
        with edit("Notizen aktualisiert") as d: d["notes"] = val
        st.success("Gespeichert!")


# =====================================================================
# EINSTELLUNGEN & DISCORD-WEBHOOK-KONFIGURATION
# =====================================================================
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
        new = st.text_input(f"Neues Passwort (min. {MIN_PW} Zeichen)", type="password")
        if st.form_submit_button("Passwort ändern"):
            if authenticate(user["username"], old) and len(new) >= MIN_PW:
                set_password(user["username"], new, "Passwort geändert")
                st.success("Passwort geändert.")
            else: st.error(f"Aktuelles Passwort falsch oder neues Passwort zu kurz (min. {MIN_PW} Zeichen).")

    if is_admin:
        st.markdown("---")
        st.subheader("🧪 Probezeit")
        nd = st.number_input("Standard-Probezeit (Tage)", 1, 120, prob_days())
        if st.button("💾 Probezeit speichern", key="pd_save"):
            with edit("Standard-Probezeit geändert") as d: d["settings"]["probation_days"] = int(nd)
            st.rerun()

    if is_owner:
        st.markdown("---")
        st.subheader("🤖 Discord-Anbindung (nur Alpha-Owner)")
        st.caption("Webhook-URLs und Bot-Token liegen in `discord_config.json`, nicht in den Teamdaten und nicht im Backup. "
                   "Leere Felder nutzen den „Allgemein“-Webhook. Den Token kannst du auch als Umgebungsvariable `DISCORD_BOT_TOKEN` setzen.")
        cfg = dc_cfg()
        with st.form("discord_cfg_form"):
            new_wh = {k: st.text_input(lbl, value=cfg["webhooks"].get(k, ""), type="password",
                                       placeholder="https://discord.com/api/webhooks/…", key=f"wh_input_{k}") for k, lbl in WEBHOOK_CHANNELS}
            sync = st.checkbox("Discord-Rolle bei Rangänderung automatisch anpassen", value=bool(cfg["sync_roles"]))
            c1, c2 = st.columns(2)
            gid = c1.text_input("Server-ID", value=cfg["guild_id"])
            tok = c2.text_input("Bot-Token" + (" (gespeichert, leer = behalten)" if cfg["bot_token"] else ""), type="password")
            st.markdown("**Rang → Discord-Rollen-ID**")
            rc = st.columns(3)
            roles = {r: rc[i % 3].text_input(r, value=cfg["roles"].get(r, ""), key=f"dcr_{i}") for i, r in enumerate(RANKS)}
            save_wh = st.form_submit_button("💾 Discord-Einstellungen speichern", use_container_width=True)
        if save_wh:
            new_wh = {k: v.strip() for k, v in new_wh.items()}
            roles = {k: v.strip() for k, v in roles.items()}
            if any(v and not DC_HOOK_RE.match(v) for v in new_wh.values()):
                st.error("Ungültige Webhook-URL. Sie muss eine discord.com-Webhook-Adresse sein.")
            elif any(v and not v.isdigit() for v in [gid.strip(), *roles.values()]):
                st.error("Server- und Rollen-IDs bestehen nur aus Ziffern.")
            else:
                cfg.update(webhooks=new_wh, sync_roles=sync, guild_id=gid.strip(), roles=roles)
                if tok.strip(): cfg["bot_token"] = tok.strip()
                dc_save(cfg)
                st.success("Gespeichert.")
        st.markdown("**🧪 Testnachricht senden**")
        for col, (k, lbl) in zip(st.columns(len(WEBHOOK_CHANNELS)), WEBHOOK_CHANNELS):
            if col.button(lbl.split(" ")[0] + " " + k, key=f"dct_{k}", use_container_width=True):
                r_ = dc_test(k, user["username"])
                if r_ is None: st.warning(f"Für „{lbl}“ ist kein gültiger Webhook gespeichert.")
                elif r_[0]: st.success(f"„{lbl}“: gesendet.")
                else: st.error(f"„{lbl}“: {DC_ERR.get(r_[1], 'Fehler')} ({r_[1]})")
        st.markdown("**📜 Letzte Sendungen**")
        show("".join(f"<div class='muted'>{esc(t_)} – <strong>{esc(w_)}</strong>: {esc(r_)}</div>" for t_, w_, r_ in reversed(_dc_log()[-15:]))
             or "<span class='muted'>Noch nichts gesendet.</span>")


# =====================================================================
# BENUTZER & RECHTE
# =====================================================================
elif key == "accounts":
    st.title("🔑 Benutzer & Rechte")
    if not is_admin:
        st.error("Nur für Administratoren.")
        st.stop()
    with st.expander("➕ Benutzer anlegen"):
        with st.form("add_user", clear_on_submit=True):
            un = st.text_input("Benutzername")
            up = st.text_input(f"Start-Passwort (min. {MIN_PW} Zeichen)", type="password")
            ua = st.checkbox("Administrator (voller Zugriff)")
            uo = st.checkbox("Alpha-Owner (Zugriff auf Discord-Einstellungen)") if is_owner else False
            cols = st.columns(3)
            perms = {k: cols[i % 3].selectbox(l, perm_opts(k), format_func=lambda x: PERM_LABELS[x], index=1, key=f"p_{k}")
                     for i, (k, l) in enumerate(TABS) if k not in ("accounts", "settings")}
            if st.form_submit_button("Anlegen", use_container_width=True):
                if len(un.strip()) < 3 or len(up) < MIN_PW: st.error(f"Benutzername min. 3, Passwort min. {MIN_PW} Zeichen.")
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
                        _th = d["settings"].get("themes", {})
                        if u["username"] in _th: _th[new_clean] = _th.pop(u["username"])
                    if ss.user["username"] == u["username"]:
                        ss.user["username"] = new_clean
                    st.success("Benutzername erfolgreich aktualisiert!")
                    st.rerun()

            st.markdown("---")
            is_self = u["username"] == user["username"]
            adm = st.checkbox("Administrator (voller Zugriff)", value=bool(u.get("is_admin")),
                              disabled=is_self, key=f"adm_{u['username']}")
            ow = (st.checkbox("Alpha-Owner (übergeordnet, Zugriff auf Discord-Einstellungen)", value=bool(u.get("is_owner")),
                              disabled=is_self, key=f"own_{u['username']}") if is_owner else bool(u.get("is_owner")))
            lm_opts = ["–"] + member_names
            lm = st.selectbox("Verknüpftes Teammitglied (Rang-Rechte, eigene Abmeldung)", lm_opts,
                              index=lm_opts.index(u["member"]) if u.get("member") in lm_opts else 0,
                              format_func=lambda n: n if n == "–" else mlabel(n), key=f"lm_{u['username']}")
            cur = u.get("permissions") or {}
            pc = st.columns(3)
            newp = {k: pc[i % 3].selectbox(l, perm_opts(k), format_func=lambda x: PERM_LABELS[x],
                                           index=perm_opts(k).index(perm_cur(cur, k)) if perm_cur(cur, k) in perm_opts(k) else len(perm_opts(k)) - 1,
                                           key=f"ep_{u['username']}_{k}")
                    for i, (k, l) in enumerate(TABS) if k not in ("accounts", "settings")}
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
            np_ = st.text_input(f"Neues Passwort setzen (min. {MIN_PW} Zeichen)", type="password", key=f"np_{u['username']}")
            if st.button("🔑 Passwort zurücksetzen", key=f"rp_{u['username']}"):
                if len(np_) >= MIN_PW:
                    set_password(u["username"], np_, f"Passwort von {u['username']} zurückgesetzt")
                    st.success("Passwort gesetzt.")
                else: st.error(f"Mindestens {MIN_PW} Zeichen.")
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