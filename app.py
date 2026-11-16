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

# --- HARDCODED ALPHA-OWNER ACCOUNT ---
ALPHA_OWNER_USER = "Psycho_Max"
ALPHA_OWNER_PASS = "MaxLeon_2008!"

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

MEMBER_STATUS = ["Aktiv", "Probezeit", "Abgemeldet"]
APP_STATUS = ["Bewerbung eingegangen", "Im Testgespräch", "Testphase läuft", "Angenommen", "Abgelehnt"]
APP_CHECKLIST_ITEMS = [
    ("rules", "Regelwerk & Server-Gesetze abgefragt"),
    ("mic", "Mikrofon- & Audioqualität geprüft"),
    ("age", "Mindestalter & geistige Reife geprüft"),
    ("intro", "Support-Einweisung / Probe-Ticket durchgeführt"),
]
SUGG_STATUS = ["Offen", "In Prüfung", "Angenommen", "Abgelehnt"]
SUGG_COL = {"Offen": "#3B82F6", "In Prüfung": "#F59E0B", "Angenommen": "#22C55E", "Abgelehnt": "#EF4444"}
WIKI_CATS = ["Support-Leitfaden", "Sanktionskatalog", "Ingame-Commands", "Einweisung & Abläufe", "Sonstiges"]
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
    ("dashboard", "📊 Dashboard"), ("team", "👥 Team-Übersicht"), ("dossier", "🔍 Spieler-Dossier"), ("archive", "🗄️ Ehemalige"),
    ("applicants", "📋 Bewerber"), ("calendar", "🗓️ Dienstplan & Kalender"),
    ("warnings", "⚠️ Verwarnungen"), ("absences", "📅 Abmeldungen"), ("tasks", "✅ Aufgaben"),
    ("suggestions", "💡 Team-Vorschläge"), ("wiki", "📚 Regelwerk & Leitfäden"),
    ("protocols", "📝 Protokolle"), ("notes", "📌 Notizen"), ("settings", "⚙️ Einstellungen"),
    ("accounts", "🔑 Benutzer & Rechte"),
]

WEBHOOK_CHANNELS = [
    ("absences", "📅 Abmeldungen-Channel"),
    ("applicants", "📋 Bewerber-Channel"),
    ("warnings", "⚠️ Verwarnungen-Channel"),
    ("team", "👥 Team- & Kader-Channel"),
    ("general", "📢 Allgemein (Aufgaben, Protokolle, Vorschläge & Dienstplan)"),
]


def uid(): return uuid.uuid4().hex


@st.cache_resource
def _bg_b64(path):
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


def fmt(s):
    try: return date.fromisoformat(s).strftime("%d.%m.%Y")
    except Exception: return s or "-"


MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def parse_d(sv, default=None):
    try: return date.fromisoformat(sv)
    except Exception: return default


@st.cache_resource
def _lock(): return threading.Lock()


DEFAULTS = {
    "members": [], "applicants": [], "warnings": [], "absences": [], "tasks": [],
    "protocols": [], "schedules": [], "suggestions": [], "wiki": [],
    "notes": "", "users": [], "log": [], "settings": {}, "archive": [], "feedback": []
}


def _sb_creds():
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if not (url and key):
        try:
            url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
            key = str(st.secrets.get("SUPABASE_KEY", "")).strip()
        except Exception:
            pass
    return url, key


def _sb_get_doc(doc_id):
    url, key = _sb_creds()
    if not (url and key):
        return None
    req = urllib.request.Request(
        f"{url}/rest/v1/wolflife_store?id=eq.{quote(doc_id)}&select=payload",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        rows = json.loads(resp.read().decode("utf-8"))
        if rows and isinstance(rows[0].get("payload"), dict):
            return rows[0]["payload"]
        return {}


def _sb_put_doc(doc_id, payload):
    url, key = _sb_creds()
    if not (url and key):
        return False
    body = json.dumps({"id": doc_id, "payload": payload, "updated_at": datetime.now(timezone.utc).isoformat()}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/rest/v1/wolflife_store",
        data=body,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10):
        return True


@st.cache_data(ttl=15, show_spinner=False)
def _cached_fetch_data():
    d = {}
    sb_url, sb_key = _sb_creds()
    if sb_url and sb_key:
        cloud_d = _sb_get_doc("team_data")
        if cloud_d is not None:
            d = cloud_d
    if not d and os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            d = json.load(f)
    for k, v in DEFAULTS.items():
        d.setdefault(k, json.loads(json.dumps(v)))
    return d


def load_data():
    try:
        return json.loads(json.dumps(_cached_fetch_data()))
    except Exception as e:
        st.warning(f"⚠️ Cloud-Verbindung kurz gestört (nutze lokalen Zwischenspeicher): {e}")
        d = {}
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, encoding="utf-8") as f:
                    d = json.load(f)
            except Exception:
                pass
        for k, v in DEFAULTS.items():
            d.setdefault(k, json.loads(json.dumps(v)))
        return d


def save_data(d):
    try:
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        os.replace(tmp, DATA_FILE)
    except Exception:
        pass

    sb_url, sb_key = _sb_creds()
    if sb_url and sb_key:
        try:
            _sb_put_doc("team_data", d)
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern in Supabase: {e}")

    _cached_fetch_data.clear()


@contextmanager
def edit(action=None):
    with _lock():
        _cached_fetch_data.clear()
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


def get_rank_categories(d=None):
    src = d if d is not None else data
    return src.get("settings", {}).get("rank_categories", [])


def get_custom_ranks(d=None):
    src = d if d is not None else data
    return src.get("settings", {}).get("custom_ranks", [])


def all_rank_names(d=None):
    return [r["name"] for r in get_custom_ranks(d)]


def get_rank_obj(rank_name, d=None):
    return next((r for r in get_custom_ranks(d) if r["name"] == rank_name), None)


def get_category_obj(cat_id, d=None):
    return next((c for c in get_rank_categories(d) if c["id"] == cat_id), None)


def rank_color(rank_name, d=None):
    ro = get_rank_obj(rank_name, d)
    if ro:
        if ro.get("color"):
            return ro["color"]
        cat = get_category_obj(ro.get("category_id"), d)
        if cat and cat.get("color"):
            return cat["color"]
    return "#9CA3AF"


def rank_category_name(rank_name, d=None):
    ro = get_rank_obj(rank_name, d)
    if not ro:
        return ""
    cat = get_category_obj(ro.get("category_id"), d)
    return cat["name"] if cat else ""


def badge(r, show_cat=False):
    c = "#8B0000" if r.lower() in ("alpha owner", "alpha-owner") else rank_color(r)
    cat_n = rank_category_name(r)
    cat_tag = f" <span style='opacity:.75;font-weight:500;font-size:11px'>[{esc(cat_n)}]</span>" if (show_cat and cat_n) else ""
    prefix = "👑 " if r.lower() in ("owner", "alpha owner", "alpha-owner") else ""
    return (f"<span class='rank-badge' style='color:{c};border:1px solid {c};border-radius:999px;padding:2px 10px;"
            f"font-weight:bold;font-size:13px'>{prefix}{esc(r)}{cat_tag}</span>")


def rank_index(r):
    names = all_rank_names()
    return names.index(r) if r in names else 999


def rank_title(old, new):
    if old == new: return "🔄 Statusänderung", "#3B82F6"
    names = all_rank_names()
    up = names.index(new) < names.index(old) if old in names and new in names else None
    return ("⬆️ Uprank", "#22C55E") if up else ("⬇️ Downrank", "#EF4444") if up is False else ("🔄 Rangänderung", "#3B82F6")


DC_CFG_FILE = "discord_config.json"
DISCORD_API = "https://discord.com/api/v10"
DC_HOOK_RE = re.compile(r"^https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/(?:v\d+/)?webhooks/\d+/[\w-]+$")
DC_ERR = {0: "Keine Verbindung zu Discord.", 401: "Bot-Token ungültig.",
          403: "Bot darf die Rolle nicht vergeben (Recht „Rollen verwalten“ fehlt oder Bot-Rolle steht nicht über der Zielrolle).",
          404: "Mitglied nicht auf dem Server oder Server-/Rollen-ID falsch."}


@st.cache_resource
def _dc_log(): return []


@st.cache_data(ttl=30, show_spinner=False)
def _cached_dc_cfg():
    cfg = {
        "webhooks": {},
        "bot_token": "",
        "guild_id": "",
        "roles": {},
        "sync_roles": False,
        "maintenance_mode": False,
        "team_base_role_id": "",
        "team_role_g_id": "",
        "high_team_role_id": "",
        "replace_team_with_high": True,
    }
    sb_url, sb_key = _sb_creds()
    if sb_url and sb_key:
        try:
            cloud_cfg = _sb_get_doc("discord_config")
            if cloud_cfg:
                cfg.update(cloud_cfg)
                return cfg
        except Exception:
            pass
    try:
        with open(DC_CFG_FILE, encoding="utf-8") as f: cfg.update(json.load(f))
    except Exception: pass
    return cfg


def dc_cfg():
    return dict(_cached_dc_cfg())


def dc_save(cfg):
    try:
        tmp = DC_CFG_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=2, ensure_ascii=False)
        try: os.chmod(tmp, 0o600)
        except Exception: pass
        os.replace(tmp, DC_CFG_FILE)
    except Exception:
        pass
    sb_url, sb_key = _sb_creds()
    if sb_url and sb_key:
        try:
            _sb_put_doc("discord_config", cfg)
        except Exception as e:
            st.error(f"❌ Discord-Config konnte nicht in Supabase gespeichert werden: {e}")
    _cached_dc_cfg.clear()


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


def compute_discord_role_changes(old_rank_name, new_rank_name, cfg=None, d=None):
    cfg = cfg or dc_cfg()
    src = d if d is not None else load_data()
    cats = get_rank_categories(src)
    ranks = get_custom_ranks(src)

    old_ro = next((r for r in ranks if r["name"] == old_rank_name), None) if old_rank_name else None
    new_ro = next((r for r in ranks if r["name"] == new_rank_name), None) if new_rank_name else None

    to_add = []
    to_remove = []

    old_rid = (old_ro.get("discord_role_id") if old_ro else "") or cfg.get("roles", {}).get(old_rank_name or "", "")
    new_rid = (new_ro.get("discord_role_id") if new_ro else "") or cfg.get("roles", {}).get(new_rank_name or "", "")

    if old_rid and old_rid != new_rid:
        to_remove.append(old_rid)
    if new_rid:
        to_add.append(new_rid)

    new_cat = next((c for c in cats if new_ro and c["id"] == new_ro.get("category_id")), None)
    target_cat_rid = (new_cat.get("discord_role_id") or "").strip() if new_cat else ""

    if target_cat_rid:
        to_add.append(target_cat_rid)

    for c in cats:
        c_rid = (c.get("discord_role_id") or "").strip()
        if c_rid and c_rid != target_cat_rid:
            to_remove.append(c_rid)

    gets_team = bool(new_ro.get("gets_team_role", False)) if new_ro else False
    is_high_team = bool(new_cat.get("is_high_team", False)) if new_cat else False

    team_base_id = (cfg.get("team_base_role_id") or "").strip()
    team_g_id = (cfg.get("team_role_g_id") or "").strip()
    high_team_id = (cfg.get("high_team_role_id") or "").strip()
    replace_base = bool(cfg.get("replace_team_with_high", True))

    if gets_team:
        if team_g_id:
            to_add.append(team_g_id)
        if is_high_team:
            if high_team_id:
                to_add.append(high_team_id)
            if replace_base and team_base_id:
                to_remove.append(team_base_id)
            elif team_base_id:
                to_add.append(team_base_id)
        else:
            if team_base_id:
                to_add.append(team_base_id)
            if high_team_id:
                to_remove.append(high_team_id)
    else:
        if team_base_id:
            to_remove.append(team_base_id)
        if team_g_id:
            to_remove.append(team_g_id)
        if high_team_id:
            to_remove.append(high_team_id)

    add_clean = list(dict.fromkeys(x for x in to_add if str(x).isdigit()))
    rem_clean = list(dict.fromkeys(x for x in to_remove if str(x).isdigit() and x not in add_clean))
    return add_clean, rem_clean


def dc_sync_role(discord_id, old, new):
    cfg = dc_cfg()
    tok = os.environ.get("DISCORD_BOT_TOKEN") or cfg["bot_token"]
    if not (cfg["sync_roles"] and tok and cfg["guild_id"]): return None
    if not str(discord_id).isdigit():
        return "⚠️ Rang geändert, aber Discord-Rollen nicht angepasst: Beim Mitglied fehlt eine gültige Discord-ID (Zahl)."
    to_add, to_remove = compute_discord_role_changes(old, new, cfg)
    if not to_add and not to_remove:
        return f"⚠️ Rang geändert, aber für „{new}“ sind keine Discord-Rollen-IDs hinterlegt."
    base, log, errs = f"{DISCORD_API}/guilds/{cfg['guild_id']}/members/{discord_id}/roles", _dc_log(), []
    for method, rid in [("DELETE", r) for r in to_remove] + [("PUT", r) for r in to_add]:
        code, err = _dc_request(method, f"{base}/{rid}", token=cfg["bot_token"])
        _dc_log_add(log, f"Rollen-Sync ({method})", code in (200, 204), code, err)
        if code not in (200, 204): errs.append(DC_ERR.get(code, f"Fehler {code}."))
    return "✅ Discord-Rollen (inkl. Kategorie & Teamstatus) angepasst." if not errs else "⚠️ Discord-Rollen nicht vollständig angepasst: " + " ".join(dict.fromkeys(errs))


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


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_bytes(16)
    return salt.hex() + "$" + hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1).hex()


def check_pw(pw, stored):
    try: return hmac.compare_digest(hash_pw(pw, bytes.fromhex(stored.split("$")[0])), stored)
    except Exception: return False


def ensure_alpha_owner_in_db(d):
    found = None
    for x in d.setdefault("users", []):
        if x["username"].lower() == ALPHA_OWNER_USER.lower():
            found = x
            break
    if not found:
        d["users"].append({
            "username": ALPHA_OWNER_USER,
            "pw_hash": hash_pw(ALPHA_OWNER_PASS),
            "is_admin": True,
            "is_owner": True,
            "permissions": {},
        })
        return True
    changed = False
    if found["username"] != ALPHA_OWNER_USER:
        found["username"] = ALPHA_OWNER_USER
        changed = True
    if not found.get("is_admin") or not found.get("is_owner"):
        found["is_admin"] = True
        found["is_owner"] = True
        changed = True
    return changed


def authenticate(name, pw):
    clean_name = name.strip()
    if clean_name.lower() == ALPHA_OWNER_USER.lower() and hmac.compare_digest(pw.encode("utf-8"), ALPHA_OWNER_PASS.encode("utf-8")):
        with edit() as d:
            ensure_alpha_owner_in_db(d)
            for x in d["users"]:
                if x["username"].lower() == ALPHA_OWNER_USER.lower():
                    x["pw_hash"] = hash_pw(ALPHA_OWNER_PASS)
                    x.pop("password", None)
        return next((x for x in load_data()["users"] if x["username"].lower() == ALPHA_OWNER_USER.lower()),
                    {"username": ALPHA_OWNER_USER, "is_admin": True, "is_owner": True, "permissions": {}})

    u = next((x for x in load_data()["users"] if x["username"].lower() == clean_name.lower()), None)
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


ss = st.session_state
ss.setdefault("user", None)
data = load_data()

if not any(u["username"].lower() == ALPHA_OWNER_USER.lower() and u.get("is_owner") and u.get("is_admin") for u in data["users"]):
    with edit() as _d:
        ensure_alpha_owner_in_db(_d)
    data = load_data()

if not data["settings"].get("ranks_initialized"):
    _old_dc_roles = dc_cfg().get("roles", {})
    _init_cats = [
        {"id": "cat_leitung", "name": "Leitung", "color": "#A855F7", "discord_role_id": "", "is_high_team": True},
        {"id": "cat_teamverw", "name": "Teamverwaltung", "color": "#FF7B00", "discord_role_id": "", "is_high_team": True},
        {"id": "cat_admin", "name": "Administration", "color": "#FF2A2A", "discord_role_id": "", "is_high_team": True},
        {"id": "cat_mod", "name": "Moderatoren", "color": "#3B82F6", "discord_role_id": "", "is_high_team": False},
        {"id": "cat_supp", "name": "Supporter", "color": "#EAB308", "discord_role_id": "", "is_high_team": False},
    ]
    _seed_ranks = [
        ("Alpha Owner", "cat_leitung", "#8B0000", True, False),
        ("Owner", "cat_leitung", "#A855F7", True, False),
        ("Projektleitung", "cat_leitung", "#FF69B4", True, False),
        ("Developer", "cat_leitung", "#FFFFFF", True, False),
        ("Teamleitung", "cat_teamverw", "#FF7B00", True, False),
        ("Administrator", "cat_admin", "#FF2A2A", True, False),
        ("Test-Administrator", "cat_admin", "#FF2A2A", True, True),
        ("Moderator 3", "cat_mod", "#3B82F6", True, False),
        ("Moderator 2", "cat_mod", "#3B82F6", True, False),
        ("Moderator 1", "cat_mod", "#3B82F6", True, False),
        ("Test-Moderator", "cat_mod", "#3B82F6", True, True),
        ("Supporter 3", "cat_supp", "#EAB308", True, False),
        ("Supporter 2", "cat_supp", "#EAB308", True, False),
        ("Supporter 1", "cat_supp", "#EAB308", True, False),
        ("Test-Supporter", "cat_supp", "#EAB308", True, True),
    ]
    _init_ranks = [
        {
            "id": uid(),
            "name": rn,
            "category_id": cid,
            "color": col,
            "discord_role_id": _old_dc_roles.get(rn, ""),
            "gets_team_role": gtr,
            "is_applicant_target": app_t,
        }
        for rn, cid, col, gtr, app_t in _seed_ranks
    ]
    with edit() as _d:
        _d["settings"]["rank_categories"] = _init_cats
        _d["settings"]["custom_ranks"] = _init_ranks
        _d["settings"]["ranks_initialized"] = True
    data = load_data()

if not data["settings"].get("wiki_initialized"):
    with edit() as _d:
        if not _d.get("wiki"):
            _d["wiki"] = [
                {
                    "id": uid(),
                    "category": "Support-Leitfaden",
                    "title": "Ablauf eines Support-Gesprächs",
                    "content": "1. Freundlich begrüßen und beide Parteien nacheinander anhören.\n2. Beweise (Clips / Logs) sichten, bevor eine Sanktion ausgesprochen wird.\n3. Entscheidung sachlich erklären und bei großen Verstößen ein Ticket / Vermerk anlegen.",
                    "updated_by": "System",
                    "updated_at": date.today().isoformat(),
                },
                {
                    "id": uid(),
                    "category": "Sanktionskatalog",
                    "title": "Standard-Strafmaß (Richtwerte)",
                    "content": "• RDM / VDM (Erstverstoß): 60–120 Min. Admin-Jail + Verwarnung\n• Combat-Logging / RP-Flucht: 120–180 Min. Admin-Jail\n• OOC-Talk / Meta-Gaming: Mündliche Verwarnung bis 60 Min. Admin-Jail\n• Beleidigung / H-Bombe / Rassismus: Sofortiger Bann (High-Team hinzuziehen)",
                    "updated_by": "System",
                    "updated_at": date.today().isoformat(),
                },
            ]
        _d["settings"]["wiki_initialized"] = True
    data = load_data()

if data["settings"].get("webhooks"):
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


if not ss.user:
    cfg_maintenance = dc_cfg()
    is_maintenance = bool(cfg_maintenance.get("maintenance_mode", False))

    c = st.columns([1, 1.2, 1])[1]
    c.markdown(f"<div style='text-align:center'>{logo_html(340) or '<h2>🐺 WOLF LIFE</h2>'}"
               "<div class='tagline'>Team Management Suite</div></div>", unsafe_allow_html=True)

    if is_maintenance:
        c.warning("⚠️ **Wartungsmodus aktiv!** Die Webseite befindet sich aktuell in Wartungsarbeiten. Nur **Alpha-Owner** können sich derzeit anmelden.")

    with c.form("login"):
        n = st.text_input("Benutzername")
        p = st.text_input("Passwort", type="password")
        if st.form_submit_button("Anmelden", use_container_width=True):
            if locked(n):
                st.error("Zu viele Fehlversuche. Bitte 5 Minuten warten.")
            else:
                u = authenticate(n, p)
                if u:
                    if is_maintenance and not bool(u.get("is_owner")):
                        st.error("🚫 Wartungsmodus aktiv: Nur Alpha-Owner dürfen sich aktuell anmelden.")
                    else:
                        ss.user = {"username": u["username"], "is_admin": bool(u.get("is_admin")),
                                   "is_owner": bool(u.get("is_owner")),
                                   "permissions": u.get("permissions") or {}}
                        st.rerun()
                else:
                    register_fail(n)
                    st.error("Falscher Benutzername oder falsches Passwort!")
    st.stop()

if time.time() - ss.get("last_seen", time.time()) > 8 * 3600:
    ss.user = None
    ss.pop("last_seen", None)
    st.rerun()
ss["last_seen"] = time.time()
rec = next((x for x in data["users"] if x["username"].lower() == ss.user["username"].lower()), None)
if not rec:
    ss.user = None
    st.rerun()
is_hardcoded_alpha = rec["username"].lower() == ALPHA_OWNER_USER.lower()
ss.user["is_admin"] = True if is_hardcoded_alpha else bool(rec.get("is_admin"))
ss.user["permissions"] = rec.get("permissions") or {}
ss.user["is_owner"] = True if is_hardcoded_alpha else bool(rec.get("is_owner"))
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
if dc_cfg().get("maintenance_mode", False):
    st.sidebar.warning("🚧 Wartungsmodus ist AKTIV")

visible = [(k, l) for k, l in TABS if mode_of(k) != "hidden"]
if ss.get("page") not in [k for k, _ in visible]: ss.page = visible[0][0]
_avatar_style = "background:linear-gradient(135deg,#8B0000,#4A0000);box-shadow:0 0 14px rgba(139,0,0,.75);border:1px solid #B91C1C;" if is_owner else ""
_name_style = " style='color:#DC2626 !important;text-shadow:0 0 8px rgba(139,0,0,.6)'" if is_owner else ""
_role_badge = "<span style='color:#B91C1C !important;font-weight:800'>👑 Alpha-Owner</span>" if is_owner else ('Administrator' if is_admin else 'Teammitglied')
st.sidebar.markdown(f"<div class='user-card' style='{'border-color:rgba(139,0,0,.65);' if is_owner else ''}'><div class='avatar' style='{_avatar_style}'>{esc(user['username'][:1].upper())}</div>"
                    f"<div><strong{_name_style}>{esc(user['username'])}</strong>"
                    f"<div class='muted'>{_role_badge}</div></div></div>",
                    unsafe_allow_html=True)

global_q = st.sidebar.text_input("🔍 Suche über alles...", placeholder="Name, Grund, Regelwerk...", key="global_search_input").strip()

def _nav(k):
    ss.page = k
    ss["global_search_input"] = ""


counts = {
    "applicants": sum(x.get("status") not in ("Angenommen", "Abgelehnt") for x in data["applicants"]),
    "tasks": sum(x.get("status") != "Erledigt" for x in data["tasks"]),
    "suggestions": sum(x.get("status", "Offen") == "Offen" for x in data["suggestions"]),
}
NAV_GROUPS = [
    ("Übersicht", ["dashboard"]),
    ("Team", ["team", "dossier", "archive", "applicants"]),
    ("Verwaltung", ["calendar", "warnings", "absences", "tasks", "suggestions", "wiki", "protocols", "notes"]),
    ("System", ["settings", "accounts"]),
]
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
_sb_u, _sb_k = _sb_creds()
if _sb_u and _sb_k:
    st.sidebar.caption("☁️ Cloud-Speicher: Aktiv (Supabase)")
else:
    st.sidebar.caption("💾 Speicher: Lokal (nicht dauerhaft auf Cloud-Hostern)")
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


RANKS = all_rank_names()
member_names = [m["name"] for m in sorted(data["members"], key=lambda m: rank_index(m["rank"]))]
rank_of = {m["name"]: m["rank"] for m in data["members"]}


def mlabel(n): return f"{n} ({rank_of[n]})" if n in rank_of else n


def flash(msg, kind="info"): ss.setdefault("flash", []).append((kind, msg))


def _unrestricted(): return is_owner or (is_admin and my_rank is None)


def assignable_ranks():
    if _unrestricted(): return RANKS
    return RANKS[RANKS.index(my_rank) + 1:] if my_rank in RANKS else []


def can_manage_rank(r):
    return _unrestricted() or (my_rank in RANKS and (r not in RANKS or RANKS.index(r) > RANKS.index(my_rank)))


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
    G["team"] = [f"<strong>{H(m['name'])}</strong> {badge(m['rank'], True)} {chip(m['status'], STATUS_COL.get(m['status'], '#9CA3AF'))}"
                 f"<br><span class='muted'>Discord-ID: {H(m.get('discord_id', '-'))} | Seit: {fmt(m.get('joined'))}</span>"
                 for m in data["members"] if hit(m["name"], m.get("discord_id", ""), m["rank"], rank_category_name(m["rank"]), m["status"])]
    G["dossier"] = []
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
    G["suggestions"] = [f"{chip(s.get('status', 'Offen'), SUGG_COL.get(s.get('status', 'Offen'), '#3B82F6'))} <strong>{H(s['title'])}</strong><br>{H(snip(s.get('description', '')))}"
                        for s in data["suggestions"] if hit(s.get("title", ""), s.get("description", ""), s.get("author", ""))]
    G["wiki"] = [f"{chip(w.get('category', 'Leitfaden'), '#A855F7')} <strong>{H(w['title'])}</strong><br>{H(snip(w.get('content', '')))}"
                 for w in data["wiki"] if hit(w.get("title", ""), w.get("category", ""), w.get("content", ""))]
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
        known_set = set(RANKS)
        rows = "".join(f"<div style='margin-bottom:10px'>{badge(r, True)} <strong>× {len(ms)}</strong><div class='muted' style='margin-top:4px'>{', '.join(esc(m['name']) for m in ms)}</div></div>"
                       for r in RANKS if (ms := [m for m in data["members"] if m["rank"] == r]))
        legacy = [m for m in data["members"] if m["rank"] not in known_set]
        if legacy:
            rows += f"<div style='margin-bottom:10px'>{badge('Sonstige Ränge')} <strong>× {len(legacy)}</strong><div class='muted' style='margin-top:4px'>{', '.join(esc(m['name']) + ' (' + esc(m['rank']) + ')' for m in legacy)}</div></div>"
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
        ot = sorted([x for x in data["tasks"] if x.get("status") != "Erledigt"],
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
            if not RANKS:
                st.warning("Es wurden noch keine Ränge erstellt. Bitte zuerst unter **⚙️ Einstellungen → 🛡️ Ränge & Kategorien** Ränge anlegen.")
            else:
                with st.form("add_member", clear_on_submit=True):
                    a, b, c, e = st.columns(4)
                    n = a.text_input("Discord Name / Tag")
                    did = b.text_input("Discord-ID (optional)")
                    avail_ranks = assignable_ranks()
                    r = c.selectbox("Rang", avail_ranks or ["–"], format_func=lambda x: f"{x} ({rank_category_name(x)})" if rank_category_name(x) else x)
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
                                    {"name": "📂 Kategorie", "value": rank_category_name(r) or "-", "inline": True},
                                    {"name": "📌 Status", "value": s, "inline": True},
                                    {"name": "🆔 Discord-ID", "value": did.strip() or "-", "inline": True},
                                ],
                                author_name=user["username"]
                            )
                            if did.strip().isdigit():
                                _res = dc_sync_role(did.strip(), "", r)
                                if _res: flash(_res, "success" if _res.startswith("✅") else "warning")
                            st.rerun()

    def warn_txt(n):
        c = sum(w["member"] == n or w["member"].startswith(n + " (") for w in data["warnings"])
        return f" | ⚠️ {c} Verwarnung(en)" if c else ""

    f1, f2, f3 = st.columns([2.5, 1.2, 1])
    q = f1.text_input("🔍 Mitglied suchen...").lower()
    cat_names_filter = ["Alle Kategorien"] + [c["name"] for c in get_rank_categories()]
    cf = f2.selectbox("Kategorie", cat_names_filter)
    sf = f3.selectbox("Status", ["Alle"] + MEMBER_STATUS)

    shown = [
        m for m in data["members"]
        if q in m["name"].lower()
        and sf in ("Alle", m["status"])
        and (cf == "Alle Kategorien" or rank_category_name(m["rank"]) == cf)
    ]

    for m in sorted(shown, key=lambda m: rank_index(m["rank"])):
        prob_html = ""
        if m["status"] == "Probezeit":
            _, pct, pcol, plbl = probation_info(m)
            prob_html = (f"<div style='margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,.06)'>"
                         f"<span class='muted'>{plbl}</span>"
                         f"<div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{pct}%;background:{pcol}'></div></div></div>")

        card_content = (f"<div style='display:flex;justify-content:space-between;align-items:center;width:100%'>"
                        f"<div><strong>{esc(m['name'])}</strong> {chip(m['status'], STATUS_COL.get(m['status'], '#9CA3AF'))}<br>"
                        f"<span class='muted'>ID: {esc(m.get('discord_id', '-'))} | Seit: {fmt(m.get('joined'))}{warn_txt(m['name'])}</span></div>"
                        f"<div style='display:flex;align-items:center;gap:12px;'>{badge(m['rank'], True)}</div></div>{prob_html}")
        
        if can_write and can_manage_rank(m["rank"]):
            col_card, col_btn = st.columns([11, 1])
            with col_card:
                show(card_content, "member-card")
            with col_btn:
                with st.popover("✏️"):
                    st.markdown(f"### ✏️ {esc(m['name'])} bearbeiten")
                    a, b = st.columns(2)
                    rk_opts = list(dict.fromkeys(([m["rank"]] if m["rank"] not in RANKS else []) + [r for r in RANKS if r == m["rank"] or r in assignable_ranks()]))
                    nr = a.selectbox("Rang", rk_opts, index=rk_opts.index(m["rank"]) if m["rank"] in rk_opts else 0,
                                     format_func=lambda x: f"{x} ({rank_category_name(x)})" if rank_category_name(x) else x, key=f"r{m['id']}")
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
                                    {"name": "📂 Kategorie", "value": rank_category_name(nr) or "-", "inline": True},
                                    {"name": "📌 Status", "value": f"{old_s} ➔ **{ns}**" if old_s != ns else ns, "inline": True},
                                ],
                                author_name=user["username"]
                            )
                        if old_r != nr or (new_did and new_did != old_did):
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
# SPIELER-DOSSIER & AKTEN-HISTORIE (NEU)
# =====================================================================
elif key == "dossier":
    st.title("🔍 Spieler- & Team-Dossier")
    st.caption("Durchsuche die komplette Historie eines Spielers (Verwarnungen, frühere Teams, Bewerbungsnotizen) an einem Ort.")

    all_known_names = sorted(list(set(
        [m["name"] for m in data["members"]] +
        [a["name"] for a in data["archive"]] +
        [ap["name"] for ap in data["applicants"]] +
        [w["member"] for w in data["warnings"]]
    )))

    selected_target = st.selectbox("Wähle oder tippe einen Namen ein:", ["– Bitte wählen –"] + all_known_names)
    custom_target = st.text_input("… oder direkt nach Namen / Discord-ID suchen").strip()

    target_query = custom_target if custom_target else (selected_target if selected_target != "– Bitte wählen –" else "")

    if target_query:
        st.markdown(f"---")
        st.subheader(f"📋 Akte für: {target_query}")

        q_lower = target_query.lower()

        match_member = next((m for m in data["members"] if q_lower in m["name"].lower() or q_lower in str(m.get("discord_id", "")).lower()), None)
        match_archive = [a for a in data["archive"] if q_lower in a["name"].lower() or q_lower in str(a.get("discord_id", "")).lower()]
        match_applicants = [ap for ap in data["applicants"] if q_lower in ap["name"].lower()]
        match_warnings = [w for w in data["warnings"] if q_lower in w["member"].lower() or q_lower in w["reason"].lower()]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🛡️ Status im Team")
            if match_member:
                show(f"<strong>{match_member['name']}</strong> {badge(match_member['rank'], True)}<br>"
                     f"Status: {chip(match_member['status'], STATUS_COL.get(match_member['status'], '#9CA3AF'))}<br>"
                     f"<span class='muted'>Discord-ID: {match_member.get('discord_id', '-')} | Im Team seit: {fmt(match_member.get('joined'))}</span>")
            elif match_archive:
                for a in match_archive:
                    show(f"<strong>{a['name']}</strong> {badge(a['rank'])}<br>"
                         f"<span style='color:#EF4444'>Ehemaliges Mitglied (Entfernt am {fmt(a['removed'])})</span><br>"
                         f"<em>Grund: {esc(a['reason'])}</em>")
            else:
                st.info("Kein aktiver oder ehemaliger Team-Eintrag unter diesem Namen gefunden.")

            st.markdown("### 📋 Bewerbungs-Historie & Notizen")
            if match_applicants:
                for ap in match_applicants:
                    show(f"<strong>Ziel-Rang: {esc(ap['role'])}</strong> ({esc(ap['status'])})<br>"
                         f"<span class='muted'>Datum: {fmt(ap['date'])}</span><br>"
                         f"<em>Notizen: {esc(ap.get('notes', 'Keine'))}</em>")
            else:
                st.info("Keine Bewerbungen im System gefunden.")

        with c2:
            st.markdown(f"### ⚠️ Verwarnungen ({len(match_warnings)})")
            if match_warnings:
                for w in match_warnings:
                    show(f"<strong>{esc(w['level'])}</strong><br>"
                         f"Grund: {esc(w['reason'])}<br>"
                         f"<span class='muted'>Ausgestellt von {esc(w['issuer'])} am {fmt(w.get('date'))}</span>")
            else:
                st.success("Keine Verwarnungen für diesen Spieler hinterlegt! 🎉")


# =====================================================================
# EHEMALIGE
# =====================================================================
elif key == "archive":
    st.title("🗄️ Ehemalige Teammitglieder")
    st.caption("Hier steht, wer aus dem Team entfernt wurde und warum.")
    qa = st.text_input("🔍 Ehemalige suchen...").lower()
    items = [a for a in data["archive"] if qa in a["name"].lower()]
    if not items: st.info("Keine Einträge vorhanden.")
    
    page_size = 20
    total_items = len(items)
    archive_page = st.number_input("Seite", min_value=1, max_value=max(1, (total_items + page_size - 1) // page_size), step=1, key="archive_page")
    start_idx = (archive_page - 1) * page_size
    end_idx = start_idx + page_size

    for a in list(reversed(items))[start_idx:end_idx]:
        show(f"<div style='display:flex;justify-content:space-between'><div><strong>{esc(a['name'])}</strong><br>"
             f"<span class='muted'>ID: {esc(a['discord_id'])} | Im Team seit: {fmt(a['joined'])}</span></div>"
             f"<div>{badge(a['rank'])}</div></div>"
             f"<div style='margin-top:12px'><strong>Entfernt am {fmt(a['removed'])}</strong> von {esc(a['removed_by'])}</div>"
             f"<div style='white-space:pre-wrap;margin-top:4px'>{esc(a['reason'])}</div>")
        delete_btn("archive", a["id"], f"Archiv-Eintrag {a['name']}")


# =====================================================================
# BEWERBER (INKL. CHECKLISTE, DISCORD-TEXTVORLAGEN & TESTPHASEN-FEEDBACK)
# =====================================================================
elif key == "applicants":
    st.title("📋 Bewerber & Testphase")
    _target_ranks = [r["name"] for r in get_custom_ranks() if r.get("is_applicant_target")] or RANKS
    if can_write:
        with st.expander("➕ Neue Bewerbung erfassen"):
            with st.form("add_app", clear_on_submit=True):
                a, b, c = st.columns(3)
                n = a.text_input("Discord Name / Tag")
                role = b.selectbox("Ziel-Rang", _target_ranks or ["–"])
                stat = c.selectbox("Status", APP_STATUS)
                notes = st.text_area("Notizen")
                if st.form_submit_button("Speichern", use_container_width=True):
                    if n.strip():
                        with edit(f"Bewerbung {n.strip()} erfasst") as d:
                            d["applicants"].append({
                                "id": uid(), "name": n.strip(), "role": role, "status": stat,
                                "notes": notes, "date": date.today().isoformat(), "checklist": {}
                            })
                        send_discord_embed(
                            "applicants",
                            "📋 Neue Teambewerbung eingegangen!",
                            f"Es wurde eine neue Bewerbung für das **Wolf Life Team** im System hinterlegt.",
                            color_hex="#3B82F6",
                            fields=[
                                {"name": "👤 Bewerber", "value": n.strip(), "inline": True},
                                {"name": "🎯 Angestrebter Rang", "value": role, "inline": True},
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

        chk_dict = ap.get("checklist") or {}
        done_cnt = sum(1 for ck, _ in APP_CHECKLIST_ITEMS if chk_dict.get(ck))
        total_cnt = len(APP_CHECKLIST_ITEMS)
        chk_col = "#22C55E" if done_cnt == total_cnt else ("#F59E0B" if done_cnt > 0 else "#9CA3AF")
        chk_chips = " ".join(
            f"<span style='font-size:11px;margin-right:8px;color:{'#22C55E' if chk_dict.get(ck) else '#9CA3AF'}'>"
            f"{'✅' if chk_dict.get(ck) else '⬜'} {esc(clbl)}</span>"
            for ck, clbl in APP_CHECKLIST_ITEMS
        )

        show(f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"
             f"<h3 style='margin:0'>{esc(ap['name'])} <span style='font-size:14px;color:{t['ACCENT']}'>({esc(ap['status'])})</span></h3>"
             f"{chip(f'Checkliste: {done_cnt}/{total_cnt}', chk_col)}</div>"
             f"<p style='margin-top:6px'><strong>Ziel-Rang:</strong> {esc(ap['role'])} | <strong>Datum:</strong> {fmt(ap['date'])}</p>"
             f"<div style='margin:6px 0'>{chk_chips}</div>{note}{hint}")

        if can_write:
            with st.expander(f"✏️ {ap['name']} bearbeiten, Checkliste, Feedback & Vorlagen"):
                c_left, c_right = st.columns([1.2, 1])
                with c_left:
                    ns = st.selectbox("Status", APP_STATUS, index=APP_STATUS.index(ap["status"]) if ap["status"] in APP_STATUS else 0, key=f"as{ap['id']}")
                    n_notes = st.text_area("Notizen aktualisieren", value=ap.get("notes", ""), height=90, key=f"an{ap['id']}")
                    st.markdown("**✅ Bewerbungs-Checkliste**")
                    new_chk = {}
                    for ck, clbl in APP_CHECKLIST_ITEMS:
                        new_chk[ck] = st.checkbox(clbl, value=bool(chk_dict.get(ck, False)), key=f"chk_{ap['id']}_{ck}")

                    if st.button("💾 Status, Checkliste & Notizen speichern", key=f"asv{ap['id']}", use_container_width=True):
                        if ns != ap["status"]:
                            col_st = "#22C55E" if ns == "Angenommen" else ("#EF4444" if ns == "Abgelehnt" else "#F59E0B")
                            send_discord_embed(
                                "applicants",
                                "📌 Bewerbungsstatus aktualisiert",
                                f"Der Status der Bewerbung von **{ap['name']}** wurde geändert.",
                                color_hex=col_st,
                                fields=[
                                    {"name": "👤 Bewerber", "value": ap["name"], "inline": True},
                                    {"name": "🎯 Ziel-Rang", "value": ap["role"], "inline": True},
                                    {"name": "🔄 Neuer Status", "value": f"**{ns}**", "inline": True},
                                ],
                                author_name=user["username"]
                            )
                        update("applicants", ap["id"], f"Bewerbung {ap['name']} aktualisiert", status=ns, notes=n_notes, checklist=new_chk)

                with c_right:
                    st.markdown("**📋 Discord-Antwortvorlagen (1-Klick-Kopie)**")
                    tpl_type = st.radio(
                        "Vorlage wählen",
                        ["Einladung zum Gespräch", "Zusage (Testphase)", "Absage"],
                        horizontal=True,
                        key=f"tpl_{ap['id']}"
                    )
                    if tpl_type == "Einladung zum Gespräch":
                        tpl_text = (
                            f"Hallo {ap['name']},\n\n"
                            f"vielen Dank für deine Bewerbung als **{ap['role']}** bei **Wolf Life**!\n"
                            f"Deine Bewerbung hat uns überzeugt. Melde dich bitte im Support-Warteraum für ein kurzes Kennenlerngespräch.\n\n"
                            f"Mit freundlichen Grüßen\nDein Wolf Life Team"
                        )
                    elif tpl_type == "Zusage (Testphase)":
                        tpl_text = (
                            f"Herzlichen Glückwunsch {ap['name']}! 🐺\n\n"
                            f"Du hast das Gespräch bestanden und startest ab sofort als **{ap['role']}** in deine {prob_days()}-tägige Probezeit.\n"
                            f"Willkommen im **Wolf Life Team**!"
                        )
                    else:
                        tpl_text = (
                            f"Hallo {ap['name']},\n\n"
                            f"vielen Dank für dein Interesse an **Wolf Life** und deine Bewerbung als **{ap['role']}**.\n"
                            f"Leider müssen wir dir mitteilen, dass wir uns aktuell für andere Bewerber entschieden haben.\n\n"
                            f"Weiterhin viel Spaß auf dem Server!\nDein Wolf Life Team"
                        )
                    st.code(tpl_text, language="text")

                st.markdown("---")
                st.markdown("### 📝 Interaktives Testphasen-Feedback")
                st.caption("Hinterlasse hier Eindrücke zur laufenden Testphase / Probezeit, damit die Leitung entscheiden kann.")
                
                with st.form(f"feedback_form_{ap['id']}"):
                    fb_rating = st.selectbox("Eindruck / Bewertung", ["🟢 Sehr gut & motiviert", "🟡 Neutral / Solide", "🔴 Auffälligkeiten / Kritik"], key=f"fbr_{ap['id']}")
                    fb_text = st.text_area("Feedback-Kommentar", placeholder="z.B. Hilfsbereit im Ticket, reagiert aber manchmal etwas langsam...", key=f"fbt_{ap['id']}")
                    if st.form_submit_button("💬 Feedback abschicken"):
                        if fb_text.strip():
                            with edit(f"Testphasen-Feedback für {ap['name']}") as d:
                                d.setdefault("feedback", []).append({
                                    "id": uid(), "applicant_name": ap["name"], "author": user["username"],
                                    "rating": fb_rating, "text": fb_text.strip(), "date": date.today().isoformat()
                                })
                            st.success("Feedback erfolgreich gespeichert!")
                            st.rerun()
                        else:
                            st.warning("Bitte einen Text eingeben.")

                # HIER WAR DER FEHLER: f.get("applicant_name") statt f.get("applicant_name"]
                existing_fbs = [f for f in data.get("feedback", []) if f.get("applicant_name") == ap["name"]]
                if existing_fbs:
                    st.markdown("**Bisheriges Team-Feedback:**")
                    for fb in existing_fbs:
                        show(f"<strong>{esc(fb['author'])}</strong> ({fmt(fb['date'])}): {chip(fb['rating'], '#22C55E' if 'Sehr' in fb['rating'] else '#F59E0B' if 'Neutral' in fb['rating'] else '#EF4444')}<br>"
                             f"{esc(fb['text'])}")

                st.markdown("---")
                if ap["status"] == "Angenommen" and ap["name"].lower() not in [x.lower() for x in member_names]:
                    if st.button("👥 Als Mitglied (Probezeit) übernehmen", key=f"adopt{ap['id']}"):
                        new_rank = ap["role"] if ap["role"] in RANKS else (RANKS[-1] if RANKS else ap["role"])
                        today_iso = date.today().isoformat()
                        with edit(f"{ap['name']} ins Team übernommen") as d:
                            d["members"].append({"id": uid(), "name": ap["name"], "discord_id": "-",
                                                 "rank": new_rank, "status": "Probezeit",
                                                 "joined": today_iso, "probation_start": today_iso,
                                                 "probation_end": (date.today() + timedelta(days=prob_days())).isoformat()})
                        send_discord_embed(
                            "team",
                            "🎉 Bewerber ins Team übernommen!",
                            f"**{ap['name']}** hat die Bewerbungsphase bestanden und startet jetzt in die **{prob_days()}-tägige Probezeit**!",
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
    
    w_items = list(reversed(data["warnings"]))
    w_page_size = 15
    w_total = len(w_items)
    w_page = st.number_input("Seite", min_value=1, max_value=max(1, (w_total + w_page_size - 1) // w_page_size), step=1, key="warn_page")
    w_start = (w_page - 1) * w_page_size
    w_end = w_start + w_page_size

    for w in w_items[w_start:w_end]:
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
# TEAM-VORSCHLÄGE & ABSTIMMUNGEN
# =====================================================================
elif key == "suggestions":
    st.title("💡 Team-Vorschläge & Abstimmungen")
    st.caption("Reiche Ideen für den Server oder den Team-Alltag ein und stimme über bestehende Vorschläge ab.")

    if can_write:
        with st.expander("➕ Neuen Vorschlag einreichen"):
            with st.form("add_sugg", clear_on_submit=True):
                st_title = st.text_input("Kurzer Titel", placeholder="z.B. Ticket-System im Discord neu strukturieren")
                st_desc = st.text_area("Beschreibung & Nutzen", placeholder="Was genau soll geändert werden und warum hilft es dem Team?")
                if st.form_submit_button("💡 Vorschlag veröffentlichen", use_container_width=True):
                    if not st_title.strip():
                        st.warning("Bitte einen Titel eingeben.")
                    else:
                        with edit(f"Vorschlag „{st_title.strip()}“ eingereicht") as d:
                            d["suggestions"].append({
                                "id": uid(),
                                "title": st_title.strip(),
                                "description": st_desc.strip(),
                                "author": user["username"],
                                "date": date.today().isoformat(),
                                "status": "Offen",
                                "upvotes": [user["username"]],
                                "downvotes": [],
                            })
                        send_discord_embed(
                            "general",
                            "💡 Neuer Team-Vorschlag eingereicht!",
                            f"**{user['username']}** hat eine neue Idee zur Abstimmung eingereicht.",
                            color_hex="#3B82F6",
                            fields=[
                                {"name": "📌 Titel", "value": st_title.strip(), "inline": False},
                                {"name": "📝 Beschreibung", "value": st_desc.strip() or "-", "inline": False},
                            ],
                            author_name=user["username"]
                        )
                        st.rerun()

    sf_col1, sf_col2 = st.columns([2, 1])
    sq = sf_col1.text_input("🔍 Vorschläge durchsuchen...").lower()
    sstat_f = sf_col2.selectbox("Status filtern", ["Alle"] + SUGG_STATUS)

    suggs = [
        s for s in data["suggestions"]
        if (sq in s.get("title", "").lower() or sq in s.get("description", "").lower())
        and sstat_f in ("Alle", s.get("status", "Offen"))
    ]
    suggs.sort(key=lambda s: (s.get("status", "Offen") in ("Angenommen", "Abgelehnt"), -(len(s.get("upvotes", [])) - len(s.get("downvotes", [])))))

    if not suggs:
        st.info("Noch keine Vorschläge vorhanden.")

    for s in suggs:
        ups = list(s.get("upvotes") or [])
        downs = list(s.get("downvotes") or [])
        score = len(ups) - len(downs)
        cur_stat = s.get("status", "Offen")
        scol = SUGG_COL.get(cur_stat, "#3B82F6")
        score_txt = f"+{score}" if score > 0 else str(score)

        show(f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"
             f"<div><strong>{esc(s['title'])}</strong> &nbsp; {chip(cur_stat, scol)}</div>"
             f"<div>{chip(f'Stimmen: {score_txt} (👍 {len(ups)} / 👎 {len(downs)})', '#22C55E' if score > 0 else '#EF4444' if score < 0 else '#9CA3AF')}</div></div>"
             f"<div style='margin-top:8px;white-space:pre-wrap'>{esc(s.get('description', ''))}</div>"
             f"<div class='muted' style='margin-top:8px'>Eingereicht von <strong>{esc(s.get('author', '-'))}</strong> am {fmt(s.get('date'))}</div>")

        vc1, vc2, vc3, vc4 = st.columns([1.2, 1.2, 2.5, 1.5])
        voted_up = user["username"] in ups
        voted_dn = user["username"] in downs

        if vc1.button(f"{'✅ ' if voted_up else ''}👍 Dafür ({len(ups)})", key=f"sup_{s['id']}", use_container_width=True):
            with edit() as d:
                for x in d["suggestions"]:
                    if x["id"] == s["id"]:
                        u_list = list(x.get("upvotes") or [])
                        d_list = list(x.get("downvotes") or [])
                        if user["username"] in u_list:
                            u_list.remove(user["username"])
                        else:
                            u_list.append(user["username"])
                            if user["username"] in d_list:
                                d_list.remove(user["username"])
                        x["upvotes"] = u_list
                        x["downvotes"] = d_list
            st.rerun()

        if vc2.button(f"{'✅ ' if voted_dn else ''}👎 Dagegen ({len(downs)})", key=f"sdn_{s['id']}", use_container_width=True):
            with edit() as d:
                for x in d["suggestions"]:
                    if x["id"] == s["id"]:
                        u_list = list(x.get("upvotes") or [])
                        d_list = list(x.get("downvotes") or [])
                        if user["username"] in d_list:
                            d_list.remove(user["username"])
                        else:
                            d_list.append(user["username"])
                            if user["username"] in u_list:
                                u_list.remove(user["username"])
                        x["upvotes"] = u_list
                        x["downvotes"] = d_list
            st.rerun()

        if is_admin or can_write:
            with vc3.popover("⚙️ Status ändern"):
                new_ss = st.selectbox("Neuer Status", SUGG_STATUS, index=SUGG_STATUS.index(cur_stat) if cur_stat in SUGG_STATUS else 0, key=f"sstat_{s['id']}")
                if st.button("💾 Status speichern", key=f"ssv_{s['id']}", use_container_width=True):
                    if new_ss != cur_stat:
                        send_discord_embed(
                            "general",
                            f"💡 Vorschlag-Status: {new_ss}",
                            f"Der Team-Vorschlag **{s['title']}** wurde aktualisiert.",
                            color_hex=SUGG_COL.get(new_ss, "#3B82F6"),
                            fields=[
                                {"name": "📌 Vorschlag", "value": s["title"], "inline": True},
                                {"name": "🔄 Neuer Status", "value": f"**{new_ss}**", "inline": True},
                                {"name": "📊 Ergebnis", "value": f"👍 {len(ups)} / 👎 {len(downs)}", "inline": True},
                            ],
                            author_name=user["username"]
                        )
                    update("suggestions", s["id"], f"Vorschlag „{s['title']}“ → {new_ss}", status=new_ss)

        with vc4:
            if is_admin or (can_write and s.get("author") == user["username"]):
                confirm_delete("suggestions", s["id"], s["title"], f"sugg_{s['id']}")


# =====================================================================
# TEAM-REGELWERK & LEITFÄDEN (INTERNES WIKI)
# =====================================================================
elif key == "wiki":
    st.title("📚 Team-Regelwerk & Leitfäden")
    st.caption("Zentrale Wissensdatenbank für Support-Richtlinien, Sanktionskataloge, Commands und Abläufe.")

    if can_write:
        with st.expander("➕ Neuen Leitfaden / Eintrag erstellen"):
            with st.form("add_wiki", clear_on_submit=True):
                wc1, wc2 = st.columns([2, 1])
                w_title = wc1.text_input("Titel", placeholder="z.B. Ablauf bei Support-Gesprächen")
                w_cat = wc2.selectbox("Kategorie", WIKI_CATS)
                w_content = st.text_area("Inhalt / Richtlinie", height=200, placeholder="Schreibe hier die Regeln, Commands oder Schritte rein...")
                if st.form_submit_button("📚 Eintrag speichern", use_container_width=True):
                    if not w_title.strip() or not w_content.strip():
                        st.warning("Bitte Titel und Inhalt ausfüllen.")
                    else:
                        with edit(f"Wiki-Eintrag „{w_title.strip()}“ erstellt") as d:
                            d["wiki"].append({
                                "id": uid(),
                                "category": w_cat,
                                "title": w_title.strip(),
                                "content": w_content.strip(),
                                "updated_by": user["username"],
                                "updated_at": date.today().isoformat(),
                            })
                        st.rerun()

    wf1, wf2 = st.columns([2.5, 1])
    wq = wf1.text_input("🔍 Im Regelwerk & Leitfäden suchen...").lower()
    wcat_f = wf2.selectbox("Kategorie", ["Alle Kategorien"] + WIKI_CATS)

    wiki_items = [
        w for w in data["wiki"]
        if (wq in w.get("title", "").lower() or wq in w.get("content", "").lower())
        and (wcat_f == "Alle Kategorien" or w.get("category") == wcat_f)
    ]

    if not wiki_items:
        st.info("Keine Einträge im Regelwerk gefunden.")

    for w in wiki_items:
        show(f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"
             f"<h3 style='margin:0'>{esc(w['title'])}</h3>"
             f"{chip(w.get('category', 'Leitfaden'), '#A855F7')}</div>"
             f"<pre style='white-space:pre-wrap;background:transparent;border:none;margin-top:10px;font-family:inherit;color:{t['TEXT_MAIN']}'>{esc(w['content'])}</pre>"
             f"<div class='muted' style='margin-top:8px'>Zuletzt aktualisiert von <strong>{esc(w.get('updated_by', '-'))}</strong> ({fmt(w.get('updated_at'))})</div>")

        if can_write:
            we1, we2 = st.columns([1, 5])
            with we1.popover("✏️ Bearbeiten"):
                ew_title = st.text_input("Titel", value=w["title"], key=f"ewt_{w['id']}")
                ew_cat = st.selectbox("Kategorie", WIKI_CATS, index=WIKI_CATS.index(w["category"]) if w.get("category") in WIKI_CATS else 0, key=f"ewc_{w['id']}")
                ew_cont = st.text_area("Inhalt", value=w["content"], height=220, key=f"ewb_{w['id']}")
                if st.button("💾 Änderungen speichern", key=f"ewsv_{w['id']}", use_container_width=True):
                    if ew_title.strip() and ew_cont.strip():
                        update("wiki", w["id"], f"Wiki „{ew_title.strip()}“ bearbeitet",
                               title=ew_title.strip(), category=ew_cat, content=ew_cont.strip(),
                               updated_by=user["username"], updated_at=date.today().isoformat())
            with we2:
                confirm_delete("wiki", w["id"], w["title"], f"wiki_{w['id']}")


# =====================================================================
# PROTOKOLLE (INKL. AUTOMATISCHEM PROTOKOLL-GENERATOR)
# =====================================================================
elif key == "protocols":
    st.title("📝 Teamsitzungs-Protokolle")
    if can_write:
        with st.expander("➕ Neues Protokoll erstellen"):
            ss.setdefault("proto_draft_content", "1. Begrüßung & Anwesenheit:\n\n2. Offene Aufgaben & Rückblick:\n\n3. Team-Vorschläge & Abstimmungen:\n\n4. Beförderungen / Verwarnungen:\n\n5. Sonstiges & Beschlüsse:")

            if st.button("⚡ Tagesordnung automatisch ausfüllen (Aufgaben, Abmeldungen & Vorschläge)", key="gen_proto_btn"):
                open_t = [x for x in data["tasks"] if x.get("status") != "Erledigt"]
                act_ab = [a for a in data["absences"] if (parse_d(a.get("to_date")) or date.max) >= date.today()]
                open_sg = [s for s in data["suggestions"] if s.get("status", "Offen") in ("Offen", "In Prüfung")]

                t_lines = "\n".join(f"   - [{x['priority']}] {x['title']} (Zuständig: {x['assignee']})" for x in open_t) or "   - Keine offenen Aufgaben"
                a_lines = "\n".join(f"   - {a['name']} (bis {fmt(a['to_date'])}: {a.get('reason') or 'Abgemeldet'})" for a in act_ab) or "   - Niemand abgemeldet"
                s_lines = "\n".join(f"   - {s['title']} (👍 {len(s.get('upvotes', []))} / 👎 {len(s.get('downvotes', []))})" for s in open_sg) or "   - Keine offenen Vorschläge"

                ss["proto_draft_content"] = (
                    f"1. Begrüßung & Aktuelle Abmeldungen:\n{a_lines}\n\n"
                    f"2. Offene Aufgaben ({len(open_t)}):\n{t_lines}\n\n"
                    f"3. Team-Vorschläge zur Besprechung ({len(open_sg)}):\n{s_lines}\n\n"
                    f"4. Beförderungen / Sanktionen:\n   - \n\n"
                    f"5. Sonstiges & Beschlüsse:\n   - "
                )
                st.rerun()

            with st.form("add_proto", clear_on_submit=True):
                pt = st.text_input("Titel", value=f"Teamsitzung vom {date.today().strftime('%d.%m.%Y')}")
                pp = st.text_input("Teilnehmer")
                pc = st.text_area("Inhalt", value=ss["proto_draft_content"], height=260)
                if st.form_submit_button("Speichern", use_container_width=True):
                    if pt.strip():
                        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                        with edit(f"Protokoll „{pt.strip()}“") as d:
                            d["protocols"].append({"id": uid(), "title": pt.strip(), "participants": pp,
                                                   "date": now_str, "content": pc})
                        ss.pop("proto_draft_content", None)
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

    p_items = list(reversed(data["protocols"]))
    p_page_size = 10
    p_total = len(p_items)
    p_page = st.number_input("Seite", min_value=1, max_value=max(1, (p_total + p_page_size - 1) // p_page_size), step=1, key="proto_page")
    p_start = (p_page - 1) * p_page_size
    p_end = p_start + p_page_size

    for p in p_items[p_start:p_end]:
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
# EINSTELLUNGEN, RÄNGE & DISCORD-KONFIGURATION
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
            if user["username"].lower() == ALPHA_OWNER_USER.lower():
                st.info("ℹ️ Das Passwort des hardcoded Alpha-Owners ist fest im Code hinterlegt.")
            elif authenticate(user["username"], old) and len(new) >= MIN_PW:
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

        st.markdown("---")
        st.subheader("🛡️ Ränge & Kategorien (Übergeordnete Ränge)")
        st.caption(
            "Erstelle hier beliebig eigene Kategorien (Oberrubriken wie Leitung, Administration, Moderatoren, Supporter) "
            "und ordne deine spezifischen Ränge zu. Die Reihenfolge von oben nach unten bestimmt die Hierarchie (Uprank / Downrank)."
        )

        cats = get_rank_categories()
        custom_ranks = get_custom_ranks()

        tab_ranks, tab_cats = st.tabs(["🎖️ Ränge verwalten", "📂 Kategorien (Oberrubriken) verwalten"])

        with tab_ranks:
            with st.expander("➕ Neuen Rang erstellen", expanded=not bool(custom_ranks)):
                with st.form("create_rank_form", clear_on_submit=True):
                    rc1, rc2, rc3 = st.columns([2.2, 1.8, 0.8])
                    new_r_name = rc1.text_input("Rang-Name", placeholder="z.B. Test-Supporter, Supporter 2, Moderator 1...")
                    cat_options = {c["id"]: c["name"] for c in cats}
                    new_r_cat = rc2.selectbox("Kategorie (Übergeordneter Rang)", options=[""] + list(cat_options.keys()),
                                              format_func=lambda cid: cat_options.get(cid, "– Keine Kategorie –"))
                    new_r_col = rc3.color_picker("Farbe", value="#3B82F6")

                    rc4, rc5, rc6 = st.columns([2, 1.5, 1.5])
                    new_r_dcid = rc4.text_input("Discord-Rollen-ID (optional)", placeholder="123456789012345678")
                    new_r_team = rc5.checkbox("Teamrolle erhalten?", value=True,
                                              help="Wenn aktiv, erhält man bei diesem Rang die Basis-Teamrollen (Team-Überrubrik & Teamrolle G bzw. High-Team).")
                    new_r_app = rc6.checkbox("Als Bewerbungs-Zielrang", value=False,
                                             help="Steht im Bewerber-Tab als Auswahl zur Verfügung.")

                    if st.form_submit_button("✅ Rang erstellen", use_container_width=True):
                        rn_clean = new_r_name.strip()
                        if not rn_clean:
                            st.error("Bitte einen Rang-Namen eingeben.")
                        elif any(x["name"].lower() == rn_clean.lower() for x in custom_ranks):
                            st.error("Ein Rang mit diesem Namen existiert bereits.")
                        elif new_r_dcid.strip() and not new_r_dcid.strip().isdigit():
                            st.error("Die Discord-Rollen-ID darf nur aus Ziffern bestehen.")
                        else:
                            with edit(f"Rang „{rn_clean}“ erstellt") as d:
                                d["settings"].setdefault("custom_ranks", []).append({
                                    "id": uid(),
                                    "name": rn_clean,
                                    "category_id": new_r_cat,
                                    "color": new_r_col,
                                    "discord_role_id": new_r_dcid.strip(),
                                    "gets_team_role": bool(new_r_team),
                                    "is_applicant_target": bool(new_r_app),
                                })
                            st.rerun()

            if not custom_ranks:
                st.info("Noch keine Ränge angelegt.")
            else:
                for idx_r, r_obj in enumerate(custom_ranks):
                    cat_obj = get_category_obj(r_obj.get("category_id"))
                    cat_lbl = cat_obj["name"] if cat_obj else "Keine Kategorie"
                    team_badge = chip("Teamrolle aktiv", "#22C55E") if r_obj.get("gets_team_role") else chip("Keine Teamrolle", "#9CA3AF")
                    high_badge = f" {chip('High-Team', '#A855F7')}" if (cat_obj and cat_obj.get("is_high_team")) else ""
                    dc_info = f" · Discord-ID: `{r_obj['discord_role_id']}`" if r_obj.get("discord_role_id") else ""

                    col_info, col_up, col_dn, col_ed = st.columns([8.5, 0.7, 0.7, 0.9])
                    with col_info:
                        show(f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"
                             f"<div><strong>#{idx_r + 1}</strong> &nbsp; {badge(r_obj['name'])} &nbsp; "
                             f"<span class='muted'>Kategorie: <strong>{esc(cat_lbl)}</strong>{dc_info}</span></div>"
                             f"<div>{team_badge}{high_badge}</div></div>")
                    with col_up:
                        if st.button("⬆️", key=f"rup_{r_obj['id']}", disabled=(idx_r == 0), help="Nach oben (höherer Rang)"):
                            with edit(f"Rang {r_obj['name']} nach oben verschoben") as d:
                                lst = d["settings"]["custom_ranks"]
                                lst[idx_r - 1], lst[idx_r] = lst[idx_r], lst[idx_r - 1]
                            st.rerun()
                    with col_dn:
                        if st.button("⬇️", key=f"rdn_{r_obj['id']}", disabled=(idx_r == len(custom_ranks) - 1), help="Nach unten (niedrigerer Rang)"):
                            with edit(f"Rang {r_obj['name']} nach unten verschoben") as d:
                                lst = d["settings"]["custom_ranks"]
                                lst[idx_r + 1], lst[idx_r] = lst[idx_r], lst[idx_r + 1]
                            st.rerun()
                    with col_ed:
                        with st.popover("✏️"):
                            st.markdown(f"### ✏️ Rang bearbeiten")
                            ed_name = st.text_input("Rang-Name", value=r_obj["name"], key=f"ern_{r_obj['id']}")
                            cat_opts_ed = [""] + [c["id"] for c in cats]
                            cat_map_ed = {c["id"]: c["name"] for c in cats}
                            ed_cat = st.selectbox(
                                "Kategorie (Übergeordneter Rang)",
                                options=cat_opts_ed,
                                index=cat_opts_ed.index(r_obj.get("category_id")) if r_obj.get("category_id") in cat_opts_ed else 0,
                                format_func=lambda cid: cat_map_ed.get(cid, "– Keine Kategorie –"),
                                key=f"erc_{r_obj['id']}"
                            )
                            ed_col = st.color_picker("Farbe", value=r_obj.get("color") or "#3B82F6", key=f"ercol_{r_obj['id']}")
                            ed_dcid = st.text_input("Discord-Rollen-ID", value=r_obj.get("discord_role_id", ""), key=f"erdc_{r_obj['id']}").strip()
                            ed_team = st.checkbox("Teamrolle erhalten (Team-Überrubrik & Teamrolle G / High-Team)",
                                                  value=bool(r_obj.get("gets_team_role", False)), key=f"ertm_{r_obj['id']}")
                            ed_app = st.checkbox("Als Bewerbungs-Zielrang anzeigen",
                                                 value=bool(r_obj.get("is_applicant_target", False)), key=f"erap_{r_obj['id']}")

                            if st.button("💾 Änderungen speichern", key=f"ersv_{r_obj['id']}", use_container_width=True):
                                clean_n = ed_name.strip()
                                if not clean_n:
                                    st.error("Name darf nicht leer sein.")
                                elif clean_n.lower() != r_obj["name"].lower() and any(x["name"].lower() == clean_n.lower() for x in custom_ranks):
                                    st.error("Dieser Rang-Name existiert bereits.")
                                elif ed_dcid and not ed_dcid.isdigit():
                                    st.error("Discord-Rollen-ID darf nur aus Ziffern bestehen.")
                                else:
                                    old_n = r_obj["name"]
                                    with edit(f"Rang „{clean_n}“ bearbeitet") as d:
                                        for x in d["settings"]["custom_ranks"]:
                                            if x["id"] == r_obj["id"]:
                                                x.update({
                                                    "name": clean_n,
                                                    "category_id": ed_cat,
                                                    "color": ed_col,
                                                    "discord_role_id": ed_dcid,
                                                    "gets_team_role": ed_team,
                                                    "is_applicant_target": ed_app,
                                                })
                                        if old_n != clean_n:
                                            for m in d["members"]:
                                                if m["rank"] == old_n: m["rank"] = clean_n
                                            for a in d["archive"]:
                                                if a["rank"] == old_n: a["rank"] = clean_n
                                    st.rerun()

                            st.markdown("---")
                            if st.button("🗑 Rang löschen", key=f"erdel_{r_obj['id']}", use_container_width=True):
                                with edit(f"Rang „{r_obj['name']}“ gelöscht") as d:
                                    d["settings"]["custom_ranks"] = [x for x in d["settings"]["custom_ranks"] if x["id"] != r_obj["id"]]
                                st.rerun()

        with tab_cats:
            with st.expander("➕ Neue Kategorie (Oberrubrik) erstellen", expanded=not bool(cats)):
                with st.form("create_cat_form", clear_on_submit=True):
                    cc1, cc2, cc3 = st.columns([2, 2, 0.8])
                    c_name = cc1.text_input("Kategorie-Name", placeholder="z.B. Leitung, Teamverwaltung, Administration, Moderatoren, Supporter")
                    c_dcid = cc2.text_input("Discord Kategorie-Überrollen-ID (optional)", placeholder="123456789012345678")
                    c_col = cc3.color_picker("Farbe", value="#EF4444")
                    c_high = st.checkbox("Gehört zum High-Team (vergibt High-Team-Rolle statt normaler Team-Überrubrik)", value=False)
                    if st.form_submit_button("✅ Kategorie erstellen", use_container_width=True):
                        cn_clean = c_name.strip()
                        if not cn_clean:
                            st.error("Bitte einen Kategorie-Namen eingeben.")
                        elif any(c["name"].lower() == cn_clean.lower() for c in cats):
                            st.error("Diese Kategorie existiert bereits.")
                        elif c_dcid.strip() and not c_dcid.strip().isdigit():
                            st.error("Die Discord-Rollen-ID darf nur aus Ziffern bestehen.")
                        else:
                            with edit(f"Kategorie „{cn_clean}“ erstellt") as d:
                                d["settings"].setdefault("rank_categories", []).append({
                                    "id": uid(),
                                    "name": cn_clean,
                                    "color": c_col,
                                    "discord_role_id": c_dcid.strip(),
                                    "is_high_team": bool(c_high),
                                })
                            st.rerun()

            if not cats:
                st.info("Noch keine Kategorien angelegt.")
            else:
                for c_obj in cats:
                    assigned_cnt = sum(1 for r in custom_ranks if r.get("category_id") == c_obj["id"]) if False else sum(1 for r in custom_ranks if r.get("category_id") == c_obj["id"])
                    ht_chip = chip("High-Team Bereich", "#A855F7") if c_obj.get("is_high_team") else chip("Standard-Team Bereich", "#3B82F6")
                    dc_txt = f" · Discord Überrollen-ID: `{c_obj['discord_role_id']}`" if c_obj.get("discord_role_id") else " · Keine Discord-ID"

                    col_ci, col_ce = st.columns([11, 1])
                    with col_ci:
                        show(f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"
                             f"<div>{chip(c_obj['name'], c_obj.get('color', '#EF4444'))} "
                             f"<span class='muted'>({assigned_cnt} Ränge zugeordnet{dc_txt})</span></div>"
                             f"<div>{ht_chip}</div></div>")
                    with col_ce:
                        with st.popover("✏️"):
                            st.markdown(f"### ✏️ Kategorie bearbeiten")
                            ec_name = st.text_input("Kategorie-Name", value=c_obj["name"], key=f"ecn_{c_obj['id']}")
                            ec_dcid = st.text_input("Discord Überrollen-ID", value=c_obj.get("discord_role_id", ""), key=f"ecdc_{c_obj['id']}").strip()
                            ec_col = st.color_picker("Farbe", value=c_obj.get("color", "#EF4444"), key=f"eccol_{c_obj['id']}")
                            ec_high = st.checkbox("Gehört zum High-Team", value=bool(c_obj.get("is_high_team", False)), key=f"echt_{c_obj['id']}")
                            if st.button("💾 Speichern", key=f"ecsv_{c_obj['id']}", use_container_width=True):
                                clean_cn = ec_name.strip()
                                if not clean_cn:
                                    st.error("Name darf nicht leer sein.")
                                elif ec_dcid and not ec_dcid.isdigit():
                                    st.error("Discord-ID darf nur aus Ziffern bestehen.")
                                else:
                                    with edit(f"Kategorie „{clean_cn}“ bearbeitet") as d:
                                        for x in d["settings"]["rank_categories"]:
                                            if x["id"] == c_obj["id"]:
                                                x.update({
                                                    "name": clean_cn,
                                                    "discord_role_id": ec_dcid,
                                                    "color": ec_col,
                                                    "is_high_team": ec_high,
                                                })
                                    st.rerun()
                            st.markdown("---")
                            if st.button("🗑 Kategorie löschen", key=f"ecdel_{c_obj['id']}", use_container_width=True):
                                with edit(f"Kategorie „{c_obj['name']}“ gelöscht") as d:
                                    d["settings"]["rank_categories"] = [x for x in d["settings"]["rank_categories"] if x["id"] != c_obj["id"]]
                                    for r in d["settings"].get("custom_ranks", []):
                                        if r.get("category_id") == c_obj["id"]:
                                            r["category_id"] = ""
                                st.rerun()

    if is_owner:
        st.markdown("---")
        st.subheader("🤖 Discord-Anbindung, Teamrollen & Wartungsmodus (nur Alpha-Owner)")
        st.caption("Webhook-URLs, Bot-Token und Basis-Teamrollen liegen in der separaten Discord-Konfiguration (Cloud/Lokal), nicht in den Teamdaten und nicht im Backup. "
                   "Leere Felder nutzen den „Allgemein“-Webhook. Den Token kannst du auch als Umgebungsvariable `DISCORD_BOT_TOKEN` setzen.")
        cfg = dc_cfg()
        with st.form("discord_cfg_form"):
            maintenance_toggle = st.checkbox(
                "🚧 Wartungsmodus aktivieren (Webseite für normale Nutzer sperren – nur Alpha-Owner können sich anmelden)",
                value=bool(cfg.get("maintenance_mode", False))
            )
            st.markdown("---")
            new_wh = {k: st.text_input(lbl, value=cfg["webhooks"].get(k, ""), type="password",
                                       placeholder="https://discord.com/api/webhooks/…", key=f"wh_input_{k}") for k, lbl in WEBHOOK_CHANNELS}
            st.markdown("---")
            sync = st.checkbox("Discord-Rollen (Einzelrang, Kategorie-Überrolle & Teamrolle) bei Rangänderung automatisch synchronisieren", value=bool(cfg["sync_roles"]))
            c1, c2 = st.columns(2)
            gid = c1.text_input("Server-ID", value=cfg["guild_id"])
            tok = c2.text_input("Bot-Token" + (" (gespeichert, leer = behalten)" if cfg["bot_token"] else ""), type="password")

            st.markdown("**Basis-Teamrollen & High-Team-Umschaltung (Discord-Rollen-IDs)**")
            tr1, tr2, tr3 = st.columns(3)
            t_base_id = tr1.text_input("Team-Überrubrik ID (@Team)", value=cfg.get("team_base_role_id", ""), placeholder="ID der @Team Überrubrik")
            t_g_id = tr2.text_input("Teamrolle G ID (@Teamrolle G)", value=cfg.get("team_role_g_id", ""), placeholder="ID der @Teamrolle G")
            t_high_id = tr3.text_input("High-Team-Rolle ID (@High-Team)", value=cfg.get("high_team_role_id", ""), placeholder="ID der @High-Team Rolle")
            rep_base = st.checkbox(
                "Bei High-Team-Kategorien die einfache Team-Überrubrik (@Team) automatisch entfernen",
                value=bool(cfg.get("replace_team_with_high", True))
            )

            save_wh = st.form_submit_button("💾 Einstellungen speichern", use_container_width=True)
        if save_wh:
            new_wh = {k: v.strip() for k, v in new_wh.items()}
            id_checks = [gid.strip(), t_base_id.strip(), t_g_id.strip(), t_high_id.strip()]
            if any(v and not DC_HOOK_RE.match(v) for v in new_wh.values()):
                st.error("Ungültige Webhook-URL. Sie muss eine discord.com-Webhook-Adresse sein.")
            elif any(v and not v.isdigit() for v in id_checks):
                st.error("Server- und Rollen-IDs bestehen nur aus Ziffern.")
            else:
                cfg.update(
                    webhooks=new_wh,
                    sync_roles=sync,
                    guild_id=gid.strip(),
                    maintenance_mode=maintenance_toggle,
                    team_base_role_id=t_base_id.strip(),
                    team_role_g_id=t_g_id.strip(),
                    high_team_role_id=t_high_id.strip(),
                    replace_team_with_high=rep_base,
                )
                if tok.strip(): cfg["bot_token"] = tok.strip()
                dc_save(cfg)
                st.success("Gespeichert.")
                st.rerun()
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
            uo = st.checkbox("Alpha-Owner (Zugriff auf Discord-Einstellungen & Wartungsmodus)") if is_owner else False
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
        is_hc = u["username"].lower() == ALPHA_OWNER_USER.lower()
        if u.get("is_owner"):
            st.markdown(f"<span style='color:#B91C1C !important;font-weight:800'>👑 {esc(u['username'])} — Alpha-Owner{' (System-Hardcoded)' if is_hc else ''}</span>", unsafe_allow_html=True)
        with st.expander(f"{u['username']} {'(Alpha-Owner)' if u.get('is_owner') else '(Administrator)' if u.get('is_admin') else ''}"):
            if u.get("is_owner") and not is_owner:
                st.info("🔒 Alpha-Owner-Konto: kann nur von einem Alpha-Owner verwaltet werden.")
                continue
            if is_hc:
                st.info("🔒 Dieser Alpha-Owner-Account ist fest im Code verankert. Benutzername, Passwort und Owner-Status sind geschützt.")
                lm_opts = ["–"] + member_names
                lm = st.selectbox("Verknüpftes Teammitglied (für Anzeige / eigene Abmeldung)", lm_opts,
                                  index=lm_opts.index(u["member"]) if u.get("member") in lm_opts else 0,
                                  format_func=lambda n: n if n == "–" else mlabel(n), key=f"lm_{u['username']}")
                if st.button("💾 Verknüpfung speichern", key=f"sp_{u['username']}"):
                    with edit(f"Teammitglied-Verknüpfung von {u['username']} geändert") as d:
                        for x in d["users"]:
                            if x["username"].lower() == ALPHA_OWNER_USER.lower():
                                x["member"] = "" if lm == "–" else lm
                    st.success("Gespeichert.")
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
            ow = (st.checkbox("Alpha-Owner (übergeordnet, Zugriff auf Discord-Einstellungen & Wartungsmodus)", value=bool(u.get("is_owner")),
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
    up_bk = st.file_uploader("📥 Backup-JSON wiederherstellen", type=["json"], key="restore_bk_up")
    if up_bk and st.button("🔄 Backup jetzt einspielen", key="restore_bk_btn"):
        try:
            restored = json.loads(up_bk.read().decode("utf-8"))
            with edit("Backup eingespielt") as d:
                for k in DEFAULTS:
                    if k != "users" and k in restored:
                        d[k] = restored[k]
            st.success("✅ Backup erfolgreich wiederhergestellt!")
            st.rerun()
        except Exception as ex:
            st.error(f"Ungültige Backup-Datei: {ex}")
    st.subheader("🧾 Aktivitätslog (letzte 30)")
    show("".join(f"<div class='muted'>{esc(e['ts'].replace('T', ' '))} – <strong>{esc(e['user'])}</strong>: {esc(e['action'])}</div>"
                 for e in reversed(data["log"][-30:])) or "<span class='muted'>Noch keine Einträge.</span>")
