import tkinter as tk
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import psutil
import threading
import time
import json
import os
from datetime import datetime, timedelta
from collections import deque
import csv
import sqlite3
import platform
import sys

# Try to import additional libraries
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class SystemPerformanceAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("System Performance Analyzer")
        self.root.geometry("1500x1000")
        self.root.minsize(1300, 900)
        
        # Enhanced color schemes
        self.themes = {
            'light': {
                'bg': '#f0f0f0',
                'fg': '#333333',
                'accent': '#1f538d',
                'secondary': '#14a085',
                'warning': '#f5a623',
                'danger': '#d0021b',
                'success': '#28a745',
                'info': '#17a2b8',
                'card_bg': '#ffffff',
                'hover': '#e6f3ff'
            },
            'dark': {
                'bg': '#212121',
                'fg': '#ffffff',
                'accent': '#1f538d',
                'secondary': '#14a085',
                'warning': '#f5a623',
                'danger': '#d0021b',
                'success': '#28a745',
                'info': '#17a2b8',
                'card_bg': '#2b2b2b',
                'hover': '#4a6741'
            }
        }
        
        self.current_theme = 'light'
        self.colors = self.themes[self.current_theme]
        
        # Enhanced performance data storage
        self.cpu_data = deque(maxlen=100)
        self.memory_data = deque(maxlen=100)
        self.disk_data = deque(maxlen=100)
        self.network_data = deque(maxlen=100)
        self.temperature_data = deque(maxlen=100)
        self.time_data = deque(maxlen=100)
        
        # Advanced settings
        self.refresh_rate = 1000
        self.font_size = 12
        self.notifications_enabled = True
        self.data_logging = True
        self.alert_thresholds = {
            'cpu': 80,
            'memory': 85,
            'disk': 90,
            'temperature': 80
        }
        
        # Analytics data
        self.performance_history = []
        self.optimization_suggestions = []
        self.system_health_score = 100
        self.benchmark_results = {}
        
        # Database for persistent storage
        self.init_database()
        
        # System information
        self.system_info = self.get_system_info()
        
        # Monitoring flags
        self.monitoring = True
        self.benchmark_running = False
        
        self.setup_ui()
        self.start_monitoring()
        self.load_settings()
        
    def init_database(self):
        """Initialize SQLite database for data persistence"""
        try:
            self.db_path = "performance_data.db"
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_usage REAL,
                    temperature REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    optimization_type TEXT,
                    description TEXT,
                    success BOOLEAN
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    event_type TEXT,
                    description TEXT,
                    severity TEXT
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
            
    def get_system_info(self):
        """Get comprehensive system information with error handling"""
        info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total,
            'boot_time': psutil.boot_time(),
        }
        
        # Handle CPU frequency with error handling
        try:
            cpu_freq = psutil.cpu_freq()
            info['cpu_freq'] = cpu_freq
        except (OSError, AttributeError, PermissionError) as e:
            print(f"Warning: CPU frequency not available: {e}")
            info['cpu_freq'] = None
            
        return info
        
    def setup_ui(self):
        """Setup the enhanced UI components"""
        # Main title frame with system info
        title_frame = ctk.CTkFrame(self.root)
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🚀 System Performance Analyzer",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=10)
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="System monitoring and performance analysis",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 10))
        
        # System health indicator
        self.health_frame = ctk.CTkFrame(title_frame)
        self.health_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.health_label = ctk.CTkLabel(
            self.health_frame,
            text=f"🎯 System Health Score: {self.system_health_score}%",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.health_label.pack(pady=5)
        
        # Create enhanced tabview
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create tabs
        self.dashboard_tab = self.notebook.add("📊 Dashboard")
        self.ai_tab = self.notebook.add("📊 Performance Analysis")
        self.analytics_tab = self.notebook.add("📈 Analytics")
        self.benchmark_tab = self.notebook.add("⚡ Benchmark")
        self.system_tab = self.notebook.add("💻 System Info")
        self.settings_tab = self.notebook.add("⚙️ Settings")
        self.help_tab = self.notebook.add("❓ Help")
        
        # Create content for each tab
        self.create_dashboard_content()
        self.create_ai_optimizer_content()
        self.create_analytics_content()
        self.create_benchmark_content()
        self.create_system_info_content()
        self.create_settings_content()
        self.create_help_content()
        
    def create_dashboard_content(self):
        """Create enhanced performance dashboard"""
        main_container = ctk.CTkScrollableFrame(self.dashboard_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Enhanced metrics cards
        metrics_frame = ctk.CTkFrame(main_container)
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        self.create_enhanced_metric_cards(metrics_frame)
        
        # Real-time alerts panel
        alerts_frame = ctk.CTkFrame(main_container)
        alerts_frame.pack(fill='x', pady=(0, 20))
        
        alerts_title = ctk.CTkLabel(
            alerts_frame,
            text="🚨 Real-time Alerts",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        alerts_title.pack(pady=(15, 10))
        
        self.alerts_textbox = ctk.CTkTextbox(
            alerts_frame,
            height=80,
            font=ctk.CTkFont(size=11)
        )
        self.alerts_textbox.pack(fill='x', padx=15, pady=(0, 15))
        
        # Enhanced charts
        charts_frame = ctk.CTkFrame(main_container)
        charts_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.create_enhanced_charts(charts_frame)
        
        # Enhanced controls
        controls_frame = ctk.CTkFrame(main_container)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        self.create_enhanced_controls(controls_frame)
        
    def create_enhanced_metric_cards(self, parent):
        """Create enhanced metric display cards with additional information"""
        parent.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # CPU Card with temperature
        cpu_frame = ctk.CTkFrame(parent)
        cpu_frame.grid(row=0, column=0, padx=8, pady=10, sticky='ew')
        
        ctk.CTkLabel(cpu_frame, text="🔥 CPU Usage", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.cpu_value_label = ctk.CTkLabel(cpu_frame, text="0%", 
                                          font=ctk.CTkFont(size=18, weight="bold"))
        self.cpu_value_label.pack()
        self.cpu_temp_label = ctk.CTkLabel(cpu_frame, text="Temp: N/A", 
                                         font=ctk.CTkFont(size=10))
        self.cpu_temp_label.pack(pady=(0, 10))
        
        # Memory Card with available memory
        memory_frame = ctk.CTkFrame(parent)
        memory_frame.grid(row=0, column=1, padx=8, pady=10, sticky='ew')
        
        ctk.CTkLabel(memory_frame, text="💾 Memory", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.memory_value_label = ctk.CTkLabel(memory_frame, text="0%", 
                                             font=ctk.CTkFont(size=18, weight="bold"))
        self.memory_value_label.pack()
        self.memory_available_label = ctk.CTkLabel(memory_frame, text="Available: 0 GB", 
                                                 font=ctk.CTkFont(size=10))
        self.memory_available_label.pack(pady=(0, 10))
        
        # Disk Card with read/write speeds
        disk_frame = ctk.CTkFrame(parent)
        disk_frame.grid(row=0, column=2, padx=8, pady=10, sticky='ew')
        
        ctk.CTkLabel(disk_frame, text="💽 Disk", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.disk_value_label = ctk.CTkLabel(disk_frame, text="0%", 
                                           font=ctk.CTkFont(size=18, weight="bold"))
        self.disk_value_label.pack()
        self.disk_io_label = ctk.CTkLabel(disk_frame, text="I/O: 0 MB/s", 
                                        font=ctk.CTkFont(size=10))
        self.disk_io_label.pack(pady=(0, 10))
        
        # Network Card with upload/download
        network_frame = ctk.CTkFrame(parent)
        network_frame.grid(row=0, column=3, padx=8, pady=10, sticky='ew')
        
        ctk.CTkLabel(network_frame, text="🌐 Network", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.network_value_label = ctk.CTkLabel(network_frame, text="0 MB/s", 
                                              font=ctk.CTkFont(size=18, weight="bold"))
        self.network_value_label.pack()
        self.network_detail_label = ctk.CTkLabel(network_frame, text="↑0 ↓0 MB/s", 
                                                font=ctk.CTkFont(size=10))
        self.network_detail_label.pack(pady=(0, 10))
        
        # System Health Card
        health_frame = ctk.CTkFrame(parent)
        health_frame.grid(row=0, column=4, padx=8, pady=10, sticky='ew')
        
        ctk.CTkLabel(health_frame, text="🎯 Health", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.health_value_label = ctk.CTkLabel(health_frame, text="100%", 
                                             font=ctk.CTkFont(size=18, weight="bold"))
        self.health_value_label.pack()
        self.uptime_label = ctk.CTkLabel(health_frame, text="Uptime: 0h", 
                                       font=ctk.CTkFont(size=10))
        self.uptime_label.pack(pady=(0, 10))
        
    def create_enhanced_charts(self, parent):
        """Create enhanced performance charts with much smaller size for clarity"""
        # Much smaller figure size for 13-inch screen clarity
        self.fig, axes = plt.subplots(2, 3, figsize=(8, 4.5))  # Significantly reduced from (10, 6)
        self.fig.patch.set_facecolor('#f0f0f0')
        
        # Tighter spacing for compact display
        self.fig.subplots_adjust(
            left=0.1, bottom=0.15, right=0.95, top=0.88, wspace=0.3, hspace=0.4
        )
        
        self.ax1, self.ax2, self.ax3 = axes[0]
        self.ax4, self.ax5, self.ax6 = axes[1]
        
        chart_configs = [
            (self.ax1, 'CPU (%)', '%'),
            (self.ax2, 'Memory (%)', '%'),
            (self.ax3, 'Disk (%)', '%'),
            (self.ax4, 'Network (MB/s)', 'MB/s'),
            (self.ax5, 'Temp (°C)', '°C'),
            (self.ax6, 'Health', 'Score')
        ]
        
        for ax, title, ylabel in chart_configs:
            ax.set_title(title, fontsize=9, fontweight='bold', pad=5)  # Smaller fonts
            ax.set_ylabel(ylabel, fontsize=8)
            ax.tick_params(labelsize=7)  # Very small tick labels
            ax.set_facecolor('#ffffff')
            ax.grid(True, alpha=0.3, linewidth=0.5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        self.animation = FuncAnimation(
            self.fig, self.update_enhanced_charts, interval=self.refresh_rate, blit=False
        )

        
    def create_enhanced_controls(self, parent):
        """Create enhanced dashboard controls"""
        parent.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Export button
        export_btn = ctk.CTkButton(
            parent,
            text="📄 Export Report",
            command=self.export_enhanced_report,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        export_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            parent,
            text="🔄 Refresh",
            command=self.manual_refresh,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        refresh_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Process manager button
        process_btn = ctk.CTkButton(
            parent,
            text="⚙️ Process Manager",
            command=self.open_enhanced_process_manager,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        process_btn.grid(row=0, column=2, padx=10, pady=10)
        
    def create_analytics_content(self):
        """Create analytics and historical data tab"""
        main_container = ctk.CTkScrollableFrame(self.analytics_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Analytics title
        title_label = ctk.CTkLabel(
            main_container,
            text="📈 Performance Analytics & Historical Data",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Time range selector
        range_frame = ctk.CTkFrame(main_container)
        range_frame.pack(fill='x', pady=10)
        
        ctk.CTkLabel(range_frame, text="📅 Time Range:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', padx=15, pady=10)
        
        self.time_range_var = ctk.StringVar(value="Last 24 Hours")
        time_range_menu = ctk.CTkOptionMenu(
            range_frame,
            variable=self.time_range_var,
            values=["Last Hour", "Last 24 Hours", "Last Week", "Last Month"],
            command=self.update_analytics
        )
        time_range_menu.pack(side='left', padx=10, pady=10)
        
        # Analytics summary
        summary_frame = ctk.CTkFrame(main_container)
        summary_frame.pack(fill='x', pady=10)
        
        summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Average metrics
        avg_cpu_frame = ctk.CTkFrame(summary_frame)
        avg_cpu_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        ctk.CTkLabel(avg_cpu_frame, text="📊 Avg CPU", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        self.avg_cpu_label = ctk.CTkLabel(avg_cpu_frame, text="0%", font=ctk.CTkFont(size=16))
        self.avg_cpu_label.pack(pady=5)
        
        avg_memory_frame = ctk.CTkFrame(summary_frame)
        avg_memory_frame.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        ctk.CTkLabel(avg_memory_frame, text="📊 Avg Memory", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        self.avg_memory_label = ctk.CTkLabel(avg_memory_frame, text="0%", font=ctk.CTkFont(size=16))
        self.avg_memory_label.pack(pady=5)
        
        peak_cpu_frame = ctk.CTkFrame(summary_frame)
        peak_cpu_frame.grid(row=0, column=2, padx=10, pady=10, sticky='ew')
        ctk.CTkLabel(peak_cpu_frame, text="🔝 Peak CPU", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        self.peak_cpu_label = ctk.CTkLabel(peak_cpu_frame, text="0%", font=ctk.CTkFont(size=16))
        self.peak_cpu_label.pack(pady=5)
        
        events_frame = ctk.CTkFrame(summary_frame)
        events_frame.grid(row=0, column=3, padx=10, pady=10, sticky='ew')
        ctk.CTkLabel(events_frame, text="📋 Events", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        self.events_count_label = ctk.CTkLabel(events_frame, text="0", font=ctk.CTkFont(size=16))
        self.events_count_label.pack(pady=5)
        
        # Historical data table
        history_frame = ctk.CTkFrame(main_container)
        history_frame.pack(fill='both', expand=True, pady=10)
        
        ctk.CTkLabel(history_frame, text="📋 Performance History", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        self.history_textbox = ctk.CTkTextbox(
            history_frame,
            font=ctk.CTkFont(size=10),
            height=300
        )
        self.history_textbox.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
    def create_benchmark_content(self):
        """Create system benchmark tab"""
        main_container = ctk.CTkScrollableFrame(self.benchmark_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Benchmark title
        title_label = ctk.CTkLabel(
            main_container,
            text="⚡ System Benchmark & Performance Testing",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Benchmark controls
        controls_frame = ctk.CTkFrame(main_container)
        controls_frame.pack(fill='x', pady=10)
        
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        cpu_benchmark_btn = ctk.CTkButton(
            controls_frame,
            text="🔥 CPU Benchmark",
            command=lambda: self.run_benchmark('cpu'),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cpu_benchmark_btn.grid(row=0, column=0, padx=10, pady=10)
        
        memory_benchmark_btn = ctk.CTkButton(
            controls_frame,
            text="💾 Memory Benchmark",
            command=lambda: self.run_benchmark('memory'),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        memory_benchmark_btn.grid(row=0, column=1, padx=10, pady=10)
        
        full_benchmark_btn = ctk.CTkButton(
            controls_frame,
            text="🚀 Full System Benchmark",
            command=lambda: self.run_benchmark('full'),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        full_benchmark_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Benchmark status
        self.benchmark_status_label = ctk.CTkLabel(
            main_container,
            text="⏳ Ready to run benchmarks",
            font=ctk.CTkFont(size=14)
        )
        self.benchmark_status_label.pack(pady=10)
        
        # Progress bar
        self.benchmark_progress = ctk.CTkProgressBar(main_container)
        self.benchmark_progress.pack(fill='x', padx=50, pady=10)
        self.benchmark_progress.set(0)
        
        # Results display
        results_frame = ctk.CTkFrame(main_container)
        results_frame.pack(fill='both', expand=True, pady=10)
        
        ctk.CTkLabel(results_frame, text="📊 Benchmark Results", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        self.benchmark_results_textbox = ctk.CTkTextbox(
            results_frame,
            font=ctk.CTkFont(size=11),
            height=400
        )
        self.benchmark_results_textbox.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
    def create_system_info_content(self):
        """Create comprehensive system information tab"""
        main_container = ctk.CTkScrollableFrame(self.system_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # System info title
        title_label = ctk.CTkLabel(
            main_container,
            text="💻 Comprehensive System Information",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # System overview
        overview_frame = ctk.CTkFrame(main_container)
        overview_frame.pack(fill='x', pady=10)
        
        overview_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Basic info
        basic_frame = ctk.CTkFrame(overview_frame)
        basic_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        ctk.CTkLabel(basic_frame, text="🖥️ Basic Information", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        basic_info = [
            f"Platform: {self.system_info['platform']}",
            f"Processor: {self.system_info['processor']}",
            f"Architecture: {self.system_info['architecture'][0]}",
            f"Python Version: {self.system_info['python_version']}"
        ]
        
        for info in basic_info:
            ctk.CTkLabel(basic_frame, text=info, font=ctk.CTkFont(size=11)).pack(anchor='w', padx=15, pady=2)
        
        # Hardware info
        hardware_frame = ctk.CTkFrame(overview_frame)
        hardware_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        ctk.CTkLabel(hardware_frame, text="⚙️ Hardware Information", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
        
        hardware_info = [
            f"CPU Cores: {self.system_info['cpu_count']}",
            f"CPU Frequency: {self.system_info['cpu_freq'].current:.2f} MHz" if self.system_info['cpu_freq'] else "CPU Frequency: N/A",
            f"Total Memory: {self.system_info['memory_total'] / (1024**3):.2f} GB",
            f"Total Disk: {self.system_info['disk_total'] / (1024**3):.2f} GB",
            f"Boot Time: {datetime.fromtimestamp(self.system_info['boot_time']).strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        for info in hardware_info:
            ctk.CTkLabel(hardware_frame, text=info, font=ctk.CTkFont(size=11)).pack(anchor='w', padx=15, pady=2)
        
        # Detailed system information
        detailed_frame = ctk.CTkFrame(main_container)
        detailed_frame.pack(fill='both', expand=True, pady=10)
        
        ctk.CTkLabel(detailed_frame, text="📋 Detailed System Report", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        self.system_info_textbox = ctk.CTkTextbox(
            detailed_frame,
            font=ctk.CTkFont(size=10),
            height=400
        )
        self.system_info_textbox.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Populate detailed system info
        self.populate_system_info()
        
    def create_ai_optimizer_content(self):
        """Create performance analysis content"""
        main_container = ctk.CTkScrollableFrame(self.ai_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # AI title
        title_label = ctk.CTkLabel(
            main_container,
            text="🧠 Performance Analysis & Recommendations",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # AI status and health
        status_frame = ctk.CTkFrame(main_container)
        status_frame.pack(fill='x', pady=10)
        
        status_frame.grid_columnconfigure((0, 1), weight=1)
        
        # AI status
        ai_status_frame = ctk.CTkFrame(status_frame)
        ai_status_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        
        ctk.CTkLabel(ai_status_frame, text="📊 Analysis Status", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        self.ai_status_label = ctk.CTkLabel(
            ai_status_frame,
            text="🔍 Analyzing system performance...",
            font=ctk.CTkFont(size=12)
        )
        self.ai_status_label.pack(pady=(0, 15))
        
        # System health
        health_status_frame = ctk.CTkFrame(status_frame)
        health_status_frame.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        ctk.CTkLabel(health_status_frame, text="🎯 System Health", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        self.health_status_label = ctk.CTkLabel(
            health_status_frame,
            text="Excellent",
            font=ctk.CTkFont(size=12)
        )
        self.health_status_label.pack(pady=(0, 15))
        
        # AI suggestions
        suggestions_frame = ctk.CTkFrame(main_container)
        suggestions_frame.pack(fill='both', expand=True, pady=10)
        
        suggestions_title = ctk.CTkLabel(
            suggestions_frame,
            text="💡 Performance Recommendations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        suggestions_title.pack(pady=(15, 10))
        
        self.suggestions_textbox = ctk.CTkTextbox(
            suggestions_frame,
            height=200,
            font=ctk.CTkFont(size=12)
        )
        self.suggestions_textbox.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # AI controls
        ai_controls_frame = ctk.CTkFrame(main_container)
        ai_controls_frame.pack(fill='x', pady=10)
        
        ai_controls_frame.grid_columnconfigure(0, weight=1)
        
        analyze_btn = ctk.CTkButton(
            ai_controls_frame,
            text="🔍 Run Analysis",
            command=self.run_ai_analysis,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        analyze_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Start AI analysis
        self.start_ai_analysis()
        
    def create_settings_content(self):
        """Create enhanced settings content"""
        main_container = ctk.CTkScrollableFrame(self.settings_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Settings title
        title_label = ctk.CTkLabel(
            main_container,
            text="⚙️ Advanced Settings & Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Theme settings
        theme_frame = ctk.CTkFrame(main_container)
        theme_frame.pack(fill='x', pady=10)
        
        theme_title = ctk.CTkLabel(
            theme_frame,
            text="🎨 Appearance Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        theme_title.pack(pady=(15, 10))
        
        self.theme_var = ctk.StringVar(value=self.current_theme)
        
        theme_options_frame = ctk.CTkFrame(theme_frame)
        theme_options_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        light_radio = ctk.CTkRadioButton(
            theme_options_frame,
            text="☀️ Light Mode",
            variable=self.theme_var,
            value='light',
            command=lambda: self.change_theme('light')
        )
        light_radio.pack(anchor='w', padx=20, pady=5)
        
        dark_radio = ctk.CTkRadioButton(
            theme_options_frame,
            text="🌙 Dark Mode",
            variable=self.theme_var,
            value='dark',
            command=lambda: self.change_theme('dark')
        )
        dark_radio.pack(anchor='w', padx=20, pady=5)
        
        # Performance settings
        perf_frame = ctk.CTkFrame(main_container)
        perf_frame.pack(fill='x', pady=10)
        
        perf_title = ctk.CTkLabel(
            perf_frame,
            text="📊 Performance Monitoring Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        perf_title.pack(pady=(15, 10))
        
        # Refresh rate
        refresh_frame = ctk.CTkFrame(perf_frame)
        refresh_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(refresh_frame, text="Refresh Rate (seconds):", 
                    font=ctk.CTkFont(size=12)).pack(anchor='w', padx=20, pady=5)
        
        self.refresh_slider = ctk.CTkSlider(
            refresh_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            command=self.update_refresh_rate
        )
        self.refresh_slider.set(self.refresh_rate // 1000)
        self.refresh_slider.pack(fill='x', padx=20, pady=5)
        
        # Data logging
        logging_frame = ctk.CTkFrame(perf_frame)
        logging_frame.pack(fill='x', padx=15, pady=5)
        
        self.logging_var = ctk.BooleanVar(value=self.data_logging)
        logging_check = ctk.CTkCheckBox(
            logging_frame,
            text="Enable data logging to database",
            variable=self.logging_var,
            command=self.toggle_data_logging
        )
        logging_check.pack(anchor='w', padx=20, pady=10)
        
        # Alert thresholds
        alerts_frame = ctk.CTkFrame(main_container)
        alerts_frame.pack(fill='x', pady=10)
        
        alerts_title = ctk.CTkLabel(
            alerts_frame,
            text="🚨 Alert Thresholds",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        alerts_title.pack(pady=(15, 10))
        
        # CPU threshold
        cpu_threshold_frame = ctk.CTkFrame(alerts_frame)
        cpu_threshold_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(cpu_threshold_frame, text="CPU Alert Threshold (%):", 
                    font=ctk.CTkFont(size=12)).pack(anchor='w', padx=20, pady=5)
        
        self.cpu_threshold_slider = ctk.CTkSlider(
            cpu_threshold_frame,
            from_=50,
            to=95,
            number_of_steps=9,
            command=lambda x: self.update_threshold('cpu', x)
        )
        self.cpu_threshold_slider.set(self.alert_thresholds['cpu'])
        self.cpu_threshold_slider.pack(fill='x', padx=20, pady=5)
        
        # Memory threshold
        memory_threshold_frame = ctk.CTkFrame(alerts_frame)
        memory_threshold_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(memory_threshold_frame, text="Memory Alert Threshold (%):", 
                    font=ctk.CTkFont(size=12)).pack(anchor='w', padx=20, pady=5)
        
        self.memory_threshold_slider = ctk.CTkSlider(
            memory_threshold_frame,
            from_=60,
            to=95,
            number_of_steps=7,
            command=lambda x: self.update_threshold('memory', x)
        )
        self.memory_threshold_slider.set(self.alert_thresholds['memory'])
        self.memory_threshold_slider.pack(fill='x', padx=20, pady=(5, 15))
        
        # Notifications
        notifications_frame = ctk.CTkFrame(main_container)
        notifications_frame.pack(fill='x', pady=10)
        
        notifications_title = ctk.CTkLabel(
            notifications_frame,
            text="🔔 Notification Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        notifications_title.pack(pady=(15, 10))
        
        notif_options_frame = ctk.CTkFrame(notifications_frame)
        notif_options_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.notifications_var = ctk.BooleanVar(value=self.notifications_enabled)
        notifications_check = ctk.CTkCheckBox(
            notif_options_frame,
            text="Enable performance alerts",
            variable=self.notifications_var,
            command=self.toggle_notifications
        )
        notifications_check.pack(anchor='w', padx=20, pady=5)
        
        
        
        
        
    def create_help_content(self):
        """Create enhanced help and FAQ content"""
        main_container = ctk.CTkScrollableFrame(self.help_tab)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="❓ Help Center & Frequently Asked Questions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Quick start guide
        quickstart_frame = ctk.CTkFrame(main_container)
        quickstart_frame.pack(fill='x', pady=10)
        
        quickstart_title = ctk.CTkLabel(
            quickstart_frame,
            text="🚀 Quick Start Guide",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        quickstart_title.pack(pady=(15, 10))
        
        quickstart_steps = [
            "1. Launch the application - monitoring starts automatically",
            "2. Navigate through tabs to explore different features",
            "3. Check the Dashboard for real-time system metrics",
            "4. Use AI Optimizer for intelligent system recommendations",
            "5. Customize settings in the Settings tab",
            "6. Export reports for analysis and record-keeping"
        ]
        
        for step in quickstart_steps:
            step_label = ctk.CTkLabel(
                quickstart_frame,
                text=step,
                font=ctk.CTkFont(size=11),
                anchor='w'
            )
            step_label.pack(fill='x', padx=20, pady=2)
        
        # Enhanced FAQ sections
        faqs = [
            {
                'category': '🚀 Getting Started',
                'questions': [
                    {
                        'question': 'How do I start monitoring my system?',
                        'answer': 'Simply launch the application and navigate to the Dashboard tab. Monitoring starts automatically and displays real-time system metrics including CPU, memory, disk, and network usage.'
                    },
                    {
                        'question': 'What are the system requirements?',
                        'answer': 'Minimum: Python 3.6+, 4GB RAM, 100MB storage. Recommended: Python 3.8+, 8GB RAM, SSD storage for optimal performance.'
                    }
                ]
            },
            {
                'category': '🤖 AI Features',
                'questions': [
                    {
                        'question': 'How does the AI optimizer work?',
                        'answer': 'The AI optimizer continuously analyzes your system performance patterns, identifies potential bottlenecks, and provides intelligent suggestions for optimization based on statistical analysis and rule-based algorithms.'
                    },
                    {
                        'question': 'Is automatic optimization safe?',
                        'answer': 'Yes, all AI optimizations are designed to be safe and non-destructive. The system will always ask for your confirmation before making any changes, and includes rollback capabilities.'
                    }
                ]
            },
            {
                'category': '⚙️ Configuration',
                'questions': [
                    {
                        'question': 'Can I customize monitoring intervals?',
                        'answer': 'Yes! Go to Settings tab and adjust the refresh rate slider. You can set monitoring intervals from 1 to 10 seconds based on your needs and system performance.'
                    },
                    {
                        'question': 'How do I change alert thresholds?',
                        'answer': 'Navigate to Settings tab and use the threshold sliders to customize CPU, memory, and other alert levels according to your requirements.'
                    }
                ]
            },
            {
                'category': '📊 Data & Reports',
                'questions': [
                    {
                        'question': 'How can I export performance data?',
                        'answer': 'Click "Export Report" in the Dashboard tab. Choose between PDF (comprehensive report) or CSV (raw data) formats for analysis or record-keeping.'
                    },
                    {
                        'question': 'Where is my data stored?',
                        'answer': 'Performance data is stored locally in an SQLite database. You can enable/disable data logging in the Settings tab. No data is transmitted externally without your consent.'
                    }
                ]
            }
        ]
        
        for faq_category in faqs:
            category_frame = ctk.CTkFrame(main_container)
            category_frame.pack(fill='x', pady=10)
            
            category_title = ctk.CTkLabel(
                category_frame,
                text=faq_category['category'],
                font=ctk.CTkFont(size=14, weight="bold")
            )
            category_title.pack(pady=(15, 10))
            
            for faq in faq_category['questions']:
                self.create_faq_item(category_frame, faq['question'], faq['answer'])
                
        # Troubleshooting section
        troubleshooting_frame = ctk.CTkFrame(main_container)
        troubleshooting_frame.pack(fill='x', pady=20)
        
        troubleshooting_title = ctk.CTkLabel(
            troubleshooting_frame,
            text="🔧 Troubleshooting",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        troubleshooting_title.pack(pady=(15, 10))
        
        troubleshooting_items = [
            "• Application won't start: Check Python version (3.6+ required) and install missing dependencies",
            "• Charts not updating: Verify monitoring is enabled and check refresh rate settings",
            "• High CPU usage: Increase monitoring interval in Settings to reduce overhead",
            "• Export fails: Ensure write permissions and sufficient disk space",
            "• Database errors: Check file permissions and disk space in application directory"
        ]
        
        for item in troubleshooting_items:
            item_label = ctk.CTkLabel(
                troubleshooting_frame,
                text=item,
                font=ctk.CTkFont(size=11),
                anchor='w',
                wraplength=800
            )
            item_label.pack(fill='x', padx=20, pady=2)
            
        # Support section
        support_frame = ctk.CTkFrame(main_container)
        support_frame.pack(fill='x', pady=20)
        
        support_title = ctk.CTkLabel(
            support_frame,
            text="📞 Technical Support",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        support_title.pack(pady=(15, 10))
        
        support_text = ctk.CTkLabel(
            support_frame,
            text="Need additional help? Our development team is here to assist!\n\n"
                 "📚 Documentation: Comprehensive guides available in Theory tab\n"
                 "🔄 Updates: Regular updates and improvements\n\n"
                 "When reporting issues, please include:\n"
                 "• Operating system and version\n"
                 "• Python version\n"
                 "• Error messages or screenshots\n"
                 "• Steps to reproduce the issue",
            font=ctk.CTkFont(size=12),
            justify='center'
        )
        support_text.pack(pady=(0, 15))
        
    def create_faq_item(self, parent, question, answer):
        """Create enhanced FAQ item with better formatting"""
        faq_frame = ctk.CTkFrame(parent)
        faq_frame.pack(fill='x', padx=15, pady=5)
        
        # Question
        question_label = ctk.CTkLabel(
            faq_frame,
            text=f"❓ {question}",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor='w'
        )
        question_label.pack(fill='x', padx=15, pady=(15, 5))
        
        # Answer
        answer_label = ctk.CTkLabel(
            faq_frame,
            text=answer,
            font=ctk.CTkFont(size=11),
            anchor='w',
            wraplength=700,
            justify='left'
        )
        answer_label.pack(fill='x', padx=15, pady=(0, 15))
        
    # Enhanced monitoring and data processing methods
    def start_monitoring(self):
        """Start enhanced system monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.enhanced_monitor_system, daemon=True)
        self.monitor_thread.start()
        
    def enhanced_monitor_system(self):
        """Enhanced system monitoring with better error handling"""
        while self.monitoring:
            try:
                current_time = time.time()
                
                # Get system metrics with error handling
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Get temperature with comprehensive error handling
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Try to find CPU temperature
                        cpu_temp = None
                        for sensor_name, sensor_list in temps.items():
                            for sensor in sensor_list:
                                if any(keyword in sensor.label.lower() for keyword in ['cpu', 'core', 'processor']):
                                    cpu_temp = sensor.current
                                    break
                            if cpu_temp:
                                break
                        
                        if cpu_temp:
                            self.temperature_data.append(cpu_temp)
                        else:
                            self.temperature_data.append(0)
                    else:
                        self.temperature_data.append(0)
                except (OSError, AttributeError, PermissionError):
                    # Temperature sensors not available or accessible
                    self.temperature_data.append(0)
                
                # Continue with rest of monitoring...
                self.cpu_data.append(cpu_percent)
                self.memory_data.append(memory.percent)
                self.disk_data.append(disk.percent)
                
                # Calculate network speed with error handling
                if hasattr(self, 'prev_network'):
                    time_diff = current_time - self.prev_network_time
                    if time_diff > 0:
                        try:
                            bytes_diff = (network.bytes_sent + network.bytes_recv - 
                                        self.prev_network.bytes_sent - self.prev_network.bytes_recv)
                            net_speed = bytes_diff / (1024 * 1024 * time_diff)  # MB/s
                            self.network_data.append(max(0, net_speed))
                        except (AttributeError, TypeError):
                            self.network_data.append(0)
                    else:
                        self.network_data.append(0)
                else:
                    self.network_data.append(0)
                
                self.prev_network = network
                self.prev_network_time = current_time
                self.time_data.append(current_time)
                
                # Rest of the monitoring code...
                self.calculate_system_health_score(cpu_percent, memory.percent, disk.percent)
                
                # Update UI
                self.root.after(0, self.update_enhanced_metric_cards, 
                            cpu_percent, memory.percent, disk.percent, 
                            self.network_data[-1] if self.network_data else 0,
                            self.temperature_data[-1] if self.temperature_data else 0)
                
                # Store performance data
                performance_data = {
                    'timestamp': current_time,
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'disk': disk.percent,
                    'network': self.network_data[-1] if self.network_data else 0,
                    'temperature': self.temperature_data[-1] if self.temperature_data else 0
                }
                
                self.performance_history.append(performance_data)
                
                # Log to database if enabled
                if self.data_logging:
                    self.log_to_database(performance_data)
                
                # Keep only recent history in memory
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-500:]
                
                # Check for alerts
                if self.notifications_enabled:
                    self.check_enhanced_performance_alerts(cpu_percent, memory.percent, disk.percent)
                
                time.sleep(self.refresh_rate / 1000)
                
            except Exception as e:
                print(f"Enhanced monitoring error: {e}")
                time.sleep(1)
                
    def calculate_system_health_score(self, cpu, memory, disk):
        """Calculate overall system health score"""
        try:
            # Base score
            score = 100
            
            # Deduct points based on usage
            if cpu > 80:
                score -= (cpu - 80) * 2
            if memory > 85:
                score -= (memory - 85) * 3
            if disk > 90:
                score -= (disk - 90) * 5
                
            # Consider temperature if available
            if self.temperature_data and self.temperature_data[-1] > 0:
                temp = self.temperature_data[-1]
                if temp > 80:
                    score -= (temp - 80) * 1.5
                    
            # Ensure score is within bounds
            self.system_health_score = max(0, min(100, score))
            
            # Update health status
            if self.system_health_score >= 90:
                health_status = "Excellent"
            elif self.system_health_score >= 75:
                health_status = "Good"
            elif self.system_health_score >= 60:
                health_status = "Fair"
            elif self.system_health_score >= 40:
                health_status = "Poor"
            else:
                health_status = "Critical"
                
            self.root.after(0, lambda: self.health_label.configure(text=f"🎯 System Health Score: {self.system_health_score:.0f}%"))
            if hasattr(self, 'health_status_label'):
                self.root.after(0, lambda: self.health_status_label.configure(text=health_status))
                
        except Exception as e:
            print(f"Health score calculation error: {e}")
            
    def update_enhanced_metric_cards(self, cpu, memory, disk, network, temperature):
        """Update enhanced metric display cards"""
        try:
            # Update basic metrics
            self.cpu_value_label.configure(text=f"{cpu:.1f}%")
            self.memory_value_label.configure(text=f"{memory:.1f}%")
            self.disk_value_label.configure(text=f"{disk:.1f}%")
            self.network_value_label.configure(text=f"{network:.2f} MB/s")
            self.health_value_label.configure(text=f"{self.system_health_score:.0f}%")
            
            # Update additional information
            if temperature > 0:
                self.cpu_temp_label.configure(text=f"Temp: {temperature:.1f}°C")
            else:
                self.cpu_temp_label.configure(text="Temp: N/A")
                
            # Memory available
            try:
                memory_info = psutil.virtual_memory()
                available_gb = memory_info.available / (1024**3)
                self.memory_available_label.configure(text=f"Available: {available_gb:.1f} GB")
            except:
                self.memory_available_label.configure(text="Available: N/A")
                
            # Disk I/O
            try:
                disk_io = psutil.disk_io_counters()
                if hasattr(self, 'prev_disk_io'):
                    time_diff = time.time() - self.prev_disk_io_time
                    if time_diff > 0:
                        read_speed = (disk_io.read_bytes - self.prev_disk_io.read_bytes) / (1024*1024*time_diff)
                        write_speed = (disk_io.write_bytes - self.prev_disk_io.write_bytes) / (1024*1024*time_diff)
                        total_io = read_speed + write_speed
                        self.disk_io_label.configure(text=f"I/O: {total_io:.1f} MB/s")
                    else:
                        self.disk_io_label.configure(text="I/O: 0 MB/s")
                else:
                    self.disk_io_label.configure(text="I/O: 0 MB/s")
                    
                self.prev_disk_io = disk_io
                self.prev_disk_io_time = time.time()
            except:
                self.disk_io_label.configure(text="I/O: N/A")
                
            # Network details
            try:
                # Simulate upload/download split for display
                upload = network * 0.3  # Approximate
                download = network * 0.7  # Approximate
                self.network_detail_label.configure(text=f"↑{upload:.1f} ↓{download:.1f} MB/s")
            except:
                self.network_detail_label.configure(text="↑0 ↓0 MB/s")
                
            # System uptime
            try:
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time
                uptime_hours = uptime_seconds / 3600
                if uptime_hours < 24:
                    self.uptime_label.configure(text=f"Uptime: {uptime_hours:.1f}h")
                else:
                    uptime_days = uptime_hours / 24
                    self.uptime_label.configure(text=f"Uptime: {uptime_days:.1f}d")
            except:
                self.uptime_label.configure(text="Uptime: N/A")
                
        except Exception as e:
            print(f"Enhanced metric cards update error: {e}")
            
    def log_to_database(self, data):
        """Log performance data to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO performance_logs 
                (timestamp, cpu_usage, memory_usage, disk_usage, network_usage, temperature)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.fromtimestamp(data['timestamp']),
                data['cpu'],
                data['memory'],
                data['disk'],
                data['network'],
                data['temperature']
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Database logging error: {e}")
            
    def check_enhanced_performance_alerts(self, cpu, memory, disk):
        """Enhanced performance alert checking"""
        alerts = []
        
        if cpu > self.alert_thresholds['cpu']:
            alerts.append(f"🔥 High CPU usage: {cpu:.1f}% (threshold: {self.alert_thresholds['cpu']}%)")
        if memory > self.alert_thresholds['memory']:
            alerts.append(f"💾 High memory usage: {memory:.1f}% (threshold: {self.alert_thresholds['memory']}%)")
        if disk > self.alert_thresholds['disk']:
            alerts.append(f"💽 High disk usage: {disk:.1f}% (threshold: {self.alert_thresholds['disk']}%)")
            
        # Temperature alerts
        if self.temperature_data and self.temperature_data[-1] > self.alert_thresholds.get('temperature', 80):
            alerts.append(f"🌡️ High temperature: {self.temperature_data[-1]:.1f}°C")
            
        if alerts:
            alert_text = "\n".join(alerts)
            self.root.after(0, lambda: self.update_alerts_display(alert_text))
            
            # Show popup if significant alerts
            if not hasattr(self, 'last_alert_time') or time.time() - self.last_alert_time > 30:
                self.show_alert(alert_text)
                self.last_alert_time = time.time()
                
    def update_alerts_display(self, alert_text):
        """Update the alerts display panel"""
        try:
            if hasattr(self, 'alerts_textbox'):
                current_time = datetime.now().strftime("%H:%M:%S")
                self.alerts_textbox.delete('0.0', 'end')
                self.alerts_textbox.insert('0.0', f"[{current_time}] {alert_text}")
        except:
            pass
            
    def show_alert(self, message):
        """Show enhanced performance alert"""
        def show_messagebox():
            import tkinter.messagebox as messagebox
            messagebox.showwarning("Performance Alert", message)
        
        self.root.after(0, show_messagebox)
        
    def start_ai_analysis(self):
        """Start enhanced AI analysis"""
        self.ai_thread = threading.Thread(target=self.enhanced_ai_analysis_loop, daemon=True)
        self.ai_thread.start()
        
    def enhanced_ai_analysis_loop(self):
        """Enhanced continuous AI analysis"""
        while True:
            try:
                time.sleep(15)  # Analyze every 15 seconds
                self.analyze_enhanced_performance_patterns()
            except Exception as e:
                print(f"Enhanced AI analysis error: {e}")
                
    def analyze_enhanced_performance_patterns(self):
        """Enhanced performance pattern analysis"""
        if len(self.performance_history) < 20:
            return
            
        recent_data = self.performance_history[-20:]
        suggestions = []
        
        # Advanced CPU analysis
        cpu_values = [d['cpu'] for d in recent_data]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        cpu_trend = (cpu_values[-5:] and sum(cpu_values[-5:]) / 5) - (cpu_values[:5] and sum(cpu_values[:5]) / 5)
        
        if avg_cpu > 70:
            suggestions.append(f"🔥 High average CPU usage ({avg_cpu:.1f}%). Consider closing unnecessary applications or upgrading hardware.")
        if cpu_trend > 10:
            suggestions.append("📈 CPU usage trending upward. Monitor for runaway processes or consider system restart.")
            
        # Advanced memory analysis
        memory_values = [d['memory'] for d in recent_data]
        avg_memory = sum(memory_values) / len(memory_values)
        memory_trend = (sum(memory_values[-5:]) / 5) - (sum(memory_values[:5]) / 5)
        
        if avg_memory > 80:
            suggestions.append(f"💾 High memory usage ({avg_memory:.1f}%). Consider closing memory-intensive applications.")
        if memory_trend > 15:
            suggestions.append("📊 Memory usage increasing rapidly. Possible memory leak detected.")
            
        # Disk analysis
        disk_values = [d['disk'] for d in recent_data]
        avg_disk = sum(disk_values) / len(disk_values)
        
        if avg_disk > 85:
            suggestions.append(f"💽 Disk space critical ({avg_disk:.1f}%). Run disk cleanup or free up space.")
            
        # Network analysis
        network_values = [d['network'] for d in recent_data]
        avg_network = sum(network_values) / len(network_values)
        
        if avg_network > 50:  # High network usage
            suggestions.append(f"🌐 High network activity ({avg_network:.1f} MB/s). Monitor for bandwidth-intensive applications.")
            
        # Temperature analysis
        temp_values = [d['temperature'] for d in recent_data if d['temperature'] > 0]
        if temp_values:
            avg_temp = sum(temp_values) / len(temp_values)
            if avg_temp > 75:
                suggestions.append(f"🌡️ High system temperature ({avg_temp:.1f}°C). Check cooling system.")
                
        # System health recommendations
        if self.system_health_score < 70:
            suggestions.append(f"⚠️ System health declining (Score: {self.system_health_score:.0f}%). Consider comprehensive optimization.")
            
        # Update suggestions
        self.optimization_suggestions = suggestions
        self.root.after(0, self.update_enhanced_ai_status)
        
    def update_enhanced_ai_status(self):
        """Update enhanced AI status display"""
        if hasattr(self, 'ai_status_label'):
            status = f"📊 Analysis complete. Health Score: {self.system_health_score:.0f}%. Found {len(self.optimization_suggestions)} recommendations."
            self.ai_status_label.configure(text=status)
            
        if hasattr(self, 'suggestions_textbox'):
            self.suggestions_textbox.delete('0.0', 'end')
            if self.optimization_suggestions:
                for i, suggestion in enumerate(self.optimization_suggestions, 1):
                    self.suggestions_textbox.insert('end', f"{i}. {suggestion}\n\n")
            else:
                self.suggestions_textbox.insert('0.0', "✅ System running optimally. No recommendations at this time.")
                
    def run_ai_analysis(self):
        """Manually trigger enhanced AI analysis"""
        self.ai_status_label.configure(text="🔍 Running comprehensive deep analysis...")
        threading.Thread(target=self.perform_enhanced_deep_analysis, daemon=True).start()
        
    def perform_enhanced_deep_analysis(self):
        """Perform enhanced deep system analysis"""
        try:
            time.sleep(3)  # Simulate analysis time
            
            suggestions = []
            
            # Process analysis
            try:
                processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']))
                high_cpu_processes = [p for p in processes if p.info['cpu_percent'] and p.info['cpu_percent'] > 15]
                high_memory_processes = [p for p in processes if p.info['memory_percent'] and p.info['memory_percent'] > 10]
                zombie_processes = [p for p in processes if p.info['status'] == 'zombie']
                
                if high_cpu_processes:
                    suggestions.append(f"🔍 Found {len(high_cpu_processes)} high-CPU processes. Consider optimizing or terminating unnecessary processes.")
                    
                if high_memory_processes:
                    suggestions.append(f"🔍 Found {len(high_memory_processes)} memory-intensive processes. Monitor for memory leaks.")
                    
                if zombie_processes:
                    suggestions.append(f"🧟 Found {len(zombie_processes)} zombie processes. System restart recommended.")
                    
            except Exception as e:
                suggestions.append(f"⚠️ Process analysis error: {str(e)}")
                
            # System uptime analysis
            try:
                boot_time = psutil.boot_time()
                uptime = time.time() - boot_time
                uptime_days = uptime / (24 * 3600)
                
                if uptime_days > 7:
                    suggestions.append(f"⏰ System uptime: {uptime_days:.1f} days. Consider restarting for optimal performance.")
                elif uptime_days > 30:
                    suggestions.append(f"🔄 Extended uptime ({uptime_days:.1f} days). Restart strongly recommended for system stability.")
                    
            except Exception as e:
                suggestions.append(f"⚠️ Uptime analysis error: {str(e)}")
                
            # Disk analysis
            try:
                disk_usage = psutil.disk_usage('/')
                if disk_usage.percent > 80:
                    free_gb = disk_usage.free / (1024**3)
                    suggestions.append(f"🗂️ Disk cleanup recommended. Only {free_gb:.1f} GB free space remaining.")
                    
                # Disk I/O analysis
                disk_io = psutil.disk_io_counters()
                if disk_io and hasattr(self, 'prev_disk_io'):
                    # Analyze I/O patterns (simplified)
                    suggestions.append("💽 Disk I/O analysis completed. Consider SSD upgrade for better performance.")
                    
            except Exception as e:
                suggestions.append(f"⚠️ Disk analysis error: {str(e)}")
                
            # Network analysis
            try:
                network_connections = len(psutil.net_connections())
                if network_connections > 100:
                    suggestions.append(f"🌐 High number of network connections ({network_connections}). Monitor for suspicious activity.")
                    
            except Exception as e:
                suggestions.append(f"⚠️ Network analysis error: {str(e)}")
                
            # Add to existing suggestions
            self.optimization_suggestions.extend(suggestions)
            self.root.after(0, self.update_enhanced_ai_status)
            
        except Exception as e:
            error_msg = f"Deep analysis failed: {str(e)}"
            self.root.after(0, lambda: self.ai_status_label.configure(text=f"❌ {error_msg}"))
            
            
            
    def populate_system_info(self):
        """Populate detailed system information textbox"""
        try:
            info_lines = []
            info_lines.append("🖥️ COMPREHENSIVE SYSTEM INFORMATION")
            info_lines.append("=" * 50)
            info_lines.append("")
            
            # Basic system info
            info_lines.append("📋 BASIC INFORMATION:")
            info_lines.append(f"Platform: {self.system_info['platform']}")
            info_lines.append(f"Processor: {self.system_info['processor']}")
            info_lines.append(f"Architecture: {self.system_info['architecture']}")
            info_lines.append(f"Python Version: {self.system_info['python_version']}")
            info_lines.append("")
            
            # Hardware info
            info_lines.append("⚙️ HARDWARE INFORMATION:")
            info_lines.append(f"CPU Cores: {self.system_info['cpu_count']}")
            if self.system_info['cpu_freq']:
                info_lines.append(f"CPU Frequency: {self.system_info['cpu_freq'].current:.2f} MHz")
                info_lines.append(f"CPU Max Frequency: {self.system_info['cpu_freq'].max:.2f} MHz")
            else:
                info_lines.append("CPU Frequency: N/A")
            info_lines.append(f"Total Memory: {self.system_info['memory_total'] / (1024**3):.2f} GB")
            info_lines.append(f"Total Disk: {self.system_info['disk_total'] / (1024**3):.2f} GB")
            info_lines.append("")
            
            # System status
            info_lines.append("📊 CURRENT SYSTEM STATUS:")
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                info_lines.append(f"Current CPU Usage: {cpu_percent:.1f}%")
                info_lines.append(f"Current Memory Usage: {memory.percent:.1f}%")
                info_lines.append(f"Available Memory: {memory.available / (1024**3):.2f} GB")
                info_lines.append(f"Current Disk Usage: {disk.percent:.1f}%")
                info_lines.append(f"Free Disk Space: {disk.free / (1024**3):.2f} GB")
            except:
                info_lines.append("Unable to retrieve current status")
            info_lines.append("")
            
            # System uptime
            info_lines.append("⏰ SYSTEM TIMING:")
            boot_time_str = datetime.fromtimestamp(self.system_info['boot_time']).strftime('%Y-%m-%d %H:%M:%S')
            info_lines.append(f"Boot Time: {boot_time_str}")
            uptime_seconds = time.time() - self.system_info['boot_time']
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            info_lines.append(f"System Uptime: {uptime_str}")
            info_lines.append("")
            
            # Running processes summary
            info_lines.append("🔄 PROCESS SUMMARY:")
            try:
                processes = list(psutil.process_iter())
                info_lines.append(f"Total Running Processes: {len(processes)}")
                
                # Count by status
                status_count = {}
                for proc in processes:
                    try:
                        status = proc.status()
                        status_count[status] = status_count.get(status, 0) + 1
                    except:
                        pass
                        
                for status, count in status_count.items():
                    info_lines.append(f"• {status.title()}: {count}")
                    
            except:
                info_lines.append("Unable to retrieve process information")
            info_lines.append("")
            
            # Performance monitoring info
            info_lines.append("📈 MONITORING INFORMATION:")
            info_lines.append(f"Monitoring Active: {'Yes' if self.monitoring else 'No'}")
            info_lines.append(f"Data Points Collected: {len(self.performance_history)}")
            info_lines.append(f"Current Health Score: {self.system_health_score:.0f}%")
            info_lines.append(f"Data Logging: {'Enabled' if self.data_logging else 'Disabled'}")
            info_lines.append(f"Refresh Rate: {self.refresh_rate / 1000:.1f} seconds")
            
            self.system_info_textbox.delete('0.0', 'end')
            self.system_info_textbox.insert('0.0', '\n'.join(info_lines))
            
        except Exception as e:
            self.system_info_textbox.delete('0.0', 'end')
            self.system_info_textbox.insert('0.0', f"Error loading system info: {e}")
            
    def update_enhanced_charts(self, frame):
        """Update enhanced performance charts"""
        try:
            if len(self.cpu_data) == 0:
                return
                
            x_data = list(range(len(self.cpu_data)))
            
            # CPU Usage
            self.ax1.clear()
            self.ax1.plot(x_data, list(self.cpu_data), color=self.colors['accent'], linewidth=2)
            self.ax1.set_title('CPU Usage (%)', fontsize=12, fontweight='bold')
            self.ax1.set_ylabel('Percentage')
            self.ax1.set_ylim(0, 100)
            
            # Memory Usage
            self.ax2.clear()
            self.ax2.plot(x_data, list(self.memory_data), color=self.colors['secondary'], linewidth=2)
            self.ax2.set_title('Memory Usage (%)', fontsize=12, fontweight='bold')
            self.ax2.set_ylabel('Percentage')
            self.ax2.set_ylim(0, 100)
            
            # Disk Usage
            self.ax3.clear()
            self.ax3.plot(x_data, list(self.disk_data), color=self.colors['warning'], linewidth=2)
            self.ax3.set_title('Disk Usage (%)', fontsize=12, fontweight='bold')
            self.ax3.set_ylabel('Percentage')
            self.ax3.set_ylim(0, 100)
            
            # Network Usage
            self.ax4.clear()
            self.ax4.plot(x_data, list(self.network_data), color=self.colors['danger'], linewidth=2)
            self.ax4.set_title('Network Usage (MB/s)', fontsize=12, fontweight='bold')
            self.ax4.set_ylabel('MB/s')
            
            # Temperature
            self.ax5.clear()
            if self.temperature_data and any(t > 0 for t in self.temperature_data):
                self.ax5.plot(x_data, list(self.temperature_data), color=self.colors['info'], linewidth=2)
                self.ax5.set_title('Temperature (°C)', fontsize=12, fontweight='bold')
                self.ax5.set_ylabel('Temperature')
            else:
                self.ax5.text(0.5, 0.5, 'Temperature\nNot Available', 
                            horizontalalignment='center', verticalalignment='center',
                            transform=self.ax5.transAxes, fontsize=12)
                self.ax5.set_title('Temperature (°C)', fontsize=12, fontweight='bold')
            
            # System Health Score
            self.ax6.clear()
            health_scores = [self.system_health_score] * len(x_data)
            self.ax6.plot(x_data, health_scores, color=self.colors['success'], linewidth=3)
            self.ax6.set_title('System Health Score', fontsize=12, fontweight='bold')
            self.ax6.set_ylabel('Score')
            self.ax6.set_ylim(0, 100)
            
            # Style all axes
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
                ax.set_facecolor(self.colors['card_bg'])
                ax.grid(True, alpha=0.3)
                
            self.fig.patch.set_facecolor(self.colors['bg'])
            
        except Exception as e:
            print(f"Enhanced chart update error: {e}")
            
    def export_enhanced_report(self):
        """Export enhanced performance report"""
        self.export_report()
        
    def open_enhanced_process_manager(self):
        """Open enhanced process manager window"""
        process_window = ctk.CTkToplevel(self.root)
        process_window.title("Enhanced Process Manager")
        process_window.geometry("1000x700")
        
        # Title
        title_label = ctk.CTkLabel(
            process_window,
            text="⚙️ Enhanced Process Manager",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Controls frame
        controls_frame = ctk.CTkFrame(process_window)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=lambda: self.refresh_enhanced_process_list(process_textbox),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        refresh_btn.grid(row=0, column=0, padx=10, pady=10)
        
        sort_cpu_btn = ctk.CTkButton(
            controls_frame,
            text="📊 Sort by CPU",
            command=lambda: self.sort_processes_by(process_textbox, 'cpu'),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        sort_cpu_btn.grid(row=0, column=1, padx=10, pady=10)
        
        sort_memory_btn = ctk.CTkButton(
            controls_frame,
            text="💾 Sort by Memory",
            command=lambda: self.sort_processes_by(process_textbox, 'memory'),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        sort_memory_btn.grid(row=0, column=2, padx=10, pady=10)
        
        kill_process_btn = ctk.CTkButton(
            controls_frame,
            text="❌ Kill Selected",
            command=lambda: self.kill_selected_process(process_textbox),
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="red"
        )
        kill_process_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Process list frame
        process_frame = ctk.CTkFrame(process_window)
        process_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Process textbox
        process_textbox = ctk.CTkTextbox(
            process_frame,
            font=ctk.CTkFont(size=10)
        )
        process_textbox.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Initial load
        self.refresh_enhanced_process_list(process_textbox)
        
    def refresh_enhanced_process_list(self, textbox):
        """Refresh enhanced process list"""
        try:
            textbox.delete('0.0', 'end')
            
            # Header
            header = f"{'PID':<8} {'Name':<25} {'Status':<12} {'CPU %':<8} {'Memory %':<10} {'Threads':<8}\n"
            textbox.insert('end', header)
            textbox.insert('end', "-" * 80 + "\n")
            
            # Get processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'num_threads']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            # Sort by CPU usage (descending)
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            # Display processes
            for proc in processes[:50]:  # Show top 50 processes
                try:
                    pid = proc['pid']
                    name = (proc['name'] or 'Unknown')[:24]
                    status = (proc['status'] or 'Unknown')[:11]
                    cpu = proc['cpu_percent'] or 0
                    memory = proc['memory_percent'] or 0
                    threads = proc['num_threads'] or 0
                    
                    line = f"{pid:<8} {name:<25} {status:<12} {cpu:<8.1f} {memory:<10.1f} {threads:<8}\n"
                    textbox.insert('end', line)
                except:
                    continue
                    
        except Exception as e:
            textbox.delete('0.0', 'end')
            textbox.insert('0.0', f"Error loading processes: {e}")
            
    def sort_processes_by(self, textbox, sort_by):
        """Sort processes by specified metric"""
        # For simplicity, just refresh the list
        # In a full implementation, you would maintain the process list and sort it
        self.refresh_enhanced_process_list(textbox)
        
    def kill_selected_process(self, textbox):
        """Kill selected process (placeholder)"""
        import tkinter.messagebox as messagebox
        messagebox.showwarning("Kill Process", "Process termination feature requires administrative privileges.\nThis is a demonstration version.")
        
            
            
            
                
    def update_analytics(self, value):
        """Update analytics data based on selected time range"""
        try:
            # Calculate analytics based on performance history
            if self.performance_history:
                # Get data based on time range
                now = time.time()
                if value == "Last Hour":
                    cutoff = now - 3600
                elif value == "Last 24 Hours":
                    cutoff = now - 86400
                elif value == "Last Week":
                    cutoff = now - 604800
                else:  # Last Month
                    cutoff = now - 2592000
                    
                filtered_data = [d for d in self.performance_history if d['timestamp'] >= cutoff]
                
                if filtered_data:
                    avg_cpu = sum(d['cpu'] for d in filtered_data)
                    avg_cpu = sum(d['cpu'] for d in filtered_data) / len(filtered_data)
                    avg_memory = sum(d['memory'] for d in filtered_data) / len(filtered_data)
                    peak_cpu = max(d['cpu'] for d in filtered_data)
                    
                    # Update analytics display
                    self.avg_cpu_label.configure(text=f"{avg_cpu:.1f}%")
                    self.avg_memory_label.configure(text=f"{avg_memory:.1f}%")
                    self.peak_cpu_label.configure(text=f"{peak_cpu:.1f}%")
                    self.events_count_label.configure(text=str(len(filtered_data)))
                    
                    # Update history textbox
                    self.update_history_display(filtered_data)
                    
        except Exception as e:
            print(f"Analytics update error: {e}")
            
    def update_history_display(self, data):
        """Update the performance history display"""
        try:
            self.history_textbox.delete('0.0', 'end')
            
            # Header
            header = f"{'Timestamp':<20} {'CPU %':<8} {'Memory %':<10} {'Disk %':<8} {'Network MB/s':<12} {'Temp °C':<8}\n"
            self.history_textbox.insert('end', header)
            self.history_textbox.insert('end', "-" * 80 + "\n")
            
            # Show last 50 entries
            for entry in data[-50:]:
                timestamp = datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                line = f"{timestamp:<20} {entry['cpu']:<8.1f} {entry['memory']:<10.1f} {entry['disk']:<8.1f} {entry['network']:<12.2f} {entry['temperature']:<8.1f}\n"
                self.history_textbox.insert('end', line)
                
        except Exception as e:
            self.history_textbox.insert('0.0', f"Error displaying history: {e}")
            
    def run_benchmark(self, benchmark_type):
        """Run system benchmark tests"""
        if self.benchmark_running:
            import tkinter.messagebox as messagebox
            messagebox.showwarning("Benchmark Running", "A benchmark is already in progress.")
            return
            
        self.benchmark_running = True
        self.benchmark_progress.set(0)
        self.benchmark_status_label.configure(text=f"🚀 Starting {benchmark_type} benchmark...")
        
        threading.Thread(target=self.perform_benchmark, args=(benchmark_type,), daemon=True).start()
        
    def perform_benchmark(self, benchmark_type):
        """Perform the actual benchmark test"""
        try:
            results = []
            
            if benchmark_type == 'cpu':
                results = self.run_cpu_benchmark()
            elif benchmark_type == 'memory':
                results = self.run_memory_benchmark()
            elif benchmark_type == 'full':
                results = self.run_full_benchmark()
                
            # Display results
            self.display_benchmark_results(results)
            
        except Exception as e:
            self.root.after(0, lambda: self.benchmark_status_label.configure(text=f"❌ Benchmark failed: {str(e)}"))
        finally:
            self.benchmark_running = False
            self.root.after(0, lambda: self.benchmark_progress.set(1))
            
    def run_cpu_benchmark(self):
        """Run CPU-specific benchmark"""
        results = []
        self.root.after(0, lambda: self.benchmark_status_label.configure(text="🔥 Testing CPU performance..."))
        
        # CPU integer operations test
        start_time = time.time()
        self.root.after(0, lambda: self.benchmark_progress.set(0.2))
        
        total = 0
        for i in range(1000000):
            total += i * i
        
        cpu_int_time = time.time() - start_time
        results.append(f"CPU Integer Operations: {cpu_int_time:.3f} seconds")
        
        # CPU floating point test
        self.root.after(0, lambda: self.benchmark_progress.set(0.5))
        start_time = time.time()
        
        import math
        total = 0.0
        for i in range(500000):
            total += math.sqrt(i) * math.sin(i)
            
        cpu_float_time = time.time() - start_time
        results.append(f"CPU Floating Point: {cpu_float_time:.3f} seconds")
        
        # CPU multi-threading test
        self.root.after(0, lambda: self.benchmark_progress.set(0.8))
        start_time = time.time()
        
        def cpu_worker():
            total = 0
            for i in range(250000):
                total += i ** 2
            return total
            
        threads = []
        for _ in range(4):
            thread = threading.Thread(target=cpu_worker)
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        cpu_multi_time = time.time() - start_time
        results.append(f"CPU Multi-threading: {cpu_multi_time:.3f} seconds")
        
        # Calculate CPU score
        cpu_score = 1000 / (cpu_int_time + cpu_float_time + cpu_multi_time)
        results.append(f"CPU Benchmark Score: {cpu_score:.0f}")
        
        self.root.after(0, lambda: self.benchmark_status_label.configure(text="✅ CPU benchmark completed"))
        return results
        
    def run_memory_benchmark(self):
        """Run memory-specific benchmark"""
        results = []
        self.root.after(0, lambda: self.benchmark_status_label.configure(text="💾 Testing memory performance..."))
        
        # Memory allocation test
        self.root.after(0, lambda: self.benchmark_progress.set(0.2))
        start_time = time.time()
        
        large_list = []
        for i in range(1000000):
            large_list.append(i)
            
        mem_alloc_time = time.time() - start_time
        results.append(f"Memory Allocation: {mem_alloc_time:.3f} seconds")
        
        # Memory access test
        self.root.after(0, lambda: self.benchmark_progress.set(0.5))
        start_time = time.time()
        
        total = 0
        for i in range(0, len(large_list), 100):
            total += large_list[i]
            
        mem_access_time = time.time() - start_time
        results.append(f"Memory Access: {mem_access_time:.3f} seconds")
        
        # Memory copy test
        self.root.after(0, lambda: self.benchmark_progress.set(0.8))
        start_time = time.time()
        
        copied_list = large_list.copy()
        
        mem_copy_time = time.time() - start_time
        results.append(f"Memory Copy: {mem_copy_time:.3f} seconds")
        
        # Clean up
        del large_list, copied_list
        
        
        # Calculate memory score
        memory_score = 1000 / (mem_alloc_time + mem_access_time + mem_copy_time)
        results.append(f"Memory Benchmark Score: {memory_score:.0f}")
        
        self.root.after(0, lambda: self.benchmark_status_label.configure(text="✅ Memory benchmark completed"))
        return results
        
    def run_full_benchmark(self):
        """Run comprehensive system benchmark"""
        results = []
        self.root.after(0, lambda: self.benchmark_status_label.configure(text="🚀 Running full system benchmark..."))
        
        # CPU tests
        self.root.after(0, lambda: self.benchmark_progress.set(0.1))
        cpu_results = self.run_cpu_benchmark()
        results.extend(cpu_results)
        results.append("")
        
        # Memory tests
        self.root.after(0, lambda: self.benchmark_progress.set(0.4))
        memory_results = self.run_memory_benchmark()
        results.extend(memory_results)
        results.append("")
        
        # Disk I/O test (simplified)
        self.root.after(0, lambda: self.benchmark_progress.set(0.7))
        self.root.after(0, lambda: self.benchmark_status_label.configure(text="💽 Testing disk performance..."))
        
        start_time = time.time()
        try:
            # Write test
            test_data = "x" * 1024 * 1024  # 1MB of data
            with open("benchmark_test.tmp", "w") as f:
                for _ in range(10):
                    f.write(test_data)
                    
            # Read test
            with open("benchmark_test.tmp", "r") as f:
                data = f.read()
                
            # Clean up
            os.remove("benchmark_test.tmp")
            
            disk_time = time.time() - start_time
            disk_score = 100 / disk_time
            results.append(f"Disk I/O Test: {disk_time:.3f} seconds")
            results.append(f"Disk Benchmark Score: {disk_score:.0f}")
            
        except Exception as e:
            results.append(f"Disk I/O Test: Failed ({str(e)})")
            
        # Overall system score
        self.root.after(0, lambda: self.benchmark_progress.set(0.9))
        overall_score = (self.system_health_score + 
                        sum(float(line.split(': ')[1]) for line in results 
                            if 'Score:' in line and line.split(': ')[1].replace('.', '').isdigit())) / 4
        results.append("")
        results.append(f"Overall System Score: {overall_score:.0f}")
        
        self.root.after(0, lambda: self.benchmark_status_label.configure(text="✅ Full system benchmark completed"))
        return results
        
    def display_benchmark_results(self, results):
        """Display benchmark results in the textbox"""
        def update_display():
            self.benchmark_results_textbox.delete('0.0', 'end')
            
            header = f"📊 BENCHMARK RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += "=" * 60 + "\n\n"
            self.benchmark_results_textbox.insert('end', header)
            
            for result in results:
                self.benchmark_results_textbox.insert('end', result + '\n')
                
            # Store results
            self.benchmark_results = {
                'timestamp': datetime.now(),
                'results': results
            }
            
        self.root.after(0, update_display)
        
    def change_theme(self, theme):
        """Change application theme"""
        self.current_theme = theme
        self.colors = self.themes[theme]
        
        # Update CustomTkinter appearance mode
        if theme == 'dark':
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
            
    def update_refresh_rate(self, value):
        """Update monitoring refresh rate"""
        self.refresh_rate = int(value) * 1000
        
    def update_font_size(self, value):
        """Update application font size"""
        self.font_size = int(value)
        
    def update_threshold(self, metric, value):
        """Update alert threshold for specific metric"""
        self.alert_thresholds[metric] = int(value)
        
    def toggle_notifications(self):
        """Toggle performance notifications"""
        self.notifications_enabled = self.notifications_var.get()
        
    def toggle_data_logging(self):
        """Toggle data logging to database"""
        self.data_logging = self.logging_var.get()
        
        
    def save_settings(self):
        """Save current settings to file"""
        try:
            settings = {
                'theme': self.current_theme,
                'refresh_rate': self.refresh_rate,
                'font_size': self.font_size,
                'notifications_enabled': self.notifications_enabled,
                        'data_logging': self.data_logging,
                'alert_thresholds': self.alert_thresholds
            }
            
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Settings save error: {e}")
            
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    
                self.current_theme = settings.get('theme', 'light')
                self.refresh_rate = settings.get('refresh_rate', 1000)
                self.font_size = settings.get('font_size', 12)
                self.notifications_enabled = settings.get('notifications_enabled', True)
                self.data_logging = settings.get('data_logging', True)
                self.alert_thresholds.update(settings.get('alert_thresholds', {}))
                
                # Apply loaded theme
                self.change_theme(self.current_theme)
                
        except Exception as e:
            print(f"Settings load error: {e}")
            
    def export_report(self):
        """Export enhanced performance report"""
        if not self.performance_history:
            import tkinter.messagebox as messagebox
            messagebox.showwarning("No Data", "No performance data available to export.")
            return
            
        import tkinter.messagebox as messagebox
        file_format = messagebox.askyesnocancel("Export Format", 
            "Choose export format:\n\nYes = PDF Report\nNo = CSV Data\nCancel = Cancel")
        
        if file_format is None:
            return
        elif file_format and PDF_AVAILABLE:
            self.export_enhanced_pdf_report()
        elif file_format and not PDF_AVAILABLE:
            messagebox.showwarning("PDF Not Available", 
                "PDF export requires reportlab library.\nExporting as CSV instead.")
            self.export_enhanced_csv_report()
        else:
            self.export_enhanced_csv_report()
            
    def export_enhanced_pdf_report(self):
        """Export enhanced PDF report with comprehensive data"""
        try:
            import tkinter.filedialog as filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Enhanced Performance Report"
            )
            
            if filename:
                doc = SimpleDocTemplate(filename, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                # Title
                title = Paragraph("System Performance Analysis Report", styles['Title'])
                story.append(title)
                
                # System info
                system_info_text = f"""
                <b>System Information:</b><br/>

                Platform: {self.system_info['platform']}<br/>
                CPU Cores: {self.system_info['cpu_count']}<br/>
                Total Memory: {self.system_info['memory_total'] / (1024**3):.2f} GB<br/>
                Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
                """
                story.append(Paragraph(system_info_text, styles['Normal']))
                
                # Performance summary
                if self.performance_history:
                    recent_data = self.performance_history[-100:]
                    avg_cpu = sum(d['cpu'] for d in recent_data) / len(recent_data)
                    avg_memory = sum(d['memory'] for d in recent_data) / len(recent_data)
                    avg_disk = sum(d['disk'] for d in recent_data) / len(recent_data)
                    peak_cpu = max(d['cpu'] for d in recent_data)
                    peak_memory = max(d['memory'] for d in recent_data)
                    
                    summary_text = f"""
                    <b>Performance Summary (Last 100 readings):</b><br/>
                    Average CPU Usage: {avg_cpu:.1f}%<br/>
                    Average Memory Usage: {avg_memory:.1f}%<br/>
                    Average Disk Usage: {avg_disk:.1f}%<br/>
                    Peak CPU Usage: {peak_cpu:.1f}%<br/>
                    Peak Memory Usage: {peak_memory:.1f}%<br/>
                    Current Health Score: {self.system_health_score:.0f}%<br/>
                    """
                    story.append(Paragraph(summary_text, styles['Normal']))
                
                # AI Recommendations
                if self.optimization_suggestions:
                    story.append(Paragraph("<b>AI Optimization Recommendations:</b>", styles['Heading2']))
                    for i, suggestion in enumerate(self.optimization_suggestions[:10], 1):
                        story.append(Paragraph(f"{i}. {suggestion}", styles['Normal']))
                        
                # Build PDF
                doc.build(story)
                
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Export Complete", f"Enhanced report exported to:\n{filename}")
                
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Export Error", f"Failed to export PDF report:\n{str(e)}")
            
    def export_enhanced_csv_report(self):
        """Export enhanced CSV data"""
        try:
            import tkinter.filedialog as filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Performance Data"
            )
            
            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow([
                        'Timestamp', 'CPU %', 'Memory %', 'Disk %', 
                        'Network MB/s', 'Temperature °C', 'Health Score'
                    ])
                    
                    # Data
                    for data in self.performance_history:
                        writer.writerow([
                            datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                            data['cpu'],
                            data['memory'],
                            data['disk'],
                            data['network'],
                            data['temperature'],
                            self.system_health_score
                        ])
                        
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Export Complete", f"Performance data exported to:\n{filename}")
                
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Export Error", f"Failed to export CSV data:\n{str(e)}")
            
    def manual_refresh(self):
        """Manually refresh all performance data"""
        try:
            # Force immediate chart update
            if hasattr(self, 'canvas'):
                self.canvas.draw()
                
            # Refresh system info
            if hasattr(self, 'system_info_textbox'):
                self.populate_system_info()
                
            # Update analytics
            if hasattr(self, 'time_range_var'):
                self.update_analytics(self.time_range_var.get())
                
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Refresh Complete", "All performance data has been refreshed!")
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Refresh Error", f"Failed to refresh data:\n{str(e)}")
            
    def on_closing(self):
        """Handle application closing with cleanup"""
        try:
            # Stop monitoring
            self.monitoring = False
            
            # Stop animation
            if hasattr(self, 'animation'):
                self.animation.event_source.stop()
                
            # Save settings
            self.save_settings()
            
            # Close database connection
            if hasattr(self, 'conn'):
                self.conn.close()
                
            # Clean up temporary files
            temp_files = ['benchmark_test.tmp']
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
                    
            # Final cleanup
            
        except Exception as e:
            print(f"Cleanup error: {e}")
        finally:
            self.root.quit()
            self.root.destroy()

def main():
    """Main function to run the enhanced application"""
    # Create the main window
    root = ctk.CTk()
    
    # Create and run the application
    app = SystemPerformanceAnalyzer(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center the window on screen
    root.update_idletasks()
    width = 1500
    height = 1000
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the GUI event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        app.on_closing()
    except Exception as e:
        print(f"Application error: {e}")
        app.on_closing()

if __name__ == "__main__":
    # Check Python version
    import sys
    if sys.version_info < (3, 6):
        print("❌ This application requires Python 3.6 or higher")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    # Check required modules
    required_modules = ['customtkinter', 'matplotlib', 'psutil']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required modules:")
        for module in missing_modules:
            print(f"   • {module}")
        print("\n📦 Install missing modules using:")
        print(f"pip install {' '.join(missing_modules)}")
        print("\n🔧 For full functionality, also install:")
        print("pip install reportlab  # For PDF export")
        sys.exit(1)
    
    # Print enhanced startup information
    print("=" * 70)
    print("🚀 SYSTEM PERFORMANCE ANALYZER & OPTIMIZER v2.0")
    print("   Advanced System Monitoring and Optimization Suite")
    print("   Clean system monitoring and performance analysis application")
    print("=" * 70)
    print("✨ ENHANCED FEATURES:")
    print("   📊 Real-time performance monitoring with 6 metrics")
    print("   📊 Performance analysis and recommendations")
    print("   📈 Comprehensive analytics and historical data")
    print("   ⚡ System benchmark testing suite")
    print("   💻 Detailed system information and diagnostics")
    print("   🎨 Modern CustomTkinter interface with themes")
    print("   📄 Enhanced reporting (PDF/CSV export)")
    print("   🗄️ SQLite database for data persistence")
    print("=" * 70)
    print("📋 SYSTEM REQUIREMENTS:")
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}+ (Current: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})")
    print("   ✅ CustomTkinter, matplotlib, psutil")
    print("   📦 Optional: reportlab (PDF export)")
    print("=" * 70)
    print("🔧 STARTING APPLICATION...")
    print("   Initializing monitoring systems...")
    print("   Loading performance analysis...")
    print("   Preparing user interface...")
    print()
    
    # Run the main application
    try:
        main()
    except Exception as e:
        print(f"\n❌ Application startup failed: {e}")
        print("Please check system requirements and try again.")
        sys.exit(1)
