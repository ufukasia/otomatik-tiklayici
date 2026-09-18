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
        "form.kosul_baslik": " Koşul — isteğe bağlı ",
        "form.kosul_goruntu_sec": "🔍 Koşul Görüntüsü Seç",
        "form.kosul_dene": "Koşulu Şimdi Dene",
        "form.kosul_tolerans": "Koşul toleransı (%)",
        "form.kosul_zaman": "Koşul araması (ms)",
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
        "liste.ornek_kosul": "🔍 sablon_260101_120000.png yoksa",
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
        "secici.kosul": "Ekranda ARANACAK koşul alanını fareyle çizin",
        "secici.kosul_alt": "Bu alan ekranda görünüyorsa adım çalışır"
                           "   ·   burada tıklama noktası sorulmaz"
                           "   ·   ESC = vazgeç",
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
        "kayit.kosul_alindi": "Koşul görüntüsü yakalandı: %s (%dx%d px, bölge %d,%d)",
        "kayit.eski_kosul": "Eski sürümün %d koşul adımı kaldırıldı; koşullar artık her adımın kendi içinde.",
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
        "motor.kosul_var_tamam": "Adım %d: koşul sağlandı — '%s' ekranda bulundu.",
        "motor.kosul_var_atla": "Adım %d atlandı — '%s' ekranda bulunamadı.",
        "motor.kosul_yok_tamam": "Adım %d: koşul sağlandı — '%s' ekranda yok.",
        "motor.kosul_yok_atla": "Adım %d atlandı — '%s' ekranda duruyor.",

        # --- bulunamazsa / kosul ---
        "bulunamazsa.durdur": "Çalışmayı durdur",
        "bulunamazsa.atla": "Adımı atla",
        "kosul.tur_": "Koşulsuz çalış",
        "kosul.tur_var": "Şu görüntü ekranda VARSA çalış",
        "kosul.tur_yok": "Şu görüntü ekranda YOKSA çalış",
        "kosul.liste_var": "🔍 %s varsa",
        "kosul.liste_yok": "🔍 %s yoksa",
        "kosul.onizleme_yok": "Koşul görüntüsü seçilmedi",
        "kosul.onizleme": "%s · %d x %d px",

        # --- dogrulama ---
        "hata.bilinmeyen_islem": "Bilinmeyen işlem türü: %s",
        "hata.tekrar": "Tekrar sayısı en az 1 olmalı.",
        "hata.bekleme": "Bekleme süresi negatif olamaz.",
        "hata.kosul_turu": "Geçersiz koşul türü: %s",
        "hata.kosul_goruntu_yok": "Koşul seçtiniz ama koşul görüntüsü yok. "
                                 "'Koşul Görüntüsü Seç' ile ekranda aranacak "
                                 "alanı yakalayın.",
        "hata.kosul_goruntu_dosya": "Koşul görüntüsü bulunamadı: %s",
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
        "kutu.kosul_yok_baslik": "Koşul görüntüsü yok",
        "kutu.kosul_yok": "Önce 'Koşul Görüntüsü Seç' ile ekranda aranacak alanı "
                         "yakalayın.",
        "kutu.kosul_var_baslik": "Koşul sağlanıyor",
        "kutu.kosul_var": "'%s' şu anda ekranda görünüyor.\n\n"
                         "Bu koşulla adım çalışır.",
        "kutu.kosul_yok_simdi_baslik": "Koşul sağlanmıyor",
        "kutu.kosul_yok_simdi": "'%s' şu anda ekranda bulunamadı.\n\n"
                               "Hedef pencere açık mı? Tolerans değerini "
                               "artırmayı deneyin.",
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
            "KOŞUL — ekranda şu yazı/görüntü varsa bu adımı yap\n"
            "  İsteğe bağlıdır; hiç dokunmazsanız adım her zaman çalışır.\n"
            "  1. Formdaki 'Koşul' kutusundan 'Şu görüntü ekranda VARSA çalış'\n"
            "     (ya da YOKSA) seçin.\n"
            "  2. 'Koşul Görüntüsü Seç' ile o yazının çevresine bir kare çizin.\n"
            "     Burada tıklama noktası sorulmaz - bu alan yalnızca aranır.\n"
            "  3. Adımın kendi hedefi (tıklayacağı yer) ayrıdır ve değişmez.\n"
            "  Koşul tutmazsa adım o turda atlanır, günlüğe yazılır.\n"
            "  'Koşulu Şimdi Dene' ile koşulun şu an sağlanıp sağlanmadığını görün.\n\n"
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
        "islem.tus": "Press Key",
        "islem.metin": "Type Text",
        "islem.bekle": "Wait",

        "deger.tekerlek": "Notches (+up / -down)",
        "deger.tus": "Key (e.g. enter, ctrl+c, f5)",
        "deger.metin": "Text to type",
        "deger.yok": "Value (unused)",

        "form.baslik": " Add / Edit Step ",
        "form.islem": "Action",
        "form.kosul_baslik": " Condition — optional ",
        "form.kosul_goruntu_sec": "🔍 Pick Condition Image",
        "form.kosul_dene": "Test Condition Now",
        "form.kosul_tolerans": "Condition tolerance (%)",
        "form.kosul_zaman": "Condition search (ms)",
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
        "liste.ornek_kosul": "🔍 if no sablon_260101_120000.png",
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
        "secici.kosul": "Drag the CONDITION area to look for on screen",
        "secici.kosul_alt": "The step runs when this area is on screen"
                           "   ·   no click point is asked here"
                           "   ·   ESC = cancel",
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
        "kayit.kosul_alindi": "Condition image captured: %s (%dx%d px, region %d,%d)",
        "kayit.eski_kosul": "%d condition step(s) from the old version were dropped; conditions now live inside each step.",
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
        "motor.kosul_var_tamam": "Step %d: condition met — '%s' found on screen.",
        "motor.kosul_var_atla": "Step %d skipped — '%s' not found on screen.",
        "motor.kosul_yok_tamam": "Step %d: condition met — '%s' is not on screen.",
        "motor.kosul_yok_atla": "Step %d skipped — '%s' is still on screen.",

        "bulunamazsa.durdur": "Stop the run",
        "bulunamazsa.atla": "Skip the step",
        "kosul.tur_": "Always run",
        "kosul.tur_var": "Run if this image IS on screen",
        "kosul.tur_yok": "Run if this image is NOT on screen",
        "kosul.liste_var": "🔍 if %s",
        "kosul.liste_yok": "🔍 if no %s",
        "kosul.onizleme_yok": "No condition image selected",
        "kosul.onizleme": "%s · %d x %d px",

        "hata.bilinmeyen_islem": "Unknown action type: %s",
        "hata.tekrar": "Repeat count must be at least 1.",
        "hata.bekleme": "Delay cannot be negative.",
        "hata.kosul_turu": "Invalid condition type: %s",
        "hata.kosul_goruntu_yok": "You picked a condition but no condition image. "
                                 "Use 'Pick Condition Image' to capture the area "
                                 "to look for.",
        "hata.kosul_goruntu_dosya": "Condition image not found: %s",
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
        "kutu.kosul_yok_baslik": "No condition image",
        "kutu.kosul_yok": "Use 'Pick Condition Image' first to capture the area to "
                         "look for.",
        "kutu.kosul_var_baslik": "Condition is met",
        "kutu.kosul_var": "'%s' is on screen right now.\n\n"
                         "With this condition the step would run.",
        "kutu.kosul_yok_simdi_baslik": "Condition is not met",
        "kutu.kosul_yok_simdi": "'%s' is not on screen right now.\n\n"
                               "Is the target window open? Try increasing the "
                               "tolerance.",
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
            "CONDITION — run this step only if something is on screen\n"
            "  Optional; leave it alone and the step always runs.\n"
            "  1. In the 'Condition' box pick 'Run if this image IS on screen'\n"
            "     (or is NOT).\n"
            "  2. Press 'Pick Condition Image' and drag a box around that text.\n"
            "     No click point is asked for - this area is only searched.\n"
            "  3. The step's own target (what it clicks) stays separate.\n"
            "  If the condition does not hold, the step is skipped for that loop\n"
            "  and it is written to the log.\n"
            "  'Test Condition Now' shows whether the condition holds right now.\n\n"
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
