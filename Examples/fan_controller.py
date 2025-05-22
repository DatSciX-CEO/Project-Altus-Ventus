
import time
import socket
import json
from wind_server import get_top_speed  # Fetch top speed set in web app

# --- Realistic Wind Power Calculation ---
def calculate_motor_power(speed_mph, top_speed, max_real_wind_speed=70, max_power=100):
    if top_speed < 5:
        return 0  # Avoid division errors early on

    normalized_speed = speed_mph / top_speed
    real_wind_equivalent = normalized_speed * max_real_wind_speed
    power = (real_wind_equivalent / max_real_wind_speed) ** 2 * max_power
    return min(max(power, 0), max_power)

# --- Connect to BeamNG telemetry ---
def connect_to_beamng(port=4444):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.settimeout(1.0)
    return sock

# --- Parse BeamNG vehicle speed from telemetry ---
def get_vehicle_speed_mph(data):
    try:
        telemetry = json.loads(data.decode("utf-8"))
        velocity = telemetry["vel"]  # vel = [x, y, z] in m/s
        speed_mps = (velocity[0] ** 2 + velocity[1] ** 2 + velocity[2] ** 2) ** 0.5
        return speed_mps * 2.237  # m/s → mph
    except (KeyError, json.JSONDecodeError):
        return 0

# --- MAIN LOOP ---
def main():
    print("Starting fan control system...")
    sock = connect_to_beamng()

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            current_speed_mph = get_vehicle_speed_mph(data)
            top_speed = get_top_speed()  # From Flask web app

            power = calculate_motor_power(current_speed_mph, top_speed)

            # --- Send power to fan motor ---
            print(f"Speed: {current_speed_mph:.1f} mph | Top Speed: {top_speed:.1f} mph | Fan Power: {power:.1f}%")
            # Here, replace with actual motor control code e.g. PWM output

        except socket.timeout:
            print("Waiting for data from BeamNG...")
        except KeyboardInterrupt:
            print("Exiting...")
            break

        time.sleep(0.05)  # Smooth updates ~20 Hz

if __name__ == "__main__":
    main()
