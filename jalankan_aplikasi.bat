@echo off
title Generator Surat Warga
cd /d "%~dp0"

echo ============================================
echo   Generator Surat Warga - Memulai aplikasi
echo ============================================
echo.

REM Cek apakah Python sudah terpasang
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [GAGAL] Python belum terpasang di komputer ini.
    echo Silakan install Python dulu dari https://python.org lalu coba lagi.
    pause
    exit /b
)

REM Cek apakah library yang dibutuhkan sudah terpasang, kalau belum akan diinstall otomatis
python -c "import streamlit" >nul 2>nul
if %errorlevel% neq 0 (
    echo Menyiapkan aplikasi untuk pertama kali, mohon tunggu sebentar...
    pip install -r requirements.txt
)

echo.
echo Membuka aplikasi di browser...
echo (Jangan tutup jendela hitam ini selama aplikasi masih dipakai)
echo.

streamlit run app.py

pause
