"""Registry template surat yang dinamis (tanpa hardcode di app.py).

Semua jenis surat, file .docx-nya, dan awalan nomor suratnya disimpan di satu
file JSON (`templates.json`). Perangkat desa cukup menambah/menghapus template
lewat UI, kode program tidak perlu disentuh sama sekali.

Saat pertama kali dijalankan (templates.json belum ada), TEMPLATE BAWAAN yang
file .docx-nya sudah tersedia di folder templates/ otomatis didaftarkan lewat
fungsi seed_template_bawaan(), sehingga template lama tidak perlu di-upload ulang.

Struktur file `templates.json`:
{
  "templates": [
    {
      "id": "surat_pengantar",          # id unik & stabil (dipakai counter penomoran)
      "nama": "Surat Pengantar",         # nama yang tampil di dropdown
      "file": "surat_pengantar.docx",    # nama file di folder templates/
      "prefix": "440/"                   # awalan nomor surat khusus jenis ini
    },
    ...
  ]
}

File .docx fisiknya disimpan di folder `templates/`.
"""

import json
import os
import re
import unicodedata

from kunci_file import KunciFile

TEMPLATE_DIR = "templates"
REGISTRY_PATH = "templates.json"

# ------------------------------------------------------------------
# TEMPLATE BAWAAN
# Didaftarkan otomatis saat pertama kali aplikasi jalan (templates.json belum ada).
# Syaratnya: file .docx-nya memang sudah ada di folder templates/.
# Untuk mengubah awalan nomor bawaan, cukup ganti "prefix" di sini.
# ------------------------------------------------------------------
TEMPLATE_BAWAAN = [
    {"id": "surat_pengantar", "nama": "Surat Pengantar",
     "file": "surat_pengantar.docx", "prefix": "440/"},
    {"id": "surat_domisili", "nama": "Surat Keterangan Domisili",
     "file": "surat_domisili.docx", "prefix": "470/"},
    {"id": "surat_tidak_mampu", "nama": "Surat Keterangan Tidak Mampu",
     "file": "surat_tidak_mampu.docx", "prefix": "470/"},
]


# ------------------------------------------------------------------
# Util internal
# ------------------------------------------------------------------
def _registry_kosong():
    return {"templates": []}


def _load() -> dict:
    if not os.path.exists(REGISTRY_PATH):
        return _registry_kosong()
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _registry_kosong()
    if not isinstance(data, dict) or "templates" not in data:
        return _registry_kosong()
    return data


def _simpan(data: dict) -> None:
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def buat_id(nama: str) -> str:
    """Ubah nama surat jadi id yang aman untuk nama file/kunci (slug)."""
    teks = unicodedata.normalize("NFKD", nama).encode("ascii", "ignore").decode("ascii")
    teks = teks.lower().strip()
    teks = re.sub(r"[^a-z0-9]+", "_", teks)
    teks = teks.strip("_")
    return teks or "template"


def _id_unik(nama: str, data: dict) -> str:
    """Pastikan id tidak bentrok dengan template lain."""
    dasar = buat_id(nama)
    ada = {t["id"] for t in data["templates"]}
    if dasar not in ada:
        return dasar
    i = 2
    while f"{dasar}_{i}" in ada:
        i += 1
    return f"{dasar}_{i}"


def normalisasi_prefix(prefix: str) -> str:
    """Rapikan awalan nomor surat. Kosong dibolehkan (berarti tanpa awalan)."""
    return (prefix or "").strip()


# ------------------------------------------------------------------
# SEEDING TEMPLATE BAWAAN
# ------------------------------------------------------------------
def seed_template_bawaan() -> None:
    """Daftarkan template bawaan saat registry masih kosong / belum ada.

    Dipanggil sekali di awal aplikasi. Aman dipanggil berkali-kali: kalau
    templates.json sudah ada, fungsi ini tidak melakukan apa-apa (tidak menimpa
    perubahan yang sudah dibuat perangkat desa). Hanya mendaftarkan template
    bawaan yang file .docx-nya benar-benar ada di folder templates/.
    """
    if os.path.exists(REGISTRY_PATH):
        return  # registry sudah pernah dibuat; jangan ganggu isinya

    terdaftar = []
    for t in TEMPLATE_BAWAAN:
        if os.path.exists(os.path.join(TEMPLATE_DIR, t["file"])):
            terdaftar.append({
                "id": t["id"],
                "nama": t["nama"],
                "file": t["file"],
                "prefix": normalisasi_prefix(t["prefix"]),
            })

    # Tetap tulis file (walau kosong) supaya seeding tidak diulang tiap refresh.
    _simpan({"templates": terdaftar})


# ------------------------------------------------------------------
# API publik
# ------------------------------------------------------------------
def daftar_template() -> list:
    """Kembalikan list template (urut sesuai urutan penambahan)."""
    return _load()["templates"]


def peta_nama_ke_template() -> dict:
    """Dict {nama_surat: objek_template} untuk kebutuhan dropdown & lookup cepat."""
    return {t["nama"]: t for t in daftar_template()}


def cari_by_id(template_id: str):
    for t in daftar_template():
        if t["id"] == template_id:
            return t
    return None


def nama_sudah_ada(nama: str) -> bool:
    nama_bersih = (nama or "").strip().lower()
    return any(t["nama"].strip().lower() == nama_bersih for t in daftar_template())


def path_file(template: dict) -> str:
    return os.path.join(TEMPLATE_DIR, template["file"])


def tambah_template(nama: str, prefix: str, isi_docx: bytes) -> dict:
    """Tambah template baru: simpan file .docx + catat di registry.

    Mengembalikan objek template yang baru dibuat.
    Melempar ValueError kalau input tidak valid / nama duplikat.
    """
    nama = (nama or "").strip()
    if not nama:
        raise ValueError("Nama surat tidak boleh kosong.")
    if not isi_docx:
        raise ValueError("File template .docx belum diunggah.")
    if nama_sudah_ada(nama):
        raise ValueError(f"Sudah ada template dengan nama '{nama}'.")

    os.makedirs(TEMPLATE_DIR, exist_ok=True)

    with KunciFile(REGISTRY_PATH + ".lock"):
        data = _load()
        template_id = _id_unik(nama, data)
        nama_file = f"{template_id}.docx"

        with open(os.path.join(TEMPLATE_DIR, nama_file), "wb") as f:
            f.write(isi_docx)

        template = {
            "id": template_id,
            "nama": nama,
            "file": nama_file,
            "prefix": normalisasi_prefix(prefix),
        }
        data["templates"].append(template)
        _simpan(data)

    return template


def hapus_template(template_id: str) -> bool:
    """Hapus template dari registry + hapus file .docx-nya.

    Riwayat penomoran yang sudah terlanjur terbit TIDAK ikut dihapus di sini
    (biar jejak nomor lama tetap ada); pembersihan counter diserahkan ke modul
    penomoran bila diperlukan. Kembalikan True kalau ada yang terhapus.
    """
    with KunciFile(REGISTRY_PATH + ".lock"):
        data = _load()
        target = next((t for t in data["templates"] if t["id"] == template_id), None)
        if target is None:
            return False

        file_path = os.path.join(TEMPLATE_DIR, target["file"])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass  # file mungkin sedang dipakai; registry tetap dibersihkan

        data["templates"] = [t for t in data["templates"] if t["id"] != template_id]
        _simpan(data)

    return True