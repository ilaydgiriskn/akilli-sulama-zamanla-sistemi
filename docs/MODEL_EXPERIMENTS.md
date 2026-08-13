# Makine Öğrenmesi Model Deneyleri ve Kavramlar (Sözlük)

Bu doküman, projede kullanılan veri bilimi kavramlarını, model denemelerini ve özellik (feature) mühendisliği testlerini açıklamak amacıyla oluşturulmuştur.

## 1. Veri Dengesizliği (Class Imbalance) ve Çözüm Yaklaşımları
Veri setimizde "Low" (Sulama Gerekmez) sınıfı binlerce örnekten oluşurken, "High" (Yüksek Sulama) sınıfı sadece 50-60 satırdan oluşuyordu. Modeli bu haliyle eğitirsek model tembelleşip sürekli "Low" diyerek hile yapar. Bunu çözmek için 3 adım denedik:

### A. Normal RF (Random Forest)
- **Nedir:** Standart Random Forest algoritmasıdır. Verideki adaletsizliğe (imbalance) müdahale etmez.
- **Sonuç:** Model "High" sınıfını tamamen göz ardı eder, çoğunluk neyse onu tahmin etmeye meyilli olur.

### B. Balanced RF (Sınıf Ağırlıklandırmalı)
- **Nedir:** Veride oynama yapmayız ama modele şu kuralı veririz: "Low sınıfını bilirsen sana 1 puan veririm, ama nadir olan High sınıfını bilirsen 100 puan veririm." (`class_weight='balanced'`).
- **Sonuç:** Model azınlık sınıflara daha fazla odaklanmaya başlar, ancak hala ellerindeki 50 satırlık "High" verisiyle çalışmak zorunda olduğu için öğrenme kapasitesi kısıtlıdır.

### C. SMOTE / SMOTENC (Sentetik Veri Üretimi)
- **Nedir:** Azınlık sınıfı sadece ödüllendirmek yetmez, onlara ders çalışacak daha çok materyal vermeliyiz diyerek veri sayısını artırma işlemidir. İki mevcut "High" verisinin özelliklerini harmanlayarak aralarında yeni, kurgusal (sentetik) ama **matematiksel olarak gerçekçi** yeni "High" verileri üretiriz. 
- **SMOTENC Farkı:** Verimizde kategorik (metin tabanlı, One-Hot kodlanmış) veriler olduğu için normal SMOTE kullanırsak "Yarım Buğday - Yarım Mısır" gibi saçma sentezler üretir. SMOTENC ise kategorik verileri (Nominal) dokunmadan koruyup sadece sayısal verilerin (Sıcaklık, Nem) sentetiğini üretir.

---

## 2. Feature (Özellik) Grupları Karşılaştırması Ne Demek?
Kullandığımız 11 farklı veri sütununu (Feature) mantıksal olarak 3 gruba ayırdık:
1. **Çevresel (Environmental):** Sıcaklık, Yağış, Nem, Rüzgar.
2. **Toprak (Soil):** Toprak Nemi, pH, Toprak Tipi.
3. **Tarımsal (Agronomic):** Ürün Tipi, Bitki Büyüme Evresi (Growth Stage), Mevsim (Season), Malçlama.

"Feature grupları karşılaştırıldı" demek, *Sadece hava durumuna bakarsam model suyu ne kadar doğru bilir? Sadece toprağa bakarsam ne kadar bilir? Üçüne birden bakarsam ne kadar bilir?* diye sorup modelleri birbiriyle yarıştırdık demektir.

---

## 3. Feature Ablation (Özellik Kesip Çıkarma) Testi Nedir?
Tıpta "Ablasyon", işe yaramayan veya soruna yol açan bir dokuyu kesip çıkarma işlemidir. Makine öğrenmesinde **Ablation Testi** ise şudur:
Mükemmel çalışan %99 doğruluk oranına sahip bir modelimiz var. Bu başarının hangi kolondan (sütundan) geldiğini anlamak için kolonları tek tek "kesip çıkarırız" ve modeli tekrar eğitiriz.

**Örnek (Bizim Projedeki Ablation Sonucu):**
- **Tam Model (11 Sütun):** %99 Başarı
- **Toprak Nemi Çıkarılmış Model (10 Sütun):** %81 Başarı (Özellikle High bulma oranı %88'den %33'e çakıldı).

**Ablation Sonucu:** Modelin zekasının ve %99'luk başarısının sırrı, Toprak Nemi ile Tarımsal Verilerin birleşimidir. Toprak nemi verisini kesip çıkarırsak sistem çöker. Ablation testi, hangi verinin sistemin kalbi olduğunu bilimsel olarak ispatlar.
