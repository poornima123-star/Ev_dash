import streamlit as st
import pandas as pd
import numpy as np
import time
from sklearn.linear_model import LinearRegression
import os

st.set_page_config(page_title="EV Smart Dashboard", layout="centered")

# 🌙 DARK THEME
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #161A23;
}
div[data-testid="stMetric"] {
    background-color: #1F2937;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.4);
}
button {
    background-color: #2563EB !important;
    color: white !important;
    border-radius: 8px;
}
h1, h2, h3, h4, h5, h6, p, span {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ EV Smart Dashboard")

# Sidebar Controls
st.sidebar.header("Control Panel")
start = st.sidebar.button("▶ Start Driving")
stop = st.sidebar.button("⏹ Stop")
charge_btn = st.sidebar.button("🔌 Charge Battery")

# Session State Initialization
if "running" not in st.session_state:
    st.session_state.running = False

if "charging" not in st.session_state:
    st.session_state.charging = False

if "battery" not in st.session_state:
    st.session_state.battery = 100.0

if "health" not in st.session_state:
    st.session_state.health = 100.0

if "history" not in st.session_state:
    st.session_state.history = []

if "time_step" not in st.session_state:
    st.session_state.time_step = 0

# Button Logic
if start:
    st.session_state.running = True
    st.session_state.charging = False

if stop:
    st.session_state.running = False

if charge_btn:
    st.session_state.charging = True
    st.session_state.running = False

placeholder = st.empty()

# Cloud log file
file_name = "ev_cloud_log.csv"
if not os.path.exists(file_name):
    pd.DataFrame(columns=["Time","Speed","Voltage","Current","Battery","Health"]).to_csv(file_name, index=False)

while st.session_state.running or st.session_state.charging:

    time.sleep(1)

    st.session_state.time_step += 1
    t = st.session_state.time_step

    # Simulated inputs
    speed = np.random.randint(20, 100) if st.session_state.running else 0
    voltage = np.random.uniform(300, 400)
    current = np.random.uniform(10, 50)

    # 🔋 Battery Logic
    if st.session_state.running:
        st.session_state.battery -= np.random.uniform(0.05, 0.15)

    if st.session_state.charging:
        st.session_state.battery += np.random.uniform(0.2, 0.5)

        if st.session_state.battery >= 100:
            st.session_state.battery = 100
            st.session_state.charging = False

    # ❤️ Battery Health Degradation
    st.session_state.health -= np.random.uniform(0.005, 0.02)

    # Store history
    st.session_state.history.append([
        t, speed, voltage, current,
        st.session_state.battery,
        st.session_state.health
    ])

    df = pd.DataFrame(
        st.session_state.history,
        columns=["Time","Speed","Voltage","Current","Battery","Health"]
    )

    df["Power (kW)"] = (df["Voltage"] * df["Current"]) / 1000

    # ☁ Cloud Logging
    df.tail(1).to_csv(file_name, mode='a', header=False, index=False)

    # 🤖 AI Prediction
    if len(df) > 10:
        model = LinearRegression()
        model.fit(df[["Time"]], df["Battery"])
        future = np.array([[t + 10]])
        predicted_battery = model.predict(future)[0]
    else:
        predicted_battery = st.session_state.battery

    # ⚠ Fault Detection
    if st.session_state.battery < 20:
        status = "⚠ Low Battery"
    elif voltage > 390:
        status = "⚠ High Voltage"
    else:
        status = "✅ Normal"

    # 🔌 Charging Suggestion
    if st.session_state.battery < 30:
        suggestion = "🔌 Charge Immediately"
    else:
        suggestion = "✔ Battery OK"

    # UI Display
    with placeholder.container():

        st.subheader("📱 Live EV Status")

        col1, col2 = st.columns(2)
        col1.metric("🚗 Speed", f"{speed} km/h")
        col2.metric("🔋 Battery", f"{st.session_state.battery:.2f}%")

        col3, col4 = st.columns(2)
        col3.metric("⚡ Power", f"{df['Power (kW)'].iloc[-1]:.2f} kW")
        col4.metric("❤️ Health", f"{st.session_state.health:.2f}%")

        st.metric("🔮 Predicted Battery (10s)", f"{predicted_battery:.2f}%")

        if st.session_state.charging:
            st.success("🔌 Charging in progress...")

        st.subheader("📊 Performance Graph")
        st.line_chart(df[["Battery","Health"]])

        st.subheader("🧠 Insights")
        st.write("Status:", status)
        st.write("Suggestion:", suggestion)

st.info("👉 Use Start, Stop, or Charge from sidebar")