import logging
import os.path
from logging.handlers import (
    RotatingFileHandler
)
from service_api_models import JsonFormatter
from pathlib import Path

LOG_FILE_MAX_BYTES = 500 * 1000  # Host API specification: MAX Limit = 500 KB Size of each log file.
LOG_FILE_ROTATE_COUNT = 3        # Client API specification.  If > 0 rotation and sending logs to service enabled.

logger = logging.getLogger('cdd_sdk_logger')


class CustomRotatingFileHandler(RotatingFileHandler):
    def __init__(
            self,
            callback_func,
            filename,
            mode='a',
            maxBytes=0,
            backupCount=0,
            encoding=None,
            delay=False,
    ):
        super().__init__(filename=filename,
                         mode=mode,
                         maxBytes=maxBytes,
                         backupCount=backupCount,
                         encoding=encoding,
                         delay=delay)
        if backupCount > 0:
            self.callback_dump_logs = callback_func
        else:
            self.callback_dump_logs = None

        # After rotation, grab the .1 file (most current file rotated)
        self.callback_target_filename = str(filename) + ".1"

    def doRollover(self):
        super().doRollover()
        if self.callback_dump_logs:
            if os.path.exists(self.callback_target_filename):
                self.callback_dump_logs(self.callback_target_filename)


class CDDLogHandler(object):
    """
    Class to manage the logger and the 3 handlers
    Formats logs in JSON

    1. stream_handler fpr printing to std out
    2. rotating_handler writes to N rotated files in log_path
        Uses: LOG_FILE_MAX_BYTES, LOG_FILE_ROTATE_COUNT

        The call_back_function is called after each rotation operation.
        call_back_function(<log_path.1>: str)
        Passes the .1 rotation file.

    """
    def __init__(self,
                 call_back_function,
                 log_path: str,
                 device_id: str = "Notset"
                 ):
        self._call_back = call_back_function
        self._device_id = device_id
        self._log_path = log_path
        self._init()

    def update_device_id(self, device_id: str):
        update: bool = self._device_id != device_id
        self._device_id = device_id
        if update:
            self._set_formatter()

    def dump(self):
        # Normally this happens when the file size == LOG_FILE_MAX_BYTES.
        # This allows the system to force a log rotate and as a consequence
        # fire the callback which reports logs to the host service.
        # This might be convenient to call when say the client connects.
        self.rotating_handler.doRollover()

    def _set_formatter(self):
        self.formatter = JsonFormatter(device_id=self._device_id)
        self.stream_handler.setFormatter(self.formatter)
        self.rotating_handler.setFormatter(self.formatter)

    def _init(self):
        # Create a logger
        logger.setLevel(logging.INFO)  # Set the logging level

        self.stream_handler = logging.StreamHandler()
        logger.addHandler(self.stream_handler)

        # Create rotating handler
        log_file = Path(self._log_path) / "cdd_sdk.log"
        self.rotating_handler = CustomRotatingFileHandler(
            filename=log_file,
            callback_func=self._call_back,
            mode='a',
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_FILE_ROTATE_COUNT
        )
        logger.addHandler(self.rotating_handler)

        self._set_formatter()
