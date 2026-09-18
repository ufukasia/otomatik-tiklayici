# -*- coding: utf-8 -*-
"""
demo.gif uretir: GERCEK uygulamayi calistirip ekrani kaydeder.

Gereksinim: python -m pip install pillow
Kullanim:   python gif_yap.py   (calisirken fareye dokunmayin)

Akis:
  1  Aranacak bolge fareyle cizilir
  2  Tiklanacak nokta isaretlenir
  3  Hedef pencere baska yere tasinir; program onu bulup dogru noktaya tiklar

Fare imleci GDI ile yakalanmaz, bu yuzden her kareye gercek imlec konumundan
bir ok cizilir. Alt seride o anki asama yazilir.
"""
import os
import sys
import threading
import time
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont

KLASOR = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.join(KLASOR, "derleme_gecici")
os.makedirs(SCRATCH, exist_ok=True)
sys.path.insert(0, KLASOR)

import diller
import ekran
import winput
import motor
import otomatik_tiklayici as app

winput.dpi_farkindaligi_ac()
app.AYAR_DOSYASI = os.path.join(SCRATCH, "gif_ayarlar.json")
# Uygulama acilirken dili bu dosyadan okur; GIF her iki README'de kullanilacagi
# icin arayuz Ingilizce olmali.
import json
with open(app.AYAR_DOSYASI, "w", encoding="utf-8") as _d:
    json.dump({"dil": "en"}, _d)

# ---------------------------------------------------------------- kayit alani
KX, KY, KG, KYK = 1060, 255, 990, 500
OLCEK = 0.64
KARE_MS = 90

YAZILAR = {
    1: "1  ·  Drag the area to search for   /   Aranacak alani cizin",
    2: "2  ·  Mark the point to click   /   Tiklanacak noktayi isaretleyin",
    3: "3  ·  Window moved — it finds the area and clicks that point",
}

kareler = []
kayit_suruyor = threading.Event()
asama = {"v": 1}


def kaydedici():
    sonraki = time.perf_counter()
    while kayit_suruyor.is_set():
        try:
            bayt, g, y, _s, _u = ekran.yakala(KX, KY, KG, KYK)
        except Exception:
            break
        kareler.append((bayt, g, y, winput.imlec_konumu(), asama["v"]))
        sonraki += KARE_MS / 1000.0
        uyku = sonraki - time.perf_counter()
        time.sleep(uyku if uyku > 0 else 0)
        if uyku <= 0:
            sonraki = time.perf_counter()


def bekle(saniye):
    bitis = time.perf_counter() + saniye
    while time.perf_counter() < bitis:
        try:
            kok.update()
        except tk.TclError:
            return
        time.sleep(0.01)


def yumusak_tasi(x1, y1, x2, y2, adim=14, gecikme=0.035):
    for i in range(1, adim + 1):
        t = i / adim
        t = t * t * (3 - 2 * t)
        winput.fareyi_tasi(int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t))
        time.sleep(gecikme)


# ---------------------------------------------------------------- sahne
diller.ayarla("en")
u = app.Uygulama()
u.withdraw()
u.update()
kok = u

# Kayit alanini kaplayan notr bir zemin: gercek masaustu icerigi GIF'e girmesin
zemin = tk.Toplevel(u)
zemin.overrideredirect(True)
zemin.attributes("-topmost", True)
zemin.geometry("%dx%d+%d+%d" % (KG + 40, KYK + 40, KX - 20, KY - 20))
zemin_tuval = tk.Canvas(zemin, highlightthickness=0, bg="#0f172a")
zemin_tuval.pack(fill="both", expand=True)
for _i in range(0, KYK + 40, 3):                      # yumusak degrade
    _t = _i / float(KYK + 40)
    zemin_tuval.create_line(
        0, _i, KG + 40, _i, width=3,
        fill="#%02x%02x%02x" % (int(15 + 26 * _t), int(23 + 36 * _t), int(42 + 56 * _t)))
zemin.update()

HEDEF_G, HEDEF_Y = 520, 330
hedef = tk.Toplevel(u)
hedef.overrideredirect(True)
hedef.attributes("-topmost", True)
tuval = tk.Canvas(hedef, bg="#ffffff", highlightthickness=0)
tuval.pack(fill="both", expand=True)
tuval.create_rectangle(0, 0, HEDEF_G, 56, fill="#2563eb", outline="")
tuval.create_text(24, 28, text="Demo Window", anchor="w", fill="white",
                  font=("Segoe UI", 15, "bold"))
tuval.create_text(28, 100, text="Your files are ready.", anchor="w", fill="#111827",
                  font=("Segoe UI", 15))
tuval.create_text(28, 136, text="Choose an action to continue.", anchor="w",
                  fill="#6b7280", font=("Segoe UI", 12))
tuval.create_rectangle(28, 180, 190, 236, fill="#e5e7eb", outline="#9ca3af", width=2)
tuval.create_text(109, 208, text="Cancel", fill="#374151", font=("Segoe UI", 13))
DUGME = (250, 180, 470, 236)
dugme_kutu = tuval.create_rectangle(*DUGME, fill="#f97316", outline="#c2410c", width=2)
dugme_yazi = tuval.create_text((DUGME[0] + DUGME[2]) // 2, (DUGME[1] + DUGME[3]) // 2,
                               text="Download", fill="white",
                               font=("Segoe UI", 14, "bold"))
tuval.create_text(28, 292, text="demo target — not a real application", anchor="w",
                  fill="#9ca3af", font=("Segoe UI", 9))

ILK_X, ILK_Y = 1120, 300
hedef.geometry("%dx%d+%d+%d" % (HEDEF_G, HEDEF_Y, ILK_X, ILK_Y))
hedef.update()
bekle(0.6)

tiklandi = {"n": 0}


def dugmeye_tiklandi(olay=None):
    tiklandi["n"] += 1
    tuval.itemconfigure(dugme_kutu, fill="#16a34a", outline="#15803d")
    tuval.itemconfigure(dugme_yazi, text="✓  Clicked")


tuval.tag_bind(dugme_kutu, "<Button-1>", dugmeye_tiklandi)
tuval.tag_bind(dugme_yazi, "<Button-1>", dugmeye_tiklandi)

BOLGE = (ILK_X + 20, ILK_Y + 70, ILK_X + 500, ILK_Y + 260)
BUTON_MERKEZI = (ILK_X + (DUGME[0] + DUGME[2]) // 2, ILK_Y + (DUGME[1] + DUGME[3]) // 2)


def surucu():
    time.sleep(1.9)
    x1, y1, x2, y2 = BOLGE
    yumusak_tasi(x1 - 140, y1 - 80, x1, y1, adim=18)
    time.sleep(0.5)
    winput.basili_tut("sol")
    time.sleep(0.35)
    yumusak_tasi(x1, y1, x2, y2, adim=26, gecikme=0.05)
    time.sleep(0.6)
    winput.dugmeyi_birak("sol")
    asama["v"] = 2
    time.sleep(1.2)
    yumusak_tasi(x2, y2, BUTON_MERKEZI[0], BUTON_MERKEZI[1], adim=24, gecikme=0.05)
    time.sleep(1.1)
    winput.tikla("sol")


kayit_suruyor.set()
threading.Thread(target=kaydedici, daemon=True).start()
threading.Thread(target=surucu, daemon=True).start()

u.d_islem.set(motor.islem_adi("sol_tik"))
u.d_hedef.set("goruntu")
u.bolge_sec()
u.update()
bekle(0.8)

sablon = u.d_goruntu.get()
print("yakalanan sablon:", sablon, "| kayma:", u.d_kaydir_x.get(), u.d_kaydir_y.get())

asama["v"] = 3
bekle(0.6)
hedef.geometry("%dx%d+%d+%d" % (HEDEF_G, HEDEF_Y, 1450, 390))
hedef.update_idletasks()
hedef.lift()
bekle(1.5)

adim = motor.bos_adim("sol_tik")
adim.update({"hedef": "goruntu", "goruntu": sablon, "esik": 0, "zaman_asimi": 3000,
             "kaydir_x": int(u.d_kaydir_x.get()), "kaydir_y": int(u.d_kaydir_y.get()),
             "bekleme": 0})

bitti = {"durum": False}
oynatici = motor.Oynatici([adim], 1, 0,
                          lambda ol, v: bitti.__setitem__("durum", True)
                          if ol == "bitti" else None, acil_tus=False)
oynatici.start()
bitis = time.perf_counter() + 12
while not bitti["durum"] and time.perf_counter() < bitis:
    bekle(0.05)
bekle(2.0)

kayit_suruyor.clear()
time.sleep(0.4)
print("tiklama sayisi:", tiklandi["n"], "| ham kare:", len(kareler))

hedef.destroy()
zemin.destroy()
u.dinleyici.durdur()
u.destroy()
for p in (motor.goruntu_yolu(sablon) if sablon else "", app.AYAR_DOSYASI):
    if p and os.path.isfile(p):
        os.remove(p)

# ---------------------------------------------------------------- GIF uret
if not kareler:
    raise SystemExit("kare yakalanamadi")

OK = [(0, 0), (0, 22), (5.6, 16.8), (9.3, 25.6), (13.2, 23.9), (9.7, 15.3), (16.5, 15)]


def imlec_ciz(resim, x, y):
    ciz = ImageDraw.Draw(resim)
    noktalar = [(x + ox * 1.6, y + oy * 1.6) for ox, oy in OK]
    ciz.polygon(noktalar, fill=(255, 255, 255))
    ciz.line(noktalar + [noktalar[0]], fill=(17, 24, 39), width=3, joint="curve")


try:
    yazi_tipi = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 19)
except Exception:
    yazi_tipi = ImageFont.load_default()


def serit_ciz(resim, metin):
    ciz = ImageDraw.Draw(resim, "RGBA")
    g, y = resim.size
    ciz.rectangle([0, y - 42, g, y], fill=(17, 24, 39, 235))
    ciz.text((16, y - 31), metin, font=yazi_tipi, fill=(255, 255, 255))


hedef_g, hedef_y = int(KG * OLCEK), int(KYK * OLCEK)
resimler = []
onceki = None
for bayt, g, y, (mx, my), asama_no in kareler:
    anahtar = (bayt, mx, my, asama_no)
    if anahtar == onceki:
        continue                       # imlec de ekran da degismediyse atla
    onceki = anahtar
    kare = Image.frombuffer("RGBA", (g, y), bayt, "raw", "BGRA", 0, 1).convert("RGB")
    if KX <= mx < KX + KG and KY <= my < KY + KYK:
        imlec_ciz(kare, mx - KX, my - KY)
    kare = kare.resize((hedef_g, hedef_y), Image.LANCZOS)
    serit_ciz(kare, YAZILAR[asama_no])
    resimler.append(kare)

# Son karede bir sure duraksa
resimler += [resimler[-1]] * 12
print("benzersiz kare:", len(resimler), "| boyut:", hedef_g, "x", hedef_y,
      "| sure: %.1f sn" % (len(resimler) * KARE_MS / 1000.0))

cikti = os.path.join(KLASOR, "demo.gif")
resimler[0].save(cikti, save_all=True, append_images=resimler[1:],
                 duration=KARE_MS, loop=0, optimize=True,
                 palette=Image.ADAPTIVE, colors=128)
print("GIF:", cikti, "%.1f MB" % (os.path.getsize(cikti) / 1024 / 1024))

