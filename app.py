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
HISTORY_PATH = "riwayat_surat.csv"     # tempat nomor surat tersimpan otomatis

# Tambah/kurangi baris di bawah ini untuk menambah jenis surat baru.
# key   = nama yang muncul di dropdown
# value = nama file .docx di folder templates/
TEMPLATES = {
    "Surat Pengantar": "surat_pengantar.docx",
    "Surat Keterangan Domisili": "surat_domisili.docx",
    "Surat Keterangan Tidak Mampu": "surat_tidak_mampu.docx",
}

# Kode klasifikasi surat per jenis. Sesuaikan dengan pedoman tata naskah
# dinas desa Anda (biasanya sudah ditentukan Kecamatan/Kabupaten).
# Kalau belum tahu kodenya, boleh dikosongi/samakan dulu, tinggal edit di sini kapan saja.
KODE_SURAT = {
    "Surat Pengantar": "474",
    "Surat Keterangan Domisili": "470",
    "Surat Keterangan Tidak Mampu": "460",
}

KODE_DESA = "Ds"  # ganti dengan singkatan/kode resmi desa Anda, misal "05" atau "SMJ"

# Format nomor surat otomatis. Variabel yang tersedia untuk dipakai di sini:
#   {urut}          -> nomor urut berjalan, reset tiap tahun (001, 002, ...)
#   {kode}          -> diambil dari KODE_SURAT sesuai jenis surat
#   {desa}          -> diambil dari KODE_DESA di atas
#   {bulan_romawi}  -> bulan saat ini dalam angka romawi (I - XII)
#   {tahun}         -> tahun saat ini
# Contoh umum di desa: 470/003/Ds/VII/2026
NOMOR_SURAT_FORMAT = "{urut}/{kode}/{desa}/{bulan_romawi}/{tahun}"

BULAN_ID = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}

BULAN_ROMAWI = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
    7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII",
}

HISTORY_COLUMNS = ["urut", "nomor_surat", "jenis_surat", "nik", "nama", "tahun", "tanggal_dibuat"]


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


# ------------------------------------------------------------
# Nomor surat otomatis + riwayat
# ------------------------------------------------------------
def load_riwayat() -> pd.DataFrame:
    """Baca riwayat nomor surat yang pernah dibuat. Kalau belum ada file, mulai kosong."""
    if os.path.exists(HISTORY_PATH):
        return pd.read_csv(HISTORY_PATH, dtype={"nik": str})
    return pd.DataFrame(columns=HISTORY_COLUMNS)


def urut_berikutnya(riwayat: pd.DataFrame, tahun_ini: int) -> int:
    """Nomor urut berjalan; reset ke 1 tiap kali ganti tahun."""
    if riwayat.empty:
        return 1
    riwayat_tahun_ini = riwayat[riwayat["tahun"] == tahun_ini]
    if riwayat_tahun_ini.empty:
        return 1
    return int(riwayat_tahun_ini["urut"].max()) + 1


def buat_nomor_surat(jenis_surat: str, riwayat: pd.DataFrame):
    """Hitung nomor urut & nomor surat berikutnya (belum disimpan ke riwayat)."""
    sekarang = datetime.now()
    urut = urut_berikutnya(riwayat, sekarang.year)
    nomor = NOMOR_SURAT_FORMAT.format(
        urut=str(urut).zfill(3),
        kode=KODE_SURAT.get(jenis_surat, "000"),
        desa=KODE_DESA,
        bulan_romawi=BULAN_ROMAWI[sekarang.month],
        tahun=sekarang.year,
    )
    return urut, nomor


def simpan_riwayat(riwayat: pd.DataFrame, urut: int, nomor: str, jenis_surat: str, nik: str, nama: str) -> pd.DataFrame:
    """Catat nomor surat yang baru saja dipakai supaya nomor berikutnya lanjut otomatis."""
    baris_baru = pd.DataFrame([{
        "urut": urut,
        "nomor_surat": nomor,
        "jenis_surat": jenis_surat,
        "nik": nik,
        "nama": nama,
        "tahun": datetime.now().year,
        "tanggal_dibuat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    riwayat_baru = pd.concat([riwayat, baris_baru], ignore_index=True)
    riwayat_baru.to_csv(HISTORY_PATH, index=False)
    return riwayat_baru


# ============================================================
# UI
# ============================================================
st.set_page_config(page_title="Generator Surat Warga", page_icon="📄", layout="centered")
st.title("📄 Generator Surat Warga")
st.caption("Input NIK, pilih jenis surat, dokumen otomatis terisi dari data warga — nomor surat juga otomatis berurutan.")

if not os.path.exists(DATA_PATH):
    st.error(f"File data '{DATA_PATH}' tidak ditemukan. Letakkan di folder yang sama dengan app.py.")
    st.stop()

df = load_data()
riwayat = load_riwayat()

with st.expander("🔍 Lihat seluruh data warga"):
    st.dataframe(df, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    nik_input = st.text_input("Masukkan NIK", max_chars=16, placeholder="16 digit angka")
with col2:
    jenis_surat = st.selectbox("Pilih Jenis Surat", list(TEMPLATES.keys()))

# Preview nomor surat yang AKAN dipakai — belum tercatat di riwayat sampai
# tombol "Cari & Buat Surat" benar-benar ditekan.
urut_preview, nomor_preview = buat_nomor_surat(jenis_surat, riwayat)
st.info(f"Nomor surat yang akan digunakan: **{nomor_preview}**  \n"
        f"(otomatis, urutan ke-{urut_preview} tahun {datetime.now().year})")

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

    # Hitung ulang nomor surat tepat sebelum dipakai, supaya kalau ada surat lain
    # yang dibuat orang lain di antara preview & klik tombol ini, nomornya tetap benar.
    riwayat = load_riwayat()
    urut, nomor_surat = buat_nomor_surat(jenis_surat, riwayat)

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

    # Baru catat ke riwayat setelah dokumen berhasil dibuat, supaya nomor
    # berikutnya otomatis lanjut dari sini.
    riwayat = simpan_riwayat(riwayat, urut, nomor_surat, jenis_surat, data["NIK"], data["Nama"])

    nama_file = f"{jenis_surat.replace(' ', '_')}_{data['NIK']}.docx"
    st.download_button(
        label=f"⬇️ Download Surat (.docx) — Nomor {nomor_surat}",
        data=buffer,
        file_name=nama_file,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )

st.divider()

with st.expander("📜 Riwayat Nomor Surat yang Sudah Dibuat"):
    riwayat_terbaru = load_riwayat()
    if riwayat_terbaru.empty:
        st.caption("Belum ada surat yang dibuat.")
    else:
        st.dataframe(
            riwayat_terbaru.sort_values("urut", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            f"File riwayat tersimpan di `{HISTORY_PATH}` — jangan dihapus, karena dari situ "
            "aplikasi tahu nomor urut terakhir yang sudah dipakai."
        )

with st.expander("➕ Cara menambah jenis surat baru"):
    st.markdown(
        """
        1. Buat file `.docx` baru di folder `templates/`, isi dengan format surat yang diinginkan.
        2. Di dalam file itu, tulis placeholder `{{ nama }}`, `{{ nik }}`, `{{ alamat }}`, dst
           di posisi yang sesuai (lihat daftar variabel yang tersedia di README).
        3. Tambahkan satu baris baru di dictionary `TEMPLATES` pada awal file `app.py`, contoh:
           `"Surat Keterangan Usaha": "surat_keterangan_usaha.docx"`
        4. (Opsional) Tambahkan juga kode klasifikasinya di dictionary `KODE_SURAT` supaya
           nomor suratnya punya kode yang sesuai.
        5. Simpan, lalu jalankan ulang aplikasinya.
        """
    )
