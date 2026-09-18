# -*- coding: utf-8 -*-
"""
diller.py - Arayuz metinleri (Turkce / English).

Kullanim:
    from diller import M
    M("dugme.baslat")            -> "▶  BAŞLAT  (F6)"
    M("durum.tur") % (2, 5)      -> "Tur 2/5"

Dil degistirmek icin diller.ayarla("en"). Eksik bir anahtar varsa once
Turkce karsiligi, o da yoksa anahtarin kendisi dondurulur.
"""

VARSAYILAN = "tr"

DILLER = [("tr", "Türkçe"), ("en", "English")]

_secili = VARSAYILAN


def ayarla(kod):
    global _secili
    _secili = kod if kod in METINLER else VARSAYILAN
    return _secili


def mevcut():
    return _secili


def M(anahtar):
    sozluk = METINLER.get(_secili, {})
    if anahtar in sozluk:
        return sozluk[anahtar]
    return METINLER[VARSAYILAN].get(anahtar, anahtar)


METINLER = {
    # ==================================================================== TR
    "tr": {
        "uygulama.ad": "Otomatik Tıklayıcı",

        # --- menu ---
        "menu.dosya": "Dosya",
        "menu.yeni": "Yeni Liste",
        "menu.ac": "Aç...",
        "menu.kaydet": "Kaydet",
        "menu.farkli_kaydet": "Farklı Kaydet...",
        "menu.cikis": "Çıkış",
        "menu.dil": "Dil / Language",
        "menu.yardim": "Yardım",
        "menu.kullanim": "Kullanım / Kısayollar",
        "menu.hakkinda": "Hakkında",

        # --- islem adlari ---
        "islem.sol_tik": "Sol Tık",
        "islem.sag_tik": "Sağ Tık",
        "islem.cift_tik": "Çift Tık",
        "islem.orta_tik": "Orta Tık",
        "islem.tasi": "Fareyi Taşı",
        "islem.basili_tut": "Sol Tuşu Basılı Tut",
        "islem.birak": "Sol Tuşu Bırak",
        "islem.tekerlek": "Tekerlek Kaydır",
        "islem.goruntu_bekle": "Görüntüyü Bekle",
        "islem.kosul": "Koşul (IF)",
        "islem.tus": "Tuşa Bas",
        "islem.metin": "Metin Yaz",
        "islem.bekle": "Bekle",

        # --- deger alani etiketleri ---
        "deger.tekerlek": "Çentik (+yukarı / -aşağı)",
        "deger.tus": "Tuş (örn: enter, ctrl+c, f5)",
        "deger.metin": "Yazılacak metin",
        "deger.yok": "Değer (kullanılmıyor)",

        # --- form ---
        "form.baslik": " Adım Ekle / Düzenle ",
        "form.islem": "İşlem",
        "form.sonucu_yaz": "Sonucu yaz",
        "form.yuvasina": "yuvasına",
        "form.hedef": "Hedef",
        "form.koordinat": "Koordinat",
        "form.goruntu": "Görüntü",
        "form.konum": "Konum X / Y",
        "form.konum_yakala": "📍 Konumu Yakala  (F7)",
        "form.geri_sayim": "⏱ 3 sn Sonra Yakala",
        "form.geri_sayim_devam": "⏱ %d ...",
        "form.f7_ekle": "F7 basınca doğrudan listeye ekle",
        "form.bolge_sec": "🖼 Bölge + Tıklama Noktası Seç",
        "form.nokta_sec": "🎯 Tıklama Noktasını Değiştir",
        "form.tolerans": "Eşleşme toleransı (%)",
        "form.zaman_asimi": "En fazla arama (ms)",
        "form.kaydirma": "Tıklama kayması",
        "form.bulunamazsa": "Bulunamazsa",
        "form.simdi_ara": "🔍 Şimdi Ekranda Ara",
        "form.kosul_sart": "Çalışma koşulu",
        "form.tekrar": "Tekrar",
        "form.bekleme": "Sonra bekle (ms)",
        "form.not": "Not",
        "form.ekle": "➕ Listeye Ekle",
        "form.guncelle": "✎ Seçiliyi Güncelle",

        # --- onizleme ---
        "onizleme.yok": "Henüz görüntü seçilmedi",
        "onizleme.dosya_yok": "⚠ Dosya bulunamadı:\n%s",
        "onizleme.hata": "Önizleme gösterilemedi:\n%s",
        "onizleme.bilgi": "%s · %d x %d px\n🔴 tıklama: %s",
        "onizleme.merkez": "tam ortasına",
        "onizleme.kaydirma": "ortadan %+d, %+d",
        "onizleme.disarida": " (bölgenin dışında)",

        # --- liste ---
        "liste.baslik": " Adım Listesi ",
        "liste.sira": "#",
        "liste.durum": "Aktif",
        "liste.islem": "İşlem",
        "liste.kosul": "Koşul",
        "liste.hedef": "Hedef",
        "liste.deger": "Değer",
        "liste.tekrar": "Tekrar",
        "liste.bekleme": "Bekleme (ms)",
        "liste.not": "Not",
        "liste.ornek_islem": "Sol Tuşu Basılı Tut",
        "liste.ornek_kosul": "→ if1 belirle",
        "liste.ornek_deger": "ctrl+shift+s",
        "liste.yukari": "▲ Yukarı",
        "liste.asagi": "▼ Aşağı",
        "liste.cogalt": "⧉ Çoğalt",
        "liste.aktiflik": "✓/✗ Aktiflik",
        "liste.sil": "🗑 Sil",
        "liste.temizle": "Tümünü Temizle",
        "liste.dene": "▶ Seçiliyi Dene",

        # --- calistirma ---
        "cal.baslik": " Çalıştırma ",
        "cal.tur": "Tur sayısı",
        "cal.sonsuz": "(0 = sonsuz)",
        "cal.tur_beklemesi": "Tur arası bekleme (ms)",
        "cal.hazirlik": "Başlamadan önce (sn)",
        "cal.konum_sapmasi": "Konum sapması (px)",
        "cal.gecikme_sapmasi": "Gecikme sapması (%)",
        "cal.kucult": "Başlayınca pencereyi küçült",
        "cal.baslat": "▶  BAŞLAT  (F6)",
        "cal.duraklat": "⏸ Duraklat (F9)",
        "cal.devam": "▶ Devam Et (F9)",
        "cal.durdur": "⏹ Durdur (F8 / Ctrl+T)",
        "cal.gunluk": " Günlük ",

        # --- durum ---
        "durum.beklemede": "Beklemede",
        "durum.calisiyor": "ÇALIŞIYOR",
        "durum.duraklatildi": "DURAKLATILDI",
        "durum.basliyor": "Başlıyor...",
        "durum.basliyor_sayac": "Başlıyor: %d",
        "durum.durduruluyor": "Durduruluyor...",
        "durum.iptal": "İptal edildi",
        "durum.tamamlandi": "Tamamlandı",
        "durum.durduruldu": "Durduruldu",
        "durum.bulunamadi": "Görüntü bulunamadı",
        "durum.hata": "Hata ile durdu",
        "durum.imlec_bos": "İmleç: -",
        "durum.imlec": "İmleç:  X = %-6d Y = %-6d",
        "durum.kaydedilmemis": "Kaydedilmemiş liste",
        "durum.tur": "Tur %d/%s",
        "durum.adim": "%s · Adım %d/%d · %s",

        # --- bolge secici ---
        "secici.asama1": "1/2  ·  Ekranda ARANACAK alanı fareyle çizin",
        "secici.asama1_alt": "Tıklanacak butonu ya da onu içeren çerçeveyi kapsayın"
                            "   ·   ESC = vazgeç",
        "secici.asama2": "2/2  ·  Şimdi TIKLANACAK noktayı seçin",
        "secici.asama2_alt": "Nokta bölgenin dışında da olabilir"
                            "   ·   Enter = bölgenin ortası   ·   ESC = vazgeç",
        "secici.olcu": "%d x %d piksel",
        "secici.bolge": "aranacak bölge: %d x %d piksel",

        # --- gunluk ---
        "kayit.hazir": "Hazır. F6 başlat · F8 veya Ctrl+T durdur · "
                       "F9 duraklat · F7 konum yakala.",
        "kayit.acil": "Acil durum: çalışırken ESC tuşunu basılı tutun.",
        "kayit.kisayol_uyari": "UYARI: Şu kısayollar başka bir program tarafından "
                              "kullanılıyor: %s",
        "kayit.adim_eklendi": "Adım eklendi (%d): %s",
        "kayit.adim_guncellendi": "Adım %d güncellendi: %s",
        "kayit.adim_silindi": "Adım silindi: %s",
        "kayit.liste_temizlendi": "Liste temizlendi.",
        "kayit.deneme": "Deneme: %s (2 sn sonra)",
        "kayit.deneme_hata": "Deneme başarısız: %s",
        "kayit.konum": "Konum yakalandı: (%d, %d)",
        "kayit.bolge_iptal": "Bölge seçimi iptal edildi.",
        "kayit.nokta_iptal": "Tıklama noktası seçimi iptal edildi.",
        "kayit.goruntu_alindi": "Görüntü yakalandı: %s (%dx%d px, bölge %d,%d) · "
                               "tıklama noktası %d,%d (ortadan %+d, %+d)",
        "kayit.nokta_guncel": "Tıklama noktası güncellendi: %d,%d (ortadan %+d, %+d)",
        "kayit.arama_yok": "Arama: '%s' ekranda bulunamadı (%.0f ms).",
        "kayit.arama_var": "Arama: '%s' bulundu → bölge (%d, %d) %dx%d, "
                          "tıklanacak nokta (%d, %d), %.0f ms",
        "kayit.baslatiliyor": "%d saniye içinde başlıyor - hedef pencereye geçin.",
        "kayit.baslatildi": "Başlatıldı - %s tur, %d aktif adım.",
        "kayit.sonsuz": "sonsuz",
        "kayit.baslatma_iptal": "Başlatma iptal edildi.",
        "kayit.duraklatildi": "Duraklatıldı.",
        "kayit.devam": "Devam ediliyor.",
        "kayit.bitti": "Çalışma bitti: %s",
        "kayit.yeni_liste": "Yeni liste oluşturuldu.",
        "kayit.acildi": "Açıldı: %s (%d adım)",
        "kayit.kaydedildi": "Kaydedildi: %s",
        "kayit.son_liste": "Son liste geri yüklendi: %s",
        "kayit.dil": "Dil değiştirildi: %s",

        # --- motor gunlukleri ---
        "motor.esc": "ESC algılandı - acil durduruldu.",
        "motor.goruntu_hata": "Görüntü aranamadı (%s): %s",
        "motor.hata": "HATA (adım %d): %s",
        "motor.bulunamadi": "Adım %d: '%s' görüntüsü ekranda bulunamadı - %s.",
        "motor.kosul_sonuc": "Koşul %s = %s  ('%s' ekranda %s)",
        "motor.aktif": "AKTİF",
        "motor.pasif": "pasif",
        "motor.bulundu": "bulundu",
        "motor.yok": "yok",
        "motor.adim_atlandi": "Adım %d atlandı (%s değil).",

        # --- bulunamazsa / kosul ---
        "bulunamazsa.durdur": "Çalışmayı durdur",
        "bulunamazsa.atla": "Adımı atla",
        "kosul.her_zaman": "Her zaman çalış",
        "kosul.aktifse": "%s aktifse",
        "kosul.pasifse": "%s pasifse",
        "kosul.belirle": "→ %s belirle",

        # --- dogrulama ---
        "hata.bilinmeyen_islem": "Bilinmeyen işlem türü: %s",
        "hata.tekrar": "Tekrar sayısı en az 1 olmalı.",
        "hata.bekleme": "Bekleme süresi negatif olamaz.",
        "hata.kosul_sart": "Geçersiz çalışma koşulu: %s",
        "hata.kosul_adi": "Koşul adı %s arasından seçilmeli.",
        "hata.yalniz_goruntu": "'%s' işlemi yalnızca görüntü hedefiyle kullanılabilir.",
        "hata.goruntu_yok": "Görüntü seçilmemiş. 'Bölge + Tıklama Noktası Seç' ile "
                           "bir alan yakalayın.",
        "hata.goruntu_dosya": "Görüntü dosyası bulunamadı: %s",
        "hata.tolerans": "Eşleşme toleransı 0-100 arasında olmalı.",
        "hata.arama_suresi": "Arama süresi negatif olamaz.",
        "hata.bulunamazsa": "Geçersiz 'bulunamazsa' davranışı.",
        "hata.tekerlek": "Tekerlek çentiği tam sayı olmalı (örn: 3 veya -3).",
        "hata.metin_bos": "Yazılacak metin boş.",

        # --- iletisim kutulari ---
        "kutu.gecersiz_baslik": "Geçersiz adım",
        "kutu.gecersiz_adim": "Adım %d: %s",
        "kutu.secim_yok_baslik": "Seçim yok",
        "kutu.secim_yok": "Önce listeden bir adım seçin.",
        "kutu.liste_bos_baslik": "Liste boş",
        "kutu.liste_bos": "Çalıştırılacak aktif adım yok.",
        "kutu.temizle_baslik": "Tümünü temizle",
        "kutu.temizle": "Listedeki %d adımın tamamı silinsin mi?",
        "kutu.goruntu_yok_baslik": "Görüntü yok",
        "kutu.goruntu_yok": "Önce 'Bölge + Tıklama Noktası Seç' ile bir alan yakalayın.",
        "kutu.alinamadi": "Görüntü alınamadı",
        "kutu.kaydedilemedi": "Görüntü kaydedilemedi",
        "kutu.arama_hata": "Arama başarısız",
        "kutu.bulunamadi_baslik": "Bulunamadı",
        "kutu.bulunamadi": "'%s' görüntüsü şu anda ekranda bulunamadı.\n\n"
                          "Hedef pencere açık mı? Tolerans değerini artırmayı deneyin.",
        "kutu.bolge_yok_baslik": "Bölge ekranda yok",
        "kutu.bolge_yok": "Tıklama noktasını seçebilmek için bölgenin şu anda ekranda "
                         "görünmesi gerekir.\n\nHedef pencereyi açıp tekrar deneyin.",
        "kutu.tanimsiz_baslik": "Tanımsız koşul",
        "kutu.tanimsiz": "Şu koşulları belirleyen bir 'Koşul (IF)' adımı yok: %s\n\n"
                        "Bu koşullar pasif sayılacağı için onlara bağlı adımlar hiç "
                        "çalışmayacak.\n\nYine de başlatılsın mı?",
        "kutu.yeni_baslik": "Yeni liste",
        "kutu.yeni": "Kaydedilmemiş değişiklikler var. Devam edilsin mi?",
        "kutu.acilamadi": "Açılamadı",
        "kutu.acilamadi_mesaj": "Dosya okunamadı:\n%s",
        "kutu.kayit_hata": "Kaydedilemedi",
        "kutu.calisiyor_baslik": "Çalışıyor",
        "kutu.calisiyor": "Otomasyon çalışıyor. Durdurulup çıkılsın mı?",
        "kutu.degisiklik_baslik": "Kaydedilmemiş değişiklik",
        "kutu.degisiklik": "Liste kaydedilsin mi?",
        "kutu.ac_baslik": "Adım listesi aç",
        "kutu.kaydet_baslik": "Adım listesini kaydet",
        "kutu.dosya_turu": "Tıklama listesi",
        "kutu.tum_dosyalar": "Tüm dosyalar",

        # --- yardim ---
        "yardim.baslik": "Kullanım",
        "yardim.metin": (
            "KISAYOLLAR (program arka planda olsa da çalışır)\n"
            "  F6     : Başlat / Durdur\n"
            "  F7     : İmlecin bulunduğu konumu forma yakala\n"
            "  F8     : Durdur\n"
            "  Ctrl+T : Durdur\n"
            "  F9     : Duraklat / Devam et\n"
            "  ESC    : Çalışırken basılı tutun - acil durdurma\n\n"
            "HIZLI LİSTE OLUŞTURMA\n"
            "  1. İşlem türünü seçin (örn. Sol Tık)\n"
            "  2. 'F7 basınca doğrudan listeye ekle' kutusunu işaretleyin\n"
            "  3. Fareyi hedefe götürüp F7'ye basın - adım eklenir\n\n"
            "GÖRÜNTÜ İLE HEDEFLEME (iki adımda)\n"
            "  Hedef = Görüntü seçip 'Bölge + Tıklama Noktası Seç'e basın:\n"
            "    1) Ekranda ARANACAK alanı fareyle çizin\n"
            "    2) Sonra TIKLANACAK noktayı fareyle işaretleyin\n"
            "       (Enter = bölgenin ortası, nokta bölge dışında da olabilir)\n"
            "  Program çalışırken o alanı ekranda arar ve işaretlediğiniz\n"
            "  noktaya tıklar; pencere yer değiştirse de doğru yeri bulur.\n"
            "  Önizlemede kırmızı nişan tıklanacak yeri gösterir.\n\n"
            "KOŞUL (IF) — ekranda şu varsa şunu yap\n"
            "  1. İşlem = 'Koşul (IF)' seçin, sonucu yazacağı yuvayı belirtin\n"
            "     (if1 … if6) ve aranacak görüntüyü yakalayın.\n"
            "  2. Çalıştığında o görüntü ekranda varsa yuva AKTİF, yoksa pasif olur.\n"
            "  3. Sonraki adımlarda 'Çalışma koşulu' kutusundan\n"
            "     'if1 aktifse' ya da 'if1 pasifse' seçin.\n"
            "  Koşullar her turun başında sıfırlanıp yeniden ölçülür.\n\n"
            "TUŞ YAZIMI (Tuşa Bas işlemi)\n"
            "  enter, tab, esc, space, f5, up, down, delete\n"
            "  ctrl+c, ctrl+shift+s, alt+f4, win+d\n\n"
            "TUR SAYISI\n"
            "  0 yazarsanız siz durdurana kadar sonsuz tekrar eder.\n\n"
            "Listeye çift tıklamak adımı aktif/pasif yapar."),
        "hakkinda.baslik": "Hakkında",
        "hakkinda.metin": (
            "%s v%s\n\n"
            "Windows SendInput API'si ile çalışan, harici kütüphane\n"
            "gerektirmeyen otomasyon aracı.\n\n"
            "Python %s · Tk %s\n"
            "DPI modu: %s"),
    },

    # ==================================================================== EN
    "en": {
        "uygulama.ad": "Auto Clicker",

        "menu.dosya": "File",
        "menu.yeni": "New List",
        "menu.ac": "Open...",
        "menu.kaydet": "Save",
        "menu.farkli_kaydet": "Save As...",
        "menu.cikis": "Exit",
        "menu.dil": "Dil / Language",
        "menu.yardim": "Help",
        "menu.kullanim": "Usage / Shortcuts",
        "menu.hakkinda": "About",

        "islem.sol_tik": "Left Click",
        "islem.sag_tik": "Right Click",
        "islem.cift_tik": "Double Click",
        "islem.orta_tik": "Middle Click",
        "islem.tasi": "Move Mouse",
        "islem.basili_tut": "Hold Left Button",
        "islem.birak": "Release Left Button",
        "islem.tekerlek": "Scroll Wheel",
        "islem.goruntu_bekle": "Wait For Image",
        "islem.kosul": "Condition (IF)",
        "islem.tus": "Press Key",
        "islem.metin": "Type Text",
        "islem.bekle": "Wait",

        "deger.tekerlek": "Notches (+up / -down)",
        "deger.tus": "Key (e.g. enter, ctrl+c, f5)",
        "deger.metin": "Text to type",
        "deger.yok": "Value (unused)",

        "form.baslik": " Add / Edit Step ",
        "form.islem": "Action",
        "form.sonucu_yaz": "Write result to",
        "form.yuvasina": "slot",
        "form.hedef": "Target",
        "form.koordinat": "Coordinate",
        "form.goruntu": "Image",
        "form.konum": "Position X / Y",
        "form.konum_yakala": "📍 Capture Position  (F7)",
        "form.geri_sayim": "⏱ Capture in 3 s",
        "form.geri_sayim_devam": "⏱ %d ...",
        "form.f7_ekle": "Add to list directly when F7 is pressed",
        "form.bolge_sec": "🖼 Select Region + Click Point",
        "form.nokta_sec": "🎯 Change Click Point Only",
        "form.tolerans": "Match tolerance (%)",
        "form.zaman_asimi": "Max search time (ms)",
        "form.kaydirma": "Click offset",
        "form.bulunamazsa": "If not found",
        "form.simdi_ara": "🔍 Search Screen Now",
        "form.kosul_sart": "Run condition",
        "form.tekrar": "Repeat",
        "form.bekleme": "Delay after (ms)",
        "form.not": "Note",
        "form.ekle": "➕ Add To List",
        "form.guncelle": "✎ Update Selected",

        "onizleme.yok": "No image selected yet",
        "onizleme.dosya_yok": "⚠ File not found:\n%s",
        "onizleme.hata": "Preview unavailable:\n%s",
        "onizleme.bilgi": "%s · %d x %d px\n🔴 click: %s",
        "onizleme.merkez": "at the exact center",
        "onizleme.kaydirma": "%+d, %+d from center",
        "onizleme.disarida": " (outside the region)",

        "liste.baslik": " Step List ",
        "liste.sira": "#",
        "liste.durum": "Active",
        "liste.islem": "Action",
        "liste.kosul": "Condition",
        "liste.hedef": "Target",
        "liste.deger": "Value",
        "liste.tekrar": "Repeat",
        "liste.bekleme": "Delay (ms)",
        "liste.not": "Note",
        "liste.ornek_islem": "Release Left Button",
        "liste.ornek_kosul": "→ set if1",
        "liste.ornek_deger": "ctrl+shift+s",
        "liste.yukari": "▲ Up",
        "liste.asagi": "▼ Down",
        "liste.cogalt": "⧉ Duplicate",
        "liste.aktiflik": "✓/✗ Toggle",
        "liste.sil": "🗑 Delete",
        "liste.temizle": "Clear All",
        "liste.dene": "▶ Test Selected",

        "cal.baslik": " Run ",
        "cal.tur": "Loop count",
        "cal.sonsuz": "(0 = endless)",
        "cal.tur_beklemesi": "Delay between loops (ms)",
        "cal.hazirlik": "Countdown before start (s)",
        "cal.konum_sapmasi": "Position jitter (px)",
        "cal.gecikme_sapmasi": "Delay jitter (%)",
        "cal.kucult": "Minimize window on start",
        "cal.baslat": "▶  START  (F6)",
        "cal.duraklat": "⏸ Pause (F9)",
        "cal.devam": "▶ Resume (F9)",
        "cal.durdur": "⏹ Stop (F8 / Ctrl+T)",
        "cal.gunluk": " Log ",

        "durum.beklemede": "Idle",
        "durum.calisiyor": "RUNNING",
        "durum.duraklatildi": "PAUSED",
        "durum.basliyor": "Starting...",
        "durum.basliyor_sayac": "Starting: %d",
        "durum.durduruluyor": "Stopping...",
        "durum.iptal": "Cancelled",
        "durum.tamamlandi": "Completed",
        "durum.durduruldu": "Stopped",
        "durum.bulunamadi": "Image not found",
        "durum.hata": "Stopped with error",
        "durum.imlec_bos": "Cursor: -",
        "durum.imlec": "Cursor:  X = %-6d Y = %-6d",
        "durum.kaydedilmemis": "Unsaved list",
        "durum.tur": "Loop %d/%s",
        "durum.adim": "%s · Step %d/%d · %s",

        "secici.asama1": "1/2  ·  Drag to mark the area to SEARCH FOR on screen",
        "secici.asama1_alt": "Cover the button, or the frame containing it"
                            "   ·   ESC = cancel",
        "secici.asama2": "2/2  ·  Now pick the point to CLICK",
        "secici.asama2_alt": "The point may be outside the region"
                            "   ·   Enter = center of region   ·   ESC = cancel",
        "secici.olcu": "%d x %d pixels",
        "secici.bolge": "search area: %d x %d pixels",

        "kayit.hazir": "Ready. F6 start · F8 or Ctrl+T stop · "
                       "F9 pause · F7 capture position.",
        "kayit.acil": "Emergency: hold the ESC key while running.",
        "kayit.kisayol_uyari": "WARNING: these shortcuts are taken by another "
                              "program: %s",
        "kayit.adim_eklendi": "Step added (%d): %s",
        "kayit.adim_guncellendi": "Step %d updated: %s",
        "kayit.adim_silindi": "Step deleted: %s",
        "kayit.liste_temizlendi": "List cleared.",
        "kayit.deneme": "Test: %s (in 2 s)",
        "kayit.deneme_hata": "Test failed: %s",
        "kayit.konum": "Position captured: (%d, %d)",
        "kayit.bolge_iptal": "Region selection cancelled.",
        "kayit.nokta_iptal": "Click point selection cancelled.",
        "kayit.goruntu_alindi": "Image captured: %s (%dx%d px, region %d,%d) · "
                               "click point %d,%d (%+d, %+d from center)",
        "kayit.nokta_guncel": "Click point updated: %d,%d (%+d, %+d from center)",
        "kayit.arama_yok": "Search: '%s' not found on screen (%.0f ms).",
        "kayit.arama_var": "Search: '%s' found → region (%d, %d) %dx%d, "
                          "click point (%d, %d), %.0f ms",
        "kayit.baslatiliyor": "Starting in %d seconds - switch to the target window.",
        "kayit.baslatildi": "Started - %s loops, %d active steps.",
        "kayit.sonsuz": "endless",
        "kayit.baslatma_iptal": "Start cancelled.",
        "kayit.duraklatildi": "Paused.",
        "kayit.devam": "Resumed.",
        "kayit.bitti": "Run finished: %s",
        "kayit.yeni_liste": "New list created.",
        "kayit.acildi": "Opened: %s (%d steps)",
        "kayit.kaydedildi": "Saved: %s",
        "kayit.son_liste": "Last list restored: %s",
        "kayit.dil": "Language changed: %s",

        "motor.esc": "ESC detected - emergency stop.",
        "motor.goruntu_hata": "Image search failed (%s): %s",
        "motor.hata": "ERROR (step %d): %s",
        "motor.bulunamadi": "Step %d: image '%s' not found on screen - %s.",
        "motor.kosul_sonuc": "Condition %s = %s  ('%s' %s on screen)",
        "motor.aktif": "ACTIVE",
        "motor.pasif": "inactive",
        "motor.bulundu": "found",
        "motor.yok": "not found",
        "motor.adim_atlandi": "Step %d skipped (not %s).",

        "bulunamazsa.durdur": "Stop the run",
        "bulunamazsa.atla": "Skip the step",
        "kosul.her_zaman": "Always run",
        "kosul.aktifse": "if %s is active",
        "kosul.pasifse": "if %s is inactive",
        "kosul.belirle": "→ set %s",

        "hata.bilinmeyen_islem": "Unknown action type: %s",
        "hata.tekrar": "Repeat count must be at least 1.",
        "hata.bekleme": "Delay cannot be negative.",
        "hata.kosul_sart": "Invalid run condition: %s",
        "hata.kosul_adi": "Condition slot must be one of %s.",
        "hata.yalniz_goruntu": "'%s' can only be used with an image target.",
        "hata.goruntu_yok": "No image selected. Capture an area with "
                           "'Select Region + Click Point'.",
        "hata.goruntu_dosya": "Image file not found: %s",
        "hata.tolerans": "Match tolerance must be between 0 and 100.",
        "hata.arama_suresi": "Search time cannot be negative.",
        "hata.bulunamazsa": "Invalid 'if not found' behaviour.",
        "hata.tekerlek": "Scroll notches must be a whole number (e.g. 3 or -3).",
        "hata.metin_bos": "Text to type is empty.",

        "kutu.gecersiz_baslik": "Invalid step",
        "kutu.gecersiz_adim": "Step %d: %s",
        "kutu.secim_yok_baslik": "Nothing selected",
        "kutu.secim_yok": "Select a step from the list first.",
        "kutu.liste_bos_baslik": "List is empty",
        "kutu.liste_bos": "There are no active steps to run.",
        "kutu.temizle_baslik": "Clear all",
        "kutu.temizle": "Delete all %d steps in the list?",
        "kutu.goruntu_yok_baslik": "No image",
        "kutu.goruntu_yok": "Capture an area with 'Select Region + Click Point' first.",
        "kutu.alinamadi": "Could not capture image",
        "kutu.kaydedilemedi": "Could not save image",
        "kutu.arama_hata": "Search failed",
        "kutu.bulunamadi_baslik": "Not found",
        "kutu.bulunamadi": "Image '%s' is not on the screen right now.\n\n"
                          "Is the target window open? Try increasing the tolerance.",
        "kutu.bolge_yok_baslik": "Region not on screen",
        "kutu.bolge_yok": "The region must be visible on screen to pick a click "
                         "point.\n\nOpen the target window and try again.",
        "kutu.tanimsiz_baslik": "Undefined condition",
        "kutu.tanimsiz": "No 'Condition (IF)' step sets these conditions: %s\n\n"
                        "They will count as inactive, so steps bound to them will "
                        "never run.\n\nStart anyway?",
        "kutu.yeni_baslik": "New list",
        "kutu.yeni": "There are unsaved changes. Continue?",
        "kutu.acilamadi": "Could not open",
        "kutu.acilamadi_mesaj": "File could not be read:\n%s",
        "kutu.kayit_hata": "Could not save",
        "kutu.calisiyor_baslik": "Running",
        "kutu.calisiyor": "Automation is running. Stop it and quit?",
        "kutu.degisiklik_baslik": "Unsaved changes",
        "kutu.degisiklik": "Save the list?",
        "kutu.ac_baslik": "Open step list",
        "kutu.kaydet_baslik": "Save step list",
        "kutu.dosya_turu": "Click list",
        "kutu.tum_dosyalar": "All files",

        "yardim.baslik": "Usage",
        "yardim.metin": (
            "SHORTCUTS (work even when the program is in the background)\n"
            "  F6     : Start / Stop\n"
            "  F7     : Capture the current cursor position into the form\n"
            "  F8     : Stop\n"
            "  Ctrl+T : Stop\n"
            "  F9     : Pause / Resume\n"
            "  ESC    : Hold it down while running - emergency stop\n\n"
            "BUILDING A LIST QUICKLY\n"
            "  1. Pick an action type (e.g. Left Click)\n"
            "  2. Tick 'Add to list directly when F7 is pressed'\n"
            "  3. Move the mouse to the target and press F7 - a step is added\n\n"
            "TARGETING BY IMAGE (two steps)\n"
            "  Set Target = Image and press 'Select Region + Click Point':\n"
            "    1) Drag to mark the area to SEARCH FOR on screen\n"
            "    2) Then mark the point to CLICK\n"
            "       (Enter = center of the region; the point may be outside it)\n"
            "  While running, the program looks for that area on screen and\n"
            "  clicks the point you marked - even if the window has moved.\n"
            "  The red crosshair in the preview shows where it will click.\n\n"
            "CONDITION (IF) — do this if that is on screen\n"
            "  1. Pick Action = 'Condition (IF)', choose the slot to write to\n"
            "     (if1 … if6) and capture the image to look for.\n"
            "  2. When it runs, the slot becomes ACTIVE if the image is on\n"
            "     screen, inactive otherwise.\n"
            "  3. In later steps use the 'Run condition' box to pick\n"
            "     'if if1 is active' or 'if if1 is inactive'.\n"
            "  Conditions are reset and re-measured at the start of every loop.\n\n"
            "KEY SYNTAX (Press Key action)\n"
            "  enter, tab, esc, space, f5, up, down, delete\n"
            "  ctrl+c, ctrl+shift+s, alt+f4, win+d\n\n"
            "LOOP COUNT\n"
            "  Enter 0 to repeat endlessly until you stop it.\n\n"
            "Double-clicking a row toggles that step active/inactive."),
        "hakkinda.baslik": "About",
        "hakkinda.metin": (
            "%s v%s\n\n"
            "Automation tool built on the Windows SendInput API,\n"
            "with no external dependencies.\n\n"
            "Python %s · Tk %s\n"
            "DPI mode: %s"),
    },
}
