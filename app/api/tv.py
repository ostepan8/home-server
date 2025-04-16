# app/api/tv.py
from fastapi import APIRouter, HTTPException
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
async def launch_app_by_name(tv_id: str, app_name: str):
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
async def volume_up(tv_id: str):
    """Increase TV volume"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.volume_up()


@router.post("/{tv_id}/volume_down")  # Add this decorator
async def volume_down(tv_id: str):
    """Decrease TV volume"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.volume_down()


@router.post("/{tv_id}/navigate/{direction}")
async def navigate(tv_id: str, direction: str):
    """Navigate in a direction (up, down, left, right, select, back, home)"""
    tv = registry.get_device(tv_id)

    if not tv or not hasattr(tv, "type") or tv.type != "tv":
        raise HTTPException(status_code=404, detail="TV not found")

    return await tv.navigate(direction)
