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
import os
import urllib.parse
import urllib.request
import urllib.error

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

RESELLER_PRIVATE_DB_PATH = BASE_DIR / "database" / "reseller_private.db"
SHEET_STRUCTURE_DB_PATH = BASE_DIR / "database" / "sheet_structure.db"
DEFAULT_RESELLER_MARKUP = 20.0
def _secret_or_env(name: str) -> str:
    value = os.getenv(name, "")
    if value:
        return str(value)
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""

SUPABASE_URL = _secret_or_env("SUPABASE_URL").rstrip("/")
SUPABASE_SECRET_KEY = _secret_or_env("SUPABASE_SECRET_KEY")
AHREFS_API_KEY = _secret_or_env("AHREFS_API_KEY")


# =========================================================
# STYLING — LOVABLE INSPIRED PREMIUM SAAS
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Sora:wght@500;600;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0');

    :root {
        --bg: #E8EDF5;
        --surface: #F8FAFD;
        --surface-2: #EEF3F8;
        --surface-3: #E3EAF3;
        --ink: #172033;
        --muted: #65728A;
        --border: #CED7E4;
        --sidebar: #090E1A;
        --sidebar-2: #0B1222;
        --sidebar-line: rgba(255,255,255,.08);
        --purple: #6B4FE3;
        --purple-soft: #ECE7FF;
        --cyan: #0FA9B2;
        --cyan-soft: #DDF6F5;
        --ice: #E7F1FF;
        --gold: #D59B2D;
        --gold-soft: #FFF2D7;
        --danger: #F06A78;
        --shadow: 0 18px 45px -30px rgba(0,0,0,.72);
        --shadow-lg: 0 28px 70px -34px rgba(0,0,0,.82);
    }

    html, body, [class*="css"] { font-family: "Manrope", sans-serif; }
    h1,h2,h3,h4,.main-title,.metric-value,.hero-title { font-family: "Sora", sans-serif !important; }

    .stApp {
        background:
            radial-gradient(circle at 88% 0%, rgba(15,169,178,.10), transparent 25rem),
            radial-gradient(circle at 68% 9%, rgba(107,79,227,.08), transparent 22rem),
            linear-gradient(180deg,#EDF2F8 0%,#E6ECF4 100%);
        color: var(--ink);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.15rem;
        padding-bottom: 3rem;
        animation: none;
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
        width:40px; height:40px; border-radius:14px;
        display:grid; place-items:center;
        background:
            radial-gradient(circle at 28% 22%,rgba(255,255,255,.28),transparent 25%),
            linear-gradient(135deg,#7650E3 0%,#4D7CE0 52%,#1AC8C7 100%);
        box-shadow:
            0 10px 28px rgba(70,82,215,.32),
            inset 0 0 0 1px rgba(255,255,255,.18);
        transition:transform .2s ease,box-shadow .2s ease;
    }
    .sidebar-logo:hover {
        transform:translateY(-2px) rotate(-2deg);
        box-shadow:0 14px 32px rgba(70,82,215,.38);
    }
    .sidebar-logo .material-symbols-rounded {font-size:20px;color:white;}
    .sidebar-title {font-family:"Sora";font-size:14px;font-weight:750;color:#fff;line-height:1.25;letter-spacing:-.01em;}
    .sidebar-sub {font-size:10px;color:#96A2BA;margin-top:3px;letter-spacing:.035em;}

    [data-testid="stSidebar"] [role="radiogroup"] label {
        position:relative;
        border-radius:13px;
        padding:10px 12px 10px 46px;
        margin:3px 4px;
        min-height:43px;
        transition:all .18s ease;
        font-size:13.2px;
        font-weight:650;
        color:#C7CEDD;
        border:1px solid transparent;
        letter-spacing:.005em;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background:linear-gradient(90deg,rgba(255,255,255,.06),rgba(255,255,255,.025));
        transform:translateX(3px);
        color:#fff;
        border-color:rgba(255,255,255,.07);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background:
            linear-gradient(90deg,rgba(112,69,214,.28),rgba(24,191,197,.10));
        color:#fff;
        border-color:rgba(132,101,229,.46);
        box-shadow:
            inset 3px 0 0 #49E2DF,
            0 8px 22px rgba(0,0,0,.13);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label::before {
        font-family:"Material Symbols Rounded";
        position:absolute;
        left:12px;
        top:50%;
        transform:translateY(-50%);
        width:25px;
        height:25px;
        border-radius:8px;
        display:grid;
        place-items:center;
        font-size:17px;
        color:#C3CCDD;
        background:rgba(255,255,255,.055);
        border:1px solid rgba(255,255,255,.07);
        transition:all .18s ease;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover::before {
        background:rgba(255,255,255,.09);
        transform:translateY(-50%) scale(1.04);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked)::before {
        color:#071B23;
        background:linear-gradient(135deg,#71F0E7,#41C9D8);
        border-color:rgba(255,255,255,.45);
        box-shadow:0 6px 16px rgba(24,191,197,.24);
    }

    /* Navigation icons — matched to current menu order */
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1)::before  {content:"dashboard";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2)::before  {content:"monitoring";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3)::before  {content:"search";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4)::before  {content:"query_stats";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5)::before  {content:"person_search";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6)::before  {content:"add_circle";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(7)::before  {content:"upload_file";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(8)::before  {content:"edit_square";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(9)::before  {content:"delete";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(10)::before {content:"content_copy";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(11)::before {content:"download";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(12)::before {content:"star";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(13)::before {content:"contact_page";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(14)::before {content:"shield_person";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(15)::before {content:"sell";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(16)::before {content:"data_table";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(17)::before {content:"cloud_sync";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(18)::before {content:"lock_person";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(19)::before {content:"conversion_path";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(20)::before {content:"groups";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(21)::before {content:"support_agent";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(22)::before {content:"account_circle";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(23)::before {content:"backup";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(24)::before {content:"settings";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(25)::before {content:"admin_panel_settings";}

    /* Tiny visual separator before admin / system tools */
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(17) {
        margin-top:10px;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(23) {
        margin-top:10px;
    }

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
    .main-title {font-size:36px;font-weight:700;letter-spacing:-.035em;color:#172033;margin:0;line-height:1.14;}
    .subtitle {color:#65728A;font-size:13px;margin:7px 0 18px;}

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
        background:linear-gradient(145deg,#FBFCFE,#F1F5F9);
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
    .metric-label {font-size:10px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:#758198;margin-bottom:7px;}
    .metric-value {font-size:28px;font-weight:600;color:#172033;letter-spacing:-.03em;}
    .metric-delta {font-size:10px;color:#7A879C;margin-top:5px;}

    .section-title {font-family:"Sora";font-size:19px;font-weight:650;color:#1B2437;margin:26px 0 12px;display:flex;align-items:center;gap:10px;}
    .section-kicker {font-size:11px;color:var(--muted);margin-top:-7px;margin-bottom:14px;}

    .surface-card {
        background:linear-gradient(145deg,#FBFCFE,#F2F6FA);
        border:1px solid var(--border);border-radius:18px;box-shadow:var(--shadow);padding:20px;
        color:#1B2437;
    }

    .publisher-list {background:#F9FBFD;border:1px solid var(--border);border-radius:18px;overflow:hidden;box-shadow:var(--shadow);}
    .publisher-head {display:flex;justify-content:space-between;align-items:center;padding:17px 19px;border-bottom:1px solid var(--border);}
    .publisher-title {font-family:"Sora";font-weight:650;font-size:15px;color:#242635;}
    .publisher-sub {font-size:10.5px;color:#7A7E8A;margin-top:3px;}
    .publisher-row {display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:14px;align-items:center;padding:13px 19px;border-bottom:1px solid #E8E3DA;transition:background .15s ease;}
    .publisher-row:last-child{border-bottom:0}.publisher-row:hover{background:#EEF3F8}
    .publisher-site {font-size:12.5px;font-weight:700;color:#1B2437;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
    .publisher-meta {font-size:10px;color:#748198;margin-top:2px;}
    .dr-badge {background:#E8EEF6;border:1px solid #D4DEE9;border-radius:999px;padding:5px 8px;font-size:10px;font-weight:700;color:#344158;}
    .price-tag {font-size:12px;font-weight:800;color:var(--purple);min-width:55px;text-align:right;}

    .form-section {
        background:linear-gradient(145deg,#FBFCFE,#F1F5F9);border:1px solid var(--border);border-radius:18px;padding:20px 22px;margin:12px 0 16px;box-shadow:var(--shadow);
    }
    .form-section-title {font-family:"Sora";font-size:17px;font-weight:650;color:#1B2437;margin-bottom:3px;}
    .form-section-sub {font-size:11px;color:#718097;margin-bottom:13px;}

    div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius:12px!important;
        border-color:#CBD5E1!important;
        background:#F9FBFD!important;
        color:#182033!important;
        min-height:42px;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {box-shadow:0 0 0 2px rgba(112,69,214,.13)!important;border-color:#8D70DD!important;}

    .stButton > button,.stDownloadButton > button,.stLinkButton > a {
        border-radius:11px!important;font-weight:700!important;min-height:41px;transition:transform .16s ease,box-shadow .16s ease!important;
    }
    .stButton > button:hover,.stDownloadButton > button:hover,.stLinkButton > a:hover {transform:translateY(-1px);}
    .stButton > button[kind="primary"] {background:linear-gradient(135deg,#6E42D4,#7249DB 55%,#4F71DA);border:0;box-shadow:0 9px 22px rgba(112,69,214,.22);}


    .wa-float {position:fixed;right:22px;bottom:22px;z-index:9999;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none!important;background:linear-gradient(135deg,#17A854,#24CA67);box-shadow:0 12px 28px rgba(34,197,94,.32);border:2px solid rgba(255,255,255,.9);transition:transform .18s ease;animation:softGlow 3s ease-in-out infinite;}
    .wa-float:hover{transform:translateY(-3px) scale(1.03)}.wa-float svg{width:29px;height:29px;fill:#fff}
    .whatsapp-button {display:block;text-align:center;background:linear-gradient(135deg,#16A34A,#22C55E);color:#fff!important;padding:12px 16px;border-radius:11px;font-weight:800;text-decoration:none!important;margin:8px 0;box-shadow:0 8px 18px rgba(34,197,94,.22);}


    /* Remove remaining bright white surfaces */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [data-baseweb="select"] ul,
    [role="listbox"] {
        background:#F9FBFD!important;
        color:#182033!important;
        border-color:#CBD5E1!important;
    }
    [role="option"] {background:#F9FBFD!important;color:#182033!important;}
    [role="option"]:hover {background:#EAF1F8!important;}

    [data-testid="stDataFrame"] {
        border:1px solid var(--border);
        border-radius:16px;
        overflow:hidden;
        background:#F4F7FB;
        box-shadow:var(--shadow);
    }

    [data-testid="stMetric"] {
        background:#F8FAFD;
        border:1px solid var(--border);
        border-radius:16px;
        padding:14px;
        box-shadow:var(--shadow);
    }

    [data-testid="stAlert"] {
        background:#F4F7FB!important;
        color:#1C2538!important;
        border:1px solid #D2DBE7!important;
        border-radius:14px!important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background:#F4F7FB;
        border-radius:12px;
        padding:4px;
    }

    .stTabs [data-baseweb="tab"] {
        color:#67758C!important;
        border-radius:9px;
    }

    .stTabs [aria-selected="true"] {
        background:#E7EEFA!important;
        color:#20304A!important;
    }

    .stExpander {
        background:#F8FAFD!important;
        border:1px solid #D2DBE7!important;
        border-radius:14px!important;
    }

    /* Softer loading / less visual flash */
    [data-testid="stStatusWidget"],
    [data-testid="stSpinner"] {
        color:#5FE0DB!important;
    }


    /* High-contrast premium polish */
    .stButton > button:not([kind="primary"]),
    .stDownloadButton > button,
    .stLinkButton > a {
        background:#F7F9FC!important;
        color:#22304A!important;
        border:1px solid #C9D4E2!important;
        box-shadow:0 5px 14px rgba(25,41,72,.07)!important;
    }
    .stButton > button:not([kind="primary"]):hover,
    .stDownloadButton > button:hover,
    .stLinkButton > a:hover {
        background:#EEF3F9!important;
        color:#172033!important;
        border-color:#9FB1C8!important;
    }
    [data-testid="stCaptionContainer"], .stCaption, small {
        color:#68758C!important;
    }
    label, [data-testid="stWidgetLabel"] {
        color:#253149!important;
        font-weight:600!important;
    }
    [data-testid="stDataFrame"] {
        background:#F8FAFD!important;
        border-color:#CBD6E3!important;
    }
    [data-testid="stMetric"] {
        background:#F8FAFD!important;
        color:#182033!important;
    }

    /* Distinct icon colors */
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1)::before  {background:rgba(71,194,230,.16);color:#58D5F3;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2)::before  {background:rgba(157,124,245,.16);color:#B79AF9;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3)::before  {background:rgba(84,169,255,.16);color:#72B7FF;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4)::before  {background:rgba(46,213,168,.16);color:#5DE2B7;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5)::before  {background:rgba(244,184,75,.16);color:#F5C65E;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6)::before  {background:rgba(69,216,191,.16);color:#5AE3C8;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(7)::before  {background:rgba(91,180,255,.16);color:#77C3FF;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(8)::before  {background:rgba(183,139,246,.16);color:#CAA4FA;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(9)::before  {background:rgba(245,107,120,.16);color:#FF8995;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(10)::before {background:rgba(244,184,75,.16);color:#F5C65E;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(11)::before {background:rgba(75,205,167,.16);color:#6BE0BB;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(12)::before {background:rgba(250,200,69,.16);color:#FFD65C;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(13)::before {background:rgba(71,194,230,.16);color:#6FDBF2;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(14)::before {background:rgba(121,101,237,.16);color:#A391F3;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(15)::before {background:rgba(232,145,74,.16);color:#F0A66A;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(16)::before {background:rgba(91,180,255,.16);color:#76C2FF;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(17)::before {background:rgba(46,213,168,.16);color:#5DE2B7;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(18)::before {background:rgba(241,123,158,.16);color:#F395B2;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(19)::before {background:rgba(157,124,245,.16);color:#B89AF8;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(20)::before {background:rgba(75,205,167,.16);color:#69DEBA;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(21)::before {background:rgba(91,180,255,.16);color:#75C1FF;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(22)::before {background:rgba(157,124,245,.16);color:#B99AF8;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(23)::before {background:rgba(244,184,75,.16);color:#F5C65E;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(24)::before {background:rgba(137,151,176,.18);color:#BBC5D6;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(25)::before {background:rgba(245,107,120,.16);color:#FF8995;}

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
# SUPABASE / LIVE SYNC
# =========================================================
def cloud_enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SECRET_KEY)

def _supabase_headers(extra=None):
    h={"apikey":SUPABASE_SECRET_KEY,"Authorization":f"Bearer {SUPABASE_SECRET_KEY}","Content-Type":"application/json"}
    if extra: h.update(extra)
    return h

def supabase_request(method, table, query="", payload=None, prefer=""):
    if not cloud_enabled():
        raise RuntimeError("Supabase secrets configured nahi hain.")
    url=f"{SUPABASE_URL}/rest/v1/{table}" + (("?"+query.lstrip("?")) if query else "")
    data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode("utf-8")
    headers=_supabase_headers({"Prefer":prefer} if prefer else None)
    req=urllib.request.Request(url,data=data,headers=headers,method=method.upper())
    try:
        with urllib.request.urlopen(req,timeout=45) as r:
            raw=r.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        body=exc.read().decode("utf-8",errors="ignore")
        raise RuntimeError(f"Supabase HTTP {exc.code}: {body}") from exc

def cloud_fetch(table, select="*", extra_query=""):
    q=f"select={urllib.parse.quote(select,safe='*,()')}"
    if extra_query: q += "&"+extra_query.lstrip("&")
    return pd.DataFrame(supabase_request("GET",table,q) or [])

def cloud_upsert_rows(table, rows, on_conflict=""):
    if not rows: return
    q=("on_conflict="+urllib.parse.quote(on_conflict,safe=",")) if on_conflict else ""
    supabase_request("POST",table,q,rows,"resolution=merge-duplicates,return=minimal")

def cloud_delete(table, query):
    supabase_request("DELETE",table,query,prefer="return=minimal")

def load_cloud_sites():
    if not cloud_enabled(): return pd.DataFrame()
    all_rows=[]; offset=0; limit=1000
    while True:
        batch=supabase_request("GET","gp_sites",f"select=*&order=id.desc&offset={offset}&limit={limit}") or []
        all_rows.extend(batch)
        if len(batch)<limit: break
        offset += limit
    return pd.DataFrame(all_rows)

def cloud_patch_site(site_id, updates):
    if not cloud_enabled(): return
    payload=dict(updates); payload["updated_at"]=datetime.now().isoformat(timespec="seconds")
    supabase_request("PATCH","gp_sites",f"id=eq.{int(site_id)}",payload,"return=minimal")

def cloud_delete_site(site_id):
    if cloud_enabled(): cloud_delete("gp_sites",f"id=eq.{int(site_id)}")


def _site_payload_from_dict(r: dict) -> dict:
    return {
        "id": int(r["id"]),
        "site": clean_value(r.get("site","")),
        "country": clean_value(r.get("country","")),
        "da": clean_value(r.get("da","")),
        "dr": clean_value(r.get("dr","")),
        "traffic": clean_value(r.get("traffic","")),
        "original_price": parse_price(r.get("original_price", r.get("general_price",""))),
        "selling_price": parse_price(r.get("selling_price", r.get("general_price",""))),
        "markup_percent": float(r.get("markup_percent", DEFAULT_RESELLER_MARKUP) or DEFAULT_RESELLER_MARKUP),
        "manual_price": bool(r.get("manual_price",0)),
        "casino_original_price": parse_price(r.get("casino_original_price", r.get("casino_price",""))),
        "casino_selling_price": parse_price(r.get("casino_selling_price", r.get("casino_price",""))),
        "payment_method": clean_value(r.get("payment_method","")),
        "tat": clean_value(r.get("tat","")),
        "type": clean_value(r.get("type","")),
        "link_type": clean_value(r.get("link_type","")),
        "source_file": clean_value(r.get("source_file","")),
        "sheet_name": clean_value(r.get("sheet_name","")),
        "favorite": bool(r.get("favorite",0)),
        "created_at": clean_value(r.get("created_at","")) or datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }


def fast_sync_local_sites_to_cloud(progress_callback=None, batch_size: int = 250) -> int:
    """Fast bulk initial sync. One HTTP request per batch instead of one per site."""
    if not cloud_enabled():
        raise RuntimeError("Supabase not configured.")

    with sqlite3.connect(DB_PATH) as conn:
        frame = pd.read_sql_query("SELECT * FROM sites ORDER BY id", conn)

    total = len(frame)
    if total == 0:
        return 0

    # Initial sync intentionally replaces cloud gp_sites.
    cloud_delete("gp_sites", "id=gt.0")

    sent = 0
    for start in range(0, total, batch_size):
        batch_df = frame.iloc[start:start + batch_size]
        payload = [_site_payload_from_dict(r.to_dict()) for _, r in batch_df.iterrows()]
        cloud_upsert_rows("gp_sites", payload, on_conflict="id")
        sent += len(payload)
        if progress_callback:
            progress_callback(sent, total)

    return sent



# =========================================================
# AHREFS REAL METRICS
# =========================================================
def ahrefs_enabled() -> bool:
    return bool(AHREFS_API_KEY)


def _ahrefs_request_json(url: str, *, method: str = "GET", payload=None):
    if not AHREFS_API_KEY:
        raise RuntimeError("AHREFS_API_KEY is not configured.")

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {AHREFS_API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "GP-Site-Finder-Pro/1.0",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        if exc.code == 401:
            raise RuntimeError("Ahrefs API key invalid/expired (401).") from exc
        if exc.code == 403:
            raise RuntimeError(
                "Ahrefs plan/API key me Site Explorer traffic access enabled nahi hai (403)."
            ) from exc
        if exc.code == 429:
            raise RuntimeError(
                "Ahrefs rate limit reached (429). Thori dair baad try karein."
            ) from exc
        raise RuntimeError(f"Ahrefs HTTP {exc.code}: {body[:300]}") from exc
    except Exception as exc:
        raise RuntimeError(f"Ahrefs connection error: {exc}") from exc


@st.cache_data(show_spinner=False, ttl=1800)
def ahrefs_live_dr(target: str) -> dict:
    target = normalize_domain(target)
    if not target:
        raise ValueError("Valid domain required.")

    endpoint = "https://api.ahrefs.com/v3/public/domain-rating-free"
    query = urllib.parse.urlencode({"target": target, "output": "json"})
    payload = _ahrefs_request_json(f"{endpoint}?{query}")

    dr_obj = payload.get("domain_rating", {}) if isinstance(payload, dict) else {}
    return {
        "dr": dr_obj.get("domain_rating"),
        "license": clean_value(dr_obj.get("license", "")),
        "warning": clean_value(dr_obj.get("warning", "")),
    }


@st.cache_data(show_spinner=False, ttl=1800)
def ahrefs_live_traffic(target: str) -> dict:
    """
    Ahrefs estimated monthly organic traffic.
    This endpoint may require paid Site Explorer API access.
    """
    target = normalize_domain(target)
    if not target:
        raise ValueError("Valid domain required.")

    endpoint = "https://api.ahrefs.com/v3/site-explorer/metrics"
    query = urllib.parse.urlencode({
        "target": target,
        "date": datetime.now().date().isoformat(),
        "mode": "domain",
        "protocol": "both",
        "volume_mode": "monthly",
        "traffic_mode": "static",
        "output": "json",
    })

    payload = _ahrefs_request_json(f"{endpoint}?{query}")
    metrics = payload.get("metrics", {}) if isinstance(payload, dict) else {}

    return {
        "organic_traffic": metrics.get("org_traffic"),
        "organic_keywords": metrics.get("org_keywords"),
        "organic_keywords_top3": metrics.get("org_keywords_1_3"),
        "organic_traffic_value_cents": metrics.get("org_cost"),
    }


def save_live_dr(site_id: int, live_dr) -> None:
    if live_dr is None:
        return
    dr_text = str(round(float(live_dr), 1))
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE sites SET dr=? WHERE id=?", (dr_text, int(site_id)))
        conn.commit()

    try:
        sync_one_site_to_cloud(int(site_id))
    except Exception:
        pass


def save_live_traffic(site_id: int, live_traffic) -> None:
    if live_traffic is None:
        return
    traffic_text = str(int(live_traffic))
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE sites SET traffic=? WHERE id=?",
            (traffic_text, int(site_id)),
        )
        conn.commit()

    try:
        sync_one_site_to_cloud(int(site_id))
    except Exception:
        pass



# =========================================================
# FAST SEARCH / PAGINATION HELPERS
# =========================================================
@st.cache_data(show_spinner=False, ttl=1800)
def cached_filter_lists(
    niches: tuple,
    countries: tuple,
    payments: tuple,
    link_types: tuple,
    sheets: tuple,
):
    return {
        "niche": ["All"] + list(niches),
        "country": ["All"] + list(countries),
        "payment": ["All"] + list(payments),
        "link_type": ["All"] + list(link_types),
        "sheet": ["All"] + list(sheets),
    }


def _clean_filter_values(frame: pd.DataFrame, column: str):
    if column not in frame.columns:
        return tuple()
    values = safe_unique(frame, column)
    return tuple(values[1:] if values and values[0] == "All" else values)


def get_filter_options(frame: pd.DataFrame) -> dict:
    return cached_filter_lists(
        _clean_filter_values(frame, "detected_niche"),
        _clean_filter_values(frame, "country"),
        _clean_filter_values(frame, "payment_method"),
        _clean_filter_values(frame, "link_type"),
        _clean_filter_values(frame, "sheet_name"),
    )


def fast_filter_sites(
    frame: pd.DataFrame,
    search_query: str,
    niche: str,
    country: str,
    payment: str,
    link_type: str,
    sheet: str,
    min_dr: float,
    max_price: float,
) -> pd.DataFrame:
    filtered = frame

    if search_query.strip():
        raw_query = search_query.strip().lower()
        smart_query = normalize_search_query(raw_query)
        queries = [value for value in {raw_query, smart_query} if value]

        search_mask = pd.Series(False, index=filtered.index)

        for query in queries:
            search_mask |= filtered["_search_text"].str.contains(
                query,
                regex=False,
                na=False,
            )

        if "site" in filtered.columns and smart_query:
            normalized_sites = (
                filtered["site"]
                .fillna("")
                .astype(str)
                .map(normalize_search_query)
            )
            search_mask |= normalized_sites.eq(smart_query)

        filtered = filtered.loc[search_mask]

    if niche != "All":
        filtered = filtered.loc[filtered["detected_niche"].eq(niche)]
    if country != "All":
        filtered = filtered.loc[filtered["country"].eq(country)]
    if payment != "All":
        filtered = filtered.loc[filtered["payment_method"].eq(payment)]
    if link_type != "All":
        filtered = filtered.loc[filtered["link_type"].eq(link_type)]
    if sheet != "All":
        filtered = filtered.loc[filtered["sheet_name"].eq(sheet)]

    return filtered.loc[
        filtered["_dr_num"].fillna(-1).ge(min_dr)
        & filtered["_price_num"].fillna(0).le(max_price)
    ]


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
        existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(sites)").fetchall()}
        for col_name, col_type in [
            ("original_price","TEXT"),("selling_price","TEXT"),("markup_percent","REAL DEFAULT 20"),
            ("manual_price","INTEGER DEFAULT 0"),("casino_original_price","TEXT"),("casino_selling_price","TEXT")
        ]:
            if col_name not in existing_cols:
                conn.execute(f"ALTER TABLE sites ADD COLUMN {col_name} {col_type}")
        conn.execute("""CREATE TABLE IF NOT EXISTS reseller_settings(
            source_file TEXT NOT NULL, sheet_name TEXT NOT NULL, markup_percent REAL DEFAULT 20,
            updated_at TEXT NOT NULL, PRIMARY KEY(source_file,sheet_name))""")
        conn.execute("UPDATE sites SET original_price=general_price WHERE original_price IS NULL OR original_price='' ")
        conn.execute("UPDATE sites SET casino_original_price=casino_price WHERE casino_original_price IS NULL OR casino_original_price='' ")
        conn.execute("UPDATE sites SET markup_percent=20 WHERE markup_percent IS NULL")
        conn.execute("""UPDATE sites SET selling_price=CASE WHEN selling_price IS NULL OR selling_price='' THEN
            CASE WHEN CAST(REPLACE(REPLACE(original_price,'$',''),',','') AS REAL)>0 THEN printf('%.2f',CAST(REPLACE(REPLACE(original_price,'$',''),',','') AS REAL)*1.20) ELSE general_price END ELSE selling_price END""")
        conn.execute("""UPDATE sites SET casino_selling_price=CASE WHEN casino_selling_price IS NULL OR casino_selling_price='' THEN
            CASE WHEN CAST(REPLACE(REPLACE(casino_original_price,'$',''),',','') AS REAL)>0 THEN printf('%.2f',CAST(REPLACE(REPLACE(casino_original_price,'$',''),',','') AS REAL)*1.20) ELSE casino_price END ELSE casino_selling_price END""")
        conn.execute("UPDATE sites SET general_price=selling_price WHERE selling_price IS NOT NULL AND selling_price<>''")
        conn.execute("UPDATE sites SET casino_price=casino_selling_price WHERE casino_selling_price IS NOT NULL AND casino_selling_price<>''")
        conn.commit()

    with sqlite3.connect(RESELLER_PRIVATE_DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS reseller_private(
            id INTEGER PRIMARY KEY AUTOINCREMENT, source_file TEXT NOT NULL, sheet_name TEXT,
            field_name TEXT NOT NULL, field_value TEXT, updated_at TEXT NOT NULL)""")
        conn.commit()

    with sqlite3.connect(SHEET_STRUCTURE_DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS sheet_structure(
            source_file TEXT NOT NULL, sheet_name TEXT NOT NULL, header_row INTEGER, status TEXT,
            mapped_fields TEXT, private_count INTEGER DEFAULT 0, updated_at TEXT NOT NULL,
            PRIMARY KEY(source_file,sheet_name))""")
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


@st.cache_data(show_spinner=False, ttl=1800)
def load_sites() -> pd.DataFrame:
    """
    FAST STARTUP MODE:
    - Local SQLite is primary for instant page load.
    - Supabase is only used as fallback if local DB is empty.
    - Cloud Sync page remains responsible for explicit cloud synchronization.
    """
    frame = pd.DataFrame()

    # 1) Local first — much faster than downloading 13k+ rows on every fresh app start.
    try:
        with sqlite3.connect(DB_PATH) as conn:
            frame = pd.read_sql_query(
                "SELECT * FROM sites ORDER BY id DESC",
                conn,
            )
    except Exception:
        frame = pd.DataFrame()

    # 2) Cloud fallback only when local DB has no site data.
    if frame.empty and cloud_enabled():
        try:
            frame = load_cloud_sites()
        except Exception:
            frame = pd.DataFrame()

    if frame.empty:
        return frame

    if "selling_price" in frame.columns:
        frame["general_price"] = frame["selling_price"].where(
            frame["selling_price"].notna(),
            frame.get("general_price"),
        )

    if "casino_selling_price" in frame.columns:
        frame["casino_price"] = frame["casino_selling_price"].where(
            frame["casino_selling_price"].notna(),
            frame.get("casino_price"),
        )

    frame = add_detected_niche(frame)

    for _cat_col in ["country", "payment_method", "link_type"]:
        if _cat_col in frame.columns:
            _s = frame[_cat_col].fillna("").astype(str).str.strip()
            _s = _s.mask(_s.map(_looks_numeric_only), "")

            if _cat_col == "country":
                _country_valid = (
                    _s.str.contains(r"[A-Za-z]", regex=True, na=False)
                    & ~_s.str.contains(r"\d", regex=True, na=False)
                    & _s.str.match(r"^[A-Za-zÀ-ÿ .,'()&/-]+$", na=False)
                    & (_s.str.len() <= 80)
                )
                _s = _s.mask(~_country_valid, "")

            elif _cat_col == "payment_method":
                _allowed = [
                    "after", "upfront", "advance", "negoti",
                    "paypal", "bank", "wise", "payoneer",
                    "crypto", "usdt", "stripe", "other",
                ]
                _valid = _s.str.lower().map(
                    lambda x: (
                        x == ""
                        or any(token in x for token in _allowed)
                    )
                )
                _s = _s.mask(~_valid, "")

            elif _cat_col == "link_type":
                _allowed = [
                    "dofollow", "do follow", "nofollow",
                    "no follow", "mixed", "sponsored",
                ]
                _valid = _s.str.lower().map(
                    lambda x: (
                        x == ""
                        or any(token in x for token in _allowed)
                    )
                )
                _s = _s.mask(~_valid, "")

            frame[_cat_col] = _s

    searchable_columns = [
        c for c in [
            "site", "country", "type", "detected_niche",
            "source_file", "sheet_name", "payment_method", "link_type"
        ]
        if c in frame.columns
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
        frame.get("general_price", pd.Series(index=frame.index, dtype=object)),
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



NICHE_RULES = {
    "SaaS": [
        "saas", "software", "cloud", "crm", "erp", "app", "apps", "platform",
        "startup", "b2b", "automation", "hosting", "web tool"
    ],
    "Tech": [
        "tech", "technology", "digital", "computer", "mobile", "gadget",
        "electronics", "cyber", "internet", "ai", "artificial intelligence"
    ],
    "Business": [
        "business", "finance", "marketing", "entrepreneur", "startup",
        "corporate", "management", "invest", "investment"
    ],
    "Food": [
        "food", "recipe", "restaurant", "kitchen", "cooking", "chef",
        "meal", "drink", "beverage"
    ],
    "Health": [
        "health", "medical", "fitness", "wellness", "doctor", "hospital",
        "medicine", "nutrition", "dental"
    ],
    "Travel": [
        "travel", "tour", "tourism", "hotel", "holiday", "vacation",
        "flight", "trip"
    ],
    "Education": [
        "education", "school", "college", "university", "student",
        "learning", "academy", "course"
    ],
    "Home & Garden": [
        "home", "garden", "interior", "decor", "furniture", "property",
        "real estate", "construction"
    ],
    "Fashion & Beauty": [
        "fashion", "beauty", "style", "clothing", "apparel", "makeup",
        "skin", "jewelry"
    ],
    "Sports": [
        "sport", "sports", "football", "cricket", "basketball", "soccer",
        "fitness sports"
    ],
    "Entertainment": [
        "entertainment", "movie", "music", "celebrity", "gaming", "games",
        "film", "tv"
    ],
    "News": [
        "news", "media", "daily", "journal", "press", "magazine"
    ],
    "Automotive": [
        "auto", "automotive", "car", "cars", "vehicle", "motor", "bike"
    ],
    "Crypto": [
        "crypto", "bitcoin", "blockchain", "web3", "forex"
    ],
}


def detect_niche_value(row) -> str:
    parts = [
        clean_value(row.get("type", "")),
        clean_value(row.get("sheet_name", "")),
        clean_value(row.get("source_file", "")),
        clean_value(row.get("site", "")),
    ]
    text = " ".join(parts).lower()

    # Stronger signal from explicit type/sheet name first.
    explicit = " ".join(parts[:2]).lower()
    for niche, keywords in NICHE_RULES.items():
        if any(k in explicit for k in keywords):
            return niche

    # Then domain/source fallback.
    for niche, keywords in NICHE_RULES.items():
        if any(k in text for k in keywords):
            return niche

    return "General"


def add_detected_niche(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        frame["detected_niche"] = []
        return frame
    frame = frame.copy()
    frame["detected_niche"] = frame.apply(detect_niche_value, axis=1)
    return frame


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


def parse_price(value):
    m=re.search(r"-?\d+(?:\.\d+)?",clean_value(value).replace(",",""))
    return float(m.group()) if m else None

def get_sheet_markup(source_file, sheet_name):
    with sqlite3.connect(DB_PATH) as conn:
        row=conn.execute("SELECT markup_percent FROM reseller_settings WHERE source_file=? AND sheet_name=?",(source_file,sheet_name)).fetchone()
    return float(row[0]) if row else DEFAULT_RESELLER_MARKUP

def sync_one_site_to_cloud(site_id):
    if not cloud_enabled(): return
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory=sqlite3.Row
        r=conn.execute("SELECT * FROM sites WHERE id=?",(int(site_id),)).fetchone()
    if not r: return
    d=dict(r)
    payload={
        "id":int(d["id"]),"site":clean_value(d.get("site","")),"country":clean_value(d.get("country","")),
        "da":clean_value(d.get("da","")),"dr":clean_value(d.get("dr","")),"traffic":clean_value(d.get("traffic","")),
        "original_price":parse_price(d.get("original_price",d.get("general_price",""))),
        "selling_price":parse_price(d.get("selling_price",d.get("general_price",""))),
        "markup_percent":float(d.get("markup_percent",DEFAULT_RESELLER_MARKUP) or DEFAULT_RESELLER_MARKUP),
        "manual_price":bool(d.get("manual_price",0)),
        "casino_original_price":parse_price(d.get("casino_original_price",d.get("casino_price",""))),
        "casino_selling_price":parse_price(d.get("casino_selling_price",d.get("casino_price",""))),
        "payment_method":clean_value(d.get("payment_method","")),"tat":clean_value(d.get("tat","")),
        "type":clean_value(d.get("type","")),"link_type":clean_value(d.get("link_type","")),
        "source_file":clean_value(d.get("source_file","")),"sheet_name":clean_value(d.get("sheet_name","")),
        "favorite":bool(d.get("favorite",0)),"created_at":clean_value(d.get("created_at","")) or datetime.now().isoformat(timespec="seconds"),
        "updated_at":datetime.now().isoformat(timespec="seconds")
    }
    cloud_upsert_rows("gp_sites",[payload],"id")

def set_sheet_markup(source_file, sheet_name, markup):
    now=datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO reseller_settings(source_file,sheet_name,markup_percent,updated_at) VALUES(?,?,?,?)
        ON CONFLICT(source_file,sheet_name) DO UPDATE SET markup_percent=excluded.markup_percent,updated_at=excluded.updated_at""",(source_file,sheet_name,float(markup),now))
        conn.execute("""UPDATE sites SET markup_percent=?,
            selling_price=CASE WHEN manual_price=1 THEN selling_price WHEN CAST(REPLACE(REPLACE(original_price,'$',''),',','') AS REAL)>0 THEN printf('%.2f',CAST(REPLACE(REPLACE(original_price,'$',''),',','') AS REAL)*(1+?/100.0)) ELSE selling_price END,
            general_price=CASE WHEN manual_price=1 THEN general_price WHEN CAST(REPLACE(REPLACE(original_price,'$',''),',','') AS REAL)>0 THEN printf('%.2f',CAST(REPLACE(REPLACE(original_price,'$',''),',','') AS REAL)*(1+?/100.0)) ELSE general_price END
            WHERE source_file=? AND sheet_name=?""",(float(markup),float(markup),float(markup),source_file,sheet_name))
        ids=[x[0] for x in conn.execute("SELECT id FROM sites WHERE source_file=? AND sheet_name=?",(source_file,sheet_name)).fetchall()]
        conn.commit()
    if cloud_enabled():
        cloud_upsert_rows("reseller_settings",[{"source_file":source_file,"sheet_name":sheet_name,"markup_percent":float(markup),"updated_at":now}],"source_file,sheet_name")
        for site_id in ids: sync_one_site_to_cloud(site_id)

PRIVATE_KEYWORDS=["owner","founder","ceo","manager","publisher","admin","contact","phone","mobile","whatsapp","email","telegram","skype","linkedin","paypal","payoneer","wise","stripe","usdt","jazzcash","easypaisa","sadapay","nayapay","bank","binance","account","payment","iban"]

def detect_private_rows(raw_df, header_row, source_file, sheet_name):
    sn=clean_heading(sheet_name)
    if any(x in sn for x in ["scammer","scam alert","blacklist","reported"]): return []
    if header_row is not None: scan_limit=min(header_row,len(raw_df))
    else:
        if not any(x in sn for x in ["intro","contact","team","payment","about"]): return []
        scan_limit=min(60,len(raw_df))
    out=[]
    for idx in range(scan_limit):
        vals=[clean_value(v) for v in raw_df.iloc[idx].tolist()]; vals=[v for v in vals if v]
        if not vals: continue
        joined=" | ".join(vals); low=joined.lower()
        phone=bool(re.search(r"\+?\d[\d\s().-]{7,}\d",joined)); email=bool(re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}",joined,re.I)); key=any(k in low for k in PRIVATE_KEYWORDS)
        if not (phone or email or key): continue
        kind="Payment" if ("payment" in low or any(k in low for k in ["paypal","payoneer","wise","stripe","jazzcash","easypaisa","bank","binance","usdt"])) else ("WhatsApp / Phone" if phone or any(k in low for k in ["whatsapp","phone","mobile"]) else ("Email" if email else "Team / Contact"))
        out.append({"source_file":source_file,"sheet_name":sheet_name,"field_name":f"{kind} • Row {idx+1}","field_value":joined})
    return out

def save_private_rows(rows):
    if not rows: return 0
    now=datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(RESELLER_PRIVATE_DB_PATH) as conn:
        for r in rows:
            conn.execute("DELETE FROM reseller_private WHERE source_file=? AND sheet_name=? AND field_name=?",(r["source_file"],r["sheet_name"],r["field_name"]))
            conn.execute("INSERT INTO reseller_private(source_file,sheet_name,field_name,field_value,updated_at) VALUES(?,?,?,?,?)",(r["source_file"],r["sheet_name"],r["field_name"],r["field_value"],now))
        conn.commit()
    if cloud_enabled():
        payload=[{"source_file":r["source_file"],"sheet_name":r["sheet_name"],"field_name":r["field_name"],"field_value":r["field_value"],"private":True,"updated_at":now} for r in rows]
        cloud_upsert_rows("reseller_private",payload)
    return len(rows)

def save_structure_report(source_file,sheet_name,header_row,mapped_fields,private_count):
    now=datetime.now().isoformat(timespec="seconds"); status="OK" if header_row is not None else ("Private info sheet" if private_count else "No website header")
    with sqlite3.connect(SHEET_STRUCTURE_DB_PATH) as conn:
        conn.execute("""INSERT INTO sheet_structure(source_file,sheet_name,header_row,status,mapped_fields,private_count,updated_at) VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(source_file,sheet_name) DO UPDATE SET header_row=excluded.header_row,status=excluded.status,mapped_fields=excluded.mapped_fields,private_count=excluded.private_count,updated_at=excluded.updated_at""",(source_file,sheet_name,(header_row+1 if header_row is not None else None),status,mapped_fields,int(private_count),now)); conn.commit()
    if cloud_enabled(): cloud_upsert_rows("sheet_structure",[{"source_file":source_file,"sheet_name":sheet_name,"header_row":(header_row+1 if header_row is not None else None),"status":status,"mapped_fields":mapped_fields,"private_count":int(private_count),"updated_at":now}],"source_file,sheet_name")

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
        original=clean_value(item["general_price"]); casino_original=clean_value(item["casino_price"]); markup=get_sheet_markup(source_file,sheet_name)
        item["original_price"]=original; item["markup_percent"]=markup; item["manual_price"]=0
        item["selling_price"]=(f"{parse_price(original)*(1+markup/100.0):.2f}" if parse_price(original) is not None else original)
        item["casino_original_price"]=casino_original; item["casino_selling_price"]=(f"{parse_price(casino_original)*(1+markup/100.0):.2f}" if parse_price(casino_original) is not None else casino_original)
        item["general_price"]=item["selling_price"]; item["casino_price"]=item["casino_selling_price"]; rows.append(item)

    return pd.DataFrame(rows)


def save_imported_sites(prepared_df):
    if prepared_df.empty: return 0
    ids=[]
    with sqlite3.connect(DB_PATH) as conn:
        for _,r in prepared_df.iterrows():
            ex=conn.execute("SELECT id,manual_price,selling_price FROM sites WHERE lower(site)=lower(?) AND source_file=? AND sheet_name=?",(r["site"],r["source_file"],r["sheet_name"])).fetchone()
            sell=r["selling_price"]
            if ex and ex[1]: sell=ex[2]
            if ex:
                site_id=ex[0]; conn.execute("""UPDATE sites SET country=?,da=?,dr=?,traffic=?,general_price=?,casino_price=?,payment_method=?,tat=?,type=?,link_type=?,favorite=?,created_at=?,original_price=?,selling_price=?,markup_percent=?,casino_original_price=?,casino_selling_price=? WHERE id=?""",(r["country"],r["da"],r["dr"],r["traffic"],sell,r["casino_selling_price"],r["payment_method"],r["tat"],r["type"],r["link_type"],int(r["favorite"]),r["created_at"],r["original_price"],sell,float(r["markup_percent"]),r["casino_original_price"],r["casino_selling_price"],site_id))
            else:
                cur=conn.execute("""INSERT INTO sites(site,country,da,dr,traffic,general_price,casino_price,payment_method,tat,type,link_type,source_file,sheet_name,favorite,created_at,original_price,selling_price,markup_percent,manual_price,casino_original_price,casino_selling_price) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(r["site"],r["country"],r["da"],r["dr"],r["traffic"],sell,r["casino_selling_price"],r["payment_method"],r["tat"],r["type"],r["link_type"],r["source_file"],r["sheet_name"],int(r["favorite"]),r["created_at"],r["original_price"],sell,float(r["markup_percent"]),0,r["casino_original_price"],r["casino_selling_price"])); site_id=cur.lastrowid
            ids.append(int(site_id))
        conn.commit()
    for site_id in ids: sync_one_site_to_cloud(site_id)
    return len(prepared_df)


def _looks_numeric_only(value: str) -> bool:
    value = str(value or "").strip().replace(",", "")
    return bool(re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value))


def safe_unique(df, column):
    if column not in df.columns:
        return ["All"]

    values = df[column].fillna("").astype(str).str.strip()
    values = values[values != ""]

    if column in {
        "country", "payment_method", "link_type",
        "sheet_name", "detected_niche", "type",
    }:
        values = values[~values.map(_looks_numeric_only)]

    if column == "country":
        # Country dropdown should contain readable country/location names only.
        # Reject anything containing digits (e.g. 102.0, 50000, etc.).
        values = values[
            values.str.contains(r"[A-Za-z]", regex=True, na=False)
            & ~values.str.contains(r"\d", regex=True, na=False)
            & values.str.match(r"^[A-Za-zÀ-ÿ .,'()&/-]+$", na=False)
            & (values.str.len() <= 80)
        ]

    elif column == "payment_method":
        allowed_tokens = [
            "after", "upfront", "advance", "negoti",
            "paypal", "bank", "wise", "payoneer",
            "crypto", "usdt", "stripe", "other",
        ]
        values = values[
            values.str.lower().map(
                lambda x: any(token in x for token in allowed_tokens)
            )
        ]

    elif column == "link_type":
        allowed_tokens = [
            "dofollow", "do follow", "nofollow",
            "no follow", "mixed", "sponsored",
        ]
        values = values[
            values.str.lower().map(
                lambda x: any(token in x for token in allowed_tokens)
            )
        ]

    elif column == "sheet_name":
        values = values[values.str.len() <= 120]

    return ["All"] + sorted(
        values.unique().tolist(),
        key=lambda x: x.lower(),
    )


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


def navigate_to(page_name: str) -> None:
    st.session_state["nav_page"] = page_name


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
            "Real Metrics Search",
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
            "Reseller Private Details",
            "Reseller Price Manager",
            "Sheet Structure Scanner",
            "Cloud Sync",
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
        st.button(
            "Search Websites",
            type="primary",
            width="stretch",
            on_click=navigate_to,
            args=("Search Websites",),
            key="dashboard_go_search",
        )
    with action2:
        st.button(
            "Export Results",
            width="stretch",
            on_click=navigate_to,
            args=("Export Results",),
            key="dashboard_go_export",
        )

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

    top_df = df[[c for c in df.columns if c in {"site","country","type","link_type","dr","general_price"}]].copy()
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
        "Fast mode enabled — filters cached hain aur table sirf current page ke rows render karta hai."
    )

    filter_options = get_filter_options(df)

    search = st.text_input(
        "Search website, country, niche or source file",
        placeholder="Paste URL or search: example.com | India | SaaS | technology",
        key="fast_search_query",
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        niche = st.selectbox(
            "🎯 Niche",
            filter_options["niche"],
            key="fast_filter_niche",
        )

    with c2:
        country = st.selectbox(
            "🌍 Country",
            filter_options["country"],
            key="fast_filter_country",
        )

    with c3:
        payment = st.selectbox(
            "💳 Payment",
            filter_options["payment"],
            key="fast_filter_payment",
        )

    with c4:
        link_type = st.selectbox(
            "🔗 Link Type",
            filter_options["link_type"],
            key="fast_filter_link_type",
        )

    with c5:
        sheet = st.selectbox(
            "📄 Sheet",
            filter_options["sheet"],
            key="fast_filter_sheet",
        )

    c6, c7, c8 = st.columns(3)

    with c6:
        min_dr = st.number_input(
            "⭐ Minimum DR",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="fast_filter_min_dr",
        )

    with c7:
        max_price = st.number_input(
            "💰 Maximum General Price",
            min_value=0.0,
            value=100000.0,
            step=1.0,
            key="fast_filter_max_price",
        )

    with c8:
        page_size = st.selectbox(
            "📄 Rows per page",
            [25, 50, 100, 200],
            index=1,
            key="fast_filter_page_size",
        )

    filtered = fast_filter_sites(
        df,
        search,
        niche,
        country,
        payment,
        link_type,
        sheet,
        float(min_dr),
        float(max_price),
    )

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
        key="fast_page_number",
    )

    start_row = (page_number - 1) * page_size
    end_row = min(start_row + page_size, total_results)

    visible_columns = [
        column
        for column in [
            "id", "site", "detected_niche", "country",
            "da", "dr", "traffic", "general_price",
            "casino_price", "payment_method", "tat",
            "type", "link_type", "source_file",
            "sheet_name", "favorite",
        ]
        if column in filtered.columns
    ]

    page_df = filtered.iloc[start_row:end_row][visible_columns]

    i1, i2, i3 = st.columns(3)
    i1.metric("Matching Sites", f"{total_results:,}")
    i2.metric("Current Page", f"{page_number}/{total_pages}")
    i3.metric(
        "Showing",
        f"{start_row + 1 if total_results else 0:,}–{end_row:,}"
    )

    if niche == "All" and not filtered.empty and "detected_niche" in filtered.columns:
        top_niches = filtered["detected_niche"].value_counts().head(8)
        niche_text = "  •  ".join(
            f"{name}: {count:,}" for name, count in top_niches.items()
        )
        st.caption("Auto-detected niches → " + niche_text)

    st.dataframe(
        page_df,
        width="stretch",
        hide_index=True,
        height=520,
    )

    st.markdown("### ⚡ Quick Row Actions")

    if page_df.empty:
        st.caption("Action ke liye current page par website available nahi hai.")
    else:
        action_options = {
            f"{row['site']} | ID {int(row['id'])}": int(row["id"])
            for _, row in page_df.iterrows()
        }

        selected_action_label = st.selectbox(
            "Website select karein",
            list(action_options.keys()),
            key="fast_search_action_site",
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

        a1, a2, a3 = st.columns(3)

        with a1:
            st.link_button(
                "🌐 Open Website",
                selected_url,
                width="stretch",
            )

        with a2:
            is_favorite = bool(selected_action_row.get("favorite", 0))
            favorite_text = "☆ Remove Favorite" if is_favorite else "⭐ Add Favorite"

            if st.button(
                favorite_text,
                width="stretch",
                key="fast_quick_favorite",
            ):
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(
                        "UPDATE sites SET favorite=? WHERE id=?",
                        (0 if is_favorite else 1, selected_action_id),
                    )
                    conn.commit()

                sync_one_site_to_cloud(int(selected_action_id))
                refresh_sites()
                st.success("Favorite status update ho gaya.")
                st.rerun()

        with a3:
            if not st.session_state.admin_logged_in:
                st.button(
                    "🗑️ Delete (Admin Only)",
                    disabled=True,
                    width="stretch",
                    key="fast_delete_disabled",
                )
            else:
                confirm_quick_delete = st.checkbox(
                    "Delete confirm",
                    key="fast_quick_delete_confirm",
                )

                if st.button(
                    "🗑️ Delete Selected",
                    type="primary",
                    width="stretch",
                    disabled=not confirm_quick_delete,
                    key="fast_quick_delete",
                ):
                    with sqlite3.connect(DB_PATH) as conn:
                        conn.execute(
                            "DELETE FROM sites WHERE id=?",
                            (selected_action_id,),
                        )
                        conn.commit()

                    cloud_delete_site(int(selected_action_id))
                    refresh_sites()
                    st.success("Selected website delete ho gayi.")
                    st.rerun()

    export_columns = [
        column for column in df.columns
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
        width="stretch",
    )


# =========================================================
# IMPORT
# =========================================================
elif page == "Import Excel":
    if require_admin():
        st.header("Import Excel or CSV")
        st.caption("Auto-private reseller contacts + default 20% markup + cloud sync.")
        uploaded_file=st.file_uploader("Choose Excel or CSV File",type=["xlsx","xlsm","csv"])
        if uploaded_file is not None:
            try:
                filename=uploaded_file.name; lower=filename.lower(); private_total=0
                sheets=["CSV"] if lower.endswith(".csv") else pd.ExcelFile(uploaded_file).sheet_names
                st.success(f"✅ File loaded: {filename}")
                selected_sheet=st.selectbox("📄 Select Excel Sheet / Tab",sheets)
                scan_sheets=sheets
                for sh in scan_sheets:
                    uploaded_file.seek(0)
                    raw=pd.read_csv(uploaded_file,header=None,dtype=str,on_bad_lines="skip") if sh=="CSV" else pd.read_excel(uploaded_file,sheet_name=sh,header=None,dtype=str)
                    hr=find_header_row(raw); priv=detect_private_rows(raw,hr,filename,sh); private_total += save_private_rows(priv)
                    mapped=""
                    if hr is not None:
                        cols=[clean_value(v) for v in raw.iloc[hr].tolist()]
                        mapped=", ".join(f"{field}→{match_column(cols,aliases)}" for field,aliases in COLUMN_ALIASES.items() if match_column(cols,aliases) is not None)
                    save_structure_report(filename,sh,hr,mapped,len(priv))
                uploaded_file.seek(0)
                raw_df=pd.read_csv(uploaded_file,header=None,dtype=str,on_bad_lines="skip") if selected_sheet=="CSV" else pd.read_excel(uploaded_file,sheet_name=selected_sheet,header=None,dtype=str)
                header_row=find_header_row(raw_df)
                if header_row is None:
                    st.warning("Selected sheet website table nahi lagti; private scan save ho gaya.")
                    st.info(f"🔒 Private rows protected: {private_total}")
                else:
                    uploaded_file.seek(0)
                    imported_df=pd.read_csv(uploaded_file,header=header_row,dtype=str,on_bad_lines="skip") if selected_sheet=="CSV" else pd.read_excel(uploaded_file,sheet_name=selected_sheet,header=header_row,dtype=str)
                    prepared_df=prepare_import_dataframe(imported_df.dropna(how="all"),filename,selected_sheet)
                    a,b,c,d=st.columns(4); a.metric("Sheet",selected_sheet); b.metric("Rows",len(imported_df)); c.metric("Valid",len(prepared_df)); d.metric("Private",private_total)
                    cols=[x for x in ["site","original_price","selling_price","markup_percent","sheet_name"] if x in prepared_df.columns]
                    st.dataframe(prepared_df[cols].head(50),width="stretch",hide_index=True)
                    confirm=st.checkbox("✅ Preview check kar li hai.")
                    if st.button("📥 Import Selected Sheet",type="primary",width="stretch",disabled=not confirm):
                        count=save_imported_sites(prepared_df); refresh_sites(); st.success(f"✅ {count:,} sites save/update • 🔒 {private_total} private rows • 💰 20% markup")
            except Exception as exc: st.error(f"Import error: {type(exc).__name__}: {exc}")



# =========================================================
# ADD

# =========================================================
# LIVE DR CHECKER
# =========================================================
elif page == "Real Metrics Search":
    st.header("Real Metrics Search")
    st.caption(
        "Domain search karein — saved sheet metrics aur available Ahrefs live metrics ek jagah compare honge."
    )

    if not ahrefs_enabled():
        st.error("AHREFS_API_KEY environment variable missing.")
    else:
        metric_query = st.text_input(
            "🌐 Website / Domain",
            placeholder="example.com  |  https://example.com/",
            key="real_metrics_domain_search",
        )

        check_metrics = st.button(
            "🔎 Check Real Metrics",
            type="primary",
            width="stretch",
            key="check_real_metrics",
        )

        if check_metrics:
            domain = normalize_domain(metric_query)

            if not domain:
                st.error("Valid domain likhein.")
            else:
                # Find matching site in current database, if present.
                matched = df[
                    df["site"]
                    .fillna("")
                    .astype(str)
                    .map(normalize_domain)
                    == domain
                ]

                saved_row = matched.iloc[0] if not matched.empty else None
                saved_id = (
                    int(saved_row["id"])
                    if saved_row is not None and "id" in saved_row
                    else None
                )

                saved_da = clean_value(saved_row.get("da", "")) if saved_row is not None else ""
                saved_dr = clean_value(saved_row.get("dr", "")) if saved_row is not None else ""
                saved_traffic = clean_value(saved_row.get("traffic", "")) if saved_row is not None else ""

                st.session_state["metrics_domain"] = domain
                st.session_state["metrics_saved_id"] = saved_id
                st.session_state["metrics_saved_da"] = saved_da
                st.session_state["metrics_saved_dr"] = saved_dr
                st.session_state["metrics_saved_traffic"] = saved_traffic

                # DR is checked independently so it can still work when paid traffic access is unavailable.
                try:
                    with st.spinner(f"Checking live DR for {domain}..."):
                        dr_result = ahrefs_live_dr(domain)
                    st.session_state["metrics_live_dr"] = dr_result.get("dr")
                    st.session_state["metrics_dr_error"] = ""
                    st.session_state["metrics_dr_warning"] = dr_result.get("warning", "")
                except Exception as exc:
                    st.session_state["metrics_live_dr"] = None
                    st.session_state["metrics_dr_error"] = str(exc)
                    st.session_state["metrics_dr_warning"] = ""

                try:
                    with st.spinner(f"Checking Ahrefs organic traffic for {domain}..."):
                        traffic_result = ahrefs_live_traffic(domain)
                    st.session_state["metrics_live_traffic"] = traffic_result.get("organic_traffic")
                    st.session_state["metrics_live_keywords"] = traffic_result.get("organic_keywords")
                    st.session_state["metrics_live_top3"] = traffic_result.get("organic_keywords_top3")
                    st.session_state["metrics_traffic_error"] = ""
                except Exception as exc:
                    st.session_state["metrics_live_traffic"] = None
                    st.session_state["metrics_live_keywords"] = None
                    st.session_state["metrics_live_top3"] = None
                    st.session_state["metrics_traffic_error"] = str(exc)

        domain = st.session_state.get("metrics_domain")
        if domain:
            saved_id = st.session_state.get("metrics_saved_id")
            saved_da = st.session_state.get("metrics_saved_da", "")
            saved_dr = st.session_state.get("metrics_saved_dr", "")
            saved_traffic = st.session_state.get("metrics_saved_traffic", "")
            live_dr = st.session_state.get("metrics_live_dr")
            live_traffic = st.session_state.get("metrics_live_traffic")
            live_keywords = st.session_state.get("metrics_live_keywords")
            live_top3 = st.session_state.get("metrics_live_top3")

            st.markdown(f"### {domain}")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric(
                "Live Ahrefs DR",
                f"{float(live_dr):.1f}" if live_dr is not None else "-"
            )
            m2.metric(
                "Live Organic Traffic",
                f"{int(live_traffic):,}" if live_traffic is not None else "-"
            )
            m3.metric(
                "Organic Keywords",
                f"{int(live_keywords):,}" if live_keywords is not None else "-"
            )
            m4.metric(
                "Top-3 Keywords",
                f"{int(live_top3):,}" if live_top3 is not None else "-"
            )

            st.markdown("#### Saved / Sheet Metrics")
            s1, s2, s3 = st.columns(3)
            s1.metric("Saved DA", saved_da or "-")
            s2.metric("Saved DR", saved_dr or "-")
            s3.metric("Saved Traffic", saved_traffic or "-")

            st.caption(
                "DA is a Moz metric. Moz API connected nahi hai, isliye DA yahan sheet/database value hi show hoti hai. "
                "Live DR aur organic traffic Ahrefs se aate hain."
            )

            dr_error = st.session_state.get("metrics_dr_error", "")
            traffic_error = st.session_state.get("metrics_traffic_error", "")
            dr_warning = st.session_state.get("metrics_dr_warning", "")

            if dr_warning:
                st.warning(dr_warning)

            if dr_error:
                st.error(f"DR: {dr_error}")

            if traffic_error:
                st.warning(
                    "Traffic live fetch nahi hua. " + traffic_error
                    + " Saved Traffic upar compare ke liye available hai."
                )

            if saved_id is not None and st.session_state.get("admin_logged_in", False):
                st.markdown("#### Save Verified Metrics")
                b1, b2 = st.columns(2)

                with b1:
                    if st.button(
                        "💾 Save Live DR",
                        width="stretch",
                        disabled=live_dr is None,
                        key="save_real_live_dr",
                    ):
                        save_live_dr(saved_id, live_dr)
                        refresh_sites()
                        st.success("Live Ahrefs DR local + cloud me save ho gaya.")

                with b2:
                    if st.button(
                        "💾 Save Live Traffic",
                        width="stretch",
                        disabled=live_traffic is None,
                        key="save_real_live_traffic",
                    ):
                        save_live_traffic(saved_id, live_traffic)
                        refresh_sites()
                        st.success("Live organic traffic local + cloud me save ho gaya.")

            elif saved_id is None:
                st.info(
                    "Ye domain current GP Site Finder database me nahi mila. Live metrics dekh sakte hain, "
                    "lekin save karne ke liye pehle site database me add karein."
                )

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
        width="stretch",
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
            width="stretch",
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
        width="stretch",
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

            submitted = st.form_submit_button("Save Website", type="primary", width="stretch")

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

                save = st.form_submit_button("💾 Save Changes", type="primary", width="stretch")

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
                    sync_one_site_to_cloud(int(selected_id))
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
                save_contact = st.form_submit_button("Save Outreach Contact", type="primary", width="stretch")
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
                width="stretch",
                disabled=not confirm,
            ):
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("DELETE FROM sites WHERE id=?", (selected_id,))
                    conn.commit()
                cloud_delete_site(int(selected_id))
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
        if st.button(button_text, width="stretch"):
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
    st.dataframe(favorites, width="stretch", hide_index=True, height=580)


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
                save_contact = st.form_submit_button("💾 Save Contact", type="primary", width="stretch")

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
        st.dataframe(contacts_df, width="stretch", hide_index=True, height=400)


# =========================================================
# RESELLER PRIVATE DETAILS
# =========================================================
elif page == "Reseller Private Details":
    if require_admin():
        st.header("Reseller Private Details")
        srcs=safe_unique(df,"source_file"); selected=st.selectbox("Source / Reseller File",srcs)
        if selected!="All":
            pdf=pd.DataFrame()
            if cloud_enabled():
                try: pdf=cloud_fetch("reseller_private","*","source_file=eq."+urllib.parse.quote(selected,safe=""))
                except Exception: pass
            if pdf.empty:
                with sqlite3.connect(RESELLER_PRIVATE_DB_PATH) as conn: pdf=pd.read_sql_query("SELECT * FROM reseller_private WHERE source_file=? ORDER BY sheet_name,id",conn,params=(selected,))
            if pdf.empty: st.warning("Private details nahi milin.")
            else:
                for i,r in pdf.iterrows():
                    value=clean_value(r.get("field_value","")); st.markdown(f"**{clean_value(r.get('sheet_name',''))} — {clean_value(r.get('field_name',''))}**"); st.code(value,language=None)
                    m=re.search(r"\+?\d[\d\s().-]{7,}\d",value)
                    if m: st.link_button("🟢 WhatsApp",whatsapp_url(m.group()),width="stretch")

# =========================================================
# RESELLER PRICE MANAGER
# =========================================================
elif page == "Reseller Price Manager":
    if require_admin():
        st.header("Reseller Price Manager")
        selected_id,row=site_selector(df,"Website select karein")
        if row is not None:
            original=clean_value(row.get("original_price",row.get("general_price",""))); selling=clean_value(row.get("selling_price",row.get("general_price",""))); markup=float(row.get("markup_percent",DEFAULT_RESELLER_MARKUP) or DEFAULT_RESELLER_MARKUP); manual=bool(row.get("manual_price",False))
            a,b,c,d=st.columns(4); a.metric("Original Price",original or "-"); b.metric("Markup",f"{markup:.1f}%"); c.metric("Selling Price",selling or "-"); d.metric("Mode","Manual" if manual else "Auto")
            mp=st.number_input("Manual Selling Price",min_value=0.0,value=float(parse_price(selling) or 0),step=1.0)
            c1,c2=st.columns(2)
            with c1:
                if st.button("Save Manual Price",type="primary",width="stretch"):
                    with sqlite3.connect(DB_PATH) as conn: conn.execute("UPDATE sites SET selling_price=?,general_price=?,manual_price=1 WHERE id=?",(f"{mp:.2f}",f"{mp:.2f}",int(selected_id))); conn.commit()
                    sync_one_site_to_cloud(int(selected_id)); refresh_sites(); st.rerun()
            with c2:
                if st.button("Reset to Auto Markup",width="stretch"):
                    on=parse_price(original); auto=f"{on*(1+markup/100.0):.2f}" if on is not None else original
                    with sqlite3.connect(DB_PATH) as conn: conn.execute("UPDATE sites SET selling_price=?,general_price=?,manual_price=0 WHERE id=?",(auto,auto,int(selected_id))); conn.commit()
                    sync_one_site_to_cloud(int(selected_id)); refresh_sites(); st.rerun()
            nm=st.number_input("Entire Sheet Markup %",min_value=0.0,max_value=500.0,value=markup,step=1.0)
            if st.button("Apply Markup to Entire Sheet",width="stretch"): set_sheet_markup(clean_value(row.get("source_file","")),clean_value(row.get("sheet_name","")),nm); refresh_sites(); st.rerun()

# =========================================================
# SHEET STRUCTURE SCANNER
# =========================================================
elif page == "Sheet Structure Scanner":
    if require_admin():
        st.header("Sheet Structure Scanner")
        sdf=pd.DataFrame()
        if cloud_enabled():
            try: sdf=cloud_fetch("sheet_structure")
            except Exception: pass
        if sdf.empty:
            with sqlite3.connect(SHEET_STRUCTURE_DB_PATH) as conn: sdf=pd.read_sql_query("SELECT * FROM sheet_structure ORDER BY updated_at DESC",conn)
        st.dataframe(sdf,width="stretch",hide_index=True,height=620) if not sdf.empty else st.info("No structure reports yet.")

# =========================================================
# CLOUD SYNC
# =========================================================
elif page == "Cloud Sync":
    if require_admin():
        st.header("Cloud Sync")
        st.caption("Desktop ↔ Supabase ↔ Streamlit central database")

        if not cloud_enabled():
            st.error("Supabase connection settings missing.")
        else:
            st.success("✅ Supabase configured")

            if st.button("Test Cloud Connection", width="stretch"):
                try:
                    st.success(f"Cloud rows: {len(load_cloud_sites()):,}")
                except Exception as exc:
                    st.error(str(exc))

            st.warning("Initial sync local gp_sites ko cloud gp_sites me replace karega.")
            ok = st.checkbox("I confirm initial local → cloud sync")

            if st.button(
                "☁️ Sync Local Sites to Supabase",
                type="primary",
                width="stretch",
                disabled=not ok,
            ):
                try:
                    progress = st.progress(0)
                    status = st.empty()

                    def update_progress(done, total):
                        pct = int((done / total) * 100) if total else 100
                        progress.progress(min(pct, 100))
                        status.info(f"Uploading: {done:,} / {total:,} sites ({pct}%)")

                    with st.spinner("Fast batch sync chal rahi hai..."):
                        count = fast_sync_local_sites_to_cloud(
                            progress_callback=update_progress,
                            batch_size=250,
                        )

                    progress.progress(100)
                    status.success(f"✅ Sites complete: {count:,}")

                    # These are much smaller tables, so sync them after sites.
                    try:
                        private_count = sync_reseller_private_to_cloud()
                    except Exception:
                        private_count = 0
                    try:
                        settings_count = sync_reseller_settings_to_cloud()
                    except Exception:
                        settings_count = 0

                    refresh_sites()
                    st.success(
                        f"✅ Cloud sync complete — {count:,} sites, "
                        f"{private_count:,} private rows, {settings_count:,} reseller settings."
                    )
                except Exception as exc:
                    st.error(f"Sync error: {type(exc).__name__}: {exc}")

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
                width="stretch",
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
                width="stretch",
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
                    width="stretch",
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
                width="stretch",
            ):
                delete_admin_private_contact(int(selected["id"]))
                st.success("Private contact delete ho gaya.")
                st.rerun()

            st.download_button(
                "Download Private Contacts CSV",
                vault_df.to_csv(index=False).encode("utf-8-sig"),
                "gp_site_finder_admin_private_contacts.csv",
                "text/csv",
                width="stretch",
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
                width="stretch",
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
            width="stretch",
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
            width="stretch",
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
            width="stretch",
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
            width="stretch",
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
                width="stretch",
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
        width="stretch",
    )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Sites")
    st.download_button(
        "📗 Download All Sites as Excel",
        excel_buffer.getvalue(),
        "gp_site_finder_all_sites.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
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
                                    width="stretch",
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
                                    width="stretch",
                                )

                        with button_columns[1]:
                            if website_value:
                                st.link_button(
                                    "Website",
                                    normalize_public_url(
                                        website_value
                                    ),
                                    width="stretch",
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
                    width="stretch",
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
                        width="stretch",
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
                    width="stretch",
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
                width="stretch",
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
                width="stretch",
            )

        if profile_settings.get("website"):
            st.link_button(
                "Visit Website",
                normalize_public_url(
                    profile_settings["website"]
                ),
                width="stretch",
            )

        if profile_settings.get("linkedin"):
            st.link_button(
                "LinkedIn Profile",
                normalize_public_url(
                    profile_settings["linkedin"]
                ),
                width="stretch",
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
                width="stretch",
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
                    width="stretch",
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
                    width="stretch",
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
                width="stretch",
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
                width="stretch",
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
                width="stretch",
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
                width="stretch",
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
        if st.button("🔒 Logout", width="stretch"):
            st.session_state.admin_logged_in = False
            st.rerun()
    else:
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password")

        if st.button("🔓 Login", type="primary", width="stretch"):
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
            width="stretch",
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
            width="stretch",
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
    st.write(f"Supabase Live Sync: `{'ON' if cloud_enabled() else 'OFF'}`")
    st.write("Startup mode: `FAST LOCAL-FIRST`")
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
                    width="stretch",
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
                    width="stretch",
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
                    width="stretch",
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
                    width="stretch",
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
                    width="stretch",
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
