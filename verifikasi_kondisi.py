import os
import pandas as pd
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# --- KONFIGURASI ONLINE ANDA ---
EXCEL_FILE = "Book2.xlsx"  
# MASUKKAN ID FOLDER GOOGLE DRIVE ANDA DI BAWAH INI
GOOGLE_DRIVE_FOLDER_ID = "1HKy1AwGYwSluFOObLJCHwGmraD5kXzOl" 

PILIHAN_KONDISI = [
    "Jalan berlubang", "Jalan Lapen", "Jalan Rabat", "Jalan silikat", 
    "Jalan tanah", "Keausan permukaan", "Kerusakan tepi", "Normal", 
    "Paving block", "Retak buaya", "Retak memanjang"
]

st.set_page_config(layout="wide", page_title="Online Verifikasi Foto Survey Jalan")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    img { max-height: 85vh; object-fit: contain; }
    </style>
    """,
    unsafe_allow_html=True
)

# Fungsi mengambil URL gambar langsung dari Google Drive berdasarkan nama file
@st.cache_data(ttl=600)
def dapatkan_url_foto_drive(nama_file, folder_id):
    # Menggunakan API publik Google Drive untuk mencari file berdasarkan nama di dalam folder tertentu
    url_pencarian = f"https://googleapis.com'{nama_file}'+and+'{folder_id}'+in+parents&key=KUNCI_API_ANDA_JIKA_BUTUH"
    # Menggunakan trik export direct download web stream Google Drive standar
    # Untuk file publik, kita bisa memanggil langsung url proxy id jika nama file diubah menjadi ID file.
    # Trik termudah tanpa API Key untuk file massal adalah menaruh ID file di Excel, 
    # Namun jika berdasarkan teks nama, kita gunakan endpoint kompresi thumbnail resolusi tinggi:
    return f"https://google.com{nama_file}&sz=w1000"

# Load data Excel
if "df" not in st.session_state:
    if os.path.exists(EXCEL_FILE):
        df_awal = pd.read_excel(EXCEL_FILE, keep_default_na=False)
        if 'Kondisi' not in df_awal.columns:
            df_awal['Kondisi'] = ""
        st.session_state.df = df_awal
    else:
        st.error(f"File Excel '{EXCEL_FILE}' tidak ditemukan di server!")
        st.stop()

if "index" not in st.session_state:
    st.session_state.index = 0

df = st.session_state.df
total_data = len(df)
idx = st.session_state.index

# TATA LETAK PANEL
col_kiri, col_kanan = st.columns(2)

row = df.iloc[idx]
nama_file_dokumen = str(row['nama_file']).strip() if 'nama_file' in df.columns and pd.notna(row['nama_file']) else ""
nama_file_foto = str(row['Foto']).strip() if 'Foto' in df.columns and pd.notna(row['Foto']) else ""
if nama_file_dokumen in ["nan", "None"]: nama_file_dokumen = ""
if nama_file_foto in ["nan", "None"]: nama_file_foto = ""

nama_target_foto = nama_file_foto if nama_file_foto != "" else nama_file_dokumen
kondisi_saat_ini = str(row['Kondisi']).strip() if 'Kondisi' in df.columns and pd.notna(row['Kondisi']) else ""
if kondisi_saat_ini in ["nan", "None"]: kondisi_saat_ini = ""

# PANEL KIRI: GAMBAR ONLINE
with col_kiri:
    if nama_target_foto == "":
        st.warning("⚠️ Baris ini tidak memiliki nama file foto.")
    else:
        # Menampilkan gambar langsung via link Google Drive menggunakan HTML embedding proxy
        # Cara terbaik tanpa ribet token API untuk gambar publik di Drive:
        url_drive_langsung = f"https://open-drive.com{GOOGLE_DRIVE_FOLDER_ID}&file_name={nama_target_foto}"
        
        # Opsi alternatif menggunakan komponen gambar Streamlit
        st.image(f"https://google.com{GOOGLE_DRIVE_FOLDER_ID}", caption=nama_target_foto, use_column_width=True)
        st.info("Catatan: Untuk integrasi gambar online massal berkecepatan tinggi, disarankan menggunakan hosting cloud storage seperti Cloudinary/ImgBB atau memasukkan ID File Drive unik pada kolom Excel.")

# PANEL KANAN: KONTROL
with col_kanan:
    st.write(f"### Data Online {idx + 1} dari {total_data}")
    st.write("---")
    
    default_idx = PILIHAN_KONDISI.index(kondisi_saat_ini) if kondisi_saat_ini in PILIHAN_KONDISI else 0
    pilihan = st.selectbox("Klasifikasi Kondisi:", options=PILIHAN_KONDISI, index=default_idx, key=f"select_{idx}")
    
    if pilihan != kondisi_saat_ini:
        df.at[idx, 'Kondisi'] = pilihan
        df.to_excel(EXCEL_FILE, index=False)
        st.toast(f"Tersimpan di Server Cloud: {pilihan}", icon="✅")
    
    st.write("---")
    
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.button("◀ Previous", disabled=(idx == 0), use_container_width=True):
            st.session_state.index -= 1
            st.rerun()
    with nav_col2:
        if st.button("Next ▶", disabled=(idx == total_data - 1), use_container_width=True):
            st.session_state.index += 1
            st.rerun()
