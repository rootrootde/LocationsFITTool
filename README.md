# LocationsFITTool

LocationsFITTool is a desktop app for managing "Favorite Locations" (Locations.fit) on certain Garmin GPD devices. It allows you to 
- import waypoints from the Locations.fit file on your device (app cannot manage the file transfer itself)
- import waypoints from GPX files (experimental)
- manually add new waypoints
- edit existing waypoints
- delete waypoints

and create a new Locations-type FIT file that can be copied to your device to update the internal Locations.fit file.

## ⚠️ Important Notes ⚠️
- This app **cannot directly edit** the Locations.fit file in `Garmin/Locations`.
- Instead, it creates a new Locations-type FIT file that you can copy to your device (Garmin/NewFiles). The device will process it on next startup.
- I only tested this on a Garmin Edge Explore 2, it _should_ work on other devices since it follows the FIT protocol, but I can't guarantee it.
Proceed at your own risk. This might corrupt your device data, brick it or set your house on fire. I don't know.

## Modes
- **ADD**: Add new waypoints to existing ones on device.
- **REPLACE**: Replace all device waypoints with the new ones.
- **DELETE_ALL**: Delete all device waypoints (waypoints in the file are ignored).

## 


## Requirements
- Python 3.9+
- [PySide6](https://pypi.org/project/PySide6/)
- [gpxpy](https://pypi.org/project/gpxpy/)
- Own fork of [fit-tool](hhttps://pypi.org/project/fit-tool/)
(see src/main/python/fit_tool/)

⚠️ Currently only tested on macOS 15.4.1.

## Setup

### Get the code
```sh
git clone https://github.com/rootrootde/LocationsFITTool
cd LocationsFITTool
```


### With [uv](https://github.com/astral-sh/uv) (recommended)
```sh
uv sync
uv run src/main/python/main.py
```

### With pip
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main/python/location_tool/gui.py
```


## License
MIT (or see LICENSE file)
