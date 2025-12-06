"""
Option A: Multi-Scenario Comparison Dashboard
Python Shiny Express Version
"""

from shiny.express import input, render, ui
from shiny import reactive
import plotly.graph_objects as go
import pandas as pd
from the_goal_optimization import create_goal_optimization_model

# Page setup
ui.page_opts(
    title="Multi-Scenario Comparison - The Goal",
    fillable=True
)

# Header
ui.markdown("""
# 🏭 The Goal: Multi-Scenario Comparison
*What Python Can Do That Excel Solver Cannot*

**💡 Why This Matters:** In Excel Solver, you can only solve ONE scenario at a time. 
To compare 3 different strategies, you'd need to manually solve each one, write down results, 
and create comparison charts yourself. Python solves all scenarios simultaneously and generates 
comparisons automatically!
""")

# Sidebar for controls
with ui.sidebar(width=350):
    ui.h3("📊 Configure Your Scenarios")
    
    ui.input_radio_buttons(
        "selected_scenario",
        "Select Scenario to Edit:",
        choices={
            "scenario1": "Scenario 1",
            "scenario2": "Scenario 2", 
            "scenario3": "Scenario 3"
        },
        selected="scenario1"
    )
    
    ui.hr()
    
    # Scenario 1 inputs
    with ui.panel_conditional("input.selected_scenario === 'scenario1'"):
        ui.h4("Edit Scenario 1")
        ui.input_text("name1", "Scenario Name:", value="Baseline")
        ui.input_slider("heat1", "Heat Treatment (hrs):", min=80, max=240, value=160, step=10)
        ui.input_slider("mach1", "Machining (hrs):", min=100, max=300, value=200, step=10)
        ui.input_slider("assy1", "Assembly (hrs):", min=100, max=300, value=180, step=10)
        ui.input_slider("dema1", "Demand A:", min=0, max=100, value=50, step=5)
        ui.input_slider("demb1", "Demand B:", min=0, max=150, value=80, step=5)
        ui.input_slider("profa1", "Profit A ($):", min=50, max=150, value=90, step=5)
        ui.input_slider("profb1", "Profit B ($):", min=30, max=100, value=60, step=5)
    
    # Scenario 2 inputs
    with ui.panel_conditional("input.selected_scenario === 'scenario2'"):
        ui.h4("Edit Scenario 2")
        ui.input_text("name2", "Scenario Name:", value="Elevate Bottleneck")
        ui.input_slider("heat2", "Heat Treatment (hrs):", min=80, max=240, value=200, step=10)
        ui.input_slider("mach2", "Machining (hrs):", min=100, max=300, value=200, step=10)
        ui.input_slider("assy2", "Assembly (hrs):", min=100, max=300, value=180, step=10)
        ui.input_slider("dema2", "Demand A:", min=0, max=100, value=50, step=5)
        ui.input_slider("demb2", "Demand B:", min=0, max=150, value=80, step=5)
        ui.input_slider("profa2", "Profit A ($):", min=50, max=150, value=90, step=5)
        ui.input_slider("profb2", "Profit B ($):", min=30, max=100, value=60, step=5)
    
    # Scenario 3 inputs
    with ui.panel_conditional("input.selected_scenario === 'scenario3'"):
        ui.h4("Edit Scenario 3")
        ui.input_text("name3", "Scenario Name:", value="Premium Product A")
        ui.input_slider("heat3", "Heat Treatment (hrs):", min=80, max=240, value=160, step=10)
        ui.input_slider("mach3", "Machining (hrs):", min=100, max=300, value=200, step=10)
        ui.input_slider("assy3", "Assembly (hrs):", min=100, max=300, value=180, step=10)
        ui.input_slider("dema3", "Demand A:", min=0, max=100, value=50, step=5)
        ui.input_slider("demb3", "Demand B:", min=0, max=150, value=80, step=5)
        ui.input_slider("profa3", "Profit A ($):", min=50, max=150, value=140, step=5)
        ui.input_slider("profb3", "Profit B ($):", min=30, max=100, value=60, step=5)

# Reactive calculations
@reactive.calc
def solve_scenarios():
    """Solve all three scenarios"""
    results = {}
    
    # Scenario 1
    results['scenario1'], _ = create_goal_optimization_model(
        heat_treatment_capacity=input.heat1(),
        machining_capacity=input.mach1(),
        assembly_capacity=input.assy1(),
        demand_a=input.dema1(),
        demand_b=input.demb1(),
        profit_a=input.profa1(),
        profit_b=input.profb1()
    )
    results['scenario1']['name'] = input.name1()
    
    # Scenario 2
    results['scenario2'], _ = create_goal_optimization_model(
        heat_treatment_capacity=input.heat2(),
        machining_capacity=input.mach2(),
        assembly_capacity=input.assy2(),
        demand_a=input.dema2(),
        demand_b=input.demb2(),
        profit_a=input.profa2(),
        profit_b=input.profb2()
    )
    results['scenario2']['name'] = input.name2()
    
    # Scenario 3
    results['scenario3'], _ = create_goal_optimization_model(
        heat_treatment_capacity=input.heat3(),
        machining_capacity=input.mach3(),
        assembly_capacity=input.assy3(),
        demand_a=input.dema3(),
        demand_b=input.demb3(),
        profit_a=input.profa3(),
        profit_b=input.profb3()
    )
    results['scenario3']['name'] = input.name3()
    
    return results

# Main content area
ui.h2("📊 Scenario Comparison")

# Display scenario cards
with ui.layout_columns(col_widths=[4, 4, 4]):
    
    # Scenario 1 Card
    with ui.card():
        @render.ui
        def scenario1_card():
            results = solve_scenarios()
            result = results['scenario1']
            
            # Determine if best
            all_throughputs = [r['total_throughput'] for r in results.values()]
            is_best = result['total_throughput'] == max(all_throughputs)
            badge = "👑 BEST" if is_best else ""
            border_color = "#16a34a" if is_best else "#94a3b8"
            
            return ui.HTML(f"""
                <div style="border: 3px solid {border_color}; border-radius: 8px; padding: 15px; background-color: #f8fafc;">
                    <h3 style="color: #1e3a8a;">{result['name']} {badge}</h3>
                    <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h4 style="color: #1e40af;">Throughput: ${result['total_throughput']:,.2f}</h4>
                    </div>
                    <p style="color: #15803d;"><strong>Product A:</strong> {result['product_a']:.1f} units</p>
                    <p style="color: #92400e;"><strong>Product B:</strong> {result['product_b']:.1f} units</p>
                    <p style="color: #991b1b;"><strong>Bottleneck:</strong> {result['bottleneck']}</p>
                    <p style="color: #991b1b;"><small>HT Utilization: {result['heat_treatment_utilization']:.1f}%</small></p>
                </div>
            """)
    
    # Scenario 2 Card
    with ui.card():
        @render.ui
        def scenario2_card():
            results = solve_scenarios()
            result = results['scenario2']
            
            all_throughputs = [r['total_throughput'] for r in results.values()]
            is_best = result['total_throughput'] == max(all_throughputs)
            badge = "👑 BEST" if is_best else ""
            border_color = "#16a34a" if is_best else "#94a3b8"
            
            return ui.HTML(f"""
                <div style="border: 3px solid {border_color}; border-radius: 8px; padding: 15px; background-color: #f8fafc;">
                    <h3 style="color: #1e3a8a;">{result['name']} {badge}</h3>
                    <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h4 style="color: #1e40af;">Throughput: ${result['total_throughput']:,.2f}</h4>
                    </div>
                    <p style="color: #15803d;"><strong>Product A:</strong> {result['product_a']:.1f} units</p>
                    <p style="color: #92400e;"><strong>Product B:</strong> {result['product_b']:.1f} units</p>
                    <p style="color: #991b1b;"><strong>Bottleneck:</strong> {result['bottleneck']}</p>
                    <p style="color: #991b1b;"><small>HT Utilization: {result['heat_treatment_utilization']:.1f}%</small></p>
                </div>
            """)
    
    # Scenario 3 Card
    with ui.card():
        @render.ui
        def scenario3_card():
            results = solve_scenarios()
            result = results['scenario3']
            
            all_throughputs = [r['total_throughput'] for r in results.values()]
            is_best = result['total_throughput'] == max(all_throughputs)
            badge = "👑 BEST" if is_best else ""
            border_color = "#16a34a" if is_best else "#94a3b8"
            
            return ui.HTML(f"""
                <div style="border: 3px solid {border_color}; border-radius: 8px; padding: 15px; background-color: #f8fafc;">
                    <h3 style="color: #1e3a8a;">{result['name']} {badge}</h3>
                    <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h4 style="color: #1e40af;">Throughput: ${result['total_throughput']:,.2f}</h4>
                    </div>
                    <p style="color: #15803d;"><strong>Product A:</strong> {result['product_a']:.1f} units</p>
                    <p style="color: #92400e;"><strong>Product B:</strong> {result['product_b']:.1f} units</p>
                    <p style="color: #991b1b;"><strong>Bottleneck:</strong> {result['bottleneck']}</p>
                    <p style="color: #991b1b;"><small>HT Utilization: {result['heat_treatment_utilization']:.1f}%</small></p>
                </div>
            """)

# Charts section
ui.hr()
ui.h2("📈 Visual Comparisons")

with ui.layout_columns(col_widths=[6, 6]):
    
    # Throughput comparison chart
    with ui.card():
        ui.card_header("Total Throughput Comparison")
        
        @render.plot
        def throughput_chart():
            results = solve_scenarios()
            
            names = [results[s]['name'] for s in ['scenario1', 'scenario2', 'scenario3']]
            throughputs = [results[s]['total_throughput'] for s in ['scenario1', 'scenario2', 'scenario3']]
            colors = ['#16a34a' if t == max(throughputs) else '#3b82f6' for t in throughputs]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=names,
                y=throughputs,
                marker_color=colors,
                text=[f'${t:,.0f}' for t in throughputs],
                textposition='outside'
            ))
            
            fig.update_layout(
                yaxis_title='Throughput ($)',
                showlegend=False,
                height=400
            )
            
            return fig
    
    # Product mix comparison chart
    with ui.card():
        ui.card_header("Product Mix Comparison")
        
        @render.plot
        def product_mix_chart():
            results = solve_scenarios()
            
            fig = go.Figure()
            
            for sid in ['scenario1', 'scenario2', 'scenario3']:
                fig.add_trace(go.Bar(
                    name=results[sid]['name'],
                    x=['Product A', 'Product B'],
                    y=[results[sid]['product_a'], results[sid]['product_b']],
                ))
            
            fig.update_layout(
                yaxis_title='Units Produced',
                barmode='group',
                height=400
            )
            
            return fig

# Insights section
ui.hr()
ui.h2("💡 Automatic Insights & Recommendations")

@render.ui
def insights():
    results = solve_scenarios()
    
    # Find best scenario
    best_sid = max(results.items(), key=lambda x: x[1]['total_throughput'])[0]
    best_result = results[best_sid]
    best_name = best_result['name']
    
    # Calculate differences
    baseline_throughput = results['scenario1']['total_throughput']
    best_throughput = best_result['total_throughput']
    improvement = best_throughput - baseline_throughput
    improvement_pct = (improvement / baseline_throughput) * 100 if baseline_throughput > 0 else 0
    
    insights_html = f"""
    <div style="background-color: #dcfce7; padding: 15px; border-radius: 8px; border-left: 4px solid #16a34a; margin: 10px 0;">
        <strong>Best Scenario:</strong> {best_name} achieves the highest throughput at ${best_throughput:,.2f}
    </div>
    """
    
    if best_sid != 'scenario1':
        insights_html += f"""
        <div style="background-color: #dcfce7; padding: 15px; border-radius: 8px; border-left: 4px solid #16a34a; margin: 10px 0;">
            <strong>Improvement:</strong> {best_name} produces ${improvement:,.2f} ({improvement_pct:.1f}%) more than the baseline
        </div>
        """
    
    # Bottleneck insights
    bottlenecks = [results[s]['bottleneck'] for s in ['scenario1', 'scenario2', 'scenario3']]
    if len(set(bottlenecks)) > 1:
        insights_html += f"""
        <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; margin: 10px 0;">
            <strong>Bottleneck Shift:</strong> The constraint changes across scenarios: {', '.join(set(bottlenecks))}
        </div>
        """
    else:
        insights_html += f"""
        <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; margin: 10px 0;">
            <strong>Consistent Bottleneck:</strong> {bottlenecks[0]} remains the constraint across all scenarios
        </div>
        """
    
    return ui.HTML(insights_html)

# Footer
ui.hr()
ui.markdown("""
**Why Python > Excel for This:** Excel Solver requires manual solving of each scenario, 
separate worksheets, manual comparison charts, and significant time. Python does it all 
automatically in real-time!

*Based on "The Goal" by Eliyahu M. Goldratt*
""")
