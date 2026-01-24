# Standard library imports
import os
import threading
import time
from pathlib import Path

# Generated model imports
from internal_api_client.models.request_thumbnail_request_content import RequestThumbnailRequestContent
from internal_api_client.models.thumbnail_request import ThumbnailRequest

# Third-party imports

# Local application imports
from custom_exceptions import (
    InvalidThumbnailSubscription,
    ThumbnailProcessingError
)
from custom_logger import logger
from utils import upload_file

WAIT_TIME_CHECK_NEXT_IMAGE: float = 0.1  # (seconds) Slows the threading loop to a reasonable value.


class ThumbnailThreadedUploader(threading.Thread):
    """
    Handles automatically transmitting thumbnails according to the ThumbnailRequest class instance in its own thread.

    To Start Call: <ThumbnailUploader instance>.start()... a base class method that internally calls self.run()
    To Stop Call:  ThumbnailUploader instance>.stop() or let the class stop automatically when expired.
    """
    def __init__(self, thumbnail_request: ThumbnailRequest, source: str):
        super().__init__()  # Can immediately be terminated when the process stops, no cleanup needed.
        self.source = source
        self.thumbnail_request = thumbnail_request
        self._stop_event = threading.Event()

    def stop(self):
        """
        Call this method to stop the thread.  Will also stop when the current thumbnail expires.
        """
        self._stop_event.set()
        logger.info(f"Thumbnail Stop called")
        if self.is_alive():
            self.join(timeout=1)  # ensure garbage collection is performed

    def run(self):
        """
        Don't call this method directly.  (see threading.Thread base class)
        This method will be called by the start() base class method.

        Publish_thumbnail every <period> seconds until <expires> upon which this thread is terminated and this class
        can be garbage collected. Can not call start() a second time.  If another subscription needs handling, call
        stop() and then construct a new class instance and start it.
        """
        try:
            logger.info(f"Thumbnails: Starting uploader for source: {self.source}.")
            now = int(time.time())
            while not self._stop_event.is_set() and self.thumbnail_request.expires > now:
                if validate_request_params(self.thumbnail_request):
                    upload_file(self.thumbnail_request.local_path,
                                self.thumbnail_request.remote_path,
                                self.thumbnail_request.period,
                                file_type="thumbnail"
                                )
                # Wait request.period but exit within 0.1s if stop called
                for _ in range(self.thumbnail_request.period * 10):
                    if self._stop_event.is_set():
                        return
                    time.sleep(0.1)
                now = int(time.time())

            if self.thumbnail_request.expires < now:
                logger.info(f"Thumbnails: Subscription Expired.")
        except Exception as e:
            # Host Service Endpoint is down or other major problem.
            # In these instances the subscription instance will self terminate.
            logger.exception(f"Thumbnails:  Uploader instance stopped due to uncaught exception: {e}")
            self.valid = False  # Not strictly needed but may help for debugging/unit testing.
        logger.info(f"Thumbnails: Threaded execution instance complete.")


class ThumbnailManager(object):
    """
    Construct a single instance of this class to manages the ThumbnailRequest.
    To handle a new ThumbnailRequest simply call update_thumbnail()
    """
    def __init__(self):
        self.thumbnail_requests: dict = {}
        self.thumbnail_uploader: dict = {}

    def stop_all(self):
        """
        Stops all current ThumbnailRequest subscriptions.
        """
        for key, uploader in self.thumbnail_uploader.items():
            uploader.stop()

    def update_thumbnail(self, thumbnail_subscription: RequestThumbnailRequestContent):
        """
        Stops any current ThumbnailRequest, updates and starts the updated ThumbnailRequest.
        """
        try:
            # Request is RequestThumbnailRequestContent with requests dict: {"<source>": ThumbnailRequest, ... }
            for key, request in thumbnail_subscription.requests.items():
                # Stop if there is an existing subscription for this same source.
                if key in self.thumbnail_uploader:
                    logger.info(f"Thumbnails: Stopping uploader for source: {key}.")
                    self.thumbnail_uploader[key].stop()  # Garbage collected here.
                    # Wait until the last thread really stops before starting a new one.
                    time.sleep(WAIT_TIME_CHECK_NEXT_IMAGE * 2)
                # Check params to see if we can start a new uploader.
                if not validate_request_params(request):
                    return
                self.thumbnail_uploader[key] = ThumbnailThreadedUploader(request, key)
                self.thumbnail_uploader[key].start()
        except (TypeError, ValueError, AttributeError) as e:
            raise InvalidThumbnailSubscription(details=f"Invalid payload. Msg: {e}.") from e
        except Exception as e:
            raise InvalidThumbnailSubscription(details=f"Unknown error.  Msg: {e}.") from e


def validate_request_params(thumbnail_request: ThumbnailRequest) -> bool:
    """
    Checks properties of the request to ensure it can be fulfilled.
    Will not throw exception since these errors can simply be transient.

    Raises: ThumbnailProcessingError on exception.
    """
    try:
        if thumbnail_request.expires < int(time.time()):
            logger.info(f"Thumbnail: Request expired.")
            return False

        # Convert to Path object.
        path = Path(thumbnail_request.local_path)

        # Check path exists.
        if not path.exists():
            logger.warn(f"Thumbnails: Local Path does not exist: {path}")
            return False

        # Check readable.
        if not os.access(path, os.R_OK):
            logger.warn(f"Thumbnails: local_path is not readable: {path}")
            return False

        file_size = path.stat().st_size
        file_size_kb = file_size / 1024
        # Skip files > the threshold set by the thumbnail request emitted by the host service.
        if file_size_kb > thumbnail_request.max_size_kilobyte:
            logger.warn(f"Thumbnails: {file_size_kb}KB file exceeds {thumbnail_request.max_size_kb}KB limit.")
            return False

        return True

    except Exception as e:
        raise ThumbnailProcessingError(details=f"Unknown error. Msg: {e}.") from e
