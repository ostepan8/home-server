# app/devices/lights.py
from typing import Dict, Any, Optional, Union
from yeelight import Bulb
import asyncio
import time


class YeelightController:
    """Controller for Yeelight bulbs"""

    def __init__(self, ip_address: Union[str, Dict], name: str = "", room: str = ""):
        # Handle both string and dictionary IP address formats
        if isinstance(ip_address, dict) and "ip" in ip_address:
            self.ip_address = ip_address["ip"]
            # If room is not provided but is in the IP address dictionary, use that
            if not room and "room" in ip_address:
                room = ip_address["room"]
        else:
            self.ip_address = ip_address

        self.name = name
        self.room = room
        self.type = "light"
        self.bulb = Bulb(
            self.ip_address, effect="smooth", duration=300
        )  # Smoother transitions
        self.last_command_time = 0
        self.min_command_interval = 0.5  # Minimum time between commands in seconds

    async def _rate_limit(self):
        """Ensure we don't flood the device with commands"""
        current_time = time.time()
        time_since_last = current_time - self.last_command_time
        if time_since_last < self.min_command_interval:
            await asyncio.sleep(self.min_command_interval - time_since_last)
        self.last_command_time = time.time()

    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the light"""
        await self._rate_limit()

        try:
            # Run in a separate thread since Yeelight lib is blocking
            loop = asyncio.get_running_loop()
            properties = await loop.run_in_executor(None, self.bulb.get_properties)

            return {
                "power": properties.get("power") == "on",
                "brightness": int(properties.get("bright", 100)),
                "color_temp": int(properties.get("ct", 4000)),
                "rgb": properties.get("rgb", "0"),
                "name": self.name,
                "room": self.room,
                "type": self.type,
                "ip_address": self.ip_address,
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "name": self.name,
                "room": self.room,
                "type": self.type,
                "ip_address": self.ip_address,
            }

    async def set_state(self, **kwargs) -> Dict[str, Any]:
        """Update the state of the light"""
        await self._rate_limit()
        loop = asyncio.get_running_loop()

        try:
            # Process each parameter
            if "power" in kwargs:
                if kwargs["power"]:
                    await loop.run_in_executor(None, self.bulb.turn_on)
                else:
                    await loop.run_in_executor(None, self.bulb.turn_off)

            if "brightness" in kwargs and kwargs.get("power") != False:
                brightness = min(max(int(kwargs["brightness"]), 1), 100)
                await loop.run_in_executor(
                    None, lambda: self.bulb.set_brightness(brightness)
                )

            if "color_temp" in kwargs and kwargs.get("power") != False:
                color_temp = int(kwargs["color_temp"])
                await loop.run_in_executor(
                    None, lambda: self.bulb.set_color_temp(color_temp)
                )

            if "rgb" in kwargs and kwargs.get("power") != False:
                r, g, b = kwargs["rgb"]
                await loop.run_in_executor(None, lambda: self.bulb.set_rgb(r, g, b))

            # Add a small delay after commands to avoid flooding the network
            await asyncio.sleep(0.2)

            return await self.get_status()
        except Exception as e:
            return {"error": str(e), "status": "error"}

    async def turn_on(self) -> Dict[str, Any]:
        """Turn the light on"""
        return await self.set_state(power=True)

    async def turn_off(self) -> Dict[str, Any]:
        """Turn the light off"""
        return await self.set_state(power=False)

    def get_config(self) -> Dict[str, Any]:
        """Get configuration data for this device"""
        return {"ip_address": self.ip_address, "name": self.name, "room": self.room}
