# app/api/lights.py
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from app.devices.registry import DeviceRegistry

router = APIRouter()
registry = DeviceRegistry()


@router.get("/")
async def get_all_lights():
    """Get all lights"""
    light_devices = registry.get_devices_by_type("light")

    # Get the status for each light
    result = {}
    for device_id, controller in light_devices.items():
        try:
            status = await controller.get_status()
            result[device_id] = status
        except Exception as e:
            result[device_id] = {"status": "error", "error": str(e)}

    return result


@router.get("/{light_id}")
async def get_light(light_id: str):
    """Get a specific light"""
    light = registry.get_device(light_id)

    if not light or not hasattr(light, "type") or light.type != "light":
        raise HTTPException(status_code=404, detail="Light not found")

    return await light.get_status()


@router.post("/{light_id}/turn_on")
async def turn_on_light(light_id: str):
    """Turn on a light"""
    light = registry.get_device(light_id)

    if not light or not hasattr(light, "type") or light.type != "light":
        raise HTTPException(status_code=404, detail="Light not found")

    return await light.turn_on()


@router.post("/{light_id}/turn_off")
async def turn_off_light(light_id: str):
    """Turn off a light"""
    light = registry.get_device(light_id)

    if not light or not hasattr(light, "type") or light.type != "light":
        raise HTTPException(status_code=404, detail="Light not found")

    return await light.turn_off()


@router.post("/{light_id}/brightness")
async def set_light_brightness(light_id: str, brightness: int):
    """Set a light's brightness"""
    light = registry.get_device(light_id)

    if not light or not hasattr(light, "type") or light.type != "light":
        raise HTTPException(status_code=404, detail="Light not found")

    return await light.set_state(brightness=brightness)


@router.post("/{light_id}/color")
async def set_light_color(light_id: str, r: int, g: int, b: int):
    """Set a light's color"""
    light = registry.get_device(light_id)

    if not light or not hasattr(light, "type") or light.type != "light":
        raise HTTPException(status_code=404, detail="Light not found")

    return await light.set_state(rgb=[r, g, b])


@router.post("/room/{room}/turn_on")
async def turn_on_room_lights(room: str):
    """Turn on all lights in a room"""
    room_devices = registry.get_devices_by_room(room)

    light_devices = {
        device_id: controller
        for device_id, controller in room_devices.items()
        if hasattr(controller, "type") and controller.type == "light"
    }

    # Turn on each light
    results = {}
    for device_id, controller in light_devices.items():
        try:
            status = await controller.turn_on()
            results[device_id] = status
        except Exception as e:
            results[device_id] = {"status": "error", "error": str(e)}

    return results


@router.post("/room/{room}/turn_off")
async def turn_off_room_lights(room: str):
    """Turn off all lights in a room"""
    room_devices = registry.get_devices_by_room(room)

    light_devices = {
        device_id: controller
        for device_id, controller in room_devices.items()
        if hasattr(controller, "type") and controller.type == "light"
    }

    # Turn off each light
    results = {}
    for device_id, controller in light_devices.items():
        try:
            status = await controller.turn_off()
            results[device_id] = status
        except Exception as e:
            results[device_id] = {"status": "error", "error": str(e)}

    return results
