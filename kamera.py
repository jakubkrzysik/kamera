#!/usr/bin/env python3
import time
import base64
import requests
import cv2
import RPi.GPIO as GPIO
from picamera2 import Picamera2

BUTTON_GPIO = 4
SERVER_URL = 'http://192.168.1.100:5000/upload'

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (2592, 1944)})
picam2.configure(config)
picam2.start()

def capture_and_send():
    print("Robię zdjęcie...")
    try:
        image = picam2.capture_array()
    except Exception as e:
        print("Błąd przy przechwytywaniu obrazu:", e)
        return
    ret, jpeg = cv2.imencode('.jpg', image)
    if not ret:
        print("Błąd przy kodowaniu obrazu do JPEG!")
        return
    jpeg_bytes = jpeg.tobytes()
    encoded_image = base64.b64encode(jpeg_bytes).decode('utf-8')
    payload = {"image": encoded_image, "timestamp": time.time()}
    try:
        response = requests.post(SERVER_URL, json=payload)
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
