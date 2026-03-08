"""
=============================================================
  APP STREAMLIT — AJINOMOTO PRODUCTION MONITORING
  v4 — Bulk Edit Base Data (Single Row + Bulk via data_editor)
=============================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import subprocess

# ── Password dari environment variable (aman, tidak hardcoded) ───────────────
# Di lokal: set di file .streamlit/secrets.toml
# Di Streamlit Cloud: set di Settings → Secrets
def get_password():
    # Coba baca dari Streamlit secrets dulu (Streamlit Cloud)
    try:
        return st.secrets["PASSWORD"]
    except Exception:
        pass
    # Fallback: baca dari environment variable
    return os.getenv("PASSWORD", "changeme")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.')

st.set_page_config(
    page_title="Ajinomoto FI-2 Production Monitor",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

OUTPUT_FOLDER = "output"

# ── Cari file base data yang tersedia (prioritas: jan_feb → data_daily) ──────
def resolve_base_daily():
    """Return path ke file base data yang tersedia, prioritas jan_feb_2026 dulu."""
    candidates = [
        os.path.join(OUTPUT_FOLDER, "data_daily_jan_feb_2026.csv"),
        os.path.join(OUTPUT_FOLDER, "data_daily.csv"),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                if not pd.read_csv(p).empty:
                    return p
            except:
                continue
    return os.path.join(OUTPUT_FOLDER, "data_daily.csv")

BASE_DAILY_PATH = resolve_base_daily()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700;900&family=Noto+Sans:wght@300;400;600;700;900&display=swap');
:root {
    --aji-red:      #D71920;
    --aji-red-dark: #A01218;
    --aji-red-soft: #FDECEA;
    --aji-blue:     #003087;
    --aji-blue-mid: #004DB3;
    --aji-gold:     #C8962A;
    --aji-white:    #FFFFFF;
    --aji-off:      #F8F9FB;
    --aji-border:   #E8EAF0;
    --aji-text:     #1A1C2E;
    --aji-muted:    #6B7280;
    --green:        #1E8449;
    --green-soft:   #E9F7EF;
    --amber:        #B7770D;
    --amber-soft:   #FEF9E7;
    --red-soft:     #FDEDEC;
}
html, body, [class*="css"] { font-family: 'Noto Sans', 'Noto Sans JP', sans-serif !important; }
.main { background-color: var(--aji-off); }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1400px; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1C2E 0%, #0D1B4B 60%, #003087 100%) !important;
    border-right: 3px solid var(--aji-red) !important;
}
[data-testid="stSidebar"] * { color: #E8ECF5 !important; }
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #FFFFFF !important; font-size: 0.85rem !important;
    letter-spacing: 2px !important; text-transform: uppercase !important; font-weight: 700 !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
[data-testid="stSidebar"] label { color: #BDC6E0 !important; font-size: 0.8rem !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] { background-color: var(--aji-red) !important; border-radius: 4px !important; }
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: white !important; border-bottom: 2px solid var(--aji-red) !important;
    border-radius: 8px 8px 0 0 !important; padding: 0 8px !important; gap: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Noto Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 0.82rem !important; letter-spacing: 0.3px !important;
    color: var(--aji-muted) !important; padding: 10px 16px !important;
    border-bottom: 3px solid transparent !important; margin-bottom: -2px !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--aji-red) !important; border-bottom-color: var(--aji-red) !important;
    background: transparent !important;
}
[data-testid="stMetric"] {
    background: white !important; border-radius: 10px !important;
    padding: 18px 20px !important; border: 1px solid var(--aji-border) !important;
    border-top: 3px solid var(--aji-red) !important; box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important; font-weight: 700 !important;
    letter-spacing: 1.2px !important; text-transform: uppercase !important; color: var(--aji-muted) !important;
}
[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 900 !important; color: var(--aji-text) !important; }
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }
[data-testid="stDataFrame"] { border-radius: 8px !important; border: 1px solid var(--aji-border) !important; overflow: hidden !important; }
[data-testid="stDownloadButton"] button, .stButton button {
    background: var(--aji-red) !important; color: white !important;
    border: none !important; border-radius: 6px !important; font-weight: 600 !important; font-size: 0.82rem !important;
}
[data-testid="stDownloadButton"] button:hover, .stButton button:hover { background: var(--aji-red-dark) !important; }
.aji-section {
    font-size: 0.7rem; font-weight: 800; letter-spacing: 2.5px;
    text-transform: uppercase; color: var(--aji-red);
    margin: 1.5rem 0 0.75rem 0; padding-bottom: 6px;
    border-bottom: 2px solid var(--aji-red-soft);
    display: flex; align-items: center; gap: 8px;
}
.aji-section::before { content: ''; display: inline-block; width: 4px; height: 16px; background: var(--aji-red); border-radius: 2px; }
.badge-on-track { background:#E9F7EF; color:#1E8449; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
.badge-behind   { background:#FEF9E7; color:#B7770D; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
.badge-low      { background:#FDEDEC; color:#C0392B; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
.kpi-card { background: white; border-radius: 10px; padding: 16px 20px; border: 1px solid #E8EAF0; border-left: 4px solid var(--aji-red); box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 8px; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: var(--aji-red); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    font=dict(family="Noto Sans, sans-serif", size=12, color="#1A1C2E"),
    paper_bgcolor="white", plot_bgcolor="white",
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font_size=11,
                bgcolor="rgba(255,255,255,0.9)", bordercolor="#E8EAF0", borderwidth=1),
)
AJI_COLORS = ["#D71920","#003087","#C8962A","#1E8449","#7B2FBE",
               "#E67E22","#1A5276","#117A65","#6E2F7F","#B7770D",
               "#2E4057","#E84393","#00B4D8"]
TARGET_MAP = {
    "A5RB": 2016, "Amamiplus": 44, "PTPA 20gr": 1952, "MJCL": 2187,
    "PTCL": 3904, "50G": 1418, "100G": 1575, "Ajiplus": 1260,
    "Ajiplus Ekicho": 1260, "Ajinomoto Plus": 1260, "AJP 200gr": 2016,
    "Ajiplus Premium": 1008, "ekicho 20Kg": 1008, "250RC": 1008,
}
LINE_MAP = {
    "A5RB": "LINE-3", "Amamiplus": "LINE-13", "PTPA 20gr": "LINE-11",
    "MJCL": "LINE-4", "PTCL": "LINE-6", "50G": "LINE-5", "100G": "LINE-10",
    "Ajiplus": "LINE-12", "Ajiplus Ekicho": "LINE-12", "Ajinomoto Plus": "LINE-12",
    "AJP 200gr": "LINE-12", "Ajiplus Premium": "LINE-12", "ekicho 20Kg": "LINE-12",
    "250RC": "LINE-1",
}
MESIN_MAP = {
    "A5RB": "Vertical Packer", "Amamiplus": "YDE", "PTPA 20gr": "UNILOGO",
    "MJCL": "GP C", "PTCL": "GP TT10 E,G,H", "50G": "GP I & K",
    "100G": "GP I & K", "Ajiplus": "SANCO", "Ajiplus Ekicho": "SANCO",
    "Ajinomoto Plus": "SANCO", "AJP 200gr": "SANCO", "Ajiplus Premium": "SANCO",
    "ekicho 20Kg": "YDE", "250RC": "Vertical Packer",
}
BULAN_ID = {1:"Januari",2:"Februari",3:"Maret",4:"April",5:"Mei",6:"Juni",
            7:"Juli",8:"Agustus",9:"September",10:"Oktober",11:"November",12:"Desember"}
MANUAL_FILE = os.path.join(OUTPUT_FOLDER, "manual_production_entry.csv")

# ─────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────
def login_page():
    st.markdown("<style>.main{background:linear-gradient(135deg,#1A1C2E,#003087);min-height:100vh;}</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:40px 36px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
          <div style="color:#D71920;font-size:2rem;font-weight:900;letter-spacing:2px;">AJINOMOTO</div>
          <div style="color:#003087;font-size:0.75rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:24px;">FI-2 Production Monitor</div>
          <hr style="border-color:#F0F2F5;margin-bottom:24px;">
        </div>""", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="Masukkan password...")
        if st.button("🔐  Login", use_container_width=True):
            if password == get_password():
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("❌ Password salah")

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def load_csv(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def load_all_data():
    df_base = load_csv(os.path.basename(resolve_base_daily()))
    df_daily = df_base.copy()
    if os.path.exists(MANUAL_FILE):
        try:
            manual = pd.read_csv(MANUAL_FILE)
            if not manual.empty and "tanggal" in manual.columns:
                manual["_dt"]        = pd.to_datetime(manual["tanggal"], errors="coerce")
                manual["tgl"]        = manual["_dt"].dt.day
                manual["tahun"]      = manual["_dt"].dt.year
                manual["bulan_num"]  = manual["_dt"].dt.month
                manual["bulan"]      = manual["bulan_num"].map(BULAN_ID)
                manual["periode"]    = manual["bulan"] + " " + manual["tahun"].astype(str)
                manual["daily"]      = manual["jumlah_produksi"]
                manual["kategori"]   = "Small/Medium"
                manual["acc"]        = None
                manual["line"]       = manual["produk"].map(LINE_MAP)
                manual["target_day"] = manual["produk"].map(TARGET_MAP)
                for col in ["kg_ctn"]:
                    manual[col] = manual.get("kg_per_ctn", pd.Series([None]*len(manual)))
                if not df_base.empty:
                    cols = df_base.columns.intersection(manual.columns)
                    df_daily = pd.concat([df_base, manual[cols]], ignore_index=True)
                else:
                    df_daily = manual
        except:
            pass

    valid_periods = set()
    if not df_daily.empty and "periode" in df_daily.columns:
        valid_periods = set(df_daily["periode"].dropna().unique())

    def filter_pivot(df):
        if df.empty or not valid_periods or "periode" not in df.columns:
            return df
        return df[df["periode"].isin(valid_periods)].reset_index(drop=True)

    df_ach      = filter_pivot(load_csv("pivot_achievement.csv"))
    df_gap      = filter_pivot(load_csv("pivot_gap_acc_vs_target.csv"))
    df_progress = filter_pivot(load_csv("pivot_progress_latest.csv"))

    return {
        "daily":       df_daily,
        "achievement": df_ach,
        "gap1":        df_gap,
        "progress":    df_progress,
    }

def section(icon, title):
    st.markdown(f'<div class="aji-section">{icon} {title}</div>', unsafe_allow_html=True)

def pct_to_status(pct, thr_green, thr_yellow):
    if pct >= thr_green:  return "ON TRACK"
    if pct >= thr_yellow: return "BEHIND"
    return "LOW"

def apply_period_sort(df, col="periode"):
    if "tahun" in df.columns and "bulan_num" in df.columns:
        order = (df.drop_duplicates([col,"tahun","bulan_num"])
                   .sort_values(["tahun","bulan_num"])[col].tolist())
        df["_sort"] = df[col].map({p: i for i, p in enumerate(order)})
        df = df.sort_values("_sort").drop(columns=["_sort"])
    return df

def recalculate_pivots():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    BASE_DAILY = resolve_base_daily()
    try:
        df_base = pd.read_csv(BASE_DAILY) if os.path.exists(BASE_DAILY) else pd.DataFrame()
        if not df_base.empty and "source" in df_base.columns:
            df_base = df_base[df_base["source"] != "manual"].drop(columns=["source"])
    except:
        df_base = pd.DataFrame()

    df_manual = pd.DataFrame()
    if os.path.exists(MANUAL_FILE):
        try:
            m = pd.read_csv(MANUAL_FILE)
            if not m.empty and "tanggal" in m.columns:
                m["_dt"]       = pd.to_datetime(m["tanggal"], errors="coerce")
                m["tgl"]       = m["_dt"].dt.day
                m["tahun"]     = m["_dt"].dt.year
                m["bulan_num"] = m["_dt"].dt.month
                m["bulan"]     = m["bulan_num"].map(BULAN_ID)
                m["periode"]   = m["bulan"] + " " + m["tahun"].astype(str)
                m["daily"]     = pd.to_numeric(m["jumlah_produksi"], errors="coerce")
                m["acc"]       = None
                m["kategori"]  = "Small/Medium"
                m["line"]      = m["produk"].map(LINE_MAP)
                m["kg_ctn"]    = m.get("kg_per_ctn", pd.Series([None]*len(m)))
                m["target_day"]= m["produk"].map(TARGET_MAP)
                keep = ["bulan_num","bulan","tahun","periode","tgl","kategori",
                        "produk","line","kg_ctn","target_day","daily","acc"]
                df_manual = m[[c for c in keep if c in m.columns]]
        except Exception as e:
            print(f"Warning manual read: {e}")

    dfs = [df for df in [df_base, df_manual] if not df.empty]
    if not dfs:
        return False

    df_all = pd.concat(dfs, ignore_index=True).sort_values(
        ["tahun","bulan_num","tgl","produk"]).reset_index(drop=True)
    df_sm = df_all[df_all["kategori"] == "Small/Medium"].copy()
    df_sm["daily_num"]  = pd.to_numeric(df_sm["daily"], errors="coerce").fillna(0)
    df_sm["acc_recalc"] = df_sm.groupby(["tahun","bulan_num","produk"])["daily_num"].cumsum()
    df_sm["acc"]        = df_sm["acc"].combine_first(df_sm["acc_recalc"])

    pv_acc = (df_sm.dropna(subset=["acc"])
                   .groupby(["tahun","bulan_num","periode","produk"])["acc"]
                   .last().reset_index().sort_values(["tahun","bulan_num"]))

    ach_rows, gap_rows = [], []
    for _, row in pv_acc.iterrows():
        tgt    = TARGET_MAP.get(row["produk"], 1)
        _mask  = (df_sm["periode"] == row["periode"]) & (df_sm["produk"] == row["produk"])
        n_days = max(int((df_sm[_mask]["daily_num"] > 0).sum()), 1)  # hari aktif (daily > 0)
        tgt_kum = tgt * n_days
        pct     = row["acc"] / tgt_kum if tgt_kum > 0 else 0
        status  = "ON TRACK" if pct >= 0.85 else ("BEHIND" if pct >= 0.50 else "LOW")
        ach_rows.append({"tahun":row["tahun"],"bulan_num":row["bulan_num"],
                         "periode":row["periode"],"produk":row["produk"],
                         "acc":row["acc"],"target_day":tgt,"n_hari":n_days,
                         "target_kum":tgt_kum,"achievement":pct,
                         "achievement_pct":round(pct*100,1),"status":status})
        gap_rows.append({"tahun":row["tahun"],"bulan_num":row["bulan_num"],
                         "periode":row["periode"],"produk":row["produk"],
                         "acc":row["acc"],"target_kum":tgt_kum,
                         "gap_acc_vs_target":row["acc"]-tgt_kum})

    df_ach = pd.DataFrame(ach_rows).sort_values(["tahun","bulan_num","produk"])
    df_gap = pd.DataFrame(gap_rows).sort_values(["tahun","bulan_num","produk"])
    last_per = df_ach["periode"].iloc[-1] if not df_ach.empty else None

    df_ach.to_csv(os.path.join(OUTPUT_FOLDER, "pivot_achievement.csv"), index=False)
    df_gap.to_csv(os.path.join(OUTPUT_FOLDER, "pivot_gap_acc_vs_target.csv"), index=False)
    if last_per:
        df_prog = df_ach[df_ach["periode"] == last_per].copy()
        df_prog["progress_bar"] = df_prog["achievement"].apply(
            lambda p: "█"*min(int(p*20),20)+"░"*max(20-int(p*20),0))
        df_prog.to_csv(os.path.join(OUTPUT_FOLDER, "pivot_progress_latest.csv"), index=False)
    return True

def pivot_files_exist():
    for f in ["pivot_achievement.csv","pivot_gap_acc_vs_target.csv","pivot_progress_latest.csv"]:
        p = os.path.join(OUTPUT_FOLDER, f)
        if not os.path.exists(p):
            return False
        try:
            if pd.read_csv(p).empty:
                return False
        except:
            return False
    return True

def force_delete_pivots():
    for f in ["pivot_achievement.csv","pivot_gap_acc_vs_target.csv","pivot_progress_latest.csv"]:
        p = os.path.join(OUTPUT_FOLDER, f)
        if os.path.exists(p):
            os.remove(p)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
def build_sidebar(data):
    st.sidebar.markdown("""
    <div style="text-align:center;padding:12px 0 4px 0;">
      <div style="color:#D71920;font-size:1.3rem;font-weight:900;letter-spacing:2px;">AJINOMOTO</div>
      <div style="color:rgba(255,255,255,0.5);font-size:0.6rem;letter-spacing:2px;">FI-2 PRODUCTION MONITOR</div>
    </div>
    <hr style="margin:10px 0 16px 0;border-color:rgba(215,25,32,0.5);border-width:2px 0 0 0;">
    """, unsafe_allow_html=True)

    df_ach   = data["achievement"]
    df_daily = data["daily"]

    st.sidebar.markdown("## 🔄 Sinkronisasi Data")
    base_exists = os.path.exists(resolve_base_daily())
    pivots_ok   = pivot_files_exist()

    if base_exists and not pivots_ok:
        st.sidebar.warning("⚠️ Pivot belum sinkron dengan data!")
        if st.sidebar.button("🔄  Regenerate Sekarang", key="btn_regen_auto", use_container_width=True):
            force_delete_pivots()
            with st.spinner("⏳ Regenerating pivot..."):
                recalculate_pivots()
            st.cache_data.clear()
            st.rerun()
    else:
        if st.sidebar.button("🔄  Force Regenerate Pivot", key="btn_regen_force", use_container_width=True):
            force_delete_pivots()
            with st.spinner("⏳ Regenerating semua pivot dari data terkini..."):
                ok = recalculate_pivots()
            st.cache_data.clear()
            if ok:
                st.sidebar.success("✅ Pivot berhasil di-regenerate!")
            else:
                st.sidebar.error("❌ Gagal regenerate. Cek data_daily.csv.")
            st.rerun()

    if df_ach.empty:
        st.sidebar.warning("⚠️ Data achievement kosong.")
        return {}, {}

    st.sidebar.divider()
    st.sidebar.markdown("## 🔧 Filter Global")
    st.sidebar.caption("Berlaku untuk semua tab")
    st.sidebar.divider()

    all_periodes = (df_ach.drop_duplicates(["tahun","bulan_num","periode"])
                         .sort_values(["tahun","bulan_num"])["periode"].tolist())
    sel_periodes = st.sidebar.multiselect("📅 Periode (Bulan)", options=all_periodes, default=all_periodes)
    all_produk   = sorted(df_ach["produk"].unique())
    sel_produk   = st.sidebar.multiselect("📦 Produk", options=all_produk, default=all_produk)
    all_lines    = sorted([l for l in df_daily["line"].dropna().unique()]) if not df_daily.empty else []
    sel_lines    = st.sidebar.multiselect("🏭 Line Produksi", options=all_lines, default=all_lines)

    st.sidebar.divider()
    st.sidebar.markdown("**⚙️ Threshold Status**")
    thr_green  = st.sidebar.slider("✅ ON TRACK dari (%)", 50, 100, 85, step=5)
    thr_yellow = st.sidebar.slider("⚠️ BEHIND dari (%)",   10,  80, 50, step=5)

    st.sidebar.divider()
    st.sidebar.markdown(
        '<div style="color:rgba(255,255,255,0.3);font-size:0.65rem;text-align:center;letter-spacing:1px;">'
        'AJINOMOTO CO., INC.<br>Food Ingredients 2 (FI-2)<br>Packaging Monitoring System</div>',
        unsafe_allow_html=True)

    return {"periodes": sel_periodes, "produk": sel_produk, "lines": sel_lines}, \
           {"green": thr_green/100, "yellow": thr_yellow/100}

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
def render_header(data):
    df_ach   = data["achievement"]
    n_bulan  = df_ach["periode"].nunique() if not df_ach.empty else 0
    last_per = (df_ach.sort_values(["tahun","bulan_num"])["periode"].iloc[-1]
                if not df_ach.empty else "—")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#D71920 0%,#A01218 50%,#7A0D12 100%);
                border-radius:12px;padding:24px 32px;margin-bottom:24px;
                position:relative;overflow:hidden;box-shadow:0 4px 20px rgba(215,25,32,0.35);">
      <div style="position:absolute;top:-30px;right:-30px;width:200px;height:200px;
                  background:rgba(255,255,255,0.06);border-radius:50%;"></div>
      <div style="position:relative;display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <div>
          <div style="color:rgba(255,255,255,0.7);font-size:0.7rem;letter-spacing:3px;
                      text-transform:uppercase;font-weight:600;margin-bottom:2px;">
            Food Ingredients 2 (FI-2) · Packaging (Carton)</div>
          <div style="color:white;font-size:1.5rem;font-weight:900;line-height:1.2;">
            Dashboard Monitoring Produksi Harian</div>
          <div style="color:rgba(255,255,255,0.75);font-size:0.8rem;margin-top:4px;">
            Small / Medium Size &amp; Bag Type · Domestik &amp; Export</div>
        </div>
        <div style="margin-left:auto;text-align:right;flex-shrink:0;">
          <div style="color:rgba(255,255,255,0.6);font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;">Data tersedia</div>
          <div style="color:white;font-size:1.3rem;font-weight:800;">{n_bulan} Bulan</div>
          <div style="color:rgba(255,255,255,0.7);font-size:0.75rem;">Terakhir: {last_per}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 1–9 (tidak berubah, copy persis dari v3)
# ─────────────────────────────────────────────────────────────
def tab_overview(data, filters, thr):
    df_ach   = data["achievement"]
    df_daily = data["daily"]
    if df_ach.empty:
        st.warning("Data achievement belum ada.")
        return
    df = df_ach[df_ach["periode"].isin(filters["periodes"]) &
                df_ach["produk"].isin(filters["produk"])].copy()
    if filters["lines"] and not df_daily.empty:
        lp = df_daily[df_daily["line"].isin(filters["lines"])]["produk"].unique()
        df = df[df["produk"].isin(lp)]
    section("📊", "KPI Utama — FI-2 Packaging")
    total_acc   = df["acc"].sum()
    total_tgt   = df["target_kum"].sum()
    overall_pct = total_acc / total_tgt * 100 if total_tgt > 0 else 0
    n_on_track  = int((df.groupby(["periode","produk"])["achievement"].last() >= thr["green"]).sum())
    n_low       = int((df.groupby(["periode","produk"])["achievement"].last() < thr["yellow"]).sum())
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Acc (crt)",     f"{total_acc:,.0f}")
    c2.metric("Target Kumulatif",    f"{total_tgt:,.0f}")
    c3.metric("Overall Achievement", f"{overall_pct:.1f}%",
              delta=f"{overall_pct - thr['green']*100:+.1f}% vs threshold")
    c4.metric("✅ On Track", f"{n_on_track} item")
    c5.metric("🔴 Low",      f"{n_low} item")
    section("⚠️", "Production Risk Indicator")
    df_risk = df.copy()
    df_risk["avg_daily"]       = df_risk["acc"] / df_risk["n_hari"].replace(0,1)
    df_risk["predicted_total"] = df_risk["avg_daily"] * 28
    df_risk["predicted_pct"]   = df_risk["predicted_total"] / df_risk["target_kum"].replace(0,1) * 100
    df_risk["risk_status"]     = df_risk["predicted_pct"].apply(
        lambda x: "🟢 SAFE" if x >= 100 else ("🟡 WATCH" if x >= 85 else "🔴 RISK"))
    n_risk = (df_risk["risk_status"] == "🔴 RISK").sum()
    if n_risk > 0:
        st.error(f"🚨  **{n_risk} produk** diprediksi tidak mencapai target bulan ini")
    else:
        st.success("✅  Semua produk diprediksi mencapai target bulan ini")
    rs = df_risk[["periode","produk","acc","target_kum","predicted_total","predicted_pct","risk_status"]].copy()
    rs.columns = ["Periode","Produk","Acc","Target","Prediksi (crt)","Prediksi %","Risk"]
    rs["Prediksi %"]     = rs["Prediksi %"].apply(lambda x: f"{x:.1f}%")
    rs["Acc"]            = rs["Acc"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
    rs["Target"]         = rs["Target"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
    rs["Prediksi (crt)"] = rs["Prediksi (crt)"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
    st.dataframe(rs.sort_values("Prediksi %"), use_container_width=True, hide_index=True, height=280)
    section("🗺️", "Heatmap % Achievement (Bulan × Produk)")
    st.caption("Hijau = ON TRACK · Kuning = BEHIND · Merah = LOW")
    pivot_heat   = df.pivot_table(index="periode", columns="produk", values="achievement_pct", aggfunc="last")
    periode_order = (df.drop_duplicates(["tahun","bulan_num","periode"])
                       .sort_values(["tahun","bulan_num"])["periode"].tolist())
    pivot_heat   = pivot_heat.reindex([p for p in periode_order if p in pivot_heat.index])
    fig_heat = px.imshow(pivot_heat,
        color_continuous_scale=[(0.0,"#C0392B"),(thr["yellow"],"#FDEBD0"),
            (thr["green"]-0.01,"#FEF9E7"),(thr["green"],"#E9F7EF"),(1.0,"#0E6655")],
        zmin=0, zmax=100, text_auto=".0f", aspect="auto", labels={"color":"% Achievement"})
    fig_heat.update_layout(**PLOTLY_LAYOUT, height=max(280, len(pivot_heat)*38+80))
    fig_heat.update_traces(textfont=dict(size=11))
    st.plotly_chart(fig_heat, use_container_width=True)
    section("📈", "Distribusi Status per Bulan")
    df_s = df.copy()
    df_s["status"] = df_s["achievement"].apply(lambda x: pct_to_status(x, thr["green"], thr["yellow"]))
    sc = df_s.groupby(["periode","status"]).size().reset_index(name="count")
    sc["_ord"] = sc["periode"].map({p: i for i, p in enumerate(periode_order)})
    sc = sc.sort_values("_ord")
    fig_s = px.bar(sc, x="periode", y="count", color="status",
                   color_discrete_map={"ON TRACK":"#1E8449","BEHIND":"#D4AC0D","LOW":"#C0392B"},
                   barmode="stack", labels={"count":"Jumlah Produk","periode":"","status":"Status"})
    fig_s.update_layout(**PLOTLY_LAYOUT, height=300, bargap=0.3)
    st.plotly_chart(fig_s, use_container_width=True)

def tab_daily_production(data, filters, thr):
    df_daily = data["daily"]
    if df_daily.empty:
        st.warning("Data daily belum ada.")
        return
    df = df_daily[(df_daily["kategori"] == "Small/Medium") &
                  df_daily["periode"].isin(filters["periodes"]) &
                  df_daily["produk"].isin(filters["produk"])].copy()
    if filters["lines"]:
        df = df[df["line"].isin(filters["lines"])]
    df["daily_num"]    = pd.to_numeric(df["daily"], errors="coerce").fillna(0)
    df["target_day"]   = pd.to_numeric(df["target_day"], errors="coerce").fillna(0)
    df["vs_target_pct"] = df.apply(lambda r: r["daily_num"]/r["target_day"]*100 if r["target_day"]>0 else 0, axis=1)
    df["status_daily"] = df["vs_target_pct"].apply(lambda x: pct_to_status(x/100, thr["green"], thr["yellow"]))
    section("📦", "Ringkasan Produksi Harian — FI-2 Packaging (Carton)")
    total_prod = df["daily_num"].sum()
    total_tgt  = df["target_day"].sum()
    avg_daily  = df.groupby("tgl")["daily_num"].sum().mean()
    n_hari     = df["tgl"].nunique()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Produksi (crt)",    f"{total_prod:,.0f}")
    c2.metric("Total Target (crt)",      f"{total_tgt:,.0f}")
    c3.metric("Rata-rata Produksi/Hari", f"{avg_daily:,.0f} crt")
    c4.metric("Hari Kerja Tercatat",     f"{n_hari} hari")
    periodes_avail = (df.drop_duplicates(["tahun","bulan_num","periode"])
                        .sort_values(["tahun","bulan_num"])["periode"].tolist())
    if not periodes_avail:
        st.warning("Tidak ada data untuk filter yang dipilih.")
        return
    sel_per = st.selectbox("📅 Pilih Periode untuk Detail Daily:", periodes_avail,
                            index=len(periodes_avail)-1, key="daily_per_sel")
    if not sel_per: return
    df_per = df[df["periode"] == sel_per].copy().sort_values("tgl")
    section("📅", f"Total Produksi Harian vs Target — {sel_per}")
    df_total_day = df_per.groupby("tgl").agg(total_prod=("daily_num","sum"),total_tgt=("target_day","sum")).reset_index()
    fig_total = go.Figure()
    fig_total.add_trace(go.Bar(x=df_total_day["tgl"], y=df_total_day["total_prod"],
        name="Aktual (crt)", marker_color="#003087",
        text=df_total_day["total_prod"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside", textfont=dict(size=9)))
    fig_total.add_trace(go.Scatter(x=df_total_day["tgl"], y=df_total_day["total_tgt"],
        name="Target", mode="lines+markers",
        line=dict(color="#D71920", width=2.5, dash="dot"), marker=dict(size=6)))
    fig_total.update_layout(**PLOTLY_LAYOUT, height=360, xaxis_title="Tanggal", yaxis_title="Carton")
    fig_total.update_xaxes(dtick=2, showgrid=True, gridcolor="#F0F2F5", tickmode="linear",
                           range=[df_total_day["tgl"].min()-0.5, df_total_day["tgl"].max()+0.5])
    fig_total.update_yaxes(showgrid=True, gridcolor="#F0F2F5")
    st.plotly_chart(fig_total, use_container_width=True)
    section("📊", f"Breakdown Produksi per Produk (Stacked) — {sel_per}")
    fig_stack = px.bar(df_per, x="tgl", y="daily_num", color="produk",
                       barmode="stack", color_discrete_sequence=AJI_COLORS,
                       labels={"daily_num":"Carton","tgl":"Tanggal","produk":"Produk"})
    fig_stack.update_layout(**PLOTLY_LAYOUT, height=380)
    fig_stack.update_xaxes(dtick=2, showgrid=True, gridcolor="#F0F2F5")
    fig_stack.update_yaxes(showgrid=True, gridcolor="#F0F2F5")
    st.plotly_chart(fig_stack, use_container_width=True)
    section("🌡️", f"Heatmap Produksi Harian per Produk — {sel_per}")
    pivot_d = df_per.pivot_table(index="produk", columns="tgl", values="vs_target_pct", aggfunc="mean")
    if not pivot_d.empty:
        fig_hd = px.imshow(pivot_d,
            color_continuous_scale=[(0.0,"#C0392B"),(thr["yellow"],"#FDEBD0"),
                (thr["green"]-0.01,"#FEF9E7"),(thr["green"],"#E9F7EF"),(1.0,"#0E6655")],
            zmin=0, zmax=130, text_auto=".0f", aspect="auto",
            labels={"color":"% vs Target","x":"Tanggal","y":"Produk"})
        fig_hd.update_layout(**PLOTLY_LAYOUT, height=max(280, len(pivot_d)*36+80))
        fig_hd.update_traces(textfont=dict(size=9))
        st.plotly_chart(fig_hd, use_container_width=True)
    section("📈", f"Tren Harian per Produk — {sel_per}")
    all_prod_avail = sorted(df_per["produk"].unique())
    sel_prods = st.multiselect("Pilih produk:", all_prod_avail,
                                default=all_prod_avail[:6] if len(all_prod_avail) >= 6 else all_prod_avail,
                                key="daily_prod_sel")
    df_line = df_per[df_per["produk"].isin(sel_prods)].sort_values("tgl")
    fig_line = px.line(df_line, x="tgl", y="daily_num", color="produk", markers=True,
                       color_discrete_sequence=AJI_COLORS,
                       labels={"daily_num":"Carton/Hari","tgl":"Tanggal","produk":"Produk"})
    for i, prod in enumerate(sel_prods):
        tgt_val = TARGET_MAP.get(prod, 0)
        if tgt_val > 0:
            fig_line.add_hline(y=tgt_val, line_dash="dot",
                               line_color=AJI_COLORS[i % len(AJI_COLORS)], line_width=1, opacity=0.4)
    fig_line.update_traces(line=dict(width=2.5))
    fig_line.update_layout(**PLOTLY_LAYOUT, height=420, xaxis_title="Tanggal", yaxis_title="Carton/Hari")
    fig_line.update_xaxes(dtick=2, showgrid=True, gridcolor="#F0F2F5", tickmode="linear", tick0=1)
    fig_line.update_yaxes(showgrid=True, gridcolor="#F0F2F5")
    st.plotly_chart(fig_line, use_container_width=True)
    if "line" in df_per.columns and df_per["line"].notna().any():
        section("🏭", f"Produksi per Line — {sel_per}")
        cl1, cl2 = st.columns(2)
        with cl1:
            df_ls = df_per.groupby("line")["daily_num"].sum().reset_index().sort_values("daily_num", ascending=False)
            fig_lb = px.bar(df_ls, x="line", y="daily_num", color="line",
                            color_discrete_sequence=AJI_COLORS,
                            text=df_ls["daily_num"].apply(lambda x: f"{x:,.0f}"),
                            labels={"daily_num":"Total Carton","line":"Line"})
            fig_lb.update_traces(textposition="outside")
            fig_lb.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False, yaxis_title="Total Carton")
            st.caption("📊 Total per Line"); st.plotly_chart(fig_lb, use_container_width=True)
        with cl2:
            df_ld = df_per.groupby(["tgl","line"])["daily_num"].sum().reset_index()
            fig_lstack = px.bar(df_ld, x="tgl", y="daily_num", color="line",
                                barmode="stack", color_discrete_sequence=AJI_COLORS,
                                labels={"daily_num":"Carton","tgl":"Tanggal","line":"Line"})
            fig_lstack.update_layout(**PLOTLY_LAYOUT, height=320, xaxis_title="Tanggal", yaxis_title="Carton")
            fig_lstack.update_xaxes(dtick=2, tickmode="linear", tick0=1)
            st.caption("📅 Harian per Line (Stacked)"); st.plotly_chart(fig_lstack, use_container_width=True)
    section("🥧", f"Porsi Produksi per Produk — {sel_per}")
    df_pie = df_per.groupby("produk")["daily_num"].sum().reset_index()
    df_pie = df_pie[df_pie["daily_num"] > 0]
    fig_pie = px.pie(df_pie, names="produk", values="daily_num",
                     color_discrete_sequence=AJI_COLORS, hole=0.45)
    fig_pie.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=11))
    fig_pie.update_layout(**PLOTLY_LAYOUT, height=380)
    st.plotly_chart(fig_pie, use_container_width=True)
    section("📋", f"Tabel Data Daily — {sel_per}")
    df_tbl = df_per[["tgl","produk","line","daily_num","target_day","vs_target_pct","status_daily"]].copy()
    df_tbl.columns = ["Tgl","Produk","Line","Produksi (crt)","Target/Hari","% vs Target","Status"]
    df_tbl["% vs Target"]    = df_tbl["% vs Target"].apply(lambda x: f"{x:.1f}%")
    df_tbl["Produksi (crt)"] = df_tbl["Produksi (crt)"].apply(lambda x: f"{x:,.0f}")
    df_tbl["Target/Hari"]    = df_tbl["Target/Hari"].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
    st.dataframe(df_tbl.sort_values(["Tgl","Produk"]), use_container_width=True, hide_index=True, height=360)
    st.download_button("⬇️ Download Data Daily CSV", df_per.to_csv(index=False).encode("utf-8"),
                       file_name=f"daily_{sel_per.replace(' ','_')}.csv", mime="text/csv", key="dl_daily_csv")

def tab_achievement(data, filters, thr):
    df_ach = data["achievement"]
    if df_ach.empty:
        st.warning("Data belum ada.")
        return
    df = df_ach[df_ach["periode"].isin(filters["periodes"]) &
                df_ach["produk"].isin(filters["produk"])].copy()
    df_daily = data["daily"]
    if filters["lines"] and not df_daily.empty:
        lp = df_daily[df_daily["line"].isin(filters["lines"])]["produk"].unique()
        df = df[df["produk"].isin(lp)]
    df["status"] = df["achievement"].apply(lambda x: pct_to_status(x, thr["green"], thr["yellow"]))
    section("📋", "Tabel Detail % Achievement")
    df_d = df[["periode","produk","acc","target_kum","n_hari","achievement_pct","status"]].copy()
    df_d.columns = ["Periode","Produk","Acc","Target Kum.","Hari","% Achieve","Status"]
    df_d["% Achieve"]   = df_d["% Achieve"].apply(lambda x: f"{x:.1f}%")
    df_d["Acc"]         = df_d["Acc"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
    df_d["Target Kum."] = df_d["Target Kum."].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
    st.dataframe(df_d.sort_values(["Periode","Produk"]), use_container_width=True, hide_index=True, height=320)
    st.divider()
    if df.empty: return
    last_per  = df.sort_values(["tahun","bulan_num"])["periode"].iloc[-1]
    section("📊", f"Progress Bar — {last_per}")
    df_last   = df[df["periode"] == last_per].sort_values("achievement_pct", ascending=False)
    half      = len(df_last) // 2 + len(df_last) % 2
    col_l, col_r = st.columns(2)
    def render_bar(row, container):
        pct = min(row["achievement_pct"], 100)
        color = ("#1E8449" if row["achievement"] >= thr["green"]
                 else "#D4AC0D" if row["achievement"] >= thr["yellow"] else "#C0392B")
        badge_cls = ("badge-on-track" if row["status"]=="ON TRACK"
                     else "badge-behind" if row["status"]=="BEHIND" else "badge-low")
        container.markdown(f"""
        <div style="background:white;border-radius:8px;padding:10px 14px;margin-bottom:8px;
                    border:1px solid #E8EAF0;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-weight:700;font-size:0.82rem;color:#1A1C2E;">{row['produk']}</span>
            <span class="{badge_cls}">{row['status']}</span>
          </div>
          <div style="background:#F0F2F5;border-radius:6px;height:14px;overflow:hidden;margin-bottom:4px;">
            <div style="width:{pct:.1f}%;background:{color};height:100%;border-radius:6px;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;">
            <span style="font-size:0.72rem;color:#6B7280;">Acc: {row['acc']:,.0f} crt</span>
            <span style="font-size:0.78rem;font-weight:800;color:{color};">{row['achievement_pct']:.1f}%</span>
          </div>
        </div>""", unsafe_allow_html=True)
    rows_list = list(df_last.iterrows())
    for _, row in rows_list[:half]:  render_bar(row, col_l)
    for _, row in rows_list[half:]:  render_bar(row, col_r)
    st.divider()
    section("📈", "Tren % Achievement per Bulan")
    df = apply_period_sort(df)
    fig = px.line(df, x="periode", y="achievement_pct", color="produk", markers=True,
                  color_discrete_sequence=AJI_COLORS,
                  labels={"achievement_pct":"% Achievement","periode":"","produk":"Produk"})
    fig.add_hline(y=thr["green"]*100, line_dash="dot", line_color="#1E8449", line_width=1.5,
                  annotation_text=f"ON TRACK {thr['green']*100:.0f}%", annotation_font_color="#1E8449")
    fig.add_hline(y=thr["yellow"]*100, line_dash="dot", line_color="#D4AC0D", line_width=1.5,
                  annotation_text=f"BEHIND {thr['yellow']*100:.0f}%", annotation_font_color="#D4AC0D")
    fig.add_hrect(y0=thr["green"]*100, y1=105, fillcolor="#E9F7EF", opacity=0.3, line_width=0)
    fig.add_hrect(y0=0, y1=thr["yellow"]*100, fillcolor="#FDEDEC", opacity=0.3, line_width=0)
    fig.update_layout(**PLOTLY_LAYOUT, height=420)
    st.plotly_chart(fig, use_container_width=True)

def tab_gap(data, filters):
    st.info("**Gap** = Acc − Target Kumulatif  |  Positif = melebihi target 🟢 · Negatif = di bawah target 🔴")
    df_g = data["gap1"]
    if df_g.empty:
        st.warning("Data Gap belum ada.")
        return
    df = df_g[df_g["periode"].isin(filters["periodes"]) &
              df_g["produk"].isin(filters["produk"])].copy()
    df_daily = data["daily"]
    if filters["lines"] and not df_daily.empty:
        lp = df_daily[df_daily["line"].isin(filters["lines"])]["produk"].unique()
        df = df[df["produk"].isin(lp)]
    df = apply_period_sort(df)
    section("📋", "Tabel Gap Acc vs Target")
    dc = df[["periode","produk","acc","target_kum","gap_acc_vs_target"]].copy()
    dc.columns = ["Periode","Produk","Acc","Target Kum.","Gap"]
    for c in ["Acc","Target Kum.","Gap"]:
        dc[c] = dc[c].apply(lambda x: f"{x:+,.0f}" if pd.notna(x) else "—")
    st.dataframe(dc, use_container_width=True, hide_index=True, height=280)
    section("📊", "Gap per Produk — Bulan Terakhir")
    last = df["periode"].iloc[-1] if not df.empty else None
    if last:
        dl   = df[df["periode"] == last].sort_values("gap_acc_vs_target")
        clrs = ["#C0392B" if x < 0 else "#1E8449" for x in dl["gap_acc_vs_target"]]
        fig  = go.Figure(go.Bar(x=dl["produk"], y=dl["gap_acc_vs_target"], marker_color=clrs,
                                text=dl["gap_acc_vs_target"].apply(lambda x: f"{x:+,.0f}"),
                                textposition="outside", textfont=dict(size=11)))
        fig.add_hline(y=0, line_color="#1A1C2E", line_width=1.5)
        fig.update_layout(**PLOTLY_LAYOUT, height=360,
                          title=dict(text=f"Gap Acc vs Target — {last}", font_color="#D71920"))
        st.plotly_chart(fig, use_container_width=True)

def tab_tren(data, filters):
    df_daily = data["daily"]
    if df_daily.empty:
        st.warning("Data daily belum ada.")
        return
    df = df_daily[(df_daily["kategori"] == "Small/Medium") &
                  df_daily["periode"].isin(filters["periodes"]) &
                  df_daily["produk"].isin(filters["produk"])].copy()
    if filters["lines"]:
        df = df[df["line"].isin(filters["lines"])]
    all_prod = sorted(df["produk"].unique())
    sel = st.multiselect("Pilih produk:", all_prod,
                         default=all_prod[:5] if len(all_prod) >= 5 else all_prod, key="tren_produk")
    df_t = df[df["produk"].isin(sel)].dropna(subset=["daily"])
    section("📅", "Tren Daily dalam Satu Bulan")
    periodes_avail = (df.drop_duplicates(["tahun","bulan_num","periode"])
                        .sort_values(["tahun","bulan_num"])["periode"].tolist())
    if not periodes_avail:
        st.warning("Tidak ada data untuk filter yang dipilih.")
        return
    sel_bln = st.selectbox("Pilih bulan:", periodes_avail, index=len(periodes_avail)-1, key="tren_bln")
    if not sel_bln: return
    df_bln = df_t[df_t["periode"] == sel_bln].sort_values("tgl")
    fig1 = px.line(df_bln, x="tgl", y="daily", color="produk", markers=True,
                   color_discrete_sequence=AJI_COLORS,
                   labels={"daily":"Carton/Hari","tgl":"Tanggal","produk":"Produk"})
    fig1.update_traces(line=dict(width=2.5))
    fig1.update_layout(**PLOTLY_LAYOUT, height=380)
    fig1.update_xaxes(dtick=2, showgrid=True, gridcolor="#F0F2F5")
    st.plotly_chart(fig1, use_container_width=True)
    section("📆", "Total Produksi per Bulan")
    df_m = df_t.groupby(["tahun","bulan_num","periode","produk"])["daily"].sum().reset_index()
    df_m = apply_period_sort(df_m)
    fig2 = px.line(df_m, x="periode", y="daily", color="produk", markers=True,
                   color_discrete_sequence=AJI_COLORS,
                   labels={"daily":"Total Carton/Bulan","periode":"","produk":"Produk"})
    fig2.update_layout(**PLOTLY_LAYOUT, height=380)
    st.plotly_chart(fig2, use_container_width=True)
    if "line" in df_t.columns:
        section("🏭", "Perbandingan Produksi per Line")
        df_line = df_t.dropna(subset=["line"]).groupby(["periode","line"])["daily"].sum().reset_index()
        df_line = apply_period_sort(df_line)
        fig3 = px.bar(df_line, x="periode", y="daily", color="line", barmode="stack",
                      color_discrete_sequence=AJI_COLORS,
                      labels={"daily":"Total Carton","periode":"","line":"Line"})
        fig3.update_layout(**PLOTLY_LAYOUT, height=340)
        st.plotly_chart(fig3, use_container_width=True)

def import_numpy_std(lst):
    import numpy as np
    return float(np.std(lst))

def tab_forecasting(data, filters, thr):
    import numpy as np
    df_ach   = data["achievement"]
    df_daily = data["daily"]
    if df_ach.empty or df_daily.empty:
        st.warning("Data belum cukup untuk forecasting.")
        return
    df_a = df_ach[df_ach["produk"].isin(filters["produk"])].copy()
    df_d = df_daily[(df_daily["kategori"] == "Small/Medium") &
                    df_daily["produk"].isin(filters["produk"])].copy()
    if filters["lines"]:
        lp = df_daily[df_daily["line"].isin(filters["lines"])]["produk"].unique()
        df_a = df_a[df_a["produk"].isin(lp)]
        df_d = df_d[df_d["produk"].isin(lp)]
    df_monthly = (df_d.dropna(subset=["daily"])
                      .groupby(["tahun","bulan_num","periode","produk"])["daily"]
                      .sum().reset_index().sort_values(["tahun","bulan_num"]))
    all_products = sorted(df_monthly["produk"].unique())
    wma_rows = []
    for prod in all_products:
        hist = df_monthly[df_monthly["produk"] == prod].sort_values(["tahun","bulan_num"])
        vals = hist["daily"].tolist()
        pers = hist["periode"].tolist()
        if len(vals) < 2:
            pred = vals[-1] if vals else 0
            conf = "rendah"
        else:
            n       = min(len(vals), 6)
            recent  = vals[-n:]
            weights = list(range(1, n+1))
            pred    = sum(w*v for w,v in zip(weights,recent)) / sum(weights)
            std_val = import_numpy_std(recent)
            mean_val = sum(recent)/len(recent) if recent else 1
            cv      = std_val / mean_val if mean_val > 0 else 0
            conf    = "tinggi" if cv < 0.10 else ("sedang" if cv < 0.25 else "rendah")
        last_row  = hist.iloc[-1]
        next_bnum = last_row["bulan_num"] % 12 + 1
        next_thn  = last_row["tahun"] + (1 if last_row["bulan_num"] == 12 else 0)
        next_per  = f"{BULAN_ID[next_bnum]} {next_thn}"
        tgt_kum   = TARGET_MAP.get(prod, 0) * 26
        pred_pct  = pred / tgt_kum * 100 if tgt_kum > 0 else 0
        wma_rows.append({"produk":prod,"bulan_terakhir":pers[-1] if pers else "-",
                         "n_bulan_data":len(vals),"prediksi_next":round(pred),
                         "periode_prediksi":next_per,"target_kum":tgt_kum,
                         "prediksi_pct":round(pred_pct,1),"confidence":conf})
    df_wma = pd.DataFrame(wma_rows)
    section("🔮", "Prediksi Bulan Depan — Weighted Moving Average")
    if not df_wma.empty:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Prediksi",     f"{df_wma['prediksi_next'].sum():,.0f} crt")
        c2.metric("Rata-rata % Target", f"{df_wma['prediksi_pct'].mean():.1f}%")
        c3.metric("✅ Diprediksi Aman",  f"{(df_wma['prediksi_pct']>=thr['green']*100).sum()} produk")
        c4.metric("🔴 Diprediksi Risk",  f"{(df_wma['prediksi_pct']<thr['yellow']*100).sum()} produk")
        df_wma_show = df_wma[["produk","n_bulan_data","prediksi_next","target_kum","prediksi_pct","confidence"]].copy()
        df_wma_show.columns = ["Produk","Data (bln)","Prediksi (crt)","Target (crt)","Prediksi %","Confidence"]
        df_wma_show["Prediksi (crt)"] = df_wma_show["Prediksi (crt)"].apply(lambda x: f"{x:,.0f}")
        df_wma_show["Target (crt)"]   = df_wma_show["Target (crt)"].apply(lambda x: f"{x:,.0f}")
        df_wma_show["Prediksi %"]     = df_wma_show["Prediksi %"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_wma_show, use_container_width=True, hide_index=True, height=300)
    section("📐", "Prediksi Target Bulan Ini — Linear Regression")
    periodes_avail = (df_d.drop_duplicates(["tahun","bulan_num","periode"])
                          .sort_values(["tahun","bulan_num"])["periode"].tolist())
    if not periodes_avail:
        st.warning("Tidak ada data untuk filter yang dipilih.")
        return
    sel_per_lr = st.selectbox("Pilih bulan:", periodes_avail, index=len(periodes_avail)-1, key="lr_per")
    if not sel_per_lr: return
    df_bulan = df_d[df_d["periode"] == sel_per_lr].dropna(subset=["daily"]).copy()
    df_bulan["daily_num"] = pd.to_numeric(df_bulan["daily"], errors="coerce").fillna(0)
    df_bulan = df_bulan.sort_values(["produk","tgl"])
    df_bulan["acc_cum"] = df_bulan.groupby("produk")["daily_num"].cumsum()
    lr_rows = []
    fig_lr  = go.Figure()
    for i, prod in enumerate(sorted(df_bulan["produk"].unique())):
        df_p = df_bulan[df_bulan["produk"] == prod].sort_values("tgl")
        if len(df_p) < 2: continue
        x = df_p["tgl"].values.astype(float)
        y = df_p["acc_cum"].values.astype(float)
        n = len(x)
        b = (n*np.sum(x*y) - np.sum(x)*np.sum(y)) / (n*np.sum(x**2) - np.sum(x)**2 + 1e-10)
        a = (np.sum(y) - b*np.sum(x)) / n
        y_pred   = max(a + b*28.0, float(y[-1]))
        y_mean   = np.mean(y)
        ss_tot   = np.sum((y-y_mean)**2)
        ss_res   = np.sum((y-(a+b*x))**2)
        r2       = max(0.0, min(1.0, 1 - ss_res/(ss_tot+1e-10)))
        tgt_kum  = TARGET_MAP.get(prod,0) * 28
        pred_pct = y_pred / tgt_kum * 100 if tgt_kum > 0 else 0
        gap      = y_pred - tgt_kum
        status   = pct_to_status(pred_pct/100, thr["green"], thr["yellow"])
        hari_skrg   = int(x[-1])
        sisa_hari   = max(28-hari_skrg, 0)
        daily_needed = (tgt_kum - float(y[-1])) / sisa_hari if sisa_hari > 0 else 0
        lr_rows.append({"produk":prod,"hari_ke":hari_skrg,"acc_skrg":round(float(y[-1])),
                        "prediksi_akhir":round(y_pred),"target_kum":tgt_kum,
                        "prediksi_pct":round(pred_pct,1),"gap":round(gap),
                        "daily_needed":round(daily_needed),"r2":round(r2,3),"status_pred":status})
        color  = AJI_COLORS[i%len(AJI_COLORS)]
        x_line = np.linspace(1,28,28)
        y_line = a + b*x_line
        fig_lr.add_trace(go.Scatter(x=x.tolist(),y=y.tolist(),mode="lines+markers",name=prod,
                                    line=dict(color=color,width=2.5),marker=dict(size=6),legendgroup=prod))
        fig_lr.add_trace(go.Scatter(x=x_line.tolist(),y=y_line.tolist(),mode="lines",
                                    name=f"{prod} (trend)",line=dict(color=color,width=1.5,dash="dot"),
                                    legendgroup=prod,showlegend=False))
    fig_lr.update_layout(**PLOTLY_LAYOUT, height=420,
                         title=dict(text=f"Acc Kumulatif + Garis Tren — {sel_per_lr}", font_color="#D71920"),
                         xaxis_title="Tanggal", yaxis_title="Acc Kumulatif (crt)")
    fig_lr.update_xaxes(dtick=2, showgrid=True, gridcolor="#F0F2F5")
    fig_lr.update_yaxes(showgrid=True, gridcolor="#F0F2F5")
    st.plotly_chart(fig_lr, use_container_width=True)
    if lr_rows:
        df_lr = pd.DataFrame(lr_rows).sort_values("prediksi_pct", ascending=False)
        df_lr_show = df_lr[["produk","hari_ke","acc_skrg","prediksi_akhir","target_kum",
                             "prediksi_pct","gap","daily_needed","r2","status_pred"]].copy()
        df_lr_show.columns = ["Produk","Hari ke-","Acc Skrg","Prediksi Akhir",
                               "Target","Prediksi %","Gap","Daily Needed*","R²","Status"]
        for c in ["Acc Skrg","Prediksi Akhir","Target","Gap","Daily Needed*"]:
            df_lr_show[c] = df_lr_show[c].apply(lambda x: f"{x:,.0f}")
        df_lr_show["Prediksi %"] = df_lr_show["Prediksi %"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_lr_show, use_container_width=True, hide_index=True, height=340)
        st.caption("*Daily Needed = produksi/hari yang dibutuhkan agar target tercapai · R² mendekati 1.0 = lebih akurat")

def tab_data_raw(data, filters):
    section("🗃️", "Data Mentah & Export CSV")
    dataset_map = {
        "Data Daily (Harian)":             ("daily",       os.path.basename(resolve_base_daily())),
        "Pivot % Achievement":             ("achievement", "pivot_achievement.csv"),
        "Pivot Gap Acc vs Target":         ("gap1",        "pivot_gap_acc_vs_target.csv"),
        "Pivot Progress (Bulan Terakhir)": ("progress",    "pivot_progress_latest.csv"),
    }
    choice  = st.selectbox("Pilih dataset:", list(dataset_map.keys()), key="raw_choice")
    key, fn = dataset_map[choice]
    df_show = data[key].copy() if key in data else pd.DataFrame()
    if df_show.empty:
        st.warning(f"`{fn}` belum ada.")
        return
    if "periode" in df_show.columns:
        df_show = df_show[df_show["periode"].isin(filters["periodes"])]
    if "produk" in df_show.columns:
        df_show = df_show[df_show["produk"].isin(filters["produk"])]
    if "line" in df_show.columns and filters["lines"]:
        df_show = df_show[df_show["line"].isin(filters["lines"])]
    c1, c2 = st.columns([3, 1])
    c1.markdown(f"**{len(df_show):,} baris** · {len(df_show.columns)} kolom")
    c2.download_button(f"⬇️ Download {fn}", df_show.to_csv(index=False).encode("utf-8"),
                       file_name=fn, mime="text/csv", key="dl_raw_csv")
    st.dataframe(df_show, use_container_width=True, height=420)

def tab_data_entry(data):
    section("✏️", "Input Produksi Harian — FI-2 Packaging")
    produk_from_data = list(data["achievement"]["produk"].unique()) if not data["achievement"].empty else []
    produk_list = sorted(set(produk_from_data) | set(TARGET_MAP.keys()))
    mesin_list  = ["Vertical Packer","YDE","SANCO","UNILOGO","GP C","GP TT10 E,G,H","GP I & K"]
    line_list   = [f"LINE-{i}" for i in range(1, 14)] + ["LINE-PTPA"]
    with st.form("form_entry", clear_on_submit=True):
        st.markdown("**📝 Isi form di bawah ini:**")
        c1, c2 = st.columns(2)
        with c1:
            tanggal  = st.date_input("📅 Tanggal")
            produk   = st.selectbox("📦 Jenis Produk", produk_list)
            mesin    = st.selectbox("⚙️ Jenis Mesin", mesin_list)
            line     = st.selectbox("🏭 Line Produksi", line_list)
        with c2:
            jumlah   = st.number_input("📊 Jumlah Produksi (crt)", min_value=0, step=10)
            operator = st.text_input("👤 Operator / PIC")
            kg_ctn   = st.number_input("⚖️ KG / CTN", min_value=0.0, step=0.1, format="%.2f")
            target   = st.number_input("🎯 Target Harian (crt)", min_value=0, step=10,
                                       value=int(TARGET_MAP.get(produk, 0)) if produk in TARGET_MAP else 0)
        catatan   = st.text_area("📝 Catatan (opsional)", placeholder="Misal: mesin mati 2 jam, ganti roll...")
        submitted = st.form_submit_button("💾  Simpan Data", use_container_width=True)
        if submitted:
            new_row = pd.DataFrame({
                "tanggal":        [str(tanggal)],
                "produk":         [produk],
                "mesin":          [mesin],
                "line":           [line],
                "jumlah_produksi":[jumlah],
                "operator":       [operator],
                "kg_per_ctn":     [kg_ctn],
                "target":         [target],
                "catatan":        [catatan],
            })
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            if os.path.exists(MANUAL_FILE):
                existing = pd.read_csv(MANUAL_FILE)
                new_row  = pd.concat([existing, new_row], ignore_index=True)
            new_row.to_csv(MANUAL_FILE, index=False)
            with st.spinner("⏳ Mengupdate pivot & visualisasi..."):
                ok = recalculate_pivots()
            st.cache_data.clear()
            if ok:
                st.success(f"✅ Data {produk} ({tanggal}) tersimpan & semua chart sudah diupdate!")
            else:
                st.warning("Data tersimpan tapi pivot gagal diupdate.")
            st.rerun()

def tab_kelola_data():
    section("🗂️", "Kelola Data Entry — Lihat, Edit & Hapus")
    st.caption("Di sini Anda bisa melihat semua data yang sudah diinput secara manual, menghapus baris yang salah, atau mendownload untuk koreksi offline.")
    if not os.path.exists(MANUAL_FILE):
        st.info("📭 Belum ada data entry manual. Silahkan input data di tab **Data Entry** dulu.")
        return
    try:
        df_m = pd.read_csv(MANUAL_FILE)
    except Exception as e:
        st.error(f"Gagal membaca file: {e}"); return
    if df_m.empty:
        st.info("📭 File kosong. Belum ada data yang diinput.")
        return
    df_m = df_m.reset_index(drop=True)
    df_m.insert(0, "ID", range(1, len(df_m)+1))
    total = df_m["jumlah_produksi"].sum() if "jumlah_produksi" in df_m.columns else 0
    tgt   = df_m["target"].sum() if "target" in df_m.columns else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Baris Data", f"{len(df_m):,}")
    c2.metric("Total Produksi",   f"{total:,.0f} crt")
    c3.metric("Total Target",     f"{tgt:,.0f} crt")
    c4.metric("Achievement",      f"{total/tgt*100:.1f}%" if tgt > 0 else "—")
    st.divider()
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        produk_filter  = st.multiselect("Filter Produk:",  sorted(df_m["produk"].unique())  if "produk"  in df_m.columns else [], key="kelola_produk")
    with col_f2:
        tanggal_filter = st.multiselect("Filter Tanggal:", sorted(df_m["tanggal"].unique()) if "tanggal" in df_m.columns else [], key="kelola_tgl")
    with col_f3:
        line_filter    = st.multiselect("Filter Line:",    sorted(df_m["line"].unique())    if "line"    in df_m.columns else [], key="kelola_line")
    df_view = df_m.copy()
    if produk_filter:  df_view = df_view[df_view["produk"].isin(produk_filter)]
    if tanggal_filter: df_view = df_view[df_view["tanggal"].isin(tanggal_filter)]
    if line_filter and "line" in df_view.columns:
        df_view = df_view[df_view["line"].isin(line_filter)]
    st.markdown(f"**Menampilkan {len(df_view):,} dari {len(df_m):,} baris**")
    col_order = ["ID","tanggal","produk","line","mesin","jumlah_produksi","target","operator","kg_per_ctn","catatan"]
    col_exist  = [c for c in col_order if c in df_view.columns]
    st.dataframe(df_view[col_exist].sort_values("tanggal", ascending=False),
                 use_container_width=True, hide_index=True, height=340)
    st.divider()
    section("🗑️", "Hapus Data yang Salah Input")
    st.warning("⚠️ **Perhatian:** Penghapusan data bersifat permanen.")
    del_col1, del_col2 = st.columns([2, 1])
    with del_col1:
        id_to_delete = st.multiselect(
            "Pilih ID baris yang ingin dihapus:",
            options=df_view["ID"].tolist(),
            format_func=lambda x: f"ID {x} — {df_m[df_m['ID']==x]['tanggal'].values[0]} | {df_m[df_m['ID']==x]['produk'].values[0]} | {df_m[df_m['ID']==x]['jumlah_produksi'].values[0]:,.0f} crt" if x in df_m["ID"].values else str(x),
            key="id_hapus")
    with del_col2:
        if id_to_delete:
            for iid in id_to_delete:
                row = df_m[df_m["ID"] == iid]
                if not row.empty:
                    st.markdown(f"- ID {iid}: `{row['tanggal'].values[0]}` · `{row['produk'].values[0]}`")
    if id_to_delete:
        konfirmasi = st.checkbox(f"✅ Konfirmasi hapus {len(id_to_delete)} baris", key="konfirm_hapus")
        if st.button("🗑️  Hapus Data Terpilih", disabled=not konfirmasi, key="btn_hapus"):
            idx_to_drop = [i-1 for i in id_to_delete]
            df_orig = pd.read_csv(MANUAL_FILE)
            df_orig = df_orig.drop(index=idx_to_drop).reset_index(drop=True)
            df_orig.to_csv(MANUAL_FILE, index=False)
            force_delete_pivots()
            with st.spinner("⏳ Menghapus data & mengupdate visualisasi..."):
                recalculate_pivots()
            st.cache_data.clear()
            st.success(f"✅ {len(id_to_delete)} baris berhasil dihapus!")
            st.rerun()
    st.divider()
    section("☠️", "Reset Semua Data Entry Manual")
    with st.expander("⚠️ Bahaya Zone — Hapus SEMUA data entry manual"):
        st.error("Ini akan menghapus **seluruh** data yang sudah diinput manual. Tidak bisa di-undo!")
        confirm_all = st.text_input("Ketik **HAPUS SEMUA** untuk konfirmasi:", key="confirm_hapus_all")
        if st.button("🚨  Reset Semua Data Entry", key="btn_hapus_all"):
            if confirm_all == "HAPUS SEMUA":
                os.remove(MANUAL_FILE)
                force_delete_pivots()
                recalculate_pivots()
                st.cache_data.clear()
                st.success("✅ Semua data entry manual sudah dihapus.")
                st.rerun()
            else:
                st.error("Konfirmasi salah. Ketik HAPUS SEMUA dengan tepat.")
    st.divider()
    section("📊", "Visualisasi Data Entry Manual")
    if len(df_m) > 0:
        vc1, vc2 = st.columns(2)
        with vc1:
            df_byline = df_m.groupby("line")["jumlah_produksi"].sum().reset_index() if "line" in df_m.columns else pd.DataFrame()
            if not df_byline.empty:
                fig_vl = px.bar(df_byline.sort_values("jumlah_produksi",ascending=False), x="line", y="jumlah_produksi",
                                color="line", color_discrete_sequence=AJI_COLORS,
                                text=df_byline.sort_values("jumlah_produksi",ascending=False)["jumlah_produksi"].apply(lambda x: f"{x:,.0f}"),
                                labels={"jumlah_produksi":"Carton","line":"Line"})
                fig_vl.update_traces(textposition="outside")
                fig_vl.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False, yaxis_title="Carton")
                st.caption("📊 Total Produksi per Line"); st.plotly_chart(fig_vl, use_container_width=True)
        with vc2:
            if "produk" in df_m.columns:
                df_byprod = df_m.groupby("produk")["jumlah_produksi"].sum().reset_index()
                fig_vp = px.pie(df_byprod, names="produk", values="jumlah_produksi",
                                color_discrete_sequence=AJI_COLORS, hole=0.4)
                fig_vp.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=10))
                fig_vp.update_layout(**PLOTLY_LAYOUT, height=300)
                st.caption("🥧 Share per Produk"); st.plotly_chart(fig_vp, use_container_width=True)
        if "tanggal" in df_m.columns:
            df_bytgl = df_m.groupby("tanggal")["jumlah_produksi"].sum().reset_index().sort_values("tanggal")
            fig_tgl  = px.bar(df_bytgl, x="tanggal", y="jumlah_produksi",
                              color_discrete_sequence=["#003087"],
                              labels={"jumlah_produksi":"Carton","tanggal":"Tanggal"})
            fig_tgl.update_layout(**PLOTLY_LAYOUT, height=300)
            st.caption("📅 Produksi per Tanggal (Data Entry)"); st.plotly_chart(fig_tgl, use_container_width=True)
    st.download_button("⬇️ Download Semua Data Entry (CSV)",
                       df_m.drop(columns=["ID"]).to_csv(index=False).encode("utf-8"),
                       file_name="manual_production_entry.csv", mime="text/csv", key="dl_manual_csv")

# ─────────────────────────────────────────────────────────────
# TAB 10: KELOLA BASE DATA  ← v4: DUAL MODE EDIT
# ─────────────────────────────────────────────────────────────
def tab_kelola_base_data():
    section("🗄️", "Kelola Semua Data — Base & Manual Entry")
    st.caption("Hapus atau edit data berdasarkan periode — baik dari pipeline (base) maupun dari input manual.")
    BASE_DAILY = resolve_base_daily()
    try:
        df_base = pd.read_csv(BASE_DAILY) if os.path.exists(BASE_DAILY) else pd.DataFrame()
    except:
        df_base = pd.DataFrame()

    df_manual_raw = pd.DataFrame()
    df_manual_fmt = pd.DataFrame()
    if os.path.exists(MANUAL_FILE):
        try:
            df_manual_raw = pd.read_csv(MANUAL_FILE)
            if not df_manual_raw.empty and "tanggal" in df_manual_raw.columns:
                m = df_manual_raw.copy()
                m["_dt"]       = pd.to_datetime(m["tanggal"], errors="coerce")
                m["tgl"]       = m["_dt"].dt.day
                m["tahun"]     = m["_dt"].dt.year
                m["bulan_num"] = m["_dt"].dt.month
                m["bulan"]     = m["bulan_num"].map(BULAN_ID)
                m["periode"]   = m["bulan"] + " " + m["tahun"].astype(str)
                m["daily"]     = pd.to_numeric(m["jumlah_produksi"], errors="coerce")
                m["source"]    = "manual"
                m["line"]      = m["produk"].map(LINE_MAP)
                df_manual_fmt  = m[["tahun","bulan_num","periode","tgl","produk","line","daily","source"]]
        except:
            pass

    if not df_base.empty and "source" not in df_base.columns:
        df_base["source"] = "base"
    if not df_manual_fmt.empty:
        df_manual_fmt["source"] = "manual"

    dfs_all = [df for df in [
        df_base[["tahun","bulan_num","periode","tgl","produk","line","daily","source"]]
            if not df_base.empty and all(c in df_base.columns for c in ["tahun","bulan_num","periode"]) else pd.DataFrame(),
        df_manual_fmt
    ] if not df.empty]
    if not dfs_all:
        st.warning("Tidak ada data sama sekali.")
        return

    df_combined  = pd.concat(dfs_all, ignore_index=True)
    periode_list = (df_combined.drop_duplicates(["tahun","bulan_num","periode"])
                               .sort_values(["tahun","bulan_num"])["periode"].tolist())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Baris (Base)",   f"{len(df_base):,}")
    c2.metric("Total Baris (Manual)", f"{len(df_manual_raw):,}")
    c3.metric("Total Periode",        f"{len(periode_list)}")
    c4.metric("Periode Tersedia",     f"{periode_list[-1] if periode_list else '-'}")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # ✏️ EDIT BASE DATA — DUAL MODE: SINGLE ROW vs BULK EDIT
    # ══════════════════════════════════════════════════════════════
    section("✏️", "Edit Baris Base Data (Pipeline)")

    if df_base.empty:
        st.info("Tidak ada base data untuk diedit.")
    else:
        # ── Filter bersama untuk kedua mode ─────────────────────
        all_produk_edit = sorted(df_base["produk"].unique()) if "produk" in df_base.columns else []
        all_lines_edit  = sorted(df_base["line"].dropna().unique()) if "line" in df_base.columns else []
        base_periode_list_edit = (
            df_base.drop_duplicates(["tahun","bulan_num","periode"])
                   .sort_values(["tahun","bulan_num"])["periode"].tolist()
            if all(c in df_base.columns for c in ["tahun","bulan_num","periode"]) else [])

        ef1, ef2, ef3 = st.columns(3)
        with ef1: edit_f_per  = st.multiselect("Filter Periode:", base_periode_list_edit, key="edit_f_per")
        with ef2: edit_f_prod = st.multiselect("Filter Produk:",  all_produk_edit,        key="edit_f_prod")
        with ef3: edit_f_line = st.multiselect("Filter Line:",    all_lines_edit,         key="edit_f_line")

        df_edit_base = df_base.drop(columns=["source"], errors="ignore").copy()
        if edit_f_per:  df_edit_base = df_edit_base[df_edit_base["periode"].isin(edit_f_per)]
        if edit_f_prod: df_edit_base = df_edit_base[df_edit_base["produk"].isin(edit_f_prod)]
        if edit_f_line: df_edit_base = df_edit_base[df_edit_base["line"].isin(edit_f_line)]

        st.markdown(f"**{len(df_edit_base):,} baris ditemukan**")

        # ── Toggle mode ─────────────────────────────────────────
        edit_mode = st.radio(
            "Mode Edit:",
            options=["Edit 1 baris via form", "Edit banyak baris sekaligus"],
            horizontal=True,
            key="edit_mode_radio"
        )

        # ════════════════════════════════════════════════════════
        # MODE 1: SINGLE ROW (original behaviour, unchanged)
        # ════════════════════════════════════════════════════════
        if edit_mode.startswith("✏️"):
            df_edit_filtered = df_edit_base.reset_index().rename(columns={"index": "_orig_idx"})
            df_edit_filtered.insert(0, "No", range(1, len(df_edit_filtered)+1))

            show_edit_cols = ["No","_orig_idx","periode","tgl","produk","line","daily","acc","target_day","kategori"]
            show_edit_cols = [c for c in show_edit_cols if c in df_edit_filtered.columns]
            st.dataframe(
                df_edit_filtered[show_edit_cols].rename(columns={"_orig_idx":"Index Asli"}),
                use_container_width=True, hide_index=True, height=260
            )

            if not df_edit_filtered.empty:
                edit_label_map = {
                    row["_orig_idx"]: (
                        f"Idx {row['_orig_idx']} — {row.get('periode','?')} | "
                        f"Tgl {row.get('tgl','?')} | {row.get('produk','?')} | "
                        f"Daily: {row.get('daily',0):,.0f} crt"
                    )
                    for _, row in df_edit_filtered.iterrows()
                }
                sel_edit_idx = st.selectbox(
                    "🔍 Pilih baris yang ingin diedit (pilih satu):",
                    options=[None] + df_edit_filtered["_orig_idx"].tolist(),
                    format_func=lambda x: "— Pilih baris —" if x is None else edit_label_map.get(x, str(x)),
                    key="sel_edit_idx"
                )

                if sel_edit_idx is not None:
                    row_data = df_base.loc[sel_edit_idx].copy()
                    st.markdown("""
                    <div style="background:#EBF5FB;border-radius:10px;padding:14px 18px;
                                border-left:4px solid #003087;margin:12px 0;">
                      <div style="font-weight:700;color:#003087;font-size:0.82rem;">✏️ FORM EDIT BARIS</div>
                      <div style="color:#6B7280;font-size:0.75rem;margin-top:2px;">Ubah nilai yang perlu dikoreksi.</div>
                    </div>""", unsafe_allow_html=True)

                    with st.form("form_edit_base_single", clear_on_submit=False):
                        ec1, ec2, ec3 = st.columns(3)
                        with ec1:
                            st.markdown("**📅 Waktu**")
                            curr_tgl = int(row_data.get("tgl", 1)) if pd.notna(row_data.get("tgl")) else 1
                            new_tgl  = st.number_input("Tanggal (tgl)", min_value=1, max_value=31, value=curr_tgl, key="edit_tgl")
                            curr_bln = int(row_data.get("bulan_num", 1)) if pd.notna(row_data.get("bulan_num")) else 1
                            new_bln  = st.selectbox("Bulan", options=list(BULAN_ID.keys()),
                                                    format_func=lambda x: f"{x} — {BULAN_ID[x]}",
                                                    index=curr_bln - 1, key="edit_bln")
                            curr_thn = int(row_data.get("tahun", 2024)) if pd.notna(row_data.get("tahun")) else 2024
                            new_thn  = st.number_input("Tahun", min_value=2020, max_value=2030, value=curr_thn, key="edit_thn")
                        with ec2:
                            st.markdown("**📦 Produk & Line**")
                            all_produk_form = sorted(set(list(TARGET_MAP.keys())) |
                                                     (set(df_base["produk"].unique()) if "produk" in df_base.columns else set()))
                            curr_prod = str(row_data.get("produk", "")) if pd.notna(row_data.get("produk")) else ""
                            prod_idx  = all_produk_form.index(curr_prod) if curr_prod in all_produk_form else 0
                            new_prod  = st.selectbox("Produk", all_produk_form, index=prod_idx, key="edit_prod")
                            all_lines_form = sorted(set([f"LINE-{i}" for i in range(1, 14)] +
                                                        (list(df_base["line"].dropna().unique()) if "line" in df_base.columns else [])))
                            curr_line = str(row_data.get("line", "")) if pd.notna(row_data.get("line")) else ""
                            line_idx  = all_lines_form.index(curr_line) if curr_line in all_lines_form else 0
                            new_line  = st.selectbox("Line", all_lines_form, index=line_idx, key="edit_line")
                            kategori_opts = ["Small/Medium", "Bag Type"]
                            curr_kat  = str(row_data.get("kategori", "Small/Medium")) if pd.notna(row_data.get("kategori")) else "Small/Medium"
                            kat_idx   = kategori_opts.index(curr_kat) if curr_kat in kategori_opts else 0
                            new_kat   = st.selectbox("Kategori", kategori_opts, index=kat_idx, key="edit_kat")
                        with ec3:
                            st.markdown("**📊 Angka Produksi**")
                            curr_daily  = float(row_data.get("daily", 0)) if pd.notna(row_data.get("daily")) else 0.0
                            new_daily   = st.number_input("Daily (crt)", min_value=0.0, step=10.0, value=curr_daily, key="edit_daily")
                            curr_acc    = float(row_data.get("acc", 0)) if pd.notna(row_data.get("acc")) else 0.0
                            new_acc     = st.number_input("Acc Kumulatif (crt)", min_value=0.0, step=10.0, value=curr_acc, key="edit_acc")
                            curr_tgt    = float(row_data.get("target_day", 0)) if pd.notna(row_data.get("target_day")) else 0.0
                            new_tgt_day = st.number_input("Target Harian (crt)", min_value=0.0, step=10.0, value=curr_tgt, key="edit_tgt")
                            curr_kgctn  = float(row_data.get("kg_ctn", 0)) if pd.notna(row_data.get("kg_ctn", None)) else 0.0
                            new_kgctn   = st.number_input("KG / CTN", min_value=0.0, step=0.1, format="%.2f", value=curr_kgctn, key="edit_kgctn")

                        st.divider()
                        new_bulan   = BULAN_ID[new_bln]
                        new_periode = f"{new_bulan} {new_thn}"
                        pc1, pc2 = st.columns(2)
                        with pc1:
                            st.markdown("**Nilai Sebelum:**")
                            st.markdown(f"""<div style="background:#FEF9E7;border-radius:8px;padding:10px 14px;font-size:0.8rem;">
                              Periode: <b>{row_data.get('periode','—')}</b><br>
                              Tgl: <b>{row_data.get('tgl','—')}</b> | Produk: <b>{row_data.get('produk','—')}</b><br>
                              Daily: <b>{row_data.get('daily',0):,.0f}</b> crt | Acc: <b>{row_data.get('acc',0):,.0f}</b> crt
                            </div>""", unsafe_allow_html=True)
                        with pc2:
                            st.markdown("**Nilai Sesudah:**")
                            st.markdown(f"""<div style="background:#E9F7EF;border-radius:8px;padding:10px 14px;font-size:0.8rem;">
                              Periode: <b>{new_periode}</b><br>
                              Tgl: <b>{new_tgl}</b> | Produk: <b>{new_prod}</b><br>
                              Daily: <b>{new_daily:,.0f}</b> crt | Acc: <b>{new_acc:,.0f}</b> crt
                            </div>""", unsafe_allow_html=True)

                        save_edit = st.form_submit_button("💾  Simpan Perubahan", use_container_width=True, type="primary")
                        if save_edit:
                            df_base_upd = pd.read_csv(BASE_DAILY)
                            df_base_upd.loc[sel_edit_idx, "tgl"]        = new_tgl
                            df_base_upd.loc[sel_edit_idx, "bulan_num"]  = new_bln
                            df_base_upd.loc[sel_edit_idx, "bulan"]      = new_bulan
                            df_base_upd.loc[sel_edit_idx, "tahun"]      = new_thn
                            df_base_upd.loc[sel_edit_idx, "periode"]    = new_periode
                            df_base_upd.loc[sel_edit_idx, "produk"]     = new_prod
                            df_base_upd.loc[sel_edit_idx, "line"]       = new_line
                            df_base_upd.loc[sel_edit_idx, "kategori"]   = new_kat
                            df_base_upd.loc[sel_edit_idx, "daily"]      = new_daily
                            df_base_upd.loc[sel_edit_idx, "acc"]        = new_acc
                            df_base_upd.loc[sel_edit_idx, "target_day"] = new_tgt_day
                            if "kg_ctn" in df_base_upd.columns:
                                df_base_upd.loc[sel_edit_idx, "kg_ctn"] = new_kgctn
                            df_base_upd.drop(columns=["source"], errors="ignore").to_csv(BASE_DAILY, index=False)
                            force_delete_pivots()
                            with st.spinner("⏳ Menyimpan & mengupdate visualisasi..."):
                                recalculate_pivots()
                            st.cache_data.clear()
                            st.success(f"✅ Update berhasil! Periode: {new_periode} | Produk: {new_prod} | Daily: {new_daily:,.0f} crt")
                            st.rerun()

        # ════════════════════════════════════════════════════════
        # MODE 2: BULK EDIT via st.data_editor
        # ════════════════════════════════════════════════════════
        else:
            st.markdown("""
            <div style="background:#EBF5FB;border-radius:10px;padding:14px 18px;
                        border-left:4px solid #003087;margin:12px 0 16px 0;">
              <div style="font-weight:700;color:#003087;font-size:0.82rem;letter-spacing:0.5px;">
                📋 BULK EDIT — Edit Langsung di Tabel
              </div>
              <div style="color:#6B7280;font-size:0.77rem;margin-top:4px;">
                Klik sel yang ingin diubah, ketik nilai baru, lalu klik <b>💾 Simpan Semua Perubahan</b>.
                Gunakan filter di atas untuk mempersempit baris yang ditampilkan.
                Kolom yang bisa diedit: <b>tgl, produk, line, kategori, daily, acc, target_day, kg_ctn</b>.
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Kolom yang bisa diedit & tipe datanya
            all_produk_opts  = sorted(set(list(TARGET_MAP.keys())) |
                                      (set(df_base["produk"].unique()) if "produk" in df_base.columns else set()))
            all_lines_opts   = sorted(set([f"LINE-{i}" for i in range(1, 14)] +
                                          (list(df_base["line"].dropna().unique()) if "line" in df_base.columns else [])))
            kategori_opts    = ["Small/Medium", "Bag Type"]

            # Siapkan dataframe dengan index asli tersimpan
            df_bulk = df_edit_base.reset_index().rename(columns={"index": "_orig_idx"})

            # Kolom yang ditampilkan di editor (exclude kolom internal)
            EDITABLE_COLS = ["_orig_idx", "periode", "tgl", "produk", "line",
                             "kategori", "daily", "acc", "target_day", "kg_ctn"]
            display_cols  = [c for c in EDITABLE_COLS if c in df_bulk.columns]

            # Definisi kolom untuk data_editor
            col_config = {
                "_orig_idx":  st.column_config.NumberColumn("Index Asli", disabled=True, width="small"),
                "periode":    st.column_config.TextColumn("Periode", disabled=True, width="medium"),
                "tgl":        st.column_config.NumberColumn("Tgl", min_value=1, max_value=31, step=1, width="small"),
                "produk":     st.column_config.SelectboxColumn("Produk",   options=all_produk_opts, width="medium"),
                "line":       st.column_config.SelectboxColumn("Line",     options=all_lines_opts,  width="small"),
                "kategori":   st.column_config.SelectboxColumn("Kategori", options=kategori_opts,   width="medium"),
                "daily":      st.column_config.NumberColumn("Daily (crt)",      min_value=0, step=1,   width="medium"),
                "acc":        st.column_config.NumberColumn("Acc (crt)",         min_value=0, step=1,   width="medium"),
                "target_day": st.column_config.NumberColumn("Target/Hari (crt)", min_value=0, step=1,   width="medium"),
                "kg_ctn":     st.column_config.NumberColumn("KG/CTN",            min_value=0, step=0.1, format="%.2f", width="small"),
            }
            # Hanya sertakan kolom yang ada
            col_config_filtered = {k: v for k, v in col_config.items() if k in display_cols}

            # Simpan snapshot sebelum edit ke session state
            snapshot_key = "bulk_edit_snapshot"
            if snapshot_key not in st.session_state:
                st.session_state[snapshot_key] = df_bulk[display_cols].copy()

            edited_df = st.data_editor(
                df_bulk[display_cols],
                column_config=col_config_filtered,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",       # tidak boleh tambah/hapus baris di sini
                key="bulk_editor",
                height=min(600, max(300, len(df_bulk) * 35 + 40)),
            )

            # Deteksi perubahan
            original_snap = st.session_state[snapshot_key]
            # Bandingkan kolom numerik & string yang bisa berubah
            compare_cols = [c for c in display_cols if c != "_orig_idx"]
            try:
                changed_mask = ~edited_df[compare_cols].eq(original_snap[compare_cols]).all(axis=1)
                n_changed    = int(changed_mask.sum())
            except Exception:
                n_changed = 0
                changed_mask = pd.Series([False] * len(edited_df))

            if n_changed > 0:
                st.markdown(
                    f'<div style="background:#FEF9E7;border-radius:8px;padding:8px 14px;'
                    f'border-left:4px solid #C8962A;margin:8px 0;font-size:0.82rem;">'
                    f'⚠️ <b>{n_changed} baris</b> telah diubah — klik tombol di bawah untuk menyimpan.</div>',
                    unsafe_allow_html=True
                )
            else:
                st.caption("ℹ️ Belum ada perubahan terdeteksi.")

            bc1, bc2, bc3 = st.columns([2, 1, 1])
            with bc1:
                save_bulk = st.button(
                    f"💾  Simpan Semua Perubahan ({n_changed} baris berubah)",
                    disabled=(n_changed == 0),
                    key="btn_save_bulk",
                    type="primary",
                    use_container_width=True
                )
            with bc2:
                if st.button("↩️  Reset Tampilan", key="btn_reset_bulk", use_container_width=True):
                    # Hapus snapshot sehingga data_editor refresh dari base
                    if snapshot_key in st.session_state:
                        del st.session_state[snapshot_key]
                    st.rerun()
            with bc3:
                st.download_button(
                    "⬇️ Download Preview",
                    edited_df.to_csv(index=False).encode("utf-8"),
                    file_name="bulk_edit_preview.csv",
                    mime="text/csv",
                    key="dl_bulk_preview",
                    use_container_width=True
                )

            if save_bulk:
                # Load fresh dari disk, terapkan perubahan per orig_idx
                df_base_upd = pd.read_csv(BASE_DAILY)
                rows_updated = 0

                for _, edited_row in edited_df.iterrows():
                    orig_idx = int(edited_row["_orig_idx"])
                    if orig_idx not in df_base_upd.index:
                        continue
                    for col in compare_cols:
                        if col in df_base_upd.columns and col in edited_row:
                            df_base_upd.at[orig_idx, col] = edited_row[col]
                    rows_updated += 1

                # Recalculate periode / bulan dari tgl + bulan_num + tahun jika berubah
                # (periode = bulan + " " + tahun)
                if "bulan_num" in df_base_upd.columns and "tahun" in df_base_upd.columns:
                    df_base_upd["bulan"]   = df_base_upd["bulan_num"].map(BULAN_ID)
                    df_base_upd["periode"] = df_base_upd["bulan"] + " " + df_base_upd["tahun"].astype(str)

                df_base_upd.drop(columns=["source"], errors="ignore").to_csv(BASE_DAILY, index=False)
                force_delete_pivots()

                with st.spinner(f"⏳ Menyimpan {rows_updated} baris & mengupdate visualisasi..."):
                    recalculate_pivots()

                st.cache_data.clear()
                # Reset snapshot agar tabel refresh
                if snapshot_key in st.session_state:
                    del st.session_state[snapshot_key]

                st.success(f"✅ {rows_updated} baris berhasil disimpan! Semua chart sudah diupdate.")
                st.rerun()

    st.divider()

    # ══════════════════════════════════════════════════════
    # HAPUS PER PERIODE
    # ══════════════════════════════════════════════════════
    section("🗓️", "Hapus Data Berdasarkan Periode")
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        sel_periode_del = st.multiselect("Pilih periode yang ingin dihapus:", options=periode_list,
                                         key="del_periode_sel", placeholder="Contoh: Maret 2026...")
    if sel_periode_del:
        n_base   = len(df_base[df_base["periode"].isin(sel_periode_del)]) if not df_base.empty and "periode" in df_base.columns else 0
        n_manual = len(df_manual_fmt[df_manual_fmt["periode"].isin(sel_periode_del)]) if not df_manual_fmt.empty else 0
        n_total  = n_base + n_manual
        with col_p2:
            st.markdown(f"""<div style="background:#FDEDEC;border-radius:8px;padding:12px 16px;border-left:4px solid #C0392B;margin-top:4px;">
              <div style="font-size:0.75rem;color:#C0392B;font-weight:700;">AKAN DIHAPUS</div>
              <div style="font-size:1.4rem;font-weight:900;color:#C0392B;">{n_total:,} baris</div>
              <div style="font-size:0.7rem;color:#6B7280;">Base: {n_base} · Manual: {n_manual}</div>
              <div style="font-size:0.7rem;color:#6B7280;">{', '.join(sel_periode_del)}</div>
            </div>""", unsafe_allow_html=True)
        df_preview = df_combined[df_combined["periode"].isin(sel_periode_del)]
        with st.expander(f"👁️ Preview {n_total} baris yang akan dihapus"):
            st.dataframe(df_preview[["source","periode","tgl","produk","line","daily"]].sort_values(["source","tgl"]),
                         use_container_width=True, hide_index=True, height=280)
        konfirm_per = st.checkbox(f"✅ Konfirmasi hapus {n_total:,} baris dari: {', '.join(sel_periode_del)}", key="konfirm_del_periode")
        if st.button("🗑️  Hapus Periode Terpilih", disabled=not konfirm_per, key="btn_del_periode", type="primary"):
            deleted_from = []
            if n_base > 0 and not df_base.empty:
                df_base_baru = df_base[~df_base["periode"].isin(sel_periode_del)].drop(columns=["source"], errors="ignore").reset_index(drop=True)
                df_base_baru.to_csv(BASE_DAILY, index=False)
                deleted_from.append(f"{n_base} baris dari base")
            if n_manual > 0 and not df_manual_raw.empty:
                df_manual_raw["_dt"]  = pd.to_datetime(df_manual_raw["tanggal"], errors="coerce")
                df_manual_raw["_bln"] = df_manual_raw["_dt"].dt.month
                df_manual_raw["_thn"] = df_manual_raw["_dt"].dt.year
                df_manual_raw["_per"] = df_manual_raw["_bln"].map(BULAN_ID) + " " + df_manual_raw["_thn"].astype(str)
                df_manual_baru = df_manual_raw[~df_manual_raw["_per"].isin(sel_periode_del)].drop(
                    columns=["_dt","_bln","_thn","_per"], errors="ignore").reset_index(drop=True)
                df_manual_baru.to_csv(MANUAL_FILE, index=False)
                deleted_from.append(f"{n_manual} baris dari manual entry")
            force_delete_pivots()
            with st.spinner("⏳ Mengupdate semua visualisasi..."):
                recalculate_pivots()
            st.cache_data.clear()
            st.success(f"✅ Berhasil hapus: {' + '.join(deleted_from)}. Semua chart sudah diupdate!")
            st.rerun()

    st.divider()

    # ══════════════════════════════════════════════════════
    # HAPUS BARIS SPESIFIK
    # ══════════════════════════════════════════════════════
    section("🔍", "Hapus Baris Spesifik dari Base Data (Pipeline)")
    st.caption("Untuk hapus baris spesifik dari manual entry, gunakan tab **🗂️ Kelola Data**.")
    if df_base.empty:
        st.info("Tidak ada base data.")
    else:
        fa, fb, fc = st.columns(3)
        base_periode_list = (df_base.drop_duplicates(["tahun","bulan_num","periode"])
                                    .sort_values(["tahun","bulan_num"])["periode"].tolist()
                             if all(c in df_base.columns for c in ["tahun","bulan_num","periode"]) else [])
        with fa: f_per  = st.multiselect("Filter Periode:", base_periode_list, key="base_f_per")
        with fb:
            all_prod = sorted(df_base["produk"].unique()) if "produk" in df_base.columns else []
            f_prod = st.multiselect("Filter Produk:", all_prod, key="base_f_prod")
        with fc:
            all_lines = sorted(df_base["line"].dropna().unique()) if "line" in df_base.columns else []
            f_line = st.multiselect("Filter Line:", all_lines, key="base_f_line")
        df_filtered = df_base.drop(columns=["source"], errors="ignore").copy()
        if f_per:  df_filtered = df_filtered[df_filtered["periode"].isin(f_per)]
        if f_prod: df_filtered = df_filtered[df_filtered["produk"].isin(f_prod)]
        if f_line: df_filtered = df_filtered[df_filtered["line"].isin(f_line)]
        df_filtered = df_filtered.reset_index()
        df_filtered.rename(columns={"index": "_orig_idx"}, inplace=True)
        df_filtered.insert(0, "No", range(1, len(df_filtered)+1))
        st.markdown(f"**{len(df_filtered):,} baris ditemukan**")
        show_cols = ["No","_orig_idx","periode","tgl","produk","line","daily","acc","target_day"]
        show_cols = [c for c in show_cols if c in df_filtered.columns]
        st.dataframe(df_filtered[show_cols].rename(columns={"_orig_idx":"Index Asli"}),
                     use_container_width=True, hide_index=True, height=280)
        if not df_filtered.empty:
            label_map = {
                row["_orig_idx"]: f"Idx {row['_orig_idx']} — {row.get('periode','?')} | Tgl {row.get('tgl','?')} | {row.get('produk','?')} | {row.get('daily',0):,.0f} crt"
                for _, row in df_filtered.iterrows()
            }
            sel_idx = st.multiselect("Pilih baris yang ingin dihapus:",
                                     options=df_filtered["_orig_idx"].tolist(),
                                     format_func=lambda x: label_map.get(x, str(x)), key="base_sel_idx")
            if sel_idx:
                konfirm_row = st.checkbox(f"✅ Konfirmasi hapus {len(sel_idx)} baris ini", key="konfirm_del_rows")
                if st.button("🗑️  Hapus Baris Terpilih", disabled=not konfirm_row, key="btn_del_rows"):
                    df_base_baru = df_base.drop(index=sel_idx).drop(columns=["source"], errors="ignore").reset_index(drop=True)
                    df_base_baru.to_csv(BASE_DAILY, index=False)
                    force_delete_pivots()
                    with st.spinner("⏳ Mengupdate visualisasi..."):
                        recalculate_pivots()
                    st.cache_data.clear()
                    st.success(f"✅ {len(sel_idx)} baris berhasil dihapus dari base data!")
                    st.rerun()

    st.divider()
    section("⬇️", "Download Base Data Terkini")
    if not df_base.empty:
        st.download_button("⬇️ Download data_daily.csv",
                           df_base.drop(columns=["source"], errors="ignore").to_csv(index=False).encode("utf-8"),
                           file_name=os.path.basename(resolve_base_daily()), mime="text/csv", key="dl_base_csv")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    base_path = resolve_base_daily()
    if os.path.exists(base_path) and not pivot_files_exist():
        with st.spinner("⏳ Data dideteksi belum sinkron — regenerating pivot otomatis..."):
            recalculate_pivots()
        st.cache_data.clear()
        st.rerun()

    data = load_all_data()

    if all(v.empty for v in data.values()):
        st.error("❌ Data belum ada. Jalankan pipeline atau gunakan tab Data Entry untuk input manual.")
        if st.button("▶️  Run Pipeline", key="btn_run_pipeline"):
            with st.spinner("⏳ Menjalankan pipeline_excel_to_csv.py ..."):
                result = subprocess.run(
                    ["python", "pipeline_excel_to_csv.py"],
                    capture_output=True,
                    text=True
                )
            if result.returncode == 0:
                st.success("✅ Pipeline berhasil dijalankan. Silakan refresh dashboard.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"❌ Pipeline gagal:\n```\n{result.stderr}\n```")
        return

    render_header(data)
    filters, thresholds = build_sidebar(data)
    if not filters:
        return

    tabs = st.tabs([
        "Overview", "Daily Production", "Achievement", "Gap Analysis",
        "Tren Produksi", "Forecasting", "Data & Export",
        "Data Entry", "Kelola Data", "Kelola Base Data",
    ])
    with tabs[0]: tab_overview(data, filters, thresholds)
    with tabs[1]: tab_daily_production(data, filters, thresholds)
    with tabs[2]: tab_achievement(data, filters, thresholds)
    with tabs[3]: tab_gap(data, filters)
    with tabs[4]: tab_tren(data, filters)
    with tabs[5]: tab_forecasting(data, filters, thresholds)
    with tabs[6]: tab_data_raw(data, filters)
    with tabs[7]: tab_data_entry(data)
    with tabs[8]: tab_kelola_data()
    with tabs[9]: tab_kelola_base_data()

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        login_page()
    else:
        main()
