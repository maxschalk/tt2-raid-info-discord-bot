import sys

PLATFORM = sys.platform

IS_UNIX = 'linux' in PLATFORM or 'darwin' in PLATFORM
IS_WINDOWS = 'win32' in PLATFORM
