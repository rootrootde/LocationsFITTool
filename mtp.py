import json
import subprocess

from PySide6.QtCore import QObject, QThread, Signal


class MTPWorker(QThread):
    outputReceived = Signal(dict)
    errorOccurred = Signal(str)
    finished = Signal()

    def __init__(self, args):
        super().__init__()
        self.args = args
        self.proc = None
        self._last_progress = {}

    def run(self):
        try:
            cmd = ["./mtpx-cli"] + self.args
            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            for line in self.proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)

                    # check for progress throttling
                    if "progress" in data and "file" in data:
                        fname = data["file"]
                        prev = self._last_progress.get(fname, -1)
                        now = data["progress"]
                        if abs(now - prev) < 0.1:  # less than 0.1% change → skip
                            continue
                        self._last_progress[fname] = now

                    self.outputReceived.emit(data)
                except json.JSONDecodeError:
                    self.errorOccurred.emit(f"Invalid JSON: {line}")

        except Exception as e:
            self.errorOccurred.emit(str(e))
        finally:
            self.finished.emit()


class MTPDeviceManager(QObject):
    outputReceived = Signal(dict)
    errorOccurred = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.worker = None

    def run_command(self, args):
        if self.worker and self.worker.isRunning():
            self.errorOccurred.emit("A command is already running")
            return

        self.worker = MTPWorker(args)
        self.worker.outputReceived.connect(self.outputReceived.emit)
        self.worker.errorOccurred.connect(self.errorOccurred.emit)
        self.worker.finished.connect(self.finished.emit)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
