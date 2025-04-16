# app/api/rooms.py
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from app.devices.registry import DeviceRegistry
from pydantic import BaseModel

router = APIRouter()
registry = DeviceRegistry()


class RoomModel(BaseModel):
    name: str


@router.get("/")
async def get_all_rooms():
    """Get all rooms with their devices"""
    # Get all devices
    devices = registry.get_all_devices()

    # Group devices by room
    rooms = {}
    for device_id, controller in devices.items():
        if hasattr(controller, "room"):
            room = controller.room
            if room not in rooms:
                rooms[room] = []
            rooms[room].append(device_id)

    return rooms


@router.get("/{room}")
async def get_room_devices(room: str):
    """Get all devices in a room"""
    return await registry.get_devices_by_room(room)


@router.post("/{device_id}/set_room")
async def set_device_room(device_id: str, room_model: RoomModel):
    """Assign a device to a room"""
    device = registry.get_device(device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Update the room
    if hasattr(device, "room"):
        device.room = room_model.name

        # Save the updated configuration
        await registry.save_devices()

        return {"status": "success", "device_id": device_id, "room": room_model.name}
    else:
        raise HTTPException(
            status_code=400, detail="Device doesn't support room assignment"
        )


@router.post("/{room}/all/turn_on")
async def turn_on_all_room_devices(room: str):
    """Turn on all devices in a room"""
    room_devices = registry.get_devices_by_room(room)

    # Turn on each device
    results = {}
    for device_id, controller in room_devices.items():
        try:
            if hasattr(controller, "turn_on"):
                status = await controller.turn_on()
                results[device_id] = status
        except Exception as e:
            results[device_id] = {"status": "error", "error": str(e)}

    return results


@router.post("/{room}/all/turn_off")
async def turn_off_all_room_devices(room: str):
    """Turn off all devices in a room"""
    room_devices = registry.get_devices_by_room(room)

    # Turn off each device
    results = {}
    for device_id, controller in room_devices.items():
        try:
            if hasattr(controller, "turn_off"):
                status = await controller.turn_off()
                results[device_id] = status
        except Exception as e:
            results[device_id] = {"status": "error", "error": str(e)}

    return results
