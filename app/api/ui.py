# app/api/ui.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.devices.registry import DeviceRegistry

router = APIRouter()
registry = DeviceRegistry()


@router.get("/", response_class=HTMLResponse)
async def dashboard():
    """Simple web UI for device control"""
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
        <title>Home Automation Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .room {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .room-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }
            .device {
                padding: 10px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .device:last-child {
                border-bottom: none;
            }
            .device-name {
                font-weight: bold;
            }
            .device-status {
                color: #666;
            }
            .device-controls {
                display: flex;
                gap: 10px;
            }
            button {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
            }
            button.off {
                background-color: #f44336;
            }
            @media (max-width: 600px) {
                .device {
                    flex-direction: column;
                    align-items: flex-start;
                }
                .device-controls {
                    margin-top: 10px;
                }
            }
        </style>
        <script>
            async function controlDevice(deviceId, action, params = {}) {
                let url = '';
                let method = 'POST';
                
                if (action === 'turn_on') {
                    url = `/lights/${deviceId}/turn_on`;
                } else if (action === 'turn_off') {
                    url = `/lights/${deviceId}/turn_off`;
                } else if (action === 'set_brightness') {
                    url = `/lights/${deviceId}/brightness?brightness=${params.brightness}`;
                } else if (action === 'tv_on') {
                    url = `/tv/${deviceId}/turn_on`;
                } else if (action === 'tv_off') {
                    url = `/tv/${deviceId}/turn_off`;
                }
                
                try {
                    const response = await fetch(url, { method });
                    const result = await response.json();
                    console.log(result);
                    // Reload the page to show updated status
                    location.reload();
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred. Please try again.');
                }
            }
        </script>
    </head>
    <body>
        <h1>Home Automation Dashboard</h1>
    """

    # Add each room
    for room_name, room_devices in rooms.items():
        html_content += f"""
        <div class="room">
            <div class="room-title">{room_name}</div>
        """

        # Add each device
        for device in room_devices:
            device_id = device["id"]
            status = device["status"]
            device_type = status.get("type", "unknown")
            device_name = status.get("name", device_id)
            power = status.get("power", False)
            power_text = "On" if power else "Off"

            html_content += f"""
            <div class="device">
                <div>
                    <div class="device-name">{device_name}</div>
                    <div class="device-status">Status: {power_text}</div>
                </div>
                <div class="device-controls">
            """

            if device_type == "light":
                brightness = status.get("brightness", 0)
                html_content += f"""
                    <button onclick="controlDevice('{device_id}', 'turn_on')">Turn On</button>
                    <button class="off" onclick="controlDevice('{device_id}', 'turn_off')">Turn Off</button>
                    <select onchange="controlDevice('{device_id}', 'set_brightness', {{brightness: this.value}})">
                        <option value="">Brightness</option>
                        <option value="20">20%</option>
                        <option value="40">40%</option>
                        <option value="60">60%</option>
                        <option value="80">80%</option>
                        <option value="100">100%</option>
                    </select>
                """
            elif device_type == "tv":
                html_content += f"""
                    <button onclick="controlDevice('{device_id}', 'tv_on')">Turn On</button>
                    <button class="off" onclick="controlDevice('{device_id}', 'tv_off')">Turn Off</button>
                """

            html_content += """
                </div>
            </div>
            """

        html_content += """
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    return html_content
