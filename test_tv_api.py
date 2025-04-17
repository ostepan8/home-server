# simple_roku_control.py
import requests
import time

# Set your Roku's IP address here
ROKU_IP = "10.0.0.64"


def send_command(key):
    """Send a keypress command to the Roku TV"""
    url = f"http://{ROKU_IP}:8060/keypress/{key}"
    try:
        response = requests.post(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Successfully sent {key} command")
            return True
        else:
            print(
                f"❌ Failed to send {key} command. Status code: {response.status_code}"
            )
            return False
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return False


def device_info():
    """Get device information from the Roku TV"""
    url = f"http://{ROKU_IP}:8060/query/device-info"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Successfully got device info")
            print(
                response.text[:200] + "..."
                if len(response.text) > 200
                else response.text
            )
            return True
        else:
            print(f"❌ Failed to get device info. Status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return False


def test_basic_controls():
    """Test basic TV controls"""
    print("\n🔍 Testing connection to Roku TV...")
    device_info()

    print("\n📺 Testing volume controls")
    print("Volume Up x3:")
    for _ in range(3):
        send_command("VolumeUp")
        time.sleep(0.5)

    time.sleep(1)

    print("Volume Down x3:")
    for _ in range(3):
        send_command("VolumeDown")
        time.sleep(0.5)

    print("\n📱 Testing navigation")
    print("Pressing Home button:")
    send_command("Home")
    time.sleep(1)

    print("Pressing Up button:")
    send_command("Up")
    time.sleep(0.5)

    print("Pressing Down button:")
    send_command("Down")
    time.sleep(0.5)

    print("\n🔄 Testing power (Warning: This may turn your TV off)")
    choice = input("Do you want to test power controls? (y/n): ")
    if choice.lower() == "y":
        print("Pressing Power button:")
        send_command("Power")

    print("\n✅ Test complete!")


if __name__ == "__main__":
    print("🚀 Simple Roku TV Control")
    print("------------------------")

    while True:
        print("\nChoose an option:")
        print("1. Test all basic controls")
        print("2. Volume Up")
        print("3. Volume Down")
        print("4. Home")
        print("5. Power On/Off")
        print("6. Get device info")
        print("0. Exit")

        choice = input("\nEnter option number: ")

        if choice == "1":
            test_basic_controls()
        elif choice == "2":
            send_command("VolumeUp")
        elif choice == "3":
            send_command("VolumeDown")
        elif choice == "4":
            send_command("Home")
        elif choice == "5":
            send_command("Power")
        elif choice == "6":
            device_info()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")
