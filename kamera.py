#!/usr/bin/env python3
import time
import requests
import RPi.GPIO as GPIO
from picamera2 import Picamera2

BUTTON_GPIO = 4
SERVER_URL = 'http://147.185.221.25:35182/upload'
IMAGE_PATH = "/home/pi/captured_image.jpg"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (2592, 1944)}, lores={"size": (640, 480)}, display="lores")
picam2.configure(config)
picam2.start()

def capture_and_send():
    print("Robię zdjęcie...")
    try:
        picam2.capture_file(IMAGE_PATH, format="jpeg")  # Zapis obrazu natywnie w formacie JPEG
    except Exception as e:
        print("Błąd przy przechwytywaniu obrazu:", e)
        return
    
    # Wysłanie obrazu jako plik multipart/form-data
    try:
        with open(IMAGE_PATH, 'rb') as img_file:
            files = {'image': img_file}
            response = requests.post(SERVER_URL, files=files)
        print("Obraz wysłany. Odpowiedź serwera:", response.text)
    except Exception as e:
        print("Błąd przy wysyłaniu obrazu:", e)

def button_callback(channel):
    print("Przycisk naciśnięty!")
    capture_and_send()

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
    picam2.stop()
