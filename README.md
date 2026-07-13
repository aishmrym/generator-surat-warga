# Generator Surat Warga (Otomatis via NIK)

Aplikasi lokal sederhana untuk perangkat desa: ketik NIK, pilih jenis surat, klik
satu tombol, surat langsung terisi otomatis dari data warga, nomor surat otomatis
& berurutan, lalu siap diunduh sebagai file Word.

**Yang baru di versi ini:**
- **Kelola Template Surat lewat aplikasi** (tanpa menyentuh kode). Tambah/hapus
  jenis surat cukup lewat menu, template langsung muncul/hilang di dropdown.
- **Penomoran per jenis surat.** Tiap template punya awalan nomornya sendiri
  (mis. `470/`, `471/`), nomor urut berjalan terpisah per jenis dan reset tiap tahun.
- **Riwayat bisa dihapus** dengan roll-back nomor yang cerdas (lihat bagian 6).

## Isi folder

```
surat-generator/
├── app.py                    ← aplikasi utama (Streamlit), UI 3 menu
├── template_store.py         ← registry template dinamis (baca/tulis templates.json)
├── penomoran.py              ← penomoran per-template + riwayat + roll-back
├── kunci_file.py             ← kunci antar-proses (tanpa dependency pihak ketiga)
├── jalankan_aplikasi.bat     ← double-click untuk menjalankan (Windows)
├── requirements.txt          ← daftar library yang dibutuhkan
├── data_warga_contoh.xlsx    ← CONTOH data warga (ganti dengan data asli)
├── templates.json            ← *dibuat otomatis* — daftar template & awalan nomornya
├── riwayat_surat.json        ← *dibuat otomatis* — histori & counter nomor surat
├── surat_terbit/             ← *dibuat otomatis* — salinan .docx tiap surat terbit
├── .streamlit/
│   ├── config.toml           ← kunci ke localhost + matikan telemetry (jangan dihapus)
│   └── secrets.toml.example  ← salin jadi secrets.toml, isi kata sandi Anda
└── templates/                ← file .docx template disimpan di sini (dikelola aplikasi)
```

## 1. Instalasi (sekali saja)

Perlu Python 3.9+ ([python.org](https://python.org)).

**Windows (pakai `jalankan_aplikasi.bat`):** lewati langkah ini, `.bat` akan
mengecek Python & menginstall library otomatis saat pertama dijalankan.

**Command line / Mac / Linux:**
```bash
pip install -r requirements.txt
```

## 2. Atur kata sandi (sekali saja)

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Buka `.streamlit/secrets.toml`, ganti isinya dengan kata sandi pilihan Anda.
**Jangan** kirim/upload file `secrets.toml` (tanpa `.example`) ke mana pun.

## 3. Menjalankan aplikasi

Double-click `jalankan_aplikasi.bat` (Windows), atau:
```bash
streamlit run app.py
```
Browser terbuka di `http://localhost:8501`, lalu diminta kata sandi. Aplikasi
berjalan lokal & terkunci ke `127.0.0.1` — data warga tidak terkirim ke internet.

Ada tiga menu di sidebar: **Generate Surat**, **Kelola Template Surat**, dan
**Riwayat Surat**.

## 4. Kelola Template Surat (menu baru)

Semua jenis surat kini dibaca dinamis dari `templates.json`. Tidak ada lagi daftar
template yang ditulis di dalam kode.

**Menambah template:**
1. Buka menu **🗂️ Kelola Template Surat**.
2. Pada bagian **Tambah Template Baru**, isi:
   - **Nama surat** (mis. `Surat Keterangan Usaha`) — ini yang muncul di dropdown.
   - **Awalan nomor surat** (mis. `470/`) — awalan khusus jenis surat itu.
   - **File template `.docx`** — unggah file Word berisi placeholder (lihat bawah).
3. Klik **Simpan Template**. Template langsung tersedia di halaman Generate Surat.

**Menghapus template:** klik **🗑️ Hapus** di sebelah nama template, lalu konfirmasi.
File `.docx`-nya ikut terhapus dan template hilang dari dropdown. (Riwayat nomor
yang sudah terlanjur terbit tetap tersimpan sebagai jejak.)

**Placeholder yang tersedia** (tulis persis di dalam file Word, dengan kurung
kurawal ganda):

`{{ nik }}` `{{ nama }}` `{{ tempat_lahir }}` `{{ tanggal_lahir }}`
`{{ jenis_kelamin }}` `{{ alamat }}` `{{ agama }}` `{{ status_perkawinan }}`
`{{ pekerjaan }}` `{{ kewarganegaraan }}` `{{ nomor_surat }}` `{{ keperluan }}`
`{{ tanggal_surat }}`

> Catatan: karena template sudah dinamis, cara lama (mengedit dictionary `TEMPLATES`
> di `app.py`) **tidak diperlukan lagi** dan sudah dihapus.

## 5. Cara pakai (Generate Surat)

1. Ketik NIK warga.
2. Pilih jenis surat dari dropdown, kolom "Nomor Surat" langsung menampilkan
   preview nomor berikutnya (belum resmi terpakai selama tombol belum diklik).
3. Isi keperluan (opsional).
4. Klik **Cari & Buat Surat**. Di titik ini nomor surat baru resmi tersimpan,
   dan salinan `.docx`-nya ikut disimpan di folder `surat_terbit/`.
5. Klik tombol download untuk mengunduh file `.docx`.
6. Buka di Word untuk cek, tanda tangan/stempel, lalu cetak.

## 6. Penomoran & Riwayat Surat

**Format nomor:** `{awalan}{nomor urut}/{kode unit kerja}/{tahun}`, contoh
`470/12/409.40.10/2026`.

- **Awalan** diambil dari masing-masing template (diatur saat menambah template).
- **Nomor urut** berjalan **terpisah per template** dan **reset ke 1 setiap tahun**.
- **Kode unit kerja** (`409.40.10` default) diatur lewat `KODE_UNIT_KERJA` di awal
  `app.py`, ganti dengan kode resmi instansi Anda.

**Menghapus riwayat** (menu **📜 Riwayat Surat**, tombol 🗑️ Hapus):
- Data riwayat terhapus, dan file surat hasil generate di `surat_terbit/` ikut terhapus.
- Kalau yang dihapus adalah **nomor terakhir** pada jenis surat + tahun tersebut,
  nomornya **di-roll-back** sehingga bisa dipakai ulang (berguna untuk salah input).
- Kalau **bukan** yang terakhir, counter dibiarkan agar tidak terjadi duplikasi
  nomor.

Nomor tidak akan dobel meski beberapa staf klik "Buat Surat" nyaris bersamaan
**di komputer yang sama** — dilindungi kunci file (`kunci_file.py`, tanpa dependency
pihak ketiga). Batasan multi-komputer sama seperti versi sebelumnya (lihat bagian 8).

## 7. Menggunakan data warga Anda sendiri

Ganti isi `data_warga_contoh.xlsx` dengan data asli, atau ubah `DATA_PATH` di
`app.py`. Kolom yang harus ada (persis, huruf besar/kecil berpengaruh):

| Kolom | Contoh isi |
|---|---|
| NIK | 3507031234560001 |
| Nama | Siti Aminah |
| Tempat Lahir | Malang |
| Tanggal Lahir | 1990-08-17 |
| Jenis Kelamin | Perempuan |
| Alamat | Jl. Merdeka No. 10, RT 02/RW 05 |
| Agama | Islam |
| Status Perkawinan | Kawin |
| Pekerjaan | Wiraswasta |
| Kewarganegaraan | WNI |

**⚠️ Kolom NIK:** NIK 16 digit; Excel format Angka hanya akurat 15 digit (digit
terakhir bisa jadi 0). Sebelum mengetik/menempel NIK: blok kolom NIK → klik kanan →
**Format Cells** → **Text**, baru ketik/paste.

## 8. Keamanan (WAJIB DIBACA sebelum pakai data asli)

- **Dikunci ke localhost** lewat `.streamlit/config.toml` (`address = "127.0.0.1"`),
  jadi tidak bisa diakses perangkat lain di jaringan yang sama.
- **Gerbang kata sandi** lewat `.streamlit/secrets.toml` (lihat bagian 2).
- **Telemetry Streamlit dimatikan** (`gatherUsageStats = false`).
- "Localhost" **tidak** melindungi dari laptop dicuri, akun komputer tanpa password,
  malware, atau sinkron cloud pribadi. Aktifkan enkripsi disk (BitLocker/FileVault),
  password akun yang kuat, antivirus, dan jangan taruh folder ini di folder yang
  tersinkron ke cloud pribadi.

**Batasan multi-komputer:** kunci file hanya berlaku untuk satu `riwayat_surat.json`
di satu lokasi. Kalau dijalankan di beberapa komputer dengan salinan file terpisah,
penomoran berjalan sendiri-sendiri dan bisa bentrok. Kalau perlu konsisten
lintas-komputer, tetapkan satu "meja penomoran resmi", atau simpan `templates.json`
+ `riwayat_surat.json` + folder `templates/` & `surat_terbit/` di lokasi bersama
(server file kantor), dan konsultasikan ke staf IT/Diskominfo mengingat sensitivitas
data kependudukan.

## 9. (Opsional) Hasil langsung PDF

Install LibreOffice, lalu konversi file `.docx`:
```bash
soffice --headless --convert-to pdf nama_file.docx
```
Secara default aplikasi menghasilkan `.docx` agar staf masih bisa mengoreksi isi
surat sebelum dicetak.
