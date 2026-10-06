#!/usr/bin/env python3
"""
System Performance Analyzer - macOS Optimized
Team: Architechs (SE(OS)-VI-T250)
Created for macOS 13-inch screen optimization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import platform
import subprocess
import threading
import time
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from collections import deque

class SplashScreen:
    """Beautiful splash screen with team branding"""
    def __init__(self, root):
        self.root = root
        self.splash = tk.Toplevel(root)
        self.splash.title("System Performance Analyzer")
        self.splash.geometry("500x300")
        self.splash.configure(bg="#1a1a2e")
        self.splash.resizable(False, False)
        
        # Center the splash screen
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.splash.winfo_screenheight() // 2) - (300 // 2)
        self.splash.geometry(f"500x300+{x}+{y}")
        
        # Remove window decorations
        self.splash.overrideredirect(True)
        
        # Make sure this window stays on top
        self.splash.attributes("-topmost", True)
        
        # Main frame with gradient effect
        main_frame = tk.Frame(self.splash, bg="#1a1a2e")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # App title with gradient colors
        title_label = tk.Label(main_frame, text="System Performance", 
                              font=("SF Pro Display", 24, "bold"),
                              fg="#ff6b6b", bg="#1a1a2e")
        title_label.pack(pady=(40, 5))
        
        title_label2 = tk.Label(main_frame, text="ANALYZER", 
                               font=("SF Pro Display", 28, "bold"),
                               fg="#4ecdc4", bg="#1a1a2e")
        title_label2.pack(pady=(0, 20))
        
        # Team info
        team_frame = tk.Frame(main_frame, bg="#1a1a2e")
        team_frame.pack(pady=20)
        
        tk.Label(team_frame, text="Team: Architechs", 
                font=("SF Pro Display", 14, "bold"),
                fg="#ffe66d", bg="#1a1a2e").pack()
        
        tk.Label(team_frame, text="Team ID: SE(OS)-VI-T250", 
                font=("SF Pro Display", 12),
                fg="#a8e6cf", bg="#1a1a2e").pack(pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                     maximum=100, length=300)
        progress_bar.pack(pady=20)
        
        # Loading text
        self.loading_label = tk.Label(main_frame, text="Initializing...", 
                                     font=("SF Pro Display", 12),
                                     fg="#ffffff", bg="#1a1a2e")
        self.loading_label.pack()
        
        # Start loading animation with the event-driven approach
        self.steps = ["Initializing...", "Loading system modules...", 
                     "Checking permissions...", "Starting monitors...", "Ready!"]
        self.current_step = 0
        # Schedule the first animation step
        self.splash.after(100, self.animate_step)
    
    def animate_step(self):
        """Perform a single animation step"""
        if self.current_step < len(self.steps):
            # Update label and progress bar
            self.loading_label.config(text=self.steps[self.current_step])
            self.progress_var.set((self.current_step + 1) * 20)
            
            # Increment step counter
            self.current_step += 1
            
            # Schedule next step
            self.splash.after(800, self.animate_step)
        else:
            # Animation complete, close splash window
            self.splash.destroy()
                    
class SystemAnalyzer:
    """Main System Performance Analyzer Application"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_styles()
        self.create_menu()
        self.create_ui()
        self.start_monitoring()
        
        # Theme tracking
        self.dark_mode = True
        
    def setup_window(self):
        """Configure main window for macOS 13-inch screen"""
        self.root.title("System Performance Analyzer - Architechs")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
        
        # macOS-style window
        self.root.configure(bg="#1a1a2e")
        
    def setup_variables(self):
        """Initialize monitoring variables"""
        self.cpu_history = deque(maxlen=60)  # Last 60 readings
        self.memory_history = deque(maxlen=60)
        self.monitoring = False
        self.process_list = []
        self.cpu_threshold = 80
        self.memory_threshold = 85
        
    def setup_styles(self):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook tabs
        style.configure('Custom.TNotebook.Tab', 
                       padding=[20, 10],
                       font=('SF Pro Display', 11, 'bold'))
        
        # Configure frames
        style.configure('Card.TFrame', 
                       background='#16213e',
                       relief='flat')
        
        # Configure labels
        style.configure('Title.TLabel',
                       font=('SF Pro Display', 16, 'bold'),
                       background='#16213e',
                       foreground='#ffffff')
        
        style.configure('Info.TLabel',
                       font=('SF Pro Display', 12),
                       background='#16213e',
                       foreground='#a8e6cf')
        
    def create_menu(self):
        """Create modern menu bar"""
        menubar = tk.Menu(self.root, bg="#1a1a2e", fg="white")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2c2c54", fg="white")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Report", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#2c2c54", fg="white")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_command(label="Refresh", command=self.refresh_data)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg="#2c2c54", fg="white")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Process Manager", command=self.open_process_manager)
        tools_menu.add_command(label="Settings", command=self.open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#2c2c54", fg="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Team", command=self.show_about)
        
    def create_ui(self):
        """Create main user interface"""
        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a2e")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with system info
        self.create_header(main_container)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_container, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create tabs
        self.create_overview_tab()
        self.create_cpu_tab()
        self.create_memory_tab()
        self.create_disk_tab()
        self.create_network_tab()
        self.create_processes_tab()
        
        # Footer
        self.create_footer(main_container)
        
    def create_header(self, parent):
        """Create header with system information"""
        header_frame = tk.Frame(parent, bg="#16213e", relief="raised", bd=1)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # System info grid
        info_frame = tk.Frame(header_frame, bg="#16213e")
        info_frame.pack(fill="x", padx=20, pady=15)
        
        # Left side - System info
        left_info = tk.Frame(info_frame, bg="#16213e")
        left_info.pack(side="left", fill="x", expand=True)
        
        system_info = self.get_system_info()
        
        tk.Label(left_info, text=f"System: {system_info['system']}", 
                font=("SF Pro Display", 12, "bold"),
                fg="#4ecdc4", bg="#16213e").pack(anchor="w")
        
        tk.Label(left_info, text=f"Processor: {system_info['processor']}", 
                font=("SF Pro Display", 10),
                fg="#a8e6cf", bg="#16213e").pack(anchor="w")
        
        # Right side - Real-time indicators
        right_info = tk.Frame(info_frame, bg="#16213e")
        right_info.pack(side="right")
        
        # Status indicator
        self.status_indicator = tk.Label(right_info, text="● MONITORING", 
                                        font=("SF Pro Display", 12, "bold"),
                                        fg="#ff6b6b", bg="#16213e")
        self.status_indicator.pack()
        
        # Last update time
        self.last_update_label = tk.Label(right_info, text="", 
                                         font=("SF Pro Display", 10),
                                         fg="#ffe66d", bg="#16213e")
        self.last_update_label.pack()
        
    def create_overview_tab(self):
        """Create overview tab with key metrics"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📊 Overview")
        
        # Configure frame background
        tab_frame.configure(style='Card.TFrame')
        
        # Create 2x2 grid for overview cards
        overview_container = tk.Frame(tab_frame, bg="#1a1a2e")
        overview_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # CPU Overview Card
        self.cpu_card = self.create_metric_card(overview_container, "CPU Usage", "#ff6b6b")
        self.cpu_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Memory Overview Card
        self.memory_card = self.create_metric_card(overview_container, "Memory Usage", "#4ecdc4")
        self.memory_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Disk Overview Card
        self.disk_card = self.create_metric_card(overview_container, "Disk Usage", "#ffe66d")
        self.disk_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Network Overview Card
        self.network_card = self.create_metric_card(overview_container, "Network Activity", "#a8e6cf")
        self.network_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        overview_container.grid_columnconfigure(0, weight=1)
        overview_container.grid_columnconfigure(1, weight=1)
        overview_container.grid_rowconfigure(0, weight=1)
        overview_container.grid_rowconfigure(1, weight=1)
        
    def create_metric_card(self, parent, title, color):
        """Create a metric card widget"""
        card_frame = tk.Frame(parent, bg="#16213e", relief="raised", bd=1)
        
        # Title
        title_label = tk.Label(card_frame, text=title, 
                              font=("SF Pro Display", 14, "bold"),
                              fg=color, bg="#16213e")
        title_label.pack(pady=(15, 5))
        
        # Value
        value_label = tk.Label(card_frame, text="0%", 
                              font=("SF Pro Display", 24, "bold"),
                              fg="white", bg="#16213e")
        value_label.pack()
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(card_frame, variable=progress_var,
                                     maximum=100, length=200)
        progress_bar.pack(pady=10)
        
        # Additional info
        info_label = tk.Label(card_frame, text="", 
                             font=("SF Pro Display", 10),
                             fg="#a8e6cf", bg="#16213e")
        info_label.pack(pady=(0, 15))
        
        # Store references
        card_frame.value_label = value_label
        card_frame.progress_var = progress_var
        card_frame.info_label = info_label
        
        return card_frame
        
    def create_cpu_tab(self):
        """Create CPU monitoring tab with graphs"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🖥️ CPU")
        
        # Create matplotlib figure
        self.cpu_fig = Figure(figsize=(10, 6), facecolor='#16213e')
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_ax.set_facecolor('#1a1a2e')
        
        # Configure plot appearance
        self.cpu_ax.set_title('CPU Usage History', color='white', size=14, weight='bold')
        self.cpu_ax.set_xlabel('Time (seconds ago)', color='white')
        self.cpu_ax.set_ylabel('Usage (%)', color='white')
        self.cpu_ax.tick_params(colors='white')
        self.cpu_ax.grid(True, alpha=0.3)
        
        # Create canvas
        cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, tab_frame)
        cpu_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # CPU info frame
        cpu_info_frame = tk.Frame(tab_frame, bg="#16213e")
        cpu_info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.cpu_cores_label = tk.Label(cpu_info_frame, text="", 
                                       font=("SF Pro Display", 12),
                                       fg="#4ecdc4", bg="#16213e")
        self.cpu_cores_label.pack(side="left", padx=10)
        
        self.cpu_freq_label = tk.Label(cpu_info_frame, text="", 
                                      font=("SF Pro Display", 12),
                                      fg="#ffe66d", bg="#16213e")
        self.cpu_freq_label.pack(side="right", padx=10)
        
    def create_memory_tab(self):
        """Create memory monitoring tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="💾 Memory")
        
        # Memory chart
        self.memory_fig = Figure(figsize=(10, 6), facecolor='#16213e')
        self.memory_ax = self.memory_fig.add_subplot(111)
        self.memory_ax.set_facecolor('#1a1a2e')
        
        self.memory_ax.set_title('Memory Usage History', color='white', size=14, weight='bold')
        self.memory_ax.set_xlabel('Time (seconds ago)', color='white')
        self.memory_ax.set_ylabel('Usage (%)', color='white')
        self.memory_ax.tick_params(colors='white')
        self.memory_ax.grid(True, alpha=0.3)
        
        memory_canvas = FigureCanvasTkAgg(self.memory_fig, tab_frame)
        memory_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Memory details
        memory_details_frame = tk.Frame(tab_frame, bg="#16213e")
        memory_details_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.memory_total_label = tk.Label(memory_details_frame, text="", 
                                          font=("SF Pro Display", 12),
                                          fg="#4ecdc4", bg="#16213e")
        self.memory_total_label.pack(side="left", padx=10)
        
        self.memory_available_label = tk.Label(memory_details_frame, text="", 
                                              font=("SF Pro Display", 12),
                                              fg="#a8e6cf", bg="#16213e")
        self.memory_available_label.pack(side="right", padx=10)
        
    def create_disk_tab(self):
        """Create disk monitoring tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="💽 Disk")
        
        # Disk usage frame
        disk_frame = tk.Frame(tab_frame, bg="#1a1a2e")
        disk_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create disk usage display
        self.create_disk_display(disk_frame)
        
    def create_network_tab(self):
        """Create network monitoring tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🌐 Network")
        
        # Network stats frame
        network_frame = tk.Frame(tab_frame, bg="#1a1a2e")
        network_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create network display
        self.create_network_display(network_frame)
        
    def create_processes_tab(self):
        """Create process monitoring tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="⚙️ Processes")
        
        # Process list frame
        process_frame = tk.Frame(tab_frame, bg="#1a1a2e")
        process_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create process viewer
        self.create_process_viewer(process_frame)
        
    def create_footer(self, parent):
        """Create footer with team credits"""
        footer_frame = tk.Frame(parent, bg="#16213e", relief="raised", bd=1)
        footer_frame.pack(fill="x")
        
        # Team credits
        credits_frame = tk.Frame(footer_frame, bg="#16213e")
        credits_frame.pack(side="left", padx=20, pady=10)
        
        tk.Label(credits_frame, text="© 2024 Team Architechs | SE(OS)-VI-T250", 
                font=("SF Pro Display", 10),
                fg="#a8e6cf", bg="#16213e").pack()
        
        # Status frame
        status_frame = tk.Frame(footer_frame, bg="#16213e")
        status_frame.pack(side="right", padx=20, pady=10)
        
        self.footer_status = tk.Label(status_frame, text="System monitoring active", 
                                     font=("SF Pro Display", 10),
                                     fg="#4ecdc4", bg="#16213e")
        self.footer_status.pack()
        
    def create_disk_display(self, parent):
        """Create disk usage visualization"""
        # Title
        title_label = tk.Label(parent, text="Disk Usage by Drive", 
                              font=("SF Pro Display", 16, "bold"),
                              fg="#ffe66d", bg="#1a1a2e")
        title_label.pack(pady=10)
        
        # Disk info frame
        self.disk_info_frame = tk.Frame(parent, bg="#1a1a2e")
        self.disk_info_frame.pack(fill="both", expand=True)
        
    def create_network_display(self, parent):
        """Create network usage visualization"""
        # Title
        title_label = tk.Label(parent, text="Network Activity", 
                              font=("SF Pro Display", 16, "bold"),
                              fg="#a8e6cf", bg="#1a1a2e")
        title_label.pack(pady=10)
        
        # Network stats frame
        self.network_stats_frame = tk.Frame(parent, bg="#1a1a2e")
        self.network_stats_frame.pack(fill="both", expand=True)
        
        # Create network stats labels
        self.network_sent_label = tk.Label(self.network_stats_frame, text="", 
                                          font=("SF Pro Display", 14),
                                          fg="#4ecdc4", bg="#1a1a2e")
        self.network_sent_label.pack(pady=5)
        
        self.network_recv_label = tk.Label(self.network_stats_frame, text="", 
                                          font=("SF Pro Display", 14),
                                          fg="#ff6b6b", bg="#1a1a2e")
        self.network_recv_label.pack(pady=5)
        
    def create_process_viewer(self, parent):
        """Create process list viewer"""
        # Control frame
        control_frame = tk.Frame(parent, bg="#1a1a2e")
        control_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(control_frame, text="Running Processes", 
                font=("SF Pro Display", 16, "bold"),
                fg="#ff6b6b", bg="#1a1a2e").pack(side="left")
        
        refresh_btn = tk.Button(control_frame, text="Refresh", 
                               command=self.refresh_processes,
                               bg="#4ecdc4", fg="white",
                               font=("SF Pro Display", 11, "bold"),
                               relief="flat", padx=20)
        refresh_btn.pack(side="right")
        
        # Process tree
        tree_frame = tk.Frame(parent, bg="#1a1a2e")
        tree_frame.pack(fill="both", expand=True)
        
        # Create treeview
        columns = ('PID', 'Name', 'CPU%', 'Memory%', 'Status')
        self.process_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=120, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", 
                                   command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", 
                                   command=self.process_tree.xview)
        self.process_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.process_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu for processes
        self.create_process_context_menu()
        
    def create_process_context_menu(self):
        """Create context menu for process management"""
        self.process_menu = tk.Menu(self.root, tearoff=0, bg="#2c2c54", fg="white")
        self.process_menu.add_command(label="Terminate Process", 
                                     command=self.terminate_process)
        self.process_menu.add_command(label="Process Details", 
                                     command=self.show_process_details)
        
        self.process_tree.bind("<Button-3>", self.show_process_menu)
        
    def show_process_menu(self, event):
        """Show process context menu"""
        try:
            self.process_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.process_menu.grab_release()
            
    def terminate_process(self):
        """Terminate selected process"""
        selection = self.process_tree.selection()
        if not selection:
            return
            
        item = self.process_tree.item(selection[0])
        pid = int(item['values'][0])
        process_name = item['values'][1]
        
        if messagebox.askyesno("Terminate Process", 
                              f"Are you sure you want to terminate '{process_name}' (PID: {pid})?"):
            try:
                process = psutil.Process(pid)
                process.terminate()
                messagebox.showinfo("Success", f"Process '{process_name}' terminated successfully.")
                self.refresh_processes()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to terminate process: {str(e)}")
                
    def show_process_details(self):
        """Show detailed process information"""
        selection = self.process_tree.selection()
        if not selection:
            return
            
        item = self.process_tree.item(selection[0])
        pid = int(item['values'][0])
        
        try:
            process = psutil.Process(pid)
            details = f"""Process Details:
            
PID: {process.pid}
Name: {process.name()}
Status: {process.status()}
CPU%: {process.cpu_percent()}%
Memory%: {process.memory_percent():.2f}%
Memory Info: {process.memory_info().rss / 1024 / 1024:.2f} MB
Create Time: {datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}
Command Line: {' '.join(process.cmdline()) if process.cmdline() else 'N/A'}
"""
            messagebox.showinfo("Process Details", details)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot get process details: {str(e)}")
            
    def get_system_info(self):
        """Get basic system information"""
        return {
            'system': f"{platform.system()} {platform.release()}",
            'processor': platform.processor(),
            'machine': platform.machine(),
            'architecture': platform.architecture()[0]
        }
        
    def start_monitoring(self):
        """Start system monitoring thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()
        
    def monitor_system(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Update history
                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory.percent)
                
                # Update UI in main thread
                self.root.after(0, self.update_ui, cpu_percent, memory)
                
                # Check thresholds
                self.check_thresholds(cpu_percent, memory.percent)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                
            time.sleep(1)
            
    def update_ui(self, cpu_percent, memory):
        """Update UI with current metrics"""
        try:
            # Update overview cards
            self.update_overview_cards(cpu_percent, memory)
            
            # Update graphs
            self.update_cpu_graph()
            self.update_memory_graph()
            
            # Update detailed tabs
            self.update_cpu_details()
            self.update_memory_details(memory)
            self.update_disk_details()
            self.update_network_details()
            
            # Update status
            self.last_update_label.config(text=f"Last update: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"UI update error: {e}")
            
    def update_overview_cards(self, cpu_percent, memory):
        """Update overview cards with current metrics"""
        # CPU card
        self.cpu_card.value_label.config(text=f"{cpu_percent:.1f}%")
        self.cpu_card.progress_var.set(cpu_percent)
        self.cpu_card.info_label.config(text=f"Cores: {psutil.cpu_count()}")
        
        # Memory card
        self.memory_card.value_label.config(text=f"{memory.percent:.1f}%")
        self.memory_card.progress_var.set(memory.percent)
        self.memory_card.info_label.config(text=f"Available: {memory.available / 1024**3:.1f} GB")
        
        # Disk card
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.disk_card.value_label.config(text=f"{disk_percent:.1f}%")
        self.disk_card.progress_var.set(disk_percent)
        self.disk_card.info_label.config(text=f"Free: {disk.free / 1024**3:.1f} GB")
        
        # Network card
        net_io = psutil.net_io_counters()
        self.network_card.value_label.config(text="Active")
        self.network_card.progress_var.set(50)  # Placeholder for network activity
        self.network_card.info_label.config(text=f"Sent: {net_io.bytes_sent / 1024**2:.1f} MB")
        
    def update_cpu_graph(self):
        """Update CPU usage graph"""
        if len(self.cpu_history) < 2:
            return
            
        self.cpu_ax.clear()
        
        # Configure plot
        self.cpu_ax.set_facecolor('#1a1a2e')
        self.cpu_ax.set_title('CPU Usage History', color='white', size=14, weight='bold')
        self.cpu_ax.set_xlabel('Time (seconds ago)', color='white')
        self.cpu_ax.set_ylabel('Usage (%)', color='white')
        self.cpu_ax.tick_params(colors='white')
        self.cpu_ax.grid(True, alpha=0.3)
        
        # Plot data
        x_data = list(range(len(self.cpu_history)-1, -1, -1))
        self.cpu_ax.plot(x_data, list(self.cpu_history), color='#ff6b6b', linewidth=2)
        self.cpu_ax.fill_between(x_data, list(self.cpu_history), alpha=0.3, color='#ff6b6b')
        
        # Set limits
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.set_xlim(0, 60)
        
        self.cpu_fig.tight_layout()
        self.cpu_fig.canvas.draw()
        
    def update_memory_graph(self):
        """Update memory usage graph"""
        if len(self.memory_history) < 2:
            return
            
        self.memory_ax.clear()
        
        # Configure plot
        self.memory_ax.set_facecolor('#1a1a2e')
        self.memory_ax.set_title('Memory Usage History', color='white', size=14, weight='bold')
        self.memory_ax.set_xlabel('Time (seconds ago)', color='white')
        self.memory_ax.set_ylabel('Usage (%)', color='white')
        self.memory_ax.tick_params(colors='white')
        self.memory_ax.grid(True, alpha=0.3)
        
        # Plot data
        x_data = list(range(len(self.memory_history)-1, -1, -1))
        self.memory_ax.plot(x_data, list(self.memory_history), color='#4ecdc4', linewidth=2)
        self.memory_ax.fill_between(x_data, list(self.memory_history), alpha=0.3, color='#4ecdc4')
        
        # Set limits
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.set_xlim(0, 60)
        
        self.memory_fig.tight_layout()
        self.memory_fig.canvas.draw()
        
    def update_cpu_details(self):
        """Update CPU detailed information"""
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            
            self.cpu_cores_label.config(
                text=f"Cores: {cpu_count_physical} physical, {cpu_count_logical} logical")
            
            if cpu_freq:
                self.cpu_freq_label.config(
                    text=f"Frequency: {cpu_freq.current:.2f} MHz")
            else:
                self.cpu_freq_label.config(text="Frequency: N/A")
        except:
            pass
            
    def update_memory_details(self, memory):
        """Update memory detailed information"""
        try:
            self.memory_total_label.config(
                text=f"Total: {memory.total / 1024**3:.2f} GB | Used: {memory.used / 1024**3:.2f} GB")
            self.memory_available_label.config(
                text=f"Available: {memory.available / 1024**3:.2f} GB | Cached: {memory.cached / 1024**3:.2f} GB")
        except:
            pass
            
    def update_disk_details(self):
        """Update disk usage details"""
        try:
            # Clear existing widgets
            for widget in self.disk_info_frame.winfo_children():
                widget.destroy()
                
            # Get disk information for all mounted drives
            partitions = psutil.disk_partitions()
            
            for i, partition in enumerate(partitions):
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Create disk card
                    disk_card = tk.Frame(self.disk_info_frame, bg="#16213e", relief="raised", bd=1)
                    disk_card.pack(fill="x", padx=10, pady=5)
                    
                    # Disk info
                    info_frame = tk.Frame(disk_card, bg="#16213e")
                    info_frame.pack(fill="x", padx=15, pady=10)
                    
                    # Disk name and mount point
                    tk.Label(info_frame, 
                            text=f"Drive: {partition.device} ({partition.mountpoint})",
                            font=("SF Pro Display", 12, "bold"),
                            fg="#ffe66d", bg="#16213e").pack(anchor="w")
                    
                    # Usage information
                    total_gb = disk_usage.total / 1024**3
                    used_gb = disk_usage.used / 1024**3
                    free_gb = disk_usage.free / 1024**3
                    percent_used = (disk_usage.used / disk_usage.total) * 100
                    
                    usage_text = f"Used: {used_gb:.2f} GB | Free: {free_gb:.2f} GB | Total: {total_gb:.2f} GB"
                    tk.Label(info_frame, text=usage_text,
                            font=("SF Pro Display", 10),
                            fg="#a8e6cf", bg="#16213e").pack(anchor="w")
                    
                    # Progress bar
                    progress_frame = tk.Frame(info_frame, bg="#16213e")
                    progress_frame.pack(fill="x", pady=(5, 0))
                    
                    progress_var = tk.DoubleVar()
                    progress_var.set(percent_used)
                    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var,
                                                 maximum=100, length=300)
                    progress_bar.pack(side="left")
                    
                    tk.Label(progress_frame, text=f"{percent_used:.1f}%",
                            font=("SF Pro Display", 10, "bold"),
                            fg="#ff6b6b" if percent_used > 80 else "#4ecdc4", 
                            bg="#16213e").pack(side="right", padx=(10, 0))
                    
                except PermissionError:
                    continue
        except:
            pass
            
    def update_network_details(self):
        """Update network usage details"""
        try:
            net_io = psutil.net_io_counters()
            
            # Calculate rates (simplified)
            sent_mb = net_io.bytes_sent / 1024**2
            recv_mb = net_io.bytes_recv / 1024**2
            
            self.network_sent_label.config(
                text=f"📤 Total Sent: {sent_mb:.2f} MB | Packets: {net_io.packets_sent:,}")
            self.network_recv_label.config(
                text=f"📥 Total Received: {recv_mb:.2f} MB | Packets: {net_io.packets_recv:,}")
            
        except:
            pass
            
    def refresh_processes(self):
        """Refresh process list"""
        try:
            # Clear existing items
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
                
            # Get process list
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            # Add to tree (limit to top 50 for performance)
            for proc in processes[:50]:
                self.process_tree.insert('', 'end', values=(
                    proc['pid'],
                    proc['name'][:30],  # Truncate long names
                    f"{proc['cpu_percent'] or 0:.1f}",
                    f"{proc['memory_percent'] or 0:.1f}",
                    proc['status']
                ))
        except:
            pass
            
    def check_thresholds(self, cpu_percent, memory_percent):
        """Check if thresholds are exceeded and show alerts"""
        if cpu_percent > self.cpu_threshold:
            self.show_threshold_alert("CPU", cpu_percent, self.cpu_threshold)
            
        if memory_percent > self.memory_threshold:
            self.show_threshold_alert("Memory", memory_percent, self.memory_threshold)
            
    def show_threshold_alert(self, metric, current, threshold):
        """Show threshold exceeded alert"""
        # Simple notification (can be enhanced with system notifications)
        self.footer_status.config(
            text=f"⚠️ {metric} usage high: {current:.1f}% (threshold: {threshold}%)",
            fg="#ff6b6b")
            
        # Auto-reset status after 10 seconds
        self.root.after(10000, lambda: self.footer_status.config(
            text="System monitoring active", fg="#4ecdc4"))
            
    def refresh_data(self):
        """Manually refresh all data"""
        self.refresh_processes()
        self.footer_status.config(text="Data refreshed", fg="#4ecdc4")
        self.root.after(3000, lambda: self.footer_status.config(
            text="System monitoring active", fg="#4ecdc4"))
            
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        if self.dark_mode:
            # Light theme colors
            bg_color = "#f5f5f5"
            card_color = "#ffffff"
            text_color = "#333333"
            accent_color = "#007acc"
        else:
            # Dark theme colors (current)
            bg_color = "#1a1a2e"
            card_color = "#16213e"
            text_color = "#ffffff"
            accent_color = "#4ecdc4"
            
        # Update theme (simplified implementation)
        # In a full implementation, you would update all widget colors
        self.dark_mode = not self.dark_mode
        
        message = "Switched to Light Mode" if not self.dark_mode else "Switched to Dark Mode"
        self.footer_status.config(text=message, fg=accent_color)
        self.root.after(3000, lambda: self.footer_status.config(
            text="System monitoring active", fg="#4ecdc4"))
            
    def export_report(self):
        """Export system performance report"""
        try:
            # Generate report data
            report_data = self.generate_report_data()
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Performance Report"
            )
            
            if filename:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(report_data, f, indent=4, default=str)
                else:
                    with open(filename, 'w') as f:
                        f.write(self.format_report_text(report_data))
                        
                messagebox.showinfo("Export Complete", f"Report saved to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
            
    def generate_report_data(self):
        """Generate comprehensive system report data"""
        system_info = self.get_system_info()
        cpu_info = {
            'usage_percent': list(self.cpu_history)[-1] if self.cpu_history else 0,
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': memory.total / 1024**3,
            'available_gb': memory.available / 1024**3,
            'used_gb': memory.used / 1024**3,
            'percent': memory.percent
        }
        
        disk_info = []
        for partition in psutil.disk_partitions():
            try:
                disk_usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total_gb': disk_usage.total / 1024**3,
                    'used_gb': disk_usage.used / 1024**3,
                    'free_gb': disk_usage.free / 1024**3,
                    'percent': (disk_usage.used / disk_usage.total) * 100
                })
            except:
                continue
                
        net_io = psutil.net_io_counters()
        network_info = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': system_info,
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'network': network_info,
            'team_info': {
                'name': 'Architechs',
                'id': 'SE(OS)-VI-T250',
                'members': [
                    {'name': 'Harshit Jasuja', 'id': '220211228', 'email': 'harshitjasuja70@gmail.com'},
                    {'name': 'Shivendra Srivastava', 'id': '220211349', 'email': 'shivendrasri999@gmail.com'},
                    {'name': 'Yashika Dixit', 'id': '22022577', 'email': 'yashikadixit1611@gmail.com'}
                ]
            }
        }
        
    def format_report_text(self, data):
        """Format report data as readable text"""
        report = f"""SYSTEM PERFORMANCE REPORT
Generated: {data['timestamp']}
Team: {data['team_info']['name']} ({data['team_info']['id']})

=== SYSTEM INFORMATION ===
System: {data['system']['system']}
Processor: {data['system']['processor']}
Architecture: {data['system']['architecture']}

=== CPU INFORMATION ===
Current Usage: {data['cpu']['usage_percent']:.1f}%
Physical Cores: {data['cpu']['cores_physical']}
Logical Cores: {data['cpu']['cores_logical']}

=== MEMORY INFORMATION ===
Total: {data['memory']['total_gb']:.2f} GB
Used: {data['memory']['used_gb']:.2f} GB
Available: {data['memory']['available_gb']:.2f} GB
Usage: {data['memory']['percent']:.1f}%

=== DISK INFORMATION ==="""

        for disk in data['disk']:
            report += f"""
Drive: {disk['device']} ({disk['mountpoint']})
  Total: {disk['total_gb']:.2f} GB
  Used: {disk['used_gb']:.2f} GB ({disk['percent']:.1f}%)
  Free: {disk['free_gb']:.2f} GB"""

        report += f"""

=== NETWORK INFORMATION ===
Bytes Sent: {data['network']['bytes_sent']:,}
Bytes Received: {data['network']['bytes_recv']:,}
Packets Sent: {data['network']['packets_sent']:,}
Packets Received: {data['network']['packets_recv']:,}

=== TEAM MEMBERS ==="""

        for member in data['team_info']['members']:
            report += f"""
{member['name']} (ID: {member['id']})
Email: {member['email']}"""

        return report
        
    def open_process_manager(self):
        """Switch to process tab"""
        # Switch to processes tab
        self.notebook.select(5)  # Index of processes tab
        self.refresh_processes()
        
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#1a1a2e")
        settings_window.resizable(False, False)
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (300 // 2)
        settings_window.geometry(f"400x300+{x}+{y}")
        
        # Settings content
        main_frame = tk.Frame(settings_window, bg="#1a1a2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(main_frame, text="Settings", 
                font=("SF Pro Display", 18, "bold"),
                fg="#4ecdc4", bg="#1a1a2e").pack(pady=(0, 20))
        
        # Threshold settings
        threshold_frame = tk.LabelFrame(main_frame, text="Alert Thresholds",
                                       font=("SF Pro Display", 12, "bold"),
                                       fg="#ffe66d", bg="#16213e")
        threshold_frame.pack(fill="x", pady=10)
        
        # CPU threshold
        cpu_frame = tk.Frame(threshold_frame, bg="#16213e")
        cpu_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(cpu_frame, text="CPU Threshold (%):",
                font=("SF Pro Display", 11),
                fg="white", bg="#16213e").pack(side="left")
        
        cpu_threshold_var = tk.IntVar(value=self.cpu_threshold)
        cpu_scale = tk.Scale(cpu_frame, from_=50, to=95, orient="horizontal",
                            variable=cpu_threshold_var, bg="#16213e", fg="white",
                            highlightthickness=0)
        cpu_scale.pack(side="right")
        
        # Memory threshold
        mem_frame = tk.Frame(threshold_frame, bg="#16213e")
        mem_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(mem_frame, text="Memory Threshold (%):",
                font=("SF Pro Display", 11),
                fg="white", bg="#16213e").pack(side="left")
        
        mem_threshold_var = tk.IntVar(value=self.memory_threshold)
        mem_scale = tk.Scale(mem_frame, from_=60, to=95, orient="horizontal",
                            variable=mem_threshold_var, bg="#16213e", fg="white",
                            highlightthickness=0)
        mem_scale.pack(side="right")
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#1a1a2e")
        button_frame.pack(fill="x", pady=20)
        
        def save_settings():
            self.cpu_threshold = cpu_threshold_var.get()
            self.memory_threshold = mem_threshold_var.get()
            messagebox.showinfo("Settings", "Settings saved successfully!")
            settings_window.destroy()
            
        save_btn = tk.Button(button_frame, text="Save", command=save_settings,
                            bg="#4ecdc4", fg="white", font=("SF Pro Display", 12, "bold"),
                            relief="flat", padx=30, pady=5)
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=settings_window.destroy,
                              bg="#ff6b6b", fg="white", font=("SF Pro Display", 12, "bold"),
                              relief="flat", padx=30, pady=5)
        cancel_btn.pack(side="right")
        
    def show_about(self):
        """Show about team dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Team Architechs")
        about_window.geometry("500x400")
        about_window.configure(bg="#1a1a2e")
        about_window.resizable(False, False)
        
        # Center the window
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (about_window.winfo_screenheight() // 2) - (400 // 2)
        about_window.geometry(f"500x400+{x}+{y}")
        
        # About content
        main_frame = tk.Frame(about_window, bg="#1a1a2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # App title
        tk.Label(main_frame, text="System Performance Analyzer", 
                font=("SF Pro Display", 18, "bold"),
                fg="#4ecdc4", bg="#1a1a2e").pack(pady=(0, 10))
        
        # Team info
        team_frame = tk.Frame(main_frame, bg="#16213e", relief="raised", bd=1)
        team_frame.pack(fill="x", pady=10)
        
        team_content = tk.Frame(team_frame, bg="#16213e")
        team_content.pack(padx=20, pady=15)
        
        tk.Label(team_content, text="Team: Architechs", 
                font=("SF Pro Display", 16, "bold"),
                fg="#ffe66d", bg="#16213e").pack()
        
        tk.Label(team_content, text="Team ID: SE(OS)-VI-T250", 
                font=("SF Pro Display", 14),
                fg="#a8e6cf", bg="#16213e").pack(pady=5)
        
        # Team members
        members_frame = tk.Frame(main_frame, bg="#16213e", relief="raised", bd=1)
        members_frame.pack(fill="both", expand=True, pady=10)
        
        members_content = tk.Frame(members_frame, bg="#16213e")
        members_content.pack(padx=20, pady=15, fill="both", expand=True)
        
        tk.Label(members_content, text="Team Members:", 
                font=("SF Pro Display", 14, "bold"),
                fg="#ff6b6b", bg="#16213e").pack(pady=(0, 10))
        
        members = [
            ("Team Lead", "Harshit Jasuja", "220211228", "harshitjasuja70@gmail.com"),
            ("Member 2", "Shivendra Srivastava", "220211349", "shivendrasri999@gmail.com"),
            ("Member 3", "Yashika Dixit", "22022577", "yashikadixit1611@gmail.com")
        ]
        
        for role, name, student_id, email in members:
            member_frame = tk.Frame(members_content, bg="#1a1a2e", relief="flat", bd=1)
            member_frame.pack(fill="x", pady=5)
            
            info_frame = tk.Frame(member_frame, bg="#1a1a2e")
            info_frame.pack(padx=15, pady=10)
            
            tk.Label(info_frame, text=f"{role}: {name}", 
                    font=("SF Pro Display", 12, "bold"),
                    fg="#4ecdc4", bg="#1a1a2e").pack(anchor="w")
            
            tk.Label(info_frame, text=f"Student ID: {student_id}", 
                    font=("SF Pro Display", 10),
                    fg="#a8e6cf", bg="#1a1a2e").pack(anchor="w")
            
            tk.Label(info_frame, text=f"Email: {email}", 
                    font=("SF Pro Display", 10),
                    fg="#ffe66d", bg="#1a1a2e").pack(anchor="w")
        
        # Close button
        close_btn = tk.Button(main_frame, text="Close", command=about_window.destroy,
                             bg="#ff6b6b", fg="white", font=("SF Pro Display", 12, "bold"),
                             relief="flat", padx=30, pady=5)
        close_btn.pack(pady=10)
        
    def on_closing(self):
        """Handle application closing"""
        self.monitoring = False
        self.root.destroy()
def main():
    """Main application entry point"""
    # Create root window (hidden initially)
    root = tk.Tk()
    root.withdraw()  # Hide main window during splash
    
    # Show splash screen
    splash = SplashScreen(root)
    root.wait_window(splash.splash)
    
    # Show main window
    root.deiconify()
    
    # Create main application
    app = SystemAnalyzer(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start main loop
    root.mainloop()
    
if __name__ == "__main__":
    main()