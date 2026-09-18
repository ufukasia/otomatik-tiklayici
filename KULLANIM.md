# Auto Clicker / Otomatik Tıklayıcı — Kullanım Kılavuzu

Ekranın belirlediğiniz noktalarına, verdiğiniz sırayla ve sürelerle sol/sağ/çift tık
yapan; tuş kombinasyonu gönderen ve metin yazan Windows programı.
**Hiçbir kurulum gerekmez** — yalnızca Python'un kendisi yeterlidir (harici kütüphane yok).

## Çalıştırma

İşlemcinize uyan exe dosyasına **çift tıklayın**. Python kurulu olması gerekmez;
tek dosyadır, kurulum istemez.

| Dosya | Hangi bilgisayarda |
|---|---|
| `Otomatik Tiklayici (x64).exe` | Intel / AMD işlemcili Windows *(çoğu bilgisayar)* |
| `Otomatik Tiklayici (ARM64).exe` | Snapdragon / ARM işlemcili Windows |

Hangisi olduğunu bilmiyorsanız: **Ayarlar → Sistem → Hakkında → Sistem türü**.
Yanlışını çalıştırırsanız Windows "bu uygulama bu bilgisayarda çalışmıyor" der,
bir zarar vermez.

Kaynak koddan çalıştırmak isterseniz `Otomatik Tiklayici.bat` (veya
`python otomatik_tiklayici.py`) da aynı programı açar.

### Exe'yi başka bilgisayara taşıma

Exe'yi tek başına kopyalayabilirsiniz; ayarlarını ve şablonlarını **kendi
bulunduğu klasöre** yazar. Görüntü hedefli adımlarınız varsa `goruntuler`
klasörünü de yanında götürün, yoksa şablonlar bulunamaz.

### Yeniden derleme

Kodda değişiklik yaptıktan sonra:

```
python -m pip install pyinstaller      (bir kez)
python exe_yap.py
```

Üretilen exe, derlemeyi yapan Python'un mimarisini taşır ve dosya adına o
mimari yazılır. İki sürümü de üretmek için her iki mimarideki Python ile
ayrı ayrı çalıştırın:

```
py -3.11        exe_yap.py     ->  Otomatik Tiklayici (x64).exe
py -3.14-arm64  exe_yap.py     ->  Otomatik Tiklayici (ARM64).exe
```

Derleme sırasında exe'nin kapalı olması gerekir.

## Dil

Menüden **Dil / Language → Türkçe** veya **English** seçin. Arayüz anında o
dile geçer; açık listeniz, seçiminiz ve formdaki adım korunur. Tercih
kaydedilir, program bir sonraki açılışta aynı dille başlar.

Listeler dilden bağımsızdır: `.json` dosyalarına iç kodlar yazılır, bu yüzden
Türkçe kaydettiğiniz bir listeyi İngilizce arayüzde açabilirsiniz.

## Kısayol tuşları

Bu tuşlar program arka planda veya küçültülmüş olsa da çalışır:

| Tuş | İşlev |
|-----|-------|
| **F6** | Başlat / Durdur |
| **F7** | İmlecin bulunduğu konumu forma yakala |
| **F8** | Durdur |
| **Ctrl + T** | Durdur |
| **F9** | Duraklat / Devam et |
| **ESC** *(basılı tutun)* | Acil durdurma — çalışma sırasında her an |

## Hızlı liste oluşturma

1. Sol taraftaki **İşlem** kutusundan işlem türünü seçin (örn. `Sol Tık`).
2. **"F7 basınca doğrudan listeye ekle"** kutusunu işaretleyin.
3. Fareyi hedef noktaya götürüp **F7**'ye basın — adım listeye eklenir.
4. Her nokta için 3. adımı tekrarlayın.

Kutuyu işaretlemezseniz F7 yalnızca X/Y alanlarını doldurur; **Listeye Ekle**
düğmesiyle eklersiniz. `⏱ 3 sn Sonra Yakala` düğmesi, kısayol kullanamadığınız
durumlar için geri sayımla konum alır.

## Görüntü ile hedefleme (koordinat yerine)

Her tıklama adımı hedefini iki yoldan biriyle belirtir:

- **Koordinat** — sabit bir X/Y noktası. Pencere hep aynı yerdeyse en hızlısı.
- **Görüntü** — ekranda aranan bir kare. Program o kareyi bulur ve
  **bulduğu yerin ortasına** tıklar. Pencere yer değiştirse de çalışır.

![Bölge seçimi ve tıklama noktası](demo.gif)

Kullanımı — **iki adımda, ikisi de fareyle**:

1. Formda **Hedef → Görüntü** seçin.
2. **🖼 Bölge + Tıklama Noktası Seç**'e basın. Ekran kararır ve:
   - **1/2 · Aranacak alanı çizin** — ekranda aranacak kareyi sürükleyerek
     belirleyin (kaç piksel seçtiğiniz anlık görünür).
   - **2/2 · Tıklanacak noktayı seçin** — seçtiğiniz kare yeşil kesik çizgiyle
     sabit kalır, fareyi gezdirdikçe kırmızı nişan sizi takip eder.
     **Tıkladığınız yer, tıklanacak nokta olur.**
     `Enter` = karenin tam ortası · `ESC` = vazgeç
3. Formdaki önizlemede yakalanan kare ve üzerinde **kırmızı nişan** görünür —
   program çalışınca tam oraya tıklayacaktır.
4. **🔍 Şimdi Ekranda Ara** ile test edin: bulunursa fare o noktaya gider.

Nokta karenin **dışında** da olabilir: bir başlığı/simgeyi arayıp yanındaki
butona tıklatmak için işe yarar (önizlemede nişan turuncuya döner).

Sonradan yalnızca noktayı değiştirmek isterseniz **🎯 Yalnızca Tıklama Noktasını
Değiştir**'e basın; program kareyi ekranda bulur, üzerinde gösterir ve yeni
noktayı seçmenizi ister — kareyi yeniden çizmeniz gerekmez.

| Ayar | Anlamı |
|------|--------|
| **Eşleşme toleransı (%)** | Kaç piksele kadar farklılığa izin verilsin. `0` = birebir aynı olmalı. Gölge/animasyon varsa 5–15 deneyin. |
| **En fazla arama (ms)** | Görüntü henüz ekranda yoksa ne kadar beklenip aranmaya devam edilsin. `0` = bir kez bak, bekleme. |
| **Tıklama kayması** | Karenin ortasına göre kaç piksel sapılacağı. Nokta seçimiyle kendiliğinden dolar; istersen elle de yazabilirsin. |
| **Bulunamazsa** | `Çalışmayı durdur` veya `Adımı atla`. Bazen çıkan bir uyarı penceresini kapatmak için `Adımı atla` uygundur. |

## Koşul — "ekranda şu yazı varsa bu adımı yap"

Her adıma **isteğe bağlı** bir koşul verebilirsiniz. Hiç dokunmazsanız adım her
zaman çalışır; ayrı bir koşul adımı eklemeniz veya yuva takip etmeniz gerekmez.

Formdaki **Koşul — isteğe bağlı** kutusundan seçim yapın:

| Seçenek | Anlamı |
|---|---|
| `Koşulsuz çalış` | varsayılan — adım her zaman çalışır |
| `Şu görüntü ekranda VARSA çalış` | koşul görüntüsü bulunursa çalışır |
| `Şu görüntü ekranda YOKSA çalış` | koşul görüntüsü bulunamazsa çalışır |

Bir koşul seçtiğinizde alanlar açılır:

1. **🔍 Koşul Görüntüsü Seç** — ekran kararır, aranacak yazının/işaretin
   çevresine bir kare çizersiniz. **Burada tıklama noktası sorulmaz**; bu alan
   yalnızca aranır, üzerine tıklanmaz.
2. **Koşul toleransı (%)** — koşul aranırken kaç piksel farka izin verilsin.
3. **Koşul araması (ms)** — koşul görüntüsü henüz yoksa ne kadar beklenip
   aranmaya devam edilsin. `0` = bir kez bak, bekleme.
4. **Koşulu Şimdi Dene** — koşulun şu anda sağlanıp sağlanmadığını söyler.
   Listeyi kurarken bununla doğrulayın.

Adımın **kendi hedefi** (tıklayacağı yer) bundan bağımsızdır: koşul ekranın bir
yerindeki yazı, tıklama başka bir yerdeki düğme olabilir.

Koşulu tutmayan adım o turda atlanır ve günlüğe yazılır. Listedeki **Koşul**
sütunu her adımın yanında bunu gösterir (`🔍 onay.png varsa` gibi); koşulsuz
adımlarda boş kalır. Koşullar her turda yeniden ölçülür.

> **Örnek:** "Ekranda *Öğrenci onayladı* yazıyorsa Onayla düğmesine bas."
> 1. `Sol Tık` · hedef: Onayla düğmesi
> 2. Aynı adımda Koşul = `Şu görüntü ekranda VARSA çalış`
> 3. `Koşul Görüntüsü Seç` → *Öğrenci onayladı* yazısının çevresini çiz
>
> Yazı ekranda yoksa o tur bu adım atlanır, liste kalanıyla devam eder.

## İşlem türleri

| İşlem | Hedef | Değer alanı |
|-------|:-----:|-------------|
| Sol Tık / Sağ Tık / Çift Tık / Orta Tık | koordinat veya görüntü | — |
| Fareyi Taşı *(tıklamadan)* | koordinat veya görüntü | — |
| Sol Tuşu Basılı Tut / Sol Tuşu Bırak | koordinat veya görüntü | — |
| Tekerlek Kaydır | koordinat veya görüntü | Çentik: `3` yukarı, `-3` aşağı |
| **Görüntüyü Bekle** | yalnızca görüntü | — |
| Tuşa Bas | — | `enter`, `f5`, `ctrl+c`, `alt+f4` … |
| Metin Yaz | — | Yazılacak metin (Türkçe karakter destekli) |
| Bekle | — | — |

**Görüntüyü Bekle**, bir pencerenin/butonun ekranda belirmesini bekler ama
tıklamaz. "Sayfa yüklenene kadar bekle, sonra tıkla" gibi akışlar için
tıklama adımından önce koyun.

**Sürükle-bırak** için üç adım kullanın:
`Sol Tuşu Basılı Tut` → `Fareyi Taşı` → `Sol Tuşu Bırak`

### Tuş yazımı

Tek tuş: `enter`, `tab`, `esc`, `space`, `backspace`, `delete`, `home`, `end`,
`up` / `yukari`, `down` / `asagi`, `left` / `sol`, `right` / `sag`, `f1`–`f12`,
`a`–`z`, `0`–`9`, `num0`–`num9`

Kombinasyon: `ctrl+c`, `ctrl+shift+s`, `alt+f4`, `win+d`, `ctrl+alt+delete`

## Adım ayarları

- **Tekrar** — o adım, aynı turda arka arkaya kaç kez yapılsın.
- **Sonra bekle (ms)** — adım bittikten sonraki duraklama (1000 ms = 1 saniye).
- **Not** — kendi hatırlatmanız; çalışmayı etkilemez.

## Çalıştırma ayarları

- **Tur sayısı** — listenin baştan sona kaç kez tekrarlanacağı.
  **`0` yazarsanız siz durdurana kadar sonsuz döner.**
- **Tur arası bekleme (ms)** — her turun sonunda beklenecek süre.
- **Başlamadan önce (sn)** — Başlat'a bastıktan sonraki geri sayım; bu sürede
  hedef pencereye geçersiniz.
- **Konum sapması (px)** — her tıklama, verilen noktanın ±bu kadar pikselinde
  rastgele bir yere yapılır. `0` = tam olarak verilen noktaya.
- **Gecikme sapması (%)** — bekleme sürelerini ±bu oranda rastgele değiştirir.
- **Başlayınca pencereyi küçült** — program kendini simge durumuna küçültür.

## Liste yönetimi

- Listedeki bir satıra **çift tıklamak** o adımı aktif/pasif yapar
  (pasif adımlar gri görünür ve çalıştırılmaz).
- `▲ Yukarı` / `▼ Aşağı` ile sırayı değiştirin, `⧉ Çoğalt` ile kopyalayın.
- `▶ Seçiliyi Dene` seçili adımı 2 saniye sonra bir kez çalıştırır —
  koordinatı doğrulamak için kullanışlıdır.
- **Dosya → Kaydet** listeyi `.json` olarak saklar; program bir sonraki
  açılışta son listeyi kendiliğinden geri yükler.

## Bilinmesi gerekenler

- Tıklamalar **imlecin o an bulunduğu ekran noktasına**, tuşlar ise **o an öndeki
  (odaklı) pencereye** gider. Çalışma sırasında başka bir pencereye tıklarsanız
  adımlar oraya uygulanır.
- Koordinatlar ekran çözünürlüğüne bağlıdır. Çözünürlüğü veya ölçeklemeyi
  (%125, %150) değiştirirseniz noktaları yeniden yakalamanız gerekir.
- Yönetici olarak çalışan pencerelere (örn. Görev Yöneticisi) girdi göndermek
  için programı da yönetici olarak başlatmanız gerekir.
- F6–F9 tuşlarını başka bir program kapmışsa, günlük bölümünde uyarı görürsünüz;
  o durumda ekrandaki düğmeleri kullanın.
- **Ctrl+T**, program açıkken sistem genelinde bu programa ayrılır; bu sürede
  tarayıcıda yeni sekme açmaz. Programı kapatınca normale döner.

## Dosyalar

| Dosya | İçerik |
|-------|--------|
| `Otomatik Tiklayici (x64).exe` | Çalıştırılabilir program — Intel/AMD |
| `Otomatik Tiklayici (ARM64).exe` | Çalıştırılabilir program — ARM |
| `exe_yap.py` | Exe'yi yeniden derleyen betik |
| `simge.ico` | Uygulama simgesi |
| `otomatik_tiklayici.py` | Arayüz ve program akışı |
| `motor.py` | Adım listesini çalıştıran motor |
| `winput.py` | Windows fare/klavye girdi katmanı (SendInput) |
| `ekran.py` | Ekran yakalama, PNG okuma/yazma, görüntü arama |
| `kisayol.py` | Sistem genelinde kısayol tuşları |
| `goruntuler/` | Yakalanan şablon görüntüleri (kendiliğinden oluşur) |
| `ayarlar.json` | Son kullanılan ayarlar (kendiliğinden oluşur) |

Listeyi başka bir bilgisayara taşırken `goruntuler` klasörünü de götürün;
görüntü hedefli adımlar şablon dosyalarını oradan okur.
