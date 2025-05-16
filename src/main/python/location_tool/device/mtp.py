import json
import subprocess

from PySide6.QtCore import QObject, QThread, QTimer, Signal

from location_tool.utils.utils import get_resource_path


class MTPDeviceInfoWorker(QThread):
    device_info_result = Signal(dict)
    device_info_error = Signal(str)

    def __init__(self, appctxt, parent=None):
        super().__init__(parent)
        self.appctxt = appctxt
        self.cli_path = get_resource_path(appctxt, "mtpx-cli")

    def run(self):
        try:
            proc = subprocess.Popen(
                [self.cli_path, "device-info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate()
            found = False
            manufacturer = model = serialnumber = deviceversion = None

            if proc.returncode == 0 and stdout:
                lines = stdout.strip().splitlines()
                for line in lines:
                    try:
                        info = json.loads(line)
                        # If we successfully parse JSON, assume device is found
                        found = True
                        manufacturer = info.get("Manufacturer")
                        model = info.get("Model")
                        serialnumber = info.get("SerialNumber")
                        deviceversion = info.get("DeviceVersion")
                        self.device_info_result.emit(
                            {
                                "found": found,
                                "manufacturer": manufacturer,
                                "model": model,
                                "serialnumber": serialnumber,
                                "deviceversion": deviceversion,
                                "raw": info,
                            }
                        )
                        return
                    except json.JSONDecodeError:
                        continue
                # If no JSON found in output
                self.device_info_result.emit({"found": False})
            else:
                self.device_info_error.emit(stderr.strip() or "Unknown error")
        except Exception as e:
            self.device_info_error.emit(str(e))


class MTPDeviceManager(QObject):
    device_found = Signal(dict)
    device_error = Signal(str)

    def __init__(self, appctxt, parent=None):
        super().__init__(parent)
        self.appctxt = appctxt
        self.worker = None
        self.scan_timer = QTimer()
        self.scan_timer.setInterval(3000)
        self.scan_timer.timeout.connect(self.check_device)
        self.scan_timer.start()

    def check_device(self):
        if self.worker and self.worker.isRunning():
            return  # Already running
        self.worker = MTPDeviceInfoWorker(self.appctxt)
        self.worker.device_info_result.connect(self.device_found.emit)
        self.worker.device_info_error.connect(self.device_error.emit)
        self.worker.start()
