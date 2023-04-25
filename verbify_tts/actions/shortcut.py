"""This modules deals with common keywords shortcuts.

Some examples are:
- ALT + TAB: switch between windows
- CTRL + C: copy
- CTRL + V: paste
"""

import os
import time
import pyautogui


def shortcut_copy():
    """Copy the selected text."""
    pyautogui.hotkey("ctrl", "c")


def shortcut_paste():
    """Paste the copied text."""
    pyautogui.hotkey("ctrl", "v")


def shortcut_switch_window(n_times: int = 1):
    """Switch between windows.

    Keep the ALT pressed and press TAB n_times.
    """
    pyautogui.keyDown("alt")
    for _ in range(n_times):
        pyautogui.press("tab")
        time.sleep(0.1)
    pyautogui.keyUp("alt")


if __name__ == "__main__":
    shortcut_switch_window(2)
