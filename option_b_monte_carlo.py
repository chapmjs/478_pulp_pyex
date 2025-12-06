"""
Option B: Monte Carlo Simulation for Uncertainty Analysis
Python Shiny Express Version
"""

from shiny.express import input, render, ui
from shiny import reactive
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from the_goal_optimization import create_goal_optimization_model

# Page setup
ui.page_opts(
    title="Monte Carlo Simulation - The Goal",
    fillable=True
)

# Header
ui.markdown("""
# 🎲 The Goal: Monte Carlo Simulation
*Account for Uncertainty in Your Optimization*

**💡 Why This Matters:** In the real world, demand, capacity, and prices are uncertain. 
Excel Solver gives you ONE answer assuming everything is certain. Python can run 1,000+ 
scenarios to show you the RANGE of possible outcomes and their probabilities!
""")

# Sidebar for controls
with ui.sidebar(width=350):
    ui.h3("🎲 Simulation Settings")
    
    ui.input_slider(
        "n_sims",
        "Number of Simulations:",
        min=100,
        max=2000,
        value=500,
        step=100
    )
    
    ui.hr()
    ui.h4("📊 Base Case Parameters")
    
    ui.input_slider("base_heat", "Heat Treatment:", min=80, max=240, value=160, step=10)
    ui.input_slider("base_mach", "Machining:", min=100, max=300, value=200, step=10)
    ui.input_slider("base_assy", "Assembly:", min=100, max=300, value=180, step=10)
    ui.input_slider("base_dema", "Demand A:", min=0, max=100, value=50, step=5)
    ui.input_slider("base_demb", "Demand B:", min=0, max=150, value=80, step=5)
    ui.input_slider("base_profa", "Profit A ($):", min=50, max=150, value=90, step=5)
    ui.input_slider("base_profb", "Profit B ($):", min=30, max=100, value=60, step=5)
    
    ui.hr()
    ui.h4("🎯 Uncertainty Levels")
    
    ui.input_slider(
        "demand_unc",
        "Demand Uncertainty (%):",
        min=0,
        max=50,
        value=20,
        step=5
    )
    
    ui.input_slider(
        "capacity_unc",
        "Capacity Uncertainty (%):",
        min=0,
        max=30,
        value=10,
        step=5
    )
    
    ui.input_slider(
        "price_unc",
        "Price Uncertainty (%):",
        min=0,
        max=40,
        value=15,
        step=5
    )
    
    ui.hr()
    
    ui.input_action_button(
        "run_sim",
        "🎲 Run Simulation",
        class_="btn-primary",
        width="100%"
    )

# Reactive values
simulation_data = reactive.value(None)

# Calculate baseline
@reactive.calc
def baseline():
    result, _ = create_goal_optimization_model(
        heat_treatment_capacity=input.base_heat(),
        machining_capacity=input.base_mach(),
        assembly_capacity=input.base_assy(),
        demand_a=input.base_dema(),
        demand_b=input.base_demb(),
        profit_a=input.base_profa(),
        profit_b=input.base_profb()
    )
    return result

# Run simulation when button clicked
@reactive.effect
@reactive.event(input.run_sim)
def run_simulation():
    """Run Monte Carlo simulation"""
    
    n_sims = input.n_sims()
    
    # Storage for results
    results = []
    
    # Run simulations
    for i in range(n_sims):
        # Generate random variations
        demand_a = max(0, np.random.normal(
            input.base_dema(), 
            input.base_dema() * input.demand_unc() / 100
        ))
        demand_b = max(0, np.random.normal(
            input.base_demb(), 
            input.base_demb() * input.demand_unc() / 100
        ))
        
        heat_treatment = max(50, np.random.normal(
            input.base_heat(), 
            input.base_heat() * input.capacity_unc() / 100
        ))
        machining = max(50, np.random.normal(
            input.base_mach(), 
            input.base_mach() * input.capacity_unc() / 100
        ))
        assembly = max(50, np.random.normal(
            input.base_assy(), 
            input.base_assy() * input.capacity_unc() / 100
        ))
        
        profit_a = max(10, np.random.normal(
            input.base_profa(), 
            input.base_profa() * input.price_unc() / 100
        ))
        profit_b = max(10, np.random.normal(
            input.base_profb(), 
            input.base_profb() * input.price_unc() / 100
        ))
        
        # Solve optimization
        result, _ = create_goal_optimization_model(
            heat_treatment_capacity=heat_treatment,
            machining_capacity=machining,
            assembly_capacity=assembly,
            demand_a=demand_a,
            demand_b=demand_b,
            profit_a=profit_a,
            profit_b=profit_b
        )
        
        results.append({
            'throughput': result['total_throughput'],
            'product_a': result['product_a'],
            'product_b': result['product_b'],
            'bottleneck': result['bottleneck'],
            'ht_utilization': result['heat_treatment_utilization']
        })
    
    # Store results
    simulation_data.set(pd.DataFrame(results))

# Main content
with ui.panel_conditional("input.run_sim == 0"):
    # Before simulation runs
    ui.h2("📋 How It Works")
    
    with ui.layout_columns(col_widths=[6, 6]):
        with ui.card():
            ui.card_header("Setup & Run")
            ui.markdown("""
            **1. Set Base Parameters** (left sidebar)
            - Your expected/planned values
            - Best guess for demand, capacity, prices
            
            **2. Define Uncertainty** (left sidebar)
            - How much could each parameter vary?
            - Demand uncertainty: ±20% is typical
            - Capacity uncertainty: ±10% for breakdowns
            - Price uncertainty: ±15% for market changes
            
            **3. Run Simulation**
            - Click "Run Simulation" button
            - Python runs optimization 500+ times
            - Each time with different random values
            - Shows you range of possible outcomes
            """)
        
        with ui.card():
            ui.card_header("Questions This Answers")
            ui.markdown("""
            ✅ What's the probability we achieve $5,000+ throughput?
            
            ✅ What's our worst-case scenario?
            
            ✅ What's our best-case scenario?
            
            ✅ How much risk are we taking?
            
            ✅ Should we build safety margins?
            
            ✅ What's the 95% confidence interval?
            """)
    
    ui.hr()
    ui.h2("📊 Baseline Scenario (No Uncertainty)")
    
    @render.ui
    def baseline_display():
        base = baseline()
        
        return ui.HTML(f"""
        <div style="display: flex; gap: 20px; margin: 20px 0;">
            <div style="flex: 1; background-color: #dbeafe; padding: 20px; border-radius: 8px;">
                <h3 style="color: #1e40af; margin: 0;">Expected Throughput</h3>
                <p style="font-size: 2em; font-weight: bold; margin: 10px 0;">${base['total_throughput']:,.2f}</p>
                <small>Assumes all parameters at expected values</small>
            </div>
            <div style="flex: 1; background-color: #dcfce7; padding: 20px; border-radius: 8px;">
                <h3 style="color: #15803d; margin: 0;">Product A</h3>
                <p style="font-size: 2em; font-weight: bold; margin: 10px 0;">{base['product_a']:.1f} units</p>
            </div>
            <div style="flex: 1; background-color: #fef3c7; padding: 20px; border-radius: 8px;">
                <h3 style="color: #92400e; margin: 0;">Product B</h3>
                <p style="font-size: 2em; font-weight: bold; margin: 10px 0;">{base['product_b']:.1f} units</p>
            </div>
        </div>
        <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">
            <strong>⚠️ Reality Check:</strong> This baseline assumes perfect certainty. 
            But demand fluctuates, machines break down, and prices change. 
            Click 'Run Simulation' to see the range of possible outcomes!
        </div>
        """)

# After simulation runs
with ui.panel_conditional("input.run_sim > 0"):
    
    @render.ui
    def simulation_status():
        df = simulation_data.get()
        if df is None:
            return ui.HTML("<p>Simulation running...</p>")
        
        return ui.HTML(f"""
        <div style="background-color: #dcfce7; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <strong>✅ Completed {len(df):,} simulations!</strong>
        </div>
        """)
    
    ui.h2("📊 Simulation Results")
    
    # Key metrics
    @render.ui
    def key_metrics():
        df = simulation_data.get()
        if df is None:
            return ui.HTML("")
        
        base = baseline()
        
        mean_throughput = df['throughput'].mean()
        percentile_5 = df['throughput'].quantile(0.05)
        percentile_95 = df['throughput'].quantile(0.95)
        std_throughput = df['throughput'].std()
        
        delta_mean = mean_throughput - base['total_throughput']
        delta_5 = percentile_5 - base['total_throughput']
        delta_95 = percentile_95 - base['total_throughput']
        
        return ui.HTML(f"""
        <div style="display: flex; gap: 15px; margin: 20px 0;">
            <div style="flex: 1; background-color: #dbeafe; padding: 20px; border-radius: 8px; text-align: center;">
                <h4 style="margin: 0; color: #1e40af;">Mean Throughput</h4>
                <p style="font-size: 1.8em; font-weight: bold; margin: 10px 0;">${mean_throughput:,.2f}</p>
                <small style="color: {'#16a34a' if delta_mean >= 0 else '#dc2626'};">
                    {delta_mean:+,.2f} vs baseline
                </small>
            </div>
            <div style="flex: 1; background-color: #fee2e2; padding: 20px; border-radius: 8px; text-align: center;">
                <h4 style="margin: 0; color: #991b1b;">Worst Case (5th %ile)</h4>
                <p style="font-size: 1.8em; font-weight: bold; margin: 10px 0;">${percentile_5:,.2f}</p>
                <small style="color: #991b1b;">{delta_5:+,.2f} vs baseline</small>
            </div>
            <div style="flex: 1; background-color: #dcfce7; padding: 20px; border-radius: 8px; text-align: center;">
                <h4 style="margin: 0; color: #15803d;">Best Case (95th %ile)</h4>
                <p style="font-size: 1.8em; font-weight: bold; margin: 10px 0;">${percentile_95:,.2f}</p>
                <small style="color: #15803d;">{delta_95:+,.2f} vs baseline</small>
            </div>
            <div style="flex: 1; background-color: #fef3c7; padding: 20px; border-radius: 8px; text-align: center;">
                <h4 style="margin: 0; color: #92400e;">Risk (Std Dev)</h4>
                <p style="font-size: 1.8em; font-weight: bold; margin: 10px 0;">${std_throughput:,.2f}</p>
                <small>Higher = more uncertainty</small>
            </div>
        </div>
        """)
    
    # Distribution chart
    ui.hr()
    ui.h2("📈 Throughput Distribution")
    
    with ui.card():
        @render.plot
        def distribution_chart():
            df = simulation_data.get()
            if df is None:
                return go.Figure()
            
            base = baseline()
            mean_throughput = df['throughput'].mean()
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=df['throughput'],
                nbinsx=50,
                name='Simulated Outcomes',
                marker_color='#3b82f6',
                opacity=0.7
            ))
            
            fig.add_vline(
                x=base['total_throughput'],
                line_dash="dash",
                line_color="red",
                annotation_text="Baseline",
                annotation_position="top"
            )
            
            fig.add_vline(
                x=mean_throughput,
                line_dash="dash",
                line_color="green",
                annotation_text=f"Mean: ${mean_throughput:,.0f}",
                annotation_position="top right"
            )
            
            fig.update_layout(
                title=f'Distribution of Throughput ({len(df):,} simulations)',
                xaxis_title='Throughput ($)',
                yaxis_title='Frequency',
                showlegend=False,
                height=500
            )
            
            return fig
    
    # Probability analysis
    ui.hr()
    ui.h2("🎯 Probability Analysis")
    
    with ui.layout_columns(col_widths=[6, 6]):
        
        # Probability calculator
        with ui.card():
            ui.card_header("Target Probability Calculator")
            
            ui.input_numeric(
                "target",
                "Target Throughput ($):",
                value=None,
                min=0,
                step=100
            )
            
            @render.ui
            def probability_result():
                df = simulation_data.get()
                if df is None:
                    return ui.HTML("")
                
                target = input.target()
                if target is None or target == 0:
                    base = baseline()
                    target = int(base['total_throughput'])
                
                prob_exceed = (df['throughput'] >= target).mean() * 100
                prob_below = (df['throughput'] < target).mean() * 100
                
                gauge_color = "#16a34a" if prob_exceed >= 50 else "#dc2626"
                
                return ui.HTML(f"""
                <div style="margin: 20px 0;">
                    <h4>Probability Analysis for ${target:,}:</h4>
                    <div style="background-color: #dcfce7; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        ✅ Probability of <strong>achieving or exceeding</strong>: <strong style="font-size: 1.5em;">{prob_exceed:.1f}%</strong>
                    </div>
                    <div style="background-color: #fee2e2; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        ⚠️ Probability of <strong>falling short</strong>: <strong>{prob_below:.1f}%</strong>
                    </div>
                </div>
                """)
        
        # Confidence intervals
        with ui.card():
            ui.card_header("Confidence Intervals")
            
            @render.data_frame
            def confidence_intervals():
                df = simulation_data.get()
                if df is None:
                    return pd.DataFrame()
                
                confidence_levels = [50, 80, 90, 95, 99]
                ci_data = []
                
                for conf in confidence_levels:
                    lower = (100 - conf) / 2
                    upper = conf + lower
                    lower_bound = df['throughput'].quantile(lower / 100)
                    upper_bound = df['throughput'].quantile(upper / 100)
                    ci_data.append({
                        'Confidence': f"{conf}%",
                        'Lower Bound': f"${lower_bound:,.2f}",
                        'Upper Bound': f"${upper_bound:,.2f}",
                        'Range': f"${upper_bound - lower_bound:,.2f}"
                    })
                
                return pd.DataFrame(ci_data)
    
    # Product mix charts
    ui.hr()
    ui.h2("📦 Product Mix Variation")
    
    with ui.layout_columns(col_widths=[6, 6]):
        
        with ui.card():
            ui.card_header("Product A Distribution")
            
            @render.plot
            def product_a_dist():
                df = simulation_data.get()
                if df is None:
                    return go.Figure()
                
                fig = px.histogram(
                    df,
                    x='product_a',
                    nbins=30,
                    labels={'product_a': 'Units Produced'}
                )
                fig.update_traces(marker_color='#10b981')
                fig.update_layout(showlegend=False)
                return fig
        
        with ui.card():
            ui.card_header("Product B Distribution")
            
            @render.plot
            def product_b_dist():
                df = simulation_data.get()
                if df is None:
                    return go.Figure()
                
                fig = px.histogram(
                    df,
                    x='product_b',
                    nbins=30,
                    labels={'product_b': 'Units Produced'}
                )
                fig.update_traces(marker_color='#f59e0b')
                fig.update_layout(showlegend=False)
                return fig
    
    # Insights
    ui.hr()
    ui.h2("💡 Key Insights")
    
    @render.ui
    def insights():
        df = simulation_data.get()
        if df is None:
            return ui.HTML("")
        
        base = baseline()
        mean_throughput = df['throughput'].mean()
        percentile_5 = df['throughput'].quantile(0.05)
        percentile_95 = df['throughput'].quantile(0.95)
        
        prob_above_baseline = (df['throughput'] > base['total_throughput']).mean() * 100
        
        bottleneck_counts = df['bottleneck'].value_counts()
        most_common_bottleneck = bottleneck_counts.index[0]
        bottleneck_pct = (bottleneck_counts.iloc[0] / len(df)) * 100
        
        return ui.HTML(f"""
        <div style="display: flex; gap: 20px;">
            <div style="flex: 1; background-color: #dcfce7; padding: 20px; border-radius: 8px; border-left: 4px solid #16a34a;">
                <h4 style="margin-top: 0;">Risk Assessment</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Mean throughput is ${mean_throughput - base['total_throughput']:+,.2f} vs. baseline</li>
                    <li>{prob_above_baseline:.1f}% chance of exceeding baseline</li>
                    <li>Worst case: ${percentile_5:,.2f} ({(percentile_5/base['total_throughput']-1)*100:+.1f}%)</li>
                    <li>Best case: ${percentile_95:,.2f} ({(percentile_95/base['total_throughput']-1)*100:+.1f}%)</li>
                </ul>
            </div>
            <div style="flex: 1; background-color: #dbeafe; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <h4 style="margin-top: 0;">Bottleneck Analysis</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Most common bottleneck: <strong>{most_common_bottleneck}</strong></li>
                    <li>Frequency: <strong>{bottleneck_pct:.1f}%</strong> of simulations</li>
                    <li>This tells you where to focus improvement efforts!</li>
                </ul>
            </div>
        </div>
        """)

# Footer
ui.hr()
ui.markdown("""
**Why Python > Excel for Monte Carlo:** Excel can do basic Monte Carlo with macros, 
but it's slow (minutes for 1,000 runs), hard to visualize, and can't integrate with 
optimization at scale. Python does 1,000+ optimizations in seconds with beautiful 
interactive visualizations!

*Based on "The Goal" by Eliyahu M. Goldratt*
""")
