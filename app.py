import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# ==========================================
# PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="ICT Structural Safety Visualizer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern tech styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { color: #e0e6ed; }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #a0aec0;
        margin-bottom: 20px;
    }
    .team-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .metric-box {
        background: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #00f2fe;
        text-align: center;
    }
    .danger-box {
        background: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #ff4b4b;
        text-align: center;
    }
    </style>
""", unsafe_with_html=True)

# ==========================================
# HERO BANNER & TEAM CREDITS
# ==========================================
st.markdown('<p class="hero-title">ICT for Structural Safety</p>', unsafe_with_html=True)
st.markdown('<p class="hero-subtitle">⚡ Live Beam Deflection Visualizer & Risk Monitor</p>', unsafe_with_html=True)

# Team Members Grid Layout
st.markdown('<div class="team-card">', unsafe_with_html=True)
st.markdown("<p style='margin-bottom: 10px; font-weight: bold; color: #00f2fe; letter-spacing: 1px;'>DEVELOPED BY TEAM:</p>", unsafe_with_html=True)

cols = st.columns(5)
team_data = [
    {"name": "Abdul Mannan", "reg": "Reg No: 55"},
    {"name": "Muhammad bin Akarma", "reg": "Reg No: 59"},
    {"name": "Muneeb Azhar", "reg": "Reg No: 03"},
    {"name": "Ahmed Ali", "reg": "Reg No: 115"},
    {"name": "Hammad Fida", "reg": "Reg No: 27"}
]

for i, member in enumerate(team_data):
    with cols[i]:
        st.markdown(f"**{member['name']}**")
        st.markdown(f"<span style='color: #a0aec0; font-size: 0.85rem;'>{member['reg']}</span>", unsafe_with_html=True)
st.markdown('</div>', unsafe_with_html=True)

st.divider()

# ==========================================
# SIDEBAR CONTROLS (Live Inputs)
# ==========================================
st.sidebar.header("🏗️ Structural Parameters")

beam_type = st.sidebar.selectbox(
    "Beam Configuration", 
    ["Cantilever (Fixed-Free)", "Simply Supported (Pinned-Pinned)"]
)

length = st.sidebar.slider("Beam Length (L) [meters]", 2.0, 15.0, 8.0, 0.5)
elasticity = st.sidebar.slider("Elastic Modulus (E) [GPa]", 10, 210, 200, step=10) # 200 GPa is standard steel
inertia = st.sidebar.slider("Moment of Inertia (I) [10⁻⁶ m⁴]", 10, 500, 150, step=10)

st.sidebar.header("⚖️ Dynamic Loading")
load_type = st.sidebar.radio("Load Condition", ["Point Load at Center/Tip", "Oscillating Dynamic Load"])
base_load = st.sidebar.slider("Load Magnitude (P) [kN]", 5.0, 150.0, 50.0, 5.0)

# Real-time animation control toggle
run_live_feed = st.sidebar.toggle("🟢 Activate Live Sensor Feed", value=True)

# ==========================================
# PHYSICS & CALCULATIONS ENGINE
# ==========================================
# Convert inputs to standard SI units
E_Pa = elasticity * 1e9
I_m4 = inertia * 1e-6
L_m = length

def get_deflection_curve(x, P_N, beam_type):
    """Calculates beam deflection curve based on Euler-Bernoulli beam theory."""
    y = np.zeros_like(x)
    EI = E_Pa * I_m4
    
    if beam_type == "Cantilever (Fixed-Free)":
        # Max deflection at tip (x = L)
        # y = (P * x^2 * (3L - x)) / (6EI)
        y = (P_N * (x**2) * (3 * L_m - x)) / (6 * EI)
    else: 
        # Simply Supported with load at center (a = L/2)
        # For x <= L/2: y = (P * x * (3L^2 - 4x^2)) / (48EI)
        half_L = L_m / 2
        for idx, x_val in enumerate(x):
            if x_val <= half_L:
                y[idx] = (P_N * x_val * (3 * L_m**2 - 4 * x_val**2)) / (48 * EI)
            else:
                # Symmetric side
                x_sym = L_m - x_val
                y[idx] = (P_N * x_sym * (3 * L_m**2 - 4 * x_sym**2)) / (48 * EI)
    return y * 1000 # Convert to millimeters for readability

# ==========================================
# LIVE DASHBOARD APP LOOP
# ==========================================
x_points = np.linspace(0, L_m, 200)

# Layout slots for real-time updates
metric_slot = st.empty()
chart_slot = st.empty()

# Threshold for structural hazard alerts
SAFETY_LIMIT_MM = (L_m * 1000) / 250 # Common engineering limit: L/250

iteration = 0
while True:
    # Simulate dynamic sensor fluctuations or dynamic oscillations
    if run_live_feed:
        iteration += 1
        if load_type == "Oscillating Dynamic Load":
            # Sine wave oscillation to mimic harmonic vehicle/wind load
            dynamic_load = base_load * (1 + 0.6 * np.sin(iteration * 0.2))
        else:
            # Small random sensory noise for standard point load
            dynamic_load = base_load + np.random.uniform(-2.5, 2.5)
    else:
        dynamic_load = base_load

    # Calculate actual physics profile
    load_N = dynamic_load * 1000 # kN to N
    deflection = get_deflection_curve(x_points, load_N, beam_type)
    max_deflection = np.max(deflection)
    
    # Structural Safety Factor Check
    safety_status = "SAFE" if max_deflection < SAFETY_LIMIT_MM else "CRITICAL RISK"
    status_color = "#00f2fe" if safety_status == "SAFE" else "#ff4b4b"
    
    # 1. Update Real-Time Metrics Row
    with metric_slot.container():
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown(f'<div class="metric-box"><h5>Current Load</h5><h3>{dynamic_load:.2f} kN</h3></div>', unsafe_with_html=True)
        with m_col2:
            st.markdown(f'<div class="metric-box"><h5>Max Deflection</h5><h3>{max_deflection:.2f} mm</h3></div>', unsafe_with_html=True)
        with m_col3:
            st.markdown(f'<div class="metric-box"><h5>Allowed Limit</h5><h3>{SAFETY_LIMIT_MM:.2f} mm</h3></div>', unsafe_with_html=True)
        with m_col4:
            st.markdown(f'<div class="{ "metric-box" if safety_status=="SAFE" else "danger-box" }"><h5>Safety Assessment</h5><h3 style="color:{status_color};">{safety_status}</h3></div>', unsafe_with_html=True)

    # 2. Build Glowing Plotly Visualizer
    fig = go.Figure()
    
    # Reference/Undeflected Beam Line
    fig.add_trace(go.Scatter(
        x=x_points, y=np.zeros_like(x_points),
        mode='lines',
        name='Original Axis',
        line=dict(color='rgba(255,255,255,0.3)', width=2, dash='dash')
    ))
    
    # Live Deflected Beam Profile (Glowing Cyberpunk Line styling)
    fig.add_trace(go.Scatter(
        x=x_points, y=-deflection, # Negative so it bends downwards visually
        mode='lines',
        name='Deflected Profile',
        line=dict(color=status_color, width=5),
        fill='tozeroy',
        fillcolor=f"rgba({ '0, 242, 254' if safety_status=='SAFE' else '255, 75, 75' }, 0.15)"
    ))

    # Add visual indicators for structural supports
    if beam_type == "Cantilever (Fixed-Free)":
        # Fixed support indicator at x=0
        fig.add_shadow(type="rect", x0=-0.1, x1=0, y0=-max_deflection*1.2, y1=max_deflection*0.5, color="gray")
    else:
        # Pinned-pinned supports at both ends
        fig.add_trace(go.Scatter(x=[0, L_m], y=[0, 0], mode='markers', marker=dict(symbol='triangle-up', size=15, color='#ffaa00'), name='Supports'))

    # Plot adjustments
    fig.update_layout(
        title=f"Live Structural Strain Deformation Profile ({beam_type})",
        xaxis_title="Beam Length Location (meters)",
        yaxis_title="Vertical Displacement (mm)",
        template="plotly_dark",
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        yaxis=dict(range=[-max_deflection * 1.5 - 5, max_deflection * 0.5 + 5]),
        xaxis=dict(range=[-0.5, L_m + 0.5]),
        showlegend=False,
        height=450,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    with chart_slot.container():
        st.plotly_chart(fig, use_container_width=True)
        
    # Animation FPS handling
    if run_live_feed:
        time.sleep(0.08)
    else:
        st.stop()
