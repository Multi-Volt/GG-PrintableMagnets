# Copyright (c) 2025, John Simonis
# This code was written by John Simonis for the GreyGoo research project at The Ohio State University.
# See LICENSE.txt for more information.

import sys
import os
import serial
import serial.tools.list_ports
import pandas as pd
import openpyxl
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import magnetic_logger_core as core

class MagneticFieldLoggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Magnetic Imager")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f2f5")

        self.ser = None
        self.filename = None
        self.filename_base = None
        self.excel_wb = None
        self.excel_sheet = None
        self.df = None

        self.init_ui()

    def init_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", padding=6, font=("Segoe UI", 10))
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("TLabelframe", padding=12)
        style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        for i in range(4):
            main_frame.rowconfigure(i, weight=1)
        main_frame.columnconfigure(1, weight=1)

        serial_frame = ttk.LabelFrame(main_frame, text="Serial Connection")
        serial_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        serial_frame.columnconfigure(1, weight=1)

        ttk.Label(serial_frame, text="Select serial port:").grid(column=0, row=0, sticky="w")
        self.port_combo = ttk.Combobox(serial_frame, state="readonly")
        self.port_combo.grid(column=1, row=0, sticky="ew", padx=5)
        ttk.Button(serial_frame, text="Refresh", command=self.refresh_ports).grid(column=2, row=0, padx=5)
        ttk.Button(serial_frame, text="Connect", command=self.connect_serial).grid(column=3, row=0, padx=5)

        file_frame = ttk.LabelFrame(main_frame, text="Excel File")
        file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        file_frame.columnconfigure(1, weight=1)

        self.file_label = ttk.Label(file_frame, text="Excel file: (none)", font=("Segoe UI", 10, "italic"))
        self.file_label.grid(column=0, row=0, columnspan=2, sticky="w")
        ttk.Button(file_frame, text="Select File", command=self.select_file).grid(column=2, row=0, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        for i in range(3):
            button_frame.columnconfigure(i, weight=1)

        self.btn_calibrate = ttk.Button(button_frame, text="Calibrate Sensor", command=self.calibrate_sensor, state="disabled")
        self.btn_calibrate.grid(column=0, row=0, padx=10, sticky="ew")

        self.btn_trial = ttk.Button(button_frame, text="Run Trial", command=self.run_trial, state="disabled")
        self.btn_trial.grid(column=1, row=0, padx=10, sticky="ew")

        self.btn_finish = ttk.Button(button_frame, text="Finish and Plot", command=self.finish_plot, state="disabled")
        self.btn_finish.grid(column=2, row=0, padx=10, sticky="ew")

        log_frame = ttk.LabelFrame(main_frame, text="Log Output")
        log_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_box = scrolledtext.ScrolledText(log_frame, height=15, wrap="word", state="disabled", font=("Consolas", 10))
        self.log_box.grid(column=0, row=0, sticky="nsew")

        self.root.after_idle(self.refresh_ports)

    def log(self, message):
        def append():
            self.log_box.configure(state="normal")
            self.log_box.insert(tk.END, message + "\n")
            self.log_box.configure(state="disabled")
            self.log_box.see(tk.END)
        self.root.after(0, append)
        print(message)

    def refresh_ports(self):
        self.port_combo['values'] = [p.device for p in serial.tools.list_ports.comports()]
        if self.port_combo['values']:
            self.port_combo.current(0)

    def connect_serial(self):
        port = self.port_combo.get()
        if not port:
            messagebox.showwarning("Error", "No serial port selected.")
            return
        try:
            self.ser = serial.Serial(port, 9600, timeout=1)
            self.log(f"[✔ Connected to {port}]")
            self.btn_calibrate.config(state="normal")
            self.btn_trial.config(state="normal")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def select_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if path:
            self.filename = path
            self.filename_base = os.path.splitext(os.path.basename(path))[0]
            self.file_label.config(text=f"Excel file: {os.path.basename(path)}")

            if os.path.exists(path):
                try:
                    self.excel_wb = openpyxl.load_workbook(path)
                    self.excel_sheet = self.excel_wb.active
                    self.df = pd.read_excel(path)
                    messagebox.showinfo("Loaded", "Existing Excel file loaded.")
                    self.log(f"[✔ Loaded existing file '{path}']")
                    self.btn_trial.config(state="normal")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load Excel: {e}")
                    self.excel_wb = None
                    self.excel_sheet = None
                    self.df = None
                    self.btn_trial.config(state="disabled")
            else:
                self.excel_wb, self.excel_sheet = core.setup_excel(path)
                self.df = None
                messagebox.showinfo("New File", "New Excel file initialized.")
                self.btn_trial.config(state="normal")

            self.btn_finish.config(state="normal")

    def calibrate_sensor(self):
        if self.ser:
            threading.Thread(target=self._calibrate_worker, daemon=True).start()
        else:
            messagebox.showwarning("Error", "Serial port not connected.")

    def _calibrate_worker(self):
        core.calibrate_sensor(self.ser, log_func=self.log)
        self.root.after(0, lambda: messagebox.showinfo("Calibration", "Calibration complete."))

    def run_trial(self):
        if not self.ser or not self.excel_sheet:
            messagebox.showwarning("Error", "No serial connection or Excel file.")
            return

        trial_window = tk.Toplevel(self.root)
        trial_window.title("Run Trial Parameters")
        trial_window.geometry("300x180")
        trial_window.grab_set()

        ttk.Label(trial_window, text="Trial Name:").grid(row=0, column=0, sticky="e")
        trial_entry = ttk.Entry(trial_window)
        trial_entry.grid(row=0, column=1)

        ttk.Label(trial_window, text="Sensor Height (cm):").grid(row=1, column=0, sticky="e")
        height_entry = ttk.Entry(trial_window)
        height_entry.grid(row=1, column=1)

        ttk.Label(trial_window, text="Distance from Magnet (cm):").grid(row=2, column=0, sticky="e")
        radius_entry = ttk.Entry(trial_window)
        radius_entry.grid(row=2, column=1)

        def start_trial():
            trial = trial_entry.get()
            try:
                height = float(height_entry.get())
                radius = float(radius_entry.get())
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers for height and radius.")
                return
            trial_window.destroy()
            threading.Thread(target=self._run_trial_worker, args=(trial, height, radius), daemon=True).start()

        ttk.Button(trial_window, text="Start", command=start_trial).grid(row=3, column=0, columnspan=2, pady=10)

    def _run_trial_worker(self, trial, height, radius):
        core.run_trial(self.ser, self.excel_sheet, trial, height, radius, log_func=self.log)
        self.root.after(0, lambda: messagebox.showinfo("Trial", "Trial appended to Excel file."))

    def finish_plot(self):
        if self.excel_wb:
            self.excel_wb.save(self.filename)
            self.log(f"[✔ Excel saved to '{self.filename}']")
            try:
                self.df = pd.read_excel(self.filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read Excel: {e}")
                return
        elif self.df is not None:
            self.log(f"[✔ Using existing Excel file '{self.filename}' for plotting]")
        else:
            messagebox.showwarning("Error", "No data available to plot.")
            return

        plot_window = tk.Toplevel(self.root)
        plot_window.title("Select Plot Type")
        plot_window.geometry("300x200")
        plot_window.grab_set()

        ttk.Label(plot_window, text="Choose a plot type:").pack(pady=10)
        choices = [
            ("1 - Scalar Field", "1"),
            ("2 - Unit Vector Field", "2"),
            ("3 - True Vector Field", "3"),
            ("4 - Mesh Deformation", "4")
        ]
        selected = tk.StringVar(value="1")

        for text, val in choices:
            ttk.Radiobutton(plot_window, text=text, variable=selected, value=val).pack(anchor="w")

        def generate_plot():
            plot_choice = selected.get()
            plot_window.destroy()
            output_dir = os.path.dirname(self.filename)
            core.plot_data(self.df, self.filename_base, plot_choice, output_dir=output_dir, log_func=self.log)

        ttk.Button(plot_window, text="Plot", command=generate_plot).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MagneticFieldLoggerGUI(root)
    root.mainloop()
