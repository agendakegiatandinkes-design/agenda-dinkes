import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ==========================================
# CONFIG UTAMA
# ==========================================
st.set_page_config(
    page_title="Agenda Kegiatan Kantor",
    page_icon="📅",
    layout="wide"
)

# ==========================================
# CUSTOM CSS (AMAN UNTUK PYTHON 3.14)
# ==========================================
css_aman = "<style>[data-testid='stHeader'] {background-color: rgba(0,0,0,0);} .block-container {padding-top: 2rem; padding-bottom: 2rem;} h1 {font-size: 24px !important; font-weight: 700; color: #1E293B; margin-bottom: 5px;} .meta-text {font-size: 13px; color: #64748B; margin-bottom: 20px;} .card {background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 16px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);} .card-title {font-size: 16px !important; font-weight: 600; color: #0F172A; margin-bottom: 6px;} .card-meta {font-size: 13px; color: #475569; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;} .badge {display: inline-block; padding: 3px 8px; font-size: 11px; font-weight: 600; border-radius: 6px; text-transform: uppercase;} .badge-terlaksana {background-color: #DCFCE7; color: #15803D;} .badge-mendatang {background-color: #DBEAFE; color: #1D4ED8;} .badge-hariini {background-color: #FEF3C7; color: #D97706;}</style>"
st.markdown(css_aman, unsafe_html=True)

# ==========================================
# OTOMATIS MENCARI & MEMUAT FILE DATABASE CSV
# ==========================================
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

if csv_files:
    df = pd.read_csv(csv_files[0])
    df.columns = df.columns.str.strip().str.lower()
    df["tanggal_clean"] = pd.to_datetime(df["tanggal"], format="%d-%m-%Y", errors="coerce")
    df = df.sort_values(by=["tanggal_clean"])
else:
    st.error("Waduh! File database CSV belum ditemukan di GitHub. Silakan upload file CSV agenda Anda ke folder yang sama dengan app.py terlebih dahulu.")
    st.stop()

# ==========================================
# HEADER APLIKASI
# ==========================================
st.title("📅 Agenda Kegiatan Kantor")
st.write(f"Waktu Sistem: {datetime.now().strftime('%d-%m-%Y | %H:%M')}")
st.markdown("---")

today = pd.Timestamp.today().normalize()

hari_indonesia = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
}
bulan_indonesia = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

def format_tgl_indo(dt):
    if pd.isna(dt): return "-"
    hari = hari_indonesia[dt.strftime('%A')]
    tgl = dt.day
    bln = bulan_indonesia[dt.month]
    thn = dt.year
    return f"{hari}, {tgl} {bln} {thn}"

# ==========================================
# TABS NAVIGASI UTAMA
# ==========================================
tab1, tab2, tab3 = st.tabs(["📌 Semua Agenda", "🚀 Akan Datang", "✅ Selesai"])

def render_cards(dataframe):
    if dataframe.empty:
        st.info("Tidak ada agenda dalam kategori ini.")
        return
    for _, row in dataframe.iterrows():
        tgl_clean = row['tanggal_clean']
        tgl_display = format_tgl_indo(tgl_clean)
        jam_display = str(row.get('jam', '-')) if pd.notna(row.get('jam')) else '-'
        kegiatan = str(row.get('kegiatan', 'Tanpa Nama Kegiatan'))
        tempat = str(row.get('tempat', '-'))
        pakaian = str(row.get('pakaian', '-'))
        keterangan = str(row.get('keterangan', '-'))
        
        if pd.isna(tgl_clean):
            status_badge = '<span class="badge badge-mendatang">Agenda</span>'
        elif tgl_clean.normalize() < today:
            status_badge = '<span class="badge badge-terlaksana">Selesai</span>'
        elif tgl_clean.normalize() == today:
            status_badge = '<span class="badge badge-hariini">Hari Ini</span>'
        else:
            status_badge = '<span class="badge badge-mendatang">Akan Datang</span>'
            
        card_html = (
            f"<div class='card'>"
            f"<div style='display: flex; justify-content: space-between; align-items: start;'>"
            f"<div class='card-title'>{kegiatan}</div>"
            f"{status_badge}"
            f"</div>"
            f"<div class='card-meta'>📅 <b>{tgl_display}</b> &nbsp;|&nbsp; ⏰ {jam_display} WIB</div>"
            f"<div class='card-meta'>📍 Tempat: {tempat}</div>"
            f"<div class='card-meta'>👔 Pakaian: {pakaian}</div>"
            f"<div class='card-meta' style='color: #64748B; margin-top: 4px; font-style: italic;'>📝 Ket: {keterangan}</div>"
            f"</div>"
        )
        st.markdown(card_html, unsafe_html=True)

with tab1:
    render_cards(df)

with tab2:
    if not df.empty:
        df_mendatang = df[df["tanggal_clean"].normalize() >= today]
    else:
        df_mendatang = df
    render_cards(df_mendatang)

with tab3:
    if not df.empty:
        df_selesai = df[df["tanggal_clean"].normalize() < today]
    else:
        df_selesai = df
    render_cards(df_selesai)
