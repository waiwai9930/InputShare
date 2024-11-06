from enum import Enum
from utils import script_abs_path

class LogType(Enum):
    Info    = 0
    Error   = 1
    Server  = 2

class Logger:
    DEFAULT_LOG_FILE_NAME = "InputShare-debug.log"
    LOG_TYPE_NAME_MAP = {
        LogType.Info  : "Into",
        LogType.Error : "Error",
        LogType.Server: "Server",
    }

    def __init__(self, path: str) -> None:
        self.file = open(path, "w+")
        self.file.write("")

    def __del__(self):
        self.file.close()

    def write(self, type: LogType, message: str):
        log_type_name = Logger.LOG_TYPE_NAME_MAP[type]
        complete_log_message = f"[{log_type_name}] {message}"
        print(complete_log_message)
        self.file.write(complete_log_message + "\n")
        self.file.flush()

script_path = script_abs_path(__file__)
log_path = str(script_path.parent.joinpath(Logger.DEFAULT_LOG_FILE_NAME))
LOGGER = Logger(log_path)
