# Akıllı Sulama Zamanlama Sistemi 🌱💧

Bu proje, çeşitli tarımsal ve meteorolojik verileri (sıcaklık, hava nemi, yağış, rüzgar hızı, toprak nemi, pH, ürün tipi, büyüme evresi vb.) kullanarak bitkinin **Sulama İhtiyacını (Low, Medium, High)** yüksek doğrulukla tahmin eden gelişmiş bir makine öğrenmesi sistemidir. 

Tarımsal sulamada su israfını önlemek ve bitki verimini maksimize etmek amacıyla bu projeyi **geliştirdim**.

## 🚀 Projenin Durumu
Şu an için projenin **Frontend (Önyüz)** kısmını henüz geliştirmedim. Ancak **Backend (Arkayüz)** kısmını, veri işleme boru hattını (pipeline), makine öğrenmesi modellerini ve ileri düzey (advanced) test süreçlerini tamamen **bitirdim**. 

## 🧠 Makine Öğrenmesi (Backend) Özellikleri

Model geliştirme sürecinde sadece yüksek bir "Accuracy" elde etmekle kalmadım, aynı zamanda sistemin bilimsel olarak doğru kararlar aldığını kanıtlamak için çok çeşitli teknikler uyguladım:

* **Sınıf Dengesizliği (Class Imbalance) Çözümü:** Veri setindeki eşitsiz dağılımları önlemek ve azınlık sınıfların da doğru öğrenilmesini sağlamak için **SMOTENC** algoritmasını entegre ettim.
* **Random Forest Sınıflandırıcı:** Hiperparametreleri optimize edilmiş sağlam (robust) bir ağaç tabanlı model eğittim. Test setinde **%99.15 Doğruluk (Accuracy)** ve çok yüksek Macro F1 skorları elde ettim.

## 🧪 İleri Seviye (Advanced) Model Testleri
Modelin başarısının ezbere (overfitting) veya veri sızıntısına (data leakage) dayanmadığını ispatlamak için `scripts/advanced_tests/` altında şu zorlu testleri kodlayıp uyguladım:

1. **Learning Curve (Öğrenme Eğrisi):** Modelin veriye doyduğunu ve "ezber" yapmadığını (Train ve Test eğrilerinin birleştiğini) gösterdim.
2. **Y-Shuffle (Hedef Karıştırma):** Hedef değişkenleri tamamen rastgele dağıtarak modelin performansının %32'ye çakıldığını; yani sistemin ezberlemediğini, verideki mantıksal fiziksel bağları öğrendiğini kanıtladım.
3. **Permutation Importance:** Özellikleri rastgele bozarak model için en kritik faktörlerin sırasıyla *Büyüme Evresi (Crop Growth Stage)* ve *Toprak Nemi (Soil Moisture)* olduğunu keşfettim.
4. **Zorlu Holdout (Ürün ve Bölge):** Modeli eğitimde hiç görmediği yepyeni ürün türleri (Örn: Pirinç, Patates) ve yepyeni coğrafi bölgeler üzerinde test ettim. Her ikisinde de **%98** üzerinde genelleme başarısı yakaladım.
5. **Kopya Veri Kontrolü:** Eğitim ve Test setleri arasında %100 örtüşen hiçbir satır olmadığını, Veri Sızıntısı (Leakage) riskinin "Sıfır" olduğunu doğruladım.
6. **Dağılım ve Baseline Analizi:** Random Forest'ın başarısını Dummy, Logistic Regresyon ve basit Decision Tree gibi modellerle kıyaslayarak veri setindeki kararlı yapıyı ortaya koydum.
7. **Karar Kuralı Çıkarımı (Rule Extraction):** Sistemin "Kara Kutusu"nu açarak, *("Eğer toprak nemi düşükse ama mevsim kış ve yağışlıysa suyu az ver")* şeklindeki İngilizce IF-ELSE ziraat kurallarını metin formatında başarıyla çektim.
8. **Çok Sınıflı ROC Eğrisi:** Her sınıfın (Low, Medium, High) mükemmele yakın (AUC ~ 1.0) ayırt etme gücüne sahip olduğunu görselleştirdim.

## 📂 Proje Yapısı
* `data/`: Eğitim veri setleri (`irrigation_prediction.csv`) ve kaydedilmiş hazır model dosyaları (`water_need_model.pkl`).
* `scripts/`: Model eğitim, veri ön işleme, test betikleri ve veri görselleştirme kodları.
* `scripts/advanced_tests/`: Yukarıda belirtilen 10 aşamalı akademik düzey robustness (dayanıklılık) testlerini içeren bağımsız betikler.

---
*Gelecek Güncellemeler: Modelin çıktısını son kullanıcıya ulaştıracak görsel web (Frontend) arayüzü tasarlanacaktır.*
