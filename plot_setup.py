import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from collections import deque
import time


def setup_plot(analyzer):
    # Plot setup using Plotly
    fig = go.Figure()

    # ADC1 and ADC2 traces
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='ADC1 Signal', line=dict(color='blue')))
    fig.add_trace(
        go.Scatter(x=[], y=[], mode='markers', name='ADC1 Peaks', marker=dict(color='red', size=10, symbol='x')))

    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='ADC2 Signal', line=dict(color='green')))
    fig.add_trace(
        go.Scatter(x=[], y=[], mode='markers', name='ADC2 Peaks', marker=dict(color='red', size=10, symbol='x')))

    fig.update_layout(
        title="Dual ADC Signal Analyzer",
        xaxis=dict(title="Time (s)", range=[0, analyzer.display_time]),
        yaxis=dict(title="ADC Value", range=[390, 1520]),
        height=800
    )

    analyzer.fig = fig
