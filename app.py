import io
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from docxtpl import DocxTemplate

# ============================================================
# KONFIGURASI — sesuaikan dengan kondisi kantor desa Anda
# ============================================================
DATA_PATH = "data_warga_contoh.xlsx"   # ganti dengan file data warga asli
TEMPLATE_DIR = "templates"

# Tambah/kurangi baris di bawah ini untuk menambah jenis surat baru.
# key   = nama yang muncul di dropdown
# value = nama file .docx di folder templates/
TEMPLATES = {
    "Surat Pengantar": "surat_pengantar.docx",
    "Surat Keterangan Domisili": "surat_domisili.docx",
    "Surat Keterangan Tidak Mampu": "surat_tidak_mampu.docx",
}

BULAN_ID = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}


def format_tanggal_indo(nilai) -> str:
    """Ubah tanggal (datetime/Timestamp/string) jadi format 'DD Bulan YYYY'."""
    if pd.isna(nilai):
        return ""
    if isinstance(nilai, str):
        try:
            nilai = pd.to_datetime(nilai)
        except (ValueError, TypeError):
            return nilai
    return f"{nilai.day} {BULAN_ID[nilai.month]} {nilai.year}"


@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH, dtype={"NIK": str})
    df["NIK"] = df["NIK"].str.strip()
    return df


st.set_page_config(page_title="Generator Surat Warga", page_icon="📄", layout="centered")
st.title("📄 Generator Surat Warga")
st.caption("Input NIK, pilih jenis surat, dokumen otomatis terisi dari data warga.")

if not os.path.exists(DATA_PATH):
    st.error(f"File data '{DATA_PATH}' tidak ditemukan. Letakkan di folder yang sama dengan app.py.")
    st.stop()

df = load_data()

with st.expander("🔍 Lihat seluruh data warga"):
    st.dataframe(df, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    nik_input = st.text_input("Masukkan NIK", max_chars=16, placeholder="16 digit angka")
with col2:
    jenis_surat = st.selectbox("Pilih Jenis Surat", list(TEMPLATES.keys()))

nomor_surat = st.text_input("Nomor Surat", value="470/___/2026")
keperluan = st.text_input("Keperluan", placeholder="contoh: persyaratan melamar kerja")

if st.button("🔎 Cari & Buat Surat", type="primary", use_container_width=True):
    nik = nik_input.strip()

    if not nik:
        st.warning("NIK belum diisi.")
        st.stop()

    hasil = df[df["NIK"] == nik]

    if hasil.empty:
        st.error(f"NIK **{nik}** tidak ditemukan di database. Periksa kembali angkanya.")
        st.stop()

    data = hasil.iloc[0].to_dict()
    st.success(f"Data ditemukan: **{data['Nama']}**")

    context = {
        "nik": data.get("NIK", ""),
        "nama": data.get("Nama", ""),
        "tempat_lahir": data.get("Tempat Lahir", ""),
        "tanggal_lahir": format_tanggal_indo(data.get("Tanggal Lahir", "")),
        "jenis_kelamin": data.get("Jenis Kelamin", ""),
        "alamat": data.get("Alamat", ""),
        "agama": data.get("Agama", ""),
        "status_perkawinan": data.get("Status Perkawinan", ""),
        "pekerjaan": data.get("Pekerjaan", ""),
        "kewarganegaraan": data.get("Kewarganegaraan", "WNI"),
        "nomor_surat": nomor_surat,
        "keperluan": keperluan if keperluan else "-",
        "tanggal_surat": format_tanggal_indo(datetime.now()),
    }

    template_path = os.path.join(TEMPLATE_DIR, TEMPLATES[jenis_surat])
    doc = DocxTemplate(template_path)
    doc.render(context)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    nama_file = f"{jenis_surat.replace(' ', '_')}_{data['NIK']}.docx"
    st.download_button(
        label="⬇️ Download Surat (.docx)",
        data=buffer,
        file_name=nama_file,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )

st.divider()
with st.expander("➕ Cara menambah jenis surat baru"):
    st.markdown(
        """
        1. Buat file `.docx` baru di folder `templates/`, isi dengan format surat yang diinginkan.
        2. Di dalam file itu, tulis placeholder `{{ nama }}`, `{{ nik }}`, `{{ alamat }}`, dst
           di posisi yang sesuai (lihat daftar variabel yang tersedia di README).
        3. Tambahkan satu baris baru di dictionary `TEMPLATES` pada awal file `app.py`, contoh:
           `"Surat Keterangan Usaha": "surat_keterangan_usaha.docx"`
        4. Simpan, lalu jalankan ulang aplikasinya.
        """
    )
