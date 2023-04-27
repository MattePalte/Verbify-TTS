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
from verbify_tts.actions.audio import listen_and_execute
from verbify_tts.actions.audio import beep
from verbify_tts.actions.logger import save_image


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
        return (
            # left hip is visible
            landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility > 0.5 and
            # left hip is above the half of the screen
            landmarks[mp_pose.PoseLandmark.LEFT_HIP].y < 0.5)
    except:
        return False


def is_shoulder_down(landmarks: List[Tuple[float, float, float]]) -> bool:
    """Check if the waist of the person is below the half of the screen."""
    try:
        return (
            # left shoulder is visible
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility > 0.5 and
            # left shoulder is below the half of the screen
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y > 0.75)
    except:
        return False


def both_elbow_up(landmarks: List[Tuple[float, float, float]]) -> bool:
    """Check if both elbows are above the respective shoulders."""
    try:
        return (
            # all are visible
            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].visibility > 0.5 and
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility > 0.5 and
            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].visibility > 0.5 and
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility > 0.5 and
            # the elbows are above the shoulders
            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y < landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y and
            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y < landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        )
    except:
        return False


def overlap_hands(landmarks: List[Tuple[float, float, float]]) -> bool:
    """Check if the hands are overlapping.

    Namely if the distance between the wrists is less than 0.1.
    """
    min_distance = 0.1
    try:
        return (
            # all are visible
            landmarks[mp_pose.PoseLandmark.LEFT_WRIST].visibility > 0.5 and
            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].visibility > 0.5 and
            # the elbows are above the shoulders
            (landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x
             - landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x) < min_distance and
            (landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y
             - landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y) < min_distance
        )
    except:
        return False


def main():
    """Start the video feed and start monitoring."""
    CURRENT_STATE = None

    action_reactions = [
        ActionReaction("shoulder_down -> scroll down", is_shoulder_down, scroll_down),
        ActionReaction("elbows up -> scroll up", both_elbow_up, scroll_up),
        ActionReaction("overlap hands -> record", overlap_hands, listen_and_execute),
    ]
    # add the neutral state with a lambda which is true when nothing else is true
    other_checkers = [ar.check for ar in action_reactions]
    action_reactions.append(
        ActionReaction(
            name="neutral_state",
            checker=lambda x: not any([c(x) for c in other_checkers]),
            action=lambda: None))

    cap = cv2.VideoCapture(0)

    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            image_original = image
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
                            # log all the screen images, except for the neural state
                            if action_reaction.name != "neutral_state":
                                save_image(
                                    image_original=image_original,
                                    image_with_markers=image,
                                    category=action_reaction.checker.__name__)
                            print(f"STATE CHANGE: CHECKER: {action_reaction} fired!")
                            CURRENT_STATE = action_reaction
                            # produce a bip signal
                            # if not neutral and if no recording is happening
                            if (action_reaction.name != "neutral_state" and
                                    "record" not in action_reaction.name):
                                beep()
                            action_reaction.react()
                            break

            # ESC KEY
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()


if __name__ == "__main__":
    main()