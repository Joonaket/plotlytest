import numpy as np
import plotly.graph_objs as go
from dash import Output, Input, dash, html, dcc


class Animator:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def update_plot(self, n):
        if self.analyzer.data_queue.empty():
            return dash.no_update

        # Retrieve data from queue
        data = self.analyzer.data_queue.get()
        self.analyzer.processed_duration += self.analyzer.display_time

        # Update buffers for ADC1 and ADC2
        self.analyzer.adc1_buffer.extend(data['adc1'][-self.analyzer.display_points:])
        self.analyzer.adc2_buffer.extend(data['adc2'][-self.analyzer.display_points:])

        # Update peak counts
        self.analyzer.adc1_peak_count += len(data['adc1_peaks'])
        self.analyzer.adc2_peak_count += len(data['adc2_peaks'])

        # Calculate time values for scrolling effect
        start_time = max(0, self.analyzer.processed_duration - self.analyzer.display_time)
        time_values = np.linspace(start_time, self.analyzer.processed_duration, len(self.analyzer.adc1_buffer))

        # Prepare data for updating the figure
        traces = [
            # ADC1 Signal
            go.Scatter(x=time_values, y=list(self.analyzer.adc1_buffer), mode='lines', name='ADC1 Signal',
                       line=dict(color='blue')),
            # ADC1 Peaks
            go.Scatter(x=[time_values[peak] for peak in data['adc1_peaks']],
                       y=[self.analyzer.adc1_buffer[peak] for peak in data['adc1_peaks']], mode='markers',
                       name='ADC1 Peaks', marker=dict(color='red', size=10, symbol='x')),

            # ADC2 Signal
            go.Scatter(x=time_values, y=list(self.analyzer.adc2_buffer), mode='lines', name='ADC2 Signal',
                       line=dict(color='green')),
            # ADC2 Peaks
            go.Scatter(x=[time_values[peak] for peak in data['adc2_peaks']],
                       y=[self.analyzer.adc2_buffer[peak] for peak in data['adc2_peaks']], mode='markers',
                       name='ADC2 Peaks', marker=dict(color='red', size=10, symbol='x'))
        ]

        # Update figure layout and data
        self.analyzer.fig.update_traces(overwrite=True)
        self.analyzer.fig.update_xaxes(range=[start_time, self.analyzer.processed_duration])
        return traces

    def start_animation(self):
        app = dash.Dash(__name__)

        # Layout
        app.layout = html.Div([
            html.H1("Real-Time Dual ADC Signal Analyzer"),
            dcc.Graph(id="live-graph", figure=self.analyzer.fig),
            dcc.Interval(id="interval-component", interval=1000)  # Update interval in ms
        ])

        # Callback to update the figure at each interval
        @app.callback(
            Output("live-graph", "figure"),
            Input("interval-component", "n_intervals")
        )
        def update_graph_live(n_intervals):
            return go.Figure(data=self.update_plot(n_intervals))

        # Run the Dash app
        app.run_server(debug=True)
