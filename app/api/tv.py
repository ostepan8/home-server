# app/api/tv.py
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from app.devices.registry import DeviceRegistry

router = APIRouter()
registry = DeviceRegistry()


@router.get("/")
async def get_all_tvs():
    """Get all TVs"""
    tv_devices = registry.get_devices_by_type("tv")

    # Get the status for each TV
    result = {}
    for device_id, controller in tv_devices.items():
        try:
            status = await controller.get_status()
            result[device_id] = status
        except Exception as e:
            result[device_id] = {"status": "error", "error": str(e)}

    return result


@router.get("/{tv_id}")
async def get_tv(tv_id: str):
    """Get a specific TV"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.get_status()


@router.post("/{tv_id}/keypress/{key}")
async def send_keypress(tv_id: str, key: str):
    """Send a keypress to a TV"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.send_keypress(key)


@router.post("/{tv_id}/launch_app/{app_id}")
async def launch_app(tv_id: str, app_id: str):
    """Launch an app on a TV by ID"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.launch_app(app_id)


@router.post("/{tv_id}/launch_app_by_name")
async def launch_app_by_name(tv_id: str, app_name: str = Query(...)):
    """Launch an app on a TV by name"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.launch_app_by_name(app_name)


@router.get("/{tv_id}/apps")
async def get_apps(tv_id: str):
    """Get a list of installed apps on a TV"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.get_apps()


@router.post("/{tv_id}/turn_on")
async def turn_on_tv(tv_id: str):
    """Turn on a TV"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.turn_on()


@router.post("/{tv_id}/turn_off")
async def turn_off_tv(tv_id: str):
    """Turn off a TV"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.turn_off()


@router.post("/{tv_id}/volume_up")
async def volume_up(
    tv_id: str, amount: int = Query(1, description="Number of volume steps")
):
    """Increase TV volume"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    results = []
    for _ in range(amount):
        result = await tv.volume_up()
        results.append(result)

    return {"status": "success", "actions": amount, "results": results}


@router.post("/{tv_id}/volume_down")
async def volume_down(
    tv_id: str, amount: int = Query(1, description="Number of volume steps")
):
    """Decrease TV volume"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    results = []
    for _ in range(amount):
        result = await tv.volume_down()
        results.append(result)

    return {"status": "success", "actions": amount, "results": results}


@router.post("/{tv_id}/navigate/{direction}")
async def navigate(tv_id: str, direction: str):
    """Navigate in a direction (up, down, left, right, select, back, home)"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.navigate(direction)


@router.post("/{tv_id}/play_content")
async def play_content(
    tv_id: str,
    content_type: str = Query(..., description="Type of content (movie or tv_show)"),
    content_name: str = Query(..., description="Name of the content to play"),
):
    """Play a specific movie or TV show"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    # Check for play_content method in the TV controller
    if not hasattr(tv, "play_content"):
        # Fall back to a generic implementation using the pasted code logic
        await tv.send_keypress("Home")  # First go to home

        # Find suitable app for content based on content_type
        if content_type.lower() == "movie":
            # Logic to search for movie content providers
            return {
                "status": "searching",
                "message": f"Searching for movie: {content_name}",
            }
        elif content_type.lower() == "tv_show":
            # Logic to search for TV show content providers
            return {
                "status": "searching",
                "message": f"Searching for TV show: {content_name}",
            }
        else:
            raise HTTPException(
                status_code=400, detail="Invalid content type. Use 'movie' or 'tv_show'"
            )

    return await tv.play_content(content_type, content_name)


@router.post("/{tv_id}/playback_control")
async def playback_control(
    tv_id: str,
    action: str = Query(
        ..., description="Playback action (play, pause, stop, rewind, forward)"
    ),
):
    """Control media playback"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    action_mapping = {
        "play": "Play",
        "pause": "Play",  # Play/Pause is typically the same button
        "stop": "Stop",
        "rewind": "Rev",
        "forward": "Fwd",
    }

    key = action_mapping.get(action.lower())
    if not key:
        raise HTTPException(
            status_code=400, detail=f"Invalid playback action: {action}"
        )

    return await tv.send_keypress(key)


@router.post("/{tv_id}/channel/{channel_number}")
async def change_channel(tv_id: str, channel_number: str):
    """Change to a specific channel"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    # Send digits one by one
    results = []
    for digit in channel_number:
        if digit.isdigit():
            result = await tv.send_keypress(f"Lit_{digit}")
            results.append(result)

    return {"status": "success", "channel": channel_number, "results": results}


@router.post("/{tv_id}/search_content")
async def search_content(
    tv_id: str,
    query: str = Query(..., description="Search term"),
    provider: Optional[str] = Query(
        None, description="Specific provider to search on (e.g., Netflix, Hulu)"
    ),
):
    """Search for content on a specific provider or across providers"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    # First go to home
    await tv.send_keypress("Home")

    if provider:
        # Launch the specific provider
        launch_result = await tv.launch_app_by_name(provider)
        if launch_result.get("status") == "error":
            return {
                "status": "error",
                "message": f"Could not launch {provider}",
                "details": launch_result,
            }

        # Search implementation would depend on the specific provider
        # For now, return a status indicating we've launched the app
        return {
            "status": "launched",
            "provider": provider,
            "message": f"Launched {provider}, please use the search function in the app",
        }
    else:
        # If no provider specified, use the Roku global search
        await tv.send_keypress("Search")

        # Return instructions - actual keyboard input would need a more complex implementation
        return {
            "status": "search_ready",
            "message": "Search screen launched, use remote controls to input search term",
        }
