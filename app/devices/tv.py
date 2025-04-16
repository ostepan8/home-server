# app/devices/tv.py
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
import re
import logging
import os

logger = logging.getLogger(__name__)

# Content provider mapping
TMDB_PROVIDER_MAPPING = {
    "Netflix": {"provider_id": 8, "roku_app_name": "Netflix"},
    "Hulu": {"provider_id": 15, "roku_app_name": "Hulu"},
    "Amazon Prime Video": {"provider_id": 9, "roku_app_name": "Prime Video"},
    "Disney Plus": {"provider_id": 337, "roku_app_name": "Disney Plus"},
    "HBO Max": {"provider_id": 384, "roku_app_name": "HBO Max"},
    "Apple TV Plus": {"provider_id": 350, "roku_app_name": "Apple TV"},
    "Peacock": {"provider_id": 386, "roku_app_name": "Peacock TV"},
    "Paramount Plus": {"provider_id": 531, "roku_app_name": "Paramount Plus"},
    "YouTube": {"provider_id": 192, "roku_app_name": "YouTube"},
    "YouTube TV": {"provider_id": 363, "roku_app_name": "YouTube TV"},
}


class RokuController:
    """Controller for Roku TV devices"""

    def __init__(
        self,
        ip_address: str,
        name: str = "",
        tmdb_api_key: Optional[str] = None,
        room: str = "Living Room",
    ):
        self.ip_address = ip_address
        self.name = name
        self.type = "tv"
        self.room = room
        self.base_url = f"http://{ip_address}:8060"
        self.tmdb_api_key = tmdb_api_key or os.getenv("TMDB_API_KEY")
        self.tmdb_api_url = "https://api.themoviedb.org/3"
        self.tmdb_provider_region = "US"  # Change to your region code if necessary

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
                            "room": self.room,
                        }
                    else:
                        return {
                            "error": f"HTTP error: {response.status}",
                            "status": "error",
                            "name": self.name,
                            "type": self.type,
                            "ip_address": self.ip_address,
                            "room": self.room,
                        }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "name": self.name,
                "type": self.type,
                "ip_address": self.ip_address,
                "room": self.room,
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
        return {"ip_address": self.ip_address, "name": self.name, "room": self.room}

    # New methods below for enhanced TV control functionality

    async def search_movie_providers(self, movie_name: str) -> List[str]:
        """
        Searches for the movie on various streaming providers using TMDb API.

        Args:
            movie_name (str): The name of the movie.

        Returns:
            list: A list of provider names where the movie is available.
        """
        if not self.tmdb_api_key:
            logger.error("TMDB API key not found")
            return []

        headers = {"User-Agent": "SmartHomeControl/1.0"}
        try:
            # Step 1: Search for the movie ID
            search_url = f"{self.tmdb_api_url}/search/movie"
            search_params = {
                "api_key": self.tmdb_api_key,
                "query": movie_name,
                "language": "en-US",
                "page": 1,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    search_url, params=search_params, headers=headers
                ) as search_response:
                    if search_response.status == 200:
                        search_data = await search_response.json()
                        if "results" in search_data and len(search_data["results"]) > 0:
                            movie_id = search_data["results"][0]["id"]
                        else:
                            logger.info(f"No results found for '{movie_name}'.")
                            return []
                    else:
                        logger.error(f"TMDb search API error: {search_response.status}")
                        return []

                # Step 2: Get the providers for the movie
                provider_url = f"{self.tmdb_api_url}/movie/{movie_id}/watch/providers"
                provider_params = {"api_key": self.tmdb_api_key}

                async with session.get(
                    provider_url, params=provider_params, headers=headers
                ) as provider_response:
                    if provider_response.status == 200:
                        provider_data = await provider_response.json()
                        if self.tmdb_provider_region in provider_data.get(
                            "results", {}
                        ):
                            providers_info = provider_data["results"][
                                self.tmdb_provider_region
                            ]
                            providers = set()

                            for provider_type in [
                                "flatrate",
                                "ads",
                                "free",
                                "rent",
                                "buy",
                            ]:
                                if provider_type in providers_info:
                                    for provider in providers_info[provider_type]:
                                        provider_name = provider["provider_name"]
                                        if provider_name in TMDB_PROVIDER_MAPPING:
                                            providers.add(provider_name)

                            return list(providers)
                        else:
                            logger.info(
                                f"No providers found in region '{self.tmdb_provider_region}'."
                            )
                            return []
                    else:
                        logger.error(
                            f"TMDb provider API error: {provider_response.status}"
                        )
                        return []

        except Exception as e:
            logger.error(f"Error querying TMDb API: {e}")
            return []

    async def search_tv_show_providers(self, tv_show_name: str) -> List[str]:
        """
        Searches for the TV show on various streaming providers using TMDb API.

        Args:
            tv_show_name (str): The name of the TV show.

        Returns:
            list: A list of provider names where the show is available.
        """
        if not self.tmdb_api_key:
            logger.error("TMDB API key not found")
            return []

        headers = {"User-Agent": "SmartHomeControl/1.0"}
        try:
            # Step 1: Search for the TV show ID
            search_url = f"{self.tmdb_api_url}/search/tv"
            search_params = {
                "api_key": self.tmdb_api_key,
                "query": tv_show_name,
                "language": "en-US",
                "page": 1,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    search_url, params=search_params, headers=headers
                ) as search_response:
                    if search_response.status == 200:
                        search_data = await search_response.json()
                        if "results" in search_data and len(search_data["results"]) > 0:
                            tv_show_id = search_data["results"][0]["id"]
                        else:
                            logger.info(f"No results found for '{tv_show_name}'.")
                            return []
                    else:
                        logger.error(f"TMDb search API error: {search_response.status}")
                        return []

                # Step 2: Get the providers for the TV show
                provider_url = f"{self.tmdb_api_url}/tv/{tv_show_id}/watch/providers"
                provider_params = {"api_key": self.tmdb_api_key}

                async with session.get(
                    provider_url, params=provider_params, headers=headers
                ) as provider_response:
                    if provider_response.status == 200:
                        provider_data = await provider_response.json()
                        if self.tmdb_provider_region in provider_data.get(
                            "results", {}
                        ):
                            providers_info = provider_data["results"][
                                self.tmdb_provider_region
                            ]
                            providers = set()

                            for provider_type in [
                                "flatrate",
                                "ads",
                                "free",
                                "rent",
                                "buy",
                            ]:
                                if provider_type in providers_info:
                                    for provider in providers_info[provider_type]:
                                        provider_name = provider["provider_name"]
                                        if provider_name in TMDB_PROVIDER_MAPPING:
                                            providers.add(provider_name)

                            return list(providers)
                        else:
                            logger.info(
                                f"No providers found in region '{self.tmdb_provider_region}'."
                            )
                            return []
                    else:
                        logger.error(
                            f"TMDb provider API error: {provider_response.status}"
                        )
                        return []

        except Exception as e:
            logger.error(f"Error querying TMDb API: {e}")
            return []

    async def play_content(
        self, content_type: str, content_name: str
    ) -> Dict[str, Any]:
        """
        Attempt to play specific content (movie or TV show) by finding it on a streaming service.

        Args:
            content_type (str): Type of content ("movie" or "tv_show")
            content_name (str): Name of the content to play

        Returns:
            dict: Result of the operation
        """
        # First go home
        await self.send_keypress("Home")
        await asyncio.sleep(1)  # Give the TV time to respond

        # Search for providers
        providers = []
        if content_type.lower() == "movie":
            providers = await self.search_movie_providers(content_name)
        elif content_type.lower() == "tv_show":
            providers = await self.search_tv_show_providers(content_name)

        if not providers:
            return {
                "status": "error",
                "message": f"Could not find '{content_name}' on available streaming services.",
            }

        # Try to launch the first available provider
        for provider in providers:
            provider_info = TMDB_PROVIDER_MAPPING.get(provider)
            if provider_info:
                app_name = provider_info["roku_app_name"]
                # Launch the app
                launch_result = await self.launch_app_by_name(app_name)

                if launch_result.get("status") == "success":
                    # For supported apps like Hulu, try to navigate to search
                    if app_name.lower() == "hulu":
                        await self.navigate_hulu_search(content_name)

                    return {
                        "status": "success",
                        "provider": provider,
                        "app": app_name,
                        "content": content_name,
                        "message": f"Launched {app_name} for '{content_name}'",
                    }

        return {
            "status": "error",
            "message": f"Failed to launch a streaming service for '{content_name}'.",
        }

    async def navigate_hulu_search(self, search_term: str) -> Dict[str, Any]:
        """
        Navigate to the search function in Hulu and input a search term

        Args:
            search_term (str): The term to search for
        """
        # Wait for Hulu to load
        await asyncio.sleep(7)

        # Navigate to search
        await self.send_keypress("Select")
        await asyncio.sleep(3.5)
        await self.send_keypress("Left")
        await asyncio.sleep(0.2)
        await self.send_keypress("Up")
        await asyncio.sleep(0.2)
        await self.send_keypress("Select")
        await asyncio.sleep(0.2)

        # Very simplified keyboard navigation for the example
        # In reality you'd want to implement the full keyboard grid logic from the pasted code
        search_term = search_term.lower()
        for char in search_term[:5]:  # Just first 5 chars as example
            if char.isalpha():
                # This is a very simplified version - the real implementation would
                # calculate the path to each character on the keyboard grid
                await self.send_keypress("Right")
                await asyncio.sleep(0.2)
                await self.send_keypress("Select")
                await asyncio.sleep(0.2)

        # Navigate to search button and select
        for _ in range(3):  # Move to the right to reach search button
            await self.send_keypress("Right")
            await asyncio.sleep(0.2)

        await self.send_keypress("Select")  # Submit search
        await asyncio.sleep(1)

        return {"status": "success", "message": f"Searched for '{search_term}' on Hulu"}

    async def change_channel(self, channel_number: str) -> Dict[str, Any]:
        """
        Change to a specific channel number

        Args:
            channel_number (str): The channel number to change to

        Returns:
            dict: Result of the operation
        """
        results = []
        for digit in channel_number:
            if digit.isdigit():
                result = await self.send_keypress(f"Lit_{digit}")
                results.append(result)
                await asyncio.sleep(0.2)

        return {"status": "success", "channel": channel_number, "results": results}

    async def search_and_play(self, search_term: str) -> Dict[str, Any]:
        """
        Search for content and try to play it

        Args:
            search_term (str): The content to search for

        Returns:
            dict: Result of the operation
        """
        # First try as a movie
        movie_providers = await self.search_movie_providers(search_term)
        if movie_providers:
            return await self.play_content("movie", search_term)

        # Then try as a TV show
        tv_providers = await self.search_tv_show_providers(search_term)
        if tv_providers:
            return await self.play_content("tv_show", search_term)

        return {
            "status": "error",
            "message": f"Could not find '{search_term}' on any available streaming service.",
        }

    async def control_playback(self, action: str) -> Dict[str, Any]:
        """
        Control media playback

        Args:
            action (str): The playback action (play, pause, stop, rewind, forward)

        Returns:
            dict: Result of the operation
        """
        action_mapping = {
            "play": "Play",
            "pause": "Play",  # Play/Pause is typically the same button
            "stop": "Stop",
            "rewind": "Rev",
            "forward": "Fwd",
        }

        key = action_mapping.get(action.lower())
        if not key:
            return {"status": "error", "error": f"Invalid playback action: {action}"}

        return await self.send_keypress(key)

    async def find_remote(self) -> Dict[str, Any]:
        """
        Send a command to trigger the Roku remote finder feature

        Returns:
            dict: Result of the operation
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/findremote") as response:
                    if response.status == 200:
                        return {
                            "status": "success",
                            "message": "Remote finder activated",
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"HTTP error: {response.status}",
                        }
        except Exception as e:
            logger.error(f"Error activating remote finder: {e}")
            return {"status": "error", "error": str(e)}

    async def set_volume_multi(self, action: str, amount: int = 1) -> Dict[str, Any]:
        """
        Adjust volume multiple times in one command

        Args:
            action (str): 'up' or 'down'
            amount (int): Number of volume steps to adjust

        Returns:
            dict: Result of the operation
        """
        results = []
        key = "VolumeUp" if action.lower() == "up" else "VolumeDown"

        for _ in range(amount):
            result = await self.send_keypress(key)
            results.append(result)
            await asyncio.sleep(0.1)  # Small delay between keypresses

        return {
            "status": "success",
            "action": f"volume_{action.lower()}",
            "amount": amount,
            "results": results,
        }

    async def get_current_app(self) -> Dict[str, Any]:
        """
        Get information about the currently running app

        Returns:
            dict: Information about the current app
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/query/active-app") as response:
                    if response.status == 200:
                        xml_text = await response.text()

                        # Basic XML parsing to extract app info
                        app_id_match = re.search(r'<app id="([^"]+)"', xml_text)
                        app_name_match = re.search(
                            r'<app id="[^"]+">([^<]+)</app>', xml_text
                        )

                        if app_id_match and app_name_match:
                            return {
                                "status": "success",
                                "app_id": app_id_match.group(1),
                                "app_name": app_name_match.group(1),
                            }
                        else:
                            return {
                                "status": "error",
                                "error": "Could not parse app info",
                            }
                    else:
                        return {
                            "status": "error",
                            "error": f"HTTP error: {response.status}",
                        }
        except Exception as e:
            logger.error(f"Error getting current app: {e}")
            return {"status": "error", "error": str(e)}
