"""
Option A: Multi-Scenario Comparison Dashboard
The Goal - Production Optimization

This app demonstrates what Python can do that Excel Solver cannot:
- Compare multiple scenarios simultaneously
- Automatic visual comparisons
- Real-time updates across all scenarios
- Instant insights and recommendations
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from the_goal_optimization import create_goal_optimization_model
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Multi-Scenario Comparison - The Goal",
    page_icon="🏭",
    layout="wide"
)

# Header
st.markdown("""
<div style="background-color: #1e3a8a; color: white; padding: 20px; margin-bottom: 20px; border-radius: 8px;">
    <h1 style="margin: 0;">The Goal: Multi-Scenario Comparison Dashboard</h1>
    <p style="margin: 5px 0 0 0; font-style: italic;">What Python Can Do That Excel Solver Cannot</p>
</div>
""", unsafe_allow_html=True)

# Excel vs Python callout
st.info("""
**💡 Why This Matters:** In Excel Solver, you can only solve ONE scenario at a time. To compare 3 different strategies, 
you'd need to manually solve each one, write down results, and create comparison charts yourself. 
Python solves all scenarios simultaneously and generates comparisons automatically!
""")

# Sidebar configuration
st.sidebar.header("📊 Configure Your Scenarios")

st.sidebar.markdown("""
**Instructions:** Set up three different scenarios below. The app will optimize and compare them automatically.
""")

st.sidebar.markdown("---")

# Initialize session state for scenarios if not exists
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = {
        'scenario1': {
            'name': 'Baseline',
            'heat_treatment': 160,
            'machining': 200,
            'assembly': 180,
            'demand_a': 50,
            'demand_b': 80,
            'profit_a': 90,
            'profit_b': 60
        },
        'scenario2': {
            'name': 'Elevate Bottleneck',
            'heat_treatment': 200,  # +25%
            'machining': 200,
            'assembly': 180,
            'demand_a': 50,
            'demand_b': 80,
            'profit_a': 90,
            'profit_b': 60
        },
        'scenario3': {
            'name': 'Premium Product A',
            'heat_treatment': 160,
            'machining': 200,
            'assembly': 180,
            'demand_a': 50,
            'demand_b': 80,
            'profit_a': 140,  # +55%
            'profit_b': 60
        }
    }

# Scenario selector
selected_scenario = st.sidebar.radio(
    "Select Scenario to Edit:",
    ['scenario1', 'scenario2', 'scenario3'],
    format_func=lambda x: st.session_state.scenarios[x]['name']
)

# Edit selected scenario
st.sidebar.subheader(f"Edit: {st.session_state.scenarios[selected_scenario]['name']}")

st.session_state.scenarios[selected_scenario]['name'] = st.sidebar.text_input(
    "Scenario Name:",
    value=st.session_state.scenarios[selected_scenario]['name'],
    key=f"name_{selected_scenario}"
)

st.sidebar.markdown("**Work Center Capacities (hours/week)**")
st.session_state.scenarios[selected_scenario]['machining'] = st.sidebar.slider(
    "Machining:",
    min_value=100, max_value=300,
    value=st.session_state.scenarios[selected_scenario]['machining'],
    step=10,
    key=f"mach_{selected_scenario}"
)

st.session_state.scenarios[selected_scenario]['heat_treatment'] = st.sidebar.slider(
    "Heat Treatment:",
    min_value=80, max_value=240,
    value=st.session_state.scenarios[selected_scenario]['heat_treatment'],
    step=10,
    key=f"heat_{selected_scenario}"
)

st.session_state.scenarios[selected_scenario]['assembly'] = st.sidebar.slider(
    "Assembly:",
    min_value=100, max_value=300,
    value=st.session_state.scenarios[selected_scenario]['assembly'],
    step=10,
    key=f"assy_{selected_scenario}"
)

st.sidebar.markdown("**Product Parameters**")
st.session_state.scenarios[selected_scenario]['demand_a'] = st.sidebar.slider(
    "Max Demand - Product A:",
    min_value=0, max_value=100,
    value=st.session_state.scenarios[selected_scenario]['demand_a'],
    step=5,
    key=f"dema_{selected_scenario}"
)

st.session_state.scenarios[selected_scenario]['demand_b'] = st.sidebar.slider(
    "Max Demand - Product B:",
    min_value=0, max_value=150,
    value=st.session_state.scenarios[selected_scenario]['demand_b'],
    step=5,
    key=f"demb_{selected_scenario}"
)

st.session_state.scenarios[selected_scenario]['profit_a'] = st.sidebar.slider(
    "Profit - Product A ($):",
    min_value=50, max_value=150,
    value=st.session_state.scenarios[selected_scenario]['profit_a'],
    step=5,
    key=f"profa_{selected_scenario}"
)

st.session_state.scenarios[selected_scenario]['profit_b'] = st.sidebar.slider(
    "Profit - Product B ($):",
    min_value=30, max_value=100,
    value=st.session_state.scenarios[selected_scenario]['profit_b'],
    step=5,
    key=f"profb_{selected_scenario}"
)

st.sidebar.markdown("---")

# Quick preset buttons
st.sidebar.markdown("**Quick Presets:**")
col1, col2 = st.sidebar.columns(2)
if col1.button("Reset All", use_container_width=True):
    st.session_state.scenarios = {
        'scenario1': {
            'name': 'Baseline',
            'heat_treatment': 160, 'machining': 200, 'assembly': 180,
            'demand_a': 50, 'demand_b': 80, 'profit_a': 90, 'profit_b': 60
        },
        'scenario2': {
            'name': 'Elevate Bottleneck',
            'heat_treatment': 200, 'machining': 200, 'assembly': 180,
            'demand_a': 50, 'demand_b': 80, 'profit_a': 90, 'profit_b': 60
        },
        'scenario3': {
            'name': 'Premium Product A',
            'heat_treatment': 160, 'machining': 200, 'assembly': 180,
            'demand_a': 50, 'demand_b': 80, 'profit_a': 140, 'profit_b': 60
        }
    }
    st.rerun()

# Solve all three scenarios
results = {}
for scenario_id, params in st.session_state.scenarios.items():
    results[scenario_id], _ = create_goal_optimization_model(
        heat_treatment_capacity=params['heat_treatment'],
        machining_capacity=params['machining'],
        assembly_capacity=params['assembly'],
        demand_a=params['demand_a'],
        demand_b=params['demand_b'],
        profit_a=params['profit_a'],
        profit_b=params['profit_b']
    )
    results[scenario_id]['name'] = params['name']

# Display scenarios side-by-side
st.subheader("📊 Scenario Comparison")

cols = st.columns(3)

for idx, (scenario_id, result) in enumerate(results.items()):
    with cols[idx]:
        # Determine if this scenario has the best throughput
        is_best = result['total_throughput'] == max(r['total_throughput'] for r in results.values())
        
        border_color = "#16a34a" if is_best else "#94a3b8"
        badge = "👑 BEST" if is_best else ""
        
        st.markdown(f"""
        <div style="border: 3px solid {border_color}; border-radius: 8px; padding: 15px; margin-bottom: 20px; background-color: #f8fafc;">
            <h3 style="margin-top: 0; color: #1e3a8a;">{result['name']} {badge}</h3>
            <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="margin: 0; color: #1e40af;">Throughput: ${result['total_throughput']:,.2f}</h4>
            </div>
            <div style="background-color: #f0fdf4; padding: 10px; border-radius: 8px; margin: 5px 0; color: #15803d;">
                <strong style="color: #15803d;">Product A:</strong> {result['product_a']:.1f} units<br>
                <small style="color: #166534;">Contribution: ${result['product_a'] * st.session_state.scenarios[scenario_id]['profit_a']:,.2f}</small>
            </div>
            <div style="background-color: #fef3c7; padding: 10px; border-radius: 8px; margin: 5px 0; color: #92400e;">
                <strong style="color: #92400e;">Product B:</strong> {result['product_b']:.1f} units<br>
                <small style="color: #78350f;">Contribution: ${result['product_b'] * st.session_state.scenarios[scenario_id]['profit_b']:,.2f}</small>
            </div>
            <div style="background-color: #fee2e2; padding: 10px; border-radius: 8px; margin: 5px 0; color: #991b1b;">
                <strong style="color: #991b1b;">Bottleneck:</strong> {result['bottleneck']}<br>
                <small style="color: #7f1d1d;">HT Utilization: {result['heat_treatment_utilization']:.1f}%</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Comparison Charts
st.markdown("---")
st.subheader("📈 Visual Comparisons")

chart_cols = st.columns(2)

with chart_cols[0]:
    # Throughput comparison
    fig_throughput = go.Figure()
    
    scenario_names = [results[s]['name'] for s in ['scenario1', 'scenario2', 'scenario3']]
    throughputs = [results[s]['total_throughput'] for s in ['scenario1', 'scenario2', 'scenario3']]
    colors = ['#16a34a' if t == max(throughputs) else '#3b82f6' for t in throughputs]
    
    fig_throughput.add_trace(go.Bar(
        x=scenario_names,
        y=throughputs,
        marker_color=colors,
        text=[f'${t:,.0f}' for t in throughputs],
        textposition='outside'
    ))
    
    fig_throughput.update_layout(
        title='Total Throughput Comparison',
        yaxis_title='Throughput ($)',
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_throughput, use_container_width=True)

with chart_cols[1]:
    # Product mix comparison
    fig_mix = go.Figure()
    
    for idx, scenario_id in enumerate(['scenario1', 'scenario2', 'scenario3']):
        fig_mix.add_trace(go.Bar(
            name=results[scenario_id]['name'],
            x=['Product A', 'Product B'],
            y=[results[scenario_id]['product_a'], results[scenario_id]['product_b']],
        ))
    
    fig_mix.update_layout(
        title='Product Mix Comparison',
        yaxis_title='Units Produced',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig_mix, use_container_width=True)

# Detailed comparison table
st.markdown("---")
st.subheader("📋 Detailed Comparison Table")

comparison_data = []
for scenario_id in ['scenario1', 'scenario2', 'scenario3']:
    result = results[scenario_id]
    params = st.session_state.scenarios[scenario_id]
    comparison_data.append({
        'Scenario': result['name'],
        'Throughput': f"${result['total_throughput']:,.2f}",
        'Product A': f"{result['product_a']:.1f}",
        'Product B': f"{result['product_b']:.1f}",
        'Bottleneck': result['bottleneck'],
        'HT Capacity': f"{params['heat_treatment']}h",
        'HT Utilization': f"{result['heat_treatment_utilization']:.1f}%"
    })

df_comparison = pd.DataFrame(comparison_data)
st.dataframe(df_comparison, use_container_width=True, hide_index=True)

# Insights and Recommendations
st.markdown("---")
st.subheader("💡 Automatic Insights & Recommendations")

# Find best scenario
best_scenario_id = max(results.items(), key=lambda x: x[1]['total_throughput'])[0]
best_result = results[best_scenario_id]
best_name = best_result['name']

# Calculate differences
baseline_throughput = results['scenario1']['total_throughput']
best_throughput = best_result['total_throughput']
improvement = best_throughput - baseline_throughput
improvement_pct = (improvement / baseline_throughput) * 100 if baseline_throughput > 0 else 0

# Generate insights
insights = []

insights.append(f"**Best Scenario:** {best_name} achieves the highest throughput at ${best_throughput:,.2f}")

if best_scenario_id != 'scenario1':
    insights.append(f"**Improvement:** {best_name} produces ${improvement:,.2f} ({improvement_pct:.1f}%) more than the baseline")

# Bottleneck insights
bottlenecks = [results[s]['bottleneck'] for s in ['scenario1', 'scenario2', 'scenario3']]
if len(set(bottlenecks)) > 1:
    insights.append(f"**Bottleneck Shift:** The constraint changes across scenarios: {', '.join(set(bottlenecks))}")
else:
    insights.append(f"**Consistent Bottleneck:** {bottlenecks[0]} remains the constraint across all scenarios")

# Product mix insights
prod_a_counts = sum(1 for s in ['scenario1', 'scenario2', 'scenario3'] if results[s]['product_a'] > 1)
if prod_a_counts == 0:
    insights.append("**Product Mix:** All scenarios produce only Product B - it's more efficient at the bottleneck")
elif prod_a_counts == 3:
    insights.append("**Product Mix:** All scenarios include Product A - pricing or demand favors it")
else:
    insights.append(f"**Product Mix:** {prod_a_counts} of 3 scenarios include Product A - product mix varies by parameters")

# Display insights
for insight in insights:
    st.success(insight)

# Theory of Constraints Connection
st.markdown("---")
st.subheader("📚 Connection to Theory of Constraints")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Goldratt's Five Focusing Steps in Action:**
    
    1. **IDENTIFY** - Each scenario shows the bottleneck clearly
    2. **EXPLOIT** - Product mix optimizes throughput per constraint unit
    3. **SUBORDINATE** - Non-bottlenecks run below 100% utilization
    4. **ELEVATE** - Compare baseline to scenarios with increased capacity
    5. **REPEAT** - Notice how bottleneck can shift between scenarios
    """)

with col2:
    st.markdown("""
    **Key Insights from Multi-Scenario Analysis:**
    
    - Different strategies have different bottlenecks
    - Product mix depends on constraint efficiency, not just margin
    - Small changes in constraints can have large throughput impacts
    - Non-bottleneck improvements may have zero value
    - The "best" scenario depends on your strategic goals
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>Why Python > Excel for This:</strong> Excel Solver requires manual solving of each scenario, 
    separate worksheets, manual comparison charts, and significant time. Python does it all automatically in real-time!</p>
    <p><em>Based on "The Goal" by Eliyahu M. Goldratt</em></p>
</div>
""", unsafe_allow_html=True)
