import streamlit as st
import time
import random
import pandas as pd # For charts

# --- Configuration & State Initialization ---

DEFAULT_TOP_SPEED = 150
# This was the virtual reference in fan_controller_pwm.py
# We can still use it if we want to maintain the two-step scaling,
# or simplify to scale directly to top_speed for 100% PWM.
# For this integrated version, we'll make the scaling more direct:
# current_speed / top_speed * 100 = PWM.
# The "70 mph real wind" concept is now tied to how the user sets the 'Vehicle Top Speed for Scaling'.
# If they set top_speed to 70, then 70mph in game = 100% PWM.
# If they set top_speed to 150, then 150mph in game = 100% PWM.

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.top_speed = DEFAULT_TOP_SPEED # Inspired by wind_server.py
    st.session_state.current_game_speed_mph = 0.0
    st.session_state.current_pwm_power = 0.0
    st.session_state.simulation_running = False
    st.session_state.manual_speed_mode = False
    st.session_state.manual_speed_setpoint_mph = 0.0
    st.session_state.log_messages = ["Simulator initialized. Welcome!"]
    # Initialize history_data as an empty DataFrame with correct columns
    st.session_state.history_data = pd.DataFrame(columns=['Time', 'Game Speed (mph)', 'PWM Power (%)'])
    st.session_state.start_time = time.time()


# --- Core Logic ---

def calculate_motor_power(current_speed_mph, top_speed_setting):
    """
    Calculates motor power based on current speed and top speed setting.
    The logic is a direct scaling: if current_speed reaches top_speed_setting,
    PWM is 100%.
    This adapts the principle from fan_controller_pwm.py.
    """
    if top_speed_setting <= 0: # Avoid division by zero or negative speeds
        return 0.0
    
    # Direct linear scaling: (current speed / top_speed_for_100_pwm) * 100
    motor_power = (current_speed_mph / top_speed_setting) * 100
    
    motor_power = max(0.0, min(100.0, motor_power)) # Clamp between 0 and 100%
    return motor_power

def add_log(message):
    max_logs = 30 # Increased log history
    st.session_state.log_messages.append(f"{time.strftime('%H:%M:%S')}: {message}")
    if len(st.session_state.log_messages) > max_logs:
        st.session_state.log_messages = st.session_state.log_messages[-max_logs:]

def update_history(game_speed, pwm_power):
    max_history_points = 100
    current_time_elapsed = time.time() - st.session_state.start_time
    new_data_dict = {
        'Time': [current_time_elapsed],
        'Game Speed (mph)': [game_speed],
        'PWM Power (%)': [pwm_power]
    }
    new_data_df = pd.DataFrame(new_data_dict)
    
    st.session_state.history_data = pd.concat([st.session_state.history_data, new_data_df], ignore_index=True)
    
    if len(st.session_state.history_data) > max_history_points:
        st.session_state.history_data = st.session_state.history_data.iloc[-max_history_points:]

# --- Game Telemetry Simulation Step ---
def run_simulation_step():
    if not st.session_state.simulation_running:
        # If simulation is stopped, ensure speed and power reflect this
        if st.session_state.current_game_speed_mph != 0.0: # Only update if not already zero
            st.session_state.current_game_speed_mph = 0.0
            st.session_state.current_pwm_power = calculate_motor_power(
                st.session_state.current_game_speed_mph,
                st.session_state.top_speed
            )
            update_history(st.session_state.current_game_speed_mph, st.session_state.current_pwm_power)
            add_log("Simulation stopped. Speed and PWM set to 0.")
        return

    if st.session_state.manual_speed_mode:
        new_speed = st.session_state.manual_speed_setpoint_mph
        # Log only if speed changed, to avoid flooding logs
        if abs(new_speed - st.session_state.current_game_speed_mph) > 0.01 :
             add_log(f"Manual speed updated to: {new_speed:.2f} mph")
    else: # Random mode
        # Simulate speed: gentle random walk around a baseline, or more dynamic
        baseline_speed = st.session_state.top_speed * 0.4 # Tend towards 40% of top speed
        fluctuation = random.uniform(-st.session_state.top_speed * 0.1, st.session_state.top_speed * 0.1) # Fluctuate by +/-10% of top_speed
        
        # Make changes more gradual from current speed
        change_factor = 0.3 # How much new random value influences current speed
        target_random_speed = baseline_speed + fluctuation
        
        current_speed = st.session_state.current_game_speed_mph
        new_speed = current_speed * (1-change_factor) + target_random_speed * change_factor
        
        max_possible_speed = st.session_state.top_speed
        new_speed = max(0, min(new_speed, max_possible_speed)) # Clamp
        add_log(f"Random speed generated: {new_speed:.2f} mph")

    st.session_state.current_game_speed_mph = new_speed

    st.session_state.current_pwm_power = calculate_motor_power(
        st.session_state.current_game_speed_mph,
        st.session_state.top_speed
    )
    add_log(f"PWM: {st.session_state.current_pwm_power:.2f}% (Speed: {st.session_state.current_game_speed_mph:.2f} mph, Top: {st.session_state.top_speed} mph)")
    update_history(st.session_state.current_game_speed_mph, st.session_state.current_pwm_power)

# --- UI Layout ---
st.set_page_config(layout="wide", page_title="Altus Ventus Simulator")
st.title("💨 Project Altus Ventus - Wind Simulator")
st.markdown("An interactive simulator for the wind generation system. Adjust parameters and observe the real-time simulated output for fan control.")

controls_col, visuals_col = st.columns([1, 2]) # Adjust column ratio if needed

with controls_col:
    st.header("⚙️ Controls")

    # Renamed from original fan_controller_pwm.py's global 'top_speed'
    # and wind_server.py's 'top_speed'
    new_top_speed = st.number_input(
        "Vehicle Top Speed for Scaling (mph):",
        min_value=10, # Sensible minimum
        max_value=300,
        value=st.session_state.top_speed,
        step=10,
        key="top_speed_input",
        help="Set the game speed at which the fan PWM output will reach 100%."
    )
    if new_top_speed != st.session_state.top_speed:
        st.session_state.top_speed = new_top_speed
        add_log(f"Vehicle Top Speed for scaling set to: {st.session_state.top_speed} mph")
        # Recalculate power if top speed changed
        st.session_state.current_pwm_power = calculate_motor_power(
            st.session_state.current_game_speed_mph,
            st.session_state.top_speed
        )

    st.session_state.manual_speed_mode = st.checkbox("Enable Manual Speed Control", value=st.session_state.manual_speed_mode, key="manual_mode_checkbox")

    if st.session_state.manual_speed_mode:
        # Ensure slider value doesn't exceed the current top_speed
        manual_max = float(st.session_state.top_speed)
        current_manual_val = st.session_state.manual_speed_setpoint_mph
        if current_manual_val > manual_max: # Adjust if top_speed was lowered below current manual val
            current_manual_val = manual_max

        new_manual_speed = st.slider(
            "Set Game Speed Manually (mph):",
            min_value=0.0,
            max_value=manual_max,
            value=current_manual_val,
            step=1.0,
            key="manual_speed_slider",
            disabled=not st.session_state.manual_speed_mode
        )
        if new_manual_speed != st.session_state.manual_speed_setpoint_mph:
             st.session_state.manual_speed_setpoint_mph = new_manual_speed
             # If simulation is running in manual mode, this will be picked up by run_simulation_step

    sim_button_text = "Stop Simulation" if st.session_state.simulation_running else "Start Simulation"
    if st.button(sim_button_text, key="sim_toggle_button"):
        st.session_state.simulation_running = not st.session_state.simulation_running
        if st.session_state.simulation_running:
            add_log("Simulation started.")
            st.session_state.start_time = time.time()
            # Reset history only when starting, not every time button is clicked
            st.session_state.history_data = pd.DataFrame(columns=['Time', 'Game Speed (mph)', 'PWM Power (%)'])
        else:
            add_log("Simulation stopped.")
            # run_simulation_step() will handle setting speed/pwm to 0 on next rerun if not running

with visuals_col:
    st.header("📊 Live Status & Visuals")
    
    status_m1, status_m2 = st.columns(2)
    status_m1.metric(label="Current Simulated Game Speed", value=f"{st.session_state.current_game_speed_mph:.1f} mph")
    status_m2.metric(label="Calculated PWM Power", value=f"{st.session_state.current_pwm_power:.1f} %")

    st.subheader("Fan PWM Output Level")
    st.progress(int(st.session_state.current_pwm_power))

    st.subheader("Output History (Last 100 points)")
    if not st.session_state.history_data.empty:
        # Create a chart with a shared Y-axis for Game Speed and PWM Power for better comparison if scales are similar
        # Or, create two separate charts if scales are too different. For now, one chart with two lines.
        chart_df = st.session_state.history_data.set_index('Time')
        st.line_chart(chart_df)
    else:
        st.caption("No history data yet. Start the simulation to populate charts.")

st.header("📝 Event Log")
log_container = st.container(height=250)
for msg in reversed(st.session_state.log_messages):
    log_container.text(msg)

st.markdown("---")
st.caption("This simulator combines and adapts logic from the original project files into a single interactive application for testing and visualization.")

# --- Main Simulation Loop Control ---
if st.session_state.simulation_running:
    run_simulation_step() # Update game state
    time.sleep(0.1) # Update frequency (10 Hz for smoother charts)
    try:
        st.rerun() # Trigger rerun to update UI and continue loop
    except st.errors.ScriptThreadControlException: # Handle potential errors during rerun if app is closing
        pass
elif not st.session_state.simulation_running and st.session_state.current_game_speed_mph != 0.0:
    # If simulation was just stopped, ensure speed is set to 0 and UI updates one last time.
    run_simulation_step()
    try:
        st.rerun()
    except st.errors.ScriptThreadControlException:
        pass