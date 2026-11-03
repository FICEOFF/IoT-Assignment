import RPi.GPIO as GPIO
import threading, time

RGB_PINS = (15, 16, 18)

RGB_COLORS = {
    "red": (0, 1, 1),
    "yellow": (0, 0, 1),
    "green": (1, 0, 1),
    "cyan": (1, 0, 0),
    "blue": (1, 1, 0),
    "magenta": (0, 1, 0),
    "white": (0, 0, 0),
    "off": (1, 1, 1)
}

rgb_state = "off"
rgb_lock = threading.Lock()

def setup():
    GPIO.setmode(GPIO.BOARD)
    for pin in RGB_PINS:
        GPIO.setup(pin, GPIO.OUT, initial=1)

def cleanup():
    GPIO.cleanup(RGB_PINS)

def set_rgb(color):
    values = RGB_COLORS[color]
    global rgb_state
    with rgb_lock:
        for pin, value in zip(RGB_PINS, values):
            GPIO.output(pin, value)
        rgb_state = color

def get_rgb():
    with rgb_lock:
        return rgb_state

if __name__ == "__main__":
    setup()
    try:
        while True:
            for color in RGB_COLORS:
                set_rgb(color)
                print(f"RGB: {get_rgb()}")
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[QUIT] Stopping program...")
    finally:
        set_rgb("off")
        cleanup()
