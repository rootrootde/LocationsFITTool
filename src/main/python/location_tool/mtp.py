import json
import subprocess

from PySide6.QtCore import QObject, QThread, QTimer, Signal

from .utils import get_resource_path


class MTPCommandWorker(QThread):
    progress = Signal(int)
    result = Signal(dict)
    done = Signal()
    error = Signal(str)

    def __init__(self, appctxt, command_args, parent=None):
        """Initialize the MTP command worker."""
        super().__init__(parent)
        self.appctxt = appctxt
        self.command_args = command_args
        self.cli_path = get_resource_path(appctxt, "mtpx-cli")

    def run(self) -> None:
        """Run the MTP command and emit signals for progress and results."""
        try:
            proc = subprocess.Popen(
                [self.cli_path] + self.command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    info = json.loads(line)
                    if "progress" in info:
                        self.progress.emit(int(info["progress"]))
                    self.result.emit(info)
                except json.JSONDecodeError:
                    if line == "MTPX_DOWNLOAD_DONE" or line == "MTPX_UPLOAD_DONE":
                        self.done.emit()
            proc.wait()
            if proc.returncode != 0:
                err = proc.stderr.read().strip()
                self.error.emit(err or "Command failed")
        except Exception as e:
            self.error.emit(str(e))


class MTPDeviceManager(QObject):
    device_found = Signal(dict)
    device_error = Signal(str)

    def __init__(self, appctxt, parent=None):
        """Initialize the MTP device manager."""
        super().__init__(parent)
        self.appctxt = appctxt
        self.device_connected = None
        self.worker = None
        self.download_worker = None
        self.upload_worker = None
        self.scan_timer = QTimer()
        self.scan_timer.setInterval(3000)
        self.scan_timer.timeout.connect(self.check_device)
        self.scanning = False

    def start_scanning(self) -> None:
        """Start scanning for MTP devices."""
        if not self.scanning:
            self.check_device()
            self.scan_timer.start()
            self.scanning = True

    def stop_scanning(self) -> None:
        """Stop scanning for MTP devices."""
        if self.scanning:
            self.scan_timer.stop()
            self.scanning = False

    def _on_worker_finished(self) -> None:
        """Handle cleanup after a worker finishes."""
        sender = self.sender()
        if sender:
            if sender == self.download_worker:
                self.download_worker = None
            elif sender == self.upload_worker:
                self.upload_worker = None
            elif sender == self.worker:
                self.worker = None
            sender.deleteLater()

    def check_device(self) -> None:
        """Check for connected MTP devices."""
        if self.worker and self.worker.isRunning():
            return
        self.worker = MTPCommandWorker(self.appctxt, ["device-info"])
        self.worker.result.connect(self._handle_device_info_result)
        self.worker.error.connect(self.device_error.emit)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _handle_device_info_result(self, info: dict) -> None:
        """Emit device information when found."""
        found = True if info else False
        manufacturer = info.get("Manufacturer") if info else None
        model = info.get("Model") if info else None
        serialnumber = info.get("SerialNumber") if info else None
        deviceversion = info.get("DeviceVersion") if info else None
        self.device_found.emit(
            {
                "found": found,
                "manufacturer": manufacturer,
                "model": model,
                "serialnumber": serialnumber,
                "deviceversion": deviceversion,
                "raw": info,
            }
        )

    def start_download(self, source_path: str, target_path: str, on_done, on_error) -> None:
        """Start downloading a file from the device."""
        if self.download_worker and self.download_worker.isRunning():
            self.device_error.emit("Download already in progress.")
            return
        self.download_worker = MTPCommandWorker(
            self.appctxt, ["download", source_path, target_path]
        )
        self.download_worker.done.connect(on_done)
        self.download_worker.error.connect(on_error)
        self.download_worker.finished.connect(self._on_worker_finished)
        self.download_worker.start()

    def start_upload(self, source_path: str, target_path: str, on_done, on_error) -> None:
        """Start uploading a file to the device."""
        if self.upload_worker and self.upload_worker.isRunning():
            self.device_error.emit("Upload already in progress.")
            return
        self.upload_worker = MTPCommandWorker(self.appctxt, ["upload", source_path, target_path])
        self.upload_worker.done.connect(on_done)
        self.upload_worker.error.connect(on_error)
        self.upload_worker.finished.connect(self._on_worker_finished)
        self.upload_worker.start()
