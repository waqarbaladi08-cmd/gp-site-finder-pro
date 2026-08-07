import hashlib
import io
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

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
TEAM_IMAGES_DIR = BASE_DIR / "assets" / "team"
PROFILE_IMAGE_PATH = BASE_DIR / "assets" / "aaquib_profile.png"
HERO_IMAGE_PATH = BASE_DIR / "assets" / "dashboard_hero.png"
PROFILE_DATA_PATH = BASE_DIR / "database" / "profile_settings.json"
LINKEDIN_URL = "https://www.linkedin.com/in/aaquib-seo/"


# =========================================================
# STYLING
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0');

    :root {
        --ink: #101828;
        --muted: #667085;
        --page: #EDEBE7;
        --card: #F7F4EE;
        --line: #D7D0C5;
        --sidebar: #17151C;
        --sidebar-2: #231F2B;
        --accent: #5E3B76;
        --accent-2: #8A5A44;
        --teal: #2A7F78;
        --gold: #B8893C;
        --soft-purple: #E9E0EE;
        --soft-teal: #DDEDEA;
    }

    html, body, [class*="css"] {
        font-family: "DM Sans", sans-serif;
    }

    h1, h2, h3, .main-title, .metric-value {
        font-family: "Manrope", sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 92% 4%, rgba(94,59,118,.10), transparent 23rem),
            radial-gradient(circle at 76% 18%, rgba(42,127,120,.08), transparent 18rem),
            var(--page);
        color: var(--ink);
    }

    .block-container {
        max-width: 1440px;
        padding-top: 1.15rem;
        padding-bottom: 2.5rem;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, var(--sidebar) 0%, var(--sidebar-2) 100%);
        border-right: 1px solid rgba(255,255,255,.06);
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1.1rem;
    }

    [data-testid="stSidebar"] * {
        color: #F9FAFB;
    }

    [data-testid="stSidebar"] img {
        width: 112px !important;
        height: 112px !important;
        object-fit: cover !important;
        object-position: 50% 18% !important;
        border-radius: 24px !important;
        margin: 0 auto 12px auto !important;
        display: block !important;
        border: 1px solid rgba(255,255,255,.14);
        box-shadow: 0 18px 38px rgba(0,0,0,.28);
        background: #242A38;
    }

    .profile-card {
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 18px;
        padding: 14px 12px;
        margin: 0 0 14px 0;
        text-align: center;
        backdrop-filter: blur(12px);
    }

    .profile-name {
        font-family: "Manrope", sans-serif;
        font-size: 16px;
        font-weight: 800;
        margin: 3px 0;
        color: #FFFFFF;
    }

    .profile-role {
        color: #AEB7C8;
        font-size: 11px;
        line-height: 1.5;
        margin-bottom: 2px;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        position: relative;
        border-radius: 12px;
        padding: 8px 10px 8px 38px;
        margin: 2px 0;
        transition: all .18s ease;
        font-size: 13px;
        font-weight: 600;
        color: #D0D5DD;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255,255,255,.07);
        color: #FFFFFF;
        transform: translateX(2px);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(94,59,118,.97), rgba(138,90,68,.94));
        color: #FFFFFF;
        box-shadow: 0 8px 22px rgba(94,59,118,.26);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label::before {
        font-family: "Material Symbols Rounded";
        position: absolute;
        left: 12px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 19px;
        color: #AEB7C8;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked)::before {
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1)::before {content:"dashboard";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2)::before {content:"search";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3)::before {content:"upload_file";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4)::before {content:"add_circle";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5)::before {content:"edit_square";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6)::before {content:"delete";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(7)::before {content:"star";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(8)::before {content:"contacts";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(9)::before {content:"monitoring";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(10)::before {content:"content_copy";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(11)::before {content:"download";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(12)::before {content:"badge";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(13)::before {content:"lock";}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(14)::before {content:"settings";}

    .brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--soft-purple);
        color: #5546D7;
        border: 1px solid #E2DEFF;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .07em;
        margin-bottom: 10px;
    }

    .main-title {
        color: var(--ink);
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -.035em;
        margin: 0;
        line-height: 1.15;
    }

    .subtitle {
        color: var(--muted);
        font-size: 14px;
        margin: 7px 0 18px 0;
    }

    .brand-strip {
        display: none;
    }

    .hero-shell {
        display: grid;
        grid-template-columns: 1.12fr .88fr;
        gap: 24px;
        align-items: center;
        background:
            linear-gradient(135deg, #151827 0%, #24213D 58%, #312E60 100%);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 24px;
        padding: 28px;
        margin: 4px 0 22px 0;
        box-shadow: 0 24px 60px rgba(16,24,40,.14);
        overflow: hidden;
        position: relative;
    }

    .hero-shell::after {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        right: -90px;
        top: -100px;
        border-radius: 50%;
        background: rgba(109,93,251,.25);
        filter: blur(2px);
    }

    .hero-copy {
        position: relative;
        z-index: 2;
    }

    .hero-kicker {
        color: #B9B2FF;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        font-family: "Manrope", sans-serif;
        color: white;
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -.03em;
        line-height: 1.18;
        margin-bottom: 12px;
    }

    .hero-text {
        color: #C8CFDC;
        font-size: 14px;
        line-height: 1.7;
        max-width: 610px;
    }

    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 18px;
    }

    .hero-pill {
        color: #EEF2FF;
        background: rgba(255,255,255,.08);
        border: 1px solid rgba(255,255,255,.11);
        border-radius: 999px;
        padding: 7px 10px;
        font-size: 11px;
        font-weight: 600;
    }

    .hero-visual {
        position: relative;
        z-index: 2;
        min-height: 210px;
        background: linear-gradient(145deg, #EAE4DC, #DCD2C7);
        border: 1px solid rgba(255,255,255,.28);
        border-radius: 18px;
        padding: 15px;
        box-shadow: 0 22px 50px rgba(0,0,0,.22);
        transform: rotate(-1.2deg);
    }

    .mini-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 13px;
    }

    .mini-dots {display:flex; gap:5px;}
    .mini-dots span {
        width: 7px; height: 7px; border-radius:50%; background:#D0D5DD;
    }

    .mini-chip {
        width: 54px; height: 8px; border-radius:99px; background:#DCCFE4;
    }

    .mini-stats {
        display:grid;
        grid-template-columns: repeat(3,1fr);
        gap:9px;
        margin-bottom:12px;
    }

    .mini-stat {
        background:#EDE8E0;
        border:1px solid #EAECF0;
        border-radius:11px;
        padding:10px;
    }

    .mini-stat b {
        display:block;
        font-size:14px;
        color:#2A2430;
        margin-top:6px;
    }

    .mini-stat i {
        display:block;
        width:18px; height:18px; border-radius:6px;
        background:linear-gradient(135deg,#5E3B76,#8A5A44);
    }

    .mini-table {
        display:grid;
        gap:7px;
    }

    .mini-row {
        height:26px;
        border-radius:8px;
        background:
            linear-gradient(90deg,#EEF2F6 0 28%,transparent 28% 31%,#F3F4F6 31% 52%,transparent 52% 55%,#F3F4F6 55% 72%,transparent 72% 75%,#EDE9FE 75% 100%);
    }

    .section-title {
        display:flex;
        align-items:center;
        gap:10px;
        font-family:"Manrope", sans-serif;
        font-size:20px;
        font-weight:800;
        color:var(--ink);
        margin:22px 0 12px;
    }

    .section-icon {
        width:34px;
        height:34px;
        border-radius:10px;
        display:grid;
        place-items:center;
        background:#E7DCEB;
        color:#5E3B76;
    }

    .section-icon .material-symbols-rounded {
        font-size:20px;
    }

    .metric-card {
        background: linear-gradient(145deg, #F7F4EE, #EEE9E1);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 28px rgba(16,24,40,.055);
        min-height: 130px;
        transition: transform .18s ease, box-shadow .18s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 34px rgba(16,24,40,.09);
    }

    .metric-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display:grid;
        place-items:center;
        background: var(--soft-purple);
        color: #5B4FE5;
        margin-bottom: 14px;
    }

    .metric-icon.teal {background:#D8E8E5; color:#2A7F78;}
    .metric-icon.gold {background:#ECE1CC; color:#9A6F22;}
    .metric-icon .material-symbols-rounded {font-size:22px;}
    .metric-icon.plum {background:#E7DCEB; color:#5E3B76;}
    .metric-icon.copper {background:#E8D8CF; color:#8A5A44;}
    .metric-icon.sage {background:#DDE7DB; color:#58705A;}
    .metric-icon.slate {background:#DDE2E8; color:#4B5563;}

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #F7F4EE, #EEE9E1);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 8px 24px rgba(36,30,38,.05);
    }

    [data-testid="stDataFrame"] canvas {
        background: #F7F4EE !important;
    }


    .metric-label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .metric-value {
        font-size: 25px;
        font-weight: 800;
        color: var(--ink);
        letter-spacing: -.02em;
    }

    div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: 12px;
        border-color: var(--line);
        background: #F7F4EE;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stLinkButton > a {
        border-radius: 12px !important;
        font-weight: 700 !important;
        min-height: 42px;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #5E3B76, #8A5A44);
        border: 0;
        box-shadow: 0 9px 20px rgba(94,59,118,.24);
    }

    [data-testid="stDataFrame"] {
        overflow-x: auto;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: #F7F4EE;
        box-shadow: 0 8px 24px rgba(16,24,40,.045);
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: .75rem;
            padding-right: .75rem;
            padding-top: .7rem;
        }

        .main-title {font-size: 28px;}
        .subtitle {font-size: 13px;}
        .hero-shell {
            grid-template-columns:1fr;
            padding:20px;
            border-radius:20px;
        }
        .hero-title {font-size:24px;}
        .hero-visual {min-height:180px;}
        .metric-card {min-height:auto; padding:14px; margin-bottom:8px;}

        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: .45rem !important;
        }

        button[kind="primary"],
        button[kind="secondary"] {
            width: 100%;
        }

        [data-testid="stDataFrame"] {font-size:12px;}
    }

    .team-intro {
        background: linear-gradient(135deg, #201C28, #362D3E);
        color: #F7F2EA;
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 22px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 18px 42px rgba(26,21,31,.14);
    }

    .team-intro h2 {
        color: #FFFFFF;
        margin: 0 0 8px 0;
    }

    .team-intro p {
        color: #CFC6D5;
        margin: 0;
        max-width: 760px;
        line-height: 1.65;
    }

    .team-card {
        background: linear-gradient(145deg, #F7F4EE, #ECE6DE);
        border: 1px solid #D7D0C5;
        border-radius: 18px;
        padding: 16px;
        min-height: 250px;
        box-shadow: 0 10px 28px rgba(27,22,30,.07);
        margin-bottom: 12px;
    }

    .team-card-name {
        font-family: "Manrope", sans-serif;
        color: #25202A;
        font-size: 17px;
        font-weight: 800;
        margin-top: 8px;
    }

    .team-card-role {
        color: #5E3B76;
        font-size: 12px;
        font-weight: 750;
        margin: 3px 0 8px;
    }

    .team-card-meta {
        color: #6F6672;
        font-size: 11px;
        line-height: 1.55;
    }

    .team-card-bio {
        color: #514A54;
        font-size: 12px;
        line-height: 1.55;
        margin-top: 10px;
    }

    .team-level-badge {
        display: inline-block;
        background: #E7DCEB;
        color: #5E3B76;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: .04em;
        text-transform: uppercase;
    }



    /* Final usability improvements */
    [data-testid="stSidebar"] [role="radiogroup"] label {
        font-size: 14px !important;
        min-height: 42px;
        padding-top: 9px !important;
        padding-bottom: 9px !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label::before {
        font-size: 21px !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1)::before {color:#A78BFA;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2)::before {color:#38BDF8;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3)::before {color:#34D399;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4)::before {color:#FBBF24;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5)::before {color:#FB7185;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6)::before {color:#F87171;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(7)::before {color:#FACC15;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(8)::before {color:#2DD4BF;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(9)::before {color:#60A5FA;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(10)::before {color:#C084FC;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(11)::before {color:#4ADE80;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(12)::before {color:#F59E0B;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(13)::before {color:#22D3EE;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(14)::before {color:#A78BFA;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(15)::before {color:#FB7185;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(16)::before {color:#94A3B8;}

    h1 {font-size: 2.25rem !important;}
    h2 {font-size: 1.75rem !important;}
    h3 {font-size: 1.28rem !important;}

    .hero-live-sites {
        display: grid;
        gap: 8px;
        margin-top: 8px;
    }

    .hero-site-row {
        display: grid;
        grid-template-columns: 1.5fr .6fr .6fr .7fr;
        gap: 8px;
        align-items: center;
        background: rgba(255,255,255,.72);
        border: 1px solid rgba(255,255,255,.55);
        border-radius: 9px;
        padding: 8px 10px;
        color: #2B2530;
        font-size: 11px;
        font-weight: 650;
    }

    .hero-site-name {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .contact-card {
        background: linear-gradient(145deg, #F7F4EE, #ECE6DE);
        border: 1px solid #D7D0C5;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 28px rgba(27,22,30,.07);
    }

    .whatsapp-button {
        display: block;
        text-align: center;
        background: linear-gradient(135deg, #16A34A, #22C55E);
        color: #FFFFFF !important;
        padding: 12px 16px;
        border-radius: 12px;
        font-weight: 800;
        text-decoration: none !important;
        margin: 8px 0;
        box-shadow: 0 8px 18px rgba(34,197,94,.22);
    }

    .contact-detail {
        padding: 9px 0;
        border-bottom: 1px solid #D7D0C5;
        color: #4B4550;
        font-size: 13px;
    }

    @media (max-width:768px) {
        .hero-site-row {
            grid-template-columns: 1.5fr .5fr .5fr;
        }
        .hero-site-row span:last-child {display:none;}
    }


    /* ===== Final Premium UI ===== */
    .main-title {
        font-size: 40px !important;
        letter-spacing: -.035em !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        font-size: 14.5px !important;
        font-weight: 650 !important;
        min-height: 43px;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label::before {
        font-size: 21px !important;
    }

    /* premium multicolor icon system */
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1)::before {color:#A78BFA;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2)::before {color:#38BDF8;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3)::before {color:#34D399;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4)::before {color:#FBBF24;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5)::before {color:#FB7185;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6)::before {color:#F87171;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(7)::before {color:#FACC15;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(8)::before {color:#2DD4BF;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(9)::before {color:#60A5FA;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(10)::before {color:#C084FC;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(11)::before {color:#4ADE80;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(12)::before {color:#F59E0B;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(13)::before {color:#22D3EE;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(14)::before {color:#A78BFA;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(15)::before {color:#FB7185;}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(16)::before {color:#94A3B8;}

    .hero-photo-shell {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,.13);
        box-shadow: 0 22px 52px rgba(0,0,0,.28);
        min-height: 245px;
        background: linear-gradient(145deg,#262130,#17151C);
    }

    .hero-photo-shell img {
        width:100%;
        height:245px;
        object-fit:cover;
        display:block;
    }

    .chart-card {
        background: linear-gradient(145deg,#F7F4EE,#EEE7DE);
        border:1px solid #D7D0C5;
        border-radius:18px;
        padding:14px 16px 8px;
        box-shadow:0 10px 28px rgba(27,22,30,.06);
        margin-bottom:12px;
    }

    .chart-card-title {
        font-family:"Manrope",sans-serif;
        color:#2B2530;
        font-size:14px;
        font-weight:800;
        margin-bottom:4px;
    }

    .chart-card-caption {
        color:#756C78;
        font-size:11px;
        margin-bottom:8px;
    }

    .wa-float {
        position:fixed;
        right:22px;
        bottom:22px;
        z-index:9999;
        width:58px;
        height:58px;
        border-radius:50%;
        display:flex;
        align-items:center;
        justify-content:center;
        text-decoration:none !important;
        background:linear-gradient(135deg,#16A34A,#22C55E);
        box-shadow:0 12px 28px rgba(34,197,94,.35);
        border:2px solid rgba(255,255,255,.88);
        transition:transform .18s ease;
    }

    .wa-float:hover {transform:translateY(-3px) scale(1.04);}

    .wa-float svg {
        width:30px;
        height:30px;
        fill:#fff;
    }

    .wa-direct {
        display:flex;
        align-items:center;
        justify-content:center;
        gap:9px;
        padding:12px 16px;
        border-radius:12px;
        background:linear-gradient(135deg,#16A34A,#22C55E);
        color:#fff !important;
        font-weight:800;
        text-decoration:none !important;
        box-shadow:0 9px 20px rgba(34,197,94,.22);
        margin:8px 0;
    }

    @media(max-width:768px){
        .main-title {font-size:29px !important;}
        .wa-float {right:14px; bottom:14px; width:52px; height:52px;}
        .hero-photo-shell img {height:205px;}
        .hero-photo-shell {min-height:205px;}
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
    st.warning("🔐 Is page ke liye Admin Login zaroori hai.")
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
    if PROFILE_IMAGE_PATH.exists():
        st.image(str(PROFILE_IMAGE_PATH), width=150)

    st.markdown(
        f"""
        <div class="profile-card">
            <div class="profile-role" style="letter-spacing:.08em; text-transform:uppercase;">
                {profile_settings.get("brand_name", "Aaquib Digital Solutions")}
            </div>
            <div class="profile-name">{profile_settings["name"]}</div>
            <div class="profile-role">{profile_settings["role"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if profile_settings.get("linkedin"):
        st.link_button(
            "in  View LinkedIn Profile",
            normalize_public_url(profile_settings["linkedin"]),
            use_container_width=True,
        )

    st.markdown("## GP Site Finder")
    st.caption("Workspace & outreach intelligence")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Search Websites",
            "Import Excel",
            "Add New Site",
            "Edit Site",
            "Delete Site",
            "Favorites",
            "Private Contacts",
            "Statistics",
            "Duplicate Finder",
            "Export Results",
            "Our Team",
            "Contact Us",
            "My Profile / Contact",
            "Admin Login",
            "Settings",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    if st.session_state.admin_logged_in:
        st.success("🔓 Admin Logged In")
    else:
        st.caption("🔒 Admin Locked")
    st.caption("GP Site Finder Pro Web")


# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<span class="brand-badge">AAQUB DIGITAL SOLUTIONS</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="main-title">Aaquib Digital Solutions</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">GP Site Finder Pro — Search, filter and manage guest-post websites</p>',
    unsafe_allow_html=True,
)



# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":
    hero_sites = df.head(4).copy()
    hero_rows_html = ""

    for _, hero_row in hero_sites.iterrows():
        site_name = str(hero_row.get("site", "") or "")
        dr_value = str(hero_row.get("dr", "") or "-")
        da_value = str(hero_row.get("da", "") or "-")
        price_value = str(
            hero_row.get("general_price", "") or "-"
        )

        hero_rows_html += (
            '<div class="hero-site-row">'
            f'<span class="hero-site-name">{site_name}</span>'
            f'<span>DR {dr_value}</span>'
            f'<span>DA {da_value}</span>'
            f'<span>${price_value}</span>'
            '</div>'
        )

    if HERO_IMAGE_PATH.exists():
        hero_visual_html = f"""
        <div class="hero-photo-shell">
            <img src="data:image/png;base64,{__import__('base64').b64encode(HERO_IMAGE_PATH.read_bytes()).decode('ascii')}" alt="Guest Posting Workspace">
        </div>
        """
    else:
        hero_visual_html = f"""
        <div class="hero-visual">
            <div class="mini-top">
                <div class="mini-dots"><span></span><span></span><span></span></div>
                <div class="mini-chip"></div>
            </div>
            <div class="mini-stats">
                <div class="mini-stat"><i></i><b>{len(df):,}</b></div>
                <div class="mini-stat"><i></i><b>{df["country"].fillna("").replace("", pd.NA).dropna().nunique():,}</b></div>
                <div class="mini-stat"><i></i><b>Live</b></div>
            </div>
            <div class="hero-live-sites">
                {hero_rows_html}
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-copy">
                <div class="hero-kicker">Aaquib Digital Solutions</div>
                <div class="hero-title">Turn website research into a faster, cleaner outreach workflow.</div>
                <div class="hero-text">
                    Search thousands of guest-post opportunities, manage private contacts,
                    remove duplicates and export campaign-ready lists from one premium workspace.
                </div>
                <div class="hero-pills">
                    <span class="hero-pill">Fast Search</span>
                    <span class="hero-pill">Smart Filters</span>
                    <span class="hero-pill">Private CRM</span>
                    <span class="hero-pill">Excel Import</span>
                </div>
            </div>
            {hero_visual_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_sites = len(df)
    total_countries = (
        df["country"].fillna("").astype(str).str.strip().replace("", pd.NA).dropna().nunique()
        if "country" in df.columns else 0
    )
    dr_values = pd.to_numeric(df.get("dr", pd.Series(dtype=float)), errors="coerce")
    price_values = pd.to_numeric(df.get("general_price", pd.Series(dtype=float)), errors="coerce")
    average_dr = 0 if pd.isna(dr_values.mean()) else dr_values.mean()
    average_price = 0 if pd.isna(price_values.mean()) else price_values.mean()

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("language", "plum", "Total Websites", f"{total_sites:,}"),
        ("public", "teal", "Countries", f"{total_countries:,}"),
        ("query_stats", "sage", "Average DR", f"{average_dr:.1f}"),
        ("payments", "copper", "Average Price", f"${average_price:.2f}"),
    ]

    for col, (icon, tone, label, value) in zip(
        [c1, c2, c3, c4],
        cards,
    ):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon {tone}">
                        <span class="material-symbols-rounded">{icon}</span>
                    </div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="section-title">
            <div class="section-icon">
                <span class="material-symbols-rounded">table_view</span>
            </div>
            Recent Websites
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = [c for c in [
        "site","country","da","dr","traffic","general_price",
        "payment_method","link_type","sheet_name"
    ] if c in df.columns]
    st.dataframe(df[columns].head(30), use_container_width=True, hide_index=True, height=560)


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
elif page == "Add New Site":
    if require_admin():
        st.header("Add New Site")
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            with c1:
                site = st.text_input("🌐 Website*")
                country = st.text_input("🌍 Country")
                da = st.text_input("📈 DA")
                dr = st.text_input("⭐ DR")
                traffic = st.text_input("📊 Traffic")
                general_price = st.text_input("💰 General Price")
            with c2:
                casino_price = st.text_input("🎰 Casino Price")
                payment_method = st.selectbox("💳 Payment", ["", "Upfront", "After", "50% Advance", "Negotiable"])
                tat = st.text_input("⏱️ TAT")
                site_type = st.text_input("📁 Type/Niche")
                link_type = st.selectbox("🔗 Link Type", ["", "Dofollow", "Nofollow", "Mixed"])
                sheet_name = st.text_input("📄 Sheet Name", value="Added Sites")

            submitted = st.form_submit_button("💾 Save New Site", type="primary", use_container_width=True)

        if submitted:
            domain = normalize_domain(site)
            if not domain:
                st.error("Valid website/domain likhein.")
            else:
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
                            payment_method,tat,site_type,link_type,"Web App",
                            sheet_name or "Added Sites",0,
                            datetime.now().isoformat(timespec="seconds"),
                        ),
                    )
                    conn.commit()
                refresh_sites()
                st.success("✅ New site save ho gayi.")
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
# SETTINGS
# =========================================================
elif page == "Settings":
    st.header("Settings")
    st.caption("Profile, WhatsApp, email, website aur LinkedIn yahan manage karein.")
    st.write(f"Database path: `{DB_PATH}`")
    st.write(f"Private contacts DB: `{CONTACT_DB_PATH}`")
    st.write(f"Contact Us inbox DB: `{CONTACT_US_DB_PATH}`")
    st.write(f"Team profiles DB: `{TEAM_DB_PATH}`")
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
