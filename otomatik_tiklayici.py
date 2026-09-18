# -*- coding: utf-8 -*-
"""
Otomatik Tıklayıcı ve Klavye Otomasyonu
========================================
Ekranın belirli noktalarına, belirlenen sırayla ve sürelerle sol/sağ/çift tık
yapan; tuş kombinasyonu gönderen ve metin yazan masaüstü uygulaması.

Çalıştırmak için:  python otomatik_tiklayici.py
Harici kütüphane gerekmez (yalnızca Python standart kütüphanesi).
"""

import ctypes
import json
import os
import queue
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import diller
import ekran
import kisayol
import motor
import winput
from diller import M

SURUM = "1.0"
KLASOR = motor.uygulama_klasoru()      # .exe'de exe'nin klasoru, betikte betigin klasoru
AYAR_DOSYASI = os.path.join(KLASOR, "ayarlar.json")

# Kısayol kimlikleri
KS_BASLAT = 1
KS_DURDUR = 2
KS_YAKALA = 3
KS_DURAKLAT = 4
KS_DURDUR_CTRL_T = 5

KISAYOLLAR = {
    KS_BASLAT:         (0, winput.VK["f6"], "F6 (Başlat)"),
    KS_DURDUR:         (0, winput.VK["f8"], "F8 (Durdur)"),
    KS_YAKALA:         (0, winput.VK["f7"], "F7 (Konum Yakala)"),
    KS_DURAKLAT:       (0, winput.VK["f9"], "F9 (Duraklat)"),
    KS_DURDUR_CTRL_T:  (kisayol.MOD_CONTROL, winput.VK["t"], "Ctrl+T (Durdur)"),
}


def dili_yukle():
    """Kayitli dil tercihini arayuz kurulmadan ONCE uygular."""
    try:
        with open(AYAR_DOSYASI, "r", encoding="utf-8") as dosya:
            kod = json.load(dosya).get("dil")
    except Exception:
        kod = None
    return diller.ayarla(kod or diller.VARSAYILAN)


class BolgeSecici(tk.Toplevel):
    """
    Tum ekrani kaplayan yari saydam katman. Iki asamada calisir:
      1. Aranacak bolgeyi fareyle cizdirir.
      2. O bolge bulundugunda TIKLANACAK NOKTAYI sectirir.

    bolge verilirse 1. asama atlanir ve yalnizca nokta secilir.
    Sonuclar: .sonuc = (sol, ust, genislik, yukseklik), .nokta = (x, y)
    """

    # Katman ekranda ve girdi almaya hazir. Otomatik kayit/testler sabit bir
    # bekleme yerine bunu bekler; yoksa katman acilmadan tiklayabilirler.
    acildi = threading.Event()

    def __init__(self, ana, bolge=None, nokta_iste=True):
        super().__init__(ana)
        self.sonuc = bolge
        self.nokta = None
        self.nokta_iste = nokta_iste      # False: yalnizca alan secilir (kosul)
        self._baslangic = None
        self._kare = None
        self._nisan = []
        self.asama = 2 if bolge else 1

        vsol, vust, vgen, vyuk = ekran.sanal_ekran()

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.30)
        self.configure(bg="black", cursor="crosshair")
        # Tk'nin geometry ayristiricisi negatif konumu "sag kenardan su kadar"
        # diye yorumluyor; birincil ekranin SOLUNDA monitor varsa katman kayiyor.
        # Bu yuzden pencere Win32 ile yerlestirilir ve kayma, pencerenin GERCEK
        # konumundan okunur - yerlestirme tutmasa bile koordinatlar tutarli kalir.
        self.geometry("%dx%d+0+0" % (vgen, vyuk))
        self.update_idletasks()
        self._katmani_yerlestir(vsol, vust, vgen, vyuk)
        self._kayma = (self.winfo_rootx(), self.winfo_rooty())

        self.tuval = tk.Canvas(self, bg="black", highlightthickness=0)
        self.tuval.pack(fill="both", expand=True)

        # Yonergeyi birincil ekranin ustune yerlestir (cok monitorde kaybolmasin)
        yonerge_x = self.winfo_screenwidth() // 2 - self._kayma[0]
        yonerge_y = max(40, 60 - self._kayma[1])
        self._yonerge = self.tuval.create_text(
            yonerge_x, yonerge_y, fill="white", font=("Segoe UI", 19, "bold"), text="")
        self._alt_yonerge = self.tuval.create_text(
            yonerge_x, yonerge_y + 34, fill="#c8c8c8", font=("Segoe UI", 12), text="")
        self._olcu = self.tuval.create_text(0, 0, fill="#ffe066", anchor="nw",
                                            font=("Consolas", 12, "bold"), text="")

        self.tuval.bind("<Button-1>", self._tiklandi)
        self.tuval.bind("<B1-Motion>", self._surukle)
        self.tuval.bind("<ButtonRelease-1>", self._birakildi)
        self.tuval.bind("<Motion>", self._hareket)
        self.bind("<Escape>", lambda e: self._iptal())
        self.bind("<Return>", lambda e: self._merkezi_kabul_et())

        if self.asama == 2:
            self._asamayi_kur_nokta()
        elif nokta_iste:
            self._yonergeyi_yaz(M("secici.asama1"), M("secici.asama1_alt"))
        else:
            self._yonergeyi_yaz(M("secici.kosul"), M("secici.kosul_alt"))

        self.focus_force()
        self.grab_set()
        self.update_idletasks()
        BolgeSecici.acildi.set()

    # ------------------------------------------------------------ yardimcilar
    def _katmani_yerlestir(self, sol, ust, genislik, yukseklik):
        """Katmani sanal masaustunun tamamina, Win32 ile yerlestirir."""
        SWP_NOZORDER, SWP_NOACTIVATE = 0x0004, 0x0010
        try:
            ctypes.windll.user32.SetWindowPos(
                self.winfo_id(), 0, int(sol), int(ust), int(genislik), int(yukseklik),
                SWP_NOZORDER | SWP_NOACTIVATE)
        except Exception:
            pass                      # yerlestirme tutmazsa kayma yine dogru okunur
        self.update_idletasks()

    def _yonergeyi_yaz(self, ust, alt=""):
        self.tuval.itemconfigure(self._yonerge, text=ust)
        self.tuval.itemconfigure(self._alt_yonerge, text=alt)

    def _tuval_bolgesi(self):
        kx, ky = self._kayma
        sol, ust, genislik, yukseklik = self.sonuc
        return sol - kx, ust - ky, genislik, yukseklik

    def _asamayi_kur_nokta(self):
        """2. asama: bolge sabitlendi, simdi tiklama noktasi seciliyor."""
        self.asama = 2
        sol, ust, genislik, yukseklik = self._tuval_bolgesi()
        if self._kare:
            self.tuval.delete(self._kare)
        self._kare = self.tuval.create_rectangle(
            sol, ust, sol + genislik, ust + yukseklik, outline="#34c759", width=3,
            dash=(6, 4))
        self.tuval.coords(self._olcu, sol, ust + yukseklik + 8)
        self.tuval.itemconfigure(
            self._olcu, text=M("secici.bolge") % (genislik, yukseklik))
        self._nisani_ciz(sol + genislik // 2, ust + yukseklik // 2)
        self._yonergeyi_yaz(M("secici.asama2"), M("secici.asama2_alt"))

    def _nisani_ciz(self, x, y):
        for oge in self._nisan:
            self.tuval.delete(oge)
        self._nisan = [
            self.tuval.create_line(x - 34, y, x - 8, y, fill="#ff3b30", width=3),
            self.tuval.create_line(x + 8, y, x + 34, y, fill="#ff3b30", width=3),
            self.tuval.create_line(x, y - 34, x, y - 8, fill="#ff3b30", width=3),
            self.tuval.create_line(x, y + 8, x, y + 34, fill="#ff3b30", width=3),
            self.tuval.create_oval(x - 11, y - 11, x + 11, y + 11, outline="#ff3b30", width=3),
        ]

    # ------------------------------------------------------------ olaylar
    def _tiklandi(self, olay):
        if self.asama == 1:
            self._baslangic = (olay.x, olay.y)
            if self._kare:
                self.tuval.delete(self._kare)
            self._kare = self.tuval.create_rectangle(olay.x, olay.y, olay.x, olay.y,
                                                     outline="#ff3b30", width=3)
        else:
            kx, ky = self._kayma
            self.nokta = (olay.x + kx, olay.y + ky)
            self._kapat()

    def _surukle(self, olay):
        if self.asama != 1 or not self._baslangic:
            return
        x0, y0 = self._baslangic
        self.tuval.coords(self._kare, x0, y0, olay.x, olay.y)
        self.tuval.coords(self._olcu, min(x0, olay.x), max(y0, olay.y) + 8)
        self.tuval.itemconfigure(self._olcu, text=M("secici.olcu")
                                 % (abs(olay.x - x0), abs(olay.y - y0)))

    def _birakildi(self, olay):
        if self.asama != 1 or not self._baslangic:
            return
        x0, y0 = self._baslangic
        sol, sag = sorted((x0, olay.x))
        ust, alt = sorted((y0, olay.y))
        self._baslangic = None
        if sag - sol < 4 or alt - ust < 4:
            return                      # kazara tiklama: 1. asamada kal
        kx, ky = self._kayma
        self.sonuc = (sol + kx, ust + ky, sag - sol, alt - ust)
        if not self.nokta_iste:
            self._kapat()            # kosul alani: tiklama noktasi sorulmaz
            return
        self._asamayi_kur_nokta()

    def _hareket(self, olay):
        if self.asama == 2:
            self._nisani_ciz(olay.x, olay.y)

    def _merkezi_kabul_et(self):
        if self.asama != 2 or not self.sonuc:
            return
        sol, ust, genislik, yukseklik = self.sonuc
        self.nokta = (sol + genislik // 2, ust + yukseklik // 2)
        self._kapat()

    def _iptal(self):
        self.sonuc = None
        self.nokta = None
        self._kapat()

    def _kapat(self):
        BolgeSecici.acildi.clear()
        self.grab_release()
        self.withdraw()
        self.update_idletasks()
        self.destroy()


class Uygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        dili_yukle()          # metinler kurulmadan once dil secilmeli
        self.title("%s v%s" % (M("uygulama.ad"), SURUM))
        self._pencereyi_boyutlandir(1180, 940)
        self.minsize(980, 640)

        self.adimlar = []
        self.oynatici = None
        self.olay_kuyrugu = queue.Queue()
        self.geri_sayim_isi = None
        self.acik_dosya = None
        self.kirli = False
        self._tur_metni = ""

        self._degiskenler()
        self._arayuzu_kur()
        self._kisayollari_baslat()

        self.ayarlari_yukle()
        self.protocol("WM_DELETE_WINDOW", self.kapat)

        self._is_kuyruk = self.after(60, self._kuyrugu_isle)
        self._is_imlec = self.after(100, self._imleci_izle)
        self.kaydet_gunluk(M("kayit.hazir"))
        self.kaydet_gunluk(M("kayit.acil"))

    def _pencereyi_boyutlandir(self, istenen_genislik, istenen_yukseklik):
        """Ekranla orantili bir boyut secer ve pencereyi ortalar.

        Buyuk ekranlarda liste alani genisler, kucuk ekranlarda pencere tasmaz.
        """
        ekran_g, ekran_y = self.winfo_screenwidth(), self.winfo_screenheight()
        genislik = min(max(istenen_genislik, int(ekran_g * 0.64)), ekran_g - 60)
        yukseklik = min(max(istenen_yukseklik, int(ekran_y * 0.82)), ekran_y - 90)
        sol = max(0, (ekran_g - genislik) // 2)
        ust = max(0, (ekran_y - yukseklik) // 2 - 20)
        self.geometry("%dx%d+%d+%d" % (genislik, yukseklik, sol, ust))

    # ------------------------------------------------------------------ durum
    def _degiskenler(self):
        self.d_islem = tk.StringVar(value=motor.islem_adi("sol_tik"))
        self.d_kosul_turu = tk.StringVar(
            value=motor.kosul_turu_etiketi(motor.KOSULSUZ))
        self.d_kosul_goruntu = tk.StringVar()
        self.d_kosul_esik = tk.StringVar(value="5")
        self.d_kosul_zaman = tk.StringVar(value="0")
        self.d_kosul_onizleme = tk.StringVar(value=M("kosul.onizleme_yok"))
        self._kosul_onizleme_resmi = None
        self.d_hedef = tk.StringVar(value="konum")
        self.d_goruntu = tk.StringVar()
        self.d_esik = tk.StringVar(value="5")
        self.d_zaman_asimi = tk.StringVar(value="5000")
        self.d_kaydir_x = tk.StringVar(value="0")
        self.d_kaydir_y = tk.StringVar(value="0")
        self.d_bulunamazsa = tk.StringVar(value=motor.bulunamazsa_etiketi("durdur"))
        self.d_onizleme = tk.StringVar(value=M("onizleme.yok"))
        self._onizleme_resmi = None
        self.d_x = tk.StringVar(value="0")
        self.d_y = tk.StringVar(value="0")
        self.d_deger = tk.StringVar()
        self.d_tekrar = tk.StringVar(value="1")
        self.d_bekleme = tk.StringVar(value="500")
        self.d_not = tk.StringVar()
        self.d_deger_etiketi = tk.StringVar(value="Değer")

        self.d_tur = tk.StringVar(value="1")
        self.d_tur_beklemesi = tk.StringVar(value="1000")
        self.d_hazirlik = tk.StringVar(value="3")
        self.d_konum_sapmasi = tk.StringVar(value="0")
        self.d_gecikme_sapmasi = tk.StringVar(value="0")

        self.d_yakala_ekle = tk.BooleanVar(value=False)
        self.d_kucult = tk.BooleanVar(value=True)
        self.d_esc = tk.BooleanVar(value=True)

        self.d_dil = tk.StringVar(value=diller.mevcut())
        self.d_durum = tk.StringVar(value=M("durum.beklemede"))
        self.d_imlec = tk.StringVar(value=M("durum.imlec_bos"))
        self.d_ilerleme = tk.StringVar(value="")

    # ------------------------------------------------------------------ arayüz
    def _olculeri_hesapla(self):
        """Tum piksel olculerini ekranin yazi buyuklugune gore belirler.

        Sabit piksel degerleri yuksek DPI'li ekranlarda sutunlari sikistiriyordu;
        burada her sey gercek yazi tipi olculerinden turetilir.
        """
        self.yazi = tkfont.nametofont("TkDefaultFont")
        self.yazi_yuksekligi = self.yazi.metrics("linespace")
        self.olcek = max(1.0, self.yazi_yuksekligi / 16.0)
        self.ONIZLEME_GENISLIK = int(190 * self.olcek)
        self.ONIZLEME_YUKSEKLIK = int(120 * self.olcek)

    def _genislik(self, *metinler, bosluk=26):
        """Verilen metinlerin sigacagi sutun genisligi."""
        return max(self.yazi.measure(m) for m in metinler) + int(bosluk * self.olcek)

    def _arayuzu_kur(self):
        self._olculeri_hesapla()

        stil = ttk.Style(self)
        if "vista" in stil.theme_names():
            stil.theme_use("vista")
        stil.configure("Baslik.TLabel", font=("Segoe UI", 10, "bold"))
        stil.configure("Calisiyor.TLabel", foreground="#0a7d28", font=("Segoe UI", 10, "bold"))
        stil.configure("Durdu.TLabel", foreground="#666666", font=("Segoe UI", 10, "bold"))
        # Satirlar arasina nefes payi birak
        stil.configure("Treeview", rowheight=self.yazi_yuksekligi + int(12 * self.olcek))
        stil.configure("Treeview.Heading", padding=(int(4 * self.olcek), int(5 * self.olcek)))

        self._menu_kur()

        ana = ttk.Frame(self, padding=8)
        ana.pack(fill="both", expand=True)
        ana.rowconfigure(0, weight=1)
        ana.columnconfigure(1, weight=1)

        self._form_kur(ana)
        self._liste_kur(ana)
        self._calistirma_kur(ana)
        self._gunluk_kur(ana)
        self._durum_cubugu_kur()

    def _menu_kur(self):
        menu = tk.Menu(self)
        dosya = tk.Menu(menu, tearoff=0)
        dosya.add_command(label=M("menu.yeni"), accelerator="Ctrl+N",
                          command=self.yeni_liste)
        dosya.add_command(label=M("menu.ac"), accelerator="Ctrl+O",
                          command=self.listeyi_ac)
        dosya.add_command(label=M("menu.kaydet"), accelerator="Ctrl+S",
                          command=self.listeyi_kaydet)
        dosya.add_command(label=M("menu.farkli_kaydet"),
                          command=lambda: self.listeyi_kaydet(True))
        dosya.add_separator()
        dosya.add_command(label=M("menu.cikis"), command=self.kapat)
        menu.add_cascade(label=M("menu.dosya"), menu=dosya)

        dil = tk.Menu(menu, tearoff=0)
        for kod, ad in diller.DILLER:
            dil.add_radiobutton(label=ad, value=kod, variable=self.d_dil,
                                command=lambda k=kod: self.dili_degistir(k))
        menu.add_cascade(label=M("menu.dil"), menu=dil)

        yardim = tk.Menu(menu, tearoff=0)
        yardim.add_command(label=M("menu.kullanim"), command=self.yardim_goster)
        yardim.add_command(label=M("menu.hakkinda"), command=self.hakkinda_goster)
        menu.add_cascade(label=M("menu.yardim"), menu=yardim)
        self.config(menu=menu)

        self.bind_all("<Control-n>", lambda e: self.yeni_liste())
        self.bind_all("<Control-o>", lambda e: self.listeyi_ac())
        self.bind_all("<Control-s>", lambda e: self.listeyi_kaydet())

    # ---------------------------------------------------------- sol: adım formu
    def _form_kur(self, ebeveyn):
        kutu = ttk.LabelFrame(ebeveyn, text=M("form.baslik"), padding=10)
        kutu.grid(row=0, column=0, sticky="nsw", padx=(0, 8))
        kutu.columnconfigure(1, weight=1)
        satir = 0

        ttk.Label(kutu, text=M("form.islem")).grid(row=satir, column=0, sticky="w", pady=3)
        self.islem_kutusu = ttk.Combobox(
            kutu, textvariable=self.d_islem, state="readonly", width=21,
            values=motor.islem_adlari(),
        )
        self.islem_kutusu.grid(row=satir, column=1, columnspan=2, sticky="ew", pady=3)
        self.islem_kutusu.bind("<<ComboboxSelected>>", lambda e: self._alanlari_guncelle())
        satir += 1

        ttk.Separator(kutu, orient="horizontal").grid(
            row=satir, column=0, columnspan=3, sticky="ew", pady=8)
        satir += 1

        self.hedef_etiketi = ttk.Label(kutu, text=M("form.hedef"), style="Baslik.TLabel")
        self.hedef_etiketi.grid(row=satir, column=0, sticky="w", pady=(0, 2))
        hedef_cerceve = ttk.Frame(kutu)
        hedef_cerceve.grid(row=satir, column=1, columnspan=2, sticky="w", pady=(0, 2))
        self.hedef_konum_dugmesi = ttk.Radiobutton(
            hedef_cerceve, text=M("form.koordinat"), value="konum", variable=self.d_hedef,
            command=self._alanlari_guncelle)
        self.hedef_konum_dugmesi.pack(side="left")
        self.hedef_goruntu_dugmesi = ttk.Radiobutton(
            hedef_cerceve, text=M("form.goruntu"), value="goruntu", variable=self.d_hedef,
            command=self._alanlari_guncelle)
        self.hedef_goruntu_dugmesi.pack(side="left", padx=(12, 0))
        satir += 1

        # --- koordinat hedefi ---------------------------------------------
        self.konum_cercevesi = ttk.Frame(kutu)
        self.konum_cercevesi.grid(row=satir, column=0, columnspan=3, sticky="ew")
        self.konum_cercevesi.columnconfigure(1, weight=1)
        satir += 1

        self.konum_etiketi = ttk.Label(self.konum_cercevesi, text=M("form.konum"))
        self.konum_etiketi.grid(row=0, column=0, sticky="w", pady=3)
        konum_girdileri = ttk.Frame(self.konum_cercevesi)
        konum_girdileri.grid(row=0, column=1, sticky="ew", pady=3)
        self.x_girdi = ttk.Entry(konum_girdileri, textvariable=self.d_x, width=8)
        self.x_girdi.pack(side="left")
        ttk.Label(konum_girdileri, text=" , ").pack(side="left")
        self.y_girdi = ttk.Entry(konum_girdileri, textvariable=self.d_y, width=8)
        self.y_girdi.pack(side="left")

        self.yakala_dugmesi = ttk.Button(
            self.konum_cercevesi, text=M("form.konum_yakala"), command=self.konumu_yakala)
        self.yakala_dugmesi.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 2))

        self.geri_sayim_dugmesi = ttk.Button(
            self.konum_cercevesi, text=M("form.geri_sayim"),
            command=self.geri_sayimla_yakala)
        self.geri_sayim_dugmesi.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)

        ttk.Checkbutton(self.konum_cercevesi, text=M("form.f7_ekle"),
                        variable=self.d_yakala_ekle).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(2, 6))

        # --- goruntu hedefi -----------------------------------------------
        self.goruntu_cercevesi = ttk.Frame(kutu)
        self.goruntu_cercevesi.grid(row=satir, column=0, columnspan=3, sticky="ew")
        self.goruntu_cercevesi.columnconfigure(1, weight=1)
        satir += 1
        self._goruntu_alanlarini_kur(self.goruntu_cercevesi)

        ttk.Separator(kutu, orient="horizontal").grid(
            row=satir, column=0, columnspan=3, sticky="ew", pady=8)
        satir += 1

        self.deger_etiketi = ttk.Label(kutu, textvariable=self.d_deger_etiketi)
        self.deger_etiketi.grid(row=satir, column=0, sticky="w", pady=3)
        self.deger_girdi = ttk.Entry(kutu, textvariable=self.d_deger, width=22)
        self.deger_girdi.grid(row=satir, column=1, columnspan=2, sticky="ew", pady=3)
        satir += 1

        ttk.Separator(kutu, orient="horizontal").grid(
            row=satir, column=0, columnspan=3, sticky="ew", pady=8)
        satir += 1

        # --- kosul (istege bagli) -----------------------------------------
        kosul_kutu = ttk.LabelFrame(kutu, text=M("form.kosul_baslik"), padding=6)
        kosul_kutu.grid(row=satir, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        kosul_kutu.columnconfigure(1, weight=1)
        satir += 1

        self.kosul_turu_kutusu = ttk.Combobox(
            kosul_kutu, textvariable=self.d_kosul_turu, state="readonly", width=30,
            values=motor.kosul_turu_secenekleri())
        self.kosul_turu_kutusu.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.kosul_turu_kutusu.bind("<<ComboboxSelected>>",
                                    lambda e: self._alanlari_guncelle())

        self.kosul_cercevesi = ttk.Frame(kosul_kutu)
        self.kosul_cercevesi.grid(row=1, column=0, columnspan=2, sticky="ew",
                                  pady=(6, 0))
        self.kosul_cercevesi.columnconfigure(1, weight=1)
        self._kosul_alanlarini_kur(self.kosul_cercevesi)

        ttk.Label(kutu, text=M("form.tekrar")).grid(row=satir, column=0, sticky="w", pady=3)
        ttk.Spinbox(kutu, from_=1, to=100000, textvariable=self.d_tekrar, width=10).grid(
            row=satir, column=1, sticky="w", pady=3)
        satir += 1

        ttk.Label(kutu, text=M("form.bekleme")).grid(row=satir, column=0,
                                                     sticky="w", pady=3)
        ttk.Spinbox(kutu, from_=0, to=3600000, increment=100,
                    textvariable=self.d_bekleme, width=10).grid(
            row=satir, column=1, sticky="w", pady=3)
        satir += 1

        ttk.Label(kutu, text=M("form.not")).grid(row=satir, column=0, sticky="w", pady=3)
        ttk.Entry(kutu, textvariable=self.d_not, width=22).grid(
            row=satir, column=1, columnspan=2, sticky="ew", pady=3)
        satir += 1

        dugmeler = ttk.Frame(kutu)
        dugmeler.grid(row=satir, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        dugmeler.columnconfigure((0, 1), weight=1)
        self.ekle_dugmesi = ttk.Button(dugmeler, text=M("form.ekle"), command=self.adim_ekle)
        self.ekle_dugmesi.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        self.guncelle_dugmesi = ttk.Button(
            dugmeler, text=M("form.guncelle"), command=self.adim_guncelle)
        self.guncelle_dugmesi.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        self._alanlari_guncelle()

    def _kosul_alanlarini_kur(self, ebeveyn):
        """Koşul görüntüsü alanları — yalnızca bir koşul seçilince görünür."""
        ttk.Button(ebeveyn, text=M("form.kosul_goruntu_sec"),
                   command=self.kosul_goruntusu_sec).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        onizleme_kutu = ttk.Frame(ebeveyn, relief="sunken", borderwidth=1, padding=3)
        onizleme_kutu.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        self.kosul_onizleme_tuvali = tk.Canvas(
            onizleme_kutu, width=self.ONIZLEME_GENISLIK,
            height=int(self.ONIZLEME_YUKSEKLIK * 0.62),
            highlightthickness=0, bg="#f5f5f5")
        self.kosul_onizleme_tuvali.pack()
        ttk.Label(onizleme_kutu, textvariable=self.d_kosul_onizleme, anchor="center",
                  foreground="#555555", font=("Segoe UI", 8)).pack(fill="x")

        ttk.Label(ebeveyn, text=M("form.kosul_tolerans")).grid(row=2, column=0,
                                                              sticky="w", pady=2)
        ttk.Spinbox(ebeveyn, from_=0, to=100, textvariable=self.d_kosul_esik,
                    width=8).grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(ebeveyn, text=M("form.kosul_zaman")).grid(row=3, column=0,
                                                           sticky="w", pady=2)
        ttk.Spinbox(ebeveyn, from_=0, to=600000, increment=500,
                    textvariable=self.d_kosul_zaman, width=8).grid(
            row=3, column=1, sticky="w", pady=2)

        ttk.Button(ebeveyn, text=M("form.kosul_dene"),
                   command=self.kosulu_dene).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(5, 0))

    def _goruntu_alanlarini_kur(self, ebeveyn):
        ttk.Button(ebeveyn, text=M("form.bolge_sec"),
                   command=self.bolge_sec).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(3, 2))
        self.nokta_dugmesi = ttk.Button(ebeveyn, text=M("form.nokta_sec"),
                                        command=self.nokta_sec)
        self.nokta_dugmesi.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        onizleme_kutu = ttk.Frame(ebeveyn, relief="sunken", borderwidth=1, padding=4)
        onizleme_kutu.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self.onizleme_tuvali = tk.Canvas(
            onizleme_kutu, width=self.ONIZLEME_GENISLIK, height=self.ONIZLEME_YUKSEKLIK,
            highlightthickness=0, bg="#f5f5f5")
        self.onizleme_tuvali.pack()
        ttk.Label(onizleme_kutu, textvariable=self.d_onizleme, anchor="center",
                  foreground="#555555", font=("Segoe UI", 8), justify="center").pack(fill="x")

        ttk.Label(ebeveyn, text=M("form.tolerans")).grid(row=3, column=0,
                                                         sticky="w", pady=2)
        ttk.Spinbox(ebeveyn, from_=0, to=100, textvariable=self.d_esik, width=8).grid(
            row=3, column=1, sticky="w", pady=2)

        ttk.Label(ebeveyn, text=M("form.zaman_asimi")).grid(row=4, column=0,
                                                            sticky="w", pady=2)
        ttk.Spinbox(ebeveyn, from_=0, to=600000, increment=500,
                    textvariable=self.d_zaman_asimi, width=8).grid(
            row=4, column=1, sticky="w", pady=2)

        ttk.Label(ebeveyn, text=M("form.kaydirma")).grid(row=5, column=0,
                                                         sticky="w", pady=2)
        kaydirma = ttk.Frame(ebeveyn)
        kaydirma.grid(row=5, column=1, sticky="w", pady=2)
        ttk.Entry(kaydirma, textvariable=self.d_kaydir_x, width=6).pack(side="left")
        ttk.Label(kaydirma, text=" , ").pack(side="left")
        ttk.Entry(kaydirma, textvariable=self.d_kaydir_y, width=6).pack(side="left")

        self.bulunamazsa_etiketi = ttk.Label(ebeveyn, text=M("form.bulunamazsa"))
        self.bulunamazsa_etiketi.grid(row=6, column=0, sticky="w", pady=2)
        self.bulunamazsa_kutusu = ttk.Combobox(
            ebeveyn, textvariable=self.d_bulunamazsa, state="readonly", width=15,
            values=motor.bulunamazsa_secenekleri())
        self.bulunamazsa_kutusu.grid(row=6, column=1, sticky="w", pady=2)

        ttk.Button(ebeveyn, text=M("form.simdi_ara"), command=self.goruntuyu_dene).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(6, 2))

        for degisken in (self.d_kaydir_x, self.d_kaydir_y):
            degisken.trace_add("write", lambda *a: self._onizleme_yenile())

    # ------------------------------------------------------------ sağ: liste
    def _liste_kur(self, ebeveyn):
        kutu = ttk.LabelFrame(ebeveyn, text=M("liste.baslik"), padding=8)
        kutu.grid(row=0, column=1, sticky="nsew")
        kutu.rowconfigure(0, weight=1)
        kutu.columnconfigure(0, weight=1)

        # Her sutun, basligi ve en uzun tipik degeri sigacak kadar genis olur.
        # (Sabit piksel degerleri yuksek DPI ekranlarda metni kirpiyordu.)
        sutunlar = (
            # anahtar,  baslik,              orneklem,                     esner
            ("sira",    M("liste.sira"),     "999",                        False),
            ("durum",   M("liste.durum"),    M("liste.durum"),             False),
            ("islem",   M("liste.islem"),    M("liste.ornek_islem"),       False),
            ("kosul",   M("liste.kosul"),    M("liste.ornek_kosul"),       False),
            ("hedef",   M("liste.hedef"),    "🖼 sablon_260101_120000.png", True),
            ("deger",   M("liste.deger"),    M("liste.ornek_deger"),       True),
            ("tekrar",  M("liste.tekrar"),   M("liste.tekrar"),            False),
            ("bekleme", M("liste.bekleme"),  M("liste.bekleme"),           False),
            ("not",     M("liste.not"),      M("liste.not"),               True),
        )
        self.agac = ttk.Treeview(kutu, columns=[s[0] for s in sutunlar],
                                 show="headings", selectmode="browse", height=18)
        self._sutun_taban, self._sutun_enaz = {}, {}
        self._esnek_sutunlar, self._sabit_sutunlar = [], []
        for anahtar, baslik, orneklem, esner in sutunlar:
            solda = anahtar in ("islem", "kosul", "hedef", "deger", "not")
            genislik = self._genislik(baslik, orneklem, bosluk=26 if solda else 16)
            en_az = self._genislik(baslik, bosluk=12)
            self._sutun_taban[anahtar] = genislik
            self._sutun_enaz[anahtar] = en_az
            (self._esnek_sutunlar if esner else self._sabit_sutunlar).append(anahtar)
            self.agac.heading(anahtar, text=baslik)
            self.agac.column(anahtar, width=genislik, minwidth=en_az,
                             anchor="w" if solda else "center", stretch=esner)
        self.agac.bind("<Configure>", self._sutunlari_sigdir)
        self.agac.grid(row=0, column=0, sticky="nsew")

        dikey = ttk.Scrollbar(kutu, orient="vertical", command=self.agac.yview)
        dikey.grid(row=0, column=1, sticky="ns")
        yatay = ttk.Scrollbar(kutu, orient="horizontal", command=self.agac.xview)
        yatay.grid(row=1, column=0, sticky="ew")
        self.agac.configure(yscrollcommand=dikey.set, xscrollcommand=yatay.set)

        self.agac.tag_configure("pasif", foreground="#999999")
        self.agac.tag_configure("tek", background="#f4f6f8")
        self.agac.tag_configure("calisan", background="#cdeccd")
        self.agac.bind("<<TreeviewSelect>>", lambda e: self.secimi_forma_al())
        self.agac.bind("<Double-1>", lambda e: self.aktifligi_degistir())
        self.agac.bind("<Delete>", lambda e: self.adim_sil())

        arac = ttk.Frame(kutu)
        arac.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        for anahtar, komut in (
            ("liste.yukari", lambda: self.adim_tasi(-1)),
            ("liste.asagi", lambda: self.adim_tasi(1)),
            ("liste.cogalt", self.adim_cogalt),
            ("liste.aktiflik", self.aktifligi_degistir),
            ("liste.sil", self.adim_sil),
            ("liste.temizle", self.listeyi_temizle),
        ):
            ttk.Button(arac, text=M(anahtar), command=komut).pack(side="left", padx=2)
        ttk.Button(arac, text=M("liste.dene"), command=self.secili_adimi_dene).pack(
            side="right", padx=2)

    def _sutunlari_sigdir(self, olay=None):
        """Esnek sütunları, listenin o anki genişliğine orantılı olarak dağıtır."""
        alan = (olay.width if olay else self.agac.winfo_width()) - 4
        if alan < 100 or not self._esnek_sutunlar:
            return
        sabit = sum(self._sutun_taban[a] for a in self._sabit_sutunlar)
        taban = sum(self._sutun_taban[a] for a in self._esnek_sutunlar)
        kalan = max(0, alan - sabit)

        genislikler = {a: max(self._sutun_enaz[a],
                              int(kalan * self._sutun_taban[a] / taban))
                       for a in self._esnek_sutunlar}
        # En az genislik sinirina takilan sutunlar butceyi asabilir:
        # fazlayi, en cok bollugu olan sutundan geri al.
        fazla = sum(genislikler.values()) - kalan
        while fazla > 0:
            aday = max(genislikler, key=lambda a: genislikler[a] - self._sutun_enaz[a])
            kisilabilir = min(fazla, genislikler[aday] - self._sutun_enaz[aday])
            if kisilabilir <= 0:
                break                      # hepsi en az genislikte, daha fazlasi olmaz
            genislikler[aday] -= kisilabilir
            fazla -= kisilabilir

        for anahtar, genislik in genislikler.items():
            self.agac.column(anahtar, width=genislik)

    # ------------------------------------------------------- alt: çalıştırma
    def _calistirma_kur(self, ebeveyn):
        kutu = ttk.LabelFrame(ebeveyn, text=M("cal.baslik"), padding=10)
        kutu.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        sol = ttk.Frame(kutu)
        sol.pack(side="left", fill="y")

        ttk.Label(sol, text=M("cal.tur")).grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Spinbox(sol, from_=0, to=1000000, textvariable=self.d_tur, width=9).grid(
            row=0, column=1, sticky="w")
        ttk.Label(sol, text=M("cal.sonsuz"), foreground="#777777").grid(
            row=0, column=2, sticky="w", padx=(6, 18))

        ttk.Label(sol, text=M("cal.tur_beklemesi")).grid(row=1, column=0,
                                                         sticky="w", pady=(6, 0))
        ttk.Spinbox(sol, from_=0, to=3600000, increment=100,
                    textvariable=self.d_tur_beklemesi, width=9).grid(
            row=1, column=1, sticky="w", pady=(6, 0))

        ttk.Label(sol, text=M("cal.hazirlik")).grid(row=0, column=3,
                                                    sticky="w", padx=(0, 6))
        ttk.Spinbox(sol, from_=0, to=60, textvariable=self.d_hazirlik, width=6).grid(
            row=0, column=4, sticky="w")

        ttk.Label(sol, text=M("cal.konum_sapmasi")).grid(row=1, column=3, sticky="w",
                                                         padx=(0, 6), pady=(6, 0))
        ttk.Spinbox(sol, from_=0, to=200, textvariable=self.d_konum_sapmasi, width=6).grid(
            row=1, column=4, sticky="w", pady=(6, 0))

        ttk.Label(sol, text=M("cal.gecikme_sapmasi")).grid(row=1, column=5, sticky="w",
                                                          padx=(18, 6), pady=(6, 0))
        ttk.Spinbox(sol, from_=0, to=90, textvariable=self.d_gecikme_sapmasi, width=6).grid(
            row=1, column=6, sticky="w", pady=(6, 0))

        ttk.Checkbutton(sol, text=M("cal.kucult"), variable=self.d_kucult).grid(
            row=0, column=5, columnspan=2, sticky="w", padx=(18, 0))

        sag = ttk.Frame(kutu)
        sag.pack(side="right", fill="y")

        self.baslat_dugmesi = ttk.Button(sag, text=M("cal.baslat"),
                                         command=self.baslat, width=18)
        self.baslat_dugmesi.grid(row=0, column=0, rowspan=2, padx=4, ipady=8)
        self.duraklat_dugmesi = ttk.Button(sag, text=M("cal.duraklat"),
                                           command=self.duraklat, state="disabled",
                                           width=16)
        self.duraklat_dugmesi.grid(row=0, column=1, padx=4, pady=(0, 2))
        self.durdur_dugmesi = ttk.Button(sag, text=M("cal.durdur"),
                                         command=self.durdur, state="disabled",
                                         width=20)
        self.durdur_dugmesi.grid(row=1, column=1, padx=4, pady=(2, 0))

        bilgi = ttk.Frame(kutu)
        bilgi.pack(side="right", fill="y", padx=(0, 20))
        self.durum_etiketi = ttk.Label(bilgi, textvariable=self.d_durum, style="Durdu.TLabel")
        self.durum_etiketi.pack(anchor="e")
        ttk.Label(bilgi, textvariable=self.d_ilerleme, foreground="#555555").pack(anchor="e")

    def _gunluk_kur(self, ebeveyn):
        kutu = ttk.LabelFrame(ebeveyn, text=M("cal.gunluk"), padding=6)
        kutu.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        ebeveyn.rowconfigure(2, weight=0)
        self.gunluk = ScrolledText(kutu, height=4, wrap="word", state="disabled",
                                   font=("Consolas", 9))
        self.gunluk.pack(fill="both", expand=True)

    def _durum_cubugu_kur(self):
        cubuk = ttk.Frame(self, relief="sunken", padding=(8, 3))
        cubuk.pack(fill="x", side="bottom")
        ttk.Label(cubuk, textvariable=self.d_imlec, font=("Consolas", 9)).pack(side="left")
        self.dosya_etiketi = ttk.Label(cubuk, text=M("durum.kaydedilmemis"),
                                       foreground="#666666")
        self.dosya_etiketi.pack(side="right")

    # ------------------------------------------------------------ yardımcılar
    def kaydet_gunluk(self, mesaj):
        damga = datetime.now().strftime("%H:%M:%S")
        self.gunluk.configure(state="normal")
        self.gunluk.insert("end", "[%s] %s\n" % (damga, mesaj))
        self.gunluk.see("end")
        self.gunluk.configure(state="disabled")

    def _sayi(self, degisken, varsayilan=0, en_az=None):
        try:
            deger = int(float(str(degisken.get()).strip().replace(",", ".")))
        except (ValueError, TypeError):
            deger = varsayilan
        if en_az is not None:
            deger = max(en_az, deger)
        return deger

    def _secili_indis(self):
        secim = self.agac.selection()
        if not secim:
            return None
        return self.agac.index(secim[0])

    def _alanlari_guncelle(self):
        tip = motor.tip_bul(self.d_islem.get())
        bilgi = motor.ISLEMLER[tip]

        # Koşul isteğe bağlı: seçilmediyse alanları hiç gösterme
        if motor.kosul_turu_kodu(self.d_kosul_turu.get()):
            self.kosul_cercevesi.grid()
            self._kosul_onizleme_yenile()
        else:
            self.kosul_cercevesi.grid_remove()

        # Yalnizca goruntuyle calisan islemler koordinat secenegini kapatir
        if bilgi.get("goruntu_sart"):
            self.d_hedef.set("goruntu")
            self.hedef_konum_dugmesi.configure(state="disabled")
        else:
            self.hedef_konum_dugmesi.configure(state="normal" if bilgi["konum"] else "disabled")
        self.hedef_goruntu_dugmesi.configure(state="normal" if bilgi["konum"] else "disabled")
        self.hedef_etiketi.configure(foreground="black" if bilgi["konum"] else "#aaaaaa")

        goruntu_modu = bilgi["konum"] and self.d_hedef.get() == "goruntu"
        if bilgi["konum"] and not goruntu_modu:
            self.konum_cercevesi.grid()
        else:
            self.konum_cercevesi.grid_remove()
        if goruntu_modu:
            self.goruntu_cercevesi.grid()
            self._onizleme_yenile()
        else:
            self.goruntu_cercevesi.grid_remove()

        etiket = motor.deger_etiketi(tip)
        if etiket:
            self.d_deger_etiketi.set(etiket)
            self.deger_girdi.configure(state="normal")
            self.deger_etiketi.configure(foreground="black")
        else:
            self.d_deger_etiketi.set(M("deger.yok"))
            self.deger_girdi.configure(state="disabled")
            self.deger_etiketi.configure(foreground="#aaaaaa")

    def _formdan_adim(self):
        tip = motor.tip_bul(self.d_islem.get())
        bilgi = motor.ISLEMLER[tip]
        hedef = self.d_hedef.get() if bilgi["konum"] else "konum"
        if bilgi.get("goruntu_sart"):
            hedef = "goruntu"
        davranis = motor.bulunamazsa_kodu(self.d_bulunamazsa.get())
        kosul_turu = motor.kosul_turu_kodu(self.d_kosul_turu.get())
        return {
            "tip": tip,
            "hedef": hedef,
            "x": self._sayi(self.d_x, 0),
            "y": self._sayi(self.d_y, 0),
            "goruntu": self.d_goruntu.get().strip(),
            "kosul_turu": kosul_turu,
            "kosul_goruntu": self.d_kosul_goruntu.get().strip(),
            "kosul_esik": self._sayi(self.d_kosul_esik, 5, en_az=0),
            "kosul_zaman_asimi": self._sayi(self.d_kosul_zaman, 0, en_az=0),
            "esik": self._sayi(self.d_esik, 5, en_az=0),
            "zaman_asimi": self._sayi(self.d_zaman_asimi, 0, en_az=0),
            "kaydir_x": self._sayi(self.d_kaydir_x, 0),
            "kaydir_y": self._sayi(self.d_kaydir_y, 0),
            "bulunamazsa": davranis,
            "deger": self.d_deger.get() if bilgi["deger"] else "",
            "tekrar": self._sayi(self.d_tekrar, 1, en_az=1),
            "bekleme": self._sayi(self.d_bekleme, 0, en_az=0),
            "aktif": True,
            "not": self.d_not.get(),
        }

    def _forma_adim(self, adim):
        self.d_islem.set(motor.islem_adi(adim["tip"]))
        self.d_kosul_turu.set(motor.kosul_turu_etiketi(
            adim.get("kosul_turu", motor.KOSULSUZ)))
        self.d_kosul_goruntu.set(adim.get("kosul_goruntu", ""))
        self.d_kosul_esik.set(str(adim.get("kosul_esik", 5)))
        self.d_kosul_zaman.set(str(adim.get("kosul_zaman_asimi", 0)))
        self.d_hedef.set(adim.get("hedef", "konum"))
        self.d_goruntu.set(adim.get("goruntu", ""))
        self.d_esik.set(str(adim.get("esik", 5)))
        self.d_zaman_asimi.set(str(adim.get("zaman_asimi", 0)))
        self.d_kaydir_x.set(str(adim.get("kaydir_x", 0)))
        self.d_kaydir_y.set(str(adim.get("kaydir_y", 0)))
        self.d_bulunamazsa.set(motor.bulunamazsa_etiketi(
            adim.get("bulunamazsa", "durdur")))
        self._alanlari_guncelle()
        self.d_x.set(str(adim["x"]))
        self.d_y.set(str(adim["y"]))
        self.d_deger.set(adim.get("deger", ""))
        self.d_tekrar.set(str(adim.get("tekrar", 1)))
        self.d_bekleme.set(str(adim.get("bekleme", 0)))
        self.d_not.set(adim.get("not", ""))

    def _degisti(self):
        self.kirli = True
        self._baslik_guncelle()

    def _baslik_guncelle(self):
        ad = (os.path.basename(self.acik_dosya) if self.acik_dosya
              else M("durum.kaydedilmemis"))
        self.dosya_etiketi.configure(text=("* " if self.kirli else "") + ad)
        self.title("%s%s v%s - %s" % ("* " if self.kirli else "",
                                      M("uygulama.ad"), SURUM, ad))

    def listeyi_yenile(self, secilecek=None):
        # Onceki secimin sirasi, satirlar silinmeden once okunmali
        onceki = self._secili_indis()
        self.agac.delete(*self.agac.get_children())
        for sira, adim in enumerate(self.adimlar, start=1):
            etiketler = () if adim.get("aktif", True) else ("pasif",)
            if sira % 2 == 0:                     # okunurluk icin satir seritleme
                etiketler += ("tek",)
            self.agac.insert(
                "", "end", iid=str(sira - 1),
                values=(
                    sira,
                    "✓" if adim.get("aktif", True) else "✗",
                    motor.islem_adi(adim["tip"]),
                    motor.kosul_metni(adim),
                    motor.hedef_metni(adim),
                    adim.get("deger", ""),
                    adim.get("tekrar", 1),
                    adim.get("bekleme", 0),
                    adim.get("not", ""),
                ),
                tags=etiketler,
            )
        hedef = secilecek if secilecek is not None else onceki
        if hedef is not None and 0 <= hedef < len(self.adimlar):
            self.agac.selection_set(str(hedef))
            self.agac.see(str(hedef))

    # ------------------------------------------------------------ liste işlemleri
    def adim_ekle(self):
        adim = self._formdan_adim()
        hata = motor.adimi_dogrula(adim)
        if hata:
            messagebox.showwarning(M("kutu.gecersiz_baslik"), hata, parent=self)
            return
        indis = self._secili_indis()
        konum = len(self.adimlar) if indis is None else indis + 1
        self.adimlar.insert(konum, adim)
        self.listeyi_yenile(konum)
        self._degisti()
        self.kaydet_gunluk(M("kayit.adim_eklendi")
                           % (konum + 1, motor.adim_ozeti(adim)))

    def adim_guncelle(self):
        indis = self._secili_indis()
        if indis is None:
            messagebox.showinfo(M("kutu.secim_yok_baslik"), M("kutu.secim_yok"),
                                parent=self)
            return
        adim = self._formdan_adim()
        hata = motor.adimi_dogrula(adim)
        if hata:
            messagebox.showwarning(M("kutu.gecersiz_baslik"), hata, parent=self)
            return
        adim["aktif"] = self.adimlar[indis].get("aktif", True)
        self.adimlar[indis] = adim
        self.listeyi_yenile(indis)
        self._degisti()
        self.kaydet_gunluk(M("kayit.adim_guncellendi")
                           % (indis + 1, motor.adim_ozeti(adim)))

    def secimi_forma_al(self):
        indis = self._secili_indis()
        if indis is not None:
            self._forma_adim(self.adimlar[indis])

    def adim_sil(self):
        indis = self._secili_indis()
        if indis is None:
            return
        silinen = self.adimlar.pop(indis)
        self.listeyi_yenile(min(indis, len(self.adimlar) - 1) if self.adimlar else None)
        self._degisti()
        self.kaydet_gunluk(M("kayit.adim_silindi") % motor.adim_ozeti(silinen))

    def adim_tasi(self, yon):
        indis = self._secili_indis()
        if indis is None:
            return
        yeni = indis + yon
        if not (0 <= yeni < len(self.adimlar)):
            return
        self.adimlar[indis], self.adimlar[yeni] = self.adimlar[yeni], self.adimlar[indis]
        self.listeyi_yenile(yeni)
        self._degisti()

    def adim_cogalt(self):
        indis = self._secili_indis()
        if indis is None:
            return
        self.adimlar.insert(indis + 1, dict(self.adimlar[indis]))
        self.listeyi_yenile(indis + 1)
        self._degisti()

    def aktifligi_degistir(self):
        indis = self._secili_indis()
        if indis is None:
            return
        self.adimlar[indis]["aktif"] = not self.adimlar[indis].get("aktif", True)
        self.listeyi_yenile(indis)
        self._degisti()

    def listeyi_temizle(self):
        if not self.adimlar:
            return
        if messagebox.askyesno(M("kutu.temizle_baslik"),
                               M("kutu.temizle") % len(self.adimlar), parent=self):
            self.adimlar = []
            self.listeyi_yenile()
            self._degisti()
            self.kaydet_gunluk(M("kayit.liste_temizlendi"))

    def secili_adimi_dene(self):
        """Seçili adımı tek seferlik çalıştırır (test amaçlı)."""
        indis = self._secili_indis()
        if indis is None:
            messagebox.showinfo(M("kutu.secim_yok_baslik"), M("kutu.secim_yok"),
                                parent=self)
            return
        if self.oynatici and self.oynatici.is_alive():
            return
        adim = dict(self.adimlar[indis])
        adim["aktif"] = True
        self.kaydet_gunluk(M("kayit.deneme") % motor.adim_ozeti(adim))
        self.after(2000, lambda: self._tek_adim_calistir(adim))

    def _tek_adim_calistir(self, adim):
        try:
            gecici = motor.Oynatici([adim], 1, 0, self._motordan, acil_tus=False)
            gecici.start()
        except Exception as hata:
            self.kaydet_gunluk(M("kayit.deneme_hata") % hata)

    # ------------------------------------------------------------ koşul görüntüsü
    def _alani_yakala(self, nokta_iste, mevcut_bolge=None):
        """Ekranı karartıp bir alan seçtirir ve o alanı PNG olarak kaydeder.

        Dönüş: (dosya_adi, bolge, nokta) — iptal edilirse (None, None, None).
        """
        gorunurdu = self.state() == "normal"
        self.withdraw()
        self.update()
        time.sleep(0.25)

        bolge = nokta = goruntu = hata = None
        try:
            secici = BolgeSecici(self, bolge=mevcut_bolge, nokta_iste=nokta_iste)
            self.wait_window(secici)
            bolge, nokta = secici.sonuc, secici.nokta
            if bolge and (nokta or not nokta_iste):
                # Yakalama ana pencere geri gelmeden yapilmali
                self.update()
                time.sleep(0.25)
                goruntu = ekran.yakala(*bolge)
        except Exception as istisna:
            hata = istisna
        finally:
            if gorunurdu:
                self.deiconify()
                self.lift()

        if hata is not None:
            messagebox.showerror(M("kutu.alinamadi"), str(hata), parent=self)
            return None, None, None
        if not (bolge and goruntu):
            return None, None, None

        bayt, g, y, _s, _u = goruntu
        try:
            motor.goruntu_klasorunu_hazirla()
            damga = datetime.now().strftime("%y%m%d_%H%M%S")
            ad, sayac = "sablon_%s.png" % damga, 2
            while os.path.isfile(motor.goruntu_yolu(ad)):
                ad = "sablon_%s_%d.png" % (damga, sayac)
                sayac += 1
            ekran.png_kaydet(motor.goruntu_yolu(ad), bayt, g, y)
        except Exception as istisna:
            messagebox.showerror(M("kutu.kaydedilemedi"), str(istisna), parent=self)
            return None, None, None
        return ad, bolge, nokta

    def kosul_goruntusu_sec(self):
        """Koşul alanını seçtirir — tıklama noktası sorulmaz, sadece aranır."""
        if self.oynatici and self.oynatici.is_alive():
            return
        ad, bolge, _nokta = self._alani_yakala(nokta_iste=False)
        if not ad:
            self.kaydet_gunluk(M("kayit.bolge_iptal"))
            return
        self.d_kosul_goruntu.set(ad)
        self._kosul_onizleme_yenile()
        self.kaydet_gunluk(M("kayit.kosul_alindi")
                           % (ad, bolge[2], bolge[3], bolge[0], bolge[1]))

    def _kosul_onizleme_yenile(self):
        ad = self.d_kosul_goruntu.get().strip()
        tuval = self.kosul_onizleme_tuvali
        tuval.delete("all")
        genislik = int(tuval["width"])
        yukseklik = int(tuval["height"])
        if not ad or not os.path.isfile(motor.goruntu_yolu(ad)):
            self._kosul_onizleme_resmi = None
            tuval.create_text(genislik // 2, yukseklik // 2, width=genislik - 16,
                              text=M("onizleme.dosya_yok") % ad if ad
                              else M("kosul.onizleme_yok"),
                              fill="#999999", font=("Segoe UI", 9))
            self.d_kosul_onizleme.set("")
            return
        try:
            resim = tk.PhotoImage(file=motor.goruntu_yolu(ad))
            asil_g, asil_y = resim.width(), resim.height()
            bolen = max(1, -(-asil_g // (genislik - 12)), -(-asil_y // (yukseklik - 12)))
            if bolen > 1:
                resim = resim.subsample(bolen, bolen)
        except Exception as hata:
            self._kosul_onizleme_resmi = None
            tuval.create_text(genislik // 2, yukseklik // 2, width=genislik - 16,
                              text=M("onizleme.hata") % hata, fill="#999999",
                              font=("Segoe UI", 9))
            self.d_kosul_onizleme.set("")
            return
        self._kosul_onizleme_resmi = resim
        x0 = (genislik - resim.width()) // 2
        y0 = (yukseklik - resim.height()) // 2
        tuval.create_image(x0, y0, anchor="nw", image=resim)
        tuval.create_rectangle(x0, y0, x0 + resim.width(), y0 + resim.height(),
                               outline="#2563eb", width=2)
        self.d_kosul_onizleme.set(M("kosul.onizleme") % (ad, asil_g, asil_y))

    def kosulu_dene(self):
        """Koşulun şu anda sağlanıp sağlanmadığını gösterir."""
        ad = self.d_kosul_goruntu.get().strip()
        if not ad:
            messagebox.showinfo(M("kutu.kosul_yok_baslik"), M("kutu.kosul_yok"),
                                parent=self)
            return
        tolerans = self._sayi(self.d_kosul_esik, 5, en_az=0) / 100.0
        try:
            baslangic = time.perf_counter()
            bulunan = ekran.sablonu_bul(motor.goruntu_yolu(ad), tolerans)
            sure = (time.perf_counter() - baslangic) * 1000
        except Exception as hata:
            messagebox.showerror(M("kutu.arama_hata"), str(hata), parent=self)
            return
        if bulunan:
            self.kaydet_gunluk(M("kayit.arama_var")
                               % (ad, bulunan[0], bulunan[1], bulunan[2], bulunan[3],
                                  bulunan[0] + bulunan[2] // 2,
                                  bulunan[1] + bulunan[3] // 2, sure))
            messagebox.showinfo(M("kutu.kosul_var_baslik"), M("kutu.kosul_var") % ad,
                                parent=self)
        else:
            self.kaydet_gunluk(M("kayit.arama_yok") % (ad, sure))
            messagebox.showwarning(M("kutu.kosul_yok_simdi_baslik"),
                                   M("kutu.kosul_yok_simdi") % ad, parent=self)

    # ------------------------------------------------------------ görüntü hedefi
    def bolge_sec(self):
        """Ekranı karartıp kullanıcıdan bir kare çizmesini ister ve o kareyi kaydeder."""
        if self.oynatici and self.oynatici.is_alive():
            return
        gorunurdu = self.state() == "normal"
        self.withdraw()
        self.update()
        time.sleep(0.25)          # pencerenin ekrandan silinmesini bekle

        bolge = nokta = goruntu = hata = None
        try:
            secici = BolgeSecici(self)
            self.wait_window(secici)
            bolge, nokta = secici.sonuc, secici.nokta
            if bolge and nokta:
                # Yakalama, ana pencere geri gelmeden yapilmali; yoksa
                # secilen alanin ustune oturup kendi arayuzumuzu kaydederiz.
                self.update()
                time.sleep(0.25)          # katmanin kalkmasini bekle
                goruntu = ekran.yakala(*bolge)
        except Exception as istisna:
            hata = istisna
        finally:
            if gorunurdu:
                self.deiconify()
                self.lift()

        if hata is not None:
            messagebox.showerror(M("kutu.alinamadi"), str(hata), parent=self)
            return
        if not (bolge and nokta):
            self.kaydet_gunluk(M("kayit.bolge_iptal"))
            return

        sol, ust, genislik, yukseklik = bolge
        bayt, g, y, _s, _u = goruntu
        try:
            motor.goruntu_klasorunu_hazirla()
            damga = datetime.now().strftime("%y%m%d_%H%M%S")
            ad, sayac = "sablon_%s.png" % damga, 2
            while os.path.isfile(motor.goruntu_yolu(ad)):
                ad = "sablon_%s_%d.png" % (damga, sayac)
                sayac += 1
            ekran.png_kaydet(motor.goruntu_yolu(ad), bayt, g, y)
        except Exception as istisna:
            messagebox.showerror(M("kutu.kaydedilemedi"), str(istisna), parent=self)
            return

        kaydir_x = nokta[0] - (sol + genislik // 2)
        kaydir_y = nokta[1] - (ust + yukseklik // 2)
        self.d_goruntu.set(ad)
        self.d_kaydir_x.set(str(kaydir_x))
        self.d_kaydir_y.set(str(kaydir_y))
        self.d_hedef.set("goruntu")
        self._alanlari_guncelle()
        self.kaydet_gunluk(M("kayit.goruntu_alindi")
                           % (ad, g, y, sol, ust, nokta[0], nokta[1],
                              kaydir_x, kaydir_y))

    def nokta_sec(self):
        """Şablonu ekranda bulup, tıklanacak noktayı yeniden seçtirir."""
        if self.oynatici and self.oynatici.is_alive():
            return
        ad = self.d_goruntu.get().strip()
        if not ad:
            messagebox.showinfo(M("kutu.goruntu_yok_baslik"), M("kutu.goruntu_yok"),
                                parent=self)
            return
        yol = motor.goruntu_yolu(ad)
        tolerans = self._sayi(self.d_esik, 5, en_az=0) / 100.0
        try:
            bulunan = ekran.sablonu_bul(yol, tolerans)
        except Exception as istisna:
            messagebox.showerror(M("kutu.arama_hata"), str(istisna), parent=self)
            return
        if not bulunan:
            messagebox.showwarning(M("kutu.bolge_yok_baslik"), M("kutu.bolge_yok"),
                                   parent=self)
            return

        gorunurdu = self.state() == "normal"
        self.withdraw()
        self.update()
        time.sleep(0.25)
        nokta = None
        try:
            secici = BolgeSecici(self, bolge=bulunan)
            self.wait_window(secici)
            nokta = secici.nokta
        finally:
            if gorunurdu:
                self.deiconify()
                self.lift()

        if not nokta:
            self.kaydet_gunluk(M("kayit.nokta_iptal"))
            return
        sol, ust, genislik, yukseklik = bulunan
        kaydir_x = nokta[0] - (sol + genislik // 2)
        kaydir_y = nokta[1] - (ust + yukseklik // 2)
        self.d_kaydir_x.set(str(kaydir_x))
        self.d_kaydir_y.set(str(kaydir_y))
        self._onizleme_yenile()
        self.kaydet_gunluk(M("kayit.nokta_guncel")
                           % (nokta[0], nokta[1], kaydir_x, kaydir_y))

    def _onizleme_temizle(self, mesaj):
        self.onizleme_tuvali.delete("all")
        self._onizleme_resmi = None
        self.onizleme_tuvali.create_text(
            self.ONIZLEME_GENISLIK // 2, self.ONIZLEME_YUKSEKLIK // 2,
            text=mesaj, fill="#999999", font=("Segoe UI", 9), width=self.ONIZLEME_GENISLIK - 16)
        self.d_onizleme.set("")

    def _onizleme_yenile(self):
        """Şablonu ve üzerinde tıklanacak noktayı gösterir."""
        ad = self.d_goruntu.get().strip()
        if not ad:
            self._onizleme_temizle(M("onizleme.yok"))
            return
        yol = motor.goruntu_yolu(ad)
        if not os.path.isfile(yol):
            self._onizleme_temizle(M("onizleme.dosya_yok") % ad)
            return

        try:
            resim = tk.PhotoImage(file=yol)
            genislik, yukseklik = resim.width(), resim.height()
            # Onizleme kutusunun yarisi kadar yer tiklama noktasina ayrilir
            bolen = max(1, -(-genislik // (self.ONIZLEME_GENISLIK - 40)),
                        -(-yukseklik // (self.ONIZLEME_YUKSEKLIK - 30)))
            if bolen > 1:
                resim = resim.subsample(bolen, bolen)
        except Exception as hata:
            self._onizleme_temizle(M("onizleme.hata") % hata)
            return

        self._onizleme_resmi = resim
        self.onizleme_tuvali.delete("all")
        resim_g, resim_y = resim.width(), resim.height()
        x0 = (self.ONIZLEME_GENISLIK - resim_g) // 2
        y0 = (self.ONIZLEME_YUKSEKLIK - resim_y) // 2
        self.onizleme_tuvali.create_image(x0, y0, anchor="nw", image=resim)
        self.onizleme_tuvali.create_rectangle(x0, y0, x0 + resim_g, y0 + resim_y,
                                              outline="#34c759", width=2)

        kaydir_x = self._sayi(self.d_kaydir_x, 0)
        kaydir_y = self._sayi(self.d_kaydir_y, 0)
        nokta_x = x0 + (genislik / 2 + kaydir_x) / bolen
        nokta_y = y0 + (yukseklik / 2 + kaydir_y) / bolen
        disarida = not (x0 <= nokta_x <= x0 + resim_g and y0 <= nokta_y <= y0 + resim_y)
        nokta_x = max(6, min(self.ONIZLEME_GENISLIK - 6, nokta_x))
        nokta_y = max(6, min(self.ONIZLEME_YUKSEKLIK - 6, nokta_y))
        renk = "#ff9500" if disarida else "#ff3b30"
        self.onizleme_tuvali.create_line(nokta_x - 11, nokta_y, nokta_x - 3, nokta_y,
                                         fill=renk, width=2)
        self.onizleme_tuvali.create_line(nokta_x + 3, nokta_y, nokta_x + 11, nokta_y,
                                         fill=renk, width=2)
        self.onizleme_tuvali.create_line(nokta_x, nokta_y - 11, nokta_x, nokta_y - 3,
                                         fill=renk, width=2)
        self.onizleme_tuvali.create_line(nokta_x, nokta_y + 3, nokta_x, nokta_y + 11,
                                         fill=renk, width=2)
        self.onizleme_tuvali.create_oval(nokta_x - 5, nokta_y - 5, nokta_x + 5, nokta_y + 5,
                                         outline=renk, width=2)

        konum_metni = (M("onizleme.merkez") if (kaydir_x, kaydir_y) == (0, 0)
                       else M("onizleme.kaydirma") % (kaydir_x, kaydir_y))
        if disarida:
            konum_metni += M("onizleme.disarida")
        self.d_onizleme.set(M("onizleme.bilgi")
                            % (ad, genislik, yukseklik, konum_metni))

    def goruntuyu_dene(self):
        """Seçili görüntüyü ekranda şimdi arar ve sonucu bildirir."""
        ad = self.d_goruntu.get().strip()
        if not ad:
            messagebox.showinfo(M("kutu.goruntu_yok_baslik"), M("kutu.goruntu_yok"),
                                parent=self)
            return
        yol = motor.goruntu_yolu(ad)
        tolerans = self._sayi(self.d_esik, 5, en_az=0) / 100.0
        try:
            baslangic = time.perf_counter()
            bulunan = ekran.sablonu_bul(yol, tolerans)
            sure = (time.perf_counter() - baslangic) * 1000
        except Exception as hata:
            messagebox.showerror(M("kutu.arama_hata"), str(hata), parent=self)
            return

        if not bulunan:
            self.kaydet_gunluk(M("kayit.arama_yok") % (ad, sure))
            messagebox.showwarning(M("kutu.bulunamadi_baslik"),
                                   M("kutu.bulunamadi") % ad, parent=self)
            return

        sol, ust, genislik, yukseklik = bulunan
        merkez_x = sol + genislik // 2 + self._sayi(self.d_kaydir_x, 0)
        merkez_y = ust + yukseklik // 2 + self._sayi(self.d_kaydir_y, 0)
        self.kaydet_gunluk(M("kayit.arama_var")
                           % (ad, sol, ust, genislik, yukseklik,
                              merkez_x, merkez_y, sure))
        winput.fareyi_tasi(merkez_x, merkez_y)

    # ------------------------------------------------------------ konum yakalama
    def konumu_yakala(self):
        x, y = winput.imlec_konumu()
        self.d_x.set(str(x))
        self.d_y.set(str(y))
        if self.d_yakala_ekle.get():
            self.adim_ekle()
        else:
            self.kaydet_gunluk(M("kayit.konum") % (x, y))

    def geri_sayimla_yakala(self):
        if self.geri_sayim_isi:
            return
        self._geri_say(self._sayi(self.d_hazirlik, 3, en_az=1))

    def _geri_say(self, kalan):
        if kalan <= 0:
            self.geri_sayim_isi = None
            self.geri_sayim_dugmesi.configure(text=M("form.geri_sayim"))
            self.konumu_yakala()
            return
        self.geri_sayim_dugmesi.configure(text=M("form.geri_sayim_devam") % kalan)
        self.geri_sayim_isi = self.after(1000, lambda: self._geri_say(kalan - 1))

    def _imleci_izle(self):
        try:
            x, y = winput.imlec_konumu()
            self.d_imlec.set(M("durum.imlec") % (x, y))
        except Exception:
            pass
        self._is_imlec = self.after(100, self._imleci_izle)

    # ------------------------------------------------------------ çalıştırma
    def baslat(self):
        if self.oynatici and self.oynatici.is_alive():
            return
        if self.geri_sayim_isi:     # suren bir konum yakalama geri sayimini iptal et
            self.after_cancel(self.geri_sayim_isi)
            self.geri_sayim_isi = None
            self.geri_sayim_dugmesi.configure(text=M("form.geri_sayim"))
        aktifler = [a for a in self.adimlar if a.get("aktif", True)]
        if not aktifler:
            messagebox.showwarning(M("kutu.liste_bos_baslik"), M("kutu.liste_bos"),
                                   parent=self)
            return
        for sira, adim in enumerate(aktifler, start=1):
            hata = motor.adimi_dogrula(adim)
            if hata:
                messagebox.showwarning(M("kutu.gecersiz_baslik"),
                                       M("kutu.gecersiz_adim") % (sira, hata),
                                       parent=self)
                return

        hazirlik = self._sayi(self.d_hazirlik, 3, en_az=0)
        self._calisma_kilidi(True)
        if hazirlik > 0:
            self.d_durum.set(M("durum.basliyor"))
            self.kaydet_gunluk(M("kayit.baslatiliyor") % hazirlik)
            self._baslama_geri_sayimi(hazirlik)
        else:
            self._motoru_calistir()

    def _baslama_geri_sayimi(self, kalan):
        if kalan <= 0:
            self._motoru_calistir()
            return
        self.d_durum.set(M("durum.basliyor_sayac") % kalan)
        self.geri_sayim_isi = self.after(1000, lambda: self._baslama_geri_sayimi(kalan - 1))

    def _motoru_calistir(self):
        self.geri_sayim_isi = None
        if self.d_kucult.get():
            self.iconify()
        self.oynatici = motor.Oynatici(
            adimlar=self.adimlar,
            tur_sayisi=self._sayi(self.d_tur, 1, en_az=0),
            tur_beklemesi=self._sayi(self.d_tur_beklemesi, 0, en_az=0),
            geri_bildirim=self._motordan,
            konum_sapmasi=self._sayi(self.d_konum_sapmasi, 0, en_az=0),
            gecikme_sapmasi=self._sayi(self.d_gecikme_sapmasi, 0, en_az=0),
            acil_tus=self.d_esc.get(),
        )
        tur = self._sayi(self.d_tur, 1, en_az=0)
        self.d_durum.set(M("durum.calisiyor"))
        self.durum_etiketi.configure(style="Calisiyor.TLabel")
        self.kaydet_gunluk(M("kayit.baslatildi") % (
            M("kayit.sonsuz") if tur == 0 else str(tur),
            len([a for a in self.adimlar if a.get("aktif", True)])))
        self.oynatici.start()

    def durdur(self):
        if self.geri_sayim_isi:
            self.after_cancel(self.geri_sayim_isi)
            self.geri_sayim_isi = None
            self._calisma_kilidi(False)
            self.d_durum.set(M("durum.iptal"))
            self.kaydet_gunluk(M("kayit.baslatma_iptal"))
            return
        if self.oynatici and self.oynatici.is_alive():
            self.oynatici.durdur()
            self.d_durum.set(M("durum.durduruluyor"))

    def duraklat(self):
        if not (self.oynatici and self.oynatici.is_alive()):
            return
        duraklatildi = self.oynatici.duraklat_degistir()
        self.d_durum.set(M("durum.duraklatildi") if duraklatildi
                         else M("durum.calisiyor"))
        self.duraklat_dugmesi.configure(
            text=M("cal.devam") if duraklatildi else M("cal.duraklat"))
        self.kaydet_gunluk(M("kayit.duraklatildi") if duraklatildi
                           else M("kayit.devam"))

    def _calisma_kilidi(self, calisiyor):
        self.baslat_dugmesi.configure(state="disabled" if calisiyor else "normal")
        self.durdur_dugmesi.configure(state="normal" if calisiyor else "disabled")
        self.duraklat_dugmesi.configure(state="normal" if calisiyor else "disabled")
        if not calisiyor:
            self.duraklat_dugmesi.configure(text=M("cal.duraklat"))
            self.durum_etiketi.configure(style="Durdu.TLabel")

    # --------------------------------------------- motor -> arayüz köprüsü
    def _motordan(self, olay, veri):
        """Oynatıcı iş parçacığından çağrılır; kuyruğa bırakır."""
        self.olay_kuyrugu.put((olay, veri))

    def _kuyrugu_isle(self):
        try:
            while True:
                olay, veri = self.olay_kuyrugu.get_nowait()
                self._olayi_uygula(olay, veri)
        except queue.Empty:
            pass
        self._is_kuyruk = self.after(60, self._kuyrugu_isle)

    def _olayi_uygula(self, olay, veri):
        if olay == "kisayol":
            self._kisayol_uygula(veri)
        elif olay == "tur":
            tur, toplam = veri
            self._tur_metni = M("durum.tur") % (tur, "∞" if toplam == 0 else toplam)
            self.d_ilerleme.set(self._tur_metni)
        elif olay == "adim":
            _tur, sira, toplam_adim, adim = veri
            self.d_ilerleme.set(M("durum.adim") % (
                self._tur_metni, sira, toplam_adim, motor.adim_ozeti(adim)))
        elif olay == "kayit":
            self.kaydet_gunluk(veri)
        elif olay == "bitti":
            self._calisma_kilidi(False)
            aciklama = {"tamam": M("durum.tamamlandi"),
                        "durduruldu": M("durum.durduruldu"),
                        "bulunamadi": M("durum.bulunamadi"),
                        "hata": M("durum.hata")}.get(veri, veri)
            self.d_durum.set(aciklama)
            self.d_ilerleme.set("")
            self.kaydet_gunluk(M("kayit.bitti") % aciklama)
            self.oynatici = None
            if self.state() == "iconic":
                self.deiconify()

    # ------------------------------------------------------------ kısayollar
    def _kisayollari_baslat(self):
        self.dinleyici = kisayol.KisayolDinleyici(
            KISAYOLLAR, lambda kimlik: self.olay_kuyrugu.put(("kisayol", kimlik)))
        self.dinleyici.start()
        self.dinleyici.hazir.wait(timeout=2.0)
        if self.dinleyici.basarisiz:
            self.after(400, lambda: self.kaydet_gunluk(
                M("kayit.kisayol_uyari") % ", ".join(self.dinleyici.basarisiz)))

    def _kisayol_uygula(self, kimlik):
        if kimlik == KS_BASLAT:
            if self.oynatici and self.oynatici.is_alive():
                self.durdur()
            else:
                self.baslat()
        elif kimlik in (KS_DURDUR, KS_DURDUR_CTRL_T):
            self.durdur()
        elif kimlik == KS_YAKALA:
            self.konumu_yakala()
        elif kimlik == KS_DURAKLAT:
            self.duraklat()

    # ------------------------------------------------------------ dosya
    def yeni_liste(self):
        if self.kirli and self.adimlar and not messagebox.askyesno(
                M("kutu.yeni_baslik"), M("kutu.yeni"), parent=self):
            return
        self.adimlar = []
        self.acik_dosya = None
        self.kirli = False
        self.listeyi_yenile()
        self._baslik_guncelle()
        self.kaydet_gunluk(M("kayit.yeni_liste"))

    def listeyi_ac(self):
        yol = filedialog.askopenfilename(
            parent=self, title=M("kutu.ac_baslik"), initialdir=KLASOR,
            filetypes=[(M("kutu.dosya_turu"), "*.json"),
                       (M("kutu.tum_dosyalar"), "*.*")])
        if not yol:
            return
        try:
            with open(yol, "r", encoding="utf-8") as dosya:
                veri = json.load(dosya)
            adimlar = veri.get("adimlar", veri if isinstance(veri, list) else [])
            temiz, eski_kosul = [], 0
            for ham in adimlar:
                tip = ham.get("tip")
                if tip == "kosul":
                    # Eski surumun ayri "Koşul (IF)" adimi kaldirildi
                    eski_kosul += 1
                    continue
                if tip not in motor.ISLEMLER:
                    raise ValueError(M("hata.bilinmeyen_islem") % tip)
                adim = motor.bos_adim(tip)      # varsayilanlar adimin kendi turune gore
                adim.update({k: v for k, v in ham.items() if k in adim})
                temiz.append(adim)
            self.adimlar = temiz
            if isinstance(veri, dict):
                self.d_tur.set(str(veri.get("tur", 1)))
                self.d_tur_beklemesi.set(str(veri.get("tur_beklemesi", 1000)))
            self.acik_dosya = yol
            self.kirli = False
            self.listeyi_yenile()
            self._baslik_guncelle()
            self.kaydet_gunluk(M("kayit.acildi")
                               % (os.path.basename(yol), len(temiz)))
            if eski_kosul:
                self.kaydet_gunluk(M("kayit.eski_kosul") % eski_kosul)
        except Exception as hata:
            messagebox.showerror(M("kutu.acilamadi"),
                                 M("kutu.acilamadi_mesaj") % hata, parent=self)

    def listeyi_kaydet(self, farkli=False):
        yol = self.acik_dosya
        if farkli or not yol:
            yol = filedialog.asksaveasfilename(
                parent=self, title=M("kutu.kaydet_baslik"), initialdir=KLASOR,
                defaultextension=".json", initialfile="tiklama_listesi.json",
                filetypes=[(M("kutu.dosya_turu"), "*.json")])
            if not yol:
                return
        veri = {
            "surum": SURUM,
            "tur": self._sayi(self.d_tur, 1, en_az=0),
            "tur_beklemesi": self._sayi(self.d_tur_beklemesi, 0, en_az=0),
            "adimlar": self.adimlar,
        }
        try:
            with open(yol, "w", encoding="utf-8") as dosya:
                json.dump(veri, dosya, ensure_ascii=False, indent=2)
            self.acik_dosya = yol
            self.kirli = False
            self._baslik_guncelle()
            self.kaydet_gunluk(M("kayit.kaydedildi") % os.path.basename(yol))
        except Exception as hata:
            messagebox.showerror(M("kutu.kayit_hata"), str(hata), parent=self)

    # ------------------------------------------------------------ ayarlar
    def ayarlari_yukle(self):
        try:
            with open(AYAR_DOSYASI, "r", encoding="utf-8") as dosya:
                ayar = json.load(dosya)
        except Exception:
            return
        for anahtar, degisken in (
            ("tur", self.d_tur), ("tur_beklemesi", self.d_tur_beklemesi),
            ("hazirlik", self.d_hazirlik), ("konum_sapmasi", self.d_konum_sapmasi),
            ("gecikme_sapmasi", self.d_gecikme_sapmasi),
        ):
            if anahtar in ayar:
                degisken.set(str(ayar[anahtar]))
        if "kucult" in ayar:
            self.d_kucult.set(bool(ayar["kucult"]))
        son = ayar.get("son_dosya")
        if son and os.path.isfile(son):
            try:
                with open(son, "r", encoding="utf-8") as dosya:
                    veri = json.load(dosya)
                self.adimlar = veri.get("adimlar", [])
                self.acik_dosya = son
                self.listeyi_yenile()
                self._baslik_guncelle()
                self.kaydet_gunluk(M("kayit.son_liste") % os.path.basename(son))
            except Exception:
                pass

    def ayarlari_kaydet(self):
        ayar = {
            "tur": self.d_tur.get(),
            "tur_beklemesi": self.d_tur_beklemesi.get(),
            "hazirlik": self.d_hazirlik.get(),
            "konum_sapmasi": self.d_konum_sapmasi.get(),
            "gecikme_sapmasi": self.d_gecikme_sapmasi.get(),
            "kucult": self.d_kucult.get(),
            "dil": diller.mevcut(),
            "son_dosya": self.acik_dosya,
        }
        try:
            with open(AYAR_DOSYASI, "w", encoding="utf-8") as dosya:
                json.dump(ayar, dosya, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ------------------------------------------------------------ dil
    def dili_degistir(self, kod):
        """Dili değiştirir ve arayüzü o dilde yeniden kurar."""
        if kod == diller.mevcut():
            return
        if self.oynatici and self.oynatici.is_alive():
            self.d_dil.set(diller.mevcut())
            return

        # Formdaki adım ve seçim, dil değişince yeniden kurulacağı için saklanır
        secili = self._secili_indis()
        try:
            form_adimi = self._formdan_adim()
        except Exception:
            form_adimi = None
        gunluk_metni = self.gunluk.get("1.0", "end-1c")

        diller.ayarla(kod)
        self.d_dil.set(kod)

        for parca in self.winfo_children():
            parca.destroy()
        self._arayuzu_kur()

        self.gunluk.configure(state="normal")
        self.gunluk.insert("end", gunluk_metni + ("\n" if gunluk_metni else ""))
        self.gunluk.see("end")
        self.gunluk.configure(state="disabled")

        self.listeyi_yenile(secili)
        if form_adimi:
            self._forma_adim(form_adimi)
        self._baslik_guncelle()
        self._calisma_kilidi(False)
        self.d_durum.set(M("durum.beklemede"))
        ad = dict(diller.DILLER).get(kod, kod)
        self.kaydet_gunluk(M("kayit.dil") % ad)

    # ------------------------------------------------------------ yardım
    def yardim_goster(self):
        messagebox.showinfo(M("yardim.baslik"), M("yardim.metin"), parent=self)

    def hakkinda_goster(self):
        messagebox.showinfo(
            M("hakkinda.baslik"),
            M("hakkinda.metin") % (M("uygulama.ad"), SURUM, sys.version.split()[0],
                                   self.tk.call("info", "patchlevel"), DPI_MODU),
            parent=self)

    # ------------------------------------------------------------ kapanış
    def kapat(self):
        if self.oynatici and self.oynatici.is_alive():
            if not messagebox.askyesno(M("kutu.calisiyor_baslik"), M("kutu.calisiyor"),
                                       parent=self):
                return
            self.oynatici.durdur()
            self.oynatici.join(timeout=2.0)
        if self.kirli and self.adimlar:
            cevap = messagebox.askyesnocancel(
                M("kutu.degisiklik_baslik"), M("kutu.degisiklik"), parent=self)
            if cevap is None:
                return
            if cevap:
                self.listeyi_kaydet()
        for is_kimligi in (getattr(self, '_is_kuyruk', None),
                           getattr(self, '_is_imlec', None),
                           self.geri_sayim_isi):
            if is_kimligi:
                try:
                    self.after_cancel(is_kimligi)
                except Exception:
                    pass
        self.ayarlari_kaydet()
        try:
            self.dinleyici.durdur()
        except Exception:
            pass
        self.destroy()


DPI_MODU = "yok"


def main():
    global DPI_MODU
    if not sys.platform.startswith("win"):
        print("Bu program yalnızca Windows üzerinde çalışır.")
        return 1
    DPI_MODU = winput.dpi_farkindaligi_ac()
    uygulama = Uygulama()
    uygulama.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
