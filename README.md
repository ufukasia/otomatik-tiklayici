# Auto Clicker / Otomatik Tıklayıcı

![Auto Clicker — bölge seç, tıklanacak noktayı işaretle, program onu bulup tıklasın](demo.gif)

Windows için otomatik fare ve klavye aracı. Ekranın belirlediğiniz noktalarına
verdiğiniz sırayla ve sürelerle tıklar, tuş gönderir, metin yazar — ve
isterseniz **hedefi koordinatla değil, ekranda aradığı bir görüntüyle** bulur.

Arayüz **Türkçe ve İngilizce** (Dil / Language menüsü).

*English: [README.en.md](README.en.md)*

**Kurulum gerektirmez.** Harici Python kütüphanesi kullanılmaz: fare/klavye
girişi Windows `SendInput` API'sine, ekran yakalama GDI'ya, PNG okuma/yazma
`zlib`'e dayanır — hepsi `ctypes` ve standart kütüphaneyle.

## İndir

[Sürümler sayfasından](../../releases/latest) işlemcinize uyanı indirin:

| Dosya | Hangi bilgisayarda |
|---|---|
| `Otomatik Tiklayici (x64).exe` | Intel / AMD işlemcili Windows *(çoğu bilgisayar)* |
| `Otomatik Tiklayici (ARM64).exe` | Snapdragon / ARM işlemcili Windows |

Tek dosyadır; çift tıklayıp çalıştırırsınız. Ayarlarını ve yakaladığı
görüntüleri kendi bulunduğu klasöre yazar.

> Windows SmartScreen ilk açılışta "bilinmeyen yayımcı" uyarısı verebilir
> (imzasız bir exe olduğu için normaldir): **Daha fazla bilgi → Yine de çalıştır**.

## Ne yapar

- **Sıralı adım listesi** — sol/sağ/orta/çift tık, fareyi taşı, basılı tut/bırak,
  tekerlek, tuş kombinasyonu (`ctrl+shift+s`), metin yazma, bekleme.
  Her adımın kendi tekrar sayısı ve sonrasında bekleme süresi var.
- **Tur sayısı** — listeyi kaç kez tekrarlayacağı; `0` yazarsanız siz durdurana
  kadar sonsuz döner.
- **Görüntüyle hedefleme** — ekranı karartıp fareyle bir kare çizersiniz, sonra
  **tıklanacak noktayı** işaretlersiniz. Program çalışırken o kareyi ekranda
  arar ve işaretlediğiniz noktaya tıklar; pencere yer değiştirse de bulur.
- **Koşul** — "ekranda şu yazı varsa bu adımı yap". Her adıma isteğe bağlı bir
  *koşul görüntüsü* verirsiniz: o alan ekranda varsa (ya da yoksa) adım çalışır,
  yoksa atlanır. Koşul alanı yalnızca aranır, tıklanmaz; adımın tıklayacağı
  hedef ayrıdır.
- **Görüntüyü Bekle** — bir pencere/buton belirene kadar bekler, tıklamaz.
- **Sistem geneli kısayollar** — program arka plandayken de çalışır:
  `F6` başlat/durdur · `F7` konum yakala · `F8` veya `Ctrl+T` durdur ·
  `F9` duraklat · çalışırken **ESC basılı tutmak acil durdurur**.
- **İnsan benzeri sapma** — tıklama noktasına ±piksel, bekleme sürelerine
  ±yüzde rastgelelik verilebilir.
- Listeler `.json` olarak kaydedilir; program son listeyi açılışta geri yükler.

Ayrıntılı kullanım: **[KULLANIM.md](KULLANIM.md)**

## Kaynak koddan çalıştırma

Python 3.8+ ve Windows yeterlidir, başka bir şey gerekmez:

```
python otomatik_tiklayici.py
```

### Exe derleme

```
python -m pip install pyinstaller
python exe_yap.py
```

Üretilen exe, derlemeyi yapan Python'un mimarisini taşır ve adına o mimari
yazılır (`Otomatik Tiklayici (x64).exe` gibi). İki sürümü de üretmek için her
iki mimarideki Python ile ayrı ayrı çalıştırın.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `otomatik_tiklayici.py` | Tkinter arayüzü, bölge/nokta seçici, program akışı |
| `motor.py` | Adım listesini çalıştıran motor, koşul mantığı |
| `winput.py` | Windows fare/klavye girdi katmanı (`SendInput`) |
| `ekran.py` | Ekran yakalama (GDI), PNG okuma/yazma, şablon arama |
| `kisayol.py` | Sistem geneli kısayol tuşları (`RegisterHotKey`) |
| `diller.py` | Arayüz metinleri (Türkçe / İngilizce) |
| `exe_yap.py` | PyInstaller ile exe üretir |
| `gif_yap.py` | Yukarıdaki tanıtım GIF'ini programı çalıştırarak üretir |

## Nasıl çalışıyor

**Görüntü arama** harici bir görüntü işleme kütüphanesi olmadan yapılır:
ekran GDI `BitBlt` ile ham BGRA tamponuna alınır, şablondan en ayırt edici
yatay piksel dizisi seçilip tampon içinde `bytes.find` ile taranır, aday
konumlar satır satır doğrulanır. 6720×2167'lik bir sanal masaüstünde yakalama
~180 ms, tam ekran arama ~170 ms sürer.

**Koordinatlar fiziksel pikseldir.** Program başlarken per-monitor DPI
farkındalığı açılır, böylece %125/%150 ölçeklemede noktalar kaymaz. Arayüzün
sütun genişlikleri ve satır yükseklikleri de ekranın gerçek yazı ölçüsünden
hesaplanır.

## Sınırlar

- Yalnızca **Windows**.
- Yönetici yetkisiyle açılmış pencerelere (ör. Görev Yöneticisi) girdi
  göndermek için programı da yönetici olarak başlatmak gerekir.
- Koordinatlar ekran çözünürlüğüne bağlıdır; çözünürlük veya ölçekleme
  değişirse noktaları yeniden yakalamak gerekir. Görüntü hedefleme bu konuda
  daha dayanıklıdır ama şablon da aynı ölçekte yakalanmış olmalıdır.
- `Ctrl+T` program açıkken sistem genelinde bu programa ayrılır; o sırada
  tarayıcıda yeni sekme açmaz.
