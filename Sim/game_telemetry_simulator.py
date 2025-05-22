import socket
import time
import json
import random

UDP_TARGET_IP = "127.0.0.1"  # Localhost
UDP_TARGET_PORT = 4444

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Game Telemetry Simulator started.")
print(f"Sending UDP packets to {UDP_TARGET_IP}:{UDP_TARGET_PORT}")
print("Press Ctrl+C to stop.")

try:
    while True:
        # Simulate game speed between 0 and 200 mph
        simulated_speed_mph = random.uniform(0, 200)

        # Convert mph to m/s (as fan_controller_pwm.py expects vel[1] in m/s)
        # 1 mph = 0.44704 m/s
        simulated_speed_mps = simulated_speed_mph * 0.44704

        # Create telemetry data (assuming y-axis is forward)
        telemetry_data = {"vel": [0, simulated_speed_mps, 0]}
        message = json.dumps(telemetry_data).encode('utf-8')

        sock.sendto(message, (UDP_TARGET_IP, UDP_TARGET_PORT))
        print(f"Sent: Speed MPH = {simulated_speed_mph:.2f}, Data = {telemetry_data}")

        time.sleep(0.1)  # Send data 10 times per second

except KeyboardInterrupt:
    print("\nSimulator stopped.")
finally:
    sock.close()