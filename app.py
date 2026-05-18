import streamlit as st
import pandas as pd
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Agenda Kegiatan Kantor",
    page_icon="📅",
    layout="wide"
)

# =========================
# CUSTOM CSS MOBILE FRIENDLY
# =========================
st.markdown("""
<style>
.main {
    padding-top: 0.5rem;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 600px; /* Membuat tampilan pas & fokus di layar HP */
    margin: 0 auto;
}
.agenda-card {
    background-color: white;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border-left: 6px solid #2563eb;
}
.agenda-judul {
    font-size: 18px;
    font-weight: bold;
    color: #111827;
    margin-bottom: 8px;
}
.agenda-detail {
    font-size: 14px;
    color: #4b5563;
    margin-top: 4px;
    display: flex;
    align-items: center;
}
.agenda-tanggal {
    color: #2563eb;
    font-weight: 600;
}
.empty-box {
    text-align: center;
    padding: 40px;
    border-radius: 14px;
    background-color: #f3f4f6;
    color: #6b7280;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# GANTI DENGAN LINK GOOGLE SHEET ANDA
# =========================
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1sak_dmVop0yWI9tOCtJ_rfqcapUI3CekXGduUHE7sMo/edit?usp=sharing"

# =========================
# KONVERSI LINK GOOGLE SHEET KE CSV
# =========================
def convert_google_sheet_url(url):
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    except IndexError:
        st.error("Format Link Google Sheets tidak valid. Pastikan link disalin dengan benar.")
        st.stop()

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=60) # Cache diperbarui setiap 1 menit agar data baru cepat muncul
def load_data():
    csv_url = convert_google_sheet_url(GOOGLE_SHEET_URL)
    df = pd.read_csv(csv_url)
    
    # Memastikan kolom Tanggal terbaca dengan benar
    df["Tanggal_Clean"] = pd.to_datetime(
        df["Tanggal"],
        format="%d-%m-%Y",
        errors="coerce"
    )
    
    # Mengisi kolom Hari otomatis berdasarkan input tanggal
    hari_indonesia = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }
    df["Hari"] = df["Tanggal_Clean"].dt.day_name().map(hari_indonesia)
    
    # Sorting data dari jam paling pagi
    if "Jam" in df.columns:
        df = df.sort_values(by=["Tanggal_Clean", "Jam"])
    else:
        df = df.sort_values(by=["Tanggal_Clean"])
        
    return df

# =========================
# LOAD DATAFRAME EXECUTION
# =========================
if GOOGLE_SHEET_URL == "SALIN_LINK_GOOGLE_SHEETS_ANDA_DI_SINI":
    st.info("👋 Selamat Datang! Silakan masukkan link Google Sheets Anda pada kode app.py terlebih dahulu.")
    st.stop()

try:
    df = load_data()
except Exception as e:
    st.error("Gagal mengambil data dari Google Sheets. Pastikan akses Google Sheets sudah diatur ke 'Siapa saja yang memiliki link' (Viewer).")
    st.stop()

# =========================
# HEADER UTAMA
# =========================
st.title("📅 Agenda Kegiatan Kantor")
st.write(f"Waktu Sistem: {datetime.now().strftime('%d-%m-%Y | %H:%M')}")
st.markdown("---")

# =========================
# FILTER LOGIC
# =========================
today = pd.Timestamp.today().normalize()
bulan_ini = today.month
tahun_ini = today.year

agenda_hari_ini = df[df["Tanggal_Clean"].dt.normalize() == today]
agenda_bulan_ini = df[
    (df["Tanggal_Clean"].dt.month == bulan_ini) & 
    (df["Tanggal_Clean"].dt.year == tahun_ini)
]

# =========================
# FUNCTION TAMPI…
