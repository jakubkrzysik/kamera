#!/usr/bin/env python3
import time
import base64
import requests
import cv2
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# -----------------------------------------
# Konfiguracja ustawień
# -----------------------------------------
BUTTON_GPIO = 17  # Numer pinu GPIO, do którego podłączony jest przycisk.
SERVER_URL = 'http://192.168.1.100:5000/upload'  # Adres Twojego serwera – dostosuj!

# -----------------------------------------
# Inicjalizacja GPIO
# -----------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# -----------------------------------------
# Inicjalizacja kamery (Picamera2)
# -----------------------------------------
picam2 = Picamera2()
# Konfiguracja trybu "still" dla kamery OV5647 (5 MP) – maksymalna rozdzielczość 2592×1944
config = picam2.create_still_configuration(main={"size": (2592, 1944)})
picam2.configure(config)
picam2.start()

# -----------------------------------------
# Funkcja przechwytująca obraz i wysyłająca go na serwer
# -----------------------------------------
def capture_and_send():
    print("Robię zdjęcie...")
    try:
        # Pobieramy obraz jako tablicę numpy
        image = picam2.capture_array()
    except Exception as e:
        print("Błąd przy przechwytywaniu obrazu:", e)
        return

    # Kodujemy obraz do formatu JPEG
    ret, jpeg = cv2.imencode('.jpg', image)
    if not ret:
        print("Błąd przy kodowaniu obrazu do JPEG!")
        return
    jpeg_bytes = jpeg.tobytes()

    # Konwersja do base64
    encoded_image = base64.b64encode(jpeg_bytes).decode('utf-8')

    # Przygotowanie danych do wysłania (np. w formacie JSON)
    payload = {
        "image": encoded_image,
        "timestamp": time.time()
    }

    try:
        response = requests.post(SERVER_URL, json=payload)
        print("Obraz wysłany. Odpowiedź serwera:", response.text)
    except Exception as e:
        print("Błąd przy wysyłaniu obrazu:", e)

# -----------------------------------------
# Callback wywoływany przy naciśnięciu przycisku
# -----------------------------------------
def button_callback(channel):
    print("Przycisk naciśnięty!")
    capture_and_send()

GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=300)

# -----------------------------------------
# Główna pętla programu
# -----------------------------------------
try:
    print("Program uruchomiony, oczekiwanie na naciśnięcie przycisku...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Kończenie programu...")
finally:
    GPIO.cleanup()
    picam2.stop()
