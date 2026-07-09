<<<<<<< HEAD
# Generator Surat Warga (Otomatis via NIK)

Aplikasi sederhana: ketik NIK, pilih jenis surat, klik satu tombol → surat langsung
terisi otomatis dari data warga dan siap diunduh sebagai file Word.

## Isi folder

```
surat-generator/
├── app.py                      ← aplikasi utama (Streamlit)
├── requirements.txt            ← daftar library yang dibutuhkan
├── data_warga_contoh.xlsx      ← CONTOH data warga (ganti dengan data asli)
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
2. Pilih jenis surat dari dropdown.
3. Isi nomor surat & keperluan (opsional).
4. Klik **"Cari & Buat Surat"**.
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

## 5. Menambah jenis surat baru

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
4. Simpan, jalankan ulang `streamlit run app.py`.

Variabel yang tersedia untuk dipakai di template manapun (tulis persis dengan
tanda kurung kurawal ganda di dalam file Word):

`{{ nik }}` `{{ nama }}` `{{ tempat_lahir }}` `{{ tanggal_lahir }}`
`{{ jenis_kelamin }}` `{{ alamat }}` `{{ agama }}` `{{ status_perkawinan }}`
`{{ pekerjaan }}` `{{ kewarganegaraan }}` `{{ nomor_surat }}` `{{ keperluan }}`
`{{ tanggal_surat }}`

## 6. Mengubah kop surat / kepala desa

Buka file `.docx` di folder `templates/` langsung dengan Microsoft Word, ganti
teks `[NAMA KABUPATEN]`, `[NAMA KECAMATAN]`, `[NAMA DESA]`, `[Alamat Kantor Desa]`,
dan `[Nama Terang Kepala Desa]` dengan data yang sebenarnya — cukup edit seperti
dokumen Word biasa, lalu simpan. Placeholder `{{ ... }}` yang lain jangan disentuh.

## 7. (Opsional) Ingin hasil langsung PDF?

Install LibreOffice, lalu tambahkan baris ini di `app.py` setelah `doc.save(...)`
pada file docx sementara, lalu konversi:

```bash
soffice --headless --convert-to pdf nama_file.docx
```

Ini memerlukan LibreOffice terpasang di komputer yang menjalankan aplikasi.
Secara default aplikasi ini menghasilkan `.docx` agar staf desa masih bisa
mengoreksi/menyesuaikan isi surat sebelum dicetak.

## 8. Menjalankan untuk banyak pengguna sekaligus (opsional, lanjutan)

Jika ingin diakses banyak staf sekaligus dari komputer masing-masing (bukan
cuma satu komputer), aplikasi Streamlit ini bisa di-deploy ke:
- **Streamlit Community Cloud** (gratis, https://streamlit.io/cloud) — cocok kalau
  data warga tidak terlalu sensitif untuk disimpan di cloud pihak ketiga, atau
- Server lokal kantor desa/kecamatan yang bisa diakses lewat jaringan LAN kantor.

Untuk data kependudukan, disarankan berkonsultasi dengan Dinas Kominfo daerah
mengenai kebijakan penyimpanan data yang sesuai sebelum deploy ke cloud publik.
=======
# generator-surat-warga
Village Letter Generator is a localhost-based web application that helps village officials generate official citizen documents quickly and consistently. It automates letter creation using templates and citizen data, reducing manual work and improving administrative efficiency.
>>>>>>> 1a1f57358c19d55c98a1173e57de35cef71572e4