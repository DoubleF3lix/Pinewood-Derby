import re

import win32com.client
import win32gui

shell = win32com.client.Dispatch("WScript.Shell")

# Modified version of this (https://github.com/gaviral/Kiara-Python/blob/master/custom_utilities/os/resources/WindowManager.py)
class WindowManager:
    """Encapsulates some calls to the winapi for window management"""

    def __init__(self):
        """Constructor"""
        self._handle = None

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def maximize(self):
        win32gui.ShowWindow(
            self._handle, 3
        )  # Used to be win32con.SW_MAXIMIZE = 3, but I replaced it with its constant to avoid the dependency on win32con

    def set_foreground(self):
        """put the window in the foreground"""
        # Stops an occasional error (https://stackoverflow.com/questions/30200381/python-win32gui-setasforegroundwindow-function-not-working-properly)
        shell.SendKeys("%")  # Sends Alt
        win32gui.SetForegroundWindow(self._handle)
        self.maximize()
