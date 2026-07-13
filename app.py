import io
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from docxtpl import DocxTemplate

import penomoran
import template_store

# ============================================================
# KONFIGURASI — sesuaikan dengan kondisi kantor desa Anda
# ============================================================
DATA_PATH = "data_warga_contoh.xlsx"   # ganti dengan file data warga asli
KODE_UNIT_KERJA = "409.40.10"          # kode unit kerja/instansi, tampil di setiap nomor surat
OUTPUT_DIR = "surat_terbit"            # tempat menyimpan salinan .docx yang diterbitkan

# CATATAN: daftar jenis surat TIDAK lagi ditulis di sini. Semuanya dibaca dinamis
# dari template_store (registry templates.json). Tambah/hapus template dilakukan
# lewat menu "Kelola Template Surat" di aplikasi — kode ini tidak perlu disentuh.


# ============================================================
# UTIL TANGGAL & DATA WARGA
# ============================================================
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


def bangun_context(data: dict, nomor_surat: str, keperluan: str) -> dict:
    """Susun variabel yang bisa dipakai di dalam template .docx."""
    return {
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


def render_surat(template: dict, context: dict) -> bytes:
    """Render template .docx dengan context, kembalikan bytes hasilnya."""
    doc = DocxTemplate(template_store.path_file(template))
    doc.render(context)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# GERBANG KATA SANDI
# ============================================================
def cek_kata_sandi() -> bool:
    """Gerbang kata sandi sederhana sebelum data warga bisa diakses.

    Kata sandi TIDAK ditulis di file ini. Diatur lewat .streamlit/secrets.toml
    (lihat .streamlit/secrets.toml.example), supaya tidak ikut ter-share kalau
    folder ini disalin/dikirim ke orang lain.
    """
    if st.session_state.get("terautentikasi"):
        return True

    try:
        sandi_benar = st.secrets.get("app_password")
    except Exception:
        sandi_benar = None

    st.title("🔒 Generator Surat Warga")

    if not sandi_benar:
        st.warning(
            "Kata sandi akses belum diatur. Salin `.streamlit/secrets.toml.example` "
            "menjadi `.streamlit/secrets.toml`, isi `app_password` dengan kata sandi "
            "Anda sendiri, lalu jalankan ulang aplikasinya."
        )
        return False

    def sandi_dimasukkan():
        if st.session_state.get("sandi_input") == sandi_benar:
            st.session_state["terautentikasi"] = True
        else:
            st.session_state["sandi_salah"] = True

    st.text_input(
        "Masukkan kata sandi akses", type="password",
        key="sandi_input", on_change=sandi_dimasukkan,
    )
    if st.session_state.get("sandi_salah"):
        st.error("Kata sandi salah.")
    return False


# ============================================================
# HALAMAN: GENERATE SURAT
# ============================================================
def halaman_generate():
    st.title("📄 Generator Surat Warga")
    st.caption("Input NIK, pilih jenis surat, dokumen otomatis terisi dari data warga.")

    if not os.path.exists(DATA_PATH):
        st.error(f"File data '{DATA_PATH}' tidak ditemukan. Letakkan di folder yang sama dengan app.py.")
        return

    templates = template_store.daftar_template()
    if not templates:
        st.info(
            "Belum ada template surat. Buka menu **🗂️ Kelola Template Surat** "
            "di sidebar untuk menambahkan template pertama Anda."
        )
        return

    df = load_data()
    st.caption(
        f"📇 {len(df)} data warga termuat. Cari satu per satu lewat NIK di bawah — "
        "bukan lewat tabel, demi keamanan data."
    )

    peta = {t["nama"]: t for t in templates}

    col1, col2 = st.columns(2)
    with col1:
        nik_input = st.text_input("Masukkan NIK", max_chars=16, placeholder="16 digit angka")
    with col2:
        nama_jenis = st.selectbox("Pilih Jenis Surat", list(peta.keys()))

    template_terpilih = peta[nama_jenis]

    st.text_input(
        "Nomor Surat (otomatis)",
        value=penomoran.lihat_nomor_berikutnya(template_terpilih, KODE_UNIT_KERJA),
        disabled=True,
        help="Nomor ini didapat otomatis dari histori penomoran & baru resmi tersimpan "
             "setelah tombol 'Cari & Buat Surat' di bawah diklik.",
    )
    keperluan = st.text_input("Keperluan", placeholder="contoh: persyaratan melamar kerja")

    if st.button("🔎 Cari & Buat Surat", type="primary", use_container_width=True):
        nik = nik_input.strip()
        if not nik:
            st.warning("NIK belum diisi.")
            return

        hasil = df[df["NIK"] == nik]
        if hasil.empty:
            st.error(f"NIK **{nik}** tidak ditemukan di database. Periksa kembali angkanya.")
            return

        data = hasil.iloc[0].to_dict()
        st.success(f"Data ditemukan: **{data['Nama']}**")

        # Nama file salinan yang akan disimpan permanen
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        nama_file = f"{template_terpilih['id']}_{data['NIK']}_{stamp}.docx"

        # Terbitkan nomor resmi (counter naik + tercatat di riwayat)
        record = penomoran.terbitkan_nomor(
            template_terpilih, KODE_UNIT_KERJA,
            nik=data.get("NIK", ""), nama=data.get("Nama", ""),
            keperluan=keperluan, nama_file=nama_file,
        )
        nomor_surat = record["nomor_surat"]
        st.info(f"Nomor surat yang diterbitkan: **{nomor_surat}**")

        context = bangun_context(data, nomor_surat, keperluan)
        isi_docx = render_surat(template_terpilih, context)

        # Simpan salinan permanen supaya bisa ikut terhapus saat riwayat dihapus
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, nama_file), "wb") as f:
            f.write(isi_docx)

        st.download_button(
            label="⬇️ Download Surat (.docx)",
            data=isi_docx,
            file_name=nama_file,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )


# ============================================================
# HALAMAN: KELOLA TEMPLATE SURAT
# ============================================================
def halaman_kelola_template():
    st.title("🗂️ Kelola Template Surat")
    st.caption(
        "Tambah atau hapus jenis surat tanpa mengubah kode program. Perubahan "
        "langsung tampil di dropdown pada halaman Generate Surat."
    )

    # ---- Daftar template yang sudah ada ----
    st.subheader("Daftar Template")
    templates = template_store.daftar_template()
    if not templates:
        st.info("Belum ada template. Tambahkan lewat form di bawah.")
    else:
        for t in templates:
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.markdown(f"**{t['nama']}**  \n`{t['file']}`")
            c2.markdown(f"Awalan nomor:  \n**{t['prefix'] or '(tanpa awalan)'}**")

            konfirmasi_key = f"konfirmasi_hapus_{t['id']}"
            if c3.button("🗑️ Hapus", key=f"hapus_{t['id']}", use_container_width=True):
                st.session_state[konfirmasi_key] = True

            if st.session_state.get(konfirmasi_key):
                st.warning(f"Yakin hapus template **{t['nama']}**? File .docx-nya ikut terhapus.")
                k1, k2 = st.columns(2)
                if k1.button("Ya, hapus", key=f"ya_{t['id']}", type="primary", use_container_width=True):
                    template_store.hapus_template(t["id"])
                    st.session_state.pop(konfirmasi_key, None)
                    st.success(f"Template '{t['nama']}' dihapus.")
                    st.rerun()
                if k2.button("Batal", key=f"batal_{t['id']}", use_container_width=True):
                    st.session_state.pop(konfirmasi_key, None)
                    st.rerun()
            st.divider()

    # ---- Form tambah template ----
    st.subheader("➕ Tambah Template Baru")
    with st.form("form_tambah_template", clear_on_submit=True):
        nama_baru = st.text_input(
            "Nama surat",
            placeholder="contoh: Surat Keterangan Usaha",
        )
        prefix_baru = st.text_input(
            "Awalan nomor surat",
            placeholder="contoh: 470/",
            help="Awalan khusus jenis surat ini. Nomor urut & tahun ditambahkan "
                 "otomatis di belakangnya, mis. '470/12/409.40.10/2026'.",
        )
        file_baru = st.file_uploader("File template (.docx)", type=["docx"])
        submit = st.form_submit_button("Simpan Template", type="primary", use_container_width=True)

        if submit:
            try:
                isi = file_baru.read() if file_baru is not None else None
                template = template_store.tambah_template(nama_baru, prefix_baru, isi)
                st.success(
                    f"Template **{template['nama']}** ditambahkan dan langsung tersedia "
                    "di halaman Generate Surat."
                )
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    with st.expander("ℹ️ Variabel yang bisa dipakai di dalam file .docx"):
        st.markdown(
            """
            Tulis placeholder ini persis (dengan kurung kurawal ganda) di dalam file Word,
            aplikasi akan mengisinya otomatis:

            `{{ nik }}` `{{ nama }}` `{{ tempat_lahir }}` `{{ tanggal_lahir }}`
            `{{ jenis_kelamin }}` `{{ alamat }}` `{{ agama }}` `{{ status_perkawinan }}`
            `{{ pekerjaan }}` `{{ kewarganegaraan }}` `{{ nomor_surat }}` `{{ keperluan }}`
            `{{ tanggal_surat }}`
            """
        )


# ============================================================
# HALAMAN: RIWAYAT SURAT
# ============================================================
def halaman_riwayat():
    st.title("📜 Riwayat Surat")
    st.caption(
        "Daftar nomor surat yang sudah diterbitkan. Menghapus riwayat juga menghapus "
        "file surat hasil generate, dan me-roll-back nomor bila itu nomor terakhir."
    )

    riwayat = penomoran.daftar_riwayat()
    if not riwayat:
        st.info("Belum ada surat yang diterbitkan.")
        return

    for r in riwayat:
        record_id = f"{r.get('nomor_surat')}||{r.get('dibuat_pada')}"
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(
                f"**{r['nomor_surat']}** — {r.get('jenis_surat', '')}  \n"
                f"{r.get('nama', '')} · NIK {r.get('nik', '')}  \n"
                f"🕒 {r.get('dibuat_pada', '')}"
            )
        konfirmasi_key = f"konfirmasi_hapus_riwayat_{record_id}"
        if c2.button("🗑️ Hapus", key=f"hapus_r_{record_id}", use_container_width=True):
            st.session_state[konfirmasi_key] = True

        if st.session_state.get(konfirmasi_key):
            st.warning(
                f"Hapus riwayat **{r['nomor_surat']}**? File suratnya ikut terhapus. "
                "Kalau ini nomor terakhir pada jenis surat & tahun tsb, nomornya bisa dipakai lagi."
            )
            k1, k2 = st.columns(2)
            if k1.button("Ya, hapus", key=f"ya_r_{record_id}", type="primary", use_container_width=True):
                hasil = penomoran.hapus_riwayat(record_id, folder_output=OUTPUT_DIR)
                st.session_state.pop(konfirmasi_key, None)
                if hasil["terhapus"]:
                    pesan = "Riwayat dihapus."
                    if hasil["rollback"]:
                        pesan += " Nomor terakhir di-roll-back dan bisa dipakai ulang."
                    if hasil["file_terhapus"]:
                        pesan += " File surat ikut terhapus."
                    st.success(pesan)
                else:
                    st.error("Riwayat tidak ditemukan (mungkin sudah terhapus).")
                st.rerun()
            if k2.button("Batal", key=f"batal_r_{record_id}", use_container_width=True):
                st.session_state.pop(konfirmasi_key, None)
                st.rerun()
        st.divider()


# ============================================================
# ENTRY POINT
# ============================================================
def main():
    st.set_page_config(page_title="Generator Surat Warga", page_icon="📄", layout="centered")

    if not cek_kata_sandi():
        st.stop()

    halaman = st.sidebar.radio(
        "Menu",
        ["📄 Generate Surat", "🗂️ Kelola Template Surat", "📜 Riwayat Surat"],
    )

    if halaman == "📄 Generate Surat":
        halaman_generate()
    elif halaman == "🗂️ Kelola Template Surat":
        halaman_kelola_template()
    else:
        halaman_riwayat()


if __name__ == "__main__":
    main()
