# === Muz Toplama Oyunu ===
# El hareketleriyle muz toplayarak skor kazanılan etkileşimli bir oyun.
# Oyun sonunda "Play Again" butonuna tıklanarak tekrar başlanabilir.

import cv2
import time
import random
import numpy as np
import mediapipe as mp
import pygame
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# === Oyun Varlıkları ve Ses ===
banana_img = cv2.imread("assets/banana.png", cv2.IMREAD_UNCHANGED)
gameover_img = cv2.imread("assets/gameover.png")
pygame.mixer.init()
pop_sound = pygame.mixer.Sound("assets/pop.wav")

# === Sabitler ===
muz_max_sure = 3
muz_tutulmazsa_zaman_eksi = 2
pencere_ismi = "Muz Toplama Oyunu"
oyun_bitti = False
restart_istendi = False

# "Play Again" butonunun orijinal görsel üzerindeki koordinatları (1366x768)
play_button_coords = {
    "x1": 490,
    "x2": 880,
    "y1": 620,
    "y2": 690
}

# === Fare Tıklama Kontrolü ===
def tiklama_kontrol(event, x, y, flags, param):
    """Oyun bitince mouse ile 'Play Again' butonuna tıklamayı kontrol eder."""
    global oyun_bitti, restart_istendi
    if oyun_bitti and event == cv2.EVENT_LBUTTONDOWN:
        orijinal_genislik = 1366
        orijinal_yukseklik = 768
        pencere_genislik = 1280
        pencere_yukseklik = 720

        genislik_orani = pencere_genislik / orijinal_genislik
        yukseklik_orani = pencere_yukseklik / orijinal_yukseklik

        x1 = int(play_button_coords["x1"] * genislik_orani)
        x2 = int(play_button_coords["x2"] * genislik_orani)
        y1 = int(play_button_coords["y1"] * yukseklik_orani)
        y2 = int(play_button_coords["y2"] * yukseklik_orani)

        if x1 <= x <= x2 and y1 <= y <= y2:
            print("▶️ Play Again tıklandı.")
            restart_istendi = True

# === Mediapipe Modeli Ayarlama ===
base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# === Yardımcı Fonksiyonlar ===
def yeni_muz_olustur(w, h):
    """Yeni muz pozisyonu oluşturur."""
    return {"x": random.randint(50, w - 100), "y": random.randint(50, h - 150), "size": 64}

def koordinat_getir(landmarks, indeks, h, w):
    """Belirtilen landmark koordinatını döndürür."""
    landmark = landmarks[indeks]
    return int(landmark.x * w), int(landmark.y * h)

def muz_resmi_ciz(img, muz, muz_img):
    """PNG muz görselini ekrana çizer."""
    x, y, size = muz["x"], muz["y"], muz["size"]
    muz_resized = cv2.resize(muz_img, (size, size))
    if muz_resized.shape[2] == 4:
        alpha_s = muz_resized[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(3):
            y1, y2 = y, y + size
            x1, x2 = x, x + size
            if y2 > img.shape[0] or x2 > img.shape[1]:
                return
            img[y1:y2, x1:x2, c] = (alpha_s * muz_resized[:, :, c] + alpha_l * img[y1:y2, x1:x2, c])

def draw_level_bar(img, xp, xp_max, level):
    """Seviye (XP) barını ekrana çizer."""
    h, w, _ = img.shape
    bar_x = 50
    bar_y = h - 40
    bar_width = w - 100
    bar_height = 20
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
    fill = int(bar_width * xp / xp_max)
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + fill, bar_y + bar_height), (0, 255, 255), -1)
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
    cv2.putText(img, f"Level: {level}", (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

def draw_landmarks_on_image(image, detection_result):
    """Tespit edilen el hareketlerini ekrana çizer ve oyunu kontrol eder."""
    global banana, score, level, xp, xp_max, last_spawn_time, spawn_interval, game_duration, start_time

    hand_landmarks_list = detection_result.hand_landmarks
    annotated_image = np.copy(image)
    h, w, _ = annotated_image.shape

    for hand_landmarks in hand_landmarks_list:
        x8, y8 = koordinat_getir(hand_landmarks, 8, h, w)
        cv2.circle(annotated_image, (x8, y8), 10, (0, 255, 255), 4)

        distance = np.hypot(x8 - (banana["x"] + banana["size"] // 2), y8 - (banana["y"] + banana["size"] // 2))
        if distance < banana["size"] // 2:
            pop_sound.play()
            score += 1
            xp += 1
            banana = yeni_muz_olustur(w, h)
            last_spawn_time = time.time()
            if xp >= xp_max:
                level += 1
                xp = 0
                spawn_interval = max(0.5, spawn_interval - 0.2)
                game_duration += 5

        proto = landmark_pb2.NormalizedLandmarkList()
        proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z) for lm in hand_landmarks
        ])
        mp_drawing.draw_landmarks(
            annotated_image,
            proto,
            mp_hands.HAND_CONNECTIONS,
            mp_styles.get_default_hand_landmarks_style(),
            mp_styles.get_default_hand_connections_style()
        )

    if time.time() - last_spawn_time > muz_max_sure:
        game_duration -= muz_tutulmazsa_zaman_eksi
        banana = yeni_muz_olustur(w, h)
        last_spawn_time = time.time()

    muz_resmi_ciz(annotated_image, banana, banana_img)
    draw_level_bar(annotated_image, xp, xp_max, level)

    elapsed = int(time.time() - start_time)
    kalan = max(0, game_duration - elapsed)
    cv2.putText(annotated_image, f"Skor: {score}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
    cv2.putText(annotated_image, f"Sure: {kalan}s", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    return annotated_image, kalan

# === Ana Oyun Döngüsü ===
while True:
    score = 0
    level = 1
    xp = 0
    xp_max = 5
    spawn_interval = 2.0
    game_duration = 60
    start_time = time.time()
    banana = yeni_muz_olustur(1280, 720)
    last_spawn_time = time.time()
    oyun_bitti = False
    restart_istendi = False

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    for i in [3, 2, 1]:
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, str(i), (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 10)
        cv2.imshow(pencere_ismi, frame)
        cv2.waitKey(1000)

    while cam.isOpened():
        ret, frame = cam.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = detector.detect(mp_image)
        annotated_image, kalan = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)
        frame_to_show = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)

        if kalan <= 0:
            oyun_bitti = True

        if oyun_bitti:
            frame_to_show = cv2.resize(gameover_img, (frame.shape[1], frame.shape[0]))
            if restart_istendi:
                break

        cv2.imshow(pencere_ismi, frame_to_show)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cam.release()
            cv2.destroyAllWindows()
            exit()

    cam.release()
    cv2.destroyAllWindows()
