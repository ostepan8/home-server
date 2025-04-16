# app/devices/tv.py
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
import re
import logging

logger = logging.getLogger(__name__)


class RokuController:
    """Controller for Roku TV devices"""

    def __init__(self, ip_address: str, name: str = ""):
        self.ip_address = ip_address
        self.name = name
        self.type = "tv"
        self.base_url = f"http://{ip_address}:8060"

    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the TV"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/query/device-info"
                ) as response:
                    if response.status == 200:
                        # Parse the XML response
                        xml_text = await response.text()

                        # Very basic XML parsing to extract power state
                        power_state = (
                            "on"
                            if "<power-mode>PowerOn</power-mode>" in xml_text
                            else "off"
                        )

                        return {
                            "power": power_state == "on",
                            "name": self.name,
                            "type": self.type,
                            "ip_address": self.ip_address,
                        }
                    else:
                        return {
                            "error": f"HTTP error: {response.status}",
                            "status": "error",
                            "name": self.name,
                            "type": self.type,
                            "ip_address": self.ip_address,
                        }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "name": self.name,
                "type": self.type,
                "ip_address": self.ip_address,
            }

    async def send_keypress(self, key: str) -> Dict[str, Any]:
        """Send a keypress to the TV"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/keypress/{key}") as response:
                    if response.status == 200:
                        return {"status": "success", "key": key}
                    else:
                        return {
                            "status": "error",
                            "error": f"HTTP error: {response.status}",
                        }
        except Exception as e:
            logger.error(f"Error sending keypress {key}: {e}")
            return {"status": "error", "error": str(e)}

    async def launch_app(self, app_id: str) -> Dict[str, Any]:
        """Launch an app on the TV"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/launch/{app_id}") as response:
                    if response.status == 200:
                        return {"status": "success", "app_id": app_id}
                    else:
                        return {
                            "status": "error",
                            "error": f"HTTP error: {response.status}",
                        }
        except Exception as e:
            logger.error(f"Error launching app {app_id}: {e}")
            return {"status": "error", "error": str(e)}

    async def get_apps(self) -> List[Dict[str, Any]]:
        """Get a list of installed apps"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/query/apps") as response:
                    if response.status == 200:
                        xml_text = await response.text()

                        # Basic XML parsing to extract apps
                        app_pattern = r'<app id="([^"]+)"[^>]*>([^<]+)</app>'
                        apps = []

                        for match in re.finditer(app_pattern, xml_text):
                            app_id = match.group(1)
                            app_name = match.group(2)
                            apps.append({"id": app_id, "name": app_name})

                        return apps
                    else:
                        logger.error(f"HTTP error getting apps: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error getting apps: {e}")
            return []

    async def turn_on(self) -> Dict[str, Any]:
        """Turn on the TV"""
        return await self.send_keypress("PowerOn")

    async def turn_off(self) -> Dict[str, Any]:
        """Turn off the TV"""
        return await self.send_keypress("PowerOff")

    async def toggle_power(self) -> Dict[str, Any]:
        """Toggle the power state"""
        return await self.send_keypress("Power")

    async def volume_up(self) -> Dict[str, Any]:
        """Increase the volume"""
        return await self.send_keypress("VolumeUp")

    async def volume_down(self) -> Dict[str, Any]:
        """Decrease the volume"""
        return await self.send_keypress("VolumeDown")

    async def navigate(self, direction: str) -> Dict[str, Any]:
        """Navigate in the specified direction"""
        valid_directions = ["up", "down", "left", "right", "select", "back", "home"]
        if direction.lower() in valid_directions:
            return await self.send_keypress(direction.capitalize())
        else:
            return {"status": "error", "error": f"Invalid direction: {direction}"}

    async def launch_app_by_name(self, app_name: str) -> Dict[str, Any]:
        """Launch an app by its name"""
        apps = await self.get_apps()

        # Find the app with a matching name
        for app in apps:
            if app["name"].lower() == app_name.lower():
                return await self.launch_app(app["id"])

        return {"status": "error", "error": f"App not found: {app_name}"}

    def get_config(self) -> Dict[str, Any]:
        """Get configuration data for this device"""
        return {"ip_address": self.ip_address, "name": self.name}
