# app/api/ui.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.devices.registry import DeviceRegistry
import json

router = APIRouter()
registry = DeviceRegistry()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Enhanced web UI for device control"""
    devices = registry.get_all_devices()

    # Get the status for each device
    device_statuses = {}
    for device_id, controller in devices.items():
        try:
            status = await controller.get_status()
            device_statuses[device_id] = status
        except Exception as e:
            device_statuses[device_id] = {"status": "error", "error": str(e)}

    # Group devices by room
    rooms = {}
    for device_id, status in device_statuses.items():
        room = status.get("room", "Unknown")
        if room not in rooms:
            rooms[room] = []
        rooms[room].append({"id": device_id, "status": status})

    # Build HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Home Controller</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
        <style>
            :root {
                --primary-color: #3498db;
                --secondary-color: #2ecc71;
                --dark-color: #2c3e50;
                --light-color: #ecf0f1;
                --danger-color: #e74c3c;
                --success-color: #27ae60;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: var(--light-color);
                color: var(--dark-color);
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background-color: var(--dark-color);
                color: white;
                padding: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                position: sticky;
                top: 0;
                z-index: 100;
            }
            .header h1 {
                margin: 0;
                font-weight: 300;
            }
            .room-card {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                overflow: hidden;
                transition: transform 0.2s;
            }
            .room-card:hover {
                transform: translateY(-5px);
            }
            .room-header {
                background-color: var(--primary-color);
                color: white;
                padding: 15px 20px;
                font-size: 18px;
                font-weight: 500;
            }
            .device-container {
                padding: 0;
            }
            .device-item {
                padding: 20px;
                border-bottom: 1px solid #eee;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .device-item:last-child {
                border-bottom: none;
            }
            .device-name {
                font-weight: 600;
                font-size: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .device-status {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }
            .status-on {
                background-color: var(--secondary-color);
                color: white;
            }
            .status-off {
                background-color: #95a5a6;
                color: white;
            }
            .btn-primary {
                background-color: var(--primary-color);
                border-color: var(--primary-color);
            }
            .btn-danger {
                background-color: var(--danger-color);
                border-color: var(--danger-color);
            }
            .btn-control {
                min-width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .control-panel {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin-top: 15px;
            }
            .tv-remote {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin-top: 15px;
                max-width: 300px;
            }
            .remote-button {
                height: 50px;
                font-size: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.1s, background-color 0.2s;
            }
            .remote-button:active {
                transform: scale(0.95);
                background-color: #e9ecef;
            }
            .tv-app-section {
                margin-top: 20px;
            }
            .app-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                gap: 10px;
                margin-top: 15px;
            }
            .app-button {
                padding: 10px;
                text-align: center;
                font-size: 13px;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                border-radius: 5px;
                background-color: #f8f9fa;
                transition: background-color 0.2s;
            }
            .app-button:hover {
                background-color: #e9ecef;
            }
            .app-button i {
                font-size: 24px;
                margin-bottom: 8px;
            }
            .app-list {
                max-height: 300px;
                overflow-y: auto;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                margin-top: 15px;
            }
            .app-list-item {
                padding: 10px 15px;
                border-bottom: 1px solid #dee2e6;
                cursor: pointer;
            }
            .app-list-item:hover {
                background-color: #f8f9fa;
            }
            .app-list-item:last-child {
                border-bottom: none;
            }
            .loading {
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(255, 255, 255, 0.9);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                z-index: 1000;
            }
            .loading-spinner {
                width: 40px;
                height: 40px;
                margin: 0 auto;
                border: 4px solid rgba(0, 0, 0, 0.1);
                border-left-color: var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .device-actions {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .device-panels {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .panel-tab {
                display: none;
            }
            .panel-tab.active {
                display: block;
            }
            .tab-buttons {
                display: flex;
                gap: 5px;
                margin-bottom: 15px;
            }
            .tab-button {
                padding: 8px 16px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                cursor: pointer;
            }
            .tab-button.active {
                background-color: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }
            .status-message {
                display: none;
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 10px 20px;
                border-radius: 5px;
                color: white;
                font-weight: 500;
                z-index: 1000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            }
            .status-message.success {
                background-color: var(--success-color);
            }
            .status-message.error {
                background-color: var(--danger-color);
            }
            @media (max-width: 768px) {
                .control-panel, .tv-remote {
                    grid-template-columns: repeat(3, 1fr);
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1><i class="bi bi-house-door"></i> Smart Home Controller</h1>
            </div>
        </div>
        <div class="container">
            <div class="loading" id="loading">
                <div class="loading-spinner"></div>
                <p>Processing command...</p>
            </div>
            
            <div class="status-message" id="status-message"></div>
    """

    # Add each room
    for room_name, room_devices in rooms.items():
        html_content += f"""
        <div class="room-card">
            <div class="room-header">
                <i class="bi bi-door-open"></i> {room_name}
            </div>
            <div class="device-container">
        """

        # Add each device
        for device in room_devices:
            device_id = device["id"]
            status = device["status"]
            device_type = status.get("type", "unknown")
            device_name = status.get("name", device_id)
            power = status.get("power", False)
            power_text = "On" if power else "Off"

            icon_class = ""
            if device_type == "light":
                icon_class = "bi-lightbulb"
            elif device_type == "tv":
                icon_class = "bi-tv"
            else:
                icon_class = "bi-gear"

            html_content += f"""
            <div class="device-item">
                <div class="device-name">
                    <i class="bi {icon_class}"></i> {device_name}
                    <span id="{device_id}-status" class="device-status {('status-on' if power else 'status-off')}">{power_text}</span>
                </div>
            """

            # Different controls based on device type
            if device_type == "light":
                brightness = status.get("brightness", 0)
                html_content += f"""
                <div class="device-actions">
                    <button class="btn btn-primary" onclick="controlDevice('{device_id}', 'light', 'turn_on')">
                        <i class="bi bi-power"></i> Turn On
                    </button>
                    <button class="btn btn-danger" onclick="controlDevice('{device_id}', 'light', 'turn_off')">
                        <i class="bi bi-power"></i> Turn Off
                    </button>
                    <div class="input-group" style="max-width: 200px;">
                        <span class="input-group-text">Brightness</span>
                        <select class="form-select" onchange="controlDevice('{device_id}', 'light', 'set_brightness', {{brightness: this.value}})">
                            <option value="">Set Level</option>
                            <option value="20">20%</option>
                            <option value="40">40%</option>
                            <option value="60">60%</option>
                            <option value="80">80%</option>
                            <option value="100">100%</option>
                        </select>
                    </div>
                </div>
                """
            elif device_type == "tv":
                html_content += f"""
                <div class="device-panels">
                    <div class="tab-buttons">
                        <div class="tab-button active" onclick="showPanel('{device_id}', 'basic')">Basic Controls</div>
                        <div class="tab-button" onclick="showPanel('{device_id}', 'remote')">Remote</div>
                        <div class="tab-button" onclick="showPanel('{device_id}', 'apps')">Apps</div>
                    </div>
                    
                    <div id="{device_id}-basic" class="panel-tab active">
                        <div class="device-actions">
                            <button class="btn btn-primary" onclick="controlDevice('{device_id}', 'tv', 'turn_on')">
                                <i class="bi bi-power"></i> Turn On
                            </button>
                            <button class="btn btn-danger" onclick="controlDevice('{device_id}', 'tv', 'turn_off')">
                                <i class="bi bi-power"></i> Turn Off
                            </button>
                            <button class="btn btn-secondary" 
                                onmousedown="startVolumeControl('{device_id}', 'up')" 
                                onmouseup="stopVolumeControl()" 
                                ontouchstart="startVolumeControl('{device_id}', 'up')" 
                                ontouchend="stopVolumeControl()"
                                onmouseleave="stopVolumeControl()">
                                <i class="bi bi-volume-up"></i> Volume +
                            </button>
                            <button class="btn btn-secondary" 
                                onmousedown="startVolumeControl('{device_id}', 'down')" 
                                onmouseup="stopVolumeControl()" 
                                ontouchstart="startVolumeControl('{device_id}', 'down')" 
                                ontouchend="stopVolumeControl()"
                                onmouseleave="stopVolumeControl()">
                                <i class="bi bi-volume-down"></i> Volume -
                            </button>
                        </div>
                    </div>
                    
                    <div id="{device_id}-remote" class="panel-tab">
                        <div class="tv-remote">
                            <button class="btn btn-outline-secondary remote-button" onclick="controlDevice('{device_id}', 'tv', 'navigate', {{direction: 'up'}})">
                                <i class="bi bi-arrow-up"></i>
                            </button>
                            <button class="btn btn-outline-primary remote-button" onclick="controlDevice('{device_id}', 'tv', 'navigate', {{direction: 'home'}})">
                                <i class="bi bi-house"></i> Home
                            </button>
                            <button class="btn btn-outline-secondary remote-button" onclick="controlDevice('{device_id}', 'tv', 'navigate', {{direction: 'back'}})">
                                <i class="bi bi-arrow-return-left"></i> Back
                            </button>
                            
                            <button class="btn btn-outline-secondary remote-button" onclick="controlDevice('{device_id}', 'tv', 'navigate', {{direction: 'left'}})">
                                <i class="bi bi-arrow-left"></i>
                            </button>
                            <button class="btn btn-outline-secondary remote-button" onclick="controlDevice('{device_id}', 'tv', 'navigate', {{direction: 'select'}})">
                                <i class="bi bi-check2"></i> Select
                            </button>
                            <button class="btn btn-outline-secondary remote-button" onclick="controlDevice('{device_id}', 'tv', 'navigate', {{direction: 'right'}})">
                                <i class="bi bi-arrow-right"></i>
                            </button>
                            
                            <button class="btn btn-outline-secondary remote-button" onclick="controlDevice('{device_id}', 'tv', 'keypress', {{key: 'InstantReplay'}})">
                                <i class="bi bi-arrow-counterclockwise"></i> Replay
                            </button>
                            <button class="btn btn-outline-secondary remote-button" onclick="controlDevice('{device_id}', 'tv', 'navigate', {{direction: 'down'}})">
                                <i class="bi bi-arrow-down"></i>
                            </button>
                            <button class="btn btn-outline-secondary remote-button" onclick="controlDevice('{device_id}', 'tv', 'keypress', {{key: 'Info'}})">
                                <i class="bi bi-info-circle"></i> Info
                            </button>
                            
                            <button class="btn btn-outline-success remote-button" onclick="controlDevice('{device_id}', 'tv', 'keypress', {{key: 'Play'}})">
                                <i class="bi bi-play-fill"></i> Play/Pause
                            </button>
                            <button class="btn btn-outline-success remote-button" onclick="controlDevice('{device_id}', 'tv', 'keypress', {{key: 'Rev'}})">
                                <i class="bi bi-rewind-fill"></i> Rewind
                            </button>
                            <button class="btn btn-outline-success remote-button" onclick="controlDevice('{device_id}', 'tv', 'keypress', {{key: 'Fwd'}})">
                                <i class="bi bi-fast-forward-fill"></i> Forward
                            </button>
                        </div>
                    </div>
                    
                    <div id="{device_id}-apps" class="panel-tab">
                        <button class="btn btn-primary mb-3" onclick="loadApps('{device_id}')">
                            <i class="bi bi-grid"></i> Load Installed Apps
                        </button>
                        
                        <div class="app-grid">
                            <button class="app-button" onclick="controlDevice('{device_id}', 'tv', 'launch_app_by_name', {{app_name: 'Netflix'}})">
                                <i class="bi bi-film"></i>
                                Netflix
                            </button>
                            <button class="app-button" onclick="controlDevice('{device_id}', 'tv', 'launch_app_by_name', {{app_name: 'YouTube'}})">
                                <i class="bi bi-youtube"></i>
                                YouTube
                            </button>
                            <button class="app-button" onclick="controlDevice('{device_id}', 'tv', 'launch_app_by_name', {{app_name: 'Disney Plus'}})">
                                <i class="bi bi-star"></i>
                                Disney+
                            </button>
                            <button class="app-button" onclick="controlDevice('{device_id}', 'tv', 'launch_app_by_name', {{app_name: 'Prime Video'}})">
                                <i class="bi bi-camera-video"></i>
                                Prime
                            </button>
                            <button class="app-button" onclick="controlDevice('{device_id}', 'tv', 'launch_app_by_name', {{app_name: 'Hulu'}})">
                                <i class="bi bi-collection-play"></i>
                                Hulu
                            </button>
                            <button class="app-button" onclick="controlDevice('{device_id}', 'tv', 'launch_app_by_name', {{app_name: 'HBO Max'}})">
                                <i class="bi bi-tv"></i>
                                HBO
                            </button>
                        </div>
                        
                        <div id="{device_id}-app-list" class="app-list" style="display: none;"></div>
                    </div>
                </div>
                """

            html_content += """
            </div>
            """

        html_content += """
            </div>
        </div>
        """

    html_content += """
        </div>
        
        <script>
            // Variable to store volume control interval
            let volumeInterval = null;
            
            // Function to start continuous volume control
            function startVolumeControl(deviceId, direction) {
                // First immediate press
                controlDevice(deviceId, 'tv', direction === 'up' ? 'volume_up' : 'volume_down');
                
                // Then continuous presses while button is held
                volumeInterval = setInterval(() => {
                    controlDevice(deviceId, 'tv', direction === 'up' ? 'volume_up' : 'volume_down');
                }, 300); // Adjust timing as needed
            }
            
            // Function to stop continuous volume control
            function stopVolumeControl() {
                if (volumeInterval) {
                    clearInterval(volumeInterval);
                    volumeInterval = null;
                }
            }
            
            // Show status message
            function showStatusMessage(message, success = true) {
                const statusEl = document.getElementById('status-message');
                statusEl.textContent = message;
                statusEl.className = success ? 'status-message success' : 'status-message error';
                statusEl.style.display = 'block';
                
                // Hide after 3 seconds
                setTimeout(() => {
                    statusEl.style.display = 'none';
                }, 3000);
            }
            
            async function controlDevice(deviceId, deviceType, action, params = {}) {
                showLoading(true);
                let url = '';
                let method = 'POST';
                
                // Handle different device types and actions
                if (deviceType === 'light') {
                    if (action === 'turn_on') {
                        url = `/lights/${deviceId}/turn_on`;
                    } else if (action === 'turn_off') {
                        url = `/lights/${deviceId}/turn_off`;
                    } else if (action === 'set_brightness') {
                        url = `/lights/${deviceId}/brightness?brightness=${params.brightness}`;
                    }
                } else if (deviceType === 'tv') {
                    if (action === 'turn_on') {
                        url = `/tv/${deviceId}/turn_on`;
                    } else if (action === 'turn_off') {
                        url = `/tv/${deviceId}/turn_off`;
                    } else if (action === 'volume_up') {
                        url = `/tv/${deviceId}/volume_up`;
                    } else if (action === 'volume_down') {
                        url = `/tv/${deviceId}/volume_down`;
                    } else if (action === 'navigate') {
                        url = `/tv/${deviceId}/navigate/${params.direction}`;
                    } else if (action === 'keypress') {
                        url = `/tv/${deviceId}/keypress/${params.key}`;
                    } else if (action === 'launch_app') {
                        url = `/tv/${deviceId}/launch_app/${params.app_id}`;
                    } else if (action === 'launch_app_by_name') {
                        url = `/tv/${deviceId}/launch_app_by_name?app_name=${encodeURIComponent(params.app_name)}`;
                        method = 'POST';
                    }
                }
                
                try {
                    const response = await fetch(url, { method });
                    const result = await response.json();
                    console.log(result);
                    
                    // Don't reload the page, just update UI elements as needed
                    showLoading(false);
                    
                    // Update status message
                    if (result.status === 'success') {
                        let actionMessage = action.replace('_', ' ');
                        showStatusMessage(`${actionMessage} successful`, true);
                        
                        // Only update status for power-related actions without reloading
                        if (action === 'turn_on' || action === 'turn_off') {
                            const statusBadge = document.querySelector(`#${deviceId}-status`);
                            if (statusBadge) {
                                if (action === 'turn_on') {
                                    statusBadge.textContent = 'On';
                                    statusBadge.classList.remove('status-off');
                                    statusBadge.classList.add('status-on');
                                } else {
                                    statusBadge.textContent = 'Off';
                                    statusBadge.classList.remove('status-on');
                                    statusBadge.classList.add('status-off');
                                }
                            }
                        }
                    } else if (result.error) {
                        showStatusMessage(`Error: ${result.error}`, false);
                    }
                    
                    return result;
                } catch (error) {
                    console.error('Error:', error);
                    showLoading(false);
                    showStatusMessage('Connection error. Please try again.', false);
                }
            }
            
            async function loadApps(deviceId) {
                showLoading(true);
                try {
                    const response = await fetch(`/tv/${deviceId}/apps`);
                    const apps = await response.json();
                    
                    const appListEl = document.getElementById(`${deviceId}-app-list`);
                    appListEl.innerHTML = '';
                    appListEl.style.display = 'block';
                    
                    apps.forEach(app => {
                        const appEl = document.createElement('div');
                        appEl.className = 'app-list-item';
                        appEl.textContent = app.name;
                        appEl.onclick = () => controlDevice(deviceId, 'tv', 'launch_app', {app_id: app.id});
                        appListEl.appendChild(appEl);
                    });
                    
                    showLoading(false);
                    showStatusMessage('Apps loaded successfully', true);
                } catch (error) {
                    console.error('Error loading apps:', error);
                    showLoading(false);
                    showStatusMessage('Error loading apps. Please try again.', false);
                }
            }
            
            function showPanel(deviceId, panelName) {
                // Hide all panels
                const panels = document.querySelectorAll(`[id^="${deviceId}-"]`);
                panels.forEach(panel => {
                    panel.classList.remove('active');
                });
                
                // Show selected panel
                const selectedPanel = document.getElementById(`${deviceId}-${panelName}`);
                if (selectedPanel) {
                    selectedPanel.classList.add('active');
                }
                
                // Update tab buttons
                const deviceElement = selectedPanel.closest('.device-item');
                const tabButtons = deviceElement.querySelectorAll('.tab-button');
                tabButtons.forEach(button => {
                    button.classList.remove('active');
                    if (button.textContent.toLowerCase().includes(panelName.toLowerCase())) {
                        button.classList.add('active');
                    }
                });
            }
            
            function showLoading(show) {
                const loadingEl = document.getElementById('loading');
                if (show) {
                    loadingEl.style.display = 'block';
                } else {
                    loadingEl.style.display = 'none';
                }
            }
        </script>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    return html_content
