# -*- coding: utf-8 -*-
"""
motor.py - Adim listesini calistiran oynatma motoru.

Ayri bir is parcaciginda calisir; arayuz donmaz.
Durdurma, duraklatma ve ESC ile acil durdurma desteklenir.

Her adim hedefini iki yoldan biriyle belirtir:
  hedef = "konum"   -> sabit ekran koordinati (x, y)
  hedef = "goruntu" -> ekranda aranan sablon goruntusu; bulunan bolgenin
                       merkezine (istege bagli kaydirma ile) islem uygulanir.
"""

import os
import random
import sys
import threading
import time

import diller
import ekran
import winput
from diller import M


def uygulama_klasoru():
    """Ayarlarin ve sablonlarin saklanacagi klasor.

    .exe olarak paketlendiginde __file__ gecici bir cikarma klasorunu gosterir
    ve program kapaninca silinir; bu yuzden exe'nin kendi klasoru kullanilir.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


KLASOR = uygulama_klasoru()
GORUNTU_KLASORU = os.path.join(KLASOR, "goruntuler")

# ---------------------------------------------------------------- Islem tanimlari
# konum        : bir hedefe (koordinat veya goruntu) ihtiyac duyar mi
# deger        : deger alaninin etiketi (None ise alan kapali)
# goruntu_sart : yalnizca goruntu hedefiyle kullanilabilir mi
ISLEMLER = {
    "sol_tik":       {"konum": True,  "deger": None},
    "sag_tik":       {"konum": True,  "deger": None},
    "cift_tik":      {"konum": True,  "deger": None},
    "orta_tik":      {"konum": True,  "deger": None},
    "tasi":          {"konum": True,  "deger": None},
    "basili_tut":    {"konum": True,  "deger": None},
    "birak":         {"konum": True,  "deger": None},
    "tekerlek":      {"konum": True,  "deger": "deger.tekerlek"},
    "goruntu_bekle": {"konum": True,  "deger": None, "goruntu_sart": True},
    "tus":           {"konum": False, "deger": "deger.tus"},
    "metin":         {"konum": False, "deger": "deger.metin"},
    "bekle":         {"konum": False, "deger": None},
}

ISLEM_SIRASI = list(ISLEMLER.keys())


def islem_adi(tip):
    """Islemin secili dildeki gorunen adi."""
    return M("islem.%s" % tip)


def islem_adlari():
    return [islem_adi(tip) for tip in ISLEM_SIRASI]


def tip_bul(ad, varsayilan="sol_tik"):
    """Gorunen addan islem turunu bulur."""
    for tip in ISLEM_SIRASI:
        if islem_adi(tip) == ad:
            return tip
    return varsayilan


def deger_etiketi(tip):
    """Deger alaninin etiketi; islem deger kullanmiyorsa None."""
    anahtar = ISLEMLER[tip]["deger"]
    return M(anahtar) if anahtar else None

BULUNAMAZSA_KODLARI = ["durdur", "atla"]


def bulunamazsa_etiketi(kod):
    return M("bulunamazsa.%s" % kod)


def bulunamazsa_secenekleri():
    return [bulunamazsa_etiketi(k) for k in BULUNAMAZSA_KODLARI]


def bulunamazsa_kodu(etiket, varsayilan="durdur"):
    for kod in BULUNAMAZSA_KODLARI:
        if bulunamazsa_etiketi(kod) == etiket:
            return kod
    return varsayilan


# Kosul: her adim, istege bagli olarak kendi "kosul goruntusune" baglanabilir.
# O goruntu ekranda varsa (ya da yoksa) adim calisir, aksi halde atlanir.
# Kosul goruntusu yalnizca ARANIR; uzerine tiklanmaz.
KOSULSUZ = ""
KOSUL_TURLERI = [KOSULSUZ, "var", "yok"]


def kosul_turu_etiketi(tur):
    return M({"var": "kosul.tur_var", "yok": "kosul.tur_yok"}.get(tur, "kosul.tur_"))


def kosul_turu_secenekleri():
    return [kosul_turu_etiketi(t) for t in KOSUL_TURLERI]


def kosul_turu_kodu(etiket, varsayilan=KOSULSUZ):
    for tur in KOSUL_TURLERI:
        if kosul_turu_etiketi(tur) == etiket:
            return tur
    return varsayilan


def goruntu_yolu(ad):
    """Sablon dosya adini tam yola cevirir."""
    return os.path.join(GORUNTU_KLASORU, str(ad))


def goruntu_klasorunu_hazirla():
    os.makedirs(GORUNTU_KLASORU, exist_ok=True)
    return GORUNTU_KLASORU


def bos_adim(tip="sol_tik"):
    x, y = winput.imlec_konumu()
    return {
        "tip": tip,
        "hedef": "goruntu" if ISLEMLER.get(tip, {}).get("goruntu_sart") else "konum",
        "x": x,
        "y": y,
        "goruntu": "",
        # Kosul: bu adim yalnizca su goruntu ekranda varsa/yoksa calisir
        "kosul_turu": KOSULSUZ,         # "" | "var" | "yok"
        "kosul_goruntu": "",            # aranacak kosul goruntusu (tiklanmaz)
        "kosul_esik": 5,                # kosul icin eslesme toleransi, yuzde
        "kosul_zaman_asimi": 0,         # kosul icin en fazla arama suresi (ms)
        "esik": 5,             # eslesme toleransi, yuzde
        "zaman_asimi": 5000,   # hedef goruntu icin beklenecek en fazla sure (ms)
        "kaydir_x": 0,         # bulunan bolgenin merkezine gore kayma
        "kaydir_y": 0,
        "bulunamazsa": "durdur",
        "deger": "",
        "tekrar": 1,
        "bekleme": 500,
        "aktif": True,
        "not": "",
    }


def goruntu_hedefli(adim):
    return adim.get("hedef", "konum") == "goruntu"


def adimi_dogrula(adim):
    """Sorun varsa aciklama metni, yoksa None dondurur."""
    tip = adim.get("tip")
    if tip not in ISLEMLER:
        return M("hata.bilinmeyen_islem") % tip
    bilgi = ISLEMLER[tip]

    if adim.get("tekrar", 1) < 1:
        return M("hata.tekrar")
    if adim.get("bekleme", 0) < 0:
        return M("hata.bekleme")
    kosul_turu = adim.get("kosul_turu", KOSULSUZ)
    if kosul_turu not in KOSUL_TURLERI:
        return M("hata.kosul_turu") % kosul_turu
    if kosul_turu:
        kosul_ad = str(adim.get("kosul_goruntu", "")).strip()
        if not kosul_ad:
            return M("hata.kosul_goruntu_yok")
        if not os.path.isfile(goruntu_yolu(kosul_ad)):
            return M("hata.kosul_goruntu_dosya") % kosul_ad
        if not 0 <= adim.get("kosul_esik", 0) <= 100:
            return M("hata.tolerans")
        if adim.get("kosul_zaman_asimi", 0) < 0:
            return M("hata.arama_suresi")

    if bilgi["konum"]:
        if bilgi.get("goruntu_sart") and not goruntu_hedefli(adim):
            return M("hata.yalniz_goruntu") % islem_adi(tip)
        if goruntu_hedefli(adim):
            ad = str(adim.get("goruntu", "")).strip()
            if not ad:
                return M("hata.goruntu_yok")
            if not os.path.isfile(goruntu_yolu(ad)):
                return M("hata.goruntu_dosya") % ad
            if not 0 <= adim.get("esik", 0) <= 100:
                return M("hata.tolerans")
            if adim.get("zaman_asimi", 0) < 0:
                return M("hata.arama_suresi")
            if adim.get("bulunamazsa", "durdur") not in BULUNAMAZSA_KODLARI:
                return M("hata.bulunamazsa")

    if tip == "tus":
        try:
            winput.kombinasyon_coz(adim.get("deger", ""))
        except ValueError as hata:
            return str(hata)
    if tip == "tekerlek":
        try:
            int(str(adim.get("deger", "")).strip() or "0")
        except ValueError:
            return M("hata.tekerlek")
    if tip == "metin" and not str(adim.get("deger", "")):
        return M("hata.metin_bos")
    return None


def hedef_metni(adim):
    """Listede gosterilecek kisa hedef aciklamasi."""
    bilgi = ISLEMLER.get(adim["tip"], {"konum": False})
    if not bilgi["konum"]:
        return "-"
    if goruntu_hedefli(adim):
        metin = "🖼 %s" % (adim.get("goruntu") or "-")
        kaydirma = (adim.get("kaydir_x", 0), adim.get("kaydir_y", 0))
        if kaydirma != (0, 0):
            metin += "  %+d,%+d" % kaydirma
        return metin
    return "(%d, %d)" % (adim.get("x", 0), adim.get("y", 0))


def kosul_metni(adim):
    """Listede gosterilecek kosul sutunu metni."""
    tur = adim.get("kosul_turu", KOSULSUZ)
    if not tur:
        return ""
    ad = adim.get("kosul_goruntu") or "-"
    return M("kosul.liste_var" if tur == "var" else "kosul.liste_yok") % ad


def adim_ozeti(adim):
    bilgi = ISLEMLER.get(adim["tip"], {"konum": False})
    parcalar = [islem_adi(adim["tip"]) if adim["tip"] in ISLEMLER else adim["tip"]]
    if bilgi["konum"]:
        parcalar.append(hedef_metni(adim))
    if adim.get("deger"):
        deger = str(adim["deger"])
        parcalar.append(deger if len(deger) <= 22 else deger[:19] + "...")
    if adim.get("tekrar", 1) > 1:
        parcalar.append("x%d" % adim["tekrar"])
    return " ".join(parcalar)


# ---------------------------------------------------------------- Oynatici
class Oynatici(threading.Thread):
    def __init__(self, adimlar, tur_sayisi, tur_beklemesi, geri_bildirim,
                 konum_sapmasi=0, gecikme_sapmasi=0, acil_tus=True):
        super().__init__(daemon=True, name="Oynatici")
        self.adimlar = [a for a in adimlar if a.get("aktif", True)]
        self.tur_sayisi = int(tur_sayisi)          # 0 = sonsuz
        self.tur_beklemesi = int(tur_beklemesi)
        self.bildir = geri_bildirim                # (olay, veri) -> None
        self.konum_sapmasi = int(konum_sapmasi)
        self.gecikme_sapmasi = float(gecikme_sapmasi)
        self.acil_tus = acil_tus

        self.dur_olayi = threading.Event()
        self.duraklat_olayi = threading.Event()
        self._basili_dugmeler = set()

    # ------------------------------------------------------------ yardimcilar
    def _bekle(self, milisaniye):
        """Kesilebilir bekleme. Devam edilecekse True, durdurulduysa False."""
        bitis = time.perf_counter() + max(0.0, milisaniye) / 1000.0
        while True:
            if self.dur_olayi.is_set():
                return False
            if self.acil_tus and winput.tus_basili_mi(winput.VK_ESCAPE):
                self.bildir("kayit", M("motor.esc"))
                self.dur_olayi.set()
                return False
            if self.duraklat_olayi.is_set():
                time.sleep(0.05)
                bitis = max(bitis, time.perf_counter())
                continue
            kalan = bitis - time.perf_counter()
            if kalan <= 0:
                return True
            time.sleep(min(0.02, kalan))

    def _sapmali_konum(self, x, y):
        if self.konum_sapmasi <= 0:
            return x, y
        s = self.konum_sapmasi
        return x + random.randint(-s, s), y + random.randint(-s, s)

    def _sapmali_gecikme(self, milisaniye):
        if self.gecikme_sapmasi <= 0:
            return milisaniye
        oran = 1.0 + random.uniform(-self.gecikme_sapmasi, self.gecikme_sapmasi) / 100.0
        return max(0.0, milisaniye * oran)

    # ------------------------------------------------------------ hedef cozumleme
    def _goruntuyu_ara(self, ad, esik, zaman_asimi):
        """Sablonu ekranda arar. Bulunursa (sol, ust, genislik, yukseklik), yoksa None."""
        yol = goruntu_yolu(ad)
        tolerans = max(0, min(100, int(esik))) / 100.0
        bitis = time.perf_counter() + max(0, int(zaman_asimi)) / 1000.0
        while True:
            try:
                bulunan = ekran.sablonu_bul(yol, tolerans)
            except Exception as hata:
                self.bildir("kayit", M("motor.goruntu_hata") % (ad, hata))
                return None
            if bulunan:
                return bulunan
            if time.perf_counter() >= bitis:
                return None
            if not self._bekle(250):               # tekrar denemeden once nefes al
                return None

    def _hedef_konum(self, adim):
        """Adimin uygulanacagi ekran noktasi; goruntu bulunamazsa None."""
        if not goruntu_hedefli(adim):
            return adim["x"], adim["y"]
        bulunan = self._goruntuyu_ara(adim.get("goruntu", ""), adim.get("esik", 0),
                                      adim.get("zaman_asimi", 0))
        if not bulunan:
            return None
        sol, ust, genislik, yukseklik = bulunan
        return (sol + genislik // 2 + int(adim.get("kaydir_x", 0)),
                ust + yukseklik // 2 + int(adim.get("kaydir_y", 0)))

    # ------------------------------------------------------------ kosullar
    def kosul_saglaniyor(self, adim, sira=0):
        """Adimin kosul goruntusu ekranda mi? Kosulsuz adimlar hep calisir."""
        tur = adim.get("kosul_turu", KOSULSUZ)
        if not tur:
            return True
        ad = adim.get("kosul_goruntu", "")
        bulundu = self._goruntuyu_ara(ad, adim.get("kosul_esik", 0),
                                      adim.get("kosul_zaman_asimi", 0)) is not None
        saglandi = bulundu if tur == "var" else not bulundu
        anahtar = "motor.kosul_%s_%s" % (tur, "tamam" if saglandi else "atla")
        self.bildir("kayit", M(anahtar) % (sira, ad))
        return saglandi

    # ------------------------------------------------------------ tek adim
    def _adimi_uygula(self, adim):
        """Adimi uygular. Goruntu hedefi bulunamazsa False dondurur."""
        tip = adim["tip"]
        bilgi = ISLEMLER[tip]

        if bilgi["konum"]:
            konum = self._hedef_konum(adim)
            if konum is None:
                return False
            if tip != "goruntu_bekle":
                x, y = self._sapmali_konum(*konum)
                winput.fareyi_tasi(x, y)
                time.sleep(0.02)  # hedef pencerenin imleci algilamasi icin

        if tip == "sol_tik":
            winput.tikla("sol")
        elif tip == "sag_tik":
            winput.tikla("sag")
        elif tip == "orta_tik":
            winput.tikla("orta")
        elif tip == "cift_tik":
            winput.cift_tikla("sol")
        elif tip in ("tasi", "bekle", "goruntu_bekle"):
            pass
        elif tip == "basili_tut":
            winput.basili_tut("sol")
            self._basili_dugmeler.add("sol")
        elif tip == "birak":
            winput.dugmeyi_birak("sol")
            self._basili_dugmeler.discard("sol")
        elif tip == "tekerlek":
            winput.tekerlek(int(str(adim.get("deger", "")).strip() or "0"))
        elif tip == "tus":
            winput.tusa_bas(adim["deger"])
        elif tip == "metin":
            winput.metin_yaz(adim["deger"])
        return True

    def _temizle(self):
        """Yarim kalan basili fare tuslarini birak."""
        for dugme in list(self._basili_dugmeler):
            try:
                winput.dugmeyi_birak(dugme)
            except Exception:
                pass
        self._basili_dugmeler.clear()

    # ------------------------------------------------------------ ana dongu
    def run(self):
        sebep = "tamam"
        toplam_adim = len(self.adimlar)
        try:
            tur = 0
            while not self.dur_olayi.is_set():
                tur += 1
                if self.tur_sayisi and tur > self.tur_sayisi:
                    break

                self.bildir("tur", (tur, self.tur_sayisi))
                for sira, adim in enumerate(self.adimlar, start=1):
                    if self.dur_olayi.is_set():
                        break
                    if not self.kosul_saglaniyor(adim, sira):
                        continue
                    for _tekrar in range(max(1, int(adim.get("tekrar", 1)))):
                        if self.dur_olayi.is_set():
                            break
                        if not self._bekle(0):      # duraklatma/ESC kontrolu
                            break
                        self.bildir("adim", (tur, sira, toplam_adim, adim))
                        try:
                            uygulandi = self._adimi_uygula(adim)
                        except Exception as hata:
                            self.bildir("kayit", M("motor.hata") % (sira, hata))
                            self.dur_olayi.set()
                            sebep = "hata"
                            break

                        if not uygulandi:
                            davranis = adim.get("bulunamazsa", "durdur")
                            self.bildir("kayit", M("motor.bulunamadi")
                                        % (sira, adim.get("goruntu"),
                                           bulunamazsa_etiketi(davranis).lower()))
                            if davranis == "durdur":
                                self.dur_olayi.set()
                                sebep = "bulunamadi"
                            break      # bu adimin kalan tekrarlarini atla

                        if not self._bekle(self._sapmali_gecikme(adim.get("bekleme", 0))):
                            break

                if self.dur_olayi.is_set():
                    break
                if self.tur_sayisi and tur >= self.tur_sayisi:
                    break
                if self.tur_beklemesi and not self._bekle(self.tur_beklemesi):
                    break
        finally:
            self._temizle()
            if self.dur_olayi.is_set() and sebep not in ("hata", "bulunamadi"):
                sebep = "durduruldu"
            self.bildir("bitti", sebep)

    def durdur(self):
        self.dur_olayi.set()

    def duraklat_degistir(self):
        if self.duraklat_olayi.is_set():
            self.duraklat_olayi.clear()
            return False
        self.duraklat_olayi.set()
        return True
