# -*- coding: utf-8 -*-
"""
exe_yap.py - Programi tek dosyalik bir .exe haline getirir.

Kullanim:  python exe_yap.py
Gereksinim: python -m pip install pyinstaller

Uretilen exe, derlemeyi yapan Python'un mimarisini tasir; dosya adina da o
mimari yazilir. Ornegin:
    py -3.11  exe_yap.py   ->  Otomatik Tiklayici (x64).exe
    py -3.14-arm64 exe_yap.py  ->  Otomatik Tiklayici (ARM64).exe

Sonuc:  Otomatik Tiklayici (<mimari>).exe  (bu klasorde)

Exe, ayarlarini ve 'goruntuler' klasorunu kendi bulundugu yere yazar. Bu yuzden
buraya, mevcut ayarlar.json ve goruntuler klasorunun yanina uretilir; boylece
betik surumuyle ayni verileri kullanir.
"""

import os
import platform
import shutil
import subprocess
import sys

KLASOR = os.path.dirname(os.path.abspath(__file__))
GIRIS = "otomatik_tiklayici.py"
SIMGE = "simge.ico"
DIST = KLASOR                                    # exe dogrudan proje klasorune
BUILD = os.path.join(KLASOR, "derleme_gecici")   # ara dosyalar

MIMARILER = {"AMD64": "x64", "ARM64": "ARM64", "x86": "x86"}
MIMARI = MIMARILER.get(platform.machine(), platform.machine() or "bilinmeyen")
UYGULAMA = "Otomatik Tiklayici (%s)" % MIMARI


def main():
    if not sys.platform.startswith("win"):
        print("Bu program yalnizca Windows icin derlenir.")
        return 1

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller kurulu degil. Once sunu calistirin:")
        print("    python -m pip install pyinstaller")
        return 1

    # Ara klasoru kendimiz temizleriz: PyInstaller'in --clean secenegi
    # OneDrive/antivirus kilitli dosyalarda "Erisim engellendi" ile duruyor.
    shutil.rmtree(BUILD, ignore_errors=True)

    komut = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",              # tek dosya
        "--windowed",             # konsol penceresi acilmasin
        "--name", UYGULAMA,
        "--distpath", DIST,
        "--workpath", os.path.join(BUILD, "calisma"),
        "--specpath", BUILD,
        os.path.join(KLASOR, GIRIS),
    ]
    if os.path.isfile(os.path.join(KLASOR, SIMGE)):
        komut[komut.index("--name"):komut.index("--name")] = \
            ["--icon", os.path.join(KLASOR, SIMGE)]
    else:
        print("(bilgi) %s bulunamadi, varsayilan simge kullanilacak." % SIMGE)

    print("Derleniyor...  (Python %s, %s -> %s)\n"
          % (sys.version.split()[0], platform.machine(), MIMARI))
    sonuc = subprocess.run(komut, cwd=KLASOR)
    if sonuc.returncode != 0:
        print("\nDerleme BASARISIZ (cikis kodu %d)." % sonuc.returncode)
        return sonuc.returncode

    exe = os.path.join(DIST, UYGULAMA + ".exe")
    if not os.path.isfile(exe):
        print("\nDerleme bitti ama exe bulunamadi: %s" % exe)
        return 1

    print("\n" + "=" * 62)
    print("HAZIR:   %s" % exe)
    print("Mimari:  %s  (yalnizca bu mimarideki Windows'ta calisir)" % MIMARI)
    print("Boyut:   %.1f MB" % (os.path.getsize(exe) / 1024 / 1024))
    print()
    print("Bu dosyaya cift tiklayarak calistirin; Python kurulu olmasi gerekmez.")
    print("Baska bir bilgisayara tasirken 'goruntuler' klasorunu de goturun -")
    print("goruntu hedefli adimlar sablonlari oradan okur.")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
