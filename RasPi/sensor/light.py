import RPi.GPIO as GPIO
import time

LIGHT_PIN = 22

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LIGHT_PIN, GPIO.IN)

def cleanup():
    GPIO.cleanup(LIGHT_PIN)

def read_light():
    return "dark" if GPIO.input(LIGHT_PIN) else "bright"

if __name__ == "__main__":
    setup()
    try:
        while True:
            print(f"[{read_light().upper()}]")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[QUIT] Stopping program...")
    finally:
        cleanup()
