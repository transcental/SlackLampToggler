# Lamp Toggler

Do you want a smart lamp, but don't have the money for one of those expensive bulbs or plugs? Well, I did so I made this project. This uses a Raspberry Pi Pico WH to control a servo that can turn my lamp on and off. It's not the most elegant solution, but it works and I control it from a Slack command.

Oh, and the code is awful. The best you can say about it is that it's written.

## Parts List
- Raspberry Pi Pico WH
- SG90 Servo
- 3 Jumper Wires
- Raspberry Pi Zero 2 W 

## Setup
### Pico
1. Connect the servo to the Raspberry Pi Pico WH using the jumper wires.
2. Flash the MicroPython firmware to the pico
3. Copy the files in the `pico` folder to the.... pico. This should then run on boot. You'll need to copy `.env.example` to `.env` and fill in the values for your wifi network & server
4. Set up the pico for your lamp

### Server
**This must run on the same WiFi network as the Pico**
I used a Raspberry Pi Zero 2 W for this, but anything works as long as it's on the same network as the Pico (it communicates via a local IP address)

1. Copy the files in the `server` folder to the server
2. Install the dependencies with `python3 -m pip install -r requirements.txt`
3. Create a Slack app with the manifest below, and install it to your workspace. If installing to Hack Club, make sure to change the commands (you'll need to change them in `main.py` too)
3. Copy `.env.example` to `.env` and fill in the values for your Slack app from the dashboard
4. Run the server with `python3 main.py`

### Slack App Manifest
```json
{
    "display_information": {
        "name": "Smart Light"
    },
    "features": {
        "bot_user": {
            "display_name": "Smart Light",
            "always_online": false
        },
        "slash_commands": [
            {
                "command": "/toggle-lamp",
                "url": "https://REQUEST_URL/slack/events",
                "description": "Toggle Amber's lamp on/off",
                "should_escape": false
            }
        ]
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "commands",
                "chat:write"
            ]
        }
    },
    "settings": {
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```