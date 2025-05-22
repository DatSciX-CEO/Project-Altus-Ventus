import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go # Import Plotly

# --- Configuration & State Initialization ---
DEFAULT_TOP_SPEED = 70

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.top_speed = DEFAULT_TOP_SPEED
    st.session_state.current_game_speed_mph = 0.0
    st.session_state.current_pwm_power = 0.0
    st.session_state.simulation_running = False
    st.session_state.manual_speed_mode = False
    st.session_state.manual_speed_setpoint_mph = 0.0
    st.session_state.log_messages = ["Simulator initialized. Welcome!"]
    st.session_state.history_data = pd.DataFrame(columns=['Time', 'Game Speed (mph)', 'PWM Power (%)'])
    st.session_state.start_time = time.time()

# --- Core Logic ---
def calculate_motor_power(current_speed_mph, top_speed_setting):
    if top_speed_setting <= 0:
        return 0.0
    motor_power = (current_speed_mph / top_speed_setting) * 100
    motor_power = max(0.0, min(100.0, motor_power))
    return motor_power

def add_log(message):
    max_logs = 30
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
        if st.session_state.current_game_speed_mph != 0.0:
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
        if abs(new_speed - st.session_state.current_game_speed_mph) > 0.01 :
             add_log(f"Manual speed updated to: {new_speed:.2f} mph")
    else: 
        baseline_speed = st.session_state.top_speed * 0.4 
        fluctuation = random.uniform(-st.session_state.top_speed * 0.1, st.session_state.top_speed * 0.1)
        change_factor = 0.3
        target_random_speed = baseline_speed + fluctuation
        current_speed = st.session_state.current_game_speed_mph
        new_speed = current_speed * (1-change_factor) + target_random_speed * change_factor
        max_possible_speed = st.session_state.top_speed
        new_speed = max(0, min(new_speed, max_possible_speed))
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

controls_col, visuals_col = st.columns([1, 2])

with controls_col:
    st.header("⚙️ Controls")
    new_top_speed = st.number_input(
        "Vehicle Top Speed for Scaling (mph):",
        min_value=10, 
        max_value=300,
        value=st.session_state.top_speed,
        step=10,
        key="top_speed_input",
        help="Set the game speed at which the fan PWM output will reach 100%."
    )
    if new_top_speed != st.session_state.top_speed:
        st.session_state.top_speed = new_top_speed
        add_log(f"Vehicle Top Speed for scaling set to: {st.session_state.top_speed} mph")
        st.session_state.current_pwm_power = calculate_motor_power(
            st.session_state.current_game_speed_mph,
            st.session_state.top_speed
        )

    st.session_state.manual_speed_mode = st.checkbox("Enable Manual Speed Control", value=st.session_state.manual_speed_mode, key="manual_mode_checkbox")

    if st.session_state.manual_speed_mode:
        manual_max = float(st.session_state.top_speed)
        current_manual_val = st.session_state.manual_speed_setpoint_mph
        if current_manual_val > manual_max: 
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
             
    sim_button_text = "Stop Simulation" if st.session_state.simulation_running else "Start Simulation"
    if st.button(sim_button_text, key="sim_toggle_button"):
        st.session_state.simulation_running = not st.session_state.simulation_running
        if st.session_state.simulation_running:
            add_log("Simulation started.")
            st.session_state.start_time = time.time()
            st.session_state.history_data = pd.DataFrame(columns=['Time', 'Game Speed (mph)', 'PWM Power (%)'])
        else:
            add_log("Simulation stopped.")
            
with visuals_col:
    st.header("📊 Live Status & Visuals")
    
    status_m1, status_m2 = st.columns(2)
    status_m1.metric(label="Current Simulated Game Speed", value=f"{st.session_state.current_game_speed_mph:.1f} mph")
    status_m2.metric(label="Calculated PWM Power", value=f"{st.session_state.current_pwm_power:.1f} %")

    st.subheader("Fan PWM Output Level (Gauge)")
    gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = st.session_state.current_pwm_power,
        title = {'text': "PWM (%)", 'font': {'size': 16}}, # Smaller title font
        gauge = {'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                 'bar': {'color': "royalblue"},
                 'bgcolor': "white",
                 'borderwidth': 2,
                 'bordercolor': "gray",
                 'steps' : [
                     {'range': [0, 33], 'color': "lightgreen"},
                     {'range': [33, 66], 'color': "yellow"},
                     {'range': [66, 100], 'color': "lightcoral"}],
                 'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
    gauge_fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20)) # Adjusted margins
    st.plotly_chart(gauge_fig, use_container_width=True)

    st.subheader("Output History")
    if not st.session_state.history_data.empty and len(st.session_state.history_data) > 1:
        history_fig = go.Figure()
        history_fig.add_trace(go.Scatter(
            x=st.session_state.history_data['Time'],
            y=st.session_state.history_data['Game Speed (mph)'],
            mode='lines', # Smoother lines
            name='Game Speed (mph)',
            line=dict(color='blue', width=2)
        ))
        history_fig.add_trace(go.Scatter(
            x=st.session_state.history_data['Time'],
            y=st.session_state.history_data['PWM Power (%)'],
            mode='lines', # Smoother lines
            name='PWM Power (%)',
            yaxis='y2', # Use a secondary y-axis
            line=dict(color='red', width=2)
        ))
        history_fig.update_layout(
            # title="Live Output History", # Removed title from here as subheader exists
            xaxis_title="Time Elapsed (s)",
            yaxis_title="Game Speed (mph)",
            yaxis=dict(range=[0, st.session_state.top_speed + 10]), # Dynamically set y-axis range a bit
            yaxis2=dict(
                title="PWM Power (%)",
                overlaying='y',
                side='right',
                range=[0,105] # PWM is 0-100
            ),
            legend_title_text="Metrics",
            height=350, # Adjusted height
            margin=dict(l=20, r=20, t=20, b=20) # Compact margins
        )
        st.plotly_chart(history_fig, use_container_width=True)
    else:
        st.caption("No history data yet or not enough data (need >1 point). Start the simulation to populate charts.")

    # Optional 3D Scatter Plot
    st.subheader("3D View (Time, Speed, PWM)")
    if not st.session_state.history_data.empty and len(st.session_state.history_data) > 1:
        fig_3d = go.Figure(data=[go.Scatter3d(
            x=st.session_state.history_data['Time'],
            y=st.session_state.history_data['Game Speed (mph)'],
            z=st.session_state.history_data['PWM Power (%)'],
            mode='lines+markers', # Show lines connecting points and markers
            marker=dict(
                size=4, # Smaller markers
                color=st.session_state.history_data['PWM Power (%)'], # Color points by PWM value
                colorscale='Viridis',  # Choose a colorscale
                opacity=0.8,
                colorbar=dict(title='PWM (%)', thickness=10)
            ),
            line=dict(
                color='darkblue', # Line color
                width=2
            )
        )])
        fig_3d.update_layout(
            # title="3D History: Time, Speed, PWM", # Title removed as subheader exists
            scene=dict(
                xaxis_title='Time (s)',
                yaxis_title='Game Speed (mph)',
                zaxis_title='PWM Power (%)',
                aspectratio=dict(x=1.5, y=1, z=0.8) # Adjust aspect ratio for better view
            ),
            height=450, # Adjusted height
            margin=dict(l=0, r=0, b=0, t=0) # Minimal margins for 3D plot
        )
        st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.caption("Not enough data for 3D history yet (need >1 point).")


st.header("📝 Event Log")
log_container = st.container(height=250)
for msg in reversed(st.session_state.log_messages):
    log_container.text(msg)

st.markdown("---")
st.caption("This simulator combines and adapts logic from the original project files into a single interactive application for testing and visualization.")

# --- Main Simulation Loop Control ---
if st.session_state.simulation_running:
    run_simulation_step() 
    time.sleep(0.1) # Update frequency (10 Hz) 
    st.rerun() 
elif not st.session_state.simulation_running and st.session_state.current_game_speed_mph != 0.0:
    run_simulation_step()
    st.rerun()