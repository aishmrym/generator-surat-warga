# Generator Surat Warga (Otomatis via NIK)

Aplikasi lokal (localhost) sederhana untuk perangkat desa: ketik NIK, pilih jenis
surat, klik satu tombol → surat langsung terisi otomatis dari data warga,
**nomor surat terisi otomatis dan berurutan**, lalu siap diunduh sebagai file Word.

## Isi folder

```
surat-generator/
├── app.py                      ← aplikasi utama (Streamlit)
├── requirements.txt            ← daftar library yang dibutuhkan
├── data_warga_contoh.xlsx      ← CONTOH data warga (ganti dengan data asli)
├── riwayat_surat.csv           ← dibuat otomatis oleh aplikasi, jangan dihapus
└── templates/
    ├── surat_pengantar.docx
    ├── surat_domisili.docx
    └── surat_tidak_mampu.docx
```

## 1. Instalasi (sekali saja)

Perlu Python 3.9+ sudah terpasang di komputer. Buka Command Prompt/Terminal di
folder ini, lalu jalankan:

```bash
pip install -r requirements.txt
```

## 2. Menjalankan aplikasi

```bash
streamlit run app.py
```

Browser akan otomatis terbuka (biasanya di `http://localhost:8501`). Aplikasi ini
berjalan lokal di komputer sendiri — data warga tidak terkirim ke internet.

## 3. Cara pakai

1. Ketik NIK warga di kolom yang tersedia.
2. Pilih jenis surat dari dropdown — nomor surat berikutnya otomatis muncul sebagai pratinjau.
3. Isi keperluan (opsional).
4. Klik **"Cari & Buat Surat"**. Nomor surat resmi baru dicatat ke riwayat saat tombol ini ditekan.
5. Klik tombol download untuk mengunduh file `.docx` yang sudah terisi otomatis.
6. Buka file itu di Word untuk cek sekali lagi, tanda tangan/stempel, lalu cetak.

## 4. WAJIB — Menggunakan data warga Anda sendiri

Ganti isi `data_warga_contoh.xlsx` dengan data asli, **atau** ganti nama file
tersebut di baris `DATA_PATH` pada `app.py`. Kolom yang harus ada persis sama
namanya (huruf besar/kecil berpengaruh):

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

**⚠️ PENTING soal kolom NIK:** NIK punya 16 digit, sedangkan Excel hanya akurat
sampai 15 digit kalau kolomnya berformat Angka — digit terakhir bisa otomatis
berubah jadi 0 tanpa disadari. Sebelum mengetik/menempel data NIK:

1. Blok seluruh kolom NIK.
2. Klik kanan → **Format Cells** → pilih **Text**.
3. Baru ketik/paste NIK-nya.

Kalau data NIK sudah lama diketik sebagai Angka dan sudah rusak (ada digit yang
jadi 0), NIK tersebut harus diketik ulang manual dari sumber aslinya (KTP/KK) —
tidak bisa diperbaiki lewat aplikasi ini karena datanya sudah hilang di sumbernya.

## 5. Nomor surat otomatis & riwayat

Aplikasi ini **membuat nomor surat sendiri secara berurutan**, tidak perlu diketik
manual lagi. Cara kerjanya:

- Setiap kali surat berhasil dibuat, nomornya dicatat ke file `riwayat_surat.csv`.
- Nomor urut berikutnya otomatis dihitung dari baris terakhir di file tersebut,
  lalu **reset ke 1 setiap kali masuk tahun baru**.
- Format nomor default: `470/003/Ds/2026` (kode-jenis-surat/nomor-urut/kode-instansi/tahun).
  Anda bisa lihat & ubah bagian riwayatnya lewat expander **"📜 Riwayat Nomor Surat
  yang Sudah Dibuat"** di bagian bawah aplikasi.

**Menyesuaikan formatnya:** kalau desa Anda punya format nomor surat sendiri
(sesuai tata naskah dinas Kecamatan/Kabupaten setempat), buka `app.py` di bagian
paling atas dan ubah tiga hal ini:

```python
KODE_SURAT = {
    "Surat Pengantar": "474",
    "Surat Keterangan Domisili": "470",
    "Surat Keterangan Tidak Mampu": "460",
}
KODE_DESA = "Ds"  # ganti dengan kode/singkatan resmi desa Anda
NOMOR_SURAT_FORMAT = "{kode}/{urut}/{desa}/{tahun}"
```

`NOMOR_SURAT_FORMAT` bisa disusun ulang sesuka Anda, tinggal pakai variabel
`{kode}` `{urut}` `{desa}` `{bulan_romawi}` `{tahun}` (variabel `{bulan_romawi}`
tersedia kalau sewaktu-waktu ingin ditambahkan lagi ke format).

⚠️ **Jangan hapus atau edit manual file `riwayat_surat.csv`** kecuali Anda tahu
persis apa yang dilakukan — dari file itulah aplikasi tahu nomor urut terakhir
yang sudah dipakai, supaya tidak ada nomor surat yang dobel.

## 6. Menambah jenis surat baru

1. Buka salah satu file di `templates/` sebagai contoh format.
2. Duplikat, ubah judul & isi kalimatnya sesuai jenis surat baru, simpan dengan
   nama baru di folder `templates/`. Placeholder `{{ nama }}`, `{{ nik }}`, dst
   jangan diubah namanya — itu yang otomatis diisi oleh aplikasi.
3. Buka `app.py`, tambahkan satu baris di dictionary `TEMPLATES` (di bagian atas file):
   ```python
   TEMPLATES = {
       "Surat Pengantar": "surat_pengantar.docx",
       "Surat Keterangan Domisili": "surat_domisili.docx",
       "Surat Keterangan Tidak Mampu": "surat_tidak_mampu.docx",
       "Surat Keterangan Usaha": "surat_keterangan_usaha.docx",   # <- baris baru
   }
   ```
4. (Opsional) tambahkan juga kode klasifikasinya di `KODE_SURAT` supaya nomor
   suratnya punya kode yang sesuai.
5. Simpan, jalankan ulang `streamlit run app.py`.

Variabel yang tersedia untuk dipakai di template manapun (tulis persis dengan
tanda kurung kurawal ganda di dalam file Word):

`{{ nik }}` `{{ nama }}` `{{ tempat_lahir }}` `{{ tanggal_lahir }}`
`{{ jenis_kelamin }}` `{{ alamat }}` `{{ agama }}` `{{ status_perkawinan }}`
`{{ pekerjaan }}` `{{ kewarganegaraan }}` `{{ nomor_surat }}` `{{ keperluan }}`
`{{ tanggal_surat }}`

## 7. Mengubah kop surat / kepala desa

Buka file `.docx` di folder `templates/` langsung dengan Microsoft Word, ganti
teks `[NAMA KABUPATEN]`, `[NAMA KECAMATAN]`, `[NAMA DESA]`, `[Alamat Kantor Desa]`,
dan `[Nama Terang Kepala Desa]` dengan data yang sebenarnya — cukup edit seperti
dokumen Word biasa, lalu simpan. Placeholder `{{ ... }}` yang lain jangan disentuh.

## 8. (Opsional) Ingin hasil langsung PDF?

Install LibreOffice, lalu tambahkan baris ini di `app.py` setelah `doc.save(...)`
pada file docx sementara, lalu konversi:

```bash
soffice --headless --convert-to pdf nama_file.docx
```

Ini memerlukan LibreOffice terpasang di komputer yang menjalankan aplikasi.
Secara default aplikasi ini menghasilkan `.docx` agar staf desa masih bisa
mengoreksi/menyesuaikan isi surat sebelum dicetak.

## 9. Menjalankan untuk banyak pengguna sekaligus (opsional, lanjutan)

Jika ingin diakses banyak staf sekaligus dari komputer masing-masing (bukan
cuma satu komputer), aplikasi Streamlit ini bisa di-deploy ke:
- **Streamlit Community Cloud** (gratis, https://streamlit.io/cloud) — cocok kalau
  data warga tidak terlalu sensitif untuk disimpan di cloud pihak ketiga, atau
- Server lokal kantor desa/kecamatan yang bisa diakses lewat jaringan LAN kantor.

Kalau dipakai banyak orang sekaligus dari komputer berbeda-beda, perhatikan bahwa
`riwayat_surat.csv` harus berada di lokasi yang sama/ter-share, supaya nomor
surat tetap berurutan dan tidak dobel antar pengguna.

Untuk data kependudukan, disarankan berkonsultasi dengan Dinas Kominfo daerah
mengenai kebijakan penyimpanan data yang sesuai sebelum deploy ke cloud publik.