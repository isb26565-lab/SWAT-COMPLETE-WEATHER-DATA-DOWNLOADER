# -*- coding: utf-8 -*-
"""
Modern GUI for the SWAT weather data downloader.

Run with:
    python swat_weather_app.py

This app is intentionally a thin, friendly layer over
swat_complete_data_downloader_real.py. The downloader still does the scientific
work; this file handles file selection, settings, progress messages, and a
responsive Windows interface.
"""

from __future__ import annotations

import os
import queue
import sys
import threading
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import numpy as np
import pandas as pd

DEFAULT_WATERSHED = r"C:\SWAT_Project\GIS\Watershed_Boundary.shp"
DEFAULT_DEM = r"C:\SWAT_Project\GIS\DEM.tif"
DEFAULT_OUTPUT = r"C:\SWAT_Project\Thoubal_SWAT_Real"
DEFAULT_IMD_RAW = r"C:\SWAT_Project\IMD_Raw_Data"

# ── Color palette ──
BG_DARK = "#0f1117"
BG_CARD = "#181b24"
BG_CARD_HOVER = "#1e2230"
BG_INPUT = "#232736"
BG_INPUT_FOCUS = "#2a2f40"
BORDER = "#2d3348"
BORDER_FOCUS = "#5b8def"
TEXT_PRIMARY = "#e8ecf4"
TEXT_SECONDARY = "#8b95a8"
TEXT_MUTED = "#5c6478"
ACCENT = "#5b8def"
ACCENT_HOVER = "#7ba4f7"
ACCENT_GLOW = "#5b8def"
SUCCESS = "#34d399"
ERROR = "#f87171"
ERROR_HOVER = "#fca5a5"
WARN = "#fbbf24"
LOG_BG = "#0c0e14"
SCROLLBAR = "#2d3348"
SCROLLBAR_HOVER = "#3d4560"


class QueueWriter:
    """Redirect print output from the worker thread into the GUI log."""

    def __init__(self, log_queue: queue.Queue[str]):
        self.log_queue = log_queue

    def write(self, text: str) -> None:
        if text:
            self.log_queue.put(text)

    def flush(self) -> None:
        pass


class ModernEntry(tk.Frame):
    """A styled text entry with focus glow."""

    def __init__(self, parent, textvariable=None, width=30, **kw):
        super().__init__(parent, bg=BG_CARD, highlightthickness=0)
        self.border_frame = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        self.border_frame.pack(fill="x")
        self.entry = tk.Entry(
            self.border_frame, textvariable=textvariable, width=width,
            bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=ACCENT,
            font=("Segoe UI", 10), relief="flat", bd=0,
            highlightthickness=0, **kw,
        )
        self.entry.pack(fill="x", padx=1, pady=1, ipady=6, ipadx=6)
        self.entry.bind("<FocusIn>", lambda e: self.border_frame.configure(bg=BORDER_FOCUS))
        self.entry.bind("<FocusOut>", lambda e: self.border_frame.configure(bg=BORDER))


class ModernButton(tk.Frame):
    """A rounded, animated button using a Frame + Canvas for reliability."""

    def __init__(self, parent, text="", command=None, accent=False, width=120, height=38):
        super().__init__(parent, bg=BG_CARD, highlightthickness=0, bd=0)
        self._text = text
        self._command = command
        self._accent = accent
        self._btn_w = width
        self._btn_h = height
        self._hover = False
        self._disabled = False
        self._canvas = tk.Canvas(self, width=width, height=height, bg=BG_CARD,
                                 highlightthickness=0, bd=0)
        self._canvas.pack()
        self._canvas.bind("<Enter>", self._on_enter)
        self._canvas.bind("<Leave>", self._on_leave)
        self._canvas.bind("<ButtonRelease-1>", self._on_click)
        self.after_idle(self._draw)

    def _draw(self):
        c = self._canvas
        c.delete("all")
        if self._disabled:
            bg, fg = "#1e2230", TEXT_MUTED
        elif self._hover and self._accent == "danger":
            bg, fg = ERROR_HOVER, "#ffffff"
        elif self._accent == "danger":
            bg, fg = ERROR, "#ffffff"
        elif self._hover and self._accent:
            bg, fg = ACCENT_HOVER, "#ffffff"
        elif self._accent:
            bg, fg = ACCENT, "#ffffff"
        elif self._hover:
            bg, fg = BG_CARD_HOVER, TEXT_PRIMARY
        else:
            bg, fg = BG_INPUT, TEXT_SECONDARY
        r = 8
        x1, y1, x2, y2 = 2, 2, self._btn_w - 2, self._btn_h - 2
        c.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=bg, outline=bg)
        c.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=bg, outline=bg)
        c.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=bg, outline=bg)
        c.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=bg, outline=bg)
        c.create_rectangle(x1+r, y1, x2-r, y2, fill=bg, outline=bg)
        c.create_rectangle(x1, y1+r, x2, y2-r, fill=bg, outline=bg)
        c.create_text(self._btn_w // 2, self._btn_h // 2, text=self._text,
                      fill=fg, font=("Segoe UI Semibold", 10))

    def _on_enter(self, _e):
        if not self._disabled:
            self._hover = True
            self._draw()

    def _on_leave(self, _e):
        self._hover = False
        self._draw()

    def _on_click(self, _e):
        if not self._disabled and self._command:
            self._command()

    def set_disabled(self, val: bool):
        self._disabled = val
        self._draw()


class SWATWeatherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SWAT Weather Data Downloader")
        self.geometry("1100x750")
        self.minsize(960, 660)
        self.configure(bg=BG_DARK)

        # Set up ttk style BEFORE building any widgets
        self._setup_style()

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.worker: Optional[threading.Thread] = None
        self._cancel_event = threading.Event()

        self.vars = {
            "watershed": tk.StringVar(value=DEFAULT_WATERSHED),
            "dem": tk.StringVar(value=DEFAULT_DEM),
            "output": tk.StringVar(value=DEFAULT_OUTPUT),
            "imd_raw": tk.StringVar(value=DEFAULT_IMD_RAW),
            "area_name": tk.StringVar(value="Lower Thoubal River Catchment"),
            "file_prefix": tk.StringVar(value="Thoubal_SWAT"),
            "start_year": tk.StringVar(value="2010"),
            "end_year": tk.StringVar(value="2020"),
            "bands": tk.StringVar(value="5"),
            "stations_per_band": tk.StringVar(value="1"),
            "temp_lapse_rate": tk.StringVar(value="-6.5"),
            "precip_lapse_rate": tk.StringVar(value="16.0"),
        }

        self.status_var = tk.StringVar(value="Ready")
        self.data_var = tk.StringVar(value="")
        self._build_ui()
        self.after(100, self._drain_log_queue)

    def _setup_style(self) -> None:
        """Configure ttk theme and progressbar style once, before any widgets."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TProgressbar", background=ACCENT, troughcolor=BG_INPUT,
                        bordercolor=BG_CARD, lightcolor=ACCENT, darkcolor=ACCENT)

    # ── UI Construction ──

    def _build_ui(self) -> None:
        root = tk.Frame(self, bg=BG_DARK, padx=20, pady=16)
        root.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(root, bg=BG_DARK)
        hdr.pack(fill="x", pady=(0, 16))
        tk.Label(hdr, text="SWAT Weather Data Downloader", font=("Segoe UI Semibold", 20),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")
        tk.Label(hdr, text="Made by Shujat Mehdi", font=("Segoe UI", 10),
                 bg=BG_DARK, fg=TEXT_MUTED).pack(side="right")

        # Subtitle
        tk.Label(root, text="Build SWAT-ready weather files from IMD gridded data and NASA POWER.",
                 font=("Segoe UI", 10), bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w", pady=(0, 12))

        # Body: left settings + right log
        body = tk.PanedWindow(root, orient="horizontal", bg=BG_DARK, bd=0,
                              sashwidth=8, sashrelief="flat", opaqueresize=True)
        body.pack(fill="both", expand=True)

        # ── Left panel ──
        left_outer = tk.Frame(body, bg=BG_CARD, bd=0)
        body.add(left_outer, width=460, minsize=380)

        # Scrollable settings
        canvas = tk.Canvas(left_outer, bg=BG_CARD, highlightthickness=0, bd=0)
        canvas.pack(side="top", fill="both", expand=True)
        sb = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview,
                          bg=SCROLLBAR, troughcolor=BG_CARD, width=10, relief="flat")
        sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)

        inner = tk.Frame(canvas, bg=BG_CARD, padx=20, pady=16)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width - 14))
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # mousewheel
        def _mw(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _mw)

        self._section(inner, "Project Files", 0)
        self._path_row(inner, 1, "Watershed shapefile", "watershed", self._browse_shapefile)
        self._path_row(inner, 2, "DEM raster", "dem", self._browse_dem)
        self._path_row(inner, 3, "Output folder", "output", lambda: self._browse_folder("output"))
        self._path_row(inner, 4, "IMD raw folder", "imd_raw", lambda: self._browse_folder("imd_raw"))

        self._section(inner, "Naming", 5)
        self._text_row(inner, 6, "Area name", "area_name")
        self._text_row(inner, 7, "File prefix", "file_prefix")

        self._section(inner, "Run Settings", 8)
        self._number_row(inner, 9, "Start year", "start_year")
        self._number_row(inner, 10, "End year", "end_year")
        self._number_row(inner, 11, "Elevation bands", "bands")
        self._number_row(inner, 12, "Stations / band", "stations_per_band")
        self._number_row(inner, 13, "Temp lapse (C/1000m)", "temp_lapse_rate")
        self._number_row(inner, 14, "Precip lapse (%/100m)", "precip_lapse_rate")

        tk.Label(inner, text="Station names: pcp1/tmp1/slr1/wnd1/hmd1  |  Rain 0.25 deg  |  Temp 1.0 deg",
                 font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, wraplength=400,
                 justify="left").grid(row=15, column=0, columnspan=3, sticky="w", pady=(14, 6))

        inner.columnconfigure(1, weight=1)

        # Action bar
        action = tk.Frame(left_outer, bg=BG_CARD, padx=20, pady=14)
        action.pack(fill="x", side="bottom")
        tk.Frame(action, bg=BORDER, height=1).pack(fill="x", pady=(0, 14))

        btn_row = tk.Frame(action, bg=BG_CARD)
        btn_row.pack(fill="x")
        self.run_button = ModernButton(btn_row, text="Start Download",
                                       command=self._start_run, accent=True, width=180, height=42)
        self.run_button.pack(side="left", padx=(0, 6))
        self.cancel_button = ModernButton(btn_row, text="Cancel",
                                          command=self._cancel_run, accent="danger", width=100, height=42)
        self.cancel_button.pack(side="left", padx=(0, 6))
        self.cancel_button.set_disabled(True)
        self.open_btn = ModernButton(btn_row, text="Open Output",
                                     command=self._open_output, width=120, height=42)
        self.open_btn.pack(side="left", padx=(0, 6))
        self.clear_btn = ModernButton(btn_row, text="Clear Log",
                                      command=self._clear_log, width=100, height=42)
        self.clear_btn.pack(side="left")

        # ── Right panel ──
        right = tk.Frame(body, bg=BG_CARD, bd=0)
        body.add(right, minsize=300)

        log_hdr = tk.Frame(right, bg=BG_CARD, padx=20, pady=14)
        log_hdr.pack(fill="x")
        tk.Label(log_hdr, text="Run Log", font=("Segoe UI Semibold", 13),
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(log_hdr, text="Progress from IMD, NASA POWER, DEM, Excel & report generation.",
                 font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        log_frame = tk.Frame(right, bg=LOG_BG)
        log_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.log_text = tk.Text(
            log_frame, wrap="word", font=("Consolas", 10),
            bg=LOG_BG, fg="#c8d0e0", insertbackground=ACCENT,
            relief="flat", bd=0, padx=14, pady=14,
            selectbackground=ACCENT, selectforeground="#ffffff",
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        log_sb = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview,
                              bg=SCROLLBAR, troughcolor=LOG_BG, width=10, relief="flat")
        log_sb.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=log_sb.set)

        # Tag styles for colored log output
        self.log_text.tag_configure("done", foreground=SUCCESS)
        self.log_text.tag_configure("error", foreground=ERROR)

        # ── Footer ──
        footer = tk.Frame(root, bg=BG_CARD, padx=14, pady=8)
        footer.pack(fill="x", pady=(12, 0))

        self.status_dot = tk.Canvas(footer, width=10, height=10, bg=BG_CARD, highlightthickness=0)
        self.status_dot.pack(side="left", padx=(0, 8))
        self._draw_dot(TEXT_MUTED)
        self.status_label = tk.Label(footer, textvariable=self.status_var,
                                     font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_SECONDARY)
        self.status_label.pack(side="left")

        self.progress = ttk.Progressbar(footer, mode="indeterminate", length=180)
        self.progress.pack(side="right")

        # Data size label (shown during download)
        self.data_label = tk.Label(footer, textvariable=self.data_var,
                                   font=("Consolas", 9), bg=BG_CARD, fg=ACCENT)
        self.data_label.pack(side="right", padx=(0, 14))

    def _draw_dot(self, color):
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 9, 9, fill=color, outline=color)

    def _section(self, parent, text, row):
        f = tk.Frame(parent, bg=BG_CARD)
        f.grid(row=row, column=0, columnspan=3, sticky="w", pady=(16, 8))
        tk.Label(f, text=text, font=("Segoe UI Semibold", 12), bg=BG_CARD, fg=ACCENT).pack(anchor="w")

    def _path_row(self, parent, row, label, key, command):
        tk.Label(parent, text=label, font=("Segoe UI", 10), bg=BG_CARD,
                 fg=TEXT_SECONDARY).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        me = ModernEntry(parent, textvariable=self.vars[key], width=32)
        me.grid(row=row, column=1, sticky="we", pady=5, padx=(0, 8))
        btn = tk.Button(parent, text="Browse", command=command,
                        bg=BG_INPUT, fg=TEXT_SECONDARY, activebackground=BG_INPUT_FOCUS,
                        activeforeground=TEXT_PRIMARY, relief="flat", bd=0,
                        font=("Segoe UI", 9), padx=10, pady=4, cursor="hand2")
        btn.grid(row=row, column=2, sticky="e", pady=5)
        btn.bind("<Enter>", lambda e: btn.configure(bg=BG_INPUT_FOCUS, fg=TEXT_PRIMARY))
        btn.bind("<Leave>", lambda e: btn.configure(bg=BG_INPUT, fg=TEXT_SECONDARY))

    def _number_row(self, parent, row, label, key):
        tk.Label(parent, text=label, font=("Segoe UI", 10), bg=BG_CARD,
                 fg=TEXT_SECONDARY).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        ModernEntry(parent, textvariable=self.vars[key], width=12).grid(
            row=row, column=1, sticky="w", pady=5)

    def _text_row(self, parent, row, label, key):
        tk.Label(parent, text=label, font=("Segoe UI", 10), bg=BG_CARD,
                 fg=TEXT_SECONDARY).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        ModernEntry(parent, textvariable=self.vars[key], width=28).grid(
            row=row, column=1, sticky="we", pady=5, padx=(0, 8))

    # ── File browsers ──

    def _browse_shapefile(self):
        path = filedialog.askopenfilename(
            title="Select watershed shapefile",
            filetypes=[("Shapefile", "*.shp"), ("All files", "*.*")])
        if path:
            self.vars["watershed"].set(path)

    def _browse_dem(self):
        path = filedialog.askopenfilename(
            title="Select DEM raster",
            filetypes=[("Raster files", "*.tif *.tiff"), ("All files", "*.*")])
        if path:
            self.vars["dem"].set(path)

    def _browse_folder(self, key):
        path = filedialog.askdirectory(title="Select folder")
        if path:
            self.vars[key].set(path)

    # ── Validation ──

    def _validate(self) -> tuple[bool, str]:
        watershed = self.vars["watershed"].get().strip()
        dem = self.vars["dem"].get().strip()
        output = self.vars["output"].get().strip()
        imd_raw = self.vars["imd_raw"].get().strip()
        area_name = self.vars["area_name"].get().strip()
        file_prefix = self.vars["file_prefix"].get().strip()

        if not watershed.lower().endswith(".shp") or not os.path.exists(watershed):
            return False, "Please select a valid watershed .shp file."
        if dem and not os.path.exists(dem):
            return False, "Please select a valid DEM file, or clear the DEM field if you want fallback bands."
        if not output:
            return False, "Please select an output folder."
        if not imd_raw:
            return False, "Please select an IMD raw data folder."
        if not area_name:
            return False, "Please enter the area name for the report."
        if "\n" in area_name or "\r" in area_name:
            return False, "Area name must be one line."
        if not file_prefix:
            return False, "Please enter an output file prefix."
        if any(ch in file_prefix for ch in r'<>:"/\|?*'):
            return False, r'Output file prefix cannot contain these characters: < > : " / \ | ? *'

        try:
            start_year = int(self.vars["start_year"].get())
            end_year = int(self.vars["end_year"].get())
            bands = int(self.vars["bands"].get())
            stations = int(self.vars["stations_per_band"].get())
            temp_lapse = float(self.vars["temp_lapse_rate"].get())
            precip_lapse = float(self.vars["precip_lapse_rate"].get())
        except ValueError:
            return False, "Years, bands, and stations must be whole numbers. Lapse rates must be numeric."

        if start_year < 1901 or end_year < start_year:
            return False, "Use a valid year range. End year must be >= start year."
        if bands < 1 or bands > 20:
            return False, "Elevation bands must be between 1 and 20."
        if stations < 1 or stations > 10:
            return False, "Stations per band must be between 1 and 10."
        if temp_lapse < -15.0 or temp_lapse > 5.0:
            return False, "Temperature lapse rate should be between -15 and 5 C / 1000 m."
        if precip_lapse < -100.0 or precip_lapse > 200.0:
            return False, "Precipitation lapse rate should be between -100 and 200 % / 100 m."
        return True, ""

    # ── Run logic ──

    def _start_run(self):
        valid, message = self._validate()
        if not valid:
            messagebox.showerror("Check settings", message)
            return

        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Run in progress", "A download is already running.")
            return

        self._clear_log()
        self._cancel_event.clear()
        self.status_var.set("Running...")
        self.data_var.set("")
        self._draw_dot(ACCENT)
        self.run_button.set_disabled(True)
        self.cancel_button.set_disabled(False)
        self.progress.start(12)

        config = {
            "shp_path": self.vars["watershed"].get().strip(),
            "dem_path": self.vars["dem"].get().strip(),
            "output_dir": self.vars["output"].get().strip(),
            "imd_raw_folder": self.vars["imd_raw"].get().strip(),
            "area_name": self.vars["area_name"].get().strip(),
            "output_file_prefix": self.vars["file_prefix"].get().strip(),
            "start_year": int(self.vars["start_year"].get()),
            "end_year": int(self.vars["end_year"].get()),
            "num_bands": int(self.vars["bands"].get()),
            "stations_per_band": int(self.vars["stations_per_band"].get()),
            "temp_lapse_rate": float(self.vars["temp_lapse_rate"].get()),
            "precip_lapse_rate": float(self.vars["precip_lapse_rate"].get()),
        }

        self.worker = threading.Thread(target=self._run_downloader, args=(config,), daemon=True)
        self.worker.start()
        self._track_output_size(config["output_dir"])

    def _cancel_run(self):
        """Signal the worker to stop and update the UI."""
        if self.worker and self.worker.is_alive():
            self._cancel_event.set()
            self.log_queue.put("\n--- Cancellation requested. Waiting for current step to finish... ---\n")
            self.status_var.set("Cancelling...")
            self._draw_dot(WARN)
            self.cancel_button.set_disabled(True)

    def _run_downloader(self, config: dict) -> None:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        writer = QueueWriter(self.log_queue)
        sys.stdout = writer
        sys.stderr = writer
        cancel = self._cancel_event

        try:
            if cancel.is_set():
                raise InterruptedError("Cancelled before start.")

            print("Starting SWAT weather data workflow...\n")
            import swat_complete_data_downloader_real as downloader_module

            temp_lapse_rate = config.pop("temp_lapse_rate")
            precip_lapse_rate = config.pop("precip_lapse_rate")
            downloader_module.TEMP_LAPSE_RATE = temp_lapse_rate
            downloader_module.PRECIP_LAPSE_RATE = precip_lapse_rate

            print(f"Temperature lapse rate : {temp_lapse_rate} C / 1000 m")
            print(f"Precipitation lapse rate: {precip_lapse_rate} % / 100 m\n")
            try:
                print(f"IMD rainfall grid (deg): {downloader_module.IMD_RAINFALL_RES}")
                print(f"IMD temperature grid (deg): {downloader_module.IMD_TEMP_RES}\n")
                print("Note: Rainfall uses 0.25 deg IMD grid; temperature uses 1.0 deg IMD grid.\n")
            except Exception:
                pass

            if cancel.is_set():
                raise InterruptedError("Cancelled.")

            downloader = downloader_module.SWATDataDownloaderReal(**config)

            # --- Monkey-patch run_all to check cancel between steps ---
            def cancellable_run_all():
                import time as _time
                t0 = _time.time()

                if cancel.is_set():
                    raise InterruptedError("Cancelled.")
                downloader.generate_stations()

                if cancel.is_set():
                    raise InterruptedError("Cancelled.")
                if downloader.download_watershed_weather():
                    if cancel.is_set():
                        raise InterruptedError("Cancelled.")
                    downloader.generate_station_weather()
                    if cancel.is_set():
                        raise InterruptedError("Cancelled.")
                    downloader.create_excel()

                if cancel.is_set():
                    raise InterruptedError("Cancelled.")
                downloader.create_report()
                elapsed = _time.time() - t0
                downloader_module.line("WEATHER DATA DOWNLOAD COMPLETE")
                print(f"  Time: {elapsed / 60.0:.1f} min")
                print(f"  Output: {downloader.output_dir}")

            # --- Patch IMD download loops to check cancel per year ---
            orig_download_rainfall = downloader.imd_downloader.download_rainfall
            orig_download_temperature = downloader.imd_downloader.download_temperature

            def patched_download_rainfall():
                downloader_module.line("[AREA-WEIGHTED] DOWNLOADING IMD RAINFALL DATA")
                imd_dl = downloader.imd_downloader
                for idx, cell in enumerate(imd_dl.rainfall_cells):
                    if cancel.is_set():
                        raise InterruptedError("Cancelled during rainfall download.")
                    print(f"\n  Cell {idx + 1}/{len(imd_dl.rainfall_cells)}: ({cell.lat:.2f}, {cell.lon:.2f}) weight={cell.weight:.3f}")
                    centre_lat = cell.lat + cell.resolution / 2.0
                    centre_lon = cell.lon + cell.resolution / 2.0
                    chunks = []
                    for year in range(imd_dl.start_year, imd_dl.end_year + 1):
                        if cancel.is_set():
                            raise InterruptedError("Cancelled during rainfall download.")
                        print(f"    Year {year}: requesting IMD rain dataset ... Downloading: rain for year {year}")
                        try:
                            rain_ds = imd_dl._load_imd_xarray("rain", year)
                            print("    Download Successful !!!")
                            print("    OK")
                            pt = rain_ds.sel(lat=centre_lat, lon=centre_lon, method="nearest")
                            df_year = pt["rain"].to_dataframe(name="precip_mm").reset_index()
                            df_year = downloader_module.ensure_datetime_column(df_year, "time")
                            df_year = df_year[df_year["time"].dt.year == year]
                            df_year["precip_mm"] = df_year["precip_mm"].replace(-999.0, 0.0).clip(lower=0.0)
                            chunks.append(df_year[["time", "precip_mm"]])
                            print(f"      extracted {len(df_year)} days @ ({centre_lat:.3f},{centre_lon:.3f})")
                        except InterruptedError:
                            raise
                        except Exception as exc:
                            print("FAILED")
                            downloader_module.fail(f"{year}: {str(exc)[:120]}")
                    if chunks:
                        cell.data = pd.concat(chunks, ignore_index=True).sort_values("time")
                        annual_avg = cell.data["precip_mm"].sum() / max(1, imd_dl.end_year - imd_dl.start_year + 1)
                        downloader_module.ok(f"{len(cell.data)} days; annual mean = {annual_avg:.1f} mm")
                    else:
                        cell.data = pd.DataFrame(columns=["time", "precip_mm"])

            def patched_download_temperature():
                downloader_module.line("[AREA-WEIGHTED] DOWNLOADING IMD TEMPERATURE DATA")
                imd_dl = downloader.imd_downloader
                if not imd_dl.temp_cells:
                    print("  No temperature cells found. Skipping.")
                    return
                for idx, cell in enumerate(imd_dl.temp_cells):
                    if cancel.is_set():
                        raise InterruptedError("Cancelled during temperature download.")
                    print(f"\n  Cell {idx + 1}/{len(imd_dl.temp_cells)}: ({cell.lat:.2f}, {cell.lon:.2f}) weight={cell.weight:.3f}")
                    centre_lat = cell.lat + cell.resolution / 2.0
                    centre_lon = cell.lon + cell.resolution / 2.0
                    chunks = []
                    for year in range(imd_dl.start_year, imd_dl.end_year + 1):
                        if cancel.is_set():
                            raise InterruptedError("Cancelled during temperature download.")
                        print(f"    Year {year}: requesting IMD tmax/tmin ... Downloading: temperature for year {year}")
                        try:
                            tmax_ds = imd_dl._load_imd_xarray("tmax", year)
                            tmin_ds = imd_dl._load_imd_xarray("tmin", year)
                            print("    Download Successful !!!")
                            print("    OK")
                            df_tmax = (
                                tmax_ds.sel(lat=centre_lat, lon=centre_lon, method="nearest")["tmax"]
                                .to_dataframe(name="tmax_c").reset_index()
                            )
                            df_tmin = (
                                tmin_ds.sel(lat=centre_lat, lon=centre_lon, method="nearest")["tmin"]
                                .to_dataframe(name="tmin_c").reset_index()
                            )
                            df_tmax = downloader_module.ensure_datetime_column(df_tmax, "time")
                            df_tmin = downloader_module.ensure_datetime_column(df_tmin, "time")
                            df_tmax = df_tmax[df_tmax["time"].dt.year == year]
                            df_tmin = df_tmin[df_tmin["time"].dt.year == year]
                            df_tmax["tmax_c"] = df_tmax["tmax_c"].replace(-999.0, np.nan)
                            df_tmin["tmin_c"] = df_tmin["tmin_c"].replace(-999.0, np.nan)
                            chunks.append(df_tmax[["time", "tmax_c"]].merge(df_tmin[["time", "tmin_c"]], on="time", how="left"))
                            print(f"      extracted {len(df_tmax)} days @ ({centre_lat:.3f},{centre_lon:.3f})")
                        except InterruptedError:
                            raise
                        except Exception as exc:
                            print("FAILED")
                            downloader_module.fail(f"{year}: {str(exc)[:120]}")
                    if chunks:
                        df = pd.concat(chunks, ignore_index=True).sort_values("time")
                        df["tmax_c"] = df["tmax_c"].interpolate().ffill().bfill()
                        df["tmin_c"] = df["tmin_c"].interpolate().ffill().bfill()
                        cell.data = df
                        downloader_module.ok(f"{len(df)} days")
                    else:
                        cell.data = pd.DataFrame(columns=["time", "tmax_c", "tmin_c"])
                    print(f"  Finished temperature cell {idx + 1}/{len(imd_dl.temp_cells)}")

            # Apply patches
            downloader.imd_downloader.download_rainfall = patched_download_rainfall
            downloader.imd_downloader.download_temperature = patched_download_temperature

            cancellable_run_all()

            print("\nDONE")
            print(f"Weather files : {downloader.dirs['swat']}")
            print(f"Excel workbook: {downloader.dirs['excel']}")
            print(f"Report        : {downloader.dirs['reports']}")
            self.log_queue.put("__STATUS__:Complete")
        except InterruptedError:
            print("\nCANCELLED by user.")
            self.log_queue.put("__STATUS__:Cancelled")
        except Exception:
            if cancel.is_set():
                print("\nCANCELLED by user.")
                self.log_queue.put("__STATUS__:Cancelled")
            else:
                print("\nERROR")
                print(traceback.format_exc())
                self.log_queue.put("__STATUS__:Failed")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.log_queue.put("__FINISHED__")

    def _get_folder_size_mb(self, path: str) -> float:
        """Return total size of all files under *path* in megabytes."""
        total = 0
        try:
            for dirpath, _dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except OSError:
                        pass
        except OSError:
            pass
        return total / (1024 * 1024)

    def _track_output_size(self, output_dir: str) -> None:
        """Periodically update the data size label while running.

        Tracks both the IMD raw data folder (where imdlib downloads binary
        files) and the output folder for a combined total.
        """
        if self.worker and self.worker.is_alive():
            imd_folder = self.vars["imd_raw"].get().strip()
            mb = self._get_folder_size_mb(output_dir)
            if imd_folder and os.path.isdir(imd_folder):
                mb += self._get_folder_size_mb(imd_folder)
            if mb < 1.0:
                self.data_var.set(f"Downloaded: {mb * 1024:.0f} KB")
            elif mb < 1024.0:
                self.data_var.set(f"Downloaded: {mb:.1f} MB")
            else:
                self.data_var.set(f"Downloaded: {mb / 1024:.2f} GB")
            self.after(1000, lambda: self._track_output_size(output_dir))

    def _drain_log_queue(self) -> None:
        try:
            while True:
                item = self.log_queue.get_nowait()
                if item == "__FINISHED__":
                    self.progress.stop()
                    self.run_button.set_disabled(False)
                    self.cancel_button.set_disabled(True)
                    if self.status_var.get() in ("Running...", "Cancelling..."):
                        self.status_var.set("Finished")
                    continue
                if item.startswith("__STATUS__:"):
                    state = item.split(":", 1)[1]
                    self.status_var.set(state)
                    if state == "Complete":
                        self._draw_dot(SUCCESS)
                        messagebox.showinfo("Complete", "SWAT weather data generation finished.")
                    elif state == "Cancelled":
                        self._draw_dot(WARN)
                        messagebox.showinfo("Cancelled", "The download was cancelled.")
                    elif state == "Failed":
                        self._draw_dot(ERROR)
                        messagebox.showerror("Failed", "The run failed. Check the log for details.")
                    continue
                # Color DONE/ERROR lines
                tag = None
                if "DONE" in item:
                    tag = "done"
                elif "ERROR" in item:
                    tag = "error"
                self.log_text.insert("end", item, tag)
                self.log_text.see("end")
        except queue.Empty:
            pass
        self.after(100, self._drain_log_queue)

    def _clear_log(self):
        self.log_text.delete("1.0", "end")
        self.status_var.set("Ready")
        self._draw_dot(TEXT_MUTED)

    def _open_output(self):
        path = self.vars["output"].get().strip()
        if not path:
            messagebox.showinfo("Output folder", "Select an output folder first.")
            return
        os.makedirs(path, exist_ok=True)
        try:
            os.startfile(path)
        except Exception as exc:
            messagebox.showerror("Open output", f"Could not open folder:\n{exc}")


def main() -> None:
    app = SWATWeatherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
