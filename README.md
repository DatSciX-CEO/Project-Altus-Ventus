# Project Altus Ventus: Immersive Wind Simulation for Racing Games

**Current Status: Initial Brainstorming & Prototyping Phase**

This document outlines the concept, proposed architecture, and initial development ideas for Project Altus Ventus. The goal is to develop a physical wind simulation system that interfaces with PC racing games (initially BeamNG.drive) to provide a more immersive experience by translating in-game speed into safe, perceptible airflow.

## 1. Project Overview

Project Altus Ventus aims to create a responsive wind effect for racing simulators. By translating in-game vehicle speed into tangible, safe indoor airflow, we intend to enhance the player's sense of speed and immersion. The system is envisioned to be a relatively low-cost solution.

### 1.1. Needs Statement
To develop a cost-effective wind simulator that uses in-game data to control fan output, simulating the *sensation* of wind speeds (e.g., up to a virtual 70 mph equivalent) and translating this into safe and logical indoor airflow levels. [cite: 1]

### 1.2. Key Criteria & Constraints
* **Performance**: Simulate the sensation of significant virtual wind speeds (e.g., 70+ mph equivalent)[cite: 2], translated to safe and responsive indoor airflow.
* **Responsiveness**: Utilize in-game data for real-time fan control. [cite: 2]
* **Cost**: Be a "cheaper" alternative to existing commercial solutions. [cite: 2]
* **Components**: Utilize a brushless motor and allow for wall power. [cite: 2]
* **Control**: Include a built-in program and potentially a control panel. [cite: 2]
* **Quietness**: Aim for a quiet operation. [cite: 2]

## 2. Proposed System Architecture

The system will consist of several key parts working in conjunction:

1.  **PC (Gaming Computer)**:
    * Runs the racing game (e.g., BeamNG.drive).
    * A telemetry script/mod extracts vehicle speed data from the game.
2.  **Network Communication**:
    * Vehicle speed data is sent from the PC to the control device (e.g., Raspberry Pi) over the local network, likely using UDP.
3.  **Control Device (e.g., Raspberry Pi)**:
    * Receives speed data.
    * Runs Python scripts to process this data and calculate the appropriate fan intensity based on a configurable scale.
    * Outputs a PWM (Pulse Width Modulation) signal (0-100%) to a motor controller.
    * Hosts a simple web server (Flask app) to allow manual setting of parameters like the vehicle's top speed for calibration of the scaling logic.
4.  **Fan Assembly**:
    * A motor controller receives the PWM signal and drives a powerful motor/fan.
    * Physical enclosure and nozzles (as per design ideas in `Overview.docx` [cite: 3]) to direct airflow towards the user.

## 3. Hardware Components (Initial List)

* **Control Device**: Raspberry Pi (e.g., Pi 5) [cite: 3] or a similar single-board computer (SBC) with GPIO capabilities.
* **Motor**: Brushless motor [cite: 2] capable of driving a fan to produce desired airflow.
* **Motor Controller/Driver**: MOSFET or a dedicated motor driver (e.g., L298N) [cite: 3, 63] to interface between the Pi's GPIO and the motor. This is critical as the Pi cannot directly power the motor. [cite: 3, 54, 62]
* **Fan**: Suitable fan blade assembly.
* **Power Supplies**: Separate power supplies for the control device and the motor. [cite: 25]
* **Flyback Diode**: For motor control to protect electrical components. [cite: 3, 55, 63]
* **Wiring & Connectors**.
* **(Optional) Enclosure**: Custom-designed housing for the fan and nozzles. [cite: 3]

## 4. Software Components & Wind Scaling Logic

The core of the system's safety and effectiveness lies in how in-game speed is translated (scaled) to the fan's output (PWM duty cycle from 0-100%). The goal is *not* to replicate literal high-speed winds indoors, but to create a *perceptible and logical representation* of speed.

### 4.1. PC-Side (Game Telemetry)
* **`main.lua` (for BeamMP/BeamNG.drive)**:
    * A Lua script to be placed in the BeamMP server's client resources (`BeamMP-Server/Resources/client/beamng_telemetry/main.lua`).
    * Captures vehicle velocity (`vel = {x, y, z}`) from the game.
    * Sends this data as a JSON string via UDP to the Raspberry Pi's IP address (configurable in the script) on port 4444.
    * Restarting the BeamMP server makes this script active for all connecting players.
* **Alternative: BeamNGpy**:
    * The `Overview.docx` also details using the BeamNGpy Python library on the Raspberry Pi to connect directly to BeamNG.drive running on the PC. [cite: 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22] This involves installing `beamngpy` on the Pi and enabling the mod in BeamNG.drive. [cite: 11, 12, 13, 14]

### 4.2. Raspberry Pi (or other SBC) Side
* **`fan_controller_pwm.py`**:
    * The main Python script for fan control.
    * Listens for UDP packets containing speed data from the game PC.
    * Parses the speed data.
    * **Wind Scaling Logic**: Calculates the required PWM duty cycle (0-100%) for the fan. This is based on:
        * `current_speed`: The vehicle's speed from the game.
        * `top_speed`: The maximum speed of the current in-game vehicle, set via the `wind_server.py` web interface. This allows calibration for different cars.
        * `max_real_wind`: A reference parameter (e.g., 70 mph as in the script). This is **not a target indoor wind speed** but a virtual reference point for the *intensity scaling curve*. The script maps the `current_speed` (relative to `top_speed`) to a point on this virtual wind scale, which then translates to a PWM percentage.
        * The script uses a linear mapping: `real_wind_speed = (current_speed / max_game_speed) * max_real_wind`, then `motor_power = (real_wind_speed / max_real_wind) * 100`.
    * Uses `RPi.GPIO` library (or equivalent for other SBCs) to output PWM signal to the motor controller via a designated GPIO pin (e.g., GPIO18).
* **`wind_server.py`**:
    * A Flask-based Python web application. [cite: 49, 66]
    * Allows the user to manually set the `top_speed` of the vehicle in-game via a web browser (e.g., `http://<pi-ip>:5000`). This is crucial for the scaling logic to work correctly for different vehicles.
* **`motor_test.py`**:
    * A standalone Python script to test the PWM motor/fan setup by cycling the duty cycle. Useful for initial hardware verification.
* **Conceptual Wind Curve (`fan_controller.py` / `Overview.docx`)**:
    * An alternative, more dynamic scaling uses a quadratic curve: `power = (real_wind_equivalent / max_real_wind_speed) ** 2 * max_power`. [cite: 27] This makes lower speeds produce much less wind, and higher speeds ramp up more significantly, potentially offering a more "realistic" feel. [cite: 26]
    * **Desired Subjective Feel (Example from `Overview.docx` [cite: 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48])**:
        | Game Speed (mph) | Target Wind Power Feel (%) | Notes         |
        |------------------|----------------------------|---------------|
        | 0                | 0                          | No wind       |
        | 20               | 10                         | Gentle breeze |
        | 40               | 25                         | Light fan     |
        | 60               | 50                         | Medium wind   |
        | 80               | 75                         | Strong wind   |
        | 100              | 90                         | Almost full   |
        | Vehicle Top Speed| 100                        | Full blast    |
      This table illustrates the desired *subjective output levels*, not literal wind speeds.
* **Dependencies**:
    * `python3-pip`, `python3-rpi.gpio` (for Raspberry Pi)
    * `flask` (Python library)
    * These are installed via `apt` and `pip`.

### 4.3. Adapting the Logic for Safe Indoor Use
The key is that the `max_real_wind` parameter (e.g., 70 mph) in the scripts serves as a *reference for the intensity curve*. The actual airflow experienced by the user will depend on:
1.  The fan's capabilities at 100% PWM.
2.  The chosen scaling curve (linear, quadratic).
3.  The physical setup (distance from fan, nozzles).

Users should adjust the scaling logic or `max_real_wind` parameter in the `fan_controller_pwm.py` script to achieve a comfortable and safe range of airflow, from a gentle breeze at low game speeds to a strong but not overpowering rush of air at high game speeds, corresponding to the "Wind Power Feel" table.

## 5. Setup and Operation (Conceptual)

### 5.1. Raspberry Pi Setup
1.  Install dependencies: `sudo apt update`, `sudo apt install python3-pip python3-rpi.gpio`, `pip3 install flask`.
2.  Wire the motor to the designated GPIO pin (e.g., GPIO18) via the motor controller.
3.  Copy the Python scripts (`fan_controller_pwm.py`, `wind_server.py`, `motor_test.py`) to the Pi.
4.  Start the web server: `python3 wind_server.py`. Access it at `http://<pi-ip>:5000` to set the vehicle's top speed for calibration.
5.  In a separate terminal, run the fan controller: `python3 fan_controller_pwm.py`.

### 5.2. PC (BeamMP Server) Setup
1.  Navigate to your BeamMP server folder: `BeamMP-Server/Resources/client/`.
2.  Create a folder: `beamng_telemetry/`.
3.  Place `main.lua` inside this folder.
4.  **Crucially**, edit `main.lua` to replace `YOUR_PI_IP_HERE` with your Raspberry Pi's actual IP address.
5.  Restart the BeamMP server.

### 5.3. Testing
* Use `motor_test.py` on the Pi to verify fan control hardware and its maximum safe output.
* Ensure PC and Pi are on the same network. [cite: 18, 20]
* Start BeamNG.drive (e.g., in Free Roam). [cite: 21]
* The fan should respond to in-game speed changes according to the scaling logic.

## 6. Safety Precautions (IMPORTANT!)

* **The system is intended to produce safe levels of indoor airflow, scaled logically from game speeds.** The "70 mph" often mentioned is a *virtual reference* for scaling the *sensation of speed*, not a literal target for indoor wind velocity.
* **DO NOT power the fan/motor directly from the Raspberry Pi's GPIO pins!** [cite: 3, 54, 62] Always use a suitable motor driver or MOSFET. [cite: 3, 63]
* **Use a proper MOSFET or motor driver**. [cite: 3, 63]
* **Ensure common ground** between the Pi and the motor's power supply. [cite: 3, 55, 64]
* **Use a flyback diode** if using a motor (not just a fan) to protect components from back-EMF. [cite: 3, 55, 63]
* Ensure your motor power supply is separate from the Pi’s power (e.g., a 12V adapter for the fan). [cite: 25]
* **Calibrate and test** the system to ensure the maximum airflow generated is comfortable and safe for an indoor environment.

## 7. Customization and Future Development

* **Wind Curve Adjustment**: Modify `calculate_motor_power` in `fan_controller_pwm.py` to change how fan power scales with game speed (e.g., implement a quadratic curve for more realism as suggested in `Overview.docx` [cite: 26, 27] and `fan_controller.py`). This is key to tailoring the safe indoor wind feel.
* **Web Interface**: Enhance `wind_server.py` for more features or a better UI.
* **Telemetry Data**: Modify `main.lua` to change the update rate or data sent.
* **Systemd Autostart**: Create a systemd service (`fan_control.service` mentioned in `README_FULL_SETUP.txt`) to automatically start the scripts on Pi boot. Paths within the service file would need to be correct.
* **Alternative SBCs**: Explore using other single-board computers if a Raspberry Pi is not suitable, adapting GPIO control libraries as needed.
* **Physical Enclosure**: Develop the physical enclosure and nozzle design further (TinkerCad ideas mentioned in `Overview.docx` [cite: 3]).

## 8. Contributing

This project is currently in the early brainstorming and conceptual phase. Ideas, contributions, and suggestions are welcome as it evolves.

---
*This README is based on initial project notes and example files. It will be updated as the project progresses.*