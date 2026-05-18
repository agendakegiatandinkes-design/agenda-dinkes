import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Pengaturan Halaman Utama (Wajib di bagian paling atas)
st.set_page_config(
    page_title="Agenda Dinas Kesehatan Kota Parepare",
    page_icon="🏢",
    layout="wide"
)

# 2. Gaya Tampilan Modern (Menggunakan st.html agar aman dari eror pustaka)
st.html("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 13px;
        text-align: center;
        min-width: 100px;
    }
    .selesai { background-color: #E8F5E9; color: #2E7D32; }
    .hari-ini { background-color: #FFF3E0; color: #E65100; }
    .akan-datang { background-color: #E3F2FD; color: #0D47A1; }
    
    .tabel-agenda {
        width: 100%; 
        border-collapse: collapse; 
        background-color: white;
        border-radius: 8px;
        overflow: hidden;
    }
    .tabel-agenda th { 
        background-color: #F8F9FA; 
        color: #4A5568; 
        font-weight: bold; 
        padding: 14px;
        border-bottom: 2px solid #EDF2F7;
        text-align: left;
        font-size: 13px;
        letter-spacing: 0.5px;
    }
    .tabel-agenda td { 
        padding: 16px 14px; 
        border-bottom: 1px solid #EDF2F7;
        vertical-align: top;
    }
    </style>
""")

# 3. Otomatis Memuat File Database CSV
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

if csv_files:
    df = pd.read_csv(csv_files[0])
    df.columns = df.columns.str.strip().str.lower()
    
    # Bersihkan data kosong
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace("nan", "-")
        
    df["tanggal_clean"] = pd.to_datetime(df["tanggal"], format="%d-%m-%Y", errors="coerce")
    df = df.sort_values(by=["tanggal_clean"])
else:
    st.error("Waduh! File database CSV belum ditemukan di folder GitHub Anda.")
    st.stop()

# 4. Filter Logika Waktu Sistem
today_date = datetime.now().date()
current_month = datetime.now().month
current_year = datetime.now().year

# Header Utama Aplikasi
st.subheader("🏢 Dinas Kesehatan Kota Parepare")
st.markdown("---")

# 5. FILTER PERIODE WAKTU
st.markdown("📅 *Periode Waktu:*")
col_t1, col_t2, col_t3, _ = st.columns([1, 1, 1, 5])
with col_t1: btn_semua = st.button("Semua", use_container_width=True)
with col_t2: btn_hariini = st.button("Hari Ini", use_container_width=True)
with col_t3: btn_bulanini = st.button("Bulan Ini", use_container_width=True)

if "f_waktu" not in st.session_state:
    st.session_state.f_waktu = "semua"

if btn_semua: st.session_state.f_waktu = "semua"
if btn_hariini: st.session_state.f_waktu = "hari_ini"
if btn_bulanini: st.session_state.f_waktu = "bulan_ini"

if st.session_state.f_waktu == "hari_ini":
    df_filtered = df[df["tanggal_clean"].dt.date == today_date]
elif st.session_state.f_waktu == "bulan_ini":
    df_filtered = df[(df["tanggal_clean"].dt.month == current_month) & (df["tanggal_clean"].dt.year == current_year)]
else:
    df_filtered = df.copy()

# 6. FILTER KATEGORI BIDANG
st.markdown("🔍 *Filter Kategori Bidang:*")
kolom_bidang = 'penanggung jawab' if 'penanggung jawab' in df.columns else ('bidang' if 'bidang' in df.columns else None)

if kolom_bidang:
    raw_bidang = [b for b in df[kolom_bidang].unique() if b != "-"]
    daftar_bidang = ["Semua"] + raw_bidang
    
    # Menggunakan komponen pill penanda agar gaya visual tombolnya estetik mendatar
    pilihan_bidang = st.pills("", daftar_bidang, selection_mode="single", default="Semua")
    
    if pilihan_bidang and pilihan_bidang != "Semua":
        df_filtered = df_filtered[df_filtered[kolom_bidang] == pilihan_bidang]

st.markdown("---")

# Terjemahan Format Waktu Lokal
hari_indo = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}
bulan_indo = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}

# 7. STRUKTUR GENERATOR TABEL HTML TAMPILAN BARU
if df_filtered.empty:
    st.info("Tidak ada agenda kegiatan yang cocok dengan filter penapisan saat ini.")
else:
    html_rows = ""
    for idx, row in df_filtered.iterrows():
        tgl_clean = row['tanggal_clean']
        
        if pd.isna(tgl_clean):
            tgl_display = row.get('tanggal', '-')
            status_html = '<span class="status-badge akan-datang">Akan Datang</span>'
        else:
            agenda_date = tgl_clean.date()
            hari = hari_indo.get(tgl_clean.strftime('%A'), tgl_clean.strftime('%A'))
            bln = bulan_indo.get(tgl_clean.month, "")
            tgl_display = f"{tgl_clean.day} {bln} {tgl_clean.year}"
            
            if agenda_date < today_date:
                status_html = '<span class="status-badge selesai">Selesai</span>'
            elif agenda_date == today_date:
                status_html = '<span class="status-badge hari-ini">Hari Ini</span>'
            else:
                status_html = '<span class="status-badge akan-datang">Akan Datang</span>'
        
        jam = f"🕒 Jam {row.get('jam', '-')}" if row.get('jam', '-') != "-" else "-"
        kegiatan = row.get('kegiatan', '-')
        tempat = f"📍 {row.get('tempat', '-')}" if row.get('tempat', '-') != "-" else "-"
        pj = row.get(kolom_bidang, '-') if kolom_bidang else "-"
        
        html_rows += f"""
        <tr>
            <td><b>{tgl_display}</b><br><small style="color:#718096;">{jam}</small></td>
            <td><span style="color:#2D3748; font-weight:600; font-size:15px;">{kegiatan}</span><br><small style="color:#A0AEC0;">{tempat}</small></td>
            <td><span style="background-color:#EDF2F7; padding:4px 10px; border-radius:6px; font-size:13px; color:#4A5568;">{pj}</span></td>
            <td style="text-align:center;">{status_html}</td>
        </tr>
        """

    tabel_final = f"""
    <table class="tabel-agenda">
        <thead>
            <tr>
                <th style="width:18%;">WAKTU & TANGGAL</th>
                <th style="width:45%;">DETAIL KEGIATAN</th>
                <th style="width:22%;">PENANGGUNG JAWAB</th>
                <th style="width:15%; text-align:center;">STATUS</th>
            </tr>
        </thead>
        <tbody>
            {html_rows}
        </tbody>
    </table>
    """
    st.html(tabel_final)
