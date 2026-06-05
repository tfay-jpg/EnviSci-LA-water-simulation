import streamlit as st
import plotly.graph_objects as fgo

# Page Setup & Theme forcing
st.set_page_config(layout="wide", page_title="LA County Water Portfolio Simulator")

# Inject Custom CSS for Cards, Backgrounds, and Fonts
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-top: 5px solid #3498db;
    }
    .metric-title { font-size: 14px; color: #7f8c8d; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 28px; color: #2c3e50; font-weight: bold; margin: 5px 0; }
    .metric-caption { font-size: 12px; color: #95a5a6; }
    </style>
""", unsafe_allow_html=True)

st.title("🚰 LA County Water Management Portfolio Simulator")
st.markdown("### Interactive Policy & Climate Stress Dashboard")
st.markdown("---")

# Layout: Split screen into 2 giant columns (Inputs on Left, Results/Alerts on Right)
left_panel, right_panel = st.columns([1.1, 1])

with left_panel:
    st.markdown("## ⚙️ Simulation Controls")
    
    # Section 1: Demand Side
    st.markdown("<div style='background-color: #ebf5fb; padding: 15px; border-radius: 8px; margin-bottom: 15px;'><strong>Step 1: Reduce Systemic Demand</strong></div>", unsafe_allow_html=True)
    conservation = st.slider("Water Conservation / Demand Reduction Target (% reduction from baseline)", 0, 30, 5)
    
    # Section 2: Supply Side
    st.markdown("<div style='background-color: #e8f8f5; padding: 15px; border-radius: 8px; margin-bottom: 15px;'><strong>Step 2: Allocate Remaining Physical Supply (Must total 100%)</strong></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        imp_pct = st.number_input("Imported Water (%)", 0, 100, 60, step=1)
        rec_pct = st.number_input("Water Recycling (%)", 0, 100, 5, step=1)
        desal_pct = st.number_input("Ocean Desalination (%)", 0, 100, 0, step=1)
    with c2:
        gw_pct = st.number_input("Groundwater (%)", 0, 100, 33, step=1)
        storm_pct = st.number_input("Stormwater Capture (%)", 0, 100, 2, step=1)
    
    total_portfolio_pct = imp_pct + gw_pct + rec_pct + storm_pct + desal_pct
    st.markdown(f"**Current Total Allocation Check:** `{total_portfolio_pct}% / 100%`")

    # Section 3: Stressors
    st.markdown("<div style='background-color: #fef9e7; padding: 15px; border-radius: 8px; margin-bottom: 15px;'><strong>Step 3: Apply Future Environmental Stressors</strong></div>", unsafe_allow_html=True)
    target_year = st.slider("Target Planning Horizon Year", 2026, 2060, 2026, step=1)
    pop_growth = st.slider("Annual Population Growth Rate (%)", -0.5, 1.5, 0.4, step=0.1)
    warming = st.slider("Climate Warming / Temp Rise (°C)", 0.0, 4.0, 0.0, step=0.1)
    precip_var = st.slider("Precipitation Variability / Chaos (%)", 0, 100, 0, step=5)

# Engine Logic
years_out = target_year - 2026
baseline_gross_demand = 1550000 * ((1 + (pop_growth / 100)) ** years_out)
net_reduced_demand = baseline_gross_demand * (1 - (conservation / 100))

# Math for Outputs
imp_vol = net_reduced_demand * (imp_pct / 100)
gw_vol = net_reduced_demand * (gw_pct / 100)
rec_vol = net_reduced_demand * (rec_pct / 100)
storm_vol = net_reduced_demand * (storm_pct / 100)
desal_vol = net_reduced_demand * (desal_pct / 100)
cons_vol = baseline_gross_demand - net_reduced_demand

escalated_imp_cost = 1250 * (1 + (warming * 0.02))
total_cost = (imp_vol * escalated_imp_cost) + (gw_vol * 850) + (rec_vol * 1850) + (storm_vol * 900) + (desal_vol * 3000) + (cons_vol * 350)
avg_cost_per_af = total_cost / baseline_gross_demand

weather_dependent_share = (imp_pct + storm_pct) / 100
climate_stress_factor = (warming / 4.0) * 0.5 + (precip_var / 100.0) * 0.5
reliability_score = max(min(int(100 - (weather_dependent_share * climate_stress_factor * 70) + (conservation * 0.5)), 100), 10)
env_score = max(min(int((imp_pct * 0.8) + (gw_pct * 0.4) + (rec_pct * 0.2) + (storm_pct * 0.1) + (desal_pct * 1.0)), 100), 5)

with right_panel:
    st.markdown("## 📊 Evaluation & Metrics")
    
    if total_portfolio_pct != 100:
        st.error(f"⚠️ **PORTFOLIO MISMATCH:** Your allocation totals {total_portfolio_pct}%. Please adjust the numbers on the left until they equal exactly 100% to view performance scores.")
    else:
        # Cost Card
        st.markdown(f"""<div class='metric-card'><div class='metric-title'>💰 Total Financial Profile</div><div class='metric-value'>${total_cost / 1e9:.2f} Billion / yr</div><div class='metric-caption'>Average Cost: ${int(avg_cost_per_af)} per acre-foot (Baseline: ~$1,020)</div></div>""", unsafe_allow_html=True)
        
        # Reliability Card
        rel_color = "🟢 Stable" if reliability_score >= 80 else ("🟡 Vulnerable" if reliability_score >= 50 else "🔴 High Failure Risk")
        st.markdown(f"""<div class='metric-card' style='border-top-color: #2ecc71;'><div class='metric-title'>🛡️ System Reliability Index</div><div class='metric-value'>{reliability_score} / 100</div><div class='metric-caption'>Status: <strong>{rel_color}</strong> under simulated weather shocks.</div></div>""", unsafe_allow_html=True)
        
        # Eco Card
        eco_color = "🟢 Low Strain" if env_score <= 40 else ("🟡 Moderate Strain" if env_score <= 65 else "🔴 Severe Degradation")
        st.markdown(f"""<div class='metric-card' style='border-top-color: #e74c3c;'><div class='metric-title'>🌿 Environmental Impact Score</div><div class='metric-value'>{env_score} / 100</div><div class='metric-caption'>Status: <strong>{eco_color}</strong> (Lower scores indicate healthier local ecosystems).</div></div>""", unsafe_allow_html=True)
        
        # Donut Chart
        st.markdown("### Resource Balance Allocation")
        fig = fgo.Figure(data=[fgo.Pie(labels=['Imported Water', 'Groundwater', 'Water Recycling', 'Stormwater Capture', 'Ocean Desalination'], 
                                       values=[imp_vol, gw_vol, rec_vol, storm_vol, desal_vol], hole=.4,
                                       marker=dict(colors=['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c']))])
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=240, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        # Warnings / Infrastructure constraints area
        st.markdown("### ⚠️ Infrastructure & Hydrologic Flags")
        if gw_pct > 35: st.warning("**Groundwater Overdraft:** Exceeds basin safe yield. Triggers land subsidence.")
        if storm_pct > 15: st.warning("**Hydrologic Ceiling:** LA's climate cannot physically generate this much catchable stormwater.")
        if rec_pct > 45: st.warning("**Effluent Limitation:** Allocation exceeds available total wastewater baseline.")
        if desal_pct > 10: st.warning("**Regulatory Wall:** Scale faces grid power constraints and Coastal Commission blocking.")
        if gw_pct <= 35 and storm_pct <= 15 and rec_pct <= 45 and desal_pct <= 10:
            st.success("All allocated strategies fall within realistic engineering thresholds for LA County.")
