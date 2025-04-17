# app/config.py
import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic_settings import BaseSettings  # Change this import

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Data file
    DEVICES_FILE: str = "data/devices.json"

    # Roku
    ROKU_IP_ADDRESS: Optional[str] = os.getenv("ROKU_IP_ADDRESS")
    print(ROKU_IP_ADDRESS, "ROKU_IP_ADDRESS")

    # Yeelight light bulbs
    YEELIGHT_IP_ADDRESSES: List[str] = []

    # Populate Yeelight IPs from environment variables
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load Yeelight IP addresses from environment variables
        for key, value in os.environ.items():
            if "YEELIGHT" in key and key.endswith("_IP_ADDRESS") and value:
                print(key, "KEY")
                print(value, "VALUE")
                parts = key.split("_")
                # Extract room information
                room_name = " ".join(
                    [part.capitalize() for part in parts[:-3]]
                )  # Excluding _YEELIGHT_IP_ADDRESS
                self.YEELIGHT_IP_ADDRESSES.append(
                    {"ip": value, "room": room_name if room_name else "Unknown"}
                )
                print(self.YEELIGHT_IP_ADDRESSES, "YEELIGHT_IP_ADDRESSES")


# Create settings instance
settings = Settings()

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(settings.DEVICES_FILE), exist_ok=True)
