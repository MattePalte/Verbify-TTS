"""Tracker of the webcam feed with the pose estimation model.

This module starts a service that monitor the webcam and fires events when
certain specific rules or poses are met.
It uses the Pose Estimation model to detect the poses.

Transitions are fired only when a new gesture is detected, namely when the
state changes.

"""

import os
import mediapipe as mp
import cv2
import numpy as np
import time
from typing import Callable, List, Tuple

from pygame import mixer

from verbify_tts.actions.scrolling import scroll_down, scroll_up


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class ActionReaction(object):

    def __init__(self, name: str, checker: Callable, action: Callable):
        """Create an ActionReaction object.

        Args:
            name: Name of the action.
            checker: Function that checks if the action is triggered.
            action: Function that performs the action.
        """
        self.name = name
        self.checker = checker
        self.action = action
        self.last_triggered = 0

    def __str__(self):
        return self.name

    def react(self):
        """Perform the action."""
        self.action()

    def check(self, landmarks: List[Tuple[float, float, float]]):
        """Check if the action is triggered."""
        return self.checker(landmarks)


def is_waist_up(landmarks: List[Tuple[float, float, float]]) -> bool:
    """Check if the waist of the person is above the half of the screen."""
    try:
        return landmarks[mp_pose.PoseLandmark.LEFT_HIP].y < 0.5
    except:
        return False


def is_shoulder_down(landmarks: List[Tuple[float, float, float]]) -> bool:
    """Check if the waist of the person is below the half of the screen."""
    try:
        return landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y > 0.5
    except:
        return False


def beep():
    """Play the mp3 file with the beep sound."""
    path = os.path.join("verbify_tts/resources/success.mp3")
    # Starting the mixer
    mixer.init()
    mixer.music.load(path)
    mixer.music.play()


def main():
    """Start the video feed and start monitoring."""
    CURRENT_STATE = None

    action_reactions = [
        ActionReaction("shoulder_down -> scroll down", is_shoulder_down, scroll_down),
        ActionReaction("jump -> scroll up", is_waist_up, scroll_up),
        ActionReaction(
            name="neutral_state",
            checker=lambda x: not is_shoulder_down(x) and not is_waist_up(x),
            action=lambda: None)
    ]

    cap = cv2.VideoCapture(0)

    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))

            # if we have landmarks
            if results.pose_landmarks:
                if landmarks := results.pose_landmarks.landmark:
                    # check all the checkers functions
                    for action_reaction in action_reactions:
                        if (action_reaction.check(landmarks) and
                                CURRENT_STATE != action_reaction):
                            print(f"STATE CHANGE: CHECKER: {action_reaction} fired!")
                            CURRENT_STATE = action_reaction
                            # produce a bip signal
                            beep()
                            action_reaction.react()
                            break

            # ESC KEY
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()


if __name__ == "__main__":
    main()