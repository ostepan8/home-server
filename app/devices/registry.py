# app/devices/registry.py
import os
import json
import asyncio
from typing import Dict, List, Optional, Any
import aiofiles
from app.config import settings
from app.devices.lights import YeelightController
from app.devices.tv import RokuController
import logging

logger = logging.getLogger(__name__)


class DeviceRegistry:
    """Central registry for all devices"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeviceRegistry, cls).__new__(cls)
            cls._instance.devices = {}
            cls._instance.initialized = False
        return cls._instance

    async def load_devices(self):
        """Load devices from file"""
        if os.path.exists(settings.DEVICES_FILE):
            try:
                async with aiofiles.open(settings.DEVICES_FILE, mode="r") as f:
                    content = await f.read()
                    device_data = json.loads(content)

                    # Initialize controllers
                    for device_id, device in device_data.items():
                        await self.create_device_controller(
                            device_id, device["type"], device.get("config", {})
                        )

                    logger.info(f"Loaded {len(device_data)} devices from file")
            except Exception as e:
                logger.error(f"Error loading devices: {e}")

        # Initialize devices from environment variables if none were loaded
        if not self.devices:
            print("Discovering devices")
            await self.discover_devices()

        self.initialized = True

    async def save_devices(self):
        """Save devices to file"""
        try:
            device_data = {}

            for device_id, controller in self.devices.items():
                device_info = {
                    "id": device_id,
                    "type": controller.type,
                    "name": (
                        controller.name if hasattr(controller, "name") else device_id
                    ),
                    "config": controller.get_config(),
                }

                if hasattr(controller, "room"):
                    device_info["room"] = controller.room

                device_data[device_id] = device_info

            async with aiofiles.open(settings.DEVICES_FILE, mode="w") as f:
                await f.write(json.dumps(device_data, indent=2))

            logger.info(f"Saved {len(device_data)} devices to file")
        except Exception as e:
            logger.error(f"Error saving devices: {e}")

    async def discover_devices(self):
        """Discover devices from configuration"""
        # Add Yeelight devices
        for idx, light_info in enumerate(settings.YEELIGHT_IP_ADDRESSES):
            try:
                # Create a unique ID for each light based on room and position
                room_name = light_info["room"]
                device_id = f"light_{idx+1}"  # Keep consistent IDs for now

                await self.create_device_controller(
                    device_id,
                    "light",
                    {
                        "ip_address": light_info["ip"],
                        "name": room_name,  # Use the room name as the light name
                        "room": room_name,  # Set the correct room
                    },
                )
                logger.info(f"Added light controller for {device_id} in {room_name}")

                # Add a small delay between device initializations
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error adding Yeelight at {light_info['ip']}: {e}")

        # Add Roku TV
        if settings.ROKU_IP_ADDRESS:
            try:
                await self.create_device_controller(
                    "tv_1",
                    "tv",
                    {
                        "ip_address": settings.ROKU_IP_ADDRESS,
                        "name": "Main TV",
                        "room": "Living Room",
                    },
                )
                logger.info(f"Added TV controller using IP {settings.ROKU_IP_ADDRESS}")
            except Exception as e:
                logger.error(f"Error adding Roku TV: {e}")

    async def create_device_controller(
        self, device_id: str, device_type: str, config: Dict[str, Any]
    ):
        """Create a controller for a device"""
        try:
            if device_type == "light":
                controller = YeelightController(
                    ip_address=config["ip_address"],
                    name=config.get("name", device_id),
                    room=config.get("room", "Unknown"),
                )
                self.devices[device_id] = controller
                logger.info(f"Added light controller for {device_id}")

            elif device_type == "tv":
                controller = RokuController(
                    ip_address=config["ip_address"], name=config.get("name", device_id)
                )
                self.devices[device_id] = controller
                logger.info(f"Added TV controller for {device_id}")

            else:
                logger.error(f"Unknown device type: {device_type}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error creating controller for {device_id}: {e}")
            return False

    def get_device(self, device_id: str):
        """Get a device controller by ID"""
        return self.devices.get(device_id)

    def get_all_devices(self):
        """Get all device controllers"""
        return self.devices

    def get_devices_by_type(self, device_type: str):
        """Get all devices of a specific type"""
        return {
            device_id: controller
            for device_id, controller in self.devices.items()
            if hasattr(controller, "type") and controller.type == device_type
        }

    def get_devices_by_room(self, room: str):
        """Get all devices in a specific room"""
        return {
            device_id: controller
            for device_id, controller in self.devices.items()
            if hasattr(controller, "room") and controller.room.lower() == room.lower()
        }

    async def get_status_for_all_devices(self):
        """Get status for all devices"""
        statuses = {}

        for device_id, controller in self.devices.items():
            try:
                status = await controller.get_status()
                statuses[device_id] = status
            except Exception as e:
                logger.error(f"Error getting status for {device_id}: {e}")
                statuses[device_id] = {"error": str(e), "status": "error"}

        return statuses
