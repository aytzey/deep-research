# Araştırmadan uygulama kararına

7 Eylül 2026 — pm-busra `discover` / `decide` / `spec`.
Durum: @aytug planın detaylandırılmasını ve uygulanmasını onayladı. Aşağıdaki sözleşme
uygulama kapsamıdır; pH devresinin tasarlanıp fiziksel olarak doğrulandığı anlamına gelmez.

AMAÇ: Kullanıcı “bitki toprağının pH'ını ölçen ucuz bir devre yapmak istiyorum” dediğinde,
Codex/Claude isteği araştırılabilir sorulara ayırsın; ilgili disiplinlerin yeni çalışmalarından
başlayıp gerekli eski kaynaklara insin; seçtiği karar kaynaklarını tamamen okuyarak
uygulanabilir bir öneri, alternatiflerin elenme gerekçesi ve ilk doğrulama deneyini çıkarsın.

Sorun: tek geniş sorgu >> benzer başlıklı popüler makaleler >> bazı disiplinlerin atlanması
>> laboratuvar sonucunun kullanıcının koşullarına taşınması >> ucuz görünen ama işe
yaramayan prototip. Sinyal @aytug'un bu kullanım örneği ve aşağıdaki yerel kod incelemesi;
kullanım hacmi veya başarı oranı ölçülmedi.

Karar: Araştırmayı istemcideki model yönetsin. Mevcut MCP başlangıç yönergesi bu iş için
ortak araştırma akışını taşısın. Sunucu erişim, tarih, kaynak ve okuma bilgisini doğru
versin; makale seçimi, yeni sorular ve sentez modelde kalsın. Önce mevcut araçların
bu akışı desteklemeyen somut eksiklerini tamamlayalım.

## Mevcut durum → gereken davranış

| Yerel kanıt | Gereken davranış |
|---|---|
| [Araştırma akışı](../src/paper_pilot/server.py), `_run_research_pipeline`: tek konu sorgusu; ilk sonuçtan benzer makaleler; puan sırasından sınırlı indirme. | Kullanıcının kararına göre ayrı sorular, farklı disiplinlerden seçim ve bulguya göre tekrar arama. `download_top_n` araştırmanın tamamlandığı anlamına gelmez. |
| [Arama servisi](../src/paper_pilot/services/academic.py), `search_literature`: altı kaynağın sınırlı sonuçları, ardından `quality_score`. arXiv ilgililiğe göre sıralanıyor; DOAJ ilk sayfa sonrasında yıl filtresi uyguluyor. | Yeni yayınları sağlayıcı sorgusunda da arayan tarih sırası; devam edilebilir sonuçlar; kaynak bazında desteklenmeyen sıralama ve erişilemeyen sonuçlar açık. İlk sayfayı sonradan sıralamak tüm yeni yayınları bulmak değildir. |
| [Kayıt modeli](../src/paper_pilot/models.py), `PaperRecord`: yıl var; `rank_score` atıf, güncellik ve erişimi karıştırıyor. | Yayın tarihi ve tarih hassasiyeti korunmalı; yalnız yıl biliniyorsa gün uydurulmamalı. Güncellik, konuya uygunluk ve deneyin güvenilirliği ayrı değerlendirilir. |
| Aramanın varsayılanı `open_access_only=True`. | Kapsamlı keşifte kapalı erişimli kayıtların varlığı da görülebilmeli; indirme mevcut erişim politikasını izlemeli. Okunamayan kritik kaynak sonuçtan sessizce düşmemeli. |
| `find_similar_papers` öneri/anahtar kelime sonuçları veriyor. | Benzerlik, gerçek atıf ilişkisi diye sunulmamalı. Model tam metindeki kaynakçadan DOI/başlık takip edebilir; otomatik atıf zinciri olduğu iddia edilmez. |
| Tam metin devam noktası ve özgün PDF aktarımı artık var. | Kararı taşıyan kaynaklar bütünüyle okunmalı; özetle elenen kayıt ile tamamı okunan kaynak ayrı kaydedilmeli. |

## pH örneğinde Codex'in izleyeceği yol

1. **Kararı netleştir.** Toprağa saplanan sürekli ölçüm mü, hazırlanmış örnek üzerinde
   aralıklı ölçüm mü? “Ucuz” toplam hangi bütçe, kabul edilen hata ve üretim imkânı?
   Bu bilgileri kullanıcı henüz vermedi. Codex devre seçimini değiştiren soruları kısa
   biçimde sorar; yanıt beklerken ortak ölçüm ilkelerini araştırır. Sayısal hedef uydurmaz.
   Cevap gelmezse tek cihaz önerisini kesinleştirmek yerine iki senaryonun sonuçlarını verir.

2. **Kararı etkileyen disiplinleri aç.** Tek `cheap soil pH sensor` sorgusu yeterli değildir.
   Aşağıdaki sorgular başlangıç örnekleridir; sabit sorgu listesi veya her konuya zorlanan
   bölüm şablonu değildir. Bulunan terimlerle ve eşanlamlılarla güncellenir.

   | Alan | Araştırma sorusu ve örnek sorgu | Karara etkisi |
   |---|---|---|
   | Ziraat / toprak kimyası | `soil pH measurement suspension in situ comparison` | Hangi örnek hazırlama ve referans yöntemle karşılaştırılacak; hangi kullanım için yeterli? |
   | Malzeme / elektrokimya | `soil pH solid state reference electrode drift stability` | Duyarlı elektrotla birlikte referans elektrot, ömür, üretim ve saklama şartları. |
   | Elektronik | `potentiometric pH high impedance analog front end input bias current` | Elektrodun sinyalini bozmadan ölçmek için gereken analog devre. |
   | Ölçüm / saha doğrulaması | `soil pH sensor moisture temperature calibration field validation` | Tampon çözelti başarısı gerçek toprak koşullarında tekrarlanıyor mu? |
   | Yapılabilirlik / maliyet | Seçilen parçaların resmi veri sayfaları ve güncel tedarik bilgisi | Prob, elektronik, referans, kalibrasyon, sarf ve muhafaza dahil yapılabilir maliyet. |

3. **Yeniden eskiye tara, gerekince kaynak zincirine gir.** Arama tarihini ve kapsanan
   tarih aralıklarını kaydet. Her alanda yeni ilgili çalışmalarla başla; eskiye doğru
   genişlet. Yeni yayınlardaki temel yöntem ve karşılaştırmaların özgün kaynaklarına
   hemen dönmek serbesttir. En yeni çalışma otomatik olarak en güçlü kanıt değildir.
   Atıf sayısı da seçim için tek ölçüt olamaz. Derlemeler alan haritasını kurar;
   tasarım kararları deney makaleleri, yöntem belgeleri ve resmi veri sayfalarıyla doğrulanır.
   Yeni bir makalenin hakemlik durumu, çevrimiçi yayın tarihi ve son güncellenme tarihi
   karıştırılmaz; preprint ile dergi sürümü iki bağımsız deney diye sayılmaz.

4. **Ön eleme yap, karar kaynaklarını tamamen oku.** Başlık, yazar, yıl ve kimlik
   doğrulanır. Abstract konuya uygunluk elemesi için kullanılabilir. Yöntem, sonuç,
   sınırlılık ve ekler karar için gerekiyorsa tam metin/PDF okunur; kritik şekil, tablo,
   devre şeması ve ek dosyalar ayrıca incelenir. Çalışan tam PDF doğrudan kullanılır;
   PDF eksik/bozuksa Unpaywall, kapak/abstract çıktıysa modelin isteğiyle alternatif kopya.
   Erişim başarısızsa “Tam metne erişilemedi; tasarım dayanağı olarak doğrulanmadı.”
   Metin katmanı eksikse görüntü/PDF inceleme imkânı kullanılır; eksik kalan kapsam saklanmaz.

5. **Bulguları aynı karşılaştırmaya taşı.** Her seçenek için ölçüm yöntemi, referans
   elektrot, gerçek toprak deneyi, örnek sayısı, kalibrasyon, hata tanımı, sıcaklık/nem,
   sürüklenme, bakım ve üretim ihtiyacı çıkarılır. Her kritik iddia PDF sayfasına veya
   resmi belgenin bölümüne bağlanır. Yalnız tampon çözeltideki doğruluk gerçek toprak
   doğruluğu sayılmaz; farklı hazırlama yöntemlerindeki pH sonuçları eşdeğer varsayılmaz.
   Kaynakta verilmeyen değer “raporlanmamış” kalır. Modelin hesabı ve tasarım önerisi,
   makaledeki ölçülmüş sonuç gibi anlatılmaz.

6. **Çelişkiye ve eksik kanıta göre tekrar ara.** Bir çalışma kararlı sonuç, diğeri
   sürüklenme bildiriyorsa elektrot, deney süresi, toprak ve bakım farklarını araştır.
   Yalnız seçilmeye yakın yöntemi destekleyen yayınları toplama; başarısızlık ve
   karşılaştırma çalışmalarını da ara. Yeni bulgu kararını değiştirirse arama sorularını
   ve seçimi güncelle. Eski veya az atıflı bir saha çalışması bu aşamada belirleyici olabilir.

7. **Kullanıcının yapabileceği bir kararla bitir.** Tercih edilen ölçüm yaklaşımı,
   gerekçesi, elenen seçenekler, devre blokları, yapılabilirlik ve maliyet varsayımları,
   kalibrasyon/bakım ihtiyacı ve ilk karşılaştırma deneyi verilir. Belirleyici kanıt
   eksikse öneri koşullu kalır. Araştırma, prototipin fiziksel ölçüm doğrulamasının yerine geçmez.

“Kaç makale okuduk?” tamamlanma ölçütü değildir. Model temel seçenekleri karşılaştırdığında,
kritik iddiaları kontrol ettiğinde ve hedefli ek arama kararı değiştiren yeni kanıt
getirmediğinde neden durduğunu açıklar. Açık bir belirleyici soru varsa bunu sonuçta
korur. Süre/API sınırında kalınırsa “Araştırma kısmi; şu sorular açık kaldı.” denir;
tüm literatürün eksiksiz tarandığı iddia edilmez.

## Bu örneği neden böyle kuruyoruz?

7 Eylül 2026'da yapılan dar kaynak kontrolü, tam bir pH tasarım araştırması değildir:

- [2026, Nair vd., all-solid electrode pH meter](https://www.sciencedirect.com/science/article/pii/S0263224126006755)
  yeni bir aday yaklaşımın varlığını gösteriyor. Bu oturumda yayıncı önizlemesi görüldü;
  tam makale erişimi doğrulanmadı. Bu yüzden doğruluk/ömür iddialarıyla parça seçmedik.
- [2024, Rapid in-field soil analysis…](https://link.springer.com/article/10.1007/s11119-024-10181-6)
  toprak ölçümünde farklı teknikleri ve saha koşullarını karşılaştıran bir alan haritası
  sunuyor. Kaynakçadan birincil deneylere inmek için uygun; tek başına devre kararı değil.
- [FAO, Soil analysis, Bölüm 3](https://www.fao.org/docrep/pdf/011/i0131e/i0131e.pdf)
  pH ölçümünde örnek hazırlama ve tamponla kalibrasyon adımlarını veriyor.
  Buradan çıkardığımız ürün gereksinimi: sensör seçmeden ölçüm yöntemi tanımlanmalı.
  Uygulamada kullanılacak yöntemin güncel sürümü ayrıca doğrulanır.
- [Analog Devices, CN0326 (2013)](https://www.analog.com/en/resources/reference-designs/circuits-from-the-lab/cn0326.html)
  yüksek empedanslı pH probu için sinyal koşullandırma ve sıcaklık ölçümü içeriyor.
  Eski bir resmi devre belgesi yeni malzeme makalesini anlamaya yardımcı olabilir.
  Bu devrenin bütün parçalarını veya izolasyonunu ucuz prototipe aynen alma kararı verilmedi.

## Yöntem kararı ve geliştirme sırası

| Alternatif | Geliştirme / bağımlılık | Karar |
|---|---|---|
| YÖNTEM 1: mevcut araçlar + ortak araştırma yönergesi + gerçek tarihli keşif | Bu repoda yönerge ve sınırlı arama değişikliği; düşünme mevcut Codex/Claude'da. | Seçildi. Dosya erişimi hazır; eksik araştırma davranışını en az yeni mekanizmayla tamamlar. |
| YÖNTEM 2: yönergeyi yalnız README/CODEX/CLAUDE dosyalarına yazmak | Dokümantasyon yeterli; harici MCP istemcisinin repo dosyalarını okumasına bağlı. | (İPTAL) Kullanıcı başka bir projedeyken de yönlendirme ulaşmalı; yalnız repo belgesine güvenemeyiz. |
| YÖNTEM 3: sunucu içinde ikinci LLM, çok ajanlı planlayıcı ve görev motoru | Yeni model erişimi, durum saklama ve işletim yükü. | KAPSAM DIŞI. İstemcide zaten araştırmayı yürüten model var. |
| YÖNTEM 4: yalnız daha fazla makale indirmek | Limitleri artırmak kolay; seçim ve karşılaştırma hâlâ eksik. | (İPTAL) Eksik disiplini veya yanlış deney karşılaştırmasını çözmüyor. |

ITR-1 / TAMAM (yerel uygulama): Ortak araştırma akışını mevcut MCP yönergesine taşı; kapsamlı keşifte
erişim filtresini açık seç; gerçek tarih sırası ve aramaya devam etmeyi destekle;
sağlayıcı bazında kapsama/erişim sınırlarını döndür. Yeni sıralama mevcut varsayılan
ilgililik davranışını sessizce değiştirmemeli. Sahip: bu repo üzerindeki uygulama işi;
takvim ve kişi kapasitesi belirlenmedi, sprint sayısı uydurulmadı.

Alternatif (geçici): Model mevcut yıl filtreleriyle ayrı sorgular yürütür, sonuçları
birleştirir, kimlikle tekrarları ayıklar ve seçtiği PDF'leri tek tek okur. Bu yöntem
sağlayıcıların ilk sayfa sınırlarını kaldırmaz; “en yeni yayınların tamamı bulundu” denmez.

ITR-2: Otomatik ileri/geri atıf API'si, ancak mevcut tam metin kaynakça takibinin somut
bir darboğaz olduğu görülürse ayrı iş olarak değerlendirilir. İnteraktif grafik bu akışın
önkoşulu değildir. Resmi standart ve veri sayfalarını istemcinin mevcut web araçlarıyla
araştırmak yeterlidir; ilk aşamada yeni genel web arama motoru eklenmez.

KAPSAM DIŞI: OCR, sunucuda sentez yapan LLM, vektör veritabanı, her konuya sabit sayıda
disiplin/makale dayatmak, otomatik satın alma, zorunlu Zotero, kusursuzluk yüzdesi,
pH örneğine özel sabit sensör/parça kararı. Önceki [PDF kapsamı](FULL_TEXT_SCOPE.md) geçerlidir.

Açık sorular: @aytug — bu örnek gerçek donanım işine dönüştüğünde bütçe, ölçüm şekli,
kabul edilen hata ve üretim imkânı netleşmeli. Şu an örnek üzerinden genel akışı tanımlıyoruz.
İlk istemci doğrulamasında MCP yönergesinin Codex/Claude oturumuna gerçekten ulaşıp
araştırmaya yön verdiği de kontrol edilmeli; yalnız kodda metin bulunması yeterli değildir.

## Uygulama sözleşmesi — 7 Eylül 2026

ITR-1 üç bağlı işten oluşur; her biri bu repoda uygulanır. Yeni servis, hesap veya
çalışma zamanı bağımlılığı gerekmez. Önce arama sözleşmesi, sonra istemci yönergesi,
sonra aynı araçlar üzerinden vaka kontrolü yapılır.

| İş | Somut davranış | Hata / sınır |
|---|---|---|
| Araştırma yönergesi | Mevcut MCP `instructions` alanı: karar sorusu → disiplinlere göre sorgu → yeni çalışmalar → kaynakça ve eski yöntemler → tam okuma → karşı kanıt → uygulanabilir karar. | Talimatların iletilmesi modelin uyguladığını kanıtlamaz. İstemci davranışı ayrıca değerlendirilir. |
| Tarihli keşif | `search_literature` mevcut parametrelerine `sort_by="relevance"|"newest"`, `source="all"|kaynak`, `cursor` eklenir. Eski çağrıların varsayılanı değişmez. | Tarih sırası sağlayıcı sorgusunda uygulanır. Yalnız dönen sayfalar birleştirilir; dünya literatürünün tam sırası veya eksiksizliği vaat edilmez. |
| Aramaya devam | İlk çağrı kaynakların ilk gruplarını getirir. Her kaynak için `next_request`, aynı arama aracına verilecek parametrelerin tamamını taşır. | `cursor` ile `source="all"` kabul edilmez. Hatalı kaynak için aynı isteği yineleme bilgisi döner; hata, sonuçların bittiği sayılmaz. |
| Kapsam bilgisi | Kaynak, istenen/uygulanan sıra, gelen kayıt sayısı, biliniyorsa toplam, devam ve hata bilgisi döner. | Toplamlar sağlayıcı tahmini olabilir. DOI tekrarı, OA filtresi veya başka tarih filtresi sonrasındaki az sonuç devamı durdurmaz. |
| Tarih kaydı | `publication_date`, hassasiyet ve geldiği alan saklanır. arXiv tarihi ilk gönderim olarak etiketlenir; güncelleme tarihi kullanılmaz. | Yalnız yıl/ay biliniyorsa yapay gün eklenmez. Birleşen kaynakların farklı tarihleri korunur. Eksik tarihler sıralamada sonlara gider. |
| Kanıt seçimi | Kapsamlı yönerge `open_access_only=False` kullanır; model farklı sorular için araç çağrılarını kendisi yapar. | Erişim durumu kalite puanı değildir. PDF/Unpaywall ve tam metin devamı önceki sözleşmeye uyar. |

Girdi sınırları: kaynak başına 1–100 sonuç; boş konu, ters/geçersiz yıl aralığı,
bilinmeyen sıra/kaynak ve geçersiz devam bilgisi reddedilir. Kaynakların kendi daha
dar sınırları ayrıca belirtilir. Devam bilgisi bir URL değildir; yalnız sabit sağlayıcı
adreslerinin sorgu parametresi olarak kullanılır. Kaynakların değişen veri tabanları
nedeniyle sayfalar arasında tekrar görülebilir; model DOI/arXiv kimliğini izler.

Sağlayıcı yaklaşımı ve dayanak:

- [OpenAlex](https://help.openalex.org/api/sorting/): `publication_date:desc` ve
  [cursor](https://help.openalex.org/api/paging/). Yayın tarihi kullanılır.
- [Crossref](https://github.com/Crossref/rest-api-doc): `sort=published`, `order=desc`,
  offset; sayfa sonu ham kayıt sayısından belirlenir. 7 Eylül canlı API kontrolü:
  yayın tarihi + cursor (İPTAL), API `sort-criteria-incompatible-with-cursor` döndürüyor.
  Tarihli arama ilk 10.000 kayıtla sınırlı; ardından yıl/sorgu daraltılır.
- [arXiv](https://info.arxiv.org/help/api/user-manual.html): `submittedDate`,
  `descending`, `start`; ilk gönderim tarihi olduğu görünür.
- [Semantic Scholar](https://api.semanticscholar.org/api-docs/snippets): yeniye göre
  aramada bulk endpoint `publicationDate:desc`. Servisin büyük grubu, mevcut önbellek
  üzerinde küçük devam gruplarıyla sunulur; kesilen kayıtlar atlanmaz. İlgililik araması
  mevcut endpoint ve offset sınırını korur.
- [Europe PMC](https://europepmc.org/RestfulWebService): tarih sırası ve `cursorMark`.
- [DOAJ](https://doaj.org/api/docs): yayın yılı sırası ve sayfa numarası. Yıl hassasiyeti
  açıkça bildirilir; kayıt oluşturma tarihi yayın tarihi yerine kullanılmaz.
  Canlı v4 API'de sıralanabilir alan `bibjson.year.exact`; `bibjson.year` hatayla dönüyor.
  Aynı yılın farklı sayfaları ay/gün bakımından küresel sıralı değildir.

`next_request` yalnız başarısız olmayan kaynağın gerçekten devam edilebilir ham
sonuçlarından üretilir. Bir sayfada ilgili/OA kayıt kalmasa bile sonraki sayfaya geçilebilir.
Süresi dolmuş arama önbelleği ağ hatasını gizlemek için kullanılmaz. Geçerli önbelleğin
varlığı ve TTL yanıt kapsamında açıklanır; “şimdi yayımlanan her şey tarandı” denmez.

Çıktı yönlendirmesi: Codex kararını, önemli alternatifleri ve neden elendiklerini,
okunan kaynak/sayfaları, koşullar arasındaki farkları, erişilemeyen kaynakları ve
kararı değiştirecek ilk deneyi kullanıcıya verir. pH bütçesi/hassasiyeti için sayısal
varsayım üretmez. Bu örnek yönergeyi sınar; ürüne sabit pH bilgisi kodlanmaz.

## [İYİLEŞTİRME] Davranışı kontrol etme

Bu vaka uygulama sonrası baştan sona çalıştırılır. Yeni protokolün başarı oranı henüz
ölçülmedi. Kontrol sahibi uygulama işini yürüten ajan; sonuç kaynaklarıyla birlikte raporlanır:

- Ölçüm biçimi netleşmeden veya koşulları belirtilmeden tek devre seçilmemiş olmalı.
- Kararı etkileyen alanlar ve arama tarih aralıkları görünmeli; tek geniş sorguda kalmamalı.
- Yeni bir yayın eski ve çok atıflı sonuçların altında kaybolmamalı; kısmi tarih bilinirse belirtilmeli.
- Her belirleyici iddianın gerçekten okunan kaynağı ve sayfa/bölümü bulunmalı.
- Tam metnine ulaşılamayan adayın abstract sonucu doğrulanmış tasarım kanıtı sayılmamalı.
- Alternatifler aynı ölçüm koşullarıyla karşılaştırılmalı; karar gerekçesi ve açık sorular görünmeli.
- Çalışan tam PDF'de gereksiz Unpaywall çağrısı ve hiçbir OCR adımı olmamalı.
- Sonuç, seçilen yaklaşım ve onu yanlışlayabilecek ilk fiziksel deneyle bitmeli.

### Uygulama ve doğrulama sonucu

Yönerge mevcut MCP başlangıç mesajına eklendi; arama aracının açıklaması da seçim ve
tam okuma adımlarını hatırlatıyor. `sort_by`, `source`, `cursor`, kaynak bazında devam/hata
bilgisi ve tarih hassasiyeti uygulandı. Paket bağımlılığı ve araç sayısı artmadı.
İlgililik/OA varsayılanları korundu; disiplinlere ayırma ve karar istemcideki modelde.
Son yerel kontrolde 113 test, lint, paket oluşturma ve dağıtım dosyası kontrolleri geçti.
Çalışma zamanı kodu, testler ve bağımlılık tanımında OCR bileşeni bulunmuyor.

Canlı API kontrolünde altı kaynağın her birinden iki grup sonuç alındı; kontrol edilen
ilk/ikinci gruplarda DOI/kayıt tekrarı görülmedi. DOAJ yalnız yıl sırasını sağlıyor;
Crossref tarih sırası 10.000 kayıtta sınırlı. Semantic Scholar'da geçici HTTP hatası
sonrası yineleme gerekti. Kanıt: `data/research-search-verification.json`.

Gerçek stdio MCP bağlantısında araştırma yönergesi ve yeni araç parametreleri istemciye
ulaştı. İlk geniş pH sorguları ilgisiz yeni yayınlar da getirdi; ön eleme ve daraltma
gerektiği doğrulandı. Europe PMC'de başlığa daraltılan sorgu, ilgili 2026 ve 2023
çalışmalarını yeniye göre getirdi. Kanıtlar: `data/research-mcp-verification.json`,
`data/research-refinement-verification.json`, `data/research-targeted-verification.json`.

Seçilen `10.1038/s41598-026-57457-7` PDF'si 24 sayfa/60.332 karakter;
`10.3390/mi14122188` PDF'si 13 sayfa/35.831 karakter. Gerçek MCP üzerinden sırasıyla
6 ve 3 metin grubuyla tamamı taşındı; birleştirilen metinler bütün PDF sayfalarının
çıkarımıyla birebir eşleşti. Metin boşluğu uyarısı yok. İlk dosya kabul edilmiş makale
sürümüdür; kapak, gövde ve kaynakça içerir. Kanıt: `data/research-ph-reading-verification.json`.

Bu kontroller arama/erişim/iletim davranışını doğrular. Codex/Claude arayüzlerinde
bağımsız modelin bütün protokolü kendiliğinden izlediği, pH devresinin doğruluğu veya
araştırmanın eksiksiz olduğu iddia edilmez. Kullanıcı bütçesi/hata hedefi olmadan cihaz
seçilmedi. Yukarıdaki davranış değerlendirmesi gelecek gerçek araştırma oturumlarında da
aynı kanıt ölçütleriyle yapılabilir; tamamlandı yüzdesi uydurulmadı.
