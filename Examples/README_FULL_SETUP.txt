
Final BeamNG Fan Control Integration
====================================

Includes:
- Python web server to set top speed (Flask)
- Realistic 0–70mph wind curve with PWM fan output on Raspberry Pi
- BeamMP-compatible telemetry mod
- Test script for PWM fan
- systemd service (optional)

PART 1 - BeamMP SERVER SETUP
----------------------------
1. Go to your BeamMP server folder:
   BeamMP-Server/Resources/client/

2. Create folder:
   beamng_telemetry/

3. Place 'main.lua' inside:
   BeamMP-Server/Resources/client/beamng_telemetry/main.lua

4. In 'main.lua', REPLACE `YOUR_PI_IP_HERE` with your Raspberry Pi's IP address.

5. Restart the BeamMP server.

All players will auto-run this telemetry when they join.

PART 2 - RASPBERRY PI SETUP
---------------------------
1. Copy these files to your Raspberry Pi.

2. Install dependencies:
   sudo apt update
   sudo apt install python3-pip python3-rpi.gpio
   pip3 install flask

3. Wire GPIO 18 (Pin 12, BCM mode) to your MOSFET/motor driver.

4. Start web server:
   python3 wind_server.py
   Open in browser: http://<pi-ip>:5000

5. Set top speed of current car manually in the browser.

6. Run fan controller:
   python3 fan_controller_pwm.py

PART 3 - TEST FAN
-----------------
To test your motor/fan manually:
   python3 motor_test.py

PART 4 - SYSTEMD AUTOSTART (optional)
-------------------------------------
Use fan_control.service file if you want the Pi to autostart this on boot.

Make sure to replace paths inside the service file.

SAFETY
------
- Do NOT power your motor directly from Pi GPIO!
- Use a proper MOSFET or motor driver.
- Use a flyback diode for motors (not just fans).
- Ensure common ground between Pi and fan power supply.

CHANGING BEHAVIOR
-----------------
- Edit fan_controller_pwm.py to adjust curve, GPIO pin, or top speed handling.
- Edit wind_server.py to modify web interface (Flask).
- Edit main.lua to change telemetry update rate or data sent.

Enjoy your BeamNG wind simulator!
