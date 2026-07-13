"""Kunci file lintas-platform TANPA dependency pihak ketiga.

Menggantikan package `filelock` dengan primitif kunci bawaan OS:
- Windows -> msvcrt.locking()
- Linux/Mac -> fcntl.flock()

Dipakai sebagai context manager:
    with KunciFile("riwayat_surat.json.lock"):
        ... baca-ubah-simpan file riwayat_surat.json di sini ...
"""

import sys
import time

_IS_WINDOWS = sys.platform.startswith("win")

if _IS_WINDOWS:
    import msvcrt
else:
    import fcntl


class KunciFile:
    """Context manager kunci-file exclusive. Aman dipakai lintas proses
    (beberapa staf menjalankan `streamlit run` di komputer yang sama, atau
    beberapa tab browser ke satu server Streamlit yang sama)."""

    def __init__(self, path: str, timeout: float = 10.0):
        self._path = path
        self._timeout = timeout
        self._file = None

    def __enter__(self):
        self._file = open(self._path, "a+b")
        mulai = time.monotonic()

        if _IS_WINDOWS:
            while True:
                try:
                    self._file.seek(0)
                    msvcrt.locking(self._file.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() - mulai > self._timeout:
                        self._file.close()
                        raise TimeoutError(
                            f"Tidak bisa mengunci '{self._path}' setelah {self._timeout}s "
                            "(kemungkinan ada proses lain yang macet memegang kuncinya)."
                        )
                    time.sleep(0.05)
        else:
            fcntl.flock(self._file.fileno(), fcntl.LOCK_EX)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if _IS_WINDOWS:
                self._file.seek(0)
                msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
        finally:
            self._file.close()
        return False
