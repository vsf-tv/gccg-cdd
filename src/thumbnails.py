import attr
import cattr
import os
from pathlib import Path
import requests
import threading
import time
from custom_exceptions import (
    ThumbnailProcessingError,
    InvalidThumbnailSubscription
)

WAIT_TIME_CHECK_NEXT_IMAGE: float = 0.1  # (seconds) Slows the threading loop to a reasonable value.


@attr.define
class ThumbnailRequest:
    """
    ThumbnailRequest: Class is defined in the Host Service API and contains the complete set of information needed to
    request a thumbnail image be periodically uploaded to the Host Service Endpoint.

    Params:
        period: Seconds between uploads.

        expires: Epoch time seconds.

        max_size_KB: Host Service may not permit files to exceed this value. Enforcement is up to the Host Service
         and may include throttling, disabling thumbnails and possible de-registration.

        local_path: png or jpg only. Path to the thumbnail image. The SDK expects the application to continually
        update this file at least every 10 seconds (protocol minimum rate). local_path is defined by the application
        in the Instance Schema and provided to the service in the status message. See Message Protocol.

        remote_path: A temporary pre-signed url (PUT).

    """
    period: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    expires: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    max_size_KB: int = attr.field(
        default=0,
        validator=attr.validators.instance_of(int)
    )
    local_path: str = attr.field(
        default="",
        validator=attr.validators.instance_of(str)
    )
    remote_path: str = attr.field(
        default="",
        validator=attr.validators.instance_of(str)
    )

    def is_expired(self) -> bool:
        if self.expires < int(time.time()):
            return True
        return False


class ThumbnailThreadedUploader(threading.Thread):
    """
    Handles automatically transmitting thumbnails according to the ThumbnailRequest class instance in its own thread.

    To Start Call: <ThumbnailUploader instance>.start()... a base class method that internally calls self.run()
    To Stop Call:  ThumbnailUploader instance>.stop() or let the class stop automatically when expired.
    """
    def __init__(self, thumbnail_request: ThumbnailRequest, source: str):
        super().__init__()
        self.source = source
        self.thumbnail_request = thumbnail_request
        self._stop_event = threading.Event()

    def stop(self):
        """
        Call this method to stop the thread.  Will also stop when the current thumbnail expires.
        """
        print(f"Thumbnail Stop called")
        self._stop_event.set()
        if self.is_alive():
            self.join()  # ensure garbage collection is performed

    def run(self):
        """
        Don't call this method directly.  (see threading.Thread base class)
        This method will be called by the start() base class method.

        Publish_thumbnail every <period> seconds until <expires> upon which this thread is terminated and this class
        can be garbage collected. Can not call start() a second time.  If another subscription needs handling, call
        stop() and then construct a new class instance and start it.
        """
        try:
            now = int(time.time())
            while not self._stop_event.is_set() and self.thumbnail_request.expires > now:
                if validate_request_params(self.thumbnail_request):
                    print(f"Thumbnails:  Sending source: {self.source}."
                          f"Expires in: {self.thumbnail_request.expires - now}s.")
                    upload_file(self.thumbnail_request.local_path,
                                self.thumbnail_request.remote_path,
                                self.thumbnail_request.period
                                )
                # Wait request.period but exit within 0.1s if stop called
                for _ in range(self.thumbnail_request.period * 10):
                    if self._stop_event.is_set():
                        return
                    time.sleep(0.1)
                now = int(time.time())

            if self.thumbnail_request.expires < now:
                print(f"Thumbnails: Subscription Expired.")
        except Exception as e:
            # Host Service Endpoint is down or other major problem.
            # In these instances the subscription instance will self terminate.
            print(f"Thumbnails:  Uploader instance stopped due to uncaught exception: {e}")
            self.valid = False  # Not strictly needed but may help for debugging/unit testing.
        print(f"Thumbnails: Threaded execution instance complete.")


class ThumbnailManager(object):
    """
    Construct a single instance of this class to manages the ThumbnailRequest.
    To handle a new ThumbnailRequest simply call update_thumbnail()
    """
    def __init__(self):
        self.thumbnail_requests: dict = {}
        self.thumbnail_uploader: dict = {}

    def update_thumbnail(self, tn_json: dict):
        """
        Stops any current ThumbnailRequest, updates and starts the updated ThumbnailRequest.
        """
        try:
            # Request is dict: {"<source>": ThumbnailRequest, ... }
            thumbnail_requests = {key: cattr.structure(req, ThumbnailRequest) for key, req in tn_json.items()}
            for key, request in thumbnail_requests.items():
                # Stop if there is an existing subscription for this same source.
                if key in self.thumbnail_uploader:
                    print(f"Thumbnails: Stopping uploader for source: {key}.")
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


def validate_request_params(thumbnail_request) -> bool:
    """
    Checks properties of the request to ensure it can be fulfilled.
    Will not throw exception since these errors can simply be transient.

    Raises: ThumbnailProcessingError on exception.
    """
    try:
        if thumbnail_request.is_expired():
            print(f"Thumbnail: Request expired.")
            return False

        # Convert to Path object.
        path = Path(thumbnail_request.local_path)

        # Check path exists.
        if not path.exists():
            print(f"Thumbnails: Local Path does not exist: {path}")
            return False

        # Check readable.
        if not os.access(path, os.R_OK):
            print(f"Thumbnails: local_path is not readable: {path}")
            return False

        file_size = path.stat().st_size
        file_size_kb = file_size / 1024
        # Skip files > the threshold set by the thumbnail request emitted by the host service.
        if file_size_kb > thumbnail_request.max_size_KB:
            print(f"Thumbnails: {file_size_kb}KB file exceeds {thumbnail_request.max_size_KB}KB limit.")
            return False

        return True

    except Exception as e:
        print(f"Error publishing thumbnail: {e}")
        raise ThumbnailProcessingError(details=f"Unknown error. Msg: {e}.") from e


def upload_file(local_path, presigned_put_remote_path: str, timeout: int):
    """
    Upload a file using the pre-signed URL: presigned_put_remote_path.

    Args:
        local_path: Path to the local file to upload
        presigned_put_remote_path: pre-signed URL (PUT)

    Raises:
        requests.exceptions.RequestException: If the upload fails or times out.
    """
    with open(local_path, 'rb') as file:
        # Explicitly read the file first to ensure we get a complete copy, not a partially written image.
        with open(local_path, 'rb') as f:
            file_content = f.read()
        try:
            response = requests.put(
                url=presigned_put_remote_path,
                data=file_content,
                timeout=timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # Could be a temporary network outage.  Keep trying.
            print(f"Thumbnails: Could not upload: {e}")
        except Exception as e:
            raise ThumbnailProcessingError(f"Unknown error uploading file: {e}") from e
