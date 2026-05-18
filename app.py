import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Pengaturan Halaman Utama
st.set_page_config(
    page_title="Agenda Kegiatan Kantor",
    page_icon="📅",
    layout="wide"
)

# 2. Memuat File Database CSV Otomatis
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

if csv_files:
    df = pd.read_csv(csv_files[0])
    # Mengubah semua nama kolom menjadi huruf kecil & hapus spasi gaib
    df.columns = df.columns.str.strip().str.lower()
    
    # Memastikan semua data dibaca sebagai string/teks terlebih dahulu agar aman dari tipe data kosong
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        
    # Mengonversi kolom tanggal ke format datetime secara aman
    df["tanggal_clean"] = pd.to_datetime(df["tanggal"], format="%d-%m-%Y", errors="coerce")
    # Urutkan berdasarkan tanggal terlama ke terbaru
    df = df.sort_values(by=["tanggal_clean"])
else:
    st.error("File database CSV belum ditemukan di GitHub. Silakan upload file CSV agenda Anda terlebih dahulu.")
    st.stop()

# 3. Judul Aplikasi
st.title("📅 Agenda Kegiatan Kantor")
st.write(f"Waktu Sistem: {datetime.now().strftime('%d-%m-%Y | %H:%M')}")
st.markdown("---")

# Mengambil tanggal hari ini tanpa jam
today_date = datetime.now().date()

# Kamus Bahasa Indonesia untuk Waktu
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
    try:
        hari = hari_indonesia[dt.strftime('%A')]
        tgl = dt.day
        bln = bulan_indonesia[dt.month]
        thn = dt.year
        return f"{hari}, {tgl} {bln} {thn}"
    except:
        return "-"

# 4. Menu Tab Navigasi
tab1, tab2, tab3 = st.tabs(["📌 Semua Agenda", "🚀 Akan Datang", "✅ Selesai"])

def tampilkan_agenda(dataframe, filter_kategori="semua"):
    ada_data = False
    
    for index, row in dataframe.iterrows():
        tgl_clean = row['tanggal_clean']
        
        # Penentuan Status Berdasarkan Tanggal secara Manual (Sangat Aman)
        if pd.isna(tgl_clean):
            status = "🔵 AGENDA"
            kategori_waktu = "mendatang"
        else:
            agenda_date = tgl_clean.date()
            if agenda_date < today_date:
                status = "🟢 SELESAI"
                kategori_waktu = "selesai"
            elif agenda_date == today_date:
                status = "🟠 HARI INI"
                kategori_waktu = "mendatang"
            else:
                status = "🔵 AKAN DATANG"
                kategori_waktu = "mendatang"
        
        # Filter tampilan berdasarkan tab yang dipilih user
        if filter_kategori != "semua" and filter_kategori != kategori_waktu:
            continue
            
        ada_data = True
        tgl_display = format_tgl_indo(tgl_clean) if not pd.isna(tgl_clean) else row.get('tanggal', '-')
        
        # Mengambil data teks, ganti "nan" bawaan pandas menjadi "-"
        def bersihkan_teks(val):
            text = str(val)
            return "-" if text == "nan" or text == "" else text

        jam_display = bersihkan_teks(row.get('jam'))
        kegiatan = str(row.get('kegiatan'))
        if kegiatan == "nan" or kegiatan == "": 
            kegiatan = "Tanpa Nama Kegiatan"
            
        tempat = bersihkan_teks(row.get('tempat'))
        pakaian = bersihkan_teks(row.get('pakaian'))
        keterangan = bersihkan_teks(row.get('keterangan'))
        
        # Tampilan Kotak Informasi bawaan Streamlit (100% Kebal Error)
        with st.expander(f"{status} | {kegiatan}", expanded=True):
            st.write(f"📅 *Hari/Tanggal:* {tgl_display}")
            st.write(f"⏰ *Waktu/Jam:* {jam_display} WITA")
            st.write(f"📍 *Tempat:* {tempat}")
            st.write(f"👔 *Pakaian:* {pakaian}")
            if keterangan != "-":
                st.write(f"📝 *Keterangan:* {keterangan}")
                
    if not ada_data:
        st.info("Tidak ada agenda dalam kategori ini.")

with tab1:
    tampilkan_agenda(df, "semua")

with tab2:
    tampilkan_agenda(df, "mendatang")

with tab3:
    tampilkan_agenda(df, "selesai")
