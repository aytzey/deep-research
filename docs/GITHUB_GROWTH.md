# GitHub büyüme kararı — 7 Eylül 2026

AMAÇ: Paper Pilot'ın daha fazla kişi tarafından bulunması, denenmesi ve yıldızlanması.
İlk kitle: zaten Codex veya Claude kullanan, bir teknik karar için farklı disiplinlerdeki
makaleleri bulup okumak isteyen geliştirici ve araştırmacılar.

Karar: Önce çalışan ürünü ilk ziyarette anlaşılır ve denenebilir hale getiriyorum.
“17 araç” yerine “Codex ve Claude tam araştırma makalelerine erişsin” vaadi;
ardından çalışan kurulum, gerçek makale örneği ve paylaşılabilecek kanıt.
Yeni araştırma motoru geliştirmeyi bu büyüme işine almıyorum.

## Sinyal ve karşılaştırma

[Paper Pilot](https://github.com/aytzey/paper-pilot) başlangıçta **12 yıldız / 5 fork**.
Aşağıdaki sayılar 7 Eylül 2026 GitHub API kontrolüdür; değişebilir.

| Proje | Yıldız | README'de öne çıkan iş | Buraya etkisi |
|---|---:|---|---|
| [arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | 3.116 | arXiv'de bölüm/LaTeX okuma, atıf ve takip; kısa kurulum | “Makaleyi okuyabiliyor” tek başına benzersiz bir iddia değil. |
| [zotero-mcp](https://github.com/54yyyu/zotero-mcp) | 4.923 | Mevcut Zotero kütüphanesiyle çalışma | İlk kullanımı Zotero kurulumuna bağlamayalım; farklı başlangıç sorumuz var. |
| [PaperQA](https://github.com/Future-House/paper-qa) | 9.167 | Kaynak gösteren bilimsel soru-cevap / RAG | Kullanıcının zaten sahip olduğu ajana erişim araçları sağlama sınırını koruyalım. |

Bu kitleler örtüşebilir. Yıldızları toplayıp erişilebilir pazar veya gelecekteki yıldız
sayısı diye kullanmıyoruz. Yüksek yıldızın nedeni yalnız README değildir; proje yaşı,
dağıtım, kullanıcı güveni ve ürün farkı bu kontrolde ayrıştırılmadı.

Mevcut repodaki somut sürtünme: ilk ekranda uzun özellik listesi, ölçülmemiş “30 saniye”
iddiası, gerekmeyen e-posta/Zotero alanları ve bazı istemci örneklerinde henüz yayımlanmamış
PyPI paketini çağıran komutlar. [PyPI paket uç noktası](https://pypi.org/pypi/paper-pilot/json)
7 Eylül kontrolünde 404 döndürdü. Kurulumu kopyala >> hata al >> projeyi deneyemeden çık.

## Alternatifler

| Yöntem | Geliştirme / işletim yükü | Karar |
|---|---|---|
| 1. README, ortak kurulum ve gerçek örnek | Mevcut CLI, MCP ve doğrulama çıktıları kullanılır. Yeni servis gerekmez. | ITR-1. Ziyaretçinin hemen deneyebilmesi için somut engelleri kaldırır. |
| 2. Yeni landing page, barındırılan demo ve hesap akışı | Hosting, erişim maliyeti, bakım ve ikinci ürün yüzeyi. | KAPSAM DIŞI. Repo üzerinde gösterilebilen kanıt hazır. |
| 3. Araç sayısını artırmak | Yeni sağlayıcı ve entegrasyon bakımı. | (İPTAL) İlk kullanım sorununu çözmüyor; altı kaynak zaten var. |
| 4. Yalnız daha çok tanıtım yapmak | Yeni kullanıcının bozuk kurulumla karşılaşması sürer. | Önce ITR-1; ardından hedefli dağıtım. |

Alternatif: PyPI yayımlanana kadar GitHub kaynak kurulumu kullanılacak. Yayınlanmamış paket
komutunu çalışıyormuş gibi göstermiyoruz. Ek plugin ve registry paketlemesini aynı işe
sıkıştırmıyorum; gerçek kurulum ve bulunabilirlik verisine göre ayrı iş olacak.

Temiz kurulum kontrolünde ek engel bulundu: `mcp>=1.12.4` kısıtı 2.x sürümüne izin veriyor;
kurulan paket `mcp.server.fastmcp` importunda açılmıyor. Repo kilidiyle çalışan testler bunu
gizliyordu. Kullanılan 1.x API'si için `<2` sınırı ve CI'da yeni bağımlılık çözümüyle paket
import kontrolü ITR-1'e eklendi. MCP 2.x geçişi bu büyüme işinin kapsamına alınmadı.
Yeni PyMuPDF sürümünün eski `fitz` importunda stdout'a yazdığı uyarı da MCP iletişimine
karışıyordu. Servisler mevcut `pymupdf` adını önce kullanıyor; eski sürüm uyumluluğu korunuyor.
Temiz paket kontrolü artık açılışta protokol dışı stdout çıktısını da reddediyor.

## Uygulama sırası

| İterasyon | Somut çıktı | Durum / sahip |
|---|---|---|
| ITR-1 | Kısa README; Codex/Claude için ilk komut; e-posta/Zotero'suz örnekler; sürümlü makale ve taşınan metin kanıtı; araştırma vakası issue formu | Bu repo değişikliği. Uygulama: Codex; yayın sahibi: @aytzey. |
| ITR-2 | [Duyuru taslakları](LAUNCH.md) ile geliştirici ve araştırmacıya ayrı örnek; geri bildirim geldiğinde kurulum/erişim hatasını düzelt | Taslak hazır; paylaşım takvimi @aytzey'de. Otomatik gönderim yok. |
| ITR-3 | PyPI ve uygun MCP dizinleri; gerçek istemci oturumundan kısa kayıt | BACKLOG. Yayın hesabı/kanal sahipliği ve gerçek kullanım kaydı gerektiğinde açılacak. |

Kişi kapasitesi ve paylaşım takvimi belirlenmedi; sprint ve kesin yıldız kazanımı uydurulmadı.
İlk uygulama mevcut örnek, araç ve GitHub yüzeylerini kullanır. Ayrı takip servisi kurulmaz.

## KAPSAM DIŞI

OCR, sunucuda LLM, yeni veritabanı, ücretli reklam, otomatik sosyal paylaşım, toplu iletişim,
yıldız satın alma veya karşılıklı yıldız kampanyası. Tam metin iletimi, modelin makaleyi
anladığı veya verilen devrenin çalıştığı şeklinde pazarlanmaz.

## Açık sorular

@aytzey — İlk denemeler daha çok bir devre/algoritma kararı için mi, yoksa literatür özeti
için mi geliyor? README'nin örnek sırasını gerçek vakalara göre güncelleyeceğiz.

@aytzey — Hangi topluluklarda mevcut hesabımız ve paylaşım iznimiz var? Kanal seçimini
bu bilgiyle yapacağız; toplulukların güncel kuralları gönderim öncesi kontrol edilmeli.
PyPI yayın hesabı hazır mı? Hazır olana kadar GitHub kurulumu ana yol.

## [İYİLEŞTİRME] Ölçüm ve ilk karar noktası

Mevcut toplam: 12 yıldız. İlk ara hedef önerisi: 100 yıldız; bu bir kazanım tahmini veya
tarihli taahhüt değildir. @aytzey ilk paylaşım tarihini kaydeder; 7 ve 14 gün sonra
GitHub yıldız artışı, Insights ziyaret/referrer bilgisi ve gelen gerçek kullanım vakalarını
birlikte değerlendirir. Ziyaretlerin yıldızlayan kişilerle eşleşmesi bilinmiyor; toplam
yıldız / dönem ziyareti hesabından dönüşüm oranı üretmiyoruz.

Ziyaret düşükse dağıtım çalışılır. İnsanlar deniyor fakat kurulumu tamamlayamıyorsa yeni
özellik yerine o engel çözülür. Başarılı vakalar varsa kullanıcı izniyle örneğe dönüştürülür.
İki haftalık kontrolden sonra bir sonraki tarihli karar bu belgeye eklenir.
