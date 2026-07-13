"""Penomoran surat otomatis + riwayat, per-template dan aman multi-proses.

Setiap template punya awalan (prefix) sendiri, contoh "470/", "471/". Nomor urut
berjalan sendiri-sendiri per template dan RESET ke 1 tiap tahun baru.

Format nomor surat: {prefix}{urut}/{kode_unit_kerja}/{tahun}
  contoh prefix "470/" -> "470/12/409.40.10/2026"

Riwayat & counter disimpan di `riwayat_surat.json`:
{
  "counters": { "<template_id>-<tahun>": <urut_terakhir> },
  "riwayat": [ {record}, ... ]
}

Setiap record riwayat menyimpan `urut` dan `tahun` sehingga saat dihapus kita
bisa menentukan apakah dia nomor terakhir pada serinya (untuk roll-back).
"""

import json
import os
from datetime import datetime

from kunci_file import KunciFile

RIWAYAT_PATH = "riwayat_surat.json"


# ------------------------------------------------------------------
# Util internal
# ------------------------------------------------------------------
def _riwayat_kosong():
    return {"counters": {}, "riwayat": []}


def _load() -> dict:
    if not os.path.exists(RIWAYAT_PATH):
        return _riwayat_kosong()
    try:
        with open(RIWAYAT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _riwayat_kosong()
    data.setdefault("counters", {})
    data.setdefault("riwayat", [])
    return data


def _simpan(data: dict) -> None:
    with open(RIWAYAT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _key(template_id: str, tahun: int) -> str:
    return f"{template_id}-{tahun}"


def _rakit_nomor(prefix: str, urut: int, kode_unit_kerja: str, tahun: int) -> str:
    return f"{prefix}{urut}/{kode_unit_kerja}/{tahun}"


# ------------------------------------------------------------------
# API publik
# ------------------------------------------------------------------
def lihat_nomor_berikutnya(template: dict, kode_unit_kerja: str) -> str:
    """Preview nomor berikutnya TANPA menaikkan counter."""
    tahun = datetime.now().year
    data = _load()
    urut = data["counters"].get(_key(template["id"], tahun), 0) + 1
    return _rakit_nomor(template["prefix"], urut, kode_unit_kerja, tahun)


def terbitkan_nomor(template: dict, kode_unit_kerja: str, nik: str, nama: str,
                    keperluan: str = "", nama_file: str = "") -> dict:
    """Ambil nomor berikutnya, naikkan counter, dan catat ke riwayat (permanen).

    Dikunci file supaya aman kalau beberapa proses menerbitkan bersamaan.
    Mengembalikan record riwayat yang baru dibuat (termasuk `nomor_surat`).
    """
    tahun = datetime.now().year
    key = _key(template["id"], tahun)

    with KunciFile(RIWAYAT_PATH + ".lock"):
        data = _load()
        urut = data["counters"].get(key, 0) + 1
        data["counters"][key] = urut
        nomor_surat = _rakit_nomor(template["prefix"], urut, kode_unit_kerja, tahun)

        record = {
            "nomor_surat": nomor_surat,
            "template_id": template["id"],
            "jenis_surat": template["nama"],
            "urut": urut,
            "tahun": tahun,
            "nik": nik,
            "nama": nama,
            "keperluan": keperluan,
            "nama_file": nama_file,
            "dibuat_pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        data["riwayat"].append(record)
        _simpan(data)

    return record


def daftar_riwayat() -> list:
    """Riwayat terurut dari yang terbaru."""
    riwayat = _load()["riwayat"]
    return sorted(riwayat, key=lambda r: r.get("dibuat_pada", ""), reverse=True)


def _is_nomor_terakhir(data: dict, record: dict) -> bool:
    """True kalau `urut` pada record adalah nomor tertinggi untuk (template, tahun)
    di antara SEMUA riwayat yang masih tersisa (belum termasuk penghapusan record ini)."""
    template_id = record.get("template_id")
    tahun = record.get("tahun")
    urut = record.get("urut")
    if template_id is None or tahun is None or urut is None:
        return False

    tertinggi = max(
        (r["urut"] for r in data["riwayat"]
         if r.get("template_id") == template_id and r.get("tahun") == tahun
         and isinstance(r.get("urut"), int)),
        default=0,
    )
    return urut == tertinggi


def hapus_riwayat(record_id: str, folder_output: str = "") -> dict:
    """Hapus satu record riwayat berdasarkan nomor_surat + waktu dibuat.

    Aturan roll-back:
    - Kalau record yang dihapus adalah nomor TERAKHIR pada serinya (template+tahun),
      counter diturunkan 1 supaya nomor itu bisa dipakai ulang.
    - Kalau BUKAN yang terakhir, counter dibiarkan agar tidak terjadi duplikasi.

    Juga menghapus file surat hasil generate bila `folder_output` diberikan dan
    `nama_file`-nya tercatat.

    `record_id` = f"{nomor_surat}||{dibuat_pada}" (dipakai UI sebagai identitas baris).
    Mengembalikan dict ringkasan: {"terhapus", "rollback", "file_terhapus"}.
    """
    hasil = {"terhapus": False, "rollback": False, "file_terhapus": False}

    with KunciFile(RIWAYAT_PATH + ".lock"):
        data = _load()

        target = None
        for r in data["riwayat"]:
            if f"{r.get('nomor_surat')}||{r.get('dibuat_pada')}" == record_id:
                target = r
                break
        if target is None:
            return hasil

        rollback = _is_nomor_terakhir(data, target)

        # Hapus file surat hasil generate (kalau ada)
        nama_file = target.get("nama_file")
        if folder_output and nama_file:
            file_path = os.path.join(folder_output, nama_file)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    hasil["file_terhapus"] = True
                except OSError:
                    pass

        # Buang record dari riwayat
        data["riwayat"] = [
            r for r in data["riwayat"]
            if f"{r.get('nomor_surat')}||{r.get('dibuat_pada')}" != record_id
        ]

        # Roll-back counter hanya kalau dia nomor terakhir pada serinya
        if rollback:
            key = _key(target["template_id"], target["tahun"])
            if data["counters"].get(key, 0) == target["urut"]:
                data["counters"][key] = target["urut"] - 1
                hasil["rollback"] = True

        _simpan(data)
        hasil["terhapus"] = True

    return hasil
