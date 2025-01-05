import time
import threading
import plotly.graph_objects as go
import pandas as pd

def generate_battery_visualizations():
    try:
        # Load data from CSV
        df = pd.read_csv('battery_data.csv')
        df_additional = pd.read_csv('additional_data.csv')

        # Plot individual cell voltages (Voltage_1 to Voltage_24)
        voltage_fig = go.Figure()
        for i in range(1, 25):
            cell_voltage = f"Voltage_{i}"
            if cell_voltage in df.columns:
                voltage_fig.add_trace(go.Scatter(
                    y=df[cell_voltage],
                    mode='lines+markers',
                    name=cell_voltage,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
        voltage_fig.update_layout(
            title="Battery Cell Voltages (Voltage_1 to Voltage_24)",
            xaxis_title="Time",
            yaxis_title="Voltage (V)",
            legend_title="Cell Voltages",
            template="plotly_white"
        )

        # SOC Visualization
        soc_fig = go.Figure()
        soc_fig.add_trace(go.Scatter(
            y=df['SOC'],
            mode='lines+markers',
            name='SOC',
            line=dict(color='green'),
            marker=dict(size=8)
        ))
        soc_fig.update_layout(
            title="State of Charge",
            xaxis_title="Time",
            yaxis_title="SOC (%)",
            template="plotly_white"
        )

        # Temperature Visualization
        temp_fig = go.Figure()
        temp_fig.add_trace(go.Scatter(
            y=df['Temperature'],
            mode='lines',
            name='Temperature',
            line=dict(color='red')
        ))
        temp_fig.update_layout(
            title="Battery Temperature",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            template="plotly_white"
        )

        # Cell Voltage Range
        range_fig = go.Figure()
        range_fig.add_trace(go.Scatter(
            x=list(range(1, len(df) + 1)),
            y=df['CellMinimumVoltage'],
            mode='lines',
            fill='tonexty',
            name='Min Voltage',
            line=dict(color='orange')
        ))
        range_fig.add_trace(go.Scatter(
            x=list(range(1, len(df) + 1)),
            y=df['CellMaximumVoltage'],
            mode='lines',
            fill='tonexty',
            name='Max Voltage',
            line=dict(color='green')
        ))
        range_fig.update_layout(
            title="Voltage Range of Cells",
            xaxis_title="Time",
            yaxis_title="Voltage (V)",
            template="plotly_white"
        )

        # ERRORStatus Visualization
        error_fig = go.Figure()
        error_fig.add_trace(go.Bar(
            y=df['ERRORStatus'],
            name='Error Status',
            marker_color='purple'
        ))
        error_fig.update_layout(
            title="Error Status",
            xaxis_title="Time",
            yaxis_title="Error Code",
            template="plotly_white"
        )

        # Distance Travelled Visualization
        distance_fig = go.Figure()
        distance_fig.add_trace(go.Scatter(
            x=df_additional['Runtime'],
            y=df_additional['DistanceTravelled'],
            mode='lines+markers',
            name='Distance Travelled',
            line=dict(color='blue'),
            marker=dict(size=8)
        ))
        distance_fig.update_layout(
            title="Distance Travelled Over Time",
            xaxis_title="Runtime",
            yaxis_title="Distance Travelled (km)"
        )

        # Range Left Visualization
        range_left_fig = go.Figure()
        range_left_fig.add_trace(go.Scatter(
            x=df_additional['Runtime'],
            y=df_additional['RangeLeft'],
            mode='lines+markers',
            name='Range Left',
            line=dict(color='green'),
            marker=dict(size=8)
        ))
        range_left_fig.update_layout(
            title="Range Left Over Time",
            xaxis_title="Runtime",
            yaxis_title="Range Left (km)"
        )

        # Combined Visualization
        combined_fig = go.Figure()
        combined_fig.add_trace(go.Scatter(
            x=df_additional['Runtime'],
            y=df_additional['DistanceTravelled'],
            mode='lines+markers',
            name='Distance Travelled',
            line=dict(color='blue'),
            marker=dict(size=8),
            yaxis='y1'
        ))
        combined_fig.add_trace(go.Scatter(
            x=df_additional['Runtime'],
            y=df_additional['RangeLeft'],
            mode='lines+markers',
            name='Range Left',
            line=dict(color='green'),
            marker=dict(size=8),
            yaxis='y2'
        ))
        combined_fig.update_layout(
            title="Distance Travelled and Range Left Over Time",
            xaxis_title="Runtime",
            yaxis_title="Distance Travelled (km)",
            yaxis2=dict(
                title="Range Left (km)",
                overlaying="y",
                side="right"
            )
        )

        # Write plots to HTML
        voltage_fig.write_html("templates/voltage_plot.html")
        soc_fig.write_html("templates/soc_plot.html")
        temp_fig.write_html("templates/temp_plot.html")
        range_fig.write_html("templates/range_plot.html")
        error_fig.write_html("templates/error_plot.html")
        distance_fig.write_html("templates/distance_plot.html")
        range_left_fig.write_html("templates/range_left_plot.html")
        combined_fig.write_html("templates/combined_plot.html")
        print("Plots successfully generated.")
    except Exception as e:
        print(f"Error while generating visualizations: {e}")

def schedule_visualization(interval):
    while True:
        generate_battery_visualizations()
        time.sleep(interval)

# # Run the function every 90 seconds in a separate thread
# thread = threading.Thread(target=schedule_visualization, args=(90,))
# thread.daemon = True
# thread.start()
schedule_visualization(7)