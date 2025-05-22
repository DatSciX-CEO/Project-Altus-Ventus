
import RPi.GPIO as GPIO
import time

PWM_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)

pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

try:
    while True:
        for dc in range(0, 101, 5):
            pwm.ChangeDutyCycle(dc)
            print(f"PWM duty cycle: {dc}%")
            time.sleep(0.1)
        for dc in range(100, -1, -5):
            pwm.ChangeDutyCycle(dc)
            print(f"PWM duty cycle: {dc}%")
            time.sleep(0.1)
except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()
