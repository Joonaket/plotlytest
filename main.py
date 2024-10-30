import base64
import io

import dash
import numpy as np
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc  # Optional for styling
import pandas as pd
import plotly.graph_objs as go
from dual_adc_analyzer import DualADCSignalAnalyzer

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # Using Bootstrap for styling (optional)

# Initialize your main processing class
analyzer = DualADCSignalAnalyzer()

# Define the layout of the app
app.layout = html.Div([
    html.H1("Dual ADC Signal Analyzer"),
    dcc.Upload(id='upload-data', children=html.Button('Upload CSV')),
    dcc.Loading(id="loading", type="default", children=[
        dcc.Graph(id='signal-plot'),
    ]),
    dcc.Slider(id='threshold-slider', min=0, max=1000, value=850,
               marks={i: str(i) for i in range(0, 1001, 100)}, step=10),
    html.Div(id='stats-output'),
    html.Div(id='progress-output')  # To show progress
])


# Callback to handle data upload and processing
@app.callback(
    Output('signal-plot', 'figure'),
    Output('stats-output', 'children'),
    Input('upload-data', 'contents'),
    Input('threshold-slider', 'value')
)
def update_output(uploaded_data, threshold):
    if uploaded_data is not None:
        # Handle file upload, here you'd parse the uploaded file
        # Assume the uploaded data is a DataFrame
        content_type, content_string = uploaded_data.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Process the data using the analyzer
        result = analyzer.process_chunk(df, threshold)  # Ensure your process_chunk function handles the threshold

        # Create the plotly figure
        figure = go.Figure()

        # Plot ADC1 Signal
        figure.add_trace(go.Scatter(x=np.arange(len(result['adc1'])), y=result['adc1'],
                                     mode='lines', name='ADC1 Signal'))

        # Plot ADC2 Signal
        figure.add_trace(go.Scatter(x=np.arange(len(result['adc2'])), y=result['adc2'],
                                     mode='lines', name='ADC2 Signal'))

        # Mark Peaks
        if result['adc1_peaks'].size > 0:
            figure.add_trace(go.Scatter(x=result['adc1_peaks'], y=result['adc1'][result['adc1_peaks']],
                                         mode='markers', name='ADC1 Peaks', marker=dict(color='red', size=8)))

        if result['adc2_peaks'].size > 0:
            figure.add_trace(go.Scatter(x=result['adc2_peaks'], y=result['adc2'][result['adc2_peaks']],
                                         mode='markers', name='ADC2 Peaks', marker=dict(color='blue', size=8)))

        figure.update_layout(title='ADC Signal Analysis',
                             xaxis_title='Samples',
                             yaxis_title='Signal Value',
                             showlegend=True)

        stats = f"ADC1 Peaks: {len(result['adc1_peaks'])} | ADC2 Peaks: {len(result['adc2_peaks'])}"

        return figure, stats

    return go.Figure(), "No data processed yet."

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
