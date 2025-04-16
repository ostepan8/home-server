# Home Automation API

A simple REST API for controlling home devices (Yeelight lights and Roku TV) from a Raspberry Pi.

## Features

- Control Yeelight smart bulbs
  - Power on/off
  - Adjust brightness
  - Change colors
- Control Roku TV
  - Power on/off
  - Change volume
  - Navigation
  - Launch apps
- Room-based organization
- Simple JSON storage (no database required)
- RESTful API endpoints

## Hardware Requirements

- Raspberry Pi (3 or newer recommended)
- Yeelight smart bulbs
- Roku TV
- All devices on the same local network

## Installation

### 1. Set Up Your Raspberry Pi

Make sure your Raspberry Pi is running Raspberry Pi OS and has Python 3.7+ installed.

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
```

### 2. Clone This Repository

bashmkdir -p ~/home-api
cd ~/home-api
git clone https://github.com/yourusername/home-api .

### 3. Set Up a Virtual Environment

bashpython3 -m venv venv
source venv/bin/activate

### 4. Install Dependencies

bashpip install -r requirements.txt

### 5. Configure Your Devices

Create a .env file with your device information:
bashcp .env.example .env
nano .env
Edit the file to add your device IP addresses:

# Roku TV

ROKU_IP_ADDRESS=192.168.1.100 # Replace with your Roku TV IP

# Yeelight bulbs - add/remove as needed

BEDROOM_1_YEELIGHT_IP_ADDRESS=192.168.1.101
BEDROOM_2_YEELIGHT_IP_ADDRESS=192.168.1.102

### 6. Run the API

bashpython -m app.run
