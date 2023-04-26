"""This modules logs info or stores data in the background."""

import logging
import os
import time
import pathlib
from threading import Thread
import cv2
import numpy as np


EXERCISE_DIR = "data/exercises_pictures"
DEBUG_DIR_WITH_MARKERS = "data/debug_pictures"


def save_image(
            image_original,
            image_with_markers,
            category: str):
    """Save an image to the data folder."""
    def _save_image(image, folder):
        category_dir = os.path.join(folder, category)
        pathlib.Path(category_dir).mkdir(parents=True, exist_ok=True)

        file_path = os.path.join(category_dir, f"{time.time()}.png")
        cv2.imwrite(file_path, image)
        logging.info(f"Saved image to {file_path}")
    # save both images
    t_original = Thread(target=_save_image,
               args=(image_original, EXERCISE_DIR))
    t_original.start()
    t_markers = Thread(target=_save_image,
               args=(image_with_markers, DEBUG_DIR_WITH_MARKERS))
    t_markers.start()