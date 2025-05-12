import subprocess

from PyQt6.QtCore import QThread, pyqtSignal


class MTPStatWorker(QThread):
    result = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            proc = subprocess.Popen(
                ["./mtpx-tool", "stat", self.path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            lines = []
            for line in proc.stdout:
                line = line.strip()
                if line == "MTPX_STAT_DONE":
                    break
                lines.append(line)

            if lines and lines[0].startswith("FOUND"):
                _, full_path, size, human = lines[0].split("\t")
                self.result.emit(
                    {
                        "found": True,
                        "path": full_path,
                        "size": int(size),
                        "human": human,
                    }
                )
            else:
                self.result.emit({"found": False})

        except Exception as e:
            self.error.emit(str(e))
