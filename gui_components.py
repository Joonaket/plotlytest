import tkinter as tk
from tkinter import ttk

import tkinter as tk
from tkinter import ttk, messagebox


def create_widgets(self):
    control_frame = ttk.Frame(self.root)
    control_frame.pack(pady=5)

    ttk.Button(control_frame, text="Load Data File", command=self.load_file).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Start Analysis", command=self.start_analysis).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Stop Analysis", command=self.stop_analysis).pack(side=tk.LEFT, padx=5)

    # Threshold sensitivity frame
    threshold_frame = ttk.Frame(self.root)
    threshold_frame.pack(pady=5)
    ttk.Label(threshold_frame, text="Peak Sensitivity (Threshold):").pack(side=tk.LEFT)

    # Updated range for sensitivity (adjust as needed)
    self.threshold_slider = ttk.Scale(threshold_frame, from_=0.0, to=1000.0,
                                      orient=tk.HORIZONTAL, length=200)
    self.threshold_slider.set(850)  # Default threshold value
    self.threshold_slider.pack(side=tk.LEFT)

    self.filename_label = tk.Label(self.root, text="No file loaded", anchor='w')
    self.filename_label.pack(side=tk.TOP, fill=tk.Y)

    # Stats frame to show processing stats
    stats_frame = ttk.Frame(self.root)
    stats_frame.pack(pady=5)
    self.stats_label = ttk.Label(stats_frame, text="Processed: 0s | ADC1 Peaks: 0 | ADC2 Peaks: 0")
    self.stats_label.pack()

    self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
    self.progress.pack(pady=5)
