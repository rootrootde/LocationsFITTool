# LocationsFITTool

- [Overview](#overview)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Modes](#modes)
- [License](#license)
- [Third-party components](#third-party-components)

## Overview

LocationsFITTool is a desktop app for managing "Favorite Locations" (Locations.fit) on certain Garmin GPS devices.

It allows you to 
- **Directly download `Locations.fit`** from your connected Garmin device.
- Import waypoints from local `Locations.fit` or GPX files.
- Manually add, edit, or delete waypoints (including detailed descriptions and map symbols).
- **Directly upload** the generated FIT file to your device's `Garmin/NewFiles` directory.
- Save the waypoints to a local Locations-type FIT or GPX file.

## Requirements

- Python 3.9+
- [PySide6](https://pypi.org/project/PySide6/)
- [gpxpy](https://pypi.org/project/gpxpy/)
- [`libusb`](https://github.com/libusb/libusb) (especially for Linux/macOS for MTP device access)

⚠️ This tool is primarily designed for **Linux and macOS**. It has only been tested extensively on macOS. Windows is not officially supported, and MTP functionality may not work.

## Setup

### Get the code
```sh
git clone https://github.com/rootrootde/LocationsFITTool
cd LocationsFITTool
```


### With [uv](https://github.com/astral-sh/uv) (recommended)
```sh
uv sync
```

### With pip
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/base.txt
```

## Usage

1. Run the app:

```sh
# uv
uv run src/main/python/main.py

# pip
python src/main/python/main.py
```

2. **Connect your Garmin device.** The app will attempt to automatically detect it via MTP. The status bar will indicate the connection status.

3. **Download from Device (Recommended for existing locations):**
   - Click the "Download" button/action.
   - This will fetch `Garmin/Locations/Locations.fit` from your device and load the waypoints into the table.

4. **Import from File (Optional):**
   - Use "File > Import" or the import button to load waypoints from a local `.fit` or `.gpx` file. Waypoints will be appended to the current list.

5. **Manage Waypoints:**
   - Review the waypoints in the table.
   - Manually add new waypoints.
   - Edit existing waypoints by double-clicking cells (including name, coordinates, altitude, timestamp, symbol, and description).
   - Delete selected waypoints.

6. **Upload to Device:**
   - Click the "Upload" button/action.
   - You will be prompted to select a mode (ADD, REPLACE, DELETE_ALL - see below).
   - The app will generate a new FIT file based on the current waypoints and the selected mode, then upload it to `Garmin/NewFiles/` on your device.

7. **Save to File (Optional):**
   - Use "File > Save" or the save button to save the current waypoints to a local `.fit` or `.gpx` file. You will be prompted for the mode if saving as FIT.

8. **Finalize on Device:**
   - Disconnect your Garmin device.
   - Restart the device. It will process the file from `Garmin/NewFiles` and update its internal `Locations.fit`.

## Modes
- **ADD**: Add new waypoints to the existing ones on the device.

- **REPLACE**: Delete all Waypoints on device and replace them with the new waypoints.

- **DELETE_ALL**: Delete all waypoints on device. If waypoints are included in the new Locations.fit file, they will be ignored.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Commercial use of this software is allowed only if the resulting product is also licensed as open source software under the AGPLv3 or a compatible license.

## Third-party components

This project uses a modified version of [https://pypi.org/project/fit-tool/](fit-tool), a Python library originally developed by Stages Cycling. That component is licensed under the BSD 3-Clause License:

> Copyright 2021 Stages Cycling. All rights reserved.
>
> Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
>
> * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
> * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
> * Neither the name of Stages Cycling nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.