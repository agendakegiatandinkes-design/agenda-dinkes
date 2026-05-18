import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Pengaturan Halaman Utama
st.set_page_config(
    page_title="Agenda Dinas Kesehatan Kota Parepare",
    page_icon="📅",
    layout="wide"
)

# Custom CSS untuk mempercantik tampilan tabel agar mirip dengan gambar acuan
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .status-selesai {
        background-color: #E8F5E9; color: #2E7D32; padding: 4px 12px;
        border-radius: 12px; font-weight: bold; font-size: 13px; text-align: center;
    }
    .status-datang {
        background-color: #FFEBEE; color: #C62828; padding: 4px 12px;
        border-radius: 12px; font-weight: bold; font-size: 13px; text-align: center;
    }
    .status-hariini {
        background-color: #FFF3E0; color: #EF6C00; padding: 4px 12px;
        border-radius: 12px; font-weight: bold; font-size: 13px; text-align: center;
    }
    th { background-color: #F8F9FA !important; color: #495057 !important; font-weight: bold !important; }
    </style>
""", unsafe_html=True)

# 2. Memuat File Database CSV
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

if csv_files:
    df = pd.read_csv(csv_files[0])
    df.columns = df.columns.str.strip().str.lower()
    
    # Bersihkan data kosong (NaN) awal
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace("nan", "-")
        
    df["tanggal_clean"] = pd.to_datetime(df["tanggal"], format="%d-%m-%Y", errors="coerce")
    df = df.sort_values(by=["tanggal_clean"])
else:
    st.error("File database CSV belum ditemukan di GitHub.")
    st.stop()

# 3. Header Atas
st.title("🏢 Dinas Kesehatan Kota Parepare")
st.subheader("📅 Agenda Kegiatan Kantor")
st.markdown("---")

# 4. FILTER PERIODE WAKTU (Baris Pertama)
st.write("📁 *Periode Waktu:*")
col_tgl1, col_tgl2, col_tgl3, _ = st.columns([1, 1, 1, 5])
with col_tgl1:
    btn_semua = st.button("Semua Waktu", use_container_width=True, type="primary")
with col_tgl2:
    btn_hariini = st.button("Hari Ini", use_container_width=True)
with col_tgl3:
    btn_bulanini = st.button("Bulan Ini", use_container_width=True)

# Logika Filter Waktu Berdasarkan Tombol Klik
today_date = datetime.now().date()
current_month = datetime.now().month
current_year = datetime.now().year

if "filter_waktu" not in st.session_state:
    st.session_state.filter_waktu = "semua"

if btn_semua: st.session_state.filter_waktu = "semua"
if btn_hariini: st.session_state.filter_waktu = "hari_ini"
if btn_bulanini: st.session_state.filter_waktu = "bulan_ini"

# Jalankan Filter Waktu ke Dataframe
if st.session_state.filter_waktu == "hari_ini":
    df_filtered = df[df["tanggal_clean"].dt.date == today_date]
    st.info("Menampilkan Agenda Hari Ini")
elif st.session_state.filter_waktu == "bulan_ini":
    df_filtered = df[(df["tanggal_clean"].dt.month == current_month) & (df["tanggal_clean"].dt.year == current_year)]
    st.info("Menampilkan Agenda Bulan Ini")
else:
    df_filtered = df.copy()

# 5. FILTER KATEGORI BIDANG (Baris Kedua)
st.write("🔍 *Filter Kategori Bidang:*")

# Ambil daftar bidang unik dari kolom 'penanggung jawab' atau 'bidang' (sesuaikan nama kolom di CSV Anda)
kolom_bidang = 'penanggung jawab' if 'penanggung jawab' in df.columns else ('bidang' if 'bidang' in df.columns else None)

if kolom_bidang:
    daftar_bidang = ["Semua"] + [b for b in df[kolom_bidang].unique() if b != "-"]
    pilihan_bidang = st.radio("", daftar_bidang, horizontal=True)
    
    if pilihan_bidang != "Semua":
        df_filtered = df_filtered[df_filtered[kolom_bidang] == pilihan_bidang]

st.markdown("---")

# Kamus Waktu Indonesia
hari_indo = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
bulan_indo = {1: "Mei", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}

# 6. PEMBUATAN TABEL TAMPILAN MODERN
if df_filtered.empty:
    st.info("Tidak ada agenda yang cocok dengan filter yang dipilih.")
else:
    # Siapkan data baris demi baris untuk dimasukkan ke tabel HTML
    html_rows = ""
    
    for idx, row in df_filtered.iterrows():
        tgl_clean = row['tanggal_clean']
        
        # Format Tanggal Indo
        if pd.isna(tgl_clean):
            tgl_display = row.get('tanggal', '-')
            status_html = '<div class="status-datang">Akan Datang</div>'
        else:
            agenda_date = tgl_clean.date()
            hari = hari_indo.get(tgl_clean.strftime('%A'), tgl_clean.strftime('%A'))
            bln = bulan_indo.get(tgl_clean.month, "")
            tgl_display = f"{hari}, {tgl_clean.day} {bln} {tgl_clean.year}"
            
            # Cek Status
            if agenda_date < today_date:
                status_html = '<div class="status-selesai">Selesai</div>'
            elif agenda_date == today_date:
                status_html = '<div class="status-hariini">Hari Ini</div>'
            else:
                status_html = '<div class="status-datang">Akan Datang</div>'
        
        # Ambil Data Teks
        jam = f"🕒 Jam {row.get('jam', '-')}" if row.get('jam', '-') != "-" else "-"
        kegiatan = row.get('kegiatan', '-')
        tempat = f"📍 {row.get('tempat', '-')}" if row.get('tempat', '-') != "-" else "-"
        pj = row.get(kolom_bidang, '-') if kolom_bidang else "-"
        
        # Gabungkan data ke struktur baris tabel HTML
        html_rows += f"""
        <tr>
            <td style="padding:15px; vertical-align:top; font-size:14px;"><b>{tgl_display}</b><br><small style="color:gray;">{jam}</small></td>
            <td style="padding:15px; vertical-align:top; font-size:14px;"><b>{kegiatan}</b><br><small style="color:gray;">{tempat}</small></td>
            <td style="padding:15px; vertical-align:top; font-size:14px; color:#495057;">{pj}</td>
            <td style="padding:15px; vertical-align:middle;">{status_html}</td>
        </tr>
        """

    # Cetak struktur utuh tabel ke halaman web
    tabel_lengkap = f"""
    <table style="width:100%; border-collapse: collapse; border: 1px solid #E0E0E0; background-color: white;">
        <thead>
            <tr style="border-bottom: 2px solid #E0E0E0; text-align: left;">
                <th style="padding:12px;">WAKTU & TANGGAL</th>
                <th style="padding:12px;">DETAIL KEGIATAN</th>
                <th style="padding:12px;">PENANGGUNG JAWAB</th>
                <th style="padding:12px; text-align:center; width:150px;">STATUS</th>
            </tr>
        </thead>
        <tbody>
            {html_rows}
        </tbody>
    </table>
    """
    st.markdown(tabel_lengkap, unsafe_html=True)
