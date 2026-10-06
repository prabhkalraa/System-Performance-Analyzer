import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import psutil
import platform
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

class SystemPerformanceAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("System Performance Analyzer")
        # Increase initial window size for better content display
        self.root.geometry("1200x800")
        self.root.minsize(900, 700)  # Set minimum size to prevent UI elements from overlapping
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Colors
        self.bg_color = "#f0f0f0"
        self.header_color = "#3a7ebf"
        self.accent_color = "#5294e2"
        
        # Configure style
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TButton", background=self.accent_color, foreground="white", font=("Arial", 10, "bold"))
        self.style.configure("TNotebook", background=self.bg_color)
        self.style.configure("TNotebook.Tab", padding=[15, 5], font=("Arial", 10, "bold"))  # Increase tab padding
        self.style.map("TButton", background=[("active", "#4584d2")])
        
        # Variables
        self.monitoring = False
        self.monitoring_thread = None
        self.cpu_history = []
        self.ram_history = []
        self.timestamps = []
        self.processes_data = []
        
        # Create main container with padding
        self.main_frame = ttk.Frame(self.root, padding=(15, 10))  # Add padding to main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_processes_tab()
        self.create_system_info_tab()
        self.create_optimization_tab()
        
        # Create status bar
        self.create_status_bar()
        
        # Initialize system info
        self.update_system_info()
        
    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))  # Increase bottom padding
        
        title_label = ttk.Label(header_frame, text="System Performance Analyzer", 
                              font=("Arial", 18, "bold"), foreground=self.header_color)  # Increased font size
        title_label.pack(side=tk.LEFT, padx=10)
        
        self.monitor_button = ttk.Button(header_frame, text="Start Monitoring", 
                                      command=self.toggle_monitoring, padding=(10, 5))  # Increased button padding
        self.monitor_button.pack(side=tk.RIGHT, padx=10)
        
    def create_dashboard_tab(self):
        dashboard_frame = ttk.Frame(self.notebook, padding=10)  # Add padding to frame
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Top metrics frame - use pack instead of grid for better responsiveness
        metrics_frame = ttk.Frame(dashboard_frame)
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a frame for each metric and pack them side by side
        # CPU usage
        cpu_frame = ttk.LabelFrame(metrics_frame, text="CPU Usage", padding=(10, 5))
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.cpu_usage_var = tk.StringVar(value="0%")
        cpu_usage_label = ttk.Label(cpu_frame, textvariable=self.cpu_usage_var, 
                                  font=("Arial", 24, "bold"), foreground=self.accent_color)
        cpu_usage_label.pack(padx=20, pady=10)
        
        self.cpu_progressbar = ttk.Progressbar(cpu_frame, length=150, mode="determinate")
        self.cpu_progressbar.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        # RAM usage
        ram_frame = ttk.LabelFrame(metrics_frame, text="RAM Usage", padding=(10, 5))
        ram_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.ram_usage_var = tk.StringVar(value="0%")
        ram_usage_label = ttk.Label(ram_frame, textvariable=self.ram_usage_var, 
                                  font=("Arial", 24, "bold"), foreground=self.accent_color)
        ram_usage_label.pack(padx=20, pady=10)
        
        self.ram_progressbar = ttk.Progressbar(ram_frame, length=150, mode="determinate")
        self.ram_progressbar.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        # Disk usage
        disk_frame = ttk.LabelFrame(metrics_frame, text="Disk Usage", padding=(10, 5))
        disk_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.disk_usage_var = tk.StringVar(value="0%")
        disk_usage_label = ttk.Label(disk_frame, textvariable=self.disk_usage_var, 
                                   font=("Arial", 24, "bold"), foreground=self.accent_color)
        disk_usage_label.pack(padx=20, pady=10)
        
        self.disk_progressbar = ttk.Progressbar(disk_frame, length=150, mode="determinate")
        self.disk_progressbar.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        # Graphs frame with more space
        graphs_frame = ttk.Frame(dashboard_frame)
        graphs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)  # Increased vertical padding
        
        # Create figure for plots with improved layout
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8), dpi=100)  # Higher resolution
        self.fig.tight_layout(pad=4.0)  # Increased padding between subplots
        self.fig.subplots_adjust(hspace=0.5)  # Increase space between plots
        
        # CPU history plot
        self.ax1.set_title("CPU Usage History", fontsize=12, fontweight='bold')
        self.ax1.set_ylabel("Usage %", fontsize=10)
        self.ax1.set_ylim(0, 100)
        self.ax1.grid(True, alpha=0.3)  # Make grid less prominent
        self.cpu_line, = self.ax1.plot([], [], 'b-', label="CPU %", linewidth=2)  # Thicker line
        self.ax1.legend(loc='upper right')
        
        # RAM history plot
        self.ax2.set_title("RAM Usage History", fontsize=12, fontweight='bold')
        self.ax2.set_xlabel("Time", fontsize=10)
        self.ax2.set_ylabel("Usage %", fontsize=10)
        self.ax2.set_ylim(0, 100)
        self.ax2.grid(True, alpha=0.3)  # Make grid less prominent
        self.ram_line, = self.ax2.plot([], [], 'g-', label="RAM %", linewidth=2)  # Thicker line
        self.ax2.legend(loc='upper right')
        
        # Add canvas to window
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_processes_tab(self):
        processes_frame = ttk.Frame(self.notebook, padding=10)  # Add padding
        self.notebook.add(processes_frame, text="Processes")
        
        # Control frame
        control_frame = ttk.Frame(processes_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        refresh_button = ttk.Button(control_frame, text="Refresh Processes", 
                                 command=self.update_processes_list, padding=(10, 5))  # Increased padding
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        end_process_button = ttk.Button(control_frame, text="End Selected Process", 
                                     command=self.end_selected_process, padding=(10, 5))  # Increased padding
        end_process_button.pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(processes_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 15))  # Increase vertical padding
        
        ttk.Label(search_frame, text="Search:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_processes())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)  # Wider search box
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Processes treeview in a frame with defined height
        tree_frame = ttk.Frame(processes_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("PID", "Name", "CPU %", "Memory %", "Status")
        self.processes_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)  # Set height
        
        # Set column headings and widths
        self.processes_tree.heading("PID", text="PID")
        self.processes_tree.heading("Name", text="Name")
        self.processes_tree.heading("CPU %", text="CPU %")
        self.processes_tree.heading("Memory %", text="Memory %")
        self.processes_tree.heading("Status", text="Status")
        
        # Configure column widths
        self.processes_tree.column("PID", width=80, anchor="center")
        self.processes_tree.column("Name", width=250, anchor="w")  # Left-align names
        self.processes_tree.column("CPU %", width=100, anchor="center")
        self.processes_tree.column("Memory %", width=100, anchor="center")
        self.processes_tree.column("Status", width=100, anchor="center")
        
        # Add scrollbars in a better layout
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.processes_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.processes_tree.xview)
        self.processes_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack scrollbars and treeview
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.processes_tree.pack(fill=tk.BOTH, expand=True)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial process list
        self.update_processes_list()
        
    def create_system_info_tab(self):
        system_frame = ttk.Frame(self.notebook, padding=10)  # Add padding
        self.notebook.add(system_frame, text="System Info")
        
        # Create system info area
        info_frame = ttk.LabelFrame(system_frame, text="System Information", padding=(10, 5))
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.system_info_text = scrolledtext.ScrolledText(
            info_frame, 
            wrap=tk.WORD,
            font=("Consolas", 10),  # Monospace font for better readability
            width=80, 
            height=20
        )
        self.system_info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.system_info_text.config(state=tk.DISABLED)
        
    def create_optimization_tab(self):
        optimization_frame = ttk.Frame(self.notebook, padding=10)  # Add padding
        self.notebook.add(optimization_frame, text="Optimization")
        
        # Quick actions frame
        actions_frame = ttk.LabelFrame(optimization_frame, text="Quick Actions", padding=(10, 5))
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create frames for each row to ensure uniform button layout
        row1_frame = ttk.Frame(actions_frame)
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        row2_frame = ttk.Frame(actions_frame)
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Row 1 buttons - evenly spaced
        clean_temp_btn = ttk.Button(row1_frame, text="Clean Temporary Files", 
                                 command=lambda: self.show_message("Cleaning temporary files..."),
                                 padding=(10, 5))  # Increased padding
        clean_temp_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        end_unused_btn = ttk.Button(row1_frame, text="End Unused Processes", 
                                  command=lambda: self.show_message("Ending unused processes..."),
                                  padding=(10, 5))  # Increased padding
        end_unused_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        disk_cleanup_btn = ttk.Button(row1_frame, text="Disk Cleanup", 
                                   command=lambda: self.show_message("Running disk cleanup..."),
                                   padding=(10, 5))  # Increased padding
        disk_cleanup_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Row 2 buttons - evenly spaced
        startup_btn = ttk.Button(row2_frame, text="Manage Startup Apps", 
                              command=lambda: self.show_message("Opening startup apps manager..."),
                              padding=(10, 5))  # Increased padding
        startup_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        memory_btn = ttk.Button(row2_frame, text="Optimize Memory", 
                             command=lambda: self.show_message("Optimizing memory usage..."),
                             padding=(10, 5))  # Increased padding
        memory_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        defrag_btn = ttk.Button(row2_frame, text="Defragment Disk", 
                             command=lambda: self.show_message("Starting disk defragmentation..."),
                             padding=(10, 5))  # Increased padding
        defrag_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Performance analysis
        analysis_frame = ttk.LabelFrame(optimization_frame, text="Performance Analysis", padding=(10, 5))
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)  # Increased vertical padding
        
        # Analysis text area with better font
        self.analysis_text = scrolledtext.ScrolledText(
            analysis_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=12,  # Taller text area
            font=("Arial", 10)
        )
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.analysis_text.insert(tk.END, "Click 'Analyze System' to get performance recommendations.")
        self.analysis_text.config(state=tk.DISABLED)
        
        # Analyze button with better styling
        analyze_btn = ttk.Button(analysis_frame, text="Analyze System", 
                              command=self.analyze_system,
                              padding=(15, 8))  # Larger button padding
        analyze_btn.pack(pady=15)  # Increased padding
        
    def create_status_bar(self):
        status_frame = ttk.Frame(self.main_frame, relief=tk.SUNKEN, style="StatusBar.TFrame")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))  # Increased top padding
        
        # Create custom style for status bar
        self.style.configure("StatusBar.TFrame", background="#e1e1e1")
        self.style.configure("StatusBar.TLabel", background="#e1e1e1", padding=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               anchor=tk.W, style="StatusBar.TLabel")
        status_label.pack(side=tk.LEFT, padx=10, fill=tk.X)
        
        self.time_var = tk.StringVar()
        time_label = ttk.Label(status_frame, textvariable=self.time_var, 
                             anchor=tk.E, style="StatusBar.TLabel")
        time_label.pack(side=tk.RIGHT, padx=10)
        
        # Update time
        self.update_time()
        
    def update_time(self):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
        
    def toggle_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_button.config(text="Stop Monitoring")
            self.status_var.set("Monitoring system performance...")
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self.monitor_performance)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
        else:
            self.monitoring = False
            self.monitor_button.config(text="Start Monitoring")
            self.status_var.set("Monitoring stopped")
            
    def monitor_performance(self):
        while self.monitoring:
            # Get CPU and RAM usage
            cpu_percent = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Update UI (thread-safe)
            self.root.after(0, self.update_metrics, cpu_percent, ram_percent, disk_percent)
            
            # Add to history (limit to 60 points)
            timestamp = time.time()
            self.cpu_history.append(cpu_percent)
            self.ram_history.append(ram_percent)
            self.timestamps.append(timestamp)
            
            # Keep only the last 60 points
            if len(self.cpu_history) > 60:
                self.cpu_history.pop(0)
                self.ram_history.pop(0)
                self.timestamps.pop(0)
            
            # Update graphs
            self.root.after(0, self.update_graphs)
            
            # Update processes list every 5 seconds
            if len(self.cpu_history) % 5 == 0:
                self.root.after(0, self.update_processes_list)
            
            # Sleep for 1 second
            time.sleep(1)
    
    def update_metrics(self, cpu_percent, ram_percent, disk_percent):
        # Update CPU metrics
        self.cpu_usage_var.set(f"{cpu_percent:.1f}%")
        self.cpu_progressbar["value"] = cpu_percent
        
        # Update RAM metrics
        self.ram_usage_var.set(f"{ram_percent:.1f}%")
        self.ram_progressbar["value"] = ram_percent
        
        # Update Disk metrics
        self.disk_usage_var.set(f"{disk_percent:.1f}%")
        self.disk_progressbar["value"] = disk_percent
    
    def update_graphs(self):
        # Format timestamps for x-axis
        x_labels = [datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S') for ts in self.timestamps]
        
        # Update CPU plot
        self.cpu_line.set_data(range(len(self.cpu_history)), self.cpu_history)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax1.set_xlim(0, max(60, len(self.cpu_history)))
        
        # Display fewer x-ticks to prevent overlap
        num_ticks = min(5, len(self.timestamps))
        if num_ticks > 0:
            tick_indices = [i * len(self.timestamps) // num_ticks for i in range(num_ticks)]
            self.ax1.set_xticks(tick_indices)
            self.ax1.set_xticklabels([x_labels[i] for i in tick_indices])
        
        # Update RAM plot
        self.ram_line.set_data(range(len(self.ram_history)), self.ram_history)
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.ax2.set_xlim(0, max(60, len(self.ram_history)))
        
        # Display fewer x-ticks to prevent overlap
        if num_ticks > 0:
            self.ax2.set_xticks(tick_indices)
            self.ax2.set_xticklabels([x_labels[i] for i in tick_indices])
        
        # Redraw the canvas
        self.canvas.draw()
    
    def update_processes_list(self):
        # Clear current items
        for item in self.processes_tree.get_children():
            self.processes_tree.delete(item)
        
        # Get processes info
        self.processes_data = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                pid = pinfo['pid']
                name = pinfo['name']
                # Fix: Handle None values for CPU and memory percent
                cpu_percent = pinfo['cpu_percent'] if pinfo['cpu_percent'] is not None else 0.0
                memory_percent = pinfo['memory_percent'] if pinfo['memory_percent'] is not None else 0.0
                status = pinfo['status']
                
                self.processes_data.append((pid, name, cpu_percent, memory_percent, status))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU usage (descending)
        self.processes_data.sort(key=lambda x: x[2], reverse=True)
        
        # Apply filter if search is active
        self.filter_processes()
    
    def filter_processes(self):
        # Clear current items
        for item in self.processes_tree.get_children():
            self.processes_tree.delete(item)
        
        search_term = self.search_var.get().lower()
        
        # Add filtered items with alternating row colors for better readability
        for i, (pid, name, cpu_percent, memory_percent, status) in enumerate(self.processes_data):
            if search_term in name.lower() or search_term in str(pid):
                item_id = self.processes_tree.insert('', tk.END, values=(
                    pid, 
                    name, 
                    f"{cpu_percent:.1f}", 
                    f"{memory_percent:.1f}", 
                    status
                ))
                
                # Add alternating row colors
                if i % 2 == 0:
                    self.processes_tree.item(item_id, tags=('evenrow',))
                else:
                    self.processes_tree.item(item_id, tags=('oddrow',))
        
        # Configure row tags
        self.processes_tree.tag_configure('evenrow', background='#f0f0f0')
        self.processes_tree.tag_configure('oddrow', background='#e6e6e6')
    
    def end_selected_process(self):
        selected_item = self.processes_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "No process selected")
            return
        
        pid = self.processes_tree.item(selected_item[0], "values")[0]
        try:
            process = psutil.Process(int(pid))
            process_name = process.name()
            
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to terminate process {process_name} (PID: {pid})?")
            if confirm:
                process.terminate()
                messagebox.showinfo("Success", f"Process {process_name} terminated successfully")
                self.update_processes_list()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("Error", f"Failed to terminate process: {str(e)}")
    
    def update_system_info(self):
        self.system_info_text.config(state=tk.NORMAL)
        self.system_info_text.delete(1.0, tk.END)
        
        # Get system information with better formatting
        info = [
            f"System: {platform.system()} {platform.version()}",
            f"Architecture: {platform.machine()}",
            f"Processor: {platform.processor()}",
            f"Python Version: {platform.python_version()}",
            f"Node: {platform.node()}",
            f"Platform: {platform.platform()}"
        ]
        
        # CPU Information
        info.append("\n=== CPU Information ===")
        info.append(f"Physical cores: {psutil.cpu_count(logical=False)}")
        info.append(f"Total cores: {psutil.cpu_count(logical=True)}")
        
        # Memory Information
        info.append("\n=== Memory Information ===")
        memory = psutil.virtual_memory()
        info.append(f"Total: {self.get_size(memory.total)}")
        info.append(f"Available: {self.get_size(memory.available)}")
        info.append(f"Used: {self.get_size(memory.used)} ({memory.percent}%)")
        
        # Disk Information
        info.append("\n=== Disk Information ===")
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                info.append(f"\nDevice: {partition.device}")
                info.append(f"  Mountpoint: {partition.mountpoint}")
                info.append(f"  File system type: {partition.fstype}")
                info.append(f"  Total Size: {self.get_size(partition_usage.total)}")
                info.append(f"  Used: {self.get_size(partition_usage.used)} ({partition_usage.percent}%)")
                info.append(f"  Free: {self.get_size(partition_usage.free)}")
            except PermissionError:
                pass
        
        # Network Information
        info.append("\n=== Network Information ===")
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            info.append(f"\nInterface: {interface_name}")
            for address in interface_addresses:
                if address.family == psutil.AF_LINK:
                    info.append(f"  MAC Address: {address.address}")
                elif address.family == 2:  # IPv4
                    info.append(f"  IPv4 Address: {address.address}")
                    info.append(f"  Netmask: {address.netmask}")
                elif address.family == 23:  # IPv6
                    info.append(f"  IPv6 Address: {address.address}")
        
        # Write info to text widget
        self.system_info_text.insert(tk.END, "\n".join(info))
        self.system_info_text.config(state=tk.DISABLED)
    
    def get_size(self, bytes, suffix="B"):
        """Convert bytes to human readable size"""
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor
        return f"{bytes:.2f}P{suffix}"
    
    def analyze_system(self):
        """Perform system analysis and provide optimization recommendations"""
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)

        analysis = []
        recommendations = []

        # CPU Analysis
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            analysis.append(f"\u2022 CPU usage is high ({cpu_percent:.1f}%).")
            recommendations.append("\u2022 Consider closing CPU-intensive applications.")
            recommendations.append("\u2022 Check for background processes that might be consuming resources.")
        else:
            analysis.append(f"\u2022 CPU usage is normal ({cpu_percent:.1f}%).")

        # Memory Analysis
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            analysis.append(f"\u2022 Memory usage is high ({memory.percent:.1f}%).")
            recommendations.append("\u2022 Close unused applications to free up memory.")
            recommendations.append("\u2022 Consider adding more RAM if this happens frequently.")
        else:
            analysis.append(f"\u2022 Memory usage is normal ({memory.percent:.1f}%).")

        # Disk Analysis
        disk = psutil.disk_usage('/')
        if disk.percent > 80:
            analysis.append(f"\u2022 Disk usage is high ({disk.percent:.1f}%).")
            recommendations.append("\u2022 Delete unnecessary files to free up disk space.")
            recommendations.append("\u2022 Move files to an external drive or cloud storage.")
        else:
            analysis.append(f"\u2022 Disk usage is normal ({disk.percent:.1f}%).")

        # OS Info
        system = platform.system()
        version = platform.version()
        processor = platform.processor()
        analysis.append(f"\u2022 Operating System: {system} {version}")
        analysis.append(f"\u2022 Processor: {processor}")

        # Display analysis and recommendations
        self.analysis_text.insert(tk.END, "System Analysis:\n" + "\n".join(analysis) + "\n\n")
        if recommendations:
            self.analysis_text.insert(tk.END, "Recommendations:\n" + "\n".join(recommendations))
        else:
            self.analysis_text.insert(tk.END, "No immediate optimizations needed. System is running well.")

        self.analysis_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemPerformanceAnalyzer(root)
    root.mainloop()
