# -*- coding: utf-8 -*-
"""
ekran.py - Ekran goruntusu alma, PNG okuma/yazma ve sablon (gorsel) arama.

Harici kutuphane kullanmaz: ekran yakalama Windows GDI (ctypes),
PNG kodlama/cozme ise zlib ile yapilir.

Piksel duzeni her yerde BGRA'dir (Windows DIB duzeni); alfa kanali
karsilastirmayi bozmamasi icin daima 0'a cekilir.
"""

import ctypes
import os
import struct
import zlib
from ctypes import wintypes

gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)

SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0
BI_RGB = 0


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


# 64-bit'te tutamaclarin kirpilmamasi icin imzalar acikca bildirilir
gdi32.CreateDCW.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p)
gdi32.CreateDCW.restype = ctypes.c_void_p
gdi32.CreateCompatibleDC.argtypes = (ctypes.c_void_p,)
gdi32.CreateCompatibleDC.restype = ctypes.c_void_p
gdi32.CreateDIBSection.argtypes = (ctypes.c_void_p, ctypes.POINTER(BITMAPINFO), ctypes.c_uint,
                                   ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p, ctypes.c_uint)
gdi32.CreateDIBSection.restype = ctypes.c_void_p
gdi32.SelectObject.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
gdi32.SelectObject.restype = ctypes.c_void_p
gdi32.BitBlt.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                         ctypes.c_void_p, ctypes.c_int, ctypes.c_int, wintypes.DWORD)
gdi32.BitBlt.restype = wintypes.BOOL
gdi32.DeleteObject.argtypes = (ctypes.c_void_p,)
gdi32.DeleteDC.argtypes = (ctypes.c_void_p,)
user32.GetDC.argtypes = (ctypes.c_void_p,)
user32.GetDC.restype = ctypes.c_void_p
user32.ReleaseDC.argtypes = (ctypes.c_void_p, ctypes.c_void_p)

SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79


def sanal_ekran():
    """(sol, ust, genislik, yukseklik) - tum monitorleri kapsayan alan."""
    return (
        user32.GetSystemMetrics(SM_XVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_YVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_CXVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_CYVIRTUALSCREEN),
    )


# ---------------------------------------------------------------- ekran yakalama
def yakala(sol=None, ust=None, genislik=None, yukseklik=None):
    """
    Ekranin (bir bolumunun) goruntusunu alir.
    Donus: (bgra_baytlari, genislik, yukseklik, sol, ust)
    Koordinatlar ekran (fiziksel piksel) cinsindendir; cok monitorlu
    kurulumlarda negatif olabilir.
    """
    vsol, vust, vgen, vyuk = sanal_ekran()
    if sol is None:
        sol, ust, genislik, yukseklik = vsol, vust, vgen, vyuk
    if genislik <= 0 or yukseklik <= 0:
        raise ValueError("Gecersiz bolge boyutu: %sx%s" % (genislik, yukseklik))

    ekran_dc = gdi32.CreateDCW("DISPLAY", None, None, None) or user32.GetDC(None)
    if not ekran_dc:
        raise ctypes.WinError(ctypes.get_last_error())

    bellek_dc = hbitmap = eski = None
    try:
        bellek_dc = gdi32.CreateCompatibleDC(ekran_dc)
        if not bellek_dc:
            raise ctypes.WinError(ctypes.get_last_error())

        bilgi = BITMAPINFO()
        bilgi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bilgi.bmiHeader.biWidth = genislik
        bilgi.bmiHeader.biHeight = -yukseklik      # negatif: yukaridan asagiya
        bilgi.bmiHeader.biPlanes = 1
        bilgi.bmiHeader.biBitCount = 32
        bilgi.bmiHeader.biCompression = BI_RGB

        isaretci = ctypes.c_void_p()
        hbitmap = gdi32.CreateDIBSection(bellek_dc, ctypes.byref(bilgi), DIB_RGB_COLORS,
                                         ctypes.byref(isaretci), None, 0)
        if not hbitmap or not isaretci:
            raise ctypes.WinError(ctypes.get_last_error())

        eski = gdi32.SelectObject(bellek_dc, hbitmap)
        if not gdi32.BitBlt(bellek_dc, 0, 0, genislik, yukseklik,
                            ekran_dc, sol, ust, SRCCOPY):
            raise ctypes.WinError(ctypes.get_last_error())

        veri = bytearray(ctypes.string_at(isaretci, genislik * yukseklik * 4))
        veri[3::4] = bytes(genislik * yukseklik)   # alfa kanalini sifirla
        return bytes(veri), genislik, yukseklik, sol, ust
    finally:
        if eski and bellek_dc:
            gdi32.SelectObject(bellek_dc, eski)
        if hbitmap:
            gdi32.DeleteObject(hbitmap)
        if bellek_dc:
            gdi32.DeleteDC(bellek_dc)
        gdi32.DeleteDC(ekran_dc)


# ---------------------------------------------------------------- PNG
def _parca(etiket, veri):
    govde = etiket + veri
    return struct.pack(">I", len(veri)) + govde + struct.pack(">I", zlib.crc32(govde) & 0xFFFFFFFF)


def png_kaydet(yol, bgra, genislik, yukseklik):
    """BGRA baytlarini 8 bit RGB PNG olarak yazar (filtre 0 - hizli okunur)."""
    rgb = bytearray(genislik * yukseklik * 3)
    rgb[0::3] = bgra[2::4]
    rgb[1::3] = bgra[1::4]
    rgb[2::3] = bgra[0::4]

    satir_bayt = genislik * 3
    ham = bytearray()
    for y in range(yukseklik):
        ham.append(0)                                   # filtre turu: yok
        ham += rgb[y * satir_bayt:(y + 1) * satir_bayt]

    basliklar = struct.pack(">IIBBBBB", genislik, yukseklik, 8, 2, 0, 0, 0)
    with open(yol, "wb") as dosya:
        dosya.write(b"\x89PNG\r\n\x1a\n")
        dosya.write(_parca(b"IHDR", basliklar))
        dosya.write(_parca(b"IDAT", zlib.compress(bytes(ham), 6)))
        dosya.write(_parca(b"IEND", b""))


def _filtre_coz(ham, genislik, yukseklik, bpp):
    satir_bayt = genislik * bpp
    sonuc = bytearray(satir_bayt * yukseklik)
    onceki = bytearray(satir_bayt)
    konum = 0
    for y in range(yukseklik):
        filtre = ham[konum]
        konum += 1
        satir = bytearray(ham[konum:konum + satir_bayt])
        konum += satir_bayt
        if filtre == 1:
            for i in range(bpp, satir_bayt):
                satir[i] = (satir[i] + satir[i - bpp]) & 0xFF
        elif filtre == 2:
            for i in range(satir_bayt):
                satir[i] = (satir[i] + onceki[i]) & 0xFF
        elif filtre == 3:
            for i in range(satir_bayt):
                sol = satir[i - bpp] if i >= bpp else 0
                satir[i] = (satir[i] + ((sol + onceki[i]) >> 1)) & 0xFF
        elif filtre == 4:
            for i in range(satir_bayt):
                a = satir[i - bpp] if i >= bpp else 0
                b = onceki[i]
                c = onceki[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                tahmin = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                satir[i] = (satir[i] + tahmin) & 0xFF
        elif filtre != 0:
            raise ValueError("Desteklenmeyen PNG filtresi: %d" % filtre)
        sonuc[y * satir_bayt:(y + 1) * satir_bayt] = satir
        onceki = satir
    return sonuc


def png_oku(yol):
    """PNG dosyasini okur. Donus: (bgra_baytlari, genislik, yukseklik)."""
    with open(yol, "rb") as dosya:
        icerik = dosya.read()
    if not icerik.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Bu bir PNG dosyasi degil: %s" % os.path.basename(yol))

    konum = 8
    genislik = yukseklik = renk_turu = bit_derinligi = None
    veri = bytearray()
    while konum + 8 <= len(icerik):
        uzunluk = struct.unpack(">I", icerik[konum:konum + 4])[0]
        etiket = icerik[konum + 4:konum + 8]
        govde = icerik[konum + 8:konum + 8 + uzunluk]
        konum += 12 + uzunluk
        if etiket == b"IHDR":
            genislik, yukseklik, bit_derinligi, renk_turu, _s, _f, aralikli = \
                struct.unpack(">IIBBBBB", govde[:13])
            if aralikli:
                raise ValueError("Aralikli (interlaced) PNG desteklenmiyor.")
        elif etiket == b"IDAT":
            veri += govde
        elif etiket == b"IEND":
            break

    if genislik is None:
        raise ValueError("PNG basligi (IHDR) bulunamadi.")
    if bit_derinligi != 8 or renk_turu not in (0, 2, 6):
        raise ValueError("Yalnizca 8 bit gri/RGB/RGBA PNG desteklenir "
                         "(derinlik=%s, tur=%s)." % (bit_derinligi, renk_turu))

    bpp = {0: 1, 2: 3, 6: 4}[renk_turu]
    duz = _filtre_coz(zlib.decompress(bytes(veri)), genislik, yukseklik, bpp)

    bgra = bytearray(genislik * yukseklik * 4)
    if renk_turu == 0:
        bgra[0::4] = duz
        bgra[1::4] = duz
        bgra[2::4] = duz
    else:
        bgra[0::4] = duz[2::bpp]
        bgra[1::4] = duz[1::bpp]
        bgra[2::4] = duz[0::bpp]
    return bytes(bgra), genislik, yukseklik


def png_boyutu(yol):
    """PNG'nin (genislik, yukseklik) degerini tum dosyayi cozmeden okur."""
    with open(yol, "rb") as dosya:
        basli = dosya.read(24)
    if len(basli) < 24 or not basli.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Bu bir PNG dosyasi degil: %s" % os.path.basename(yol))
    return struct.unpack(">II", basli[16:24])


# ---------------------------------------------------------------- sablon arama
_onbellek = {}


def sablon_yukle(yol):
    """PNG'yi okur ve dosya degismedikce bellekte tutar."""
    anahtar = (os.path.abspath(yol), os.path.getmtime(yol))
    if anahtar not in _onbellek:
        _onbellek.clear()
        _onbellek[anahtar] = png_oku(yol)
    return _onbellek[anahtar]


def _anahtar_adaylari(sablon, genislik, yukseklik, adet=6, uzunluk=24):
    """
    Sablondan, aramada kullanilacak en ayirt edici yatay piksel dizilerini secer.
    Donus: [(satir_indisi, x_kaymasi, aranacak_baytlar), ...]
    """
    uzunluk = max(4, min(uzunluk, genislik))
    satir_bayt = genislik * 4
    incelenecek = sorted({int((i + 0.5) * yukseklik / adet) for i in range(adet)})

    adaylar = []
    for satir_indisi in incelenecek:
        if not (0 <= satir_indisi < yukseklik):
            continue
        satir = sablon[satir_indisi * satir_bayt:(satir_indisi + 1) * satir_bayt]
        pikseller = [satir[i:i + 4] for i in range(0, satir_bayt, 4)]
        en_iyi_x, en_iyi_puan = 0, -1
        for x in range(0, genislik - uzunluk + 1):
            puan = len(set(pikseller[x:x + uzunluk]))
            if puan > en_iyi_puan:
                en_iyi_x, en_iyi_puan = x, puan
                if puan == uzunluk:
                    break
        adaylar.append((en_iyi_puan, satir_indisi, en_iyi_x,
                        satir[en_iyi_x * 4:(en_iyi_x + uzunluk) * 4]))

    adaylar.sort(key=lambda a: -a[0])            # en ayirt edici once
    return [(s, x, b) for _p, s, x, b in adaylar]


def _dogrula(ekran, adim_bayt, x, y, sablon_satirlar, izin_verilen_fark):
    fark = 0
    for i, sablon_satir in enumerate(sablon_satirlar):
        bas = (y + i) * adim_bayt + x * 4
        dilim = ekran[bas:bas + len(sablon_satir)]
        if dilim == sablon_satir:
            continue
        if izin_verilen_fark == 0:
            return False
        for j in range(0, len(sablon_satir), 4):
            if dilim[j:j + 3] != sablon_satir[j:j + 3]:
                fark += 1
                if fark > izin_verilen_fark:
                    return False
    return True


def ara(ekran, ekran_genislik, ekran_yukseklik, sablon, sablon_genislik, sablon_yukseklik,
        tolerans=0.0, en_fazla_aday=400000):
    """
    Sablonu ekran tamponunda arar.
    tolerans: 0.0-1.0 arasi, farkli olmasina izin verilen piksel orani.
    Donus: (x, y) sol ust kose (tampon koordinati) veya None.
    """
    if sablon_genislik > ekran_genislik or sablon_yukseklik > ekran_yukseklik:
        return None

    adim_bayt = ekran_genislik * 4
    sablon_satir_bayt = sablon_genislik * 4
    sablon_satirlar = [sablon[i * sablon_satir_bayt:(i + 1) * sablon_satir_bayt]
                       for i in range(sablon_yukseklik)]
    izin_verilen_fark = int(sablon_genislik * sablon_yukseklik * max(0.0, min(1.0, tolerans)))

    for satir_indisi, x_kaymasi, anahtar in _anahtar_adaylari(
            sablon, sablon_genislik, sablon_yukseklik):
        anahtar_piksel = len(anahtar) // 4
        konum, incelenen = 0, 0
        while incelenen < en_fazla_aday:
            bulunan = ekran.find(anahtar, konum)
            if bulunan < 0:
                break
            konum = bulunan + 1
            if bulunan % 4:
                continue                      # piksel sinirina oturmuyor
            incelenen += 1
            x = (bulunan % adim_bayt) // 4
            y = bulunan // adim_bayt
            if x + anahtar_piksel > ekran_genislik:
                continue                      # satir sonunu asiyor
            sol, ust = x - x_kaymasi, y - satir_indisi
            if sol < 0 or ust < 0:
                continue
            if sol + sablon_genislik > ekran_genislik or ust + sablon_yukseklik > ekran_yukseklik:
                continue
            if _dogrula(ekran, adim_bayt, sol, ust, sablon_satirlar, izin_verilen_fark):
                return sol, ust
    return None


def sablonu_bul(sablon_yolu, tolerans=0.0, arama_bolgesi=None):
    """
    Sablonu ekranda arar.
    arama_bolgesi: (sol, ust, genislik, yukseklik) ekran koordinati veya None.
    Donus: (sol, ust, genislik, yukseklik) ekran koordinatinda veya None.
    """
    sablon, sgen, syuk = sablon_yukle(sablon_yolu)
    if arama_bolgesi:
        ekran_bayt, egen, eyuk, esol, eust = yakala(*arama_bolgesi)
    else:
        ekran_bayt, egen, eyuk, esol, eust = yakala()

    sonuc = ara(ekran_bayt, egen, eyuk, sablon, sgen, syuk, tolerans)
    if sonuc is None:
        return None
    return esol + sonuc[0], eust + sonuc[1], sgen, syuk
