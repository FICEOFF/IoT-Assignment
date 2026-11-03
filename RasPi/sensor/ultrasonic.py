import RPi.GPIO as GPIO
import time

TRIG_PIN = 11
ECHO_PIN = 13

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIG_PIN, GPIO.OUT, initial=0)
    GPIO.setup(ECHO_PIN, GPIO.IN)

def cleanup():
    GPIO.cleanup((TRIG_PIN, ECHO_PIN))

def read_distance():
    GPIO.output(TRIG_PIN, 0)
    time.sleep(0.05)
    GPIO.output(TRIG_PIN, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, 0)
    pulse_start = time.time()
    timeout = pulse_start + 0.05
    while not GPIO.input(ECHO_PIN):
        pulse_start = time.time()
        if pulse_start > timeout:
            return None
    pulse_end = pulse_start
    timeout = pulse_start + 0.05
    while GPIO.input(ECHO_PIN):
        pulse_end = time.time()
        if pulse_end > timeout:
            return None
    return round((pulse_end - pulse_start) * 17150.0, 1)

if __name__ == "__main__":
    setup()
    try:
        while True:
            distance = read_distance()
            if distance is None:
                print("[ERROR] No echo received")
            else:
                print(f"Distance: {distance} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[QUIT] Stopping program...")
    finally:
        cleanup()
