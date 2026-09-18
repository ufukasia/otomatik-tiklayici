# -*- coding: utf-8 -*-
"""
kisayol.py - Sistem genelinde calisan kisayol tuslari (RegisterHotKey).

Program arka planda / kucultulmus olsa bile kisayollar calisir.
Kendi mesaj dongusune sahip ayri bir is parcaciginda yasar.
"""

import ctypes
import threading
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetMessageW.restype = ctypes.c_int

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000


class KisayolDinleyici(threading.Thread):
    """
    baglantilar: {kimlik: (degistirici_bayraklari, sanal_tus_kodu, "gorunen ad")}
    geri_cagir:  kimlik ile cagrilir (DINLEYICI is parcaciginda!)
    """

    def __init__(self, baglantilar, geri_cagir):
        super().__init__(daemon=True, name="KisayolDinleyici")
        self.baglantilar = dict(baglantilar)
        self.geri_cagir = geri_cagir
        self.basarisiz = []
        self.hazir = threading.Event()
        self._is_parcacigi_kimligi = None

    def run(self):
        self._is_parcacigi_kimligi = ctypes.windll.kernel32.GetCurrentThreadId()
        for kimlik, (degistirici, vk, ad) in self.baglantilar.items():
            if not user32.RegisterHotKey(None, kimlik, degistirici | MOD_NOREPEAT, vk):
                self.basarisiz.append(ad)
        self.hazir.set()

        mesaj = wintypes.MSG()
        while True:
            sonuc = user32.GetMessageW(ctypes.byref(mesaj), None, 0, 0)
            if sonuc in (0, -1):
                break
            if mesaj.message == WM_HOTKEY:
                try:
                    self.geri_cagir(int(mesaj.wParam))
                except Exception:
                    pass
            user32.TranslateMessage(ctypes.byref(mesaj))
            user32.DispatchMessageW(ctypes.byref(mesaj))

        for kimlik in self.baglantilar:
            user32.UnregisterHotKey(None, kimlik)

    def durdur(self):
        if self._is_parcacigi_kimligi:
            ctypes.windll.user32.PostThreadMessageW(self._is_parcacigi_kimligi, WM_QUIT, 0, 0)
