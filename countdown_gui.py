#!/usr/bin/env python3
"""
Countdown Audio Builder GUI
---------------------------
A tkinter-based GUI for controlling the countdown_builder.py script.
Provides an easy-to-use interface for configuring and generating countdown audio files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import sys
from pathlib import Path
import os
import json

class CountdownGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Audio Builder")
        self.root.geometry("800x700")
        
        # Variables for form fields
        self.vars = {}
        self.init_variables()
        
        # Create the UI
        self.create_widgets()
        
        # Status for generation process
        self.is_generating = False
        
    def init_variables(self):
        """Initialize tkinter variables for all parameters"""
        self.vars = {
            'start': tk.IntVar(value=80),
            'interval': tk.DoubleVar(value=3.5),
            'long_interval': tk.DoubleVar(value=8.0),
            'every_n': tk.IntVar(value=8),
            'lang': tk.StringVar(value="en"),
            'tld': tk.StringVar(value="com"),
            'beep_freq': tk.IntVar(value=1000),
            'beep_ms': tk.IntVar(value=300),
            'beep_gain': tk.DoubleVar(value=-6.0),
            'fade_ms': tk.IntVar(value=12),
            'outfile': tk.StringVar(value="countdown_combined.mp3"),
            'out_bitrate': tk.StringVar(value="192k"),
            'lead_in': tk.StringVar(value=""),
            'lead_in_gap_ms': tk.IntVar(value=1000),
            'rest_text': tk.StringVar(value="rest"),
            'skip_first_rest': tk.IntVar(value=0),
            'end_with': tk.StringVar(value="")
        }
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main frame with scrollable canvas
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for organized tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic Settings Tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Settings")
        self.create_basic_settings(basic_frame)
        
        # Advanced Settings Tab
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Advanced Settings")
        self.create_advanced_settings(advanced_frame)
        
        # Audio Settings Tab
        audio_frame = ttk.Frame(notebook)
        notebook.add(audio_frame, text="Audio Settings")
        self.create_audio_settings(audio_frame)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready to generate countdown")
        self.status_label.pack(pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.generate_btn = ttk.Button(button_frame, text="Generate Countdown", command=self.generate_countdown)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.preview_btn = ttk.Button(button_frame, text="Preview Generated File", command=self.preview_audio, state=tk.DISABLED)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_preset_btn = ttk.Button(button_frame, text="Save Preset", command=self.save_preset)
        self.save_preset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.load_preset_btn = ttk.Button(button_frame, text="Load Preset", command=self.load_preset)
        self.load_preset_btn.pack(side=tk.LEFT)
    
    def create_basic_settings(self, parent):
        """Create basic settings widgets"""
        # Title
        title = ttk.Label(parent, text="Basic Countdown Settings", font=('TkDefaultFont', 12, 'bold'))
        title.pack(pady=(0, 15))
        
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Basic settings
        settings = [
            ("Starting Number:", 'start', "Number to start countdown from"),
            ("Normal Interval (seconds):", 'interval', "Time between normal counts"),
            ("Long Interval (seconds):", 'long_interval', "Time after rest cues"),
            ("Rest Every N Counts:", 'every_n', "Insert rest cue every N counts (0 to disable)"),
            ("Skip First N Rests:", 'skip_first_rest', "Number of initial rest periods to skip"),
            ("Output File:", 'outfile', "Name of the output MP3 file"),
        ]
        
        for i, (label, var_name, tooltip) in enumerate(settings):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5, padx=20)
            
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            
            if var_name == 'outfile':
                file_frame = ttk.Frame(frame)
                file_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                entry = ttk.Entry(file_frame, textvariable=self.vars[var_name], width=30)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                browse_btn = ttk.Button(file_frame, text="Browse", 
                                      command=lambda: self.browse_output_file())
                browse_btn.pack(side=tk.LEFT, padx=(5, 0))
            else:
                entry = ttk.Entry(frame, textvariable=self.vars[var_name], width=15)
                entry.pack(side=tk.LEFT)
            
            # Tooltip
            ttk.Label(frame, text=f"({tooltip})", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_advanced_settings(self, parent):
        """Create advanced settings widgets"""
        title = ttk.Label(parent, text="Text and Language Settings", font=('TkDefaultFont', 12, 'bold'))
        title.pack(pady=(0, 15))
        
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        settings = [
            ("Language Code:", 'lang', "gTTS language (en, es, fr, etc.)"),
            ("TLD Region:", 'tld', "Voice region (com, co.uk, com.au, etc.)"),
            ("Lead-in Text:", 'lead_in', "Optional opening phrase (e.g., 'Get ready')"),
            ("Lead-in Gap (ms):", 'lead_in_gap_ms', "Silence after lead-in"),
            ("Rest Text:", 'rest_text', "Word spoken during rest cues"),
            ("End Text:", 'end_with', "Optional closing phrase (e.g., 'Good job!')"),
        ]
        
        for label, var_name, tooltip in settings:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5, padx=20)
            
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            entry = ttk.Entry(frame, textvariable=self.vars[var_name], width=30)
            entry.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=f"({tooltip})", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_audio_settings(self, parent):
        """Create audio settings widgets"""
        title = ttk.Label(parent, text="Audio Processing Settings", font=('TkDefaultFont', 12, 'bold'))
        title.pack(pady=(0, 15))
        
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        settings = [
            ("Beep Frequency (Hz):", 'beep_freq', "Frequency of beep tones"),
            ("Beep Duration (ms):", 'beep_ms', "Length of each beep"),
            ("Beep Gain (dB):", 'beep_gain', "Volume of beeps (negative = quieter)"),
            ("Fade Duration (ms):", 'fade_ms', "Fade in/out to avoid clicks"),
            ("Output Bitrate:", 'out_bitrate', "MP3 bitrate (128k, 192k, 256k, etc.)"),
        ]
        
        for label, var_name, tooltip in settings:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5, padx=20)
            
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            
            if var_name == 'out_bitrate':
                combo = ttk.Combobox(frame, textvariable=self.vars[var_name], 
                                   values=['128k', '192k', '256k', '320k'], width=10)
                combo.pack(side=tk.LEFT)
            else:
                entry = ttk.Entry(frame, textvariable=self.vars[var_name], width=15)
                entry.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=f"({tooltip})", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def browse_output_file(self):
        """Open file browser for output file selection"""
        filename = filedialog.asksaveasfilename(
            title="Save countdown as...",
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if filename:
            self.vars['outfile'].set(filename)
    
    def build_command(self):
        """Build the command line arguments for countdown_builder.py"""
        cmd = [sys.executable, "countdown_builder.py"]
        
        # Add all parameters
        for param, var in self.vars.items():
            value = var.get()
            
            # Skip empty string values for optional parameters
            if param in ['lead_in', 'end_with'] and not value:
                continue
            
            # Convert parameter name to command line format
            param_name = param.replace('_', '-')
            cmd.extend([f"--{param_name}", str(value)])
        
        return cmd
    
    def generate_countdown(self):
        """Generate the countdown audio in a separate thread"""
        if self.is_generating:
            return
        
        # Validate inputs
        try:
            if self.vars['start'].get() <= 0:
                messagebox.showerror("Error", "Starting number must be positive")
                return
            if self.vars['interval'].get() <= 0:
                messagebox.showerror("Error", "Interval must be positive")
                return
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return
        
        # Check if countdown_builder.py exists
        if not Path("countdown_builder.py").exists():
            messagebox.showerror("Error", "countdown_builder.py not found in current directory")
            return
        
        # Start generation in thread
        self.is_generating = True
        self.generate_btn.config(state=tk.DISABLED)
        self.preview_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Generating countdown audio...")
        
        thread = threading.Thread(target=self.run_generation, daemon=True)
        thread.start()
    
    def run_generation(self):
        """Run the countdown generation process"""
        try:
            cmd = self.build_command()
            
            # Run the countdown builder
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            # Update UI on main thread
            self.root.after(0, self.generation_complete, result)
            
        except Exception as e:
            self.root.after(0, self.generation_error, str(e))
    
    def generation_complete(self, result):
        """Handle completion of countdown generation"""
        self.is_generating = False
        self.generate_btn.config(state=tk.NORMAL)
        self.progress.stop()
        
        if result.returncode == 0:
            self.status_label.config(text="Countdown generated successfully!")
            self.preview_btn.config(state=tk.NORMAL)
            
            # Show output
            output_file = self.vars['outfile'].get()
            messagebox.showinfo("Success", 
                              f"Countdown audio generated successfully!\n\n"
                              f"Output file: {output_file}\n"
                              f"Timeline file: {Path(output_file).with_suffix('.json')}")
        else:
            self.status_label.config(text="Generation failed!")
            error_msg = result.stderr if result.stderr else result.stdout
            messagebox.showerror("Error", f"Generation failed:\n{error_msg}")
    
    def generation_error(self, error):
        """Handle generation error"""
        self.is_generating = False
        self.generate_btn.config(state=tk.NORMAL)
        self.progress.stop()
        self.status_label.config(text="Generation failed!")
        messagebox.showerror("Error", f"An error occurred:\n{error}")
    
    def preview_audio(self):
        """Preview the generated audio file"""
        output_file = self.vars['outfile'].get()
        
        if not Path(output_file).exists():
            messagebox.showerror("Error", f"Output file {output_file} not found")
            return
        
        try:
            # Try to open with default system player
            if sys.platform.startswith('linux'):
                subprocess.run(['xdg-open', output_file])
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', output_file])
            elif sys.platform.startswith('win'):  # Windows
                os.startfile(output_file)
            else:
                messagebox.showinfo("Preview", f"Please manually open: {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open audio file:\n{e}")
    
    def save_preset(self):
        """Save current settings as a preset"""
        filename = filedialog.asksaveasfilename(
            title="Save preset as...",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                preset = {}
                for name, var in self.vars.items():
                    preset[name] = var.get()
                
                with open(filename, 'w') as f:
                    json.dump(preset, f, indent=2)
                
                messagebox.showinfo("Success", f"Preset saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save preset:\n{e}")
    
    def load_preset(self):
        """Load settings from a preset file"""
        filename = filedialog.askopenfilename(
            title="Load preset from...",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    preset = json.load(f)
                
                for name, value in preset.items():
                    if name in self.vars:
                        self.vars[name].set(value)
                
                messagebox.showinfo("Success", f"Preset loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load preset:\n{e}")


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = CountdownGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()