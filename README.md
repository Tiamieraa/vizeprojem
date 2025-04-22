# 👋 Merhaba!

Bu proje, Python ve Mediapipe kullanarak geliştirilmiş, **el hareketleriyle nesne etkileşimli bir muz toplama oyunudur**. Oyuncu kameraya elini uzatarak ekrandaki sarı muzlara dokunur, her temas bir skor ve XP kazandırır. Belirli sayıda muz toplayan oyuncu seviye atlar. Oyun sonunda "Play Again" butonuna basılarak tekrar başlanabilir.

---

## 🎮 Oyun Özellikleri

- ✋ Gerçek zamanlı el takibi (Mediapipe HandLandmarker)
- 🍌 Sarı muz görseli (PNG şeffaf)
- ⏳ Süre sayacı ve 3-2-1 geri sayım başlangıcı
- 📈 Seviye sistemi (XP bar ile)
- 🔊 Ses efektleri: Muz toplayınca `pop.wav`
- ❌ Oyunun sonunda `gameover.png` görseli
- 📽 "Play Again" butonuna mouse ile tıklayarak yeniden başlama

---

## 💡 Hangi Değişiklikleri Yaptım?

- El algılama modeli olarak **Mediapipe Tasks API** kullanıldı.
- Tüm etkileşim için **landmark[8] (işaret parmağı ucu)** kullanıldı.
- XP/Seviye sistemi eklendi: Her 5 muzda seviye atlanıyor.
- `pop.wav` sesi muz toplanınca oynatılıyor.
- `gameover.png` görseli ve mouse ile "Play Again" tıklaması aktif edildi.
- 3-2-1 başlangıç geri sayımı eklendi.

---

## 🛠️ Kurulum

1. Python 3.10+ sürümü yüklü olmalıdır. [Python.org](https://www.python.org/downloads/)
2. Ortam hazırlandıktan sonra gerekli paketleri yüklemek için:

```bash
pip install -r requirements.txt
```

**requirements.txt** içeriği:
```text
mediapipe==0.10.9        # El takibi için
opencv-python==4.9.0.80  # Görüntü işleme ve kamera erişimi
numpy==1.24.4            # Sayısal işlemler, koordinat hesaplama
pygame==2.5.2            # Ses efektlerini çalmak için
Pillow==10.3.0           # PNG resim işleme (şeffaflık için)
```

---

## 📂 Dosya Yapısı

```
muz_toplama_oyunu/
├── eren_tasdurmayli_goruntuisleme_vize.py
├── hand_landmarker.task
├── README.md
├── requirements.txt
├── assets/
│   ├── banana.png
│   ├── gameover.png
│   └── pop.wav
```

> `banana.png` şeffaf arka planlı bir PNG olmalı.

---

## ▶️ Nasıl Çalıştırılır?

```bash
python eren_tasdurmayli_goruntuisleme_vize.py
```

1. Oyun 3-2-1 geri sayım ile başlar.  
2. Kameraya elinizi uzatın, işaret parmağınız muzlara yaklaştırın.  
3. Her muz bir skor ve XP kazandırır.  
4. Belirli süre sonunda oyun biter.  
5. "Play Again" yazısına mouse ile tıklayarak yeniden başlatabilirsiniz.

---

## 👤 Geliştirici

**Ad Soyad:** Eren Taşdurmaylı  
**E-posta:** erentss1091@gmail.com  
**Teslim:** 25 Nisan 2025 - BL242 Görüntü İşleme Dersi Vize Projesi

