#!/usr/bin/env python3
"""
Countdown Audio Builder Web Interface
------------------------------------
A web-based interface for controlling the countdown_builder.py script.
Works in any browser without requiring GUI libraries.
"""

import json
import subprocess
import sys
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import socketserver
import webbrowser
import cgi
from io import StringIO

class CountdownWebHandler(SimpleHTTPRequestHandler):
    # Class variable to share status between requests
    generation_status = {"running": False, "message": "Ready", "file": None}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_main_page().encode())
        elif self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(CountdownWebHandler.generation_status).encode())
        elif self.path.startswith("/download/"):
            filename = self.path[10:]  # Remove /download/
            if Path(filename).exists():
                self.send_response(200)
                self.send_header('Content-type', 'audio/mpeg')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                with open(filename, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == "/generate":
            try:
                # Parse multipart form data
                content_type = self.headers.get('Content-Type', '')
                if content_type.startswith('multipart/form-data'):
                    # Handle multipart form data
                    form = cgi.FieldStorage(
                        fp=self.rfile,
                        headers=self.headers,
                        environ={'REQUEST_METHOD': 'POST'}
                    )
                    
                    # Convert to the expected format
                    params = {}
                    for field_name in form.keys():
                        field = form[field_name]
                        if field.filename is None:  # Regular field, not file upload
                            params[field_name] = [field.value]
                else:
                    # Handle URL-encoded form data
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    params = urllib.parse.parse_qs(post_data.decode())
                
                print(f"DEBUG: Received form data: {params}", flush=True)
                # Convert form data to countdown_builder arguments
                self.start_generation(params)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "started"}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_error(404, "Not found")
    
    def start_generation(self, params):
        """Start countdown generation in background thread"""
        if CountdownWebHandler.generation_status["running"]:
            return
        
        CountdownWebHandler.generation_status = {"running": True, "message": "Generating...", "file": None}
        
        def generate():
            try:
                # Build command
                cmd = [sys.executable, "countdown_builder.py"]
                
                # Map form parameters to command line arguments
                param_map = {
                    'start': '--start',
                    'interval': '--interval', 
                    'long_interval': '--long-interval',
                    'every_n': '--every-n',
                    'lang': '--lang',
                    'tld': '--tld',
                    'beep_freq': '--beep-freq',
                    'beep_ms': '--beep-ms',
                    'beep_gain': '--beep-gain',
                    'fade_ms': '--fade-ms',
                    'outfile': '--outfile',
                    'out_bitrate': '--out-bitrate',
                    'lead_in': '--lead-in',
                    'lead_in_gap_ms': '--lead-in-gap-ms',
                    'rest_text': '--rest-text',
                    'skip_first_rest': '--skip-first-rest',
                    'end_with': '--end-with'
                }
                
                for param, flag in param_map.items():
                    if param in params:
                        value = params[param][0].strip()
                        # Always include numeric parameters even if they're 0 or empty string
                        if value or param in ['start', 'interval', 'long_interval', 'every_n', 'beep_freq', 'beep_ms', 'beep_gain', 'fade_ms', 'lead_in_gap_ms', 'skip_first_rest']:
                            if value:  # Only add if there's actually a value
                                cmd.extend([flag, value])
                
                # Debug: Print the command being executed
                print(f"DEBUG: Executing command: {' '.join(cmd)}", flush=True)
                
                # Run generation
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Debug: Print the result
                print(f"DEBUG: Return code: {result.returncode}", flush=True)
                print(f"DEBUG: STDOUT: {result.stdout}", flush=True)
                print(f"DEBUG: STDERR: {result.stderr}", flush=True)
                
                if result.returncode == 0:
                    outfile = params.get('outfile', ['countdown_combined.mp3'])[0]
                    CountdownWebHandler.generation_status = {
                        "running": False, 
                        "message": "Generation completed successfully!", 
                        "file": outfile
                    }
                else:
                    CountdownWebHandler.generation_status = {
                        "running": False, 
                        "message": f"Generation failed: {result.stderr or result.stdout}", 
                        "file": None
                    }
            except Exception as e:
                CountdownWebHandler.generation_status = {
                    "running": False, 
                    "message": f"Error: {str(e)}", 
                    "file": None
                }
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def get_main_page(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>Countdown Audio Builder</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
        .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }
        .tab button:hover { background-color: #ddd; }
        .tab button.active { background-color: #ccc; }
        .tabcontent { display: none; padding: 20px; border: 1px solid #ccc; border-top: none; }
        .form-group { margin: 15px 0; }
        .form-group label { display: inline-block; width: 200px; font-weight: bold; }
        .form-group input, .form-group select { padding: 5px; width: 200px; }
        .form-group .help { color: #666; font-size: 0.9em; margin-left: 10px; }
        button { padding: 10px 20px; margin: 10px 5px; background: #007cba; color: white; border: none; cursor: pointer; }
        button:hover { background: #005a8b; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .status.info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .progress { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; }
        .progress-bar { height: 100%; background: #007cba; animation: slide 2s infinite; }
        @keyframes slide { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
    </style>
</head>
<body>
    <h1>🎵 Countdown Audio Builder</h1>
    
    <div class="tab">
        <button class="tablinks active" onclick="openTab(event, 'basic')">Basic Settings</button>
        <button class="tablinks" onclick="openTab(event, 'advanced')">Advanced Settings</button>
        <button class="tablinks" onclick="openTab(event, 'audio')">Audio Settings</button>
    </div>

    <form id="countdownForm">
        <div id="basic" class="tabcontent" style="display: block;">
            <h3>Basic Countdown Settings</h3>
            
            <div class="form-group">
                <label for="start">Starting Number:</label>
                <input type="number" id="start" name="start" value="40" min="1">
                <span class="help">Number to start countdown from</span>
            </div>
            
            <div class="form-group">
                <label for="interval">Normal Interval (seconds):</label>
                <input type="number" id="interval" name="interval" value="3.5" step="0.1" min="0.1">
                <span class="help">Time between normal counts</span>
            </div>
            
            <div class="form-group">
                <label for="long_interval">Long Interval (seconds):</label>
                <input type="number" id="long_interval" name="long_interval" value="8.0" step="0.1" min="0.1">
                <span class="help">Time after rest cues</span>
            </div>
            
            <div class="form-group">
                <label for="every_n">Rest Every N Counts:</label>
                <input type="number" id="every_n" name="every_n" value="8" min="0">
                <span class="help">Insert rest cue every N counts (0 to disable)</span>
            </div>
            
            <div class="form-group">
                <label for="skip_first_rest">Skip First N Rests:</label>
                <input type="number" id="skip_first_rest" name="skip_first_rest" value="0" min="0">
                <span class="help">Number of initial rest periods to skip</span>
            </div>
            
            <div class="form-group">
                <label for="outfile">Output File:</label>
                <input type="text" id="outfile" name="outfile" value="countdown_combined.mp3">
                <span class="help">Name of the output MP3 file</span>
            </div>
        </div>

        <div id="advanced" class="tabcontent">
            <h3>Text and Language Settings</h3>
            
            <div class="form-group">
                <label for="lang">Language Code:</label>
                <select id="lang" name="lang">
                    <option value="en" selected>English (en)</option>
                    <option value="es">Spanish (es)</option>
                    <option value="fr">French (fr)</option>
                    <option value="de">German (de)</option>
                    <option value="it">Italian (it)</option>
                </select>
                <span class="help">gTTS language</span>
            </div>
            
            <div class="form-group">
                <label for="tld">TLD Region:</label>
                <select id="tld" name="tld">
                    <option value="com" selected>com (US)</option>
                    <option value="co.uk">co.uk (UK)</option>
                    <option value="com.au">com.au (Australia)</option>
                    <option value="ca">ca (Canada)</option>
                </select>
                <span class="help">Voice region</span>
            </div>
            
            <div class="form-group">
                <label for="lead_in">Lead-in Text:</label>
                <input type="text" id="lead_in" name="lead_in" placeholder="e.g., Get ready">
                <span class="help">Optional opening phrase</span>
            </div>
            
            <div class="form-group">
                <label for="lead_in_gap_ms">Lead-in Gap (ms):</label>
                <input type="number" id="lead_in_gap_ms" name="lead_in_gap_ms" value="1000" min="0">
                <span class="help">Silence after lead-in</span>
            </div>
            
            <div class="form-group">
                <label for="rest_text">Rest Text:</label>
                <input type="text" id="rest_text" name="rest_text" value="rest">
                <span class="help">Word spoken during rest cues</span>
            </div>
            
            <div class="form-group">
                <label for="end_with">End Text:</label>
                <input type="text" id="end_with" name="end_with" placeholder="e.g., Good job!">
                <span class="help">Optional closing phrase</span>
            </div>
        </div>

        <div id="audio" class="tabcontent">
            <h3>Audio Processing Settings</h3>
            
            <div class="form-group">
                <label for="beep_freq">Beep Frequency (Hz):</label>
                <input type="number" id="beep_freq" name="beep_freq" value="1000" min="100" max="5000">
                <span class="help">Frequency of beep tones</span>
            </div>
            
            <div class="form-group">
                <label for="beep_ms">Beep Duration (ms):</label>
                <input type="number" id="beep_ms" name="beep_ms" value="300" min="50" max="2000">
                <span class="help">Length of each beep</span>
            </div>
            
            <div class="form-group">
                <label for="beep_gain">Beep Gain (dB):</label>
                <input type="number" id="beep_gain" name="beep_gain" value="-6.0" step="0.1">
                <span class="help">Volume of beeps (negative = quieter)</span>
            </div>
            
            <div class="form-group">
                <label for="fade_ms">Fade Duration (ms):</label>
                <input type="number" id="fade_ms" name="fade_ms" value="12" min="0" max="100">
                <span class="help">Fade in/out to avoid clicks</span>
            </div>
            
            <div class="form-group">
                <label for="out_bitrate">Output Bitrate:</label>
                <select id="out_bitrate" name="out_bitrate">
                    <option value="128k">128k</option>
                    <option value="192k" selected>192k</option>
                    <option value="256k">256k</option>
                    <option value="320k">320k</option>
                </select>
                <span class="help">MP3 quality</span>
            </div>
        </div>
    </form>

    <div style="margin-top: 20px;">
        <button type="button" onclick="generateCountdown()" id="generateBtn">🎵 Generate Countdown</button>
        <button type="button" onclick="loadPreset()" id="loadBtn">📁 Load Preset</button>
        <button type="button" onclick="savePreset()" id="saveBtn">💾 Save Preset</button>
    </div>

    <div id="status"></div>
    <div id="downloadSection" style="display: none;">
        <h3>Download Generated Files</h3>
        <button type="button" onclick="downloadAudio()" id="downloadBtn">🎵 Download Audio</button>
        <button type="button" onclick="downloadTimeline()" id="timelineBtn">📋 Download Timeline</button>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }

        function generateCountdown() {
            const form = document.getElementById('countdownForm');
            const formData = new FormData(form);
            const generateBtn = document.getElementById('generateBtn');
            
            generateBtn.disabled = true;
            generateBtn.textContent = '⏳ Generating...';
            
            document.getElementById('status').innerHTML = `
                <div class="status info">
                    <div class="progress"><div class="progress-bar"></div></div>
                    Generating countdown audio...
                </div>
            `;
            
            fetch('/generate', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    checkStatus();
                } else {
                    showError(data.error || 'Unknown error');
                }
            })
            .catch(error => {
                showError('Network error: ' + error);
            });
        }

        function checkStatus() {
            fetch('/status')
            .then(response => response.json())
            .then(data => {
                if (data.running) {
                    document.getElementById('status').innerHTML = `
                        <div class="status info">
                            <div class="progress"><div class="progress-bar"></div></div>
                            ${data.message}
                        </div>
                    `;
                    setTimeout(checkStatus, 1000);
                } else {
                    const generateBtn = document.getElementById('generateBtn');
                    generateBtn.disabled = false;
                    generateBtn.textContent = '🎵 Generate Countdown';
                    
                    if (data.file) {
                        document.getElementById('status').innerHTML = `
                            <div class="status success">${data.message}</div>
                        `;
                        document.getElementById('downloadSection').style.display = 'block';
                        document.getElementById('downloadSection').setAttribute('data-file', data.file);
                    } else {
                        showError(data.message);
                    }
                }
            });
        }

        function showError(message) {
            const generateBtn = document.getElementById('generateBtn');
            generateBtn.disabled = false;
            generateBtn.textContent = '🎵 Generate Countdown';
            
            document.getElementById('status').innerHTML = `
                <div class="status error">${message}</div>
            `;
        }

        function downloadAudio() {
            const file = document.getElementById('downloadSection').getAttribute('data-file');
            window.open('/download/' + file, '_blank');
        }

        function downloadTimeline() {
            const file = document.getElementById('downloadSection').getAttribute('data-file');
            const timelineFile = file.replace('.mp3', '.json');
            window.open('/download/' + timelineFile, '_blank');
        }

        function savePreset() {
            const form = document.getElementById('countdownForm');
            const formData = new FormData(form);
            const preset = {};
            for (let [key, value] of formData.entries()) {
                preset[key] = value;
            }
            
            const blob = new Blob([JSON.stringify(preset, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'countdown_preset.json';
            a.click();
            URL.revokeObjectURL(url);
        }

        function loadPreset() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        try {
                            const preset = JSON.parse(e.target.result);
                            for (let [key, value] of Object.entries(preset)) {
                                const element = document.getElementById(key);
                                if (element) {
                                    element.value = value;
                                }
                            }
                            document.getElementById('status').innerHTML = `
                                <div class="status success">Preset loaded successfully!</div>
                            `;
                        } catch (error) {
                            showError('Error loading preset: ' + error.message);
                        }
                    };
                    reader.readAsText(file);
                }
            };
            input.click();
        }
    </script>
</body>
</html>"""

def start_server(port=8001):
    """Start the web server"""
    handler = CountdownWebHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌐 Countdown Builder Web Interface")
        print(f"📡 Server running at: http://localhost:{port}")
        print(f"🎵 Open the URL above in your browser to use the interface")
        print(f"⌨️  Press Ctrl+C to stop the server")
        
        # Try to open browser automatically
        try:
            webbrowser.open(f'http://localhost:{port}')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    # Check if countdown_builder.py exists
    if not Path("countdown_builder.py").exists():
        print("❌ Error: countdown_builder.py not found in current directory")
        sys.exit(1)
    
    # Start server
    start_server()