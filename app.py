import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import base64
import re

# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GSHEET_ID = os.getenv("GSHEET_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

# =====================================================
# KONFIGURASI STREAMLIT
# =====================================================
st.set_page_config(
    page_title="Chatbot BMKG Teluk Bayur",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# FUNGSI ENCODE GAMBAR KE BASE64
# =====================================================
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

LOGO_B64   = get_image_base64("assets/logo_BMKG.png")
AVATAR_B64 = get_image_base64("assets/Avatar.png")
BG_B64     = get_image_base64("assets/background.png")

# =====================================================
# CUSTOM CSS
# =====================================================
bg_css = (
    f"background-image: url('data:image/png;base64,{BG_B64}'); "
    "background-size: cover; background-position: center; background-attachment: fixed;"
    if BG_B64
    else "background: linear-gradient(160deg, #d4e8f7 0%, #b8d9f0 40%, #a0c4e8 100%);"
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"], .main, .stApp {{
    height: 100% !important;
    min-height: 100vh !important;
    {bg_css}
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

/* ── Hide Streamlit chrome ── */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu, footer,
[data-testid="stSidebarNav"] {{ display: none !important; visibility: hidden !important; }}

[data-testid="stAppViewContainer"] > .main > .block-container {{
    padding: 0 0 120px 0 !important;
    max-width: 700px !important;
    width: 100% !important;
    margin: 0 auto !important;
}}

/* =====================================================
   APP WRAPPER
   ===================================================== */
.app-wrapper {{
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    width: 100%;
    position: relative;
}}

/* =====================================================
   HEADER
   ===================================================== */
.chat-header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999;
    background: linear-gradient(135deg,
        rgba(8, 28, 58, 0.97) 0%,
        rgba(15, 52, 96, 0.97) 50%,
        rgba(22, 74, 114, 0.95) 100%);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    padding: clamp(10px, 1.5vw, 18px) clamp(20px, 4vw, 52px);
    display: flex;
    align-items: center;
    gap: clamp(14px, 2vw, 24px);
    box-shadow: 0 4px 32px rgba(0,0,0,0.28), 0 1px 0 rgba(255,255,255,0.06);
    border-bottom: 1px solid rgba(255,255,255,0.07);
}}
.logo-wrap {{
    width: clamp(48px, 5vw, 68px);
    height: clamp(48px, 5vw, 68px);
    min-width: 48px;
    flex-shrink: 0;
}}
.logo-wrap img {{
    width: 100%; height: 100%;
    object-fit: contain;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.35));
}}
.header-center {{ flex: 1; text-align: center; }}
.header-center .title {{
    color: #ffffff;
    font-size: clamp(14px, 2vw, 26px);
    font-weight: 800;
    line-height: 1.25;
    letter-spacing: -0.2px;
}}
.header-center .subtitle {{
    color: rgba(255,255,255,0.65);
    font-size: clamp(10px, 1.1vw, 14px);
    font-weight: 400;
    margin-top: 3px;
}}
.header-spacer {{
    height: clamp(68px, 8vw, 92px);
    flex-shrink: 0;
}}

/* =====================================================
   WELCOME SECTION
   ===================================================== */
@keyframes fadeSlideUp {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.welcome-section-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    padding: 24px clamp(16px, 4vw, 40px) 16px;
    animation: fadeSlideUp 0.5s ease both;
}}
.welcome-avatar-wrap {{
    width: clamp(72px, 10vw, 92px);
    height: clamp(72px, 10vw, 92px);
    border-radius: 50%;
    overflow: hidden;
    border: 3px solid rgba(255,255,255,0.85);
    box-shadow: 0 6px 24px rgba(0,0,0,0.18), 0 0 0 5px rgba(255,255,255,0.22);
    margin-bottom: 14px;
    background: #dff0fb;
}}
.welcome-avatar-wrap img {{ width: 100%; height: 100%; object-fit: cover; }}
.welcome-bubble {{
    position: relative;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.7);
    border-radius: 8px 22px 22px 22px;
    padding: 16px 24px;
    text-align: center;
    color: #1a2332;
    font-size: clamp(13px, 1.2vw, 15.5px);
    line-height: 1.7;
    box-shadow: 0 4px 20px rgba(0,0,0,0.09);
    max-width: 360px;
}}
.welcome-bubble::before {{
    content: '';
    position: absolute;
    top: -10px; left: 24px;
    width: 0; height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 10px solid rgba(255,255,255,0.92);
}}

/* =====================================================
   MENU BUTTONS — solid, centered, clearly visible
   ===================================================== */
.menu-section {{
    width: 100%;
    padding: 8px clamp(16px, 5vw, 60px) 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    animation: fadeSlideUp 0.5s 0.15s ease both;
}}

/* All regular stButton */
div[data-testid="stVerticalBlock"] .stButton > button {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: rgba(255,255,255,0.88) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1.5px solid rgba(200,220,245,0.9) !important;
    border-radius: 14px !important;
    color: #0d2d52 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 14px 22px !important;
    width: 100% !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
    line-height: 1.4 !important;
    white-space: normal !important;
    height: auto !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.10) !important;
    cursor: pointer !important;
    margin-bottom: 2px !important;
    display: block !important;
}}
div[data-testid="stVerticalBlock"] .stButton > button:hover {{
    background: rgba(255,255,255,1.0) !important;
    box-shadow: 0 6px 24px rgba(13,45,82,0.18) !important;
    transform: translateY(-2px) !important;
    border-color: rgba(26,106,171,0.4) !important;
    color: #0a2240 !important;
}}
div[data-testid="stVerticalBlock"] .stButton > button:active {{
    transform: scale(0.98) !important;
}}

/* Toggle menu button — pill style, different look */
.stButton[data-key="toggle_menu"] > button,
button[data-testid="toggle_menu"] {{
    background: rgba(255,255,255,0.75) !important;
    border: 1.5px solid rgba(26,106,171,0.45) !important;
    color: #0d3663 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 9px 22px !important;
    border-radius: 24px !important;
    width: auto !important;
    min-width: 180px !important;
    text-align: center !important;
    box-shadow: 0 2px 10px rgba(13,45,82,0.12) !important;
}}
.stButton[data-key="toggle_menu"] > button:hover {{
    background: rgba(255,255,255,0.95) !important;
    border-color: rgba(26,106,171,0.7) !important;
    box-shadow: 0 4px 16px rgba(13,45,82,0.2) !important;
    transform: translateY(-1px) !important;
}}

/* =====================================================
   CHAT MESSAGES
   ===================================================== */
.messages-container {{
    width: 100%;
    padding: 16px clamp(16px, 4vw, 40px) 8px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    animation: fadeSlideUp 0.4s ease both;
}}
.msg-row {{
    display: flex;
    align-items: flex-end;
    gap: 9px;
}}
.msg-row.user {{ flex-direction: row-reverse; }}
.bot-av {{
    width: 34px; height: 34px; min-width: 34px;
    border-radius: 50%;
    overflow: hidden;
    border: 2px solid rgba(255,255,255,0.75);
    background: #dff0fb;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #1a5276;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    flex-shrink: 0;
}}
.bot-av img {{ width: 100%; height: 100%; object-fit: cover; }}
.bubble {{
    max-width: 78%;
    padding: 12px 16px;
    font-size: clamp(13px, 1.1vw, 15px);
    line-height: 1.7;
    word-wrap: break-word;
    white-space: pre-wrap;
}}
.bubble.bot {{
    background: rgba(255,255,255,0.90);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.65);
    color: #1a2332;
    border-radius: 4px 18px 18px 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}}
.bubble.bubble-html {{
    white-space: normal !important;
}}
.bubble.user {{
    background: linear-gradient(135deg, #0d3663, #1a6aab);
    color: #fff;
    border-radius: 18px 4px 18px 18px;
    box-shadow: 0 3px 16px rgba(13,54,99,0.28);
}}
.ts {{
    display: block;
    font-size: 10px;
    margin-top: 5px;
    opacity: 0.38;
    text-align: right;
}}

/* =====================================================
   INPUT BAR — force white background at every layer
   ===================================================== */
/* Outermost wrapper */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div {{
    background: transparent !important;
}}
[data-testid="stBottom"] {{
    padding: 10px clamp(16px, 4vw, 40px) 14px !important;
}}
[data-testid="stBottom"] > div {{
    max-width: 680px !important;
    margin: 0 auto !important;
    width: 100% !important;
}}

/* Chat input wrapper pill */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
.stChatInput,
.stChatInput > div {{
    background: #ffffff !important;
    border: 2px solid rgba(26,106,171,0.55) !important;
    border-radius: 22px !important;
    box-shadow: 0 4px 20px rgba(13,45,82,0.12) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    max-width: 100% !important;
}}
[data-testid="stChatInput"] > div:focus-within,
.stChatInput > div:focus-within {{
    background: #ffffff !important;
    border-color: rgba(26,106,171,0.85) !important;
    box-shadow: 0 4px 24px rgba(13,54,99,0.18), 0 0 0 3px rgba(26,106,171,0.12) !important;
}}

/* Textarea */
[data-testid="stChatInput"] textarea,
.stChatInput textarea {{
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #0d2d52 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    caret-color: #1a6aab !important;
    padding: 13px 16px !important;
}}
[data-testid="stChatInput"] textarea::placeholder,
.stChatInput textarea::placeholder {{
    color: rgba(13,45,82,0.38) !important;
    font-style: italic !important;
}}

/* Send button */
[data-testid="stChatInputSubmitButton"] {{
    background: linear-gradient(135deg, #0d3663, #1a6aab) !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    margin: 7px 8px !important;
    box-shadow: 0 3px 10px rgba(13,54,99,0.3) !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stChatInputSubmitButton"]:hover {{
    transform: scale(1.08) !important;
}}
[data-testid="stChatInputSubmitButton"] svg {{
    stroke: none !important;
    fill: #ffffff !important;
}}

/* Hide default Streamlit chat containers */
.stChatMessage {{ display: none !important; }}

/* =====================================================
   CENTERING HELPERS
   ===================================================== */
/* Force all stButton containers to center their content */
div[data-testid="column"] > div[data-testid="stVerticalBlock"] {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}}

/* =====================================================
   RESPONSIVE
   ===================================================== */
@media (max-width: 600px) {{
    .chat-header {{ padding: 10px 16px; gap: 10px; }}
    .logo-wrap {{ width: 42px; height: 42px; min-width: 42px; }}
    .bubble {{ max-width: 88%; }}
    .welcome-bubble {{ max-width: 92%; }}
    .messages-container {{ padding: 12px 14px 8px; }}
    .menu-section {{ padding: 6px 14px 12px; }}
}}

/* =====================================================
   SUHU TABLE — beautiful styled card inside bubble
   ===================================================== */
.bubble-wide {{
    max-width: 96% !important;
    padding: 14px 14px !important;
}}
.suhu-wrap {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    width: 100%;
}}
.suhu-title {{
    font-size: 13.5px;
    font-weight: 700;
    color: #0d2d52;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(26,106,171,0.15);
    letter-spacing: 0.1px;
}}
/* 3 columns side-by-side on wide screens, stack on mobile */
.suhu-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    width: 100%;
}}
@media (max-width: 680px) {{
    .suhu-grid {{ grid-template-columns: 1fr; }}
}}
@media (min-width: 681px) and (max-width: 900px) {{
    .suhu-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
.suhu-card {{
    display: flex;
    flex-direction: column;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 3px 14px rgba(0,0,0,0.09);
    background: rgba(255,255,255,0.92);
}}
.suhu-card-header {{
    background: linear-gradient(135deg, #0d3663, #1a6aab);
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
    padding: 9px 14px;
    text-align: center;
    letter-spacing: 0.2px;
}}
.suhu-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
}}
.suhu-table thead tr th {{
    background: rgba(13,54,99,0.06);
    color: #0d2d52;
    font-weight: 700;
    padding: 7px 10px;
    text-align: left;
    font-size: 11.5px;
    letter-spacing: 0.2px;
    border-bottom: 1.5px solid rgba(26,106,171,0.15);
}}
.suhu-table thead tr th:last-child {{ text-align: center; }}
.suhu-table tbody tr:nth-child(even) .suhu-td-area {{
    background: rgba(240,247,255,0.6);
}}
.suhu-table tbody tr:nth-child(odd) .suhu-td-area {{
    background: rgba(255,255,255,0.75);
}}
.suhu-table tbody tr:hover td {{ filter: brightness(0.96); }}
.suhu-td-area {{
    padding: 7px 10px;
    color: #1a2332;
    font-weight: 500;
    border-bottom: 1px solid rgba(200,220,245,0.35);
    white-space: nowrap;
}}
.suhu-td-val {{
    padding: 6px 8px;
    font-weight: 700;
    text-align: center;
    border-bottom: 1px solid rgba(200,220,245,0.25);
    font-size: 12.5px;
    white-space: nowrap;
}}
.suhu-source {{
    font-size: 10px;
    color: rgba(13,45,82,0.4);
    margin-top: 10px;
    text-align: right;
    font-style: italic;
}}

/* =====================================================
   LINK CARDS — infografis & lokasi
   ===================================================== */
.bubble.bot a {{
    color: #1a6aab !important;
    text-decoration: underline !important;
    font-weight: 500;
}}
.bubble.bot a:hover {{
    color: #0d3663 !important;
}}
    font-size: 13px;
    font-weight: 700;
    color: #0d2d52;
    margin-bottom: 10px;
    padding-bottom: 7px;
    border-bottom: 2px solid rgba(26,106,171,0.15);
}}
.link-cards {{
    display: flex;
    flex-direction: column;
    gap: 6px;
}}
.link-card {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 12px;
    background: rgba(255,255,255,0.65);
    border: 1px solid rgba(200,220,245,0.75);
    border-radius: 9px;
    text-decoration: none !important;
    color: inherit !important;
    transition: all 0.16s ease;
}}
.link-card:hover {{
    background: rgba(255,255,255,0.95);
    border-color: rgba(26,106,171,0.4);
    box-shadow: 0 2px 10px rgba(13,45,82,0.10);
    transform: translateY(-1px);
}}
.link-card-text {{
    flex: 1;
    min-width: 0;
}}
.link-card-label {{
    font-size: 10.5px;
    font-weight: 600;
    color: rgba(13,45,82,0.45);
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 1px;
}}
.link-card-url {{
    font-size: 13px;
    font-weight: 600;
    color: #0d2d52;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.link-card-arrow {{
    font-size: 13px;
    color: rgba(26,106,171,0.45);
    flex-shrink: 0;
}}
.lokasi-alamat {{
    margin-top: 8px;
    padding: 8px 11px;
    background: rgba(240,247,255,0.65);
    border-radius: 8px;
    font-size: 12px;
    color: #1a2332;
    line-height: 1.6;
    border-left: 3px solid rgba(26,106,171,0.35);
}}
</style>
""", unsafe_allow_html=True)


# =====================================================
# FUNGSI MEMBACA GOOGLE SHEETS
# =====================================================
@st.cache_data(ttl=600)
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

@st.cache_data(ttl=600)
def load_ringkasan_cuaca():
    df = load_sheet("Ringkasan%20semua")
    df = df.drop(columns=["Sumber Data"], errors="ignore")
    latest_df = df.tail(3).reset_index(drop=True)
    data = latest_df.to_dict(orient="records")
    return {
        "hari_ini": data[0] if len(data) > 0 else {},
        "besok":    data[1] if len(data) > 1 else {},
        "lusa":     data[2] if len(data) > 2 else {},
    }


def get_data_ranges():
    df = load_sheet("Narasi")
    peringatan = df.iloc[35:49, 0:4].fillna("")
    cuaca      = df.iloc[29:53, 0:4].fillna("")
    return peringatan, cuaca

def clean_cell(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def normalize_parameter(param):
    param = str(param).strip()
    return " ".join(param.split())

def dataframe_to_structured_json(df):
    structured_data = {"hari_ini": {}, "besok": {}, "lusa": {}}
    for _, row in df.iterrows():
        parameter = normalize_parameter(row.iloc[0])
        if not parameter:
            continue
        v0 = clean_cell(row.iloc[1])
        v1 = clean_cell(row.iloc[2])
        v2 = clean_cell(row.iloc[3])
        if v0: structured_data["hari_ini"][parameter] = v0
        if v1: structured_data["besok"][parameter]    = v1
        if v2: structured_data["lusa"][parameter]     = v2
    return structured_data

def get_dates():
    today = datetime.now()
    return (
        today.strftime("%d %B %Y"),
        (today + timedelta(days=1)).strftime("%d %B %Y"),
        (today + timedelta(days=2)).strftime("%d %B %Y"),
    )

today, besok, lusa = get_dates()

peringatan_df, cuaca_df = get_data_ranges()
peringatan_json = dataframe_to_structured_json(peringatan_df)
cuaca_json      = dataframe_to_structured_json(cuaca_df)
ringkasan_json  = load_ringkasan_cuaca()


#=====================================================
# LOAD SUHU 
#=====================================================
WILAYAH_PERAIRAN = [
    "Agam-Pasbar",
    "BaratPagai",
    "BaratSipora",
    "BaratSiberut",
    "TimurPagai",
    "TimurSipora",
    "TimurSiberut",
    "PesisirSelatan",
    "Padang-PadangPariaman"
]

@st.cache_data(ttl=600)
def load_suhu_berdasarkan_tanggal():
    df = load_sheet("Ringkasan%20semua")

    # Bersihkan nama kolom
    df.columns = df.columns.str.strip()
    df["perairan"] = df["perairan"].astype(str).str.strip()

    # Hapus kolom yang tidak diperlukan
    df = df.drop(columns=["Sumber Data"], errors="ignore")

    # Konversi tanggal
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

    # Filter hanya wilayah yang valid
    df = df[df["perairan"].isin(WILAYAH_PERAIRAN)]

    # Tentukan tanggal target
    today = pd.Timestamp.now().normalize()
    besok = today + pd.Timedelta(days=1)
    lusa = today + pd.Timedelta(days=2)

    target_dates = [today, besok, lusa]

    hasil = {}

    for tgl in target_dates:
        df_filtered = df[df["Tanggal"] == tgl]

        # Ambil data terbaru untuk setiap wilayah
        df_filtered = (
            df_filtered.sort_index()
            .groupby("perairan", as_index=False)
            .last()
        )

        # Urutkan sesuai daftar wilayah resmi
        df_filtered["perairan"] = pd.Categorical(
            df_filtered["perairan"],
            categories=WILAYAH_PERAIRAN,
            ordered=True
        )
        df_filtered = df_filtered.sort_values("perairan")

        hasil[tgl.strftime("%d %B %Y")] = df_filtered[
            ["perairan", "Suhu (Rata²)"]
        ]

    return hasil

def format_suhu(data_dict):
    """Return HTML: 3 tables side-by-side (responsive grid), no tabs."""
    if not isinstance(data_dict, dict):
        return "__SUHU_HTML__<p>Data suhu tidak tersedia.</p>"

    def suhu_color(val):
        try:
            v = float(val)
            if v < 26.5:   return "#b3e5fc", "#01579b"
            elif v < 27.2: return "#e1f5fe", "#0277bd"
            elif v < 27.8: return "#fff9c4", "#f57f17"
            elif v < 28.5: return "#ffe0b2", "#e65100"
            else:           return "#ffcdd2", "#b71c1c"
        except:
            return "#f5f5f5", "#424242"

    html = '<div class="suhu-wrap">'
    html += '<div class="suhu-title">🌡 Tabel Suhu Maritim Sumatera Barat</div>'
    html += '<div class="suhu-grid">'

    for tanggal, df in data_dict.items():
        html += f'<div class="suhu-card">'
        html += f'<div class="suhu-card-header">{tanggal}</div>'
        html += '<table class="suhu-table"><thead><tr><th>Perairan</th><th>Suhu (°C)</th></tr></thead><tbody>'

        if isinstance(df, pd.DataFrame) and not df.empty:
            for _, row in df.iterrows():
                perairan  = str(row.iloc[0])
                suhu_val  = row.iloc[1]
                bg, fg    = suhu_color(suhu_val)
                suhu_disp = f"{float(suhu_val):.1f}" if str(suhu_val) not in ["-", "", "nan"] else "-"
                html += f'<tr><td class="suhu-td-area">{perairan}</td>'
                html += f'<td class="suhu-td-val" style="background:{bg};color:{fg};">{suhu_disp} °C</td></tr>'
        else:
            html += '<tr><td colspan="2" style="text-align:center;padding:10px;color:#999;font-size:12px;">Data tidak tersedia</td></tr>'

        html += '</tbody></table></div>'

    html += '</div>'  # end suhu-grid
    html += '<div class="suhu-source">Sumber: Stasiun Meteorologi Maritim Teluk Bayur – BMKG</div>'
    html += '</div>'  # end suhu-wrap
    return "__SUHU_HTML__" + html

# =====================================================
# FORMAT RESPONSES PERINGATAN DINI & RINGKASAN CUACA
# =====================================================
def format_peringatan(pj, today, besok, lusa):
    tanggal_map = {"hari_ini": today, "besok": besok, "lusa": lusa}
    warning_kw  = ["Peringatan Gel", "Potensi Hujan Petir", "Potensi Hujan Lebat",
                   "Potensi Hujan Sedang", "Potensi Hujan Ringan", "Potensi Kabut",
                   "Potensi Petir", "Potensi Udara Kabur", "Potensi Angin Kencang"]
    exclude_kw  = ["Pasang Tertinggi", "Surut Terendah"]
    output      = "Informasi Peringatan Dini Cuaca Maritim\nWilayah Perairan Sumatera Barat\n"
    data_kosong = True
    for hari, tanggal in tanggal_map.items():
        output += f"\n**{tanggal}**\n"
        data_harian = pj.get(hari, {})
        ditemukan = False
        for key, nilai in data_harian.items():
            if any(ex.lower() in key.lower() for ex in exclude_kw):
                continue
            if any(kw.lower() in key.lower() for kw in warning_kw):
                if nilai and nilai.strip() not in ["-", ""]:
                    output += f"- **{key}**: {nilai}\n"
                    ditemukan = True
                    data_kosong = False
        if not ditemukan:
            output += "Tidak terdapat peringatan dini pada tanggal tersebut.\n"
    if data_kosong:
        output += ("\nTidak terdapat peringatan dini saat ini.\n"
                   "Pantau melalui:\nhttps://www.bmkg.go.id/cuaca/maritim/peringatan-gelombang-tinggi")
    output += "\n\nPantau terus informasi cuaca maritim terbaru melalui kanal resmi BMKG."
    return output

def format_ringkasan_cuaca(rj):
    output = "Ringkasan Cuaca Maritim Sumatera Barat\n\n"
    label_hari = {"hari_ini": "Hari Ini", "besok": "Besok", "lusa": "Lusa"}
    for hari, label in label_hari.items():
        data = rj.get(hari, {})
        if not data:
            continue
        output += f"**{label} ({data.get('Tanggal', '-')})**\n"
        output += f"- Cuaca Signifikan: {data.get('Cuaca Signifikan', '-')}\n"
        output += f"- Angin: {data.get('Arah Angin Terbanyak', '-')} ({data.get('Kecepatan Angin (Min)', '-')} – {data.get('Kecepatan Angin (Maks)', '-')} knot)\n"
        output += f"- Gelombang: {data.get('Gelombang Signifikan', '-')} m (Maks: {data.get('Tinggi Gelombang (Maks)', '-')}, Min: {data.get('Tinggi Gelombang (Min)', '-')})\n"
        output += f"- Suhu: {data.get('Suhu (Rata²)', '-')} °C | Kelembapan: {data.get('RH (Rata²)', '-')}%\n"
        output += f"- Arus: {data.get('Arah Arus Terbanyak', '-')} ({data.get('Kecepatan Arus (Maks)', '-')} m/s)\n\n"
    output += "Sumber: Stasiun Meteorologi Maritim Teluk Bayur - BMKG"
    return output

# =====================================================
# FORMAT KESELAMATAN PERAHU
# =====================================================
BATAS_KESELAMATAN = [
    {"nama": "Perahu Nelayan",          "angin": 15,  "gelombang": 1.25},
    {"nama": "Kapal Tongkang",          "angin": 16,  "gelombang": 1.5},
    {"nama": "Kapal Ferry",             "angin": 21,  "gelombang": 2.5},
    {"nama": "Kapal Besar (Kargo/Pesiar)", "angin": 27, "gelombang": 4.0},
]

def parse_knot(value):
    try:
        return float(re.search(r"[\d.]+", str(value)).group())
    except:
        return None

def parse_meter(value):
    try:
        return float(re.search(r"[\d.]+", str(value)).group())
    except:
        return None

@st.cache_data(ttl=600)
def load_keselamatan_per_perairan():
    """Ambil data angin & gelombang per perairan per hari dari Ringkasan semua."""
    df = load_sheet("Ringkasan%20semua")
    df.columns = df.columns.str.strip()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    df["perairan"] = df["perairan"].astype(str).str.strip()
    df = df.drop(columns=["Sumber Data"], errors="ignore")

    today_ts  = pd.Timestamp.now().normalize()
    besok_ts  = today_ts + pd.Timedelta(days=1)
    lusa_ts   = today_ts + pd.Timedelta(days=2)

    hasil = {}
    for label, tgl in [("Hari Ini", today_ts), ("Besok", besok_ts), ("Lusa", lusa_ts)]:
        df_tgl = df[df["Tanggal"] == tgl].copy()
        df_tgl = df_tgl.sort_index().groupby("perairan", as_index=False).last()
        rows = []
        for _, row in df_tgl.iterrows():
            angin     = parse_knot(row.get("Kecepatan Angin (Maks)", ""))
            gelombang = parse_meter(row.get("Tinggi Gelombang (Maks)", ""))
            rows.append({
                "perairan":  row["perairan"],
                "angin":     angin,
                "gelombang": gelombang,
                "angin_str": str(row.get("Kecepatan Angin (Maks)", "-")).strip(),
                "gel_str":   str(row.get("Tinggi Gelombang (Maks)", "-")).strip(),
                "tanggal":   tgl.strftime("%d/%m/%Y"),
            })
        hasil[label] = rows
    return hasil

def cek_status_perahu(angin, gelombang):
    """Kembalikan list perahu yang DILARANG dan DIIZINKAN."""
    dilarang = []
    diizinkan = []
    for b in BATAS_KESELAMATAN:
        bahaya = (
            (angin     is not None and angin     >= b["angin"]) or
            (gelombang is not None and gelombang >= b["gelombang"])
        )
        if bahaya:
            dilarang.append(b["nama"])
        else:
            diizinkan.append(b["nama"])
    return dilarang, diizinkan

def format_keselamatan_html():
    """Render tabel keselamatan sebagai HTML di dalam bubble."""
    data = load_keselamatan_per_perairan()

    STATUS_COLORS = {
        "DILARANG":  ("background:#FFCDD2;color:#B71C1C;font-weight:700;", "DILARANG"),
        "DIIZINKAN": ("background:#C8E6C9;color:#1B5E20;font-weight:700;", "DIIZINKAN"),
    }

    th = "padding:7px 10px;background:#f0f4f8;color:#0d2d52;font-weight:700;font-size:11.5px;border-bottom:2px solid #d0dcea;text-align:center;white-space:nowrap;"
    th_left = th + "text-align:left;"
    td_base = "padding:7px 10px;font-size:12px;border-bottom:1px solid #e8eef5;text-align:center;white-space:nowrap;"
    td_left = td_base + "text-align:left;font-weight:600;color:#1a2332;"

    html = '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;">'
    html += '<div style="font-size:13.5px;font-weight:700;color:#0d2d52;margin-bottom:4px;padding-bottom:8px;border-bottom:2px solid rgba(26,106,171,0.15);">Rekomendasi Keselamatan Pelayaran</div>'
    html += '<div style="font-size:11px;color:#546e7a;margin-bottom:12px;">Perahu berisiko jika angin atau gelombang mencapai/melebihi batas keselamatan.</div>'

    for label, rows in data.items():
        if not rows:
            continue
        tanggal = rows[0]["tanggal"]
        html += f'<div style="font-size:12px;font-weight:700;color:#0d3663;margin:10px 0 5px;background:rgba(13,54,99,0.07);padding:5px 10px;border-radius:6px;">{label} &middot; {tanggal}</div>'
        html += f'<div style="overflow-x:auto;margin-bottom:8px;">'
        html += '<table style="width:100%;border-collapse:collapse;background:#fff;">'
        html += '<thead><tr>'
        html += f'<th style="{th_left}">Perairan</th>'
        html += f'<th style="{th}">Angin Maks</th>'
        html += f'<th style="{th}">Gelombang Maks</th>'
        for b in BATAS_KESELAMATAN:
            html += f'<th style="{th}">{b["nama"]}</th>'
        html += '</tr></thead><tbody>'

        for i, r in enumerate(rows):
            row_bg = "background:#f9fbff;" if i % 2 == 0 else "background:#ffffff;"
            html += f'<tr style="{row_bg}">'
            html += f'<td style="{td_left}">{r["perairan"]}</td>'
            html += f'<td style="{td_base}">{r["angin_str"]} knot</td>'
            html += f'<td style="{td_base}">{r["gel_str"]} m</td>'
            dilarang, diizinkan = cek_status_perahu(r["angin"], r["gelombang"])
            for b in BATAS_KESELAMATAN:
                status = "DILARANG" if b["nama"] in dilarang else "DIIZINKAN"
                style, text = STATUS_COLORS[status]
                html += f'<td style="{td_base}"><span style="{style}padding:3px 8px;border-radius:10px;font-size:11px;">{text}</span></td>'
            html += '</tr>'

        html += '</tbody></table></div>'

    html += '<div style="font-size:10px;color:rgba(13,45,82,0.4);margin-top:8px;text-align:right;font-style:italic;">Sumber: Stasiun Meteorologi Maritim Teluk Bayur – BMKG</div>'
    html += '</div>'
    return "__KESELAMATAN__" + html

def build_keselamatan_llm_context():
    """
    Buat ringkasan teks dari data keselamatan untuk dimasukkan ke system prompt LLM.
    """
    data = load_keselamatan_per_perairan()
    lines = ["DATA KESELAMATAN PELAYARAN PER PERAIRAN:"]
    lines.append("Batas risiko: Perahu Nelayan >=15kt/1.25m | Tongkang >=16kt/1.5m | Ferry >=21kt/2.5m | Kapal Besar >=27kt/4m")
    for label, rows in data.items():
        if not rows:
            continue
        lines.append(f"\n{label} ({rows[0]['tanggal']}):")
        for r in rows:
            dilarang, diizinkan = cek_status_perahu(r["angin"], r["gelombang"])
            status_parts = []
            if dilarang:
                status_parts.append("DILARANG: " + ", ".join(dilarang))
            if diizinkan:
                status_parts.append("DIIZINKAN: " + ", ".join(diizinkan))
            lines.append(
                f"  {r['perairan']}: angin {r['angin_str']} knot, gelombang {r['gel_str']} m"
                + (" | " + " | ".join(status_parts) if status_parts else "")
            )
    return "\n".join(lines)


# =====================================================
# FUNGSI AMBIL DATA DINAMIS BERDASARKAN PERTANYAAN USER
# =====================================================
def parse_tanggal_dari_pertanyaan(text):
    text = text.lower()
    today = datetime.now().date()

    # keyword relatif
    if "hari ini" in text:
        return today
    elif "besok" in text:
        return today + timedelta(days=1)
    elif "lusa" in text:
        return today + timedelta(days=2)
    elif "kemarin" in text:
        return today - timedelta(days=1)

    # format: 10/04/2026 atau 10-04-2026
    match_numeric = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", text)
    if match_numeric:
        day, month, year = match_numeric.groups()
        year = int(year)
        if year < 100:
            year += 2000
        return datetime(int(year), int(month), int(day)).date()

    # format: 10 april 2026
    try:
        parsed = pd.to_datetime(text, dayfirst=True, errors='coerce')
        if pd.notna(parsed):
            return parsed.date()
    except:
        pass
    return None

INTENT_MAP = {
    "suhu": ["Suhu (Rata²)"],
    "kelembapan": ["RH (Rata²)"],
    "angin": ["Arah Angin Terbanyak", "Kecepatan Angin (Maks)", "Kecepatan Angin (Min)"],
    "gelombang": ["Gelombang Signifikan", "Tinggi Gelombang (Maks)", "Tinggi Gelombang (Min)"],
    "arus": ["Arah Arus Terbanyak", "Kecepatan Arus (Maks)"],
    "cuaca": ["Cuaca Signifikan", "Cuaca Terbaik"],
}

def detect_intent(text):
    text = text.lower()
    hasil = []

    for key, kolom in INTENT_MAP.items():
        if key in text:
            hasil.extend(kolom)

    # default fallback
    if not hasil:
        hasil = ["Cuaca Signifikan"]

    return hasil


def ambil_data_dinamis(user_input):
    df = load_sheet("Ringkasan%20semua")

    # cleaning
    df.columns = df.columns.str.strip()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    df["perairan"] = df["perairan"].astype(str).str.strip()

    # detect intent
    kolom_dipakai = detect_intent(user_input)

    # detect tanggal
    tanggal = parse_tanggal_dari_pertanyaan(user_input)

    if tanggal is None:
        tanggal = datetime.now().date()

    # filter berdasarkan tanggal (satu filter saja, tanpa duplikasi)
    df = df[df["Tanggal"].dt.date == tanggal]

    # ambil data terbaru per wilayah
    df = (
        df.sort_index()
        .groupby("perairan", as_index=False)
        .last()
    )

    # pilih kolom penting — pastikan kolom ada di dataframe
    kolom_tersedia = [k for k in kolom_dipakai if k in df.columns]
    if not kolom_tersedia:
        kolom_tersedia = ["Cuaca Signifikan"] if "Cuaca Signifikan" in df.columns else []

    kolom_final = ["perairan", "Tanggal"] + kolom_tersedia
    kolom_final = [k for k in kolom_final if k in df.columns]
    df = df[kolom_final]

    return df, tanggal

# =====================================================
# SYSTEM PROMPT & CHATBOT
# =====================================================
def build_system_prompt():
    return f"""
Anda adalah Asisten Virtual Resmi Stasiun Meteorologi Maritim Teluk Bayur - BMKG.
Berikan informasi cuaca kelautan, prakiraan tinggi gelombang, dan peringatan dini
untuk wilayah perairan Sumatera Barat.
Gunakan bahasa Indonesia yang profesional, ramah, tegas, dan informatif.
JANGAN gunakan emoticon.

Hari ini: {today} | Besok: {besok} | Lusa: {lusa}

DATA PERINGATAN DINI:
{json.dumps(peringatan_json, indent=2, ensure_ascii=False)}

DATA CUACA MARITIM:
{json.dumps(cuaca_json, indent=2, ensure_ascii=False)}

{build_keselamatan_llm_context()}

ATURAN:
- Jangan menampilkan Pasang Tertinggi/Surut Terendah dalam peringatan dini.
- Jangan mengarang data.
- Jika ditanya tentang keselamatan berlayar atau jenis perahu yang boleh/dilarang berlayar,
  gunakan DATA KESELAMATAN PELAYARAN di atas untuk menjawab secara spesifik per wilayah.
- Tolak pertanyaan di luar topik cuaca maritim dengan sopan.
- Kontak: WhatsApp https://wa.me/628116601044 | IG @stamar_tlkbayur
"""

def ask_chatbot(user_input):

    df, tanggal = ambil_data_dinamis(user_input)

    tanggal_str = tanggal.strftime("%d %B %Y") if tanggal else "tidak diketahui"

    if df.empty:
        # Coba ambil semua tanggal yang tersedia di sheet untuk memberi info yang berguna
        try:
            df_all = load_sheet("Ringkasan%20semua")
            df_all.columns = df_all.columns.str.strip()
            df_all["Tanggal"] = pd.to_datetime(df_all["Tanggal"], errors="coerce")
            tanggal_tersedia = sorted(df_all["Tanggal"].dropna().dt.date.unique())
            if tanggal_tersedia:
                tgl_info = ", ".join([t.strftime("%d/%m/%Y") for t in tanggal_tersedia[-5:]])
                return (
                    f"Maaf, data cuaca maritim untuk tanggal {tanggal_str} tidak tersedia dalam sistem kami.\n\n"
                    f"Data yang tersedia mencakup tanggal-tanggal berikut (5 terbaru): {tgl_info}.\n\n"
                    f"Silakan tanyakan informasi untuk tanggal yang tersedia, atau gunakan menu utama untuk prakiraan 3 hari ke depan."
                )
        except:
            pass
        return (
            f"Maaf, data cuaca maritim untuk tanggal {tanggal_str} tidak tersedia dalam sistem kami. "
            f"Silakan gunakan menu utama untuk melihat prakiraan cuaca 3 hari ke depan, atau hubungi kami melalui WhatsApp: https://wa.me/628116601044"
        )

    data_text = df.to_markdown(index=False)

    dynamic_prompt = f"""
Data cuaca maritim Sumatera Barat untuk tanggal {tanggal_str}:

{data_text}

Instruksi:
- Jawaban HARUS berdasarkan data di atas
- Sebutkan tanggal data yang digunakan dalam jawaban
- Jangan mengatakan data tidak tersedia jika data ada di tabel
- Jika kolom "Cuaca Signifikan" ada, jelaskan kondisi cuaca secara ringkas per wilayah
- Gunakan bahasa Indonesia yang jelas dan profesional
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": dynamic_prompt + "\n\nPertanyaan: " + user_input}
        ],
    )

    return response.choices[0].message.content

# =====================================================
# SESSION STATE
# =====================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_menu" not in st.session_state:
    st.session_state.show_menu = True

# =====================================================
# RENDER HTML MESSAGES
# =====================================================
def render_messages_html():
    parts = []
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("time", "")
        ts_html = f'<span class="ts">{ts}</span>' if ts else ""

        if role == "assistant":
            if AVATAR_B64:
                av = f'<div class="bot-av"><img src="data:image/png;base64,{AVATAR_B64}" /></div>'
            else:
                av = '<div class="bot-av">B</div>'

            # Detect raw HTML content (suhu table or link cards)
            if content.startswith("__SUHU_HTML__"):
                inner_html = content[len("__SUHU_HTML__"):]
                parts.append(f'<div class="msg-row bot">{av}<div class="bubble bot bubble-wide bubble-html">{inner_html}{ts_html}</div></div>')
            elif content.startswith("__HTML__"):
                inner_html = content[len("__HTML__"):]
                parts.append(f'<div class="msg-row bot">{av}<div class="bubble bot bubble-html">{inner_html}{ts_html}</div></div>')
            elif content.startswith("__KESELAMATAN__"):
                inner_html = content[len("__KESELAMATAN__"):]
                parts.append(f'<div class="msg-row bot">{av}<div class="bubble bot bubble-wide bubble-html">{inner_html}{ts_html}</div></div>')
            else:
                esc = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                esc = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', esc)
                esc = esc.replace("\n", "<br>")
                parts.append(f'<div class="msg-row bot">{av}<div class="bubble bot">{esc}{ts_html}</div></div>')
        else:
            esc = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            esc = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', esc)
            esc = esc.replace("\n", "<br>")
            parts.append(f'<div class="msg-row user"><div class="bubble user">{esc}{ts_html}</div></div>')

    return "\n".join(parts)

# =====================================================
# LAYOUT
# =====================================================
logo_img = (f'<img src="data:image/png;base64,{LOGO_B64}" />'
            if LOGO_B64 else '<div style="width:56px;height:56px;"></div>')

avatar_img = (f'<img src="data:image/png;base64,{AVATAR_B64}" />'
              if AVATAR_B64 else '')

has_messages = len(st.session_state.messages) > 0

# ── FIXED HEADER ─────────────────────────────────────
st.markdown(f"""
<div class="chat-header">
  <div class="logo-wrap">{logo_img}</div>
  <div class="header-center">
    <div class="title">Badan Meteorologi, Klimatologi, dan Geofisika</div>
    <div class="subtitle">Stasiun Meteorologi Maritim Kelas IV Teluk Bayur</div>
  </div>
</div>
<div class="header-spacer"></div>
""", unsafe_allow_html=True)

# ── WELCOME SECTION (always shown at top if no messages, or as header) ────
if not has_messages:
    st.markdown(f"""
    <div class="welcome-section-wrap">
      <div class="welcome-avatar-wrap">{avatar_img}</div>
      <div class="welcome-bubble">
        Halo! Selamat datang di Layanan Chatbot<br>
        <strong>BMKG Maritim Teluk Bayur</strong>.<br>
        Silakan pilih menu di bawah.
        \n Notes: 
        Jika ingin menanyakan cuaca lampau ketik tanggal dalam format DD/MM/YYYY, 
        contoh "Bagaimana cuaca maritim pada 15/03/2026?".
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── MESSAGES (chat history — always rendered if exists) ────────────────
if has_messages:
    st.markdown(f"""
    <div class="messages-container">
      {render_messages_html()}
    </div>
    """, unsafe_allow_html=True)

    # ── BUTTON "LIHAT MENU UTAMA" — centered pill ──────────────
    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        label_toggle = "✕  Tutup Menu" if st.session_state.show_menu else "☰  Lihat Menu Utama"
        if st.button(label_toggle, key="toggle_menu", use_container_width=True):
            st.session_state.show_menu = not st.session_state.show_menu
            st.rerun()

# ── MENU BUTTONS ──────────────────────────────────────
menu_items = [
    ("peringatan",  " Informasi Peringatan Dini"),
    ("infografis",  " Layanan Infografis dan Website"),
    ("cuaca",       " Ringkasan Cuaca Maritim Sumbar (3 Hari)"),
    ("keselamatan", " Jenis Perahu yang Diizinkan Berlayar"),
    ("lokasi",      " Lokasi dan Kontak"),
    ("suhu",        " Informasi Suhu Maritim"),
]

show_menu_now = (not has_messages) or st.session_state.show_menu

if show_menu_now:
    col_l, col_c, col_r = st.columns([0.5, 3, 0.5])
    with col_c:
        for menu_id, label in menu_items:
            if st.button(label, key=f"menu_{menu_id}", use_container_width=True):
                now = datetime.now().strftime("%H:%M")
                # strip emoji prefix for stored message
                clean_label = "  ".join(label.split("  ")[1:]) if "  " in label else label
                st.session_state.messages.append({"role": "user", "content": clean_label, "time": now})

                if menu_id == "peringatan":
                    resp = format_peringatan(peringatan_json, today, besok, lusa)
                elif menu_id == "cuaca":
                    resp = format_ringkasan_cuaca(ringkasan_json)
                elif menu_id == "suhu":
                    suhu_data = load_suhu_berdasarkan_tanggal()
                    resp = format_suhu(suhu_data)
                elif menu_id == "keselamatan":
                    resp = format_keselamatan_html()
                elif menu_id == "infografis":
                    resp = "__HTML__" + """
<strong>Layanan Infografis dan Website</strong><br>
Informasi geografis berupa poster infografis prakiraan cuaca maritim Sumatera Barat tersedia setiap hari di kanal Instagram resmi dan website StaMer Teluk Bayur .
Website Resmi Stasiun Meteorologi Maritim Teluk Bayur:
<a href="https://sites.google.com/bmkg.go.id/cuacamaritimsumbar/prakiraan" target="_blank">sites.google.com/bmkg.go.id/cuacamaritimsumbar</a>
Website Resmi BMKG Maritim:
<a href="https://maritim.bmkg.go.id/" target="_blank">maritim.bmkg.go.id</a>
Instagram:
<a href="https://www.instagram.com/stamar_tlkbayur/" target="_blank">@stamar_tlkbayur</a>
"""
                elif menu_id == "lokasi":
                    resp = "__HTML__" + """
<strong>Lokasi dan Kontak</strong><br>
Silahkan hubungi Stasiun Meteorologi Maritim Teluk Bayur melalui kontak resmi berikut untuk informasi lebih lanjut atau pertanyaan terkait cuaca maritim Sumatera Barat :
WhatsApp:
<a href="https://wa.me/628116601044" target="_blank">+62 811-660-1044</a>
Website Resmi Stasiun Meteorologi Maritim Teluk Bayur:
<a href="https://sites.google.com/bmkg.go.id/cuacamaritimsumbar/prakiraan" target="_blank">sites.google.com/bmkg.go.id/cuacamaritimsumbar</a>
Website Resmi BMKG Maritim:
<a href="https://maritim.bmkg.go.id/" target="_blank">maritim.bmkg.go.id</a>
Instagram :
<a href="https://www.instagram.com/stamar_tlkbayur/" target="_blank">@stamar_tlkbayur</a>
Google Maps:
<a href="https://www.google.com/maps/place/Stasiun+Meteorologi+Maritim+Teluk+Bayur" target="_blank">Stasiun Meteorologi Maritim Teluk Bayur</a>
Alamat:
Jl. Sutan Syahrir Komp. Pelindo No.26, Rawang, Kec. Padang Selatan, Kota Padang, Sumatera Barat 25123.
"""
                else:
                    resp = "Informasi tidak tersedia."

                st.session_state.messages.append({"role": "assistant", "content": resp, "time": now})
                st.session_state.show_menu = False
                st.rerun()

# ── INPUT BAR ─────────────────────────────────────────
user_input = st.chat_input("Ketik pertanyaan tentang cuaca maritim Sumatera Barat...")

if user_input:
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_input, "time": now})
    with st.spinner("Memproses..."):
        resp = ask_chatbot(user_input)
    st.session_state.messages.append({"role": "assistant", "content": resp, "time": now})
    st.session_state.show_menu = False
    st.rerun()

# ── AUTO-SCROLL + FORCE WHITE INPUT ────────────────────
st.markdown("""
<script>
(function() {
    function applyFixes() {
        // Force white background on chat input at every DOM level
        const selectors = [
            '[data-testid="stChatInput"]',
            '[data-testid="stChatInput"] > div',
            '[data-testid="stChatInput"] textarea',
            '[data-testid="stBottom"]',
            '[data-testid="stBottom"] > div',
            '[data-testid="stBottom"] > div > div',
        ];
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                el.style.setProperty('background', '#ffffff', 'important');
                el.style.setProperty('background-color', '#ffffff', 'important');
                el.style.setProperty('color', '#0d2d52', 'important');
            });
        });
        // Scroll to bottom of messages
        const msgs = document.querySelector('.messages-container');
        if (msgs) msgs.scrollIntoView({behavior: 'smooth', block: 'end'});
    }
    // Run immediately and after short delays to catch Streamlit re-renders
    applyFixes();
    setTimeout(applyFixes, 300);
    setTimeout(applyFixes, 800);
    // Also watch for DOM changes
    const observer = new MutationObserver(() => applyFixes());
    observer.observe(document.body, {childList: true, subtree: true});
})();
</script>
""", unsafe_allow_html=True)