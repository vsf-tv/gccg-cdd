import sys

# Define the mock classes
class ZoneInfo:
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return self.key
    def __repr__(self):
        return f"ZoneInfo({self.key!r})"

# Pydantic 2.10+ specific exceptions
class ZoneInfoNotFoundError(Exception):
    pass

class InvalidTimezoneError(Exception):
    pass

# Mock expected variables and functions
TZPATH = ()
def available_timezones():
    return set()

def reset_tzpath(tzpath=None):
    pass
