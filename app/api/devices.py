# app/api/devices.py
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from app.devices.registry import DeviceRegistry

router = APIRouter()
registry = DeviceRegistry()


@router.get("/")
async def get_all_devices():
    """Get all devices"""
    devices = registry.get_all_devices()

    # Get the status for each device
    result = {}
    for device_id, controller in devices.items():
        try:
            status = await controller.get_status()
            result[device_id] = status
        except Exception as e:
            result[device_id] = {"status": "error", "error": str(e)}

    return result


@router.get("/{device_id}")
async def get_device(device_id: str):
    """Get a specific device"""
    device = registry.get_device(device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return await device.get_status()


@router.post("/{device_id}/state")
async def update_device_state(device_id: str, state: Dict[str, Any]):
    """Update a device's state"""
    device = registry.get_device(device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return await device.set_state(**state)


@router.get("/room/{room}")
async def get_devices_by_room(room: str):
    """Get all devices in a room"""
    devices = registry.get_devices_by_room(room)

    # Get the status for each device
    result = {}
    for device_id, controller in devices.items():
        try:
            status = await controller.get_status()
            result[device_id] = status
        except Exception as e:
            result[device_id] = {"status": "error", "error": str(e)}

    return result
