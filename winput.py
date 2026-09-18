# -*- coding: utf-8 -*-
"""
winput.py - Windows fare/klavye girdi katmani (saf ctypes, harici kutuphane yok).

SendInput API'si kullanilir; SetCursorPos'a gore uygulama/oyun uyumlulugu daha yuksektir.
Koordinatlar FIZIKSEL piksel cinsindendir (DPI-aware).
"""

import ctypes
import time
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)


# ---------------------------------------------------------------- DPI farkindalik
def dpi_farkindaligi_ac():
    """Ekran olcekleme (%125, %150 ...) altinda koordinatlarin kaymamasi icin."""
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return "per-monitor-v2"
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return "per-monitor"
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        return "system"
    except Exception:
        return "yok"


# ---------------------------------------------------------------- Yapilar
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79

user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT
user32.GetAsyncKeyState.argtypes = (ctypes.c_int,)
user32.GetAsyncKeyState.restype = ctypes.c_short
user32.VkKeyScanW.argtypes = (ctypes.c_wchar,)
user32.VkKeyScanW.restype = ctypes.c_short


def _gonder(*girdiler):
    dizi = (INPUT * len(girdiler))(*girdiler)
    yollanan = user32.SendInput(len(girdiler), dizi, ctypes.sizeof(INPUT))
    if yollanan != len(girdiler):
        raise ctypes.WinError(ctypes.get_last_error())


# ---------------------------------------------------------------- Imlec / ekran
def imlec_konumu():
    nokta = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(nokta))
    return int(nokta.x), int(nokta.y)


def sanal_ekran():
    """(sol, ust, genislik, yukseklik) - tum monitorleri kapsayan alan."""
    return (
        user32.GetSystemMetrics(SM_XVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_YVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_CXVIRTUALSCREEN),
        user32.GetSystemMetrics(SM_CYVIRTUALSCREEN),
    )


def _mutlak(x, y):
    vx, vy, vw, vh = sanal_ekran()
    nx = int(round((x - vx) * 65535.0 / max(1, vw - 1)))
    ny = int(round((y - vy) * 65535.0 / max(1, vh - 1)))
    return max(0, min(65535, nx)), max(0, min(65535, ny))


def _fare(bayraklar, dx=0, dy=0, veri=0):
    return INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(dx=dx, dy=dy, mouseData=veri, dwFlags=bayraklar, time=0, dwExtraInfo=0),
    )


def fareyi_tasi(x, y):
    """Mutlak konuma tasir (coklu monitor ve negatif koordinat destekli)."""
    nx, ny = _mutlak(x, y)
    _gonder(_fare(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK, nx, ny))


DUGMELER = {
    "sol": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    "sag": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
    "orta": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
}


def tikla(dugme="sol", basili_ms=25):
    bas, birak_bayragi = DUGMELER[dugme]
    _gonder(_fare(bas))
    time.sleep(max(0.0, basili_ms / 1000.0))
    _gonder(_fare(birak_bayragi))


def cift_tikla(dugme="sol", ara_ms=60):
    tikla(dugme)
    time.sleep(max(0.0, ara_ms / 1000.0))
    tikla(dugme)


def basili_tut(dugme="sol"):
    _gonder(_fare(DUGMELER[dugme][0]))


def dugmeyi_birak(dugme="sol"):
    _gonder(_fare(DUGMELER[dugme][1]))


def tekerlek(cent=1):
    """Pozitif deger yukari, negatif deger asagi kaydirir. 1 cent = 120 birim."""
    _gonder(_fare(MOUSEEVENTF_WHEEL, veri=ctypes.c_int(int(cent) * 120).value & 0xFFFFFFFF))


# ---------------------------------------------------------------- Klavye
VK = {
    "enter": 0x0D, "return": 0x0D, "giris": 0x0D,
    "tab": 0x09, "sekme": 0x09,
    "esc": 0x1B, "escape": 0x1B,
    "space": 0x20, "bosluk": 0x20,
    "backspace": 0x08, "geri": 0x08,
    "delete": 0x2E, "del": 0x2E, "sil": 0x2E,
    "insert": 0x2D, "ins": 0x2D,
    "home": 0x24, "end": 0x23,
    "pageup": 0x21, "pgup": 0x21, "pagedown": 0x22, "pgdn": 0x22,
    "up": 0x26, "yukari": 0x26,
    "down": 0x28, "asagi": 0x28,
    "left": 0x25, "sol": 0x25,
    "right": 0x27, "sag": 0x27,
    "ctrl": 0x11, "control": 0x11, "kontrol": 0x11,
    "shift": 0x10,
    "alt": 0x12, "menu": 0x12,
    "win": 0x5B, "windows": 0x5B,
    "capslock": 0x14, "printscreen": 0x2C, "prtsc": 0x2C,
    "numlock": 0x90, "scrolllock": 0x91, "pause": 0x13,
    "numplus": 0x6B, "numminus": 0x6D, "numcarpi": 0x6A, "numbolu": 0x6F,
}
for _i in range(1, 25):
    VK["f%d" % _i] = 0x6F + _i
for _i in range(10):
    VK[str(_i)] = 0x30 + _i
    VK["num%d" % _i] = 0x60 + _i
for _c in "abcdefghijklmnopqrstuvwxyz":
    VK[_c] = 0x41 + ord(_c) - ord("a")

# Genisletilmis tus bayragi gerektirenler (ok tuslari, gezinme bloku, numlock ...)
GENISLETILMIS = {0x26, 0x28, 0x25, 0x27, 0x24, 0x23, 0x21, 0x22, 0x2D, 0x2E, 0x5B, 0x5C, 0x2C, 0x90}


def _tus_girdisi(vk, birak_mi=False):
    bayrak = KEYEVENTF_KEYUP if birak_mi else 0
    if vk in GENISLETILMIS:
        bayrak |= KEYEVENTF_EXTENDEDKEY
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(wVk=vk, wScan=0, dwFlags=bayrak, time=0, dwExtraInfo=0),
    )


def _unicode_girdisi(karakter, birak_mi=False):
    bayrak = KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if birak_mi else 0)
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(wVk=0, wScan=ord(karakter), dwFlags=bayrak, time=0, dwExtraInfo=0),
    )


def kombinasyon_coz(metin):
    """"ctrl+shift+s" -> ([0x11, 0x10], 0x53). Cozulemezse ValueError firlatir."""
    ham = str(metin).strip()
    if not ham:
        raise ValueError("Tus adi bos.")
    parcalar = [p.strip().lower() for p in ham.split("+")]
    # "ctrl++" gibi yazimlarda ana tus '+' karakteridir
    if len(parcalar) >= 2 and parcalar[-1] == "" and parcalar[-2] == "":
        parcalar = parcalar[:-2] + ["+"]
    if any(p == "" for p in parcalar):
        raise ValueError("Tus yazimi hatali (fazladan veya eksik '+'): %s" % ham)
    degistirici_adlari, ana = parcalar[:-1], parcalar[-1]
    degistiriciler = []
    for d in degistirici_adlari:
        if d not in VK:
            raise ValueError("Bilinmeyen degistirici tus: %s" % d)
        degistiriciler.append(VK[d])
    if ana in VK:
        return degistiriciler, VK[ana]
    if len(ana) == 1:
        kod = user32.VkKeyScanW(ana)
        if kod != -1:
            # Ust bayt, o karakter icin gereken degistiricileri bildirir
            # (mevcut klavye duzenine gore: 1=Shift, 2=Ctrl, 4=Alt)
            durum = (kod >> 8) & 0xFF
            for bayrak, vk in ((1, VK["shift"]), (2, VK["ctrl"]), (4, VK["alt"])):
                if durum & bayrak and vk not in degistiriciler:
                    degistiriciler.append(vk)
            return degistiriciler, kod & 0xFF
    raise ValueError("Bilinmeyen tus: %s" % ana)


def tusa_bas(kombinasyon, basili_ms=25):
    degistiriciler, ana = kombinasyon_coz(kombinasyon)
    for m in degistiriciler:
        _gonder(_tus_girdisi(m))
    _gonder(_tus_girdisi(ana))
    time.sleep(max(0.0, basili_ms / 1000.0))
    _gonder(_tus_girdisi(ana, True))
    for m in reversed(degistiriciler):
        _gonder(_tus_girdisi(m, True))


def metin_yaz(metin, karakter_gecikmesi_ms=8):
    """Unicode ile yazar; Turkce karakterler klavye duzeninden bagimsiz calisir."""
    for karakter in str(metin):
        if karakter == "\n":
            tusa_bas("enter")
        elif karakter == "\t":
            tusa_bas("tab")
        else:
            _gonder(_unicode_girdisi(karakter), _unicode_girdisi(karakter, True))
        if karakter_gecikmesi_ms > 0:
            time.sleep(karakter_gecikmesi_ms / 1000.0)


VK_ESCAPE = 0x1B


def tus_basili_mi(vk=VK_ESCAPE):
    """Acil durdurma icin: tus su anda fiziksel olarak basili mi?"""
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)
