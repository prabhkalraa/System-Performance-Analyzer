        
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
                # Handle missing CPU and memory values
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
                if address.family == 2:  # IPv4
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
