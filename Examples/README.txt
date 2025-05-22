
Advanced BeamNG Fan Control (PWM Edition)
-----------------------------------------

This setup reads in-game speed from BeamNG, lets you manually set top speed via web, and outputs realistic wind-like PWM to a motor or fan.

Files Included:
---------------
- fan_controller_pwm.py : Main PWM fan control script
- motor_test.py         : Standalone script to test motor/fan response
- wind_server.py        : Web server to set the top speed
- README.txt            : You're reading it!

Setup Instructions:
-------------------
1. Install dependencies on Raspberry Pi:
   sudo apt update
   sudo apt install python3-pip python3-rpi.gpio
   pip3 install flask

2. Wire the motor to GPIO18 (pin 12, BCM numbering) via MOSFET or motor controller.
   IMPORTANT: Do not power fan directly from Pi!

3. Start the web app:
   python3 wind_server.py
   Then open browser to: http://<pi-ip>:5000

4. In a second terminal, run the fan controller:
   python3 fan_controller_pwm.py

5. Use 'motor_test.py' to manually test your PWM motor setup:
   python3 motor_test.py

6. To autostart the fan controller on boot, ask to set up systemd later.

Safety:
-------
- Always use common ground between Pi and motor power
- Use a flyback diode if using a motor (not just a fan)

