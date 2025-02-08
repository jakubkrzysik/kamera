#!/usr/bin/env python3
import time
import requests
import RPi.GPIO as GPIO
from libcamera import controls
from libcamera import CameraManager
import subprocess

BUTTON_GPIO = 4
SERVER_URL = 'http://147.185.221.25:35182/upload'
IMAGE_PATH = "/home/pi/captured_image.jpg"

# Konfiguracja GPIO dla przycisku
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Konfiguracja kamery libcamera
def capture_image():
    print("Robię zdjęcie...")
    try:
        # Użycie natywnego polecenia `libcamera-still` do przechwycenia obrazu
        subprocess.run([
            "libcamera-still",
            "--width", "2592", "--height", "1944",  # Maksymalna rozdzielczość
            "--shutter", "10000",  # Czas naświetlania w mikrosekundach (zwiększ jeśli obraz nadal jest ciemny)
            "--gain", "2.0",  # ISO (możesz spróbować wyższych wartości, np. 4.0)
            "--awb", "auto",  # Automatyczny balans bieli
            "--quality", "100",  # Maksymalna jakość JPEG
            "--output", IMAGE_PATH  # Zapis obrazu do pliku
        ])
        print("Zdjęcie zapisane.")
    except Exception as e:
        print(f"Błąd przy robieniu zdjęcia: {e}")
        return False
    return True

def send_image():
    print("Wysyłanie obrazu na serwer...")
    try:
        with open(IMAGE_PATH, 'rb') as img_file:
            files = {'image': img_file}
            response = requests.post(SERVER_URL, files=files)
        print("Obraz wysłany. Odpowiedź serwera:", response.text)
    except Exception as e:
        print(f"Błąd przy wysyłaniu obrazu: {e}")

def button_callback(channel):
    print("Przycisk naciśnięty!")
    if capture_image():
        send_image()

print("Program uruchomiony, oczekiwanie na naciśnięcie przycisku...")
try:
    while True:
        if GPIO.input(BUTTON_GPIO) == GPIO.LOW:
            button_callback(BUTTON_GPIO)
            time.sleep(0.3)  # debouncing
        time.sleep(0.05)
except KeyboardInterrupt:
    print("Kończenie programu...")
finally:
    GPIO.cleanup()
