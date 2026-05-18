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
    df.columns = df.columns.str.strip()  # Hapus spasi gaib pada nama kolom
    df["Tanggal_Clean"] = pd.to_datetime(df["Tanggal"], format="%d-%m-%Y", errors="coerce")
    df = df.sort_values(by=["Tanggal_Clean"])
else:
    st.error("File database CSV belum ditemukan di GitHub. Silakan upload file CSV agenda Anda terlebih dahulu.")
    st.stop()

# 3. Judul Aplikasi
st.title("📅 Agenda Kegiatan Kantor")
st.write(f"Waktu Sistem: {datetime.now().strftime('%d-%m-%Y | %H:%M')}")
st.markdown("---")

today = pd.Timestamp.today().normalize()

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
    hari = hari_indonesia[dt.strftime('%A')]
    tgl = dt.day
    bln = bulan_indonesia[dt.month]
    thn = dt.year
    return f"{hari}, {tgl} {bln} {thn}"

# 4. Membuat Menu Tab Navigasi
tab1, tab2, tab3 = st.tabs(["📌 Semua Agenda", "🚀 Akan Datang", "✅ Selesai"])

def tampilkan_agenda(dataframe):
    if dataframe.empty:
        st.info("Tidak ada agenda dalam kategori ini.")
        return
        
    for index, row in dataframe.iterrows():
        tgl_clean = row['Tanggal_Clean']
        tgl_display = format_tgl_indo(tgl_clean)
        jam_display = str(row.get('Jam', '-')) if pd.notna(row.get('Jam')) else '-'
        kegiatan = str(row.get('Kegiatan', 'Tanpa Nama Kegiatan'))
        tempat = str(row.get('Tempat', '-'))
        pakaian = str(row.get('Pakaian', '-'))
        keterangan = str(row.get('Keterangan', '-'))
        
        # Menentukan teks status secara manual dan aman
        if pd.isna(tgl_clean):
            status = "🔵 AGENDA"
        elif tgl_clean.normalize() < today:
            status = "🟢 SELESAI"
        elif tgl_clean.normalize() == today:
            status = "🟠 HARI INI"
        else:
            status = "🔵 AKAN DATANG"
            
        # Tampilan Kotak Informasi Bersih bawaan Streamlit
        with st.expander(f"{status} | {kegiatan}", expanded=True):
            st.write(f"📅 *Hari/Tanggal:* {tgl_display}")
            st.write(f"⏰ *Waktu/Jam:* {jam_display} WITA")
            st.write(f"📍 *Tempat:* {tempat}")
            st.write(f"👔 *Pakaian:* {pakaian}")
            if keterangan != "-":
                st.write(f"📝 *Keterangan:* {keterangan}")

with tab1:
    tampilkan_agenda(df)

with tab2:
    if not df.empty:
        df_mendatang = df[df["Tanggal_Clean"].normalize() >= today]
    else:
        df_mendatang = df
    tampilkan_agenda(df_mendatang)

with tab3:
    if not df.empty:
        df_selesai = df[df["Tanggal_Clean"].normalize() < today]
    else:
        df_selesai = df
    tampilkan_agenda(df_selesai)
