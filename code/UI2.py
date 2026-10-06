import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import platform
import threading
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from collections import deque
import subprocess
import sys

class SystemPerformanceAnalyzer:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_styles()
        self.create_main_interface()
        self.start_monitoring()
        
    def setup_window(self):
        """Configure the main window for 13-inch Mac"""
        self.root.title("System Performance Analyzer - Architechs")
        
        # Optimized for 13-inch MacBook (1440x900 or 1280x800)
        window_width = 1200
        window_height = 800
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)
        
    def setup_variables(self):
        """Initialize monitoring variables"""
        self.monitoring = False
        self.cpu_data = deque(maxlen=50)
        self.memory_data = deque(maxlen=50)
        self.disk_data = deque(maxlen=50)
        self.network_data = deque(maxlen=50)
        self.time_data = deque(maxlen=50)
        
    def create_styles(self):
        """Create modern styling for the application"""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Header style
        style.configure('Header.TLabel', 
                       font=('SF Pro Display', 24, 'bold'),
                       background='#f0f0f0',
                       foreground='#1d1d1f')
        
        # Subheader style
        style.configure('Subheader.TLabel',
                       font=('SF Pro Display', 14, 'bold'),
                       background='#f0f0f0',
                       foreground='#424242')
        
        # Info style
        style.configure('Info.TLabel',
                       font=('SF Pro Text', 11),
                       background='#f0f0f0',
                       foreground='#666666')
        
        # Card style
        style.configure('Card.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=1)
        
        # Button style
        style.configure('Modern.TButton',
                       font=('SF Pro Text', 11),
                       padding=(20, 10))
        
    def create_main_interface(self):
        """Create the main user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Header section
        self.create_header()
        
        # Content area
        self.create_content_area()
        
        # Team info section
        self.create_team_info()
        
    def create_header(self):
        """Create the header section"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="System Performance Analyzer",
                               style='Header.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # System info
        system_info = f"{platform.system()} {platform.release()} | {platform.processor()}"
        info_label = ttk.Label(header_frame,
                              text=system_info,
                              style='Info.TLabel')
        info_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=0, column=1, rowspan=2, sticky=tk.E)
        
        self.start_button = ttk.Button(button_frame,
                                      text="Start Monitoring",
                                      command=self.toggle_monitoring,
                                      style='Modern.TButton')
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.refresh_button = ttk.Button(button_frame,
                                        text="Refresh",
                                        command=self.refresh_data,
                                        style='Modern.TButton')
        self.refresh_button.grid(row=0, column=1)
        
    def create_content_area(self):
        """Create the main content area with tabs"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Overview tab
        self.create_overview_tab()
        
        # CPU tab
        self.create_cpu_tab()
        
        # Memory tab
        self.create_memory_tab()
        
        # Disk tab
        self.create_disk_tab()
        
        # Network tab
        self.create_network_tab()
        
        # Process tab
        self.create_process_tab()
        
    def create_overview_tab(self):
        """Create the overview tab"""
        overview_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(overview_frame, text="Overview")
        
        # Configure grid
        overview_frame.columnconfigure((0, 1), weight=1)
        overview_frame.rowconfigure((0, 1), weight=1)
        
        # CPU card
        self.cpu_card = self.create_metric_card(overview_frame, "CPU Usage", 0, 0)
        
        # Memory card
        self.memory_card = self.create_metric_card(overview_frame, "Memory Usage", 0, 1)
        
        # Disk card
        self.disk_card = self.create_metric_card(overview_frame, "Disk Usage", 1, 0)
        
        # Network card
        self.network_card = self.create_metric_card(overview_frame, "Network I/O", 1, 1)
        
    def create_metric_card(self, parent, title, row, column):
        """Create a metric card widget"""
        card_frame = ttk.LabelFrame(parent, text=title, padding="15")
        card_frame.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), 
                       padx=10, pady=10)
        
        # Value label
        value_label = ttk.Label(card_frame, text="0%", 
                               font=('SF Pro Display', 32, 'bold'),
                               foreground='#007AFF')
        value_label.grid(row=0, column=0, pady=(0, 10))
        
        # Progress bar
        progress = ttk.Progressbar(card_frame, mode='determinate', length=200)
        progress.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Details label
        details_label = ttk.Label(card_frame, text="", 
                                 font=('SF Pro Text', 10),
                                 foreground='#666666')
        details_label.grid(row=2, column=0, pady=(10, 0))
        
        return {
            'frame': card_frame,
            'value': value_label,
            'progress': progress,
            'details': details_label
        }
        
    def create_cpu_tab(self):
        """Create the CPU monitoring tab"""
        cpu_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(cpu_frame, text="CPU")
        
        # Configure grid
        cpu_frame.columnconfigure(0, weight=1)
        cpu_frame.rowconfigure(1, weight=1)
        
        # CPU info frame
        info_frame = ttk.LabelFrame(cpu_frame, text="CPU Information", padding="15")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.cpu_info_labels = {}
        info_items = ['Physical cores', 'Logical cores', 'Current frequency', 'Max frequency']
        
        for i, item in enumerate(info_items):
            ttk.Label(info_frame, text=f"{item}:").grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=(0, 10))
            label = ttk.Label(info_frame, text="Loading...")
            label.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=(0, 30))
            self.cpu_info_labels[item] = label
        
        # CPU graph frame
        graph_frame = ttk.LabelFrame(cpu_frame, text="CPU Usage Over Time", padding="10")
        graph_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create matplotlib figure
        self.cpu_fig = Figure(figsize=(8, 4), dpi=100)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=graph_frame)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.setup_cpu_graph()
        
    def create_memory_tab(self):
        """Create the memory monitoring tab"""
        memory_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(memory_frame, text="Memory")
        
        # Configure grid
        memory_frame.columnconfigure(0, weight=1)
        memory_frame.rowconfigure(1, weight=1)
        
        # Memory info frame
        info_frame = ttk.LabelFrame(memory_frame, text="Memory Information", padding="15")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.memory_info_labels = {}
        info_items = ['Total', 'Available', 'Used', 'Percentage']
        
        for i, item in enumerate(info_items):
            ttk.Label(info_frame, text=f"{item}:").grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=(0, 10))
            label = ttk.Label(info_frame, text="Loading...")
            label.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=(0, 30))
            self.memory_info_labels[item] = label
        
        # Memory graph frame
        graph_frame = ttk.LabelFrame(memory_frame, text="Memory Usage Over Time", padding="10")
        graph_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create matplotlib figure
        self.memory_fig = Figure(figsize=(8, 4), dpi=100)
        self.memory_ax = self.memory_fig.add_subplot(111)
        self.memory_canvas = FigureCanvasTkAgg(self.memory_fig, master=graph_frame)
        self.memory_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.setup_memory_graph()
        
    def create_disk_tab(self):
        """Create the disk monitoring tab"""
        disk_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(disk_frame, text="Disk")
        
        # Configure grid
        disk_frame.columnconfigure(0, weight=1)
        disk_frame.rowconfigure(1, weight=1)
        
        # Disk info frame
        info_frame = ttk.LabelFrame(disk_frame, text="Disk Information", padding="15")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Disk usage treeview
        self.disk_tree = ttk.Treeview(info_frame, columns=('Total', 'Used', 'Free', 'Percentage'), show='tree headings', height=6)
        self.disk_tree.heading('#0', text='Device')
        self.disk_tree.heading('Total', text='Total')
        self.disk_tree.heading('Used', text='Used')
        self.disk_tree.heading('Free', text='Free')
        self.disk_tree.heading('Percentage', text='Usage %')
        
        # Configure column widths
        self.disk_tree.column('#0', width=150)
        self.disk_tree.column('Total', width=100)
        self.disk_tree.column('Used', width=100)
        self.disk_tree.column('Free', width=100)
        self.disk_tree.column('Percentage', width=100)
        
        self.disk_tree.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Disk I/O graph frame
        graph_frame = ttk.LabelFrame(disk_frame, text="Disk I/O Activity", padding="10")
        graph_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create matplotlib figure
        self.disk_fig = Figure(figsize=(8, 4), dpi=100)
        self.disk_ax = self.disk_fig.add_subplot(111)
        self.disk_canvas = FigureCanvasTkAgg(self.disk_fig, master=graph_frame)
        self.disk_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.setup_disk_graph()
        
    def create_network_tab(self):
        """Create the network monitoring tab"""
        network_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(network_frame, text="Network")
        
        # Configure grid
        network_frame.columnconfigure(0, weight=1)
        network_frame.rowconfigure(1, weight=1)
        
        # Network info frame
        info_frame = ttk.LabelFrame(network_frame, text="Network Information", padding="15")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.network_info_labels = {}
        info_items = ['Bytes sent', 'Bytes received', 'Packets sent', 'Packets received']
        
        for i, item in enumerate(info_items):
            ttk.Label(info_frame, text=f"{item}:").grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=(0, 10))
            label = ttk.Label(info_frame, text="Loading...")
            label.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=(0, 30))
            self.network_info_labels[item] = label
        
        # Network graph frame
        graph_frame = ttk.LabelFrame(network_frame, text="Network Activity", padding="10")
        graph_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create matplotlib figure
        self.network_fig = Figure(figsize=(8, 4), dpi=100)
        self.network_ax = self.network_fig.add_subplot(111)
        self.network_canvas = FigureCanvasTkAgg(self.network_fig, master=graph_frame)
        self.network_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.setup_network_graph()
        
    def create_process_tab(self):
        """Create the process monitoring tab"""
        process_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(process_frame, text="Processes")
        
        # Configure grid
        process_frame.columnconfigure(0, weight=1)
        process_frame.rowconfigure(1, weight=1)
        
        # Controls frame
        controls_frame = ttk.Frame(process_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(controls_frame, text="Sort by:").grid(row=0, column=0, padx=(0, 10))
        
        self.sort_var = tk.StringVar(value="cpu_percent")
        sort_combo = ttk.Combobox(controls_frame, textvariable=self.sort_var,
                                 values=["cpu_percent", "memory_percent", "name"],
                                 state="readonly", width=15)
        sort_combo.grid(row=0, column=1, padx=(0, 10))
        sort_combo.bind('<<ComboboxSelected>>', self.update_process_list)
        
        ttk.Button(controls_frame, text="Refresh", 
                  command=self.update_process_list,
                  style='Modern.TButton').grid(row=0, column=2)
        
        # Process treeview
        process_container = ttk.Frame(process_frame)
        process_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        process_container.columnconfigure(0, weight=1)
        process_container.rowconfigure(0, weight=1)
        
        self.process_tree = ttk.Treeview(process_container, 
                                        columns=('PID', 'CPU%', 'Memory%', 'Status'),
                                        show='tree headings')
        self.process_tree.heading('#0', text='Process Name')
        self.process_tree.heading('PID', text='PID')
        self.process_tree.heading('CPU%', text='CPU %')
        self.process_tree.heading('Memory%', text='Memory %')
        self.process_tree.heading('Status', text='Status')
        
        # Configure column widths
        self.process_tree.column('#0', width=250)
        self.process_tree.column('PID', width=80)
        self.process_tree.column('CPU%', width=80)
        self.process_tree.column('Memory%', width=100)
        self.process_tree.column('Status', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(process_container, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_team_info(self):
        """Create the team information section"""
        team_frame = ttk.LabelFrame(self.main_frame, text="Team Information", padding="15")
        team_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Team header
        team_header = ttk.Label(team_frame, text="Team Architechs - SE(OS)-VI-T250", 
                               style='Subheader.TLabel')
        team_header.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Team members
        members = [
            ("Team Leader", "Harshit Jasuja", "220211228", "harshitjasuja70@gmail.com"),
            ("Member 2", "Shivendra Srivastava", "220211349", "shivendrasri999@gmail.com"),
            ("Member 3", "Yashika Dixit", "22022577", "yashikadixit1611@gmail.com")
        ]
        
        for i, (role, name, student_id, email) in enumerate(members):
            member_frame = ttk.Frame(team_frame)
            member_frame.grid(row=i+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
            
            ttk.Label(member_frame, text=f"{role}: {name}", 
                     font=('SF Pro Text', 11, 'bold')).grid(row=0, column=0, sticky=tk.W)
            ttk.Label(member_frame, text=f"ID: {student_id} | Email: {email}",
                     style='Info.TLabel').grid(row=1, column=0, sticky=tk.W)
    
    def setup_cpu_graph(self):
        """Setup the CPU usage graph"""
        self.cpu_ax.set_title('CPU Usage (%)', fontsize=12, fontweight='bold')
        self.cpu_ax.set_ylabel('Usage (%)')
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.grid(True, alpha=0.3)
        self.cpu_line, = self.cpu_ax.plot([], [], 'b-', linewidth=2, label='CPU Usage')
        self.cpu_ax.legend()
        
    def setup_memory_graph(self):
        """Setup the memory usage graph"""
        self.memory_ax.set_title('Memory Usage (%)', fontsize=12, fontweight='bold')
        self.memory_ax.set_ylabel('Usage (%)')
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.grid(True, alpha=0.3)
        self.memory_line, = self.memory_ax.plot([], [], 'g-', linewidth=2, label='Memory Usage')
        self.memory_ax.legend()
        
    def setup_disk_graph(self):
        """Setup the disk I/O graph"""
        self.disk_ax.set_title('Disk Usage (%)', fontsize=12, fontweight='bold')
        self.disk_ax.set_ylabel('Usage (%)')
        self.disk_ax.set_ylim(0, 100)
        self.disk_ax.grid(True, alpha=0.3)
        self.disk_line, = self.disk_ax.plot([], [], 'r-', linewidth=2, label='Disk Usage')
        self.disk_ax.legend()
        
    def setup_network_graph(self):
        """Setup the network activity graph"""
        self.network_ax.set_title('Network Activity (MB/s)', fontsize=12, fontweight='bold')
        self.network_ax.set_ylabel('Speed (MB/s)')
        self.network_ax.grid(True, alpha=0.3)
        self.network_sent_line, = self.network_ax.plot([], [], 'b-', linewidth=2, label='Sent')
        self.network_recv_line, = self.network_ax.plot([], [], 'r-', linewidth=2, label='Received')
        self.network_ax.legend()
        
    def toggle_monitoring(self):
        """Toggle the monitoring state"""
        if not self.monitoring:
            self.start_monitoring()
            self.start_button.configure(text="Stop Monitoring")
        else:
            self.stop_monitoring()
            self.start_button.configure(text="Start Monitoring")
            
    def start_monitoring(self):
        """Start the system monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop the system monitoring"""
        self.monitoring = False
        
    def monitor_loop(self):
        """Main monitoring loop"""
        last_net_io = psutil.net_io_counters()
        last_time = time.time()
        
        while self.monitoring:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                self.time_data.append(current_time)
                
                # CPU data
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_data.append(cpu_percent)
                
                # Memory data
                memory = psutil.virtual_memory()
                self.memory_data.append(memory.percent)
                
                # Disk data (using root partition)
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.disk_data.append(disk_percent)
                
                # Network data
                current_net_io = psutil.net_io_counters()
                current_time_stamp = time.time()
                
                time_delta = current_time_stamp - last_time
                if time_delta > 0:
                    bytes_sent_per_sec = (current_net_io.bytes_sent - last_net_io.bytes_sent) / time_delta
                    bytes_recv_per_sec = (current_net_io.bytes_recv - last_net_io.bytes_recv) / time_delta
                    
                    # Convert to MB/s
                    mb_sent = bytes_sent_per_sec / (1024 * 1024)
                    mb_recv = bytes_recv_per_sec / (1024 * 1024)
                    
                    self.network_data.append((mb_sent, mb_recv))
                else:
                    self.network_data.append((0, 0))
                
                last_net_io = current_net_io
                last_time = current_time_stamp
                
                # Update UI in main thread
                self.root.after(0, self.update_ui)
                
                time.sleep(1)  # Update every 1 second
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)
                
    def update_ui(self):
        """Update the user interface with current data"""
        if not self.cpu_data or not self.memory_data or not self.disk_data:
            return
            
        try:
            # Update overview cards
            cpu_current = self.cpu_data[-1] if self.cpu_data else 0
            memory_current = self.memory_data[-1] if self.memory_data else 0
            disk_current = self.disk_data[-1] if self.disk_data else 0
            
            # CPU card
            self.cpu_card['value'].config(text=f"{cpu_current:.1f}%")
            self.cpu_card['progress']['value'] = cpu_current
            self.cpu_card['details'].config(text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # Memory card
            memory = psutil.virtual_memory()
            self.memory_card['value'].config(text=f"{memory.percent:.1f}%")
            self.memory_card['progress']['value'] = memory.percent
            self.memory_card['details'].config(text=f"Used: {self.format_bytes(memory.used)} / {self.format_bytes(memory.total)}")
            
            # Disk card
            disk = psutil.disk_usage('/')
            self.disk_card['value'].config(text=f"{disk_current:.1f}%")
            self.disk_card['progress']['value'] = disk_current
            self.disk_card['details'].config(text=f"Used: {self.format_bytes(disk.used)} / {self.format_bytes(disk.total)}")
            
            # Network card
            if self.network_data:
                sent, recv = self.network_data[-1]
                total_speed = sent + recv
                self.network_card['value'].config(text=f"{total_speed:.2f} MB/s")
                self.network_card['progress']['value'] = min(total_speed * 10, 100)  # Scale for visualization
                self.network_card['details'].config(text=f"↑ {sent:.2f} MB/s | ↓ {recv:.2f} MB/s")
            
            # Update graphs
            self.update_graphs()
            
            # Update detailed info
            self.update_detailed_info()
            
        except Exception as e:
            print(f"UI update error: {e}")
            
    def update_graphs(self):
        """Update all graphs with current data"""
        try:
            # CPU graph
            if len(self.cpu_data) > 1:
                self.cpu_line.set_data(range(len(self.cpu_data)), list(self.cpu_data))
                self.cpu_ax.set_xlim(0, max(len(self.cpu_data)-1, 10))
                self.cpu_canvas.draw_idle()
            
            # Memory graph
            if len(self.memory_data) > 1:
                self.memory_line.set_data(range(len(self.memory_data)), list(self.memory_data))
                self.memory_ax.set_xlim(0, max(len(self.memory_data)-1, 10))
                self.memory_canvas.draw_idle()
            
            # Disk graph
            if len(self.disk_data) > 1:
                self.disk_line.set_data(range(len(self.disk_data)), list(self.disk_data))
                self.disk_ax.set_xlim(0, max(len(self.disk_data)-1, 10))
                self.disk_canvas.draw_idle()
            
            # Network graph
            if len(self.network_data) > 1:
                sent_data = [item[0] for item in self.network_data]
                recv_data = [item[1] for item in self.network_data]
                
                self.network_sent_line.set_data(range(len(sent_data)), sent_data)
                self.network_recv_line.set_data(range(len(recv_data)), recv_data)
                self.network_ax.set_xlim(0, max(len(self.network_data)-1, 10))
                
                # Auto-scale y-axis for network
                max_val = max(max(sent_data), max(recv_data)) if sent_data and recv_data else 1
                self.network_ax.set_ylim(0, max(max_val * 1.1, 1))
                self.network_canvas.draw_idle()
                
        except Exception as e:
            print(f"Graph update error: {e}")
            
    def update_detailed_info(self):
        """Update detailed information in tabs"""
        try:
            # CPU info
            cpu_freq = psutil.cpu_freq()
            if hasattr(self, 'cpu_info_labels'):
                self.cpu_info_labels['Physical cores'].config(text=str(psutil.cpu_count(logical=False)))
                self.cpu_info_labels['Logical cores'].config(text=str(psutil.cpu_count(logical=True)))
                self.cpu_info_labels['Current frequency'].config(text=f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A")
                self.cpu_info_labels['Max frequency'].config(text=f"{cpu_freq.max:.2f} MHz" if cpu_freq else "N/A")
            
            # Memory info
            memory = psutil.virtual_memory()
            if hasattr(self, 'memory_info_labels'):
                self.memory_info_labels['Total'].config(text=self.format_bytes(memory.total))
                self.memory_info_labels['Available'].config(text=self.format_bytes(memory.available))
                self.memory_info_labels['Used'].config(text=self.format_bytes(memory.used))
                self.memory_info_labels['Percentage'].config(text=f"{memory.percent:.1f}%")
            
            # Disk info
            self.update_disk_info()
            
            # Network info
            net_io = psutil.net_io_counters()
            if hasattr(self, 'network_info_labels'):
                self.network_info_labels['Bytes sent'].config(text=self.format_bytes(net_io.bytes_sent))
                self.network_info_labels['Bytes received'].config(text=self.format_bytes(net_io.bytes_recv))
                self.network_info_labels['Packets sent'].config(text=f"{net_io.packets_sent:,}")
                self.network_info_labels['Packets received'].config(text=f"{net_io.packets_recv:,}")
                
        except Exception as e:
            print(f"Detailed info update error: {e}")
            
    def update_disk_info(self):
        """Update disk information"""
        try:
            # Clear existing items
            for item in self.disk_tree.get_children():
                self.disk_tree.delete(item)
            
            # Get disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    
                    total = self.format_bytes(disk_usage.total)
                    used = self.format_bytes(disk_usage.used)
                    free = self.format_bytes(disk_usage.free)
                    percent = f"{(disk_usage.used / disk_usage.total) * 100:.1f}%"
                    
                    # Insert into treeview
                    self.disk_tree.insert('', 'end', 
                                         text=f"{partition.device} ({partition.fstype})",
                                         values=(total, used, free, percent))
                                         
                except PermissionError:
                    # Some partitions may not be accessible
                    self.disk_tree.insert('', 'end',
                                         text=f"{partition.device} (Access Denied)",
                                         values=("N/A", "N/A", "N/A", "N/A"))
                                         
        except Exception as e:
            print(f"Disk info update error: {e}")
            
    def update_process_list(self, event=None):
        """Update the process list"""
        try:
            # Clear existing items
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            
            # Get all processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes
            sort_key = self.sort_var.get()
            if sort_key in ['cpu_percent', 'memory_percent']:
                processes.sort(key=lambda x: x[sort_key] or 0, reverse=True)
            else:
                processes.sort(key=lambda x: x[sort_key] or "")
            
            # Insert top 50 processes
            for proc in processes[:50]:
                self.process_tree.insert('', 'end',
                                        text=proc['name'] or "Unknown",
                                        values=(
                                            proc['pid'],
                                            f"{proc['cpu_percent'] or 0:.1f}%",
                                            f"{proc['memory_percent'] or 0:.1f}%",
                                            proc['status'] or "Unknown"
                                        ))
                                        
        except Exception as e:
            print(f"Process list update error: {e}")
            
    def refresh_data(self):
        """Refresh all data manually"""
        try:
            # Update overview cards immediately
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.cpu_card['value'].config(text=f"{cpu_percent:.1f}%")
            self.cpu_card['progress']['value'] = cpu_percent
            
            self.memory_card['value'].config(text=f"{memory.percent:.1f}%")
            self.memory_card['progress']['value'] = memory.percent
            
            disk_percent = (disk.used / disk.total) * 100
            self.disk_card['value'].config(text=f"{disk_percent:.1f}%")
            self.disk_card['progress']['value'] = disk_percent
            
            # Update detailed info
            self.update_detailed_info()
            
            # Update process list
            self.update_process_list()
            
            # Show refresh confirmation
            self.root.after(100, lambda: self.show_notification("Data refreshed successfully!"))
            
        except Exception as e:
            print(f"Refresh error: {e}")
            self.show_notification(f"Refresh failed: {str(e)}", "error")
            
    def show_notification(self, message, msg_type="info"):
        """Show a notification message"""
        if msg_type == "error":
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Information", message)
            
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        try:
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.1f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.1f} PB"
        except:
            return "0 B"
            
    def on_closing(self):
        """Handle application closing"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        self.root.destroy()


class ModernButton(tk.Canvas):
    """Custom modern button widget"""
    def __init__(self, parent, text="", command=None, bg_color="#007AFF", 
                 hover_color="#0051D5", text_color="white", width=120, height=40):
        super().__init__(parent, width=width, height=height, highlightthickness=0)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
        # Draw button
        self.draw_button(text)
        
        # Bind events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def draw_button(self, text):
        """Draw the button with rounded corners"""
        self.delete("all")
        
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Draw rounded rectangle (simplified)
        self.create_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(),
                             fill=color, outline="", width=0)
        
        # Draw text
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2,
                        text=text, fill=self.text_color, 
                        font=('SF Pro Text', 11, 'normal'))
        
    def on_click(self, event):
        """Handle button click"""
        if self.command:
            self.command()
            
    def on_enter(self, event):
        """Handle mouse enter"""
        self.is_hovered = True
        self.draw_button(self.itemcget(self.find_all()[-1], "text"))
        
    def on_leave(self, event):
        """Handle mouse leave"""
        self.is_hovered = False
        self.draw_button(self.itemcget(self.find_all()[-1], "text"))


def main():
    """Main function to run the application"""
    # Check if required modules are available
    try:
        import psutil
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
    except ImportError as e:
        print(f"Required module not found: {e}")
        print("Please install required modules:")
        print("pip install psutil matplotlib")
        sys.exit(1)
    
    # Create main window
    root = tk.Tk()
    
    # Set app icon and other Mac-specific settings
    if platform.system() == "Darwin":  # macOS
        try:
            # Try to set the app icon (if available)
            root.tk.call('wm', 'iconbitmap', root._w, '-default')
        except:
            pass
    
    # Create application
    app = SystemPerformanceAnalyzer(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_closing()


if __name__ == "__main__":
    main()