import hashlib
import html
import io
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
import zipfile
import shutil

import pandas as pd
import streamlit as st
from PIL import Image


# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(
    page_title="Aaquib Digital Solutions | GP Site Finder Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "local_sites.db"
CONTACT_DB_PATH = BASE_DIR / "database" / "web_private_contacts.db"
AUTH_PATH = BASE_DIR / "database" / "web_admin.json"
CONTACT_US_DB_PATH = BASE_DIR / "database" / "contact_us.db"
TEAM_DB_PATH = BASE_DIR / "database" / "team_profiles.db"
OUTREACH_DB_PATH = BASE_DIR / "database" / "outreach_pipeline.db"
ADMIN_CONTACTS_DB_PATH = BASE_DIR / "database" / "admin_private_contacts.db"
TEAM_IMAGES_DIR = BASE_DIR / "assets" / "team"
PROFILE_IMAGE_PATH = BASE_DIR / "assets" / "aaquib_profile.png"
HERO_IMAGE_PATH = BASE_DIR / "assets" / "dashboard_hero.png"
PROFILE_DATA_PATH = BASE_DIR / "database" / "profile_settings.json"
LINKEDIN_URL = "https://www.linkedin.com/in/aaquib-seo/"


# =========================================================
# STYLING — LOVABLE INSPIRED PREMIUM SAAS
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Sora:wght@500;600;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0');

    :root {
        --bg: #F6F3ED;
        --surface: #FFFCF7;
        --surface-2: #F0ECE5;
        --ink: #202231;
        --muted: #6D7080;
        --border: #DED9D0;
        --sidebar: #11192E;
        --sidebar-2: #0D1427;
        --sidebar-line: rgba(255,255,255,.09);
        --purple: #7045D6;
        --purple-soft: #EEE8FF;
        --cyan: #18BFC5;
        --cyan-soft: #DDF5F4;
        --ice: #E7F7FB;
        --gold: #DEA83B;
        --gold-soft: #F8EED7;
        --danger: #D9505B;
        --shadow: 0 1px 2px rgba(26,29,42,.05), 0 16px 40px -24px rgba(19,25,46,.34);
        --shadow-lg: 0 24px 62px -30px rgba(17,25,46,.48);
    }

    html, body, [class*="css"] { font-family: "Manrope", sans-serif; }
    h1,h2,h3,h4,.main-title,.metric-value,.hero-title { font-family: "Sora", sans-serif !important; }

    .stApp {
        background:
            radial-gradient(circle at 88% 0%, rgba(24,191,197,.07), transparent 25rem),
            radial-gradient(circle at 72% 12%, rgba(112,69,214,.055), transparent 20rem),
            var(--bg);
        color: var(--ink);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.15rem;
        padding-bottom: 3rem;
        animation: pageIn .42s cubic-bezier(.2,.75,.25,1) both;
    }

    @keyframes pageIn { from {opacity:0; transform:translateY(8px)} to {opacity:1; transform:none} }
    @keyframes softGlow { 0%,100%{box-shadow:0 0 0 rgba(24,191,197,0)} 50%{box-shadow:0 0 22px rgba(24,191,197,.11)} }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar), var(--sidebar-2));
        border-right: 1px solid var(--sidebar-line);
    }
    [data-testid="stSidebar"] > div { padding-top: .45rem; }
    [data-testid="stSidebar"] * { color: #E8EBF4; }

    .sidebar-brand {
        display:flex; align-items:center; gap:11px;
        padding: 14px 10px 17px;
        border-bottom:1px solid var(--sidebar-line);
        margin:0 -2px 10px;
    }
    .sidebar-logo {
        width:38px; height:38px; border-radius:13px;
        display:grid; place-items:center;
        background: linear-gradient(135deg,#6F48DB 0%,#3987D9 55%,#18BFC5 100%);
        box-shadow:0 10px 26px rgba(73,84,218,.30);
    }
    .sidebar-logo .material-symbols-rounded {font-size:20px;color:white;}
    .sidebar-title {font-family:"Sora";font-size:14px;font-weight:700;color:#fff;line-height:1.25;}
    .sidebar-sub {font-size:10px;color:#8993AA;margin-top:3px;letter-spacing:.025em;}

    [data-testid="stSidebar"] [role="radiogroup"] label {
        position:relative;
        border-radius:11px;
        padding:9px 10px 9px 40px;
        margin:2px 4px;
        min-height:40px;
        transition:all .18s ease;
        font-size:13.5px;
        font-weight:600;
        color:#CAD0DE;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background:rgba(255,255,255,.055);
        transform:translateX(2px);
        color:#fff;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(112,69,214,.26), rgba(24,191,197,.09));
        color:#fff;
        box-shadow:inset 0 0 0 1px rgba(130,92,232,.48);
    }
    [data-testid="stSidebar"] [role="radiogroup"] label::before {
        font-family:"Material Symbols Rounded";
        position:absolute; left:13px; top:50%; transform:translateY(-50%);
        font-size:19px; color:#AEB7CB;
        transition:all .18s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked)::before { color:#49E2DF; }

    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1)::before {content:"dashboard"; color:#9A7DF0;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2)::before {content:"monitoring"; color:#53C7D1;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3)::before {content:"search"; color:#62BFF2;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4)::before {content:"add_circle"; color:#4DD7BE;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5)::before {content:"upload_file"; color:#58C6F0;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6)::before {content:"edit_square"; color:#C19AF4;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(7)::before {content:"delete"; color:#F37D8A;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(8)::before {content:"content_copy"; color:#F2B84A;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(9)::before {content:"download"; color:#6BD6B0;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(10)::before {content:"star"; color:#F1C64E;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(11)::before {content:"contacts"; color:#51D0C3;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(12)::before {content:"groups"; color:#9B91F4;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(13)::before {content:"mail"; color:#67C7E5;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(14)::before {content:"account_circle"; color:#AA91EE;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(15)::before {content:"settings"; color:#AAB2C2;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(16)::before {content:"shield_lock"; color:#F29A73;}

    .sidebar-user {
        border:1px solid var(--sidebar-line);
        background:rgba(255,255,255,.035);
        border-radius:14px;
        padding:11px 12px;
        margin:12px 4px 2px;
    }
    .sidebar-user-name {font-size:12px;font-weight:700;color:#fff;}
    .sidebar-user-role {font-size:10px;color:#8791A9;margin-top:3px;}

    .brand-badge {
        display:inline-flex;align-items:center;gap:7px;
        color:#7050D7;font-size:10px;font-weight:800;
        text-transform:uppercase;letter-spacing:.20em;margin-bottom:7px;
    }
    .brand-badge::before {content:"";width:18px;height:2px;background:linear-gradient(90deg,var(--purple),var(--cyan));border-radius:2px;}
    .main-title {font-size:36px;font-weight:700;letter-spacing:-.035em;color:#202231;margin:0;line-height:1.14;}
    .subtitle {color:var(--muted);font-size:13px;margin:7px 0 18px;}

    .hero-shell {
        position:relative; overflow:hidden;
        min-height:310px;
        border-radius:24px;
        padding:36px 40px;
        display:grid;grid-template-columns:1.05fr .95fr;gap:24px;align-items:center;
        background:linear-gradient(120deg,#111A32 0%,#151C3D 50%,#10333D 100%);
        border:1px solid rgba(255,255,255,.08);
        box-shadow:var(--shadow-lg);
        margin:8px 0 24px;
    }
    .hero-shell::after {
        content:"";position:absolute;inset:0;
        background:radial-gradient(circle at 78% 35%,rgba(24,191,197,.16),transparent 28%),radial-gradient(circle at 55% 48%,rgba(112,69,214,.19),transparent 30%);
        pointer-events:none;
    }
    .hero-copy {position:relative;z-index:2;}
    .hero-kicker {
        display:inline-flex;background:linear-gradient(90deg,#F1C856,#DDA338);
        color:#31250A;padding:5px 10px;border-radius:999px;font-size:10px;font-weight:800;letter-spacing:.02em;margin-bottom:13px;
    }
    .hero-title {font-size:34px;line-height:1.17;color:white;font-weight:700;letter-spacing:-.035em;max-width:620px;}
    .hero-text {font-size:13px;line-height:1.65;color:#C4CADE;max-width:600px;margin-top:12px;}
    .hero-pills {display:flex;gap:8px;flex-wrap:wrap;margin-top:20px;}
    .hero-pill {padding:7px 11px;border:1px solid rgba(255,255,255,.13);background:rgba(255,255,255,.055);border-radius:999px;color:#E9EDF8;font-size:10.5px;font-weight:600;}
    .hero-photo-shell {position:relative;z-index:2;border-radius:18px;overflow:hidden;height:245px;border:1px solid rgba(255,255,255,.13);box-shadow:0 20px 44px rgba(0,0,0,.32);}
    .hero-photo-shell img {width:100%;height:100%;object-fit:cover;display:block;filter:saturate(.95) contrast(1.04);}

    .metric-card {
        background:linear-gradient(145deg,#FFFDF9,#F7F3ED);
        border:1px solid var(--border);border-radius:18px;padding:18px 19px;min-height:132px;
        box-shadow:var(--shadow);transition:transform .2s ease,box-shadow .2s ease;
        animation:pageIn .45s ease both;
    }
    .metric-card:hover {transform:translateY(-3px);box-shadow:0 16px 34px -20px rgba(20,27,49,.34);}
    .metric-icon {width:40px;height:40px;border-radius:12px;display:grid;place-items:center;margin-bottom:14px;background:var(--purple-soft);color:var(--purple);}
    .metric-icon.teal {background:var(--cyan-soft);color:#0D969D;}
    .metric-icon.sage {background:#E4F0E3;color:#527758;}
    .metric-icon.copper {background:#F3E7DF;color:#A36A49;}
    .metric-icon .material-symbols-rounded {font-size:21px;}
    .metric-label {font-size:10px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:#727584;margin-bottom:7px;}
    .metric-value {font-size:28px;font-weight:600;color:#202231;letter-spacing:-.03em;}
    .metric-delta {font-size:10px;color:#777B88;margin-top:5px;}

    .section-title {font-family:"Sora";font-size:19px;font-weight:650;color:#242635;margin:26px 0 12px;display:flex;align-items:center;gap:10px;}
    .section-kicker {font-size:11px;color:var(--muted);margin-top:-7px;margin-bottom:14px;}

    .surface-card {
        background:linear-gradient(145deg,#FFFDF9,#FBF8F2);
        border:1px solid var(--border);border-radius:18px;box-shadow:var(--shadow);padding:20px;
    }

    .publisher-list {background:#FFFDF9;border:1px solid var(--border);border-radius:18px;overflow:hidden;box-shadow:var(--shadow);}
    .publisher-head {display:flex;justify-content:space-between;align-items:center;padding:17px 19px;border-bottom:1px solid var(--border);}
    .publisher-title {font-family:"Sora";font-weight:650;font-size:15px;color:#242635;}
    .publisher-sub {font-size:10.5px;color:#7A7E8A;margin-top:3px;}
    .publisher-row {display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:14px;align-items:center;padding:13px 19px;border-bottom:1px solid #E8E3DA;transition:background .15s ease;}
    .publisher-row:last-child{border-bottom:0}.publisher-row:hover{background:#F7F3ED}
    .publisher-site {font-size:12.5px;font-weight:700;color:#262836;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
    .publisher-meta {font-size:10px;color:#7A7E8A;margin-top:2px;}
    .dr-badge {background:#F0ECE6;border-radius:999px;padding:5px 8px;font-size:10px;font-weight:700;color:#343645;}
    .price-tag {font-size:12px;font-weight:800;color:var(--purple);min-width:55px;text-align:right;}

    .form-section {
        background:linear-gradient(145deg,#FFFDF9,#FBF8F2);border:1px solid var(--border);border-radius:18px;padding:20px 22px;margin:12px 0 16px;box-shadow:var(--shadow);
    }
    .form-section-title {font-family:"Sora";font-size:17px;font-weight:650;color:#242635;margin-bottom:3px;}
    .form-section-sub {font-size:11px;color:#777B88;margin-bottom:13px;}

    div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius:12px!important;border-color:#D8D3CB!important;background:#FFFCF7!important;color:#252735!important;min-height:42px;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {box-shadow:0 0 0 2px rgba(112,69,214,.13)!important;border-color:#8D70DD!important;}

    .stButton > button,.stDownloadButton > button,.stLinkButton > a {
        border-radius:11px!important;font-weight:700!important;min-height:41px;transition:transform .16s ease,box-shadow .16s ease!important;
    }
    .stButton > button:hover,.stDownloadButton > button:hover,.stLinkButton > a:hover {transform:translateY(-1px);}
    .stButton > button[kind="primary"] {background:linear-gradient(135deg,#6E42D4,#7249DB 55%,#4F71DA);border:0;box-shadow:0 9px 22px rgba(112,69,214,.22);}

    [data-testid="stDataFrame"] {border:1px solid var(--border);border-radius:16px;overflow:hidden;background:#FFFDF9;box-shadow:var(--shadow);}
    [data-testid="stMetric"] {background:#FFFDF9;border:1px solid var(--border);border-radius:16px;padding:14px;box-shadow:var(--shadow);}

    .wa-float {position:fixed;right:22px;bottom:22px;z-index:9999;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none!important;background:linear-gradient(135deg,#17A854,#24CA67);box-shadow:0 12px 28px rgba(34,197,94,.32);border:2px solid rgba(255,255,255,.9);transition:transform .18s ease;animation:softGlow 3s ease-in-out infinite;}
    .wa-float:hover{transform:translateY(-3px) scale(1.03)}.wa-float svg{width:29px;height:29px;fill:#fff}
    .whatsapp-button {display:block;text-align:center;background:linear-gradient(135deg,#16A34A,#22C55E);color:#fff!important;padding:12px 16px;border-radius:11px;font-weight:800;text-decoration:none!important;margin:8px 0;box-shadow:0 8px 18px rgba(34,197,94,.22);}

    @media(max-width:900px){
        .hero-shell{grid-template-columns:1fr;padding:26px}.hero-photo-shell{height:220px}.hero-title{font-size:28px}.main-title{font-size:30px}
    }
    @media(max-width:768px){
        .block-container{padding-left:.75rem;padding-right:.75rem;padding-top:.7rem}.main-title{font-size:27px}.subtitle{font-size:12px}
        [data-testid="column"]{width:100%!important;flex:1 1 100%!important;min-width:100%!important}
        [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.55rem!important}.hero-shell{padding:20px;border-radius:19px}.hero-title{font-size:24px}.hero-photo-shell{height:185px}.metric-card{min-height:auto;padding:15px}.publisher-row{grid-template-columns:minmax(0,1fr) auto}.price-tag{display:none}.wa-float{right:13px;bottom:13px;width:51px;height:51px}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PROFILE / CONTACT SETTINGS
# =========================================================
DEFAULT_PROFILE = {
    "brand_name": "Aaquib Digital Solutions",
    "name": "Aaquib SEO",
    "role": "SEO, Guest Post & Outreach Specialist",
    "phone": "",
    "email": "",
    "website": "",
    "linkedin": "https://www.linkedin.com/in/aaquib-seo/",
    "location": "",
    "about": "Helping brands with guest posting, link building and outreach.",
}


def load_profile_settings() -> dict:
    PROFILE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not PROFILE_DATA_PATH.exists():
        PROFILE_DATA_PATH.write_text(
            json.dumps(DEFAULT_PROFILE, indent=2),
            encoding="utf-8",
        )
        return DEFAULT_PROFILE.copy()

    try:
        saved = json.loads(
            PROFILE_DATA_PATH.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        saved = {}

    profile = DEFAULT_PROFILE.copy()
    profile.update(
        {
            key: str(value)
            for key, value in saved.items()
            if key in profile
        }
    )
    return profile


def save_profile_settings(profile: dict) -> None:
    PROFILE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_DATA_PATH.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def whatsapp_url(phone: str, message: str = "") -> str:
    digits = re.sub(r"[^0-9]", "", str(phone or ""))

    if digits.startswith("0"):
        digits = "92" + digits[1:]

    if not digits:
        return ""

    base = f"https://wa.me/{digits}"

    if message:
        from urllib.parse import quote
        return f"{base}?text={quote(message)}"

    return base


def normalize_public_url(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    if value.lower().startswith(("http://", "https://")):
        return value
    return f"https://{value}"


def save_profile_image(uploaded_image) -> None:
    PROFILE_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

    image = Image.open(uploaded_image)
    image = image.convert("RGBA")
    image.thumbnail((900, 900))
    image.save(PROFILE_IMAGE_PATH, format="PNG", optimize=True)


def save_dashboard_hero_image(uploaded_image) -> None:
    HERO_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

    image = Image.open(uploaded_image)
    image = image.convert("RGB")
    image.thumbnail((1800, 1100))
    image.save(HERO_IMAGE_PATH, format="PNG", optimize=True)



profile_settings = load_profile_settings()

if profile_settings.get("phone"):
    floating_whatsapp = whatsapp_url(
        profile_settings["phone"],
        "Hello Aaquib Digital Solutions, I want to discuss guest posting / SEO services.",
    )

    if floating_whatsapp:
        st.markdown(
            f"""
            <a class="wa-float"
               href="{floating_whatsapp}"
               target="_blank"
               title="Chat on WhatsApp">
                <svg viewBox="0 0 32 32" aria-hidden="true">
                    <path d="M16.04 3C9.39 3 4 8.22 4 14.66c0 2.27.68 4.39 1.85 6.17L4 27l6.36-1.79a12.3 12.3 0 0 0 5.68 1.38C22.69 26.59 28 21.37 28 14.93 28 8.49 22.69 3 16.04 3zm0 21.62c-1.83 0-3.54-.5-5.01-1.37l-.36-.21-3.77 1.06 1.08-3.63-.24-.37a9.52 9.52 0 0 1-1.52-5.17c0-5.35 4.43-9.7 9.88-9.7 5.45 0 9.88 4.35 9.88 9.7s-4.43 9.69-9.94 9.69zm5.42-7.27c-.3-.15-1.77-.85-2.04-.95-.28-.1-.48-.15-.68.15-.2.3-.78.95-.96 1.15-.18.2-.35.23-.65.08-.3-.15-1.25-.45-2.39-1.43-.88-.77-1.48-1.72-1.65-2.01-.18-.3-.02-.46.13-.61.14-.13.3-.35.45-.53.15-.18.2-.3.3-.5.1-.2.05-.38-.02-.53-.08-.15-.68-1.6-.93-2.19-.25-.59-.5-.5-.68-.51h-.58c-.2 0-.53.08-.8.38-.28.3-1.05 1.01-1.05 2.47s1.08 2.87 1.23 3.07c.15.2 2.12 3.17 5.14 4.44.72.3 1.28.49 1.72.63.72.22 1.38.19 1.9.12.58-.08 1.77-.71 2.02-1.4.25-.69.25-1.28.18-1.4-.08-.13-.28-.2-.58-.35z"/>
                </svg>
            </a>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# DATABASE SETUP
# =========================================================
def ensure_databases() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sites(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                country TEXT,
                da TEXT,
                dr TEXT,
                traffic TEXT,
                general_price TEXT,
                casino_price TEXT,
                payment_method TEXT,
                tat TEXT,
                type TEXT,
                link_type TEXT,
                source_file TEXT,
                sheet_name TEXT,
                favorite INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()

    with sqlite3.connect(CONTACT_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts(
                domain TEXT PRIMARY KEY,
                admin_name TEXT,
                email TEXT,
                whatsapp TEXT,
                telegram TEXT,
                status TEXT,
                quoted_price TEXT,
                notes TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()

    with sqlite3.connect(CONTACT_US_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contact_messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                company TEXT,
                website TEXT,
                subject TEXT,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'New',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()

    TEAM_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(OUTREACH_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outreach_pipeline(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER,
                site TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'New',
                contact_name TEXT,
                contact_email TEXT,
                whatsapp TEXT,
                last_contacted TEXT,
                next_follow_up TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_outreach_site "
            "ON outreach_pipeline(site)"
        )
        conn.commit()

    with sqlite3.connect(ADMIN_CONTACTS_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_private_contacts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_type TEXT NOT NULL,
                full_name TEXT NOT NULL,
                company TEXT,
                job_title TEXT,
                email TEXT,
                phone TEXT,
                whatsapp TEXT,
                website TEXT,
                linkedin TEXT,
                address TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


    with sqlite3.connect(TEAM_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS team_members(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                designation TEXT NOT NULL,
                level TEXT NOT NULL,
                reports_to TEXT,
                email TEXT,
                phone TEXT,
                linkedin TEXT,
                website TEXT,
                location TEXT,
                bio TEXT,
                skills TEXT,
                image_path TEXT,
                display_order INTEGER DEFAULT 100,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()

    if not AUTH_PATH.exists():
        AUTH_PATH.write_text(
            json.dumps(
                {
                    "username": "admin",
                    "password_hash": hashlib.sha256(
                        "admin123".encode("utf-8")
                    ).hexdigest(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )


ensure_databases()


@st.cache_data(show_spinner=False)
def load_sites() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        frame = pd.read_sql_query("SELECT * FROM sites ORDER BY id DESC", conn)

    if frame.empty:
        return frame

    searchable_columns = [
        column
        for column in [
            "site",
            "country",
            "type",
            "source_file",
            "sheet_name",
            "payment_method",
            "link_type",
        ]
        if column in frame.columns
    ]

    frame["_search_text"] = (
        frame[searchable_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
    )

    frame["_dr_num"] = pd.to_numeric(
        frame.get("dr", pd.Series(index=frame.index, dtype=object)),
        errors="coerce",
    )

    frame["_price_num"] = pd.to_numeric(
        frame.get(
            "general_price",
            pd.Series(index=frame.index, dtype=object),
        ),
        errors="coerce",
    )

    return frame


def refresh_sites() -> None:
    load_sites.clear()


def load_contacts() -> pd.DataFrame:
    with sqlite3.connect(CONTACT_DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT * FROM contacts ORDER BY updated_at DESC", conn
        )


# =========================================================
# HELPERS
# =========================================================
COLUMN_ALIASES = {
    "site": ["site", "site name", "website", "website name", "website url", "site url", "url", "domain", "domain name"],
    "country": ["country", "location", "region", "traffic country", "top traffic country"],
    "da": ["da", "domain authority", "moz da", "web da"],
    "dr": ["dr", "domain rating", "ahrefs dr", "web dr"],
    "traffic": ["traffic", "monthly traffic", "organic traffic", "ahrefs traffic", "visits"],
    "general_price": ["price", "general price", "guest post price", "gp price", "cost", "amount"],
    "casino_price": ["casino price", "gambling price", "casino"],
    "payment_method": ["payment", "payment method", "payment terms", "pay method"],
    "tat": ["tat", "turnaround time", "delivery time", "publish time"],
    "type": ["type", "niche", "category", "website niche"],
    "link_type": ["link type", "dofollow", "nofollow", "do follow", "no follow"],
}


def clean_heading(value) -> str:
    text = str(value).strip().lower().replace("_", " ").replace("-", " ")
    text = re.sub(r"[^a-z0-9%$ ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_value(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"nan", "none", "null"} else text


def normalize_search_query(value: str) -> str:
    text = str(value or "").strip().lower()

    # Remove surrounding spaces and common URL prefixes.
    text = re.sub(r"^https?://", "", text)
    text = re.sub(r"^www\.", "", text)

    # Remove query string, fragments and trailing path/slash.
    text = text.split("?")[0]
    text = text.split("#")[0]

    # For full URLs keep the domain as the primary search term.
    if "/" in text:
        text = text.split("/")[0]

    return text.strip().rstrip("/")


def normalize_domain(value) -> str:
    text = clean_value(value).lower()
    text = re.sub(r"^https?://", "", text)
    text = re.sub(r"^www\.", "", text)
    text = text.split("/")[0].strip()
    match = re.search(
        r"(?:[a-z0-9](?:[a-z0-9-]{0,62})\.)+[a-z]{2,63}",
        text,
        flags=re.I,
    )
    return match.group(0).lower() if match else ""


def find_header_row(raw_df: pd.DataFrame):
    for row_index in range(min(40, len(raw_df))):
        values = [clean_heading(v) for v in raw_df.iloc[row_index].tolist()]
        if any(value in COLUMN_ALIASES["site"] for value in values):
            return row_index
    return None


def match_column(columns, aliases):
    normalized = {clean_heading(column): column for column in columns}
    for alias in aliases:
        alias = clean_heading(alias)
        if alias in normalized:
            return normalized[alias]
    for norm, original in normalized.items():
        for alias in aliases:
            alias = clean_heading(alias)
            if len(alias) >= 4 and (alias in norm or norm in alias):
                return original
    return None


def normalize_payment(value) -> str:
    text = clean_heading(value)
    if not text:
        return ""
    if "50" in text and ("advance" in text or "upfront" in text):
        return "50% Advance"
    if any(x in text for x in ["after", "post payment", "pay after"]):
        return "After"
    if any(x in text for x in ["upfront", "advance", "prepaid", "before publication"]):
        return "Upfront"
    if "negoti" in text:
        return "Negotiable"
    return clean_value(value)


def normalize_link_type(value) -> str:
    text = clean_heading(value)
    if not text:
        return ""
    has_do = any(x in text for x in ["dofollow", "do follow"])
    has_no = any(x in text for x in ["nofollow", "no follow"])
    if has_do and has_no:
        return "Mixed"
    if has_no:
        return "Nofollow"
    if has_do:
        return "Dofollow"
    return clean_value(value)


def prepare_import_dataframe(uploaded_df, source_file, sheet_name):
    matched = {
        field: match_column(uploaded_df.columns, aliases)
        for field, aliases in COLUMN_ALIASES.items()
    }
    if matched["site"] is None:
        raise ValueError("Website, Site, URL ya Domain column nahi mila.")

    rows = []
    now = datetime.now().isoformat(timespec="seconds")

    for _, row in uploaded_df.iterrows():
        domain = normalize_domain(row.get(matched["site"], ""))
        if not domain:
            continue

        item = {
            "site": domain,
            "country": "",
            "da": "",
            "dr": "",
            "traffic": "",
            "general_price": "",
            "casino_price": "",
            "payment_method": "",
            "tat": "",
            "type": "",
            "link_type": "",
            "source_file": source_file,
            "sheet_name": sheet_name,
            "favorite": 0,
            "created_at": now,
        }

        for field, column in matched.items():
            if column is not None:
                item[field] = clean_value(row.get(column, ""))

        item["site"] = domain
        item["payment_method"] = normalize_payment(item["payment_method"])
        item["link_type"] = normalize_link_type(item["link_type"])
        rows.append(item)

    return pd.DataFrame(rows)


def save_imported_sites(prepared_df):
    if prepared_df.empty:
        return 0

    rows = [
        (
            row["site"], row["country"], row["da"], row["dr"], row["traffic"],
            row["general_price"], row["casino_price"], row["payment_method"],
            row["tat"], row["type"], row["link_type"], row["source_file"],
            row["sheet_name"], int(row["favorite"]), row["created_at"],
        )
        for _, row in prepared_df.iterrows()
    ]

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            DELETE FROM sites
            WHERE lower(site)=lower(?) AND source_file=? AND sheet_name=?
            """,
            [(r[0], r[11], r[12]) for r in rows],
        )
        conn.executemany(
            """
            INSERT INTO sites(
                site,country,da,dr,traffic,general_price,casino_price,
                payment_method,tat,type,link_type,source_file,sheet_name,
                favorite,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            rows,
        )
        conn.commit()

    return len(rows)


def safe_unique(df, column):
    if column not in df.columns:
        return ["All"]
    values = df[column].fillna("").astype(str).str.strip()
    return ["All"] + sorted(values[values != ""].unique().tolist())


def site_selector(dataframe, label="Website select karein"):
    if dataframe.empty:
        return None, None
    options = {
        f"{row['site']} | ID {int(row['id'])}": int(row["id"])
        for _, row in dataframe.iterrows()
    }
    selected_label = st.selectbox(label, list(options.keys()))
    selected_id = options[selected_label]
    row = dataframe[dataframe["id"] == selected_id].iloc[0]
    return selected_id, row


def require_admin() -> bool:
    if st.session_state.get("admin_logged_in", False):
        return True
    st.warning("Admin Login required for this page.")
    return False



def load_team_members(active_only: bool = True) -> pd.DataFrame:
    query = """
        SELECT *
        FROM team_members
    """

    params = ()

    if active_only:
        query += " WHERE active=1"

    query += """
        ORDER BY
            CASE level
                WHEN 'CEO / Founder' THEN 1
                WHEN 'Director' THEN 2
                WHEN 'Manager' THEN 3
                WHEN 'Team Lead' THEN 4
                ELSE 5
            END,
            display_order,
            full_name
    """

    with sqlite3.connect(TEAM_DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)


def save_team_image(uploaded_file, member_id: int) -> str:
    TEAM_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    image = Image.open(uploaded_file)
    image = image.convert("RGB")
    image.thumbnail((1000, 1000))

    destination = TEAM_IMAGES_DIR / f"team_member_{member_id}.jpg"
    image.save(destination, format="JPEG", quality=92, optimize=True)

    return str(destination.relative_to(BASE_DIR))


def remove_team_image(relative_path: str) -> None:
    if not relative_path:
        return

    try:
        image_path = BASE_DIR / relative_path
        if image_path.exists():
            image_path.unlink()
    except OSError:
        pass



def load_outreach_pipeline() -> pd.DataFrame:
    with sqlite3.connect(OUTREACH_DB_PATH) as conn:
        return pd.read_sql_query(
            """
            SELECT *
            FROM outreach_pipeline
            ORDER BY updated_at DESC, id DESC
            """,
            conn,
        )


def upsert_outreach_record(
    site_id,
    site,
    status,
    contact_name="",
    contact_email="",
    whatsapp="",
    last_contacted="",
    next_follow_up="",
    notes="",
):
    now = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(OUTREACH_DB_PATH) as conn:
        existing = conn.execute(
            "SELECT id FROM outreach_pipeline WHERE site=?",
            (site,),
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE outreach_pipeline
                SET site_id=?, status=?, contact_name=?,
                    contact_email=?, whatsapp=?,
                    last_contacted=?, next_follow_up=?,
                    notes=?, updated_at=?
                WHERE site=?
                """,
                (
                    site_id,
                    status,
                    contact_name,
                    contact_email,
                    whatsapp,
                    last_contacted,
                    next_follow_up,
                    notes,
                    now,
                    site,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO outreach_pipeline(
                    site_id, site, status, contact_name,
                    contact_email, whatsapp, last_contacted,
                    next_follow_up, notes, created_at, updated_at
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    site_id,
                    site,
                    status,
                    contact_name,
                    contact_email,
                    whatsapp,
                    last_contacted,
                    next_follow_up,
                    notes,
                    now,
                    now,
                ),
            )

        conn.commit()


def make_database_backup_zip() -> bytes:
    buffer = io.BytesIO()

    with zipfile.ZipFile(
        buffer,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as archive:
        database_dir = BASE_DIR / "database"

        if database_dir.exists():
            for db_file in database_dir.rglob("*"):
                if db_file.is_file():
                    archive.write(
                        db_file,
                        Path("database") / db_file.name,
                    )

        assets_dir = BASE_DIR / "assets"
        if assets_dir.exists():
            for asset_file in assets_dir.rglob("*"):
                if asset_file.is_file():
                    archive.write(
                        asset_file,
                        Path("assets") / asset_file.relative_to(assets_dir),
                    )

    return buffer.getvalue()


def restore_database_backup(uploaded_zip) -> tuple[bool, str]:
    try:
        data = uploaded_zip.getvalue()
        with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
            names = archive.namelist()

            unsafe = [
                name for name in names
                if ".." in Path(name).parts
                or Path(name).is_absolute()
            ]
            if unsafe:
                return False, "Unsafe ZIP paths detected."

            for name in names:
                if not (
                    name.startswith("database/")
                    or name.startswith("assets/")
                ):
                    continue

                target = BASE_DIR / name
                target.parent.mkdir(parents=True, exist_ok=True)

                if not name.endswith("/"):
                    with archive.open(name) as src, open(target, "wb") as dst:
                        shutil.copyfileobj(src, dst)

        return True, "Backup successfully restore ho gaya."
    except Exception as error:
        return False, f"Restore error: {error}"



def load_admin_private_contacts() -> pd.DataFrame:
    with sqlite3.connect(ADMIN_CONTACTS_DB_PATH) as conn:
        return pd.read_sql_query(
            """
            SELECT *
            FROM admin_private_contacts
            ORDER BY updated_at DESC, id DESC
            """,
            conn,
        )


def save_admin_private_contact(
    contact_id,
    contact_type,
    full_name,
    company,
    job_title,
    email,
    phone,
    whatsapp,
    website,
    linkedin,
    address,
    notes,
):
    now = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(ADMIN_CONTACTS_DB_PATH) as conn:
        if contact_id:
            conn.execute(
                """
                UPDATE admin_private_contacts
                SET contact_type=?, full_name=?, company=?,
                    job_title=?, email=?, phone=?, whatsapp=?,
                    website=?, linkedin=?, address=?, notes=?,
                    updated_at=?
                WHERE id=?
                """,
                (
                    contact_type,
                    full_name,
                    company,
                    job_title,
                    email,
                    phone,
                    whatsapp,
                    website,
                    linkedin,
                    address,
                    notes,
                    now,
                    int(contact_id),
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO admin_private_contacts(
                    contact_type, full_name, company, job_title,
                    email, phone, whatsapp, website, linkedin,
                    address, notes, created_at, updated_at
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    contact_type,
                    full_name,
                    company,
                    job_title,
                    email,
                    phone,
                    whatsapp,
                    website,
                    linkedin,
                    address,
                    notes,
                    now,
                    now,
                ),
            )
        conn.commit()


def delete_admin_private_contact(contact_id):
    with sqlite3.connect(ADMIN_CONTACTS_DB_PATH) as conn:
        conn.execute(
            "DELETE FROM admin_private_contacts WHERE id=?",
            (int(contact_id),),
        )
        conn.commit()



def domain_from_url(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    value = re.sub(r"^https?://", "", value, flags=re.I)
    value = re.sub(r"^www\.", "", value, flags=re.I)
    return value.split("/")[0].strip().lower()


def pretty_site_name(domain: str) -> str:
    base = domain.split(".")[0] if domain else "your website"
    return re.sub(r"[-_]+", " ", base).strip().title()


def first_name_from_full_name(name: str) -> str:
    cleaned = str(name or "").strip()
    if not cleaned:
        return ""
    return cleaned.split()[0]


def generate_outreach_messages(
    website_url: str,
    recipient_type: str,
    recipient_name: str,
    niche: str,
    sender_name: str,
    sender_company: str,
    sender_role: str,
    purpose: str,
    custom_offer: str,
    tone: str,
):
    domain = domain_from_url(website_url)
    site_name = pretty_site_name(domain)
    first_name = first_name_from_full_name(recipient_name)

    greeting = f"Hi {first_name}," if first_name else f"Hi {recipient_type},"
    niche_text = niche.strip() if niche.strip() else "your niche"
    sender = sender_name.strip() or "Aaquib"
    company = sender_company.strip() or "Aaquib Digital Solutions"
    role = sender_role.strip() or "SEO & Outreach Specialist"
    offer = custom_offer.strip()

    role_openers = {
        "Author": (
            f"I came across {domain or site_name} while researching quality "
            f"content in {niche_text}. I liked the way your site presents its articles "
            f"and wanted to reach out about a possible content collaboration."
        ),
        "Admin": (
            f"I found {domain or site_name} while looking for strong publishing "
            f"opportunities in {niche_text}. I’m reaching out to ask about your current "
            f"guest-post or link-insertion availability."
        ),
        "Editor": (
            f"I’ve been reviewing publishers in {niche_text}, and "
            f"{domain or site_name} stood out as a relevant publication. "
            f"I’d like to explore an editorial collaboration with your team."
        ),
        "Site Owner": (
            f"I came across {domain or site_name} while researching websites in "
            f"{niche_text}. I’d like to discuss a potential publishing and outreach "
            f"collaboration that could be useful for both sides."
        ),
        "Manager": (
            f"I found {domain or site_name} during publisher research in {niche_text}. "
            f"I’m contacting you to explore an ongoing guest-post and outreach partnership."
        ),
    }
    opener = role_openers.get(recipient_type, role_openers["Admin"])

    purpose_lines = {
        "Guest Post": (
            "We can provide an original, well-researched article written to match "
            "your audience and editorial requirements."
        ),
        "Link Insertion": (
            "We are interested in discussing a relevant link insertion within an "
            "existing article, where it naturally fits the content."
        ),
        "Guest Post + Link Insertion": (
            "We are open to either a new guest post or a relevant link insertion, "
            "depending on what works best for your editorial policy."
        ),
        "Long-term Partnership": (
            "We are looking for reliable publishing partners for recurring placements "
            "rather than a one-time collaboration."
        ),
        "Price Inquiry": (
            "Could you please share your current publishing options, pricing, "
            "turnaround time and payment terms?"
        ),
    }
    purpose_line = purpose_lines.get(purpose, purpose_lines["Guest Post"])

    if offer:
        offer_line = f"\n\nA little more context: {offer}"
    else:
        offer_line = ""

    if tone == "Friendly":
        closing = (
            "If this is something you’re open to, I’d be happy to work around your "
            "guidelines. Could you share the available options and current rates?"
        )
    elif tone == "Short & Direct":
        closing = (
            "Please share your availability, current rate, turnaround time and "
            "publishing requirements."
        )
    else:
        closing = (
            "If you are currently accepting collaborations, please share your "
            "publishing guidelines, pricing, turnaround time and payment terms."
        )

    subject_lines = [
        f"Collaboration opportunity with {domain or site_name}",
        f"Guest post inquiry for {domain or site_name}",
        f"Publishing partnership — {company}",
    ]
    if purpose == "Link Insertion":
        subject_lines[1] = f"Link insertion inquiry for {domain or site_name}"
    elif purpose == "Long-term Partnership":
        subject_lines[1] = f"Long-term publishing partnership with {domain or site_name}"

    email = f"""{greeting}

{opener}

{purpose_line}{offer_line}

{closing}

Best regards,
{sender}
{role}
{company}"""

    follow_up_1 = f"""{greeting}

Just following up on my previous message regarding a possible collaboration with {domain or site_name}.

If you are accepting {purpose.lower()} opportunities, could you please share your current pricing, requirements and turnaround time?

Thanks,
{sender}
{company}"""

    follow_up_2 = f"""{greeting}

One last quick follow-up regarding {domain or site_name}. We’re still interested in working with your publication and can adapt to your editorial requirements.

If collaboration is currently available, please send over the details whenever convenient.

Best,
{sender}
{company}"""

    linkedin = (
        f"Hi {first_name or recipient_type}, I came across {domain or site_name} while "
        f"researching publishers in {niche_text}. I’m with {company} and wanted to "
        f"connect regarding a possible {purpose.lower()} collaboration. "
        f"If this is relevant, I’d be happy to share the details. Thanks!"
    )

    whatsapp = (
        f"Hi {first_name or recipient_type}, this is {sender} from {company}. "
        f"I found {domain or site_name} while researching {niche_text} websites. "
        f"I wanted to ask if you currently accept {purpose.lower()} collaborations. "
        f"If yes, please share your pricing, requirements and turnaround time. Thanks!"
    )

    return {
        "domain": domain,
        "subject_lines": subject_lines,
        "email": email,
        "follow_up_1": follow_up_1,
        "follow_up_2": follow_up_2,
        "linkedin": linkedin,
        "whatsapp": whatsapp,
    }



def generate_client_outreach_messages(
    website_url: str,
    client_name: str,
    company_name: str,
    client_role: str,
    niche: str,
    service: str,
    problem_or_opportunity: str,
    sender_name: str,
    sender_company: str,
    sender_role: str,
    proof: str,
    cta: str,
    tone: str,
):
    domain = domain_from_url(website_url)
    site_name = company_name.strip() or pretty_site_name(domain)
    first_name = first_name_from_full_name(client_name)

    sender = sender_name.strip() or "Aaquib"
    sender_company = sender_company.strip() or "Aaquib Digital Solutions"
    sender_role = sender_role.strip() or "SEO & Outreach Specialist"
    greeting = f"Hi {first_name}," if first_name else "Hi there,"
    niche_text = niche.strip() or "your industry"

    service_benefits = {
        "SEO": (
            "improve organic visibility, strengthen keyword rankings and create "
            "a clearer path to qualified search traffic"
        ),
        "Guest Posting": (
            "build relevant authority links through carefully selected guest-post placements"
        ),
        "Link Building": (
            "earn stronger, niche-relevant backlinks without relying on low-quality bulk links"
        ),
        "SEO + Guest Posting": (
            "combine on-site SEO improvements with relevant authority-building guest posts"
        ),
        "Content Outreach": (
            "expand content reach through publisher relationships and targeted outreach"
        ),
        "Digital PR / Outreach": (
            "build brand visibility and authority through personalized publisher outreach"
        ),
    }
    benefit = service_benefits.get(service, service_benefits["SEO + Guest Posting"])

    opportunity = problem_or_opportunity.strip()
    if opportunity:
        observation = (
            f"While reviewing {domain or site_name}, I noticed an opportunity around "
            f"{opportunity}."
        )
    else:
        observation = (
            f"I came across {domain or site_name} while researching businesses in "
            f"{niche_text}, and I thought there may be an opportunity to strengthen "
            f"its SEO and outreach performance."
        )

    proof_line = ""
    if proof.strip():
        proof_line = f"\n\nFor context, {proof.strip()}"

    cta_text = cta.strip() or (
        "Would you be open to a short conversation? I can share a few practical ideas "
        "specific to your website first—no obligation."
    )

    if tone == "Friendly":
        intro = (
            f"I’m {sender} from {sender_company}. I work with businesses on {service.lower()} "
            f"to {benefit}."
        )
    elif tone == "Short & Direct":
        intro = (
            f"I’m {sender} from {sender_company}. We help businesses with {service.lower()} "
            f"to {benefit}."
        )
    else:
        intro = (
            f"My name is {sender}, {sender_role} at {sender_company}. "
            f"We support businesses with {service.lower()} strategies designed to {benefit}."
        )

    subject_lines = [
        f"A few growth ideas for {domain or site_name}",
        f"{service} opportunity for {site_name}",
        f"Quick idea for {site_name}",
    ]

    cold_email = f"""{greeting}

{observation}

{intro}{proof_line}

{cta_text}

Best regards,
{sender}
{sender_role}
{sender_company}"""

    follow_up_1 = f"""{greeting}

Just following up on my note about {domain or site_name}.

I’d be happy to send over 2–3 quick {service.lower()} ideas specific to the site, so you can see whether they’re useful before discussing anything further.

Would that be helpful?

Best,
{sender}
{sender_company}"""

    follow_up_2 = f"""{greeting}

One last quick follow-up regarding {domain or site_name}.

If improving {service.lower()} is a priority this quarter, I’d be glad to share a simple action plan based on what I noticed. If the timing isn’t right, no worries at all.

Best regards,
{sender}
{sender_company}"""

    linkedin_connection = (
        f"Hi {first_name or client_role or 'there'}, I came across {site_name} while "
        f"researching {niche_text}. I work in {service} at {sender_company} and thought "
        f"it would be good to connect."
    )

    linkedin_dm = (
        f"Hi {first_name or client_role or 'there'}, thanks for connecting. "
        f"I had a quick look at {domain or site_name} and noticed a few opportunities "
        f"where {service.lower()} could help {benefit}. I can send 2–3 specific ideas "
        f"for the site if useful—no pitch deck needed."
    )

    whatsapp = (
        f"Hi {first_name or 'there'}, this is {sender} from {sender_company}. "
        f"I came across {domain or site_name} and noticed a few possible opportunities "
        f"around {service.lower()}. We help businesses {benefit}. "
        f"If useful, I can send a few quick recommendations for your site here."
    )

    mini_audit = (
        f"Website: {domain or site_name}\n"
        f"Industry: {niche_text}\n"
        f"Service opportunity: {service}\n"
        f"Observation: {opportunity or 'Review SEO visibility, backlinks, content gaps and outreach opportunities.'}\n"
        f"Suggested next step: Share 2–3 tailored recommendations and ask for a short call only if relevant."
    )

    return {
        "domain": domain,
        "subject_lines": subject_lines,
        "cold_email": cold_email,
        "follow_up_1": follow_up_1,
        "follow_up_2": follow_up_2,
        "linkedin_connection": linkedin_connection,
        "linkedin_dm": linkedin_dm,
        "whatsapp": whatsapp,
        "mini_audit": mini_audit,
    }


# =========================================================
# SESSION
# =========================================================
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


df = load_sites()


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-logo"><span class="material-symbols-rounded">auto_awesome</span></div>
            <div>
                <div class="sidebar-title">GP Site Finder Pro</div>
                <div class="sidebar-sub">Aaquib Digital Solutions</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Statistics",
            "Search Websites",
            "Outreach Generator",
            "Client Outreach Generator",
            "Add New Site",
            "Import Excel",
            "Edit Site",
            "Delete Site",
            "Duplicate Finder",
            "Export Results",
            "Favorites",
            "Private Contacts",
            "Admin Contact Vault",
            "Outreach Pipeline",
            "Our Team",
            "Contact Us",
            "My Profile / Contact",
            "Backup & Restore",
            "Settings",
            "Admin Login",
        ],
        label_visibility="collapsed",
        key="nav_page",
    )

    st.markdown(
        f"""
        <div class="sidebar-user">
            <div class="sidebar-user-name">{html.escape(profile_settings.get('name','Aaquib SEO'))}</div>
            <div class="sidebar-user-role">{'Administrator · Signed in' if st.session_state.admin_logged_in else 'Workspace · Admin locked'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<span class="brand-badge">Aaquib Digital Solutions</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="main-title">GP Site Finder Pro</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">A premium research workspace for guest posting, publisher outreach and link acquisition intelligence.</p>',
    unsafe_allow_html=True,
)


# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":
    total_sites = len(df)
    total_countries = (
        df["country"].fillna("").astype(str).str.strip().replace("", pd.NA).dropna().nunique()
        if "country" in df.columns else 0
    )
    dr_values = pd.to_numeric(df.get("dr", pd.Series(dtype=float)), errors="coerce")
    price_values = pd.to_numeric(df.get("general_price", pd.Series(dtype=float)), errors="coerce")
    average_dr = 0 if pd.isna(dr_values.mean()) else dr_values.mean()
    average_price = 0 if pd.isna(price_values.mean()) else price_values.mean()

    if HERO_IMAGE_PATH.exists():
        hero_b64 = __import__('base64').b64encode(HERO_IMAGE_PATH.read_bytes()).decode('ascii')
        hero_visual = f'<div class="hero-photo-shell"><img src="data:image/png;base64,{hero_b64}" alt="Guest posting research network"></div>'
    else:
        hero_visual = '<div class="hero-photo-shell" style="background:radial-gradient(circle at 70% 35%,rgba(24,191,197,.35),transparent 20%),radial-gradient(circle at 40% 60%,rgba(112,69,214,.45),transparent 26%),linear-gradient(135deg,#121A34,#113943);"></div>'

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-copy">
                <div class="hero-kicker">Outreach Intelligence</div>
                <div class="hero-title">Find, qualify and place guest posts faster.</div>
                <div class="hero-text">
                    {total_sites:,} publisher records across {total_countries:,} countries, enriched with DR,
                    traffic, pricing, link type and outreach information.
                </div>
                <div class="hero-pills">
                    <span class="hero-pill">Smart Search</span>
                    <span class="hero-pill">SEO Metrics</span>
                    <span class="hero-pill">Private CRM</span>
                    <span class="hero-pill">Excel Import</span>
                </div>
            </div>
            {hero_visual}
        </div>
        """,
        unsafe_allow_html=True,
    )

    action1, action2, spacer = st.columns([1.1,1.1,5.8])
    with action1:
        if st.button("Search Websites", type="primary", use_container_width=True):
            st.session_state.nav_page = "Search Websites"
            st.rerun()
    with action2:
        if st.button("Export Results", use_container_width=True):
            st.session_state.nav_page = "Export Results"
            st.rerun()

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("database", "", "Total Websites", f"{total_sites:,}", "Publisher inventory"),
        ("public", "teal", "Countries", f"{total_countries:,}", "Global coverage"),
        ("speed", "sage", "Average DR", f"{average_dr:.1f}", "Authority benchmark"),
        ("payments", "copper", "Average Price", f"${average_price:.0f}", "General placement price"),
    ]
    for col, (icon, tone, label, value, delta) in zip([c1,c2,c3,c4], cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon {tone}"><span class="material-symbols-rounded">{icon}</span></div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-delta">{delta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title">Guest Posting Analytics</div><div class="section-kicker">Real charts generated from your current publisher database.</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown('<div class="surface-card"><b>Top publisher countries</b><div class="section-kicker">Where most opportunities are located</div></div>', unsafe_allow_html=True)
        if "country" in df.columns:
            country_chart = df["country"].fillna("Unknown").astype(str).replace("", "Unknown").value_counts().head(10)
            st.bar_chart(country_chart)
    with ch2:
        st.markdown('<div class="surface-card"><b>Domain Rating distribution</b><div class="section-kicker">Authority profile of the database</div></div>', unsafe_allow_html=True)
        dr_numeric = pd.to_numeric(df.get("dr", pd.Series(index=df.index, dtype=float)), errors="coerce")
        dr_bins = pd.cut(dr_numeric, bins=[-1,20,40,60,80,1000], labels=["0–20","21–40","41–60","61–80","81+"])
        st.bar_chart(dr_bins.value_counts().sort_index())

    top_df = df.copy()
    top_df["_dr_num"] = pd.to_numeric(top_df.get("dr", pd.Series(index=top_df.index)), errors="coerce")
    top_df["_price_num"] = pd.to_numeric(top_df.get("general_price", pd.Series(index=top_df.index)), errors="coerce")
    top_df = top_df.sort_values(["_dr_num","_price_num"], ascending=[False,True]).head(7)
    rows_html = ""
    for _, r in top_df.iterrows():
        domain = html.escape(str(r.get("site", "") or ""))
        country = html.escape(str(r.get("country", "") or "Unknown"))
        category = html.escape(str(r.get("type", "") or "General"))
        link_type = html.escape(str(r.get("link_type", "") or ""))
        dr = "-" if pd.isna(r.get("_dr_num")) else f"{float(r['_dr_num']):.0f}"
        price = "-" if pd.isna(r.get("_price_num")) else f"${float(r['_price_num']):.0f}"
        rows_html += f"<div class='publisher-row'><div><div class='publisher-site'>{domain}</div><div class='publisher-meta'>{country} · {category} · {link_type}</div></div><div class='dr-badge'>DR {dr}</div><div class='price-tag'>{price}</div></div>"
    st.markdown(
        f"<div class='publisher-list'><div class='publisher-head'><div><div class='publisher-title'>Highest authority publishers</div><div class='publisher-sub'>Top opportunities ranked by Domain Rating</div></div></div>{rows_html}</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# SEARCH
# =========================================================
elif page == "Search Websites":
    st.header("Search Websites")
    st.caption(
        "Fast search enabled — sirf selected page ke records table me render honge."
    )

    search = st.text_input(
        "Search website, country, niche or source file",
        placeholder="Paste full URL or search: https://openskynews.net/  |  India  |  technology",
    )
    st.caption(
        "Full URLs supported — http/https, www, paths and trailing slash are handled automatically."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        country = st.selectbox(
            "🌍 Country",
            safe_unique(df, "country"),
        )

    with c2:
        payment = st.selectbox(
            "💳 Payment",
            safe_unique(df, "payment_method"),
        )

    with c3:
        link_type = st.selectbox(
            "🔗 Link Type",
            safe_unique(df, "link_type"),
        )

    with c4:
        sheet = st.selectbox(
            "📄 Sheet",
            safe_unique(df, "sheet_name"),
        )

    c5, c6, c7 = st.columns(3)

    with c5:
        min_dr = st.number_input(
            "⭐ Minimum DR",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

    with c6:
        max_price = st.number_input(
            "💰 Maximum General Price",
            min_value=0.0,
            value=100000.0,
            step=1.0,
        )

    with c7:
        page_size = st.selectbox(
            "📄 Rows per page",
            [25, 50, 100, 200],
            index=1,
        )

    filtered = df

    if search.strip():
        raw_query = search.strip().lower()
        smart_query = normalize_search_query(raw_query)

        # Search both the original text and the normalized domain.
        # This supports:
        # https://example.com/
        # http://www.example.com/page
        # www.example.com
        # example.com
        queries = [
            value
            for value in {raw_query, smart_query}
            if value
        ]

        search_mask = pd.Series(
            False,
            index=filtered.index,
        )

        for query in queries:
            search_mask = search_mask | (
                filtered["_search_text"].str.contains(
                    query,
                    regex=False,
                    na=False,
                )
            )

        # Direct normalized domain match is checked too.
        if "site" in filtered.columns and smart_query:
            normalized_sites = (
                filtered["site"]
                .fillna("")
                .astype(str)
                .map(normalize_search_query)
            )

            search_mask = search_mask | (
                normalized_sites == smart_query
            )

        filtered = filtered[search_mask]

    if country != "All":
        filtered = filtered[filtered["country"] == country]

    if payment != "All":
        filtered = filtered[
            filtered["payment_method"] == payment
        ]

    if link_type != "All":
        filtered = filtered[
            filtered["link_type"] == link_type
        ]

    if sheet != "All":
        filtered = filtered[
            filtered["sheet_name"] == sheet
        ]

    filtered = filtered[
        (filtered["_dr_num"].fillna(-1) >= min_dr)
        & (filtered["_price_num"].fillna(0) <= max_price)
    ]

    total_results = len(filtered)
    total_pages = max(
        1,
        (total_results + page_size - 1) // page_size,
    )

    page_number = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
    )

    start_row = (page_number - 1) * page_size
    end_row = min(start_row + page_size, total_results)

    visible_columns = [
        column
        for column in [
            "id",
            "site",
            "country",
            "da",
            "dr",
            "traffic",
            "general_price",
            "casino_price",
            "payment_method",
            "tat",
            "type",
            "link_type",
            "source_file",
            "sheet_name",
            "favorite",
        ]
        if column in filtered.columns
    ]

    page_df = filtered.iloc[start_row:end_row][visible_columns]

    st.info(
        f"🔎 {total_results:,} matching websites • "
        f"Showing {start_row + 1 if total_results else 0:,}–{end_row:,} • "
        f"Page {page_number}/{total_pages}"
    )

    st.dataframe(
        page_df,
        use_container_width=True,
        hide_index=True,
        height=560,
    )

    # ---------- Quick Row Actions ----------
    st.markdown("### ⚡ Quick Row Actions")

    if page_df.empty:
        st.caption("Action ke liye is page par koi website available nahi hai.")
    else:
        action_options = {
            f"{row['site']} | ID {int(row['id'])}": int(row["id"])
            for _, row in page_df.iterrows()
        }

        selected_action_label = st.selectbox(
            "Website select karein",
            list(action_options.keys()),
            key="search_action_site",
        )

        selected_action_id = action_options[selected_action_label]
        selected_action_row = df[df["id"] == selected_action_id].iloc[0]
        selected_domain = normalize_domain(selected_action_row["site"])
        selected_url = (
            selected_action_row["site"]
            if str(selected_action_row["site"]).lower().startswith(
                ("http://", "https://")
            )
            else f"https://{selected_action_row['site']}"
        )

        st.code(selected_domain, language=None)

        a1, a2, a3 = st.columns(3)

        with a1:
            st.link_button(
                "🌐 Open Website",
                selected_url,
                use_container_width=True,
            )

        with a2:
            is_favorite = bool(selected_action_row.get("favorite", 0))
            favorite_text = (
                "☆ Remove Favorite"
                if is_favorite
                else "⭐ Add Favorite"
            )

            if st.button(
                favorite_text,
                use_container_width=True,
                key="quick_favorite",
            ):
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(
                        "UPDATE sites SET favorite=? WHERE id=?",
                        (
                            0 if is_favorite else 1,
                            selected_action_id,
                        ),
                    )
                    conn.commit()

                refresh_sites()
                st.success("Favorite status update ho gaya.")
                st.rerun()

        with a3:
            if not st.session_state.admin_logged_in:
                st.button(
                    "🗑️ Delete (Admin Only)",
                    disabled=True,
                    use_container_width=True,
                )
            else:
                confirm_quick_delete = st.checkbox(
                    "Delete confirm",
                    key="quick_delete_confirm",
                )

                if st.button(
                    "🗑️ Delete Selected",
                    type="primary",
                    use_container_width=True,
                    disabled=not confirm_quick_delete,
                    key="quick_delete",
                ):
                    with sqlite3.connect(DB_PATH) as conn:
                        conn.execute(
                            "DELETE FROM sites WHERE id=?",
                            (selected_action_id,),
                        )
                        conn.commit()

                    refresh_sites()
                    st.success("Selected website delete ho gayi.")
                    st.rerun()

    export_columns = [
        column
        for column in df.columns
        if not column.startswith("_")
    ]

    csv_data = filtered[export_columns].to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 Download All Filtered Results",
        csv_data,
        "filtered_websites.csv",
        "text/csv",
        use_container_width=True,
    )


# =========================================================
# IMPORT
# =========================================================
elif page == "Import Excel":
    if require_admin():
        st.header("Import Excel or CSV")
        uploaded_file = st.file_uploader(
            "Choose Excel or CSV File",
            type=["xlsx", "xlsm", "csv"],
        )

        if uploaded_file is not None:
            try:
                filename = uploaded_file.name
                lower_name = filename.lower()

                if lower_name.endswith(".csv"):
                    sheets = ["CSV"]
                else:
                    uploaded_file.seek(0)
                    sheets = pd.ExcelFile(uploaded_file).sheet_names

                st.success(f"✅ File loaded: {filename}")
                selected_sheet = st.selectbox("📄 Select Excel Sheet / Tab", sheets)

                uploaded_file.seek(0)
                if lower_name.endswith(".csv"):
                    raw_df = pd.read_csv(uploaded_file, header=None, dtype=str, on_bad_lines="skip")
                else:
                    raw_df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, header=None, dtype=str)

                header_row = find_header_row(raw_df)

                if header_row is None:
                    st.error("Website/Site/URL/Domain header row nahi mili.")
                    st.dataframe(raw_df.head(20), use_container_width=True)
                else:
                    uploaded_file.seek(0)
                    if lower_name.endswith(".csv"):
                        imported_df = pd.read_csv(uploaded_file, header=header_row, dtype=str, on_bad_lines="skip")
                    else:
                        imported_df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, header=header_row, dtype=str)

                    imported_df = imported_df.dropna(how="all")
                    prepared_df = prepare_import_dataframe(imported_df, filename, selected_sheet)

                    a, b, c = st.columns(3)
                    a.metric("📄 Sheet", selected_sheet)
                    b.metric("📋 Rows Read", f"{len(imported_df):,}")
                    c.metric("🌐 Valid Websites", f"{len(prepared_df):,}")

                    st.dataframe(prepared_df.head(50), use_container_width=True, hide_index=True, height=500)

                    confirm = st.checkbox("✅ Preview check kar li hai.")
                    if st.button(
                        "📥 Import Selected Sheet into Database",
                        type="primary",
                        use_container_width=True,
                        disabled=not confirm,
                    ):
                        count = save_imported_sites(prepared_df)
                        refresh_sites()
                        st.success(f"✅ {count:,} websites permanently save/update ho gayi hain.")
                        st.balloons()
            except Exception as exc:
                st.error(f"Import error: {type(exc).__name__}: {exc}")


# =========================================================
# ADD
# =========================================================
# OUTREACH GENERATOR
# =========================================================
elif page == "Outreach Generator":
    st.header("Outreach Message Generator")
    st.caption(
        "Website URL aur contact role se personalized cold email, follow-ups, "
        "LinkedIn aur WhatsApp message generate karein."
    )

    g1, g2 = st.columns([1.2, 1])

    with g1:
        website_url = st.text_input(
            "Website URL*",
            placeholder="https://example.com/",
            key="outreach_gen_url",
        )
        recipient_type = st.selectbox(
            "Recipient Type",
            ["Author", "Admin", "Editor", "Site Owner", "Manager"],
            key="outreach_gen_recipient_type",
        )
        recipient_name = st.text_input(
            "Recipient Name (optional)",
            placeholder="John Doe",
            key="outreach_gen_recipient_name",
        )
        niche = st.text_input(
            "Website Niche",
            placeholder="Technology, Business, SaaS...",
            key="outreach_gen_niche",
        )

    with g2:
        purpose = st.selectbox(
            "Outreach Purpose",
            [
                "Guest Post",
                "Link Insertion",
                "Guest Post + Link Insertion",
                "Long-term Partnership",
                "Price Inquiry",
            ],
            key="outreach_gen_purpose",
        )
        tone = st.selectbox(
            "Tone",
            ["Friendly", "Professional", "Short & Direct"],
            key="outreach_gen_tone",
        )
        sender_name = st.text_input(
            "Your Name",
            value=profile_settings.get("name", "Aaquib SEO"),
            key="outreach_gen_sender",
        )
        sender_company = st.text_input(
            "Company",
            value=profile_settings.get(
                "company",
                profile_settings.get(
                    "brand",
                    "Aaquib Digital Solutions",
                ),
            ),
            key="outreach_gen_company",
        )
        sender_role = st.text_input(
            "Your Role",
            value=profile_settings.get(
                "role",
                "SEO, Guest Post & Outreach Specialist",
            ),
            key="outreach_gen_role",
        )

    custom_offer = st.text_area(
        "Extra Details / Offer (optional)",
        placeholder=(
            "Example: We can provide original content, flexible anchor text, "
            "fast payment, and are looking for long-term collaboration."
        ),
        height=90,
        key="outreach_gen_offer",
    )

    if st.button(
        "Generate Outreach Messages",
        type="primary",
        use_container_width=True,
    ):
        if not website_url.strip():
            st.error("Website URL required hai.")
        else:
            generated = generate_outreach_messages(
                website_url,
                recipient_type,
                recipient_name,
                niche,
                sender_name,
                sender_company,
                sender_role,
                purpose,
                custom_offer,
                tone,
            )
            st.session_state.outreach_generated = generated

    generated = st.session_state.get("outreach_generated")

    if generated:
        st.divider()

        st.markdown("### Subject Lines")
        for i, subject in enumerate(generated["subject_lines"], start=1):
            st.code(subject, language=None)

        st.markdown("### Cold Email")
        st.text_area(
            "Generated Email",
            value=generated["email"],
            height=310,
            key="generated_cold_email",
        )

        st.markdown("### Follow-up #1")
        st.text_area(
            "First Follow-up",
            value=generated["follow_up_1"],
            height=220,
            key="generated_followup_1",
        )

        st.markdown("### Follow-up #2")
        st.text_area(
            "Second Follow-up",
            value=generated["follow_up_2"],
            height=220,
            key="generated_followup_2",
        )

        m1, m2 = st.columns(2)

        with m1:
            st.markdown("### LinkedIn Message")
            st.text_area(
                "LinkedIn DM",
                value=generated["linkedin"],
                height=190,
                key="generated_linkedin",
            )

        with m2:
            st.markdown("### WhatsApp Message")
            st.text_area(
                "WhatsApp Message",
                value=generated["whatsapp"],
                height=190,
                key="generated_whatsapp",
            )

        st.caption(
            "Tip: generated text editable hai — send karne se pehle website aur "
            "recipient ke mutabiq 1–2 lines personalize kar lena."
        )

        st.markdown("### Save to Outreach Pipeline")

        if st.button(
            "Save Website to Pipeline",
            use_container_width=True,
            key="save_generated_to_pipeline",
        ):
            domain = generated["domain"]
            matched = df[
                df["site"]
                .fillna("")
                .astype(str)
                .map(domain_from_url)
                == domain
            ]

            if not matched.empty:
                site_row = matched.iloc[0]
                site_id = int(site_row["id"])
            else:
                site_id = None

            upsert_outreach_record(
                site_id,
                domain,
                "New",
                recipient_name.strip(),
                "",
                "",
                "",
                "",
                (
                    f"Purpose: {purpose}\n"
                    f"Generated cold email for {recipient_type}.\n\n"
                    f"{generated['email']}"
                ),
            )
            st.success("Website Outreach Pipeline me save ho gayi.")


# =========================================================
# CLIENT OUTREACH GENERATOR
# =========================================================
elif page == "Client Outreach Generator":
    st.header("Client Outreach Generator")
    st.caption(
        "Potential SEO / guest-post clients ke liye cold email, LinkedIn aur "
        "WhatsApp messages generate karein."
    )

    c1, c2 = st.columns(2)

    with c1:
        client_website = st.text_input(
            "Client Website URL*",
            placeholder="https://clientwebsite.com",
            key="client_outreach_website",
        )
        client_name = st.text_input(
            "Client / Decision Maker Name",
            placeholder="Sarah",
            key="client_outreach_name",
        )
        client_company = st.text_input(
            "Company Name",
            placeholder="Acme Inc.",
            key="client_outreach_company",
        )
        client_role = st.selectbox(
            "Decision Maker Role",
            [
                "Founder / Owner",
                "CEO",
                "Marketing Manager",
                "SEO Manager",
                "Head of Growth",
                "Agency Owner",
                "Other",
            ],
            key="client_outreach_role",
        )
        client_niche = st.text_input(
            "Business Niche",
            placeholder="SaaS, Law Firm, E-commerce, Real Estate...",
            key="client_outreach_niche",
        )

    with c2:
        client_service = st.selectbox(
            "Service to Pitch",
            [
                "SEO",
                "Guest Posting",
                "Link Building",
                "SEO + Guest Posting",
                "Content Outreach",
                "Digital PR / Outreach",
            ],
            index=3,
            key="client_outreach_service",
        )
        client_tone = st.selectbox(
            "Tone",
            ["Friendly", "Professional", "Short & Direct"],
            key="client_outreach_tone",
        )
        client_sender_name = st.text_input(
            "Your Name",
            value=profile_settings.get("name", "Aaquib SEO"),
            key="client_sender_name",
        )
        client_sender_company = st.text_input(
            "Your Company",
            value=profile_settings.get(
                "company",
                profile_settings.get("brand", "Aaquib Digital Solutions"),
            ),
            key="client_sender_company",
        )
        client_sender_role = st.text_input(
            "Your Role",
            value=profile_settings.get(
                "role",
                "SEO, Guest Post & Outreach Specialist",
            ),
            key="client_sender_role",
        )

    client_problem = st.text_area(
        "What did you notice? (optional but recommended)",
        placeholder=(
            "Example: site has useful content but weak backlink profile, "
            "important pages are not ranking, competitors have stronger authority links..."
        ),
        height=95,
        key="client_outreach_problem",
    )

    p1, p2 = st.columns(2)
    with p1:
        client_proof = st.text_area(
            "Credibility / Proof (optional)",
            placeholder=(
                "Example: I manage publisher outreach across multiple niches "
                "and can source relevant dofollow placements."
            ),
            height=90,
            key="client_outreach_proof",
        )
    with p2:
        client_cta = st.text_area(
            "Call to Action (optional)",
            placeholder=(
                "Example: Can I send you a quick 3-point backlink and SEO audit?"
            ),
            height=90,
            key="client_outreach_cta",
        )

    if st.button(
        "Generate Client Messages",
        type="primary",
        use_container_width=True,
        key="generate_client_outreach",
    ):
        if not client_website.strip():
            st.error("Client Website URL required hai.")
        else:
            st.session_state.client_outreach_generated = (
                generate_client_outreach_messages(
                    client_website,
                    client_name,
                    client_company,
                    client_role,
                    client_niche,
                    client_service,
                    client_problem,
                    client_sender_name,
                    client_sender_company,
                    client_sender_role,
                    client_proof,
                    client_cta,
                    client_tone,
                )
            )

    client_generated = st.session_state.get(
        "client_outreach_generated"
    )

    if client_generated:
        st.divider()

        st.markdown("### Quick Client Research / Mini Audit")
        st.text_area(
            "Mini Audit Notes",
            value=client_generated["mini_audit"],
            height=170,
            key="client_generated_audit",
        )

        st.markdown("### Email Subject Lines")
        for subject in client_generated["subject_lines"]:
            st.code(subject, language=None)

        st.markdown("### Client Cold Email")
        st.text_area(
            "Cold Email",
            value=client_generated["cold_email"],
            height=300,
            key="client_generated_email",
        )

        f1, f2 = st.columns(2)
        with f1:
            st.markdown("### Follow-up #1")
            st.text_area(
                "Client Follow-up 1",
                value=client_generated["follow_up_1"],
                height=230,
                key="client_generated_followup1",
            )
        with f2:
            st.markdown("### Follow-up #2")
            st.text_area(
                "Client Follow-up 2",
                value=client_generated["follow_up_2"],
                height=230,
                key="client_generated_followup2",
            )

        l1, l2 = st.columns(2)
        with l1:
            st.markdown("### LinkedIn Connection Note")
            st.text_area(
                "Connection Note",
                value=client_generated["linkedin_connection"],
                height=160,
                key="client_linkedin_connection",
            )

            st.markdown("### LinkedIn DM")
            st.text_area(
                "LinkedIn Message",
                value=client_generated["linkedin_dm"],
                height=190,
                key="client_linkedin_dm",
            )

        with l2:
            st.markdown("### WhatsApp Client Message")
            st.text_area(
                "WhatsApp Pitch",
                value=client_generated["whatsapp"],
                height=190,
                key="client_whatsapp_pitch",
            )

        st.success(
            "Messages editable hain. Client ko send karne se pehle website ke "
            "real observation ke saath personalize karna best rahega."
        )


# =========================================================
elif page == "Add New Site":
    if require_admin():
        st.header("Add New Site")
        st.caption("Create a publisher record with full SEO metrics, commercial terms and editorial contact.")

        with st.form("add_form"):
            st.markdown('<div class="form-section-title">Website Details</div><div class="form-section-sub">Core publisher and niche information.</div>', unsafe_allow_html=True)
            w1, w2 = st.columns(2)
            with w1:
                site = st.text_input("Website / URL*", placeholder="example.com")
                country = st.text_input("Country", placeholder="United States")
                site_type = st.text_input("Niche / Category", placeholder="Tech & SaaS")
            with w2:
                source_file = st.text_input("Source", value="Web App")
                sheet_name = st.text_input("Sheet / Category", value="Added Sites")
                casino_price = st.text_input("Casino / Restricted Price", placeholder="Optional")

            st.markdown('<div class="form-section-title" style="margin-top:16px">Metrics & Pricing</div><div class="form-section-sub">SEO metrics and placement pricing.</div>', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                dr = st.text_input("Domain Rating", placeholder="40")
                payment_method = st.selectbox("Payment Method", ["", "PayPal", "Upfront", "After", "50% Advance", "Negotiable", "Bank Transfer", "Other"])
            with m2:
                da = st.text_input("Domain Authority", placeholder="35")
                link_type = st.selectbox("Link Type", ["", "Dofollow", "Nofollow", "Sponsored", "Mixed"])
            with m3:
                traffic = st.text_input("Monthly Traffic", placeholder="10000")
                general_price = st.text_input("Price (USD)", placeholder="120")
            with m4:
                tat = st.text_input("Turnaround", placeholder="3-7 days")
                commercial_note = st.text_input("Commercial Note", placeholder="Negotiable / fixed")

            st.markdown('<div class="form-section-title" style="margin-top:16px">Contact Information</div><div class="form-section-sub">Private outreach contact for this website.</div>', unsafe_allow_html=True)
            ct1, ct2 = st.columns(2)
            with ct1:
                contact_name = st.text_input("Contact Name", placeholder="John Doe")
                whatsapp = st.text_input("WhatsApp", placeholder="+92 300 1234567")
            with ct2:
                contact_email = st.text_input("Contact Email", placeholder="editor@example.com")
                contact_status = st.selectbox("Contact Status", ["New", "Contacted", "Negotiating", "Approved", "Rejected"])
            notes = st.text_area("Notes", placeholder="Guidelines, accepted niches, anchor text rules, editorial notes…", height=120)

            submitted = st.form_submit_button("Save Website", type="primary", use_container_width=True)

        if submitted:
            domain = normalize_domain(site)
            if not domain:
                st.error("Valid website/domain likhein.")
            else:
                now = datetime.now().isoformat(timespec="seconds")
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(
                        """
                        INSERT INTO sites(
                            site,country,da,dr,traffic,general_price,casino_price,
                            payment_method,tat,type,link_type,source_file,sheet_name,
                            favorite,created_at
                        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            domain,country,da,dr,traffic,general_price,casino_price,
                            payment_method,tat,site_type,link_type,source_file or "Web App",
                            sheet_name or "Added Sites",0,now,
                        ),
                    )
                    conn.commit()

                # Store outreach contact in the existing private-contact database.
                with sqlite3.connect(CONTACT_DB_PATH) as conn:
                    conn.execute(
                        """
                        INSERT INTO contacts(
                            domain,admin_name,email,whatsapp,telegram,status,
                            quoted_price,notes,updated_at
                        ) VALUES(?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(domain) DO UPDATE SET
                            admin_name=excluded.admin_name,
                            email=excluded.email,
                            whatsapp=excluded.whatsapp,
                            status=excluded.status,
                            quoted_price=excluded.quoted_price,
                            notes=excluded.notes,
                            updated_at=excluded.updated_at
                        """,
                        (
                            domain,contact_name,contact_email,whatsapp,"",
                            contact_status,general_price,
                            (notes + (f"\nCommercial: {commercial_note}" if commercial_note else "")).strip(),
                            now,
                        ),
                    )
                    conn.commit()
                refresh_sites()
                st.success("Website aur outreach contact permanently save ho gaye.")
                st.rerun()


# =========================================================
# EDIT
# =========================================================
elif page == "Edit Site":
    if require_admin():
        st.header("Edit Site")
        selected_id, row = site_selector(df)

        if row is not None:
            with st.form("edit_form"):
                c1, c2 = st.columns(2)
                with c1:
                    site = st.text_input("🌐 Website", value=clean_value(row["site"]))
                    country = st.text_input("🌍 Country", value=clean_value(row["country"]))
                    da = st.text_input("📈 DA", value=clean_value(row["da"]))
                    dr = st.text_input("⭐ DR", value=clean_value(row["dr"]))
                    traffic = st.text_input("📊 Traffic", value=clean_value(row["traffic"]))
                    general_price = st.text_input("💰 General Price", value=clean_value(row["general_price"]))
                with c2:
                    casino_price = st.text_input("🎰 Casino Price", value=clean_value(row["casino_price"]))
                    payment_method = st.text_input("💳 Payment", value=clean_value(row["payment_method"]))
                    tat = st.text_input("⏱️ TAT", value=clean_value(row["tat"]))
                    site_type = st.text_input("📁 Type/Niche", value=clean_value(row["type"]))
                    link_type = st.text_input("🔗 Link Type", value=clean_value(row["link_type"]))
                    sheet_name = st.text_input("📄 Sheet Name", value=clean_value(row["sheet_name"]))

                save = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

            if save:
                domain = normalize_domain(site)
                if not domain:
                    st.error("Valid domain likhein.")
                else:
                    with sqlite3.connect(DB_PATH) as conn:
                        conn.execute(
                            """
                            UPDATE sites SET
                                site=?,country=?,da=?,dr=?,traffic=?,general_price=?,
                                casino_price=?,payment_method=?,tat=?,type=?,link_type=?,
                                sheet_name=?
                            WHERE id=?
                            """,
                            (
                                domain,country,da,dr,traffic,general_price,
                                casino_price,payment_method,tat,site_type,
                                link_type,sheet_name,selected_id,
                            ),
                        )
                        conn.commit()
                    refresh_sites()
                    st.success("✅ Website update ho gayi.")
                    st.rerun()



            st.markdown("### Edit Outreach Contact")
            current_domain = normalize_domain(clean_value(row["site"]))
            with sqlite3.connect(CONTACT_DB_PATH) as conn:
                contact_row = conn.execute(
                    "SELECT admin_name,email,whatsapp,status,quoted_price,notes FROM contacts WHERE lower(domain)=lower(?)",
                    (current_domain,),
                ).fetchone()
            contact_row = contact_row or ("", "", "", "New", "", "")
            with st.form("edit_contact_form"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_name = st.text_input("Contact Name", value=clean_value(contact_row[0]))
                    e_whatsapp = st.text_input("WhatsApp", value=clean_value(contact_row[2]))
                with ec2:
                    e_email = st.text_input("Contact Email", value=clean_value(contact_row[1]))
                    statuses = ["New", "Contacted", "Negotiating", "Approved", "Rejected"]
                    current_status = clean_value(contact_row[3]) or "New"
                    e_status = st.selectbox("Contact Status", statuses, index=statuses.index(current_status) if current_status in statuses else 0)
                e_notes = st.text_area("Notes", value=clean_value(contact_row[5]), height=110)
                save_contact = st.form_submit_button("Save Outreach Contact", type="primary", use_container_width=True)
            if save_contact:
                now = datetime.now().isoformat(timespec="seconds")
                with sqlite3.connect(CONTACT_DB_PATH) as conn:
                    conn.execute(
                        """
                        INSERT INTO contacts(domain,admin_name,email,whatsapp,telegram,status,quoted_price,notes,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(domain) DO UPDATE SET admin_name=excluded.admin_name,email=excluded.email,
                        whatsapp=excluded.whatsapp,status=excluded.status,notes=excluded.notes,updated_at=excluded.updated_at
                        """,
                        (current_domain,e_name,e_email,e_whatsapp,"",e_status,clean_value(row["general_price"]),e_notes,now),
                    )
                    conn.commit()
                st.success("Outreach contact update ho gaya.")
                st.rerun()
# =========================================================
# DELETE
# =========================================================
elif page == "Delete Site":
    if require_admin():
        st.header("Delete Site")
        selected_id, row = site_selector(df)

        if row is not None:
            st.warning(f"Selected website: **{row['site']}**")
            confirm = st.checkbox("⚠️ Main permanent delete confirm karta hoon.")
            if st.button(
                "🗑️ Permanently Delete",
                type="primary",
                use_container_width=True,
                disabled=not confirm,
            ):
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("DELETE FROM sites WHERE id=?", (selected_id,))
                    conn.commit()
                refresh_sites()
                st.success("✅ Website delete ho gayi.")
                st.rerun()


# =========================================================
# FAVORITES
# =========================================================
elif page == "Favorites":
    st.header("Favorites")

    selected_id, row = site_selector(df, "Favorite/Unfavorite ke liye website select karein")
    if row is not None:
        current = bool(row["favorite"])
        button_text = "☆ Remove Favorite" if current else "⭐ Add to Favorites"
        if st.button(button_text, use_container_width=True):
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "UPDATE sites SET favorite=? WHERE id=?",
                    (0 if current else 1, selected_id),
                )
                conn.commit()
            refresh_sites()
            st.rerun()

    favorites = df[df["favorite"] == 1].copy() if not df.empty else df
    favorites = favorites[[c for c in favorites.columns if not c.startswith("_")]]
    st.info(f"⭐ {len(favorites):,} favorite websites")
    st.dataframe(favorites, use_container_width=True, hide_index=True, height=580)


# =========================================================
# PRIVATE CONTACTS
# =========================================================
elif page == "Private Contacts":
    if require_admin():
        st.header("Private Contacts")
        selected_id, row = site_selector(df)

        if row is not None:
            domain = normalize_domain(row["site"])
            with sqlite3.connect(CONTACT_DB_PATH) as conn:
                existing = conn.execute(
                    """
                    SELECT admin_name,email,whatsapp,telegram,status,
                           quoted_price,notes
                    FROM contacts WHERE domain=?
                    """,
                    (domain,),
                ).fetchone()

            existing = existing or ("", "", "", "", "", "", "")

            with st.form("contact_form"):
                admin_name = st.text_input("👤 Admin Name", value=existing[0] or "")
                email = st.text_input("✉️ Email", value=existing[1] or "")
                whatsapp = st.text_input("📱 WhatsApp", value=existing[2] or "")
                telegram = st.text_input("💬 Telegram", value=existing[3] or "")
                status = st.selectbox(
                    "📌 Status",
                    ["Not Contacted", "Contacted", "Follow-up", "Negotiating", "Deal Done", "Rejected"],
                    index=(
                        ["Not Contacted", "Contacted", "Follow-up", "Negotiating", "Deal Done", "Rejected"].index(existing[4])
                        if existing[4] in ["Not Contacted", "Contacted", "Follow-up", "Negotiating", "Deal Done", "Rejected"]
                        else 0
                    ),
                )
                quoted_price = st.text_input("💰 Quoted Price", value=existing[5] or "")
                notes = st.text_area("📝 Notes", value=existing[6] or "", height=150)
                save_contact = st.form_submit_button("💾 Save Contact", type="primary", use_container_width=True)

            if save_contact:
                with sqlite3.connect(CONTACT_DB_PATH) as conn:
                    conn.execute(
                        """
                        INSERT INTO contacts(
                            domain,admin_name,email,whatsapp,telegram,status,
                            quoted_price,notes,updated_at
                        ) VALUES(?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(domain) DO UPDATE SET
                            admin_name=excluded.admin_name,
                            email=excluded.email,
                            whatsapp=excluded.whatsapp,
                            telegram=excluded.telegram,
                            status=excluded.status,
                            quoted_price=excluded.quoted_price,
                            notes=excluded.notes,
                            updated_at=excluded.updated_at
                        """,
                        (
                            domain,admin_name,email,whatsapp,telegram,status,
                            quoted_price,notes,
                            datetime.now().isoformat(timespec="seconds"),
                        ),
                    )
                    conn.commit()
                st.success("✅ Private contact save ho gaya.")

        contacts_df = load_contacts()
        st.markdown("### 📋 Saved Contacts")
        st.dataframe(contacts_df, use_container_width=True, hide_index=True, height=400)


# =========================================================
# ADMIN CONTACT VAULT
# =========================================================
elif page == "Admin Contact Vault":
    st.header("Admin Contact Vault")
    st.caption(
        "Saved Author/Admin contacts ke liye Outreach Generator page se "
        "email, LinkedIn aur WhatsApp messages generate kar sakte hain."
    )
    st.caption(
        "Owner, Author, Admin, Manager aur internal team contacts ko private rakhein."
    )

    if require_admin():
        st.info(
            "🔒 Private area — ye contacts public Contact Us page, dashboard "
            "ya normal visitors ko show nahi hote."
        )

        vault_df = load_admin_private_contacts()

        st.markdown("### Add Private Contact")

        with st.form("admin_private_contact_form"):
            c1, c2 = st.columns(2)

            with c1:
                contact_type = st.selectbox(
                    "Contact Type",
                    [
                        "Owner",
                        "Author",
                        "Admin",
                        "Manager",
                        "Co-Owner",
                        "Team Member",
                        "Other",
                    ],
                )
                full_name = st.text_input(
                    "Full Name*",
                    placeholder="Aaquib Hussain",
                )
                company = st.text_input(
                    "Company / Brand",
                    placeholder="Aaquib Digital Solutions",
                )
                job_title = st.text_input(
                    "Role / Designation",
                    placeholder="Founder / SEO Specialist",
                )
                email = st.text_input("Private Email")
                phone = st.text_input("Private Phone")

            with c2:
                whatsapp = st.text_input("WhatsApp")
                website = st.text_input("Website")
                linkedin = st.text_input("LinkedIn")
                address = st.text_area(
                    "Address / Location",
                    height=80,
                )
                notes = st.text_area(
                    "Private Notes",
                    height=115,
                    placeholder="Internal notes, payment details, preferred contact time...",
                )

            save_contact = st.form_submit_button(
                "Save Private Contact",
                type="primary",
                use_container_width=True,
            )

        if save_contact:
            if not full_name.strip():
                st.error("Full Name required hai.")
            else:
                save_admin_private_contact(
                    None,
                    contact_type,
                    full_name.strip(),
                    company.strip(),
                    job_title.strip(),
                    email.strip(),
                    phone.strip(),
                    whatsapp.strip(),
                    website.strip(),
                    linkedin.strip(),
                    address.strip(),
                    notes.strip(),
                )
                st.success("Private contact save ho gaya.")
                st.rerun()

        st.markdown("### Saved Private Contacts")
        vault_df = load_admin_private_contacts()

        if vault_df.empty:
            st.info("Abhi koi private admin/author contact save nahi hai.")
        else:
            show_cols = [
                "id", "contact_type", "full_name", "company",
                "job_title", "email", "phone", "whatsapp",
                "website", "linkedin", "address", "notes", "updated_at"
            ]
            st.dataframe(
                vault_df[[c for c in show_cols if c in vault_df.columns]],
                use_container_width=True,
                hide_index=True,
                height=390,
            )

            st.markdown("### Edit / Delete")

            options = {
                f"#{int(row['id'])} — {row['full_name']} ({row['contact_type']})": row
                for _, row in vault_df.iterrows()
            }
            selected_label = st.selectbox(
                "Select Contact",
                list(options.keys()),
                key="vault_selected_contact",
            )
            selected = options[selected_label]

            contact_types = [
                "Owner", "Author", "Admin", "Manager",
                "Co-Owner", "Team Member", "Other"
            ]
            current_type = str(selected.get("contact_type", "Other"))
            current_index = (
                contact_types.index(current_type)
                if current_type in contact_types
                else len(contact_types) - 1
            )

            with st.form("edit_admin_private_contact_form"):
                e1, e2 = st.columns(2)

                with e1:
                    edit_type = st.selectbox(
                        "Contact Type",
                        contact_types,
                        index=current_index,
                        key="vault_edit_type",
                    )
                    edit_name = st.text_input(
                        "Full Name*",
                        value=str(selected.get("full_name", "") or ""),
                    )
                    edit_company = st.text_input(
                        "Company / Brand",
                        value=str(selected.get("company", "") or ""),
                    )
                    edit_job = st.text_input(
                        "Role / Designation",
                        value=str(selected.get("job_title", "") or ""),
                    )
                    edit_email = st.text_input(
                        "Private Email",
                        value=str(selected.get("email", "") or ""),
                    )
                    edit_phone = st.text_input(
                        "Private Phone",
                        value=str(selected.get("phone", "") or ""),
                    )

                with e2:
                    edit_whatsapp = st.text_input(
                        "WhatsApp",
                        value=str(selected.get("whatsapp", "") or ""),
                    )
                    edit_website = st.text_input(
                        "Website",
                        value=str(selected.get("website", "") or ""),
                    )
                    edit_linkedin = st.text_input(
                        "LinkedIn",
                        value=str(selected.get("linkedin", "") or ""),
                    )
                    edit_address = st.text_area(
                        "Address / Location",
                        value=str(selected.get("address", "") or ""),
                        height=80,
                    )
                    edit_notes = st.text_area(
                        "Private Notes",
                        value=str(selected.get("notes", "") or ""),
                        height=115,
                    )

                update_contact = st.form_submit_button(
                    "Update Private Contact",
                    type="primary",
                    use_container_width=True,
                )

            if update_contact:
                if not edit_name.strip():
                    st.error("Full Name required hai.")
                else:
                    save_admin_private_contact(
                        int(selected["id"]),
                        edit_type,
                        edit_name.strip(),
                        edit_company.strip(),
                        edit_job.strip(),
                        edit_email.strip(),
                        edit_phone.strip(),
                        edit_whatsapp.strip(),
                        edit_website.strip(),
                        edit_linkedin.strip(),
                        edit_address.strip(),
                        edit_notes.strip(),
                    )
                    st.success("Private contact update ho gaya.")
                    st.rerun()

            delete_ok = st.checkbox(
                "I confirm selected private contact should be deleted.",
                key="vault_delete_ok",
            )

            if st.button(
                "Delete Selected Private Contact",
                disabled=not delete_ok,
                use_container_width=True,
            ):
                delete_admin_private_contact(int(selected["id"]))
                st.success("Private contact delete ho gaya.")
                st.rerun()

            st.download_button(
                "Download Private Contacts CSV",
                vault_df.to_csv(index=False).encode("utf-8-sig"),
                "gp_site_finder_admin_private_contacts.csv",
                "text/csv",
                use_container_width=True,
            )


# =========================================================
# OUTREACH PIPELINE
# =========================================================
elif page == "Outreach Pipeline":
    st.header("Outreach Pipeline")
    st.caption(
        "Guest-post opportunities ko New se Published tak track karein."
    )

    pipeline_df = load_outreach_pipeline()

    p1, p2, p3, p4, p5 = st.columns(5)
    statuses = [
        "New",
        "Contacted",
        "Negotiating",
        "Published",
        "Rejected",
    ]
    counts = {
        status: int(
            (pipeline_df["status"] == status).sum()
        ) if not pipeline_df.empty else 0
        for status in statuses
    }

    p1.metric("New", counts["New"])
    p2.metric("Contacted", counts["Contacted"])
    p3.metric("Negotiating", counts["Negotiating"])
    p4.metric("Published", counts["Published"])
    p5.metric("Rejected", counts["Rejected"])

    st.markdown("### Add / Update Outreach Record")

    site_options = {
        f"{row['site']} | ID {int(row['id'])}": row
        for _, row in df.head(10000).iterrows()
    }

    if site_options:
        selected_site_label = st.selectbox(
            "Website",
            list(site_options.keys()),
            key="pipeline_site",
        )
        selected_site_row = site_options[selected_site_label]
        selected_site = str(selected_site_row["site"])
        selected_site_id = int(selected_site_row["id"])

        existing = pipeline_df[
            pipeline_df["site"] == selected_site
        ]

        existing_row = (
            existing.iloc[0]
            if not existing.empty
            else None
        )

        status_default = (
            str(existing_row["status"])
            if existing_row is not None
            else "New"
        )
        status_index = (
            statuses.index(status_default)
            if status_default in statuses
            else 0
        )

        with st.form("outreach_form"):
            c1, c2 = st.columns(2)

            with c1:
                outreach_status = st.selectbox(
                    "Status",
                    statuses,
                    index=status_index,
                )
                contact_name = st.text_input(
                    "Contact Name",
                    value=(
                        str(existing_row["contact_name"] or "")
                        if existing_row is not None else ""
                    ),
                )
                contact_email = st.text_input(
                    "Contact Email",
                    value=(
                        str(existing_row["contact_email"] or "")
                        if existing_row is not None else ""
                    ),
                )

            with c2:
                whatsapp = st.text_input(
                    "WhatsApp",
                    value=(
                        str(existing_row["whatsapp"] or "")
                        if existing_row is not None else ""
                    ),
                )
                last_contacted = st.text_input(
                    "Last Contacted",
                    value=(
                        str(existing_row["last_contacted"] or "")
                        if existing_row is not None else ""
                    ),
                    placeholder="2026-08-08",
                )
                next_follow_up = st.text_input(
                    "Next Follow-up",
                    value=(
                        str(existing_row["next_follow_up"] or "")
                        if existing_row is not None else ""
                    ),
                    placeholder="2026-08-10",
                )

            outreach_notes = st.text_area(
                "Notes",
                value=(
                    str(existing_row["notes"] or "")
                    if existing_row is not None else ""
                ),
                height=100,
            )

            save_outreach = st.form_submit_button(
                "Save Outreach Record",
                type="primary",
                use_container_width=True,
            )

        if save_outreach:
            upsert_outreach_record(
                selected_site_id,
                selected_site,
                outreach_status,
                contact_name.strip(),
                contact_email.strip(),
                whatsapp.strip(),
                last_contacted.strip(),
                next_follow_up.strip(),
                outreach_notes.strip(),
            )
            st.success("Outreach record save ho gaya.")
            st.rerun()

    st.markdown("### Pipeline Records")

    if pipeline_df.empty:
        st.info("Abhi outreach pipeline empty hai.")
    else:
        status_filter = st.selectbox(
            "Filter Status",
            ["All"] + statuses,
            key="pipeline_filter",
        )

        visible_pipeline = pipeline_df.copy()

        if status_filter != "All":
            visible_pipeline = visible_pipeline[
                visible_pipeline["status"] == status_filter
            ]

        st.dataframe(
            visible_pipeline[
                [
                    c for c in [
                        "site",
                        "status",
                        "contact_name",
                        "contact_email",
                        "whatsapp",
                        "last_contacted",
                        "next_follow_up",
                        "notes",
                        "updated_at",
                    ]
                    if c in visible_pipeline.columns
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=500,
        )

        csv_pipeline = visible_pipeline.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "Download Pipeline CSV",
            csv_pipeline,
            "gp_site_finder_outreach_pipeline.csv",
            "text/csv",
            use_container_width=True,
        )


# =========================================================
# STATISTICS
# =========================================================
elif page == "Statistics":
    st.header("Statistics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌐 Total Sites", f"{len(df):,}")
    c2.metric("🌍 Countries", f"{df['country'].fillna('').replace('', pd.NA).dropna().nunique():,}")
    c3.metric("📄 Sheets", f"{df['sheet_name'].fillna('').replace('', pd.NA).dropna().nunique():,}")
    c4.metric("Favorites", f"{int((df['favorite'] == 1).sum()):,}")

    st.markdown("### 🌍 Top Countries")
    country_chart = df["country"].fillna("Unknown").replace("", "Unknown").value_counts().head(15)
    st.bar_chart(country_chart)

    st.markdown("### 💳 Payment Methods")
    payment_chart = df["payment_method"].fillna("Unknown").replace("", "Unknown").value_counts().head(10)
    st.bar_chart(payment_chart)


# =========================================================
# DUPLICATE FINDER
# =========================================================
elif page == "Duplicate Finder":
    st.header("Duplicate Finder")
    st.caption(
        "Same domain ke duplicate records detect karein aur ek record rakh kar baqi remove karein."
    )

    working_df = df.copy()
    working_df["_domain_key"] = (
        working_df["site"]
        .fillna("")
        .astype(str)
        .map(normalize_domain)
    )

    duplicate_counts = (
        working_df[working_df["_domain_key"] != ""]
        .groupby("_domain_key")
        .size()
        .sort_values(ascending=False)
    )

    duplicate_domains = duplicate_counts[
        duplicate_counts > 1
    ]

    duplicate_rows = working_df[
        working_df["_domain_key"].isin(
            duplicate_domains.index
        )
    ].copy()

    d1, d2 = st.columns(2)
    d1.metric(
        "🔁 Duplicate Domains",
        f"{len(duplicate_domains):,}",
    )
    d2.metric(
        "📋 Duplicate Rows",
        f"{len(duplicate_rows):,}",
    )

    if duplicate_rows.empty:
        st.success("✅ Koi duplicate domain nahi mila.")
    else:
        display_columns = [
            column
            for column in [
                "_domain_key",
                "id",
                "site",
                "country",
                "dr",
                "traffic",
                "general_price",
                "source_file",
                "sheet_name",
                "created_at",
            ]
            if column in duplicate_rows.columns
        ]

        st.dataframe(
            duplicate_rows[
                display_columns
            ].sort_values(
                ["_domain_key", "id"]
            ),
            use_container_width=True,
            hide_index=True,
            height=560,
        )

        selected_duplicate_domain = st.selectbox(
            "Duplicate domain select karein",
            duplicate_domains.index.tolist(),
        )

        selected_duplicates = duplicate_rows[
            duplicate_rows["_domain_key"]
            == selected_duplicate_domain
        ].sort_values("id")

        st.markdown("### Selected Domain Records")
        st.dataframe(
            selected_duplicates[display_columns],
            use_container_width=True,
            hide_index=True,
        )

        if not st.session_state.admin_logged_in:
            st.warning(
                "Duplicates remove karne ke liye Admin Login karein."
            )
        else:
            keep_choice = st.radio(
                "Kaunsa record rakhein?",
                [
                    "Oldest record (lowest ID)",
                    "Newest record (highest ID)",
                ],
                horizontal=True,
            )

            confirm_duplicates = st.checkbox(
                "⚠️ Selected domain ke extra duplicate records remove karna confirm karta hoon."
            )

            if st.button(
                "🧹 Keep One and Remove Extras",
                type="primary",
                use_container_width=True,
                disabled=not confirm_duplicates,
            ):
                ids = selected_duplicates[
                    "id"
                ].astype(int).tolist()

                keep_id = (
                    min(ids)
                    if keep_choice.startswith("Oldest")
                    else max(ids)
                )

                delete_ids = [
                    record_id
                    for record_id in ids
                    if record_id != keep_id
                ]

                with sqlite3.connect(DB_PATH) as conn:
                    conn.executemany(
                        "DELETE FROM sites WHERE id=?",
                        [(record_id,) for record_id in delete_ids],
                    )
                    conn.commit()

                refresh_sites()
                st.success(
                    f"✅ ID {keep_id} rakha gaya aur "
                    f"{len(delete_ids)} duplicate record(s) remove ho gaye."
                )
                st.rerun()


# =========================================================
# EXPORT
# =========================================================
elif page == "Export Results":
    st.header("Export Results")

    export_df = df[[c for c in df.columns if not c.startswith("_")]].copy()
    csv_bytes = export_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Download All Sites as CSV",
        csv_bytes,
        "gp_site_finder_all_sites.csv",
        "text/csv",
        use_container_width=True,
    )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Sites")
    st.download_button(
        "📗 Download All Sites as Excel",
        excel_buffer.getvalue(),
        "gp_site_finder_all_sites.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


# =========================================================
# OUR TEAM
# =========================================================
elif page == "Our Team":
    st.markdown(
        """
        <div class="team-intro">
            <h2>Meet Our Team</h2>
            <p>
                Leadership, management and specialist profiles of
                Aaquib Digital Solutions. CEO, managers, team leads
                and staff members can be added and updated from this page.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    team_df = load_team_members(active_only=True)

    if team_df.empty:
        st.info(
            "Abhi koi team profile add nahi hui. Admin Login ke baad neeche se pehla member add karein."
        )
    else:
        level_order = [
            "CEO / Founder",
            "Director",
            "Manager",
            "Team Lead",
            "Team Member",
            "Intern",
        ]

        for level in level_order:
            level_df = team_df[team_df["level"] == level]

            if level_df.empty:
                continue

            st.markdown(f"### {level}")

            columns_per_row = 3
            rows = [
                level_df.iloc[index:index + columns_per_row]
                for index in range(0, len(level_df), columns_per_row)
            ]

            for row_df in rows:
                card_columns = st.columns(columns_per_row)

                for card_column, (_, member) in zip(
                    card_columns,
                    row_df.iterrows(),
                ):
                    with card_column:
                        image_value = str(
                            member.get("image_path", "") or ""
                        ).strip()

                        if image_value:
                            member_image = BASE_DIR / image_value
                            if member_image.exists():
                                st.image(
                                    str(member_image),
                                    use_container_width=True,
                                )

                        reports_to = str(
                            member.get("reports_to", "") or ""
                        ).strip()

                        contact_lines = []

                        if str(member.get("email", "") or "").strip():
                            contact_lines.append(
                                f"Email: {member['email']}"
                            )

                        if str(member.get("phone", "") or "").strip():
                            contact_lines.append(
                                f"Phone: {member['phone']}"
                            )

                        if str(member.get("location", "") or "").strip():
                            contact_lines.append(
                                f"Location: {member['location']}"
                            )

                        if reports_to:
                            contact_lines.append(
                                f"Reports to: {reports_to}"
                            )

                        meta_html = "<br>".join(contact_lines)
                        bio_html = str(
                            member.get("bio", "") or ""
                        ).strip()

                        st.markdown(
                            f"""
                            <div class="team-card">
                                <span class="team-level-badge">
                                    {member['level']}
                                </span>
                                <div class="team-card-name">
                                    {member['full_name']}
                                </div>
                                <div class="team-card-role">
                                    {member['designation']}
                                </div>
                                <div class="team-card-meta">
                                    {meta_html}
                                </div>
                                <div class="team-card-bio">
                                    {bio_html}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        button_columns = st.columns(2)

                        linkedin_value = str(
                            member.get("linkedin", "") or ""
                        ).strip()

                        website_value = str(
                            member.get("website", "") or ""
                        ).strip()

                        with button_columns[0]:
                            if linkedin_value:
                                st.link_button(
                                    "LinkedIn",
                                    normalize_public_url(
                                        linkedin_value
                                    ),
                                    use_container_width=True,
                                )

                        with button_columns[1]:
                            if website_value:
                                st.link_button(
                                    "Website",
                                    normalize_public_url(
                                        website_value
                                    ),
                                    use_container_width=True,
                                )

    st.divider()

    if require_admin():
        st.markdown("## Team Management")

        management_tab, edit_tab = st.tabs(
            ["Add Team Member", "Edit / Delete Member"]
        )

        with management_tab:
            with st.form("add_team_member_form"):
                c1, c2 = st.columns(2)

                with c1:
                    full_name = st.text_input(
                        "Full Name*",
                        placeholder="Team member name",
                    )
                    designation = st.text_input(
                        "Designation*",
                        placeholder="SEO Manager",
                    )
                    level = st.selectbox(
                        "Team Level*",
                        [
                            "CEO / Founder",
                            "Director",
                            "Manager",
                            "Team Lead",
                            "Team Member",
                            "Intern",
                        ],
                    )
                    reports_to = st.text_input(
                        "Reports To",
                        placeholder="CEO or Manager name",
                    )
                    email = st.text_input("Email")
                    phone = st.text_input("Phone / WhatsApp")

                with c2:
                    linkedin = st.text_input("LinkedIn URL")
                    website = st.text_input("Website URL")
                    location = st.text_input("Location")
                    skills = st.text_input(
                        "Skills",
                        placeholder="SEO, Outreach, Content",
                    )
                    display_order = st.number_input(
                        "Display Order",
                        min_value=1,
                        value=100,
                        step=1,
                    )
                    active = st.checkbox(
                        "Show profile publicly",
                        value=True,
                    )

                bio = st.text_area(
                    "Short Bio",
                    height=130,
                )

                submitted_team = st.form_submit_button(
                    "Save Team Member",
                    type="primary",
                    use_container_width=True,
                )

            team_picture = st.file_uploader(
                "Upload Team Member Picture",
                type=["png", "jpg", "jpeg", "webp"],
                key="new_team_picture",
            )

            if submitted_team:
                if not full_name.strip():
                    st.error("Full Name zaroor likhein.")
                elif not designation.strip():
                    st.error("Designation zaroor likhein.")
                else:
                    now = datetime.now().isoformat(
                        timespec="seconds"
                    )

                    with sqlite3.connect(TEAM_DB_PATH) as conn:
                        cursor = conn.execute(
                            """
                            INSERT INTO team_members(
                                full_name,designation,level,reports_to,
                                email,phone,linkedin,website,location,
                                bio,skills,image_path,display_order,
                                active,created_at,updated_at
                            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                            """,
                            (
                                full_name.strip(),
                                designation.strip(),
                                level,
                                reports_to.strip(),
                                email.strip(),
                                phone.strip(),
                                linkedin.strip(),
                                website.strip(),
                                location.strip(),
                                bio.strip(),
                                skills.strip(),
                                "",
                                int(display_order),
                                1 if active else 0,
                                now,
                                now,
                            ),
                        )
                        member_id = int(cursor.lastrowid)
                        conn.commit()

                    if team_picture is not None:
                        image_path = save_team_image(
                            team_picture,
                            member_id,
                        )

                        with sqlite3.connect(TEAM_DB_PATH) as conn:
                            conn.execute(
                                """
                                UPDATE team_members
                                SET image_path=?, updated_at=?
                                WHERE id=?
                                """,
                                (
                                    image_path,
                                    now,
                                    member_id,
                                ),
                            )
                            conn.commit()

                    st.success(
                        "Team member profile successfully add ho gayi."
                    )
                    st.rerun()

        with edit_tab:
            all_team_df = load_team_members(
                active_only=False
            )

            if all_team_df.empty:
                st.info("Edit karne ke liye koi member nahi hai.")
            else:
                team_options = {
                    (
                        f"{row['full_name']} — "
                        f"{row['designation']} | ID {int(row['id'])}"
                    ): int(row["id"])
                    for _, row in all_team_df.iterrows()
                }

                selected_label = st.selectbox(
                    "Team Member Select Karein",
                    list(team_options.keys()),
                )

                selected_member_id = team_options[
                    selected_label
                ]

                selected_member = all_team_df[
                    all_team_df["id"]
                    == selected_member_id
                ].iloc[0]

                levels = [
                    "CEO / Founder",
                    "Director",
                    "Manager",
                    "Team Lead",
                    "Team Member",
                    "Intern",
                ]

                current_level = (
                    selected_member["level"]
                    if selected_member["level"] in levels
                    else "Team Member"
                )

                with st.form("edit_team_member_form"):
                    e1, e2 = st.columns(2)

                    with e1:
                        edit_name = st.text_input(
                            "Full Name",
                            value=str(
                                selected_member["full_name"]
                                or ""
                            ),
                        )
                        edit_designation = st.text_input(
                            "Designation",
                            value=str(
                                selected_member["designation"]
                                or ""
                            ),
                        )
                        edit_level = st.selectbox(
                            "Team Level",
                            levels,
                            index=levels.index(current_level),
                        )
                        edit_reports_to = st.text_input(
                            "Reports To",
                            value=str(
                                selected_member["reports_to"]
                                or ""
                            ),
                        )
                        edit_email = st.text_input(
                            "Email",
                            value=str(
                                selected_member["email"]
                                or ""
                            ),
                        )
                        edit_phone = st.text_input(
                            "Phone / WhatsApp",
                            value=str(
                                selected_member["phone"]
                                or ""
                            ),
                        )

                    with e2:
                        edit_linkedin = st.text_input(
                            "LinkedIn URL",
                            value=str(
                                selected_member["linkedin"]
                                or ""
                            ),
                        )
                        edit_website = st.text_input(
                            "Website URL",
                            value=str(
                                selected_member["website"]
                                or ""
                            ),
                        )
                        edit_location = st.text_input(
                            "Location",
                            value=str(
                                selected_member["location"]
                                or ""
                            ),
                        )
                        edit_skills = st.text_input(
                            "Skills",
                            value=str(
                                selected_member["skills"]
                                or ""
                            ),
                        )
                        edit_order = st.number_input(
                            "Display Order",
                            min_value=1,
                            value=int(
                                selected_member[
                                    "display_order"
                                ]
                                or 100
                            ),
                            step=1,
                        )
                        edit_active = st.checkbox(
                            "Show profile publicly",
                            value=bool(
                                selected_member["active"]
                            ),
                        )

                    edit_bio = st.text_area(
                        "Short Bio",
                        value=str(
                            selected_member["bio"] or ""
                        ),
                        height=130,
                    )

                    save_edit = st.form_submit_button(
                        "Save Team Profile Changes",
                        type="primary",
                        use_container_width=True,
                    )

                replacement_picture = st.file_uploader(
                    "Replace Profile Picture",
                    type=["png", "jpg", "jpeg", "webp"],
                    key=f"replace_team_picture_{selected_member_id}",
                )

                if save_edit:
                    now = datetime.now().isoformat(
                        timespec="seconds"
                    )

                    with sqlite3.connect(TEAM_DB_PATH) as conn:
                        conn.execute(
                            """
                            UPDATE team_members
                            SET full_name=?,designation=?,level=?,
                                reports_to=?,email=?,phone=?,
                                linkedin=?,website=?,location=?,
                                bio=?,skills=?,display_order=?,
                                active=?,updated_at=?
                            WHERE id=?
                            """,
                            (
                                edit_name.strip(),
                                edit_designation.strip(),
                                edit_level,
                                edit_reports_to.strip(),
                                edit_email.strip(),
                                edit_phone.strip(),
                                edit_linkedin.strip(),
                                edit_website.strip(),
                                edit_location.strip(),
                                edit_bio.strip(),
                                edit_skills.strip(),
                                int(edit_order),
                                1 if edit_active else 0,
                                now,
                                selected_member_id,
                            ),
                        )
                        conn.commit()

                    if replacement_picture is not None:
                        new_image_path = save_team_image(
                            replacement_picture,
                            selected_member_id,
                        )

                        with sqlite3.connect(TEAM_DB_PATH) as conn:
                            conn.execute(
                                """
                                UPDATE team_members
                                SET image_path=?, updated_at=?
                                WHERE id=?
                                """,
                                (
                                    new_image_path,
                                    now,
                                    selected_member_id,
                                ),
                            )
                            conn.commit()

                    st.success("Team profile update ho gayi.")
                    st.rerun()

                st.markdown("### Delete Team Member")
                confirm_team_delete = st.checkbox(
                    "Permanent delete confirm",
                    key="confirm_team_delete",
                )

                if st.button(
                    "Delete Selected Team Member",
                    type="primary",
                    use_container_width=True,
                    disabled=not confirm_team_delete,
                ):
                    remove_team_image(
                        str(
                            selected_member["image_path"]
                            or ""
                        )
                    )

                    with sqlite3.connect(TEAM_DB_PATH) as conn:
                        conn.execute(
                            """
                            DELETE FROM team_members
                            WHERE id=?
                            """,
                            (selected_member_id,),
                        )
                        conn.commit()

                    st.success("Team member delete ho gaya.")
                    st.rerun()


# =========================================================
# CONTACT US
# =========================================================
elif page == "Contact Us":
    st.header("Contact Us")
    st.caption(
        "Clients aur visitors yahan apni inquiry, contact details aur project requirements submit kar sakte hain."
    )

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown("### Send a Message")

        with st.form("public_contact_form", clear_on_submit=True):
            c1, c2 = st.columns(2)

            with c1:
                full_name = st.text_input(
                    "Full Name*",
                    placeholder="Your full name",
                )
                email = st.text_input(
                    "Email",
                    placeholder="name@example.com",
                )
                phone = st.text_input(
                    "Phone / WhatsApp",
                    placeholder="+92 300 1234567",
                )

            with c2:
                company = st.text_input(
                    "Company / Brand",
                    placeholder="Company name",
                )
                website = st.text_input(
                    "Website",
                    placeholder="https://example.com",
                )
                subject = st.selectbox(
                    "Subject",
                    [
                        "Guest Posting",
                        "Link Building",
                        "SEO Services",
                        "Website Collaboration",
                        "Technical Support",
                        "Other",
                    ],
                )

            message = st.text_area(
                "Message / Project Details*",
                placeholder="Apni requirement, budget, niche ya project details likhein...",
                height=180,
            )

            consent = st.checkbox(
                "I agree that Aaquib Digital Solutions may contact me about this inquiry."
            )

            submitted = st.form_submit_button(
                "Send Message",
                type="primary",
                use_container_width=True,
                disabled=not consent,
            )

        if submitted:
            if not full_name.strip():
                st.error("Full Name zaroor likhein.")
            elif not message.strip():
                st.error("Message / Project Details zaroor likhein.")
            elif email.strip() and "@" not in email:
                st.error("Valid email address likhein.")
            else:
                with sqlite3.connect(CONTACT_US_DB_PATH) as conn:
                    conn.execute(
                        """
                        INSERT INTO contact_messages(
                            full_name,email,phone,company,website,
                            subject,message,status,created_at
                        ) VALUES(?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            full_name.strip(),
                            email.strip(),
                            phone.strip(),
                            company.strip(),
                            website.strip(),
                            subject,
                            message.strip(),
                            "New",
                            datetime.now().isoformat(timespec="seconds"),
                        ),
                    )
                    conn.commit()

                st.success(
                    "Message successfully send ho gaya. Inquiry Admin Contact Inbox me permanently save ho gayi."
                )

    with right:
        st.markdown("### Contact Information")

        if PROFILE_IMAGE_PATH.exists():
            st.image(
                str(PROFILE_IMAGE_PATH),
                width=150,
            )

        st.markdown(
            f"### {profile_settings.get('brand_name', 'Aaquib Digital Solutions')}"
        )
        st.caption(profile_settings.get("role", ""))

        contact_html = '<div class="contact-card">'

        if profile_settings.get("phone"):
            contact_html += (
                '<div class="contact-detail">'
                f'WhatsApp: {profile_settings["phone"]}'
                '</div>'
            )

        if profile_settings.get("email"):
            contact_html += (
                '<div class="contact-detail">'
                f'Email: {profile_settings["email"]}'
                '</div>'
            )

        if profile_settings.get("website"):
            contact_html += (
                '<div class="contact-detail">'
                f'Website: {profile_settings["website"]}'
                '</div>'
            )

        if profile_settings.get("location"):
            contact_html += (
                '<div class="contact-detail">'
                f'Location: {profile_settings["location"]}'
                '</div>'
            )

        contact_html += '</div>'

        st.markdown(
            contact_html,
            unsafe_allow_html=True,
        )

        if profile_settings.get("phone"):
            direct_whatsapp = whatsapp_url(
                profile_settings["phone"],
                (
                    "Hello Aaquib Digital Solutions, "
                    "I want to discuss guest posting / SEO services."
                ),
            )

            st.markdown(
                f"""
                <a class="whatsapp-button"
                   href="{direct_whatsapp}"
                   target="_blank">
                    Chat Directly on WhatsApp
                </a>
                """,
                unsafe_allow_html=True,
            )

        if profile_settings.get("email"):
            st.link_button(
                "Email",
                f"mailto:{profile_settings['email']}",
                use_container_width=True,
            )

        if profile_settings.get("website"):
            st.link_button(
                "Visit Website",
                normalize_public_url(
                    profile_settings["website"]
                ),
                use_container_width=True,
            )

        if profile_settings.get("linkedin"):
            st.link_button(
                "LinkedIn Profile",
                normalize_public_url(
                    profile_settings["linkedin"]
                ),
                use_container_width=True,
            )

        if profile_settings.get("location"):
            st.info(
                f"Location: {profile_settings['location']}"
            )

        if profile_settings.get("about"):
            st.write(profile_settings["about"])

    st.divider()

    if st.session_state.admin_logged_in:
        st.markdown("### Contact Inbox")

        with sqlite3.connect(CONTACT_US_DB_PATH) as conn:
            inbox_df = pd.read_sql_query(
                """
                SELECT id,full_name,email,phone,company,website,
                       subject,message,status,created_at
                FROM contact_messages
                ORDER BY id DESC
                """,
                conn,
            )

        if inbox_df.empty:
            st.info("Abhi koi contact inquiry receive nahi hui.")
        else:
            i1, i2, i3 = st.columns(3)
            i1.metric("Total Messages", f"{len(inbox_df):,}")
            i2.metric(
                "New",
                f"{int((inbox_df['status'] == 'New').sum()):,}",
            )
            i3.metric(
                "Resolved",
                f"{int((inbox_df['status'] == 'Resolved').sum()):,}",
            )

            status_filter = st.selectbox(
                "Filter Inbox",
                ["All", "New", "In Progress", "Resolved"],
            )

            display_inbox = inbox_df.copy()
            if status_filter != "All":
                display_inbox = display_inbox[
                    display_inbox["status"] == status_filter
                ]

            st.dataframe(
                display_inbox,
                use_container_width=True,
                hide_index=True,
                height=480,
            )

            message_options = {
                (
                    f"ID {int(row['id'])} | "
                    f"{row['full_name']} | {row['subject']}"
                ): int(row["id"])
                for _, row in inbox_df.iterrows()
            }

            selected_message_label = st.selectbox(
                "Manage Message",
                list(message_options.keys()),
            )
            selected_message_id = message_options[
                selected_message_label
            ]

            selected_message = inbox_df[
                inbox_df["id"] == selected_message_id
            ].iloc[0]

            st.text_area(
                "Selected Message",
                value=str(selected_message["message"]),
                height=130,
                disabled=True,
            )

            m1, m2 = st.columns(2)

            with m1:
                new_status = st.selectbox(
                    "Update Status",
                    ["New", "In Progress", "Resolved"],
                    index=[
                        "New",
                        "In Progress",
                        "Resolved",
                    ].index(
                        selected_message["status"]
                        if selected_message["status"]
                        in ["New", "In Progress", "Resolved"]
                        else "New"
                    ),
                )

                if st.button(
                    "Update Message Status",
                    use_container_width=True,
                ):
                    with sqlite3.connect(
                        CONTACT_US_DB_PATH
                    ) as conn:
                        conn.execute(
                            """
                            UPDATE contact_messages
                            SET status=?
                            WHERE id=?
                            """,
                            (
                                new_status,
                                selected_message_id,
                            ),
                        )
                        conn.commit()

                    st.success("Message status update ho gaya.")
                    st.rerun()

            with m2:
                confirm_delete_message = st.checkbox(
                    "Delete message confirm"
                )

                if st.button(
                    "Delete Message",
                    type="primary",
                    use_container_width=True,
                    disabled=not confirm_delete_message,
                ):
                    with sqlite3.connect(
                        CONTACT_US_DB_PATH
                    ) as conn:
                        conn.execute(
                            """
                            DELETE FROM contact_messages
                            WHERE id=?
                            """,
                            (selected_message_id,),
                        )
                        conn.commit()

                    st.success("Contact message delete ho gaya.")
                    st.rerun()

            inbox_csv = inbox_df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "Download Contact Inbox CSV",
                data=inbox_csv,
                file_name="contact_inbox.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.caption(
            "Contact Inbox dekhne aur manage karne ke liye Admin Login karein."
        )


# =========================================================
# MY PROFILE / CONTACT
# =========================================================
elif page == "My Profile / Contact":
    st.header("My Profile & Contact")
    st.caption(
        "Admin Login ke baad yahan name, brand, WhatsApp, email, website, LinkedIn aur picture manually update karein."
    )

    left, right = st.columns([1, 2])

    with left:
        if PROFILE_IMAGE_PATH.exists():
            st.image(
                str(PROFILE_IMAGE_PATH),
                use_container_width=True,
            )
        else:
            st.info("Profile picture abhi add nahi ki gayi.")

    with right:
        st.markdown(
            f"### {profile_settings.get('brand_name', 'Aaquib Digital Solutions')}"
        )
        st.markdown(f"## {profile_settings['name']}")
        st.caption(profile_settings["role"])

        if profile_settings.get("about"):
            st.write(profile_settings["about"])

        contact_rows = []

        if profile_settings.get("phone"):
            contact_rows.append(
                f"📱 **Phone / WhatsApp:** "
                f"[{profile_settings['phone']}](https://wa.me/"
                f"{re.sub(r'[^0-9]', '', profile_settings['phone'])})"
            )

        if profile_settings.get("email"):
            contact_rows.append(
                f"✉️ **Email:** "
                f"[{profile_settings['email']}]"
                f"(mailto:{profile_settings['email']})"
            )

        if profile_settings.get("website"):
            contact_rows.append(
                f"🌐 **Website:** "
                f"[{profile_settings['website']}]"
                f"({normalize_public_url(profile_settings['website'])})"
            )

        if profile_settings.get("linkedin"):
            contact_rows.append(
                f"💼 **LinkedIn:** "
                f"[Open Profile]"
                f"({normalize_public_url(profile_settings['linkedin'])})"
            )

        if profile_settings.get("location"):
            contact_rows.append(
                f"📍 **Location:** {profile_settings['location']}"
            )

        if contact_rows:
            st.markdown("\n\n".join(contact_rows))
        else:
            st.info(
                "Contact information Settings se manually add karein."
            )

    st.divider()

    if require_admin():
        st.markdown("### ✏️ Edit Profile & Contact")

        with st.form("profile_settings_form"):
            brand_name = st.text_input(
                "Brand Name",
                value=profile_settings.get(
                    "brand_name",
                    "Aaquib Digital Solutions",
                ),
            )
            name = st.text_input(
                "Your Name",
                value=profile_settings["name"],
            )
            role = st.text_input(
                "Professional Title",
                value=profile_settings["role"],
            )
            phone = st.text_input(
                "Phone / WhatsApp Number",
                value=profile_settings["phone"],
                placeholder="+92 300 1234567",
            )
            email = st.text_input(
                "Email Address",
                value=profile_settings["email"],
                placeholder="name@example.com",
            )
            website = st.text_input(
                "Website URL",
                value=profile_settings["website"],
                placeholder="https://example.com",
            )
            linkedin = st.text_input(
                "LinkedIn URL",
                value=profile_settings["linkedin"],
            )
            location = st.text_input(
                "Location",
                value=profile_settings["location"],
                placeholder="Pakistan",
            )
            about = st.text_area(
                "About / Services",
                value=profile_settings["about"],
                height=130,
            )

            save_profile = st.form_submit_button(
                "💾 Save Profile Information",
                type="primary",
                use_container_width=True,
            )

        profile_picture = st.file_uploader(
            "🖼️ Upload / Replace Profile Picture",
            type=["png", "jpg", "jpeg", "webp"],
            key="profile_picture_upload",
        )

        if save_profile:
            new_profile = {
                "brand_name": (
                    brand_name.strip()
                    or "Aaquib Digital Solutions"
                ),
                "name": name.strip() or "Aaquib SEO",
                "role": role.strip(),
                "phone": phone.strip(),
                "email": email.strip(),
                "website": website.strip(),
                "linkedin": linkedin.strip(),
                "location": location.strip(),
                "about": about.strip(),
            }
            save_profile_settings(new_profile)
            st.success("✅ Profile information save ho gayi.")
            st.rerun()

        if profile_picture is not None:
            if st.button(
                "🖼️ Save New Profile Picture",
                type="primary",
                use_container_width=True,
            ):
                try:
                    save_profile_image(profile_picture)
                    st.success("✅ Profile picture update ho gayi.")
                    st.rerun()
                except Exception as error:
                    st.error(
                        f"Picture save nahi hui: "
                        f"{type(error).__name__}: {error}"
                    )


# =========================================================
# ADMIN LOGIN
# =========================================================
elif page == "Admin Login":
    st.header("Admin Login")

    if st.session_state.admin_logged_in:
        st.success("✅ Admin already logged in.")
        if st.button("🔒 Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()
    else:
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password")

        if st.button("🔓 Login", type="primary", use_container_width=True):
            auth = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
            password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

            if username == auth["username"] and password_hash == auth["password_hash"]:
                st.session_state.admin_logged_in = True
                st.success("✅ Login successful.")
                st.rerun()
            else:
                st.error("❌ Wrong username or password.")

    st.caption("Default login: admin / admin123")


# =========================================================
# BACKUP & RESTORE
# =========================================================
elif page == "Backup & Restore":
    st.header("Backup & Restore")
    st.caption(
        "Database, profile, contacts aur team images ka manual safety backup."
    )

    if require_admin():
        backup_bytes = make_database_backup_zip()
        backup_name = (
            "gp_site_finder_backup_"
            + datetime.now().strftime("%Y%m%d_%H%M")
            + ".zip"
        )

        st.download_button(
            "Download Full Backup ZIP",
            backup_bytes,
            backup_name,
            "application/zip",
            use_container_width=True,
            type="primary",
        )

        st.info(
            "Recommended: important changes ke baad backup ZIP download karke "
            "Google Drive / PC me save karein."
        )

        st.divider()
        st.markdown("### Restore Backup")

        restore_zip = st.file_uploader(
            "Select GP Site Finder backup ZIP",
            type=["zip"],
            key="restore_backup_zip",
        )

        confirm_restore = st.checkbox(
            "I understand existing database/assets files may be replaced.",
            key="confirm_restore",
        )

        if st.button(
            "Restore Selected Backup",
            disabled=(
                restore_zip is None
                or not confirm_restore
            ),
            use_container_width=True,
        ):
            ok, message = restore_database_backup(
                restore_zip
            )

            if ok:
                st.success(message)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(message)


# =========================================================
# SETTINGS
# =========================================================
elif page == "Settings":
    st.header("Settings")
    st.caption("Profile, WhatsApp, email, website aur LinkedIn yahan manage karein.")
    st.write(f"Database path: `{DB_PATH}`")
    st.write(f"Private contacts DB: `{CONTACT_DB_PATH}`")
    st.write(f"Contact Us inbox DB: `{CONTACT_US_DB_PATH}`")
    st.write(f"Team profiles DB: `{TEAM_DB_PATH}`")
    st.write(f"Outreach pipeline DB: `{OUTREACH_DB_PATH}`")
    st.write(f"Admin private contacts DB: `{ADMIN_CONTACTS_DB_PATH}`")
    st.write(f"Total records: `{len(df):,}`")
    st.write(f"Profile settings: `{PROFILE_DATA_PATH}`")
    st.caption(
        "Name, number, email, website, LinkedIn aur picture "
        "My Profile / Contact page se manually update karein."
    )


    if st.session_state.admin_logged_in:
        st.markdown("### Website Images")

        img_col1, img_col2 = st.columns(2)

        with img_col1:
            st.markdown("#### Profile Picture")
            if PROFILE_IMAGE_PATH.exists():
                st.image(
                    str(PROFILE_IMAGE_PATH),
                    width=160,
                )

            new_profile_picture = st.file_uploader(
                "Upload New Profile Picture",
                type=["png", "jpg", "jpeg", "webp"],
                key="settings_profile_picture",
            )

            if new_profile_picture is not None:
                if st.button(
                    "Save Profile Picture",
                    type="primary",
                    use_container_width=True,
                    key="save_settings_profile_picture",
                ):
                    try:
                        save_profile_image(new_profile_picture)
                        st.success("Profile picture update ho gayi.")
                        st.rerun()
                    except Exception as error:
                        st.error(f"Profile picture save error: {error}")

        with img_col2:
            st.markdown("#### Dashboard / Front Image")
            if HERO_IMAGE_PATH.exists():
                st.image(
                    str(HERO_IMAGE_PATH),
                    use_container_width=True,
                )
            else:
                st.caption(
                    "Abhi dashboard par live SaaS website-data visual show ho raha hai."
                )

            new_hero_picture = st.file_uploader(
                "Upload Dashboard Image",
                type=["png", "jpg", "jpeg", "webp"],
                key="settings_hero_picture",
            )

            if new_hero_picture is not None:
                if st.button(
                    "Save Dashboard Image",
                    type="primary",
                    use_container_width=True,
                    key="save_settings_hero_picture",
                ):
                    try:
                        save_dashboard_hero_image(new_hero_picture)
                        st.success("Dashboard image update ho gayi.")
                        st.rerun()
                    except Exception as error:
                        st.error(f"Dashboard image save error: {error}")

            if HERO_IMAGE_PATH.exists():
                if st.button(
                    "Remove Dashboard Image / Use Live Data Visual",
                    use_container_width=True,
                    key="remove_hero_picture",
                ):
                    try:
                        HERO_IMAGE_PATH.unlink()
                    except OSError:
                        pass
                    st.success("Dashboard live-data visual restore ho gaya.")
                    st.rerun()

    if require_admin():
        st.markdown("### Profile & Contact Settings")

        with st.expander(
            "Edit WhatsApp, Email, Website and LinkedIn",
            expanded=True,
        ):
            with st.form("quick_contact_settings_form"):
                quick_phone = st.text_input(
                    "WhatsApp Number",
                    value=profile_settings.get("phone", ""),
                    placeholder="03107180990",
                )
                quick_email = st.text_input(
                    "Email",
                    value=profile_settings.get("email", ""),
                )
                quick_website = st.text_input(
                    "Website",
                    value=profile_settings.get("website", ""),
                )
                quick_linkedin = st.text_input(
                    "LinkedIn",
                    value=profile_settings.get("linkedin", ""),
                )
                quick_location = st.text_input(
                    "Location",
                    value=profile_settings.get("location", ""),
                )

                quick_save = st.form_submit_button(
                    "Save Contact Details",
                    type="primary",
                    use_container_width=True,
                )

            if quick_save:
                updated_profile = profile_settings.copy()
                updated_profile.update(
                    {
                        "phone": quick_phone.strip(),
                        "email": quick_email.strip(),
                        "website": quick_website.strip(),
                        "linkedin": quick_linkedin.strip(),
                        "location": quick_location.strip(),
                    }
                )
                save_profile_settings(updated_profile)
                st.success(
                    "Contact details successfully save ho gayi."
                )
                st.rerun()

        st.markdown("### Change Admin Password")
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            change = st.form_submit_button("Change Password", type="primary")

        if change:
            auth = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
            current_hash = hashlib.sha256(current_password.encode("utf-8")).hexdigest()

            if current_hash != auth["password_hash"]:
                st.error("Current password ghalat hai.")
            elif len(new_password) < 8:
                st.error("New password minimum 8 characters ka ho.")
            elif new_password != confirm_password:
                st.error("New passwords match nahi karte.")
            else:
                auth["password_hash"] = hashlib.sha256(
                    new_password.encode("utf-8")
                ).hexdigest()
                AUTH_PATH.write_text(json.dumps(auth, indent=2), encoding="utf-8")
                st.success("✅ Password change ho gaya.")
