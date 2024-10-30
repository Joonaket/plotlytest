import base64
import io
import threading
from queue import Queue
import logging
import pandas as pd
import numpy as np
from collections import deque
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from Animation import Animator
from utils import CHUNK_SIZE, SAMPLE_RATE, DISPLAY_TIME, ANIMATION_SPEED
from data_processing import process_chunk

class DualADCSignalAnalyzer:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.app.title = "Dual ADC Signal Analyzer"

        # Initialize parameters
        self.chunk_size = CHUNK_SIZE
        self.sample_rate = SAMPLE_RATE
        self.display_time = DISPLAY_TIME
        self.display_points = int(self.display_time * self.sample_rate)
        self.binary_filepath = None
        self.animation_speed = ANIMATION_SPEED

        # Data buffers for both ADC channels
        self.adc1_buffer = deque(maxlen=self.display_points)
        self.adc2_buffer = deque(maxlen=self.display_points)

        # Peak detection parameters
        self.recent_adc1_peaks = []
        self.recent_adc2_peaks = []

        # Threading control
        self.stop_event = threading.Event()
        self.data_queue = Queue()

        # Statistics
        self.adc1_peak_count = 0
        self.adc2_peak_count = 0
        self.processed_duration = 0

        # Prepare layout for Dash app
        self.create_layout()
        self.animator = Animator(self)

    def create_layout(self):
        self.app.layout = html.Div([
            html.H1("Real-Time Dual ADC Signal Analyzer"),
            dcc.Graph(id='live-graph'),
            dcc.Interval(id='interval-component', interval=self.animation_speed, n_intervals=0),
            dcc.Upload(id='file-upload', children=html.Button('Upload CSV'), multiple=False),
            html.Button('Load File', id='load-button', n_clicks=0),
            html.Div(id='filename-label'),
            html.Div(id='progress-output', style={'width': '100%', 'background-color': '#f3f3f3', 'border': '1px solid #ccc', 'border-radius': '5px'}),
            html.Div(id='progress-bar', style={'width': '0%', 'height': '20px', 'background-color': '#4caf50', 'border-radius': '5px'})
        ])

    def load_file(self, contents):
        """Loads and converts a CSV file to binary format."""
        try:
            if contents:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                if 'adc1' not in df.columns or 'adc2' not in df.columns:
                    raise ValueError("CSV file must contain 'adc1' and 'adc2' columns")

                # Convert to binary format and save
                self.binary_filepath = "data.bin"  # Use a temp file path for demonstration
                df.to_pickle(self.binary_filepath)

                return f"Loaded: {self.binary_filepath.split('/')[-1]}"
            return "No file selected."
        except Exception as e:
            logging.error(f"Error loading file: {e}")
            return str(e)

    def process_chunk(self, chunk_data, threshold):
        """Process a chunk of data with a given threshold."""
        try:
            # Call the standalone function if needed, or implement your logic
            return process_chunk(chunk_data, threshold)  # Importing this from data_processing
        except Exception as e:
            logging.error(f"Error processing chunk: {e}")
            return None

    def process_data_thread(self):
        """Process binary data chunks and send them to `process_chunk`."""
        try:
            # Check if binary file exists
            if not self.binary_filepath:
                raise ValueError("Binary file not found. Please load a file first.")

            # Load binary data into a DataFrame
            binary_data = pd.read_pickle(self.binary_filepath)

            # Process data in chunks
            for i in range(0, len(binary_data), self.chunk_size):
                if self.stop_event.is_set():
                    break

                # Select the chunk and send to `process_chunk`
                chunk = binary_data.iloc[i:i + self.chunk_size]
                result = process_chunk(chunk)

                if result is not None:
                    self.data_queue.put(result)

                # Update progress
                self.update_progress(i / len(binary_data) * 100)

        except Exception as e:
            logging.error(f"Error in data processing thread: {e}")

    def update_progress(self, value):
        """Update the progress value in the progress bar."""
        self.processed_duration += self.chunk_size / self.sample_rate
        # Here you could set the width of a progress bar in a callback if you had it as an Output

    def update_graph(self, n):
        """Update the graph with new data."""
        if not self.data_queue.empty():
            data = self.data_queue.get()
            self.adc1_buffer.extend(data['adc1'][-self.display_points:])
            self.adc2_buffer.extend(data['adc2'][-self.display_points:])


            time_values = np.linspace(max(0, self.processed_duration - self.display_time), self.processed_duration, len(self.adc1_buffer))
            adc1_trace = go.Scattergl(x=time_values, y=list(self.adc1_buffer), mode='lines', name='ADC1 Signal')
            adc2_trace = go.Scattergl(x=time_values, y=list(self.adc2_buffer), mode='lines', name='ADC2 Signal')

            # Create a figure and return it
            fig = go.Figure(data=[adc1_trace, adc2_trace])
            fig.update_layout(title="Real-Time ADC Signals", xaxis_title="Time (s)", yaxis_title="ADC Value")
            return fig

    def start_analysis(self):
        """Start the analysis process."""
        if not self.binary_filepath:
            raise ValueError("Please load a file first!")

        self.stop_event.clear()
        self.adc1_peak_count = 0
        self.adc2_peak_count = 0
        self.processed_duration = 0

        # Start processing thread
        processing_thread = threading.Thread(target=self.process_data_thread)
        processing_thread.start()

    def stop_analysis(self):
        """Stop the analysis process."""
        self.stop_event.set()

    def run(self):
        """Run the Dash app."""
        @self.app.callback(
            Output('live-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_graph_live(n):
            return self.update_graph(n)

        @self.app.callback(
            Output('filename-label', 'children'),
            Input('load-button', 'n_clicks'),
            Input('file-upload', 'contents')  # Use contents for file upload
        )
        def load_file_callback(n_clicks, contents):
            if n_clicks > 0 and contents:
                return self.load_file(contents)
            return "No file loaded yet."

        self.app.run_server(debug=True)

# Create an instance and run the application
if __name__ == "__main__":
    analyzer = DualADCSignalAnalyzer()
    analyzer.run()
