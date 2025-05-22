import time
import socket
import json
import requests # For fetching top_speed from the web server

# PWM_PIN = 18 # No GPIO in simulation
# FREQUENCY = 1000 # No GPIO in simulation

# GPIO.setmode(GPIO.BCM) # No GPIO
# GPIO.setup(PWM_PIN, GPIO.OUT) # No GPIO
# pwm = GPIO.PWM(PWM_PIN, FREQUENCY) # No GPIO
# pwm.start(0) # No GPIO

UDP_IP = ""  # Listen on all available interfaces
UDP_PORT = 4444 #

# Global variable for top_speed, will be updated from server
# Initialize with a default, same as in original fan_controller_pwm.py and wind_server.py
#
top_speed = 150
wind_server_url = "http://127.0.0.1:5000/get_top_speed_api"
last_top_speed_fetch_time = 0
TOP_SPEED_FETCH_INTERVAL = 5 # Seconds

def fetch_top_speed_from_server():
    global top_speed, last_top_speed_fetch_time
    current_time = time.time()
    if current_time - last_top_speed_fetch_time > TOP_SPEED_FETCH_INTERVAL:
        try:
            response = requests.get(wind_server_url, timeout=0.5) # Short timeout
            response.raise_for_status() # Raise an exception for HTTP errors
            data = response.json()
            new_top_speed = data.get("top_speed")
            if new_top_speed is not None and isinstance(new_top_speed, (int, float)) and new_top_speed > 0:
                if top_speed != new_top_speed:
                    print(f"Updated top_speed from server: {new_top_speed} mph")
                    top_speed = new_top_speed
            else:
                print(f"Warning: Received invalid top_speed data from server: {data}")
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch top_speed from server: {e}")
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from top_speed server response.")
        last_top_speed_fetch_time = current_time

def calculate_motor_power(current_speed):
    global top_speed # Use the global top_speed updated from the server
    # Logic from fan_controller_pwm.py
    max_game_speed = top_speed
    if max_game_speed <= 0: # Avoid division by zero if top_speed is not set properly
        return 0
    max_real_wind = 70 # Virtual reference for scaling

    real_wind_speed = (current_speed / max_game_speed) * max_real_wind
    motor_power = (real_wind_speed / max_real_wind) * 100
    motor_power = max(0, min(100, motor_power)) # Clamp between 0 and 100
    return motor_power

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT)) #
sock.settimeout(0.1) #

print(f"Simulated Fan Controller started.")
print(f"Listening for UDP packets on port {UDP_PORT}")
print(f"Fetching top_speed from {wind_server_url}")
print("Press Ctrl+C to stop.")

try:
    while True:
        fetch_top_speed_from_server() # Periodically update top_speed
        try:
            data, addr = sock.recvfrom(1024) #
            telemetry = json.loads(data.decode()) #
            vel = telemetry.get("vel", [0,0,0]) #
            # Assuming y-axis is forward as in fan_controller_pwm.py
            speed_mps = vel[1]
            speed_mph = speed_mps * 2.237 # Convert m/s to mph

            power = calculate_motor_power(speed_mph)
            # Instead of GPIO control, print the simulated output
            # pwm.ChangeDutyCycle(power) # Original GPIO line
            print(f"Received Speed: {speed_mph:.2f} mph (Top Speed: {top_speed} mph) -> Simulated PWM Power: {power:.2f}%")
        except socket.timeout: #
            pass
        except Exception as e:
            print(f"Error in main loop: {e}") #
        time.sleep(0.02) #
finally:
    # pwm.stop() # No GPIO
    # GPIO.cleanup() # No GPIO
    sock.close()
    print("Simulated Fan Controller stopped.")