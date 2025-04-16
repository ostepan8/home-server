# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
from app.api import devices, lights, tv
from app.devices.registry import DeviceRegistry
from app.config import settings

app = FastAPI(
    title="Home Automation API",
    description="Simple API for controlling home devices",
    version="1.0.0",
)

# Set up CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize device registry
registry = DeviceRegistry()


@app.on_event("startup")
async def startup_event():
    # Load devices from file
    await registry.load_devices()


@app.on_event("shutdown")
async def shutdown_event():
    # Save devices to file
    await registry.save_devices()


# Include routers
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(lights.router, prefix="/lights", tags=["lights"])
app.include_router(tv.router, prefix="/tv", tags=["tv"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Home Automation API"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
