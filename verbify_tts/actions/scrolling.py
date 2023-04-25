"""This modules handles the page scrolling.

Under the hood it uses pyautogui to scroll the page up or down.
"""

import pyautogui
import time
from typing import Callable, List, Tuple


def scroll_down(speed: float = 0.1):
    """Scroll the page down.
    Params:
        speed: Speed of the scrolling. Default 0.1.
    """
    # move the mouse in the middle of the screen and then
    pyautogui.scroll(-2, speed)


def scroll_up(speed: float = 0.1):
    """Scroll the page up.
    Params:
        speed: Speed of the scrolling. Default 0.1.
    """
    # move the mouse in the middle of the screen and then
    pyautogui.scroll(2, speed)
