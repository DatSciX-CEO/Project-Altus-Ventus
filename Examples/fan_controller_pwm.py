
import time
import socket
import json
import RPi.GPIO as GPIO

PWM_PIN = 18
FREQUENCY = 1000

GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, FREQUENCY)
pwm.start(0)

UDP_IP = ""
UDP_PORT = 4444

top_speed = 150  # Default top speed, can be set from web server

def calculate_motor_power(current_speed):
    # Realistic wind curve mapping
    # Map 0-250 mph game speed to 0-70 mph real wind speed
    # Use a curve that maps linear real wind speed from 0-70 mph
    # and scales motor power PWM accordingly (0-100%)
    max_game_speed = top_speed
    max_real_wind = 70

    # Convert game speed to real wind speed linearly
    real_wind_speed = (current_speed / max_game_speed) * max_real_wind
    motor_power = (real_wind_speed / max_real_wind) * 100
    motor_power = max(0, min(100, motor_power))
    return motor_power

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.1)

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            telemetry = json.loads(data.decode())
            vel = telemetry.get("vel", [0,0,0])
            speed = (vel[1] * 2.237)  # Convert m/s to mph (assuming y axis is forward)
            power = calculate_motor_power(speed)
            pwm.ChangeDutyCycle(power)
            print(f"Speed: {speed:.2f} mph, PWM power: {power:.2f}%")
        except socket.timeout:
            pass
        except Exception as e:
            print("Error:", e)
        time.sleep(0.02)
finally:
    pwm.stop()
    GPIO.cleanup()
