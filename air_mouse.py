# ============================================================
# AIR MOUSE
# LEFT + RIGHT HAND SUPPORT
# ============================================================

import cv2
import mediapipe as mp
import pyautogui
import math
import time
import threading
import sys
import os
import webbrowser
import socket
import struct
import json
import numpy as np
import pyaudiowpatch as pyaudio

sys.modules["pyaudio"] = pyaudio

import speech_recognition as sr
import pyperclip


# ============================================================
# PATHS / SETTINGS
# ============================================================

if getattr(sys, "frozen", False):

    AIR_MOUSE_PROJECT_DIR = os.path.dirname(
        os.path.abspath(sys.executable)
    )

else:

    AIR_MOUSE_PROJECT_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )


SETTINGS_FILE = os.path.join(
    AIR_MOUSE_PROJECT_DIR,
    "settings.json"
)

HANDLER_PROJECT_DIR = AIR_MOUSE_PROJECT_DIR

_settings_lock = threading.Lock()
_settings_last_modified = None


# ============================================================
# DEFAULT SETTINGS
# ============================================================

ZONE_LEFT = 0.05
ZONE_RIGHT = 0.95
ZONE_TOP = 0.05
ZONE_BOTTOM = 0.95

pinch_threshold = 0.06
pinch_hold_time = 0.15
drag_start_time = 0.40

ring_pinch_threshold = 0.06
ring_pinch_hold_time = 0.15

middle_pinch_threshold = 0.06
scroll_dead_zone = 0.004
scroll_sensitivity = 180

task_view_touch_threshold = 0.11
task_view_hold_time = 0.80
task_view_spread_threshold = 0.20


# ============================================================
# MICROPHONE
# ============================================================

MICROPHONE_ENABLED = True

MIC_ON_COMMAND = "microphone on"
MIC_OFF_COMMAND = "microphone off"
SEARCH_COMMAND = "enteredcomputer"

CUSTOM_COMMANDS = {
    "open youtube": "https://www.youtube.com",
    "open google": "https://www.google.com",
    "open amazon": "https://www.amazon.in"
}


# ============================================================
# HAND COMMANDS
# ============================================================

HAND_COMMANDS = []

CUSTOM_HAND_COMMANDS = []
CUSTOM_HAND_COMMAND_DETAILS = []

CUSTOM_HAND_PINCH_THRESHOLD = 0.075
CUSTOM_HAND_HOLD_TIME = 0.45


# ============================================================
# SPEECH
# ============================================================

speech_energy_threshold = 300
speech_dynamic_energy_threshold = True
speech_pause_threshold = 0.7
speech_phrase_threshold = 0.3
speech_non_speaking_duration = 0.4


# ============================================================
# APPLICATION STATE
# ============================================================

current_application = None

voice_status = "MIC STARTING"

microphone_active = True
voice_running = True

voice_lock = threading.Lock()


# ============================================================
# MEDIAPIPE MODEL
# ============================================================

if getattr(sys, "frozen", False):

    MODEL_PATH = os.path.join(
        sys._MEIPASS,
        "hand_landmarker.task"
    )

else:

    MODEL_PATH = os.path.join(
        AIR_MOUSE_PROJECT_DIR,
        "hand_landmarker.task"
    )


# ============================================================
# SETTINGS
# ============================================================

def ensure_settings_file():

    try:

        if not os.path.isdir(HANDLER_PROJECT_DIR):

            print("ERROR: Project folder not found.")
            print(HANDLER_PROJECT_DIR)

            return False

        if not os.path.isfile(SETTINGS_FILE):

            print("ERROR: Shared settings.json not found.")
            print("Expected:", SETTINGS_FILE)
            print(
                "air_mouse.py will NOT create another settings.json."
            )

            return False

        return True

    except Exception as error:

        print("Settings verification error:", error)

        return False


def read_settings_file():

    last_error = None

    for _ in range(5):

        try:

            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except (
            json.JSONDecodeError,
            OSError
        ) as error:

            last_error = error
            time.sleep(0.10)

    raise last_error


def load_settings():

    global ZONE_LEFT
    global ZONE_RIGHT
    global ZONE_TOP
    global ZONE_BOTTOM

    global CUSTOM_HAND_COMMANDS
    global CUSTOM_HAND_COMMAND_DETAILS
    global HAND_COMMANDS

    global pinch_threshold
    global pinch_hold_time
    global drag_start_time

    global ring_pinch_threshold
    global ring_pinch_hold_time

    global middle_pinch_threshold
    global scroll_dead_zone
    global scroll_sensitivity

    global task_view_touch_threshold
    global task_view_hold_time
    global task_view_spread_threshold

    global MICROPHONE_ENABLED
    global MIC_ON_COMMAND
    global MIC_OFF_COMMAND
    global SEARCH_COMMAND
    global CUSTOM_COMMANDS

    global speech_energy_threshold
    global speech_dynamic_energy_threshold
    global speech_pause_threshold
    global speech_phrase_threshold
    global speech_non_speaking_duration

    global _settings_last_modified

    try:

        if not ensure_settings_file():

            return False

        modified_time = os.path.getmtime(
            SETTINGS_FILE
        )

        settings = read_settings_file()

        if not isinstance(settings, dict):

            print(
                "ERROR: settings.json must contain a JSON object."
            )

            return False

        with _settings_lock:

            ZONE_LEFT = float(
                settings.get(
                    "ZONE_LEFT",
                    ZONE_LEFT
                )
            )

            ZONE_RIGHT = float(
                settings.get(
                    "ZONE_RIGHT",
                    ZONE_RIGHT
                )
            )

            ZONE_TOP = float(
                settings.get(
                    "ZONE_TOP",
                    ZONE_TOP
                )
            )

            ZONE_BOTTOM = float(
                settings.get(
                    "ZONE_BOTTOM",
                    ZONE_BOTTOM
                )
            )

            pinch_threshold = float(
                settings.get(
                    "pinch_threshold",
                    pinch_threshold
                )
            )

            pinch_hold_time = float(
                settings.get(
                    "pinch_hold_time",
                    pinch_hold_time
                )
            )

            drag_start_time = float(
                settings.get(
                    "drag_start_time",
                    drag_start_time
                )
            )

            ring_pinch_threshold = float(
                settings.get(
                    "ring_pinch_threshold",
                    ring_pinch_threshold
                )
            )

            ring_pinch_hold_time = float(
                settings.get(
                    "ring_pinch_hold_time",
                    ring_pinch_hold_time
                )
            )

            middle_pinch_threshold = float(
                settings.get(
                    "middle_pinch_threshold",
                    middle_pinch_threshold
                )
            )

            scroll_dead_zone = float(
                settings.get(
                    "scroll_dead_zone",
                    scroll_dead_zone
                )
            )

            scroll_sensitivity = float(
                settings.get(
                    "scroll_sensitivity",
                    scroll_sensitivity
                )
            )

            task_view_touch_threshold = float(
                settings.get(
                    "task_view_touch_threshold",
                    task_view_touch_threshold
                )
            )

            task_view_hold_time = float(
                settings.get(
                    "task_view_hold_time",
                    task_view_hold_time
                )
            )

            task_view_spread_threshold = float(
                settings.get(
                    "task_view_spread_threshold",
                    task_view_spread_threshold
                )
            )

            MICROPHONE_ENABLED = bool(
                settings.get(
                    "MICROPHONE_ENABLED",
                    MICROPHONE_ENABLED
                )
            )

            MIC_ON_COMMAND = str(
                settings.get(
                    "MIC_ON_COMMAND",
                    MIC_ON_COMMAND
                )
            )

            MIC_OFF_COMMAND = str(
                settings.get(
                    "MIC_OFF_COMMAND",
                    MIC_OFF_COMMAND
                )
            )

            SEARCH_COMMAND = str(
                settings.get(
                    "SEARCH_COMMAND",
                    SEARCH_COMMAND
                )
            )

            custom_commands = settings.get(
                "CUSTOM_COMMANDS",
                CUSTOM_COMMANDS
            )

            if isinstance(custom_commands, dict):

                CUSTOM_COMMANDS = {
                    str(key).lower().strip(): str(value)
                    for key, value in custom_commands.items()
                }

            elif isinstance(custom_commands, list):

                CUSTOM_COMMANDS = {}

                for command in custom_commands:

                    if not isinstance(command, dict):
                        continue

                    name = str(
                        command.get("name", "")
                    ).lower().strip()

                    value = str(
                        command.get("value", "")
                    ).strip()

                    if name and value:

                        CUSTOM_COMMANDS[name] = value

            # ------------------------------------------------
            # CUSTOM HAND COMMANDS
            # ------------------------------------------------

            custom_hand_commands = settings.get(
                "CUSTOM_HAND_COMMANDS",
                CUSTOM_HAND_COMMANDS
            )

            custom_hand_command_details = settings.get(
                "CUSTOM_HAND_COMMAND_DETAILS",
                CUSTOM_HAND_COMMAND_DETAILS
            )

            if isinstance(custom_hand_commands, list):

                CUSTOM_HAND_COMMANDS = [
                    str(command).strip()
                    for command in custom_hand_commands
                    if str(command).strip()
                ]

            if isinstance(custom_hand_command_details, list):

                valid_details = []

                for detail in custom_hand_command_details:

                    if not isinstance(detail, dict):
                        continue

                    fingers = detail.get(
                        "fingers",
                        []
                    )

                    command = str(
                        detail.get(
                            "command",
                            ""
                        )
                    ).strip()

                    action = str(
                        detail.get(
                            "action",
                            ""
                        )
                    ).strip()

                    if not isinstance(fingers, list):
                        continue

                    fingers = [
                        str(finger).lower().strip()
                        for finger in fingers
                        if str(finger).strip()
                    ]

                    if fingers and command:

                        valid_details.append({
                            "fingers": fingers,
                            "command": command,
                            "action": action
                        })

                CUSTOM_HAND_COMMAND_DETAILS = valid_details

            # ------------------------------------------------
            # NORMAL HAND COMMANDS
            # ------------------------------------------------

            hand_commands = settings.get(
                "HAND_COMMANDS",
                HAND_COMMANDS
            )

            if isinstance(hand_commands, list):

                valid_hand_commands = []

                for hand_command in hand_commands:

                    if not isinstance(hand_command, dict):
                        continue

                    fingers = hand_command.get(
                        "fingers",
                        []
                    )

                    command_type = str(
                        hand_command.get(
                            "type",
                            ""
                        )
                    ).upper().strip()

                    value = str(
                        hand_command.get(
                            "value",
                            ""
                        )
                    ).strip()

                    if not isinstance(fingers, list):
                        continue

                    normalized_fingers = list(
                        dict.fromkeys(
                            str(finger).lower().strip()
                            for finger in fingers
                            if str(finger).strip()
                        )
                    )

                    if (
                        normalized_fingers
                        and command_type
                        and value
                    ):

                        valid_hand_commands.append({
                            "fingers": normalized_fingers,
                            "type": command_type,
                            "value": value
                        })

                HAND_COMMANDS = valid_hand_commands

            else:

                HAND_COMMANDS = []

            # ------------------------------------------------
            # SPEECH
            # ------------------------------------------------

            speech_energy_threshold = float(
                settings.get(
                    "speech_energy_threshold",
                    speech_energy_threshold
                )
            )

            speech_dynamic_energy_threshold = bool(
                settings.get(
                    "speech_dynamic_energy_threshold",
                    speech_dynamic_energy_threshold
                )
            )

            speech_pause_threshold = float(
                settings.get(
                    "speech_pause_threshold",
                    speech_pause_threshold
                )
            )

            speech_phrase_threshold = float(
                settings.get(
                    "speech_phrase_threshold",
                    speech_phrase_threshold
                )
            )

            speech_non_speaking_duration = float(
                settings.get(
                    "speech_non_speaking_duration",
                    speech_non_speaking_duration
                )
            )

            if "speech_recognizer" in globals():

                speech_recognizer.energy_threshold = (
                    speech_energy_threshold
                )

                speech_recognizer.dynamic_energy_threshold = (
                    speech_dynamic_energy_threshold
                )

                speech_recognizer.pause_threshold = (
                    speech_pause_threshold
                )

                speech_recognizer.phrase_threshold = (
                    speech_phrase_threshold
                )

                speech_recognizer.non_speaking_duration = (
                    speech_non_speaking_duration
                )

            _settings_last_modified = modified_time

        print("AirMouse settings loaded.")
        print("Hand commands:", len(HAND_COMMANDS))
        print(
            "Custom hand commands:",
            len(CUSTOM_HAND_COMMAND_DETAILS)
        )

        return True

    except Exception as error:

        print("Settings load error:", error)

        return False


def refresh_settings():

    global _settings_last_modified

    try:

        if not os.path.isfile(SETTINGS_FILE):
            return

        modified_time = os.path.getmtime(
            SETTINGS_FILE
        )

        if (
            _settings_last_modified is None
            or
            modified_time != _settings_last_modified
        ):

            load_settings()

    except Exception as error:

        print(
            "Settings refresh error:",
            error
        )


def settings_refresh_loop():

    while voice_running:

        refresh_settings()

        time.sleep(1.0)


# ============================================================
# SPEECH
# ============================================================

speech_recognizer = sr.Recognizer()

speech_recognizer.energy_threshold = (
    speech_energy_threshold
)

speech_recognizer.dynamic_energy_threshold = (
    speech_dynamic_energy_threshold
)

speech_recognizer.pause_threshold = (
    speech_pause_threshold
)

speech_recognizer.phrase_threshold = (
    speech_phrase_threshold
)

speech_recognizer.non_speaking_duration = (
    speech_non_speaking_duration
)


if not ensure_settings_file():

    raise SystemExit(
        "Shared settings.json is required."
    )


if not load_settings():

    raise SystemExit(
        "Could not load shared settings.json."
    )


def identify_application(command):

    command = command.lower().strip()

    if "youtube" in command:
        return "youtube"

    if "google" in command:
        return "google"

    if "amazon" in command:
        return "amazon"

    if "github" in command:
        return "github"

    if "chatgpt" in command:
        return "chatgpt"

    return None


settings_refresh_thread = threading.Thread(
    target=settings_refresh_loop,
    daemon=True
)

settings_refresh_thread.start()


# ============================================================
# WEBSITE / VOICE HELPERS
# ============================================================

def focus_search_box():

    global voice_status

    voice_status = "FOCUSING SEARCH"

    try:

        pyautogui.press("esc")
        time.sleep(0.15)

        pyautogui.press("/")
        time.sleep(0.50)

        voice_status = "SEARCH READY"

        return True

    except Exception as error:

        print(
            "Could not focus search box:",
            error
        )

        voice_status = "SEARCH FOCUS ERROR"

        return False


def open_application(command):

    global current_application
    global voice_status

    command = command.lower().strip()

    if command not in CUSTOM_COMMANDS:

        return False

    url = CUSTOM_COMMANDS[command]

    current_application = identify_application(
        command
    )

    voice_status = "OPENING"

    try:

        webbrowser.open(url)

    except Exception as error:

        print(
            "Could not open website:",
            error
        )

        voice_status = "OPEN ERROR"

        return False

    time.sleep(4)

    focus_search_box()

    return True


# ============================================================
# GESTURE HELPERS
# ============================================================

def get_landmark_distance(
    point_a,
    point_b
):

    return math.sqrt(
        (point_a.x - point_b.x) ** 2
        +
        (point_a.y - point_b.y) ** 2
    )


def get_custom_finger_points(hand):

    return {
        "thumb": hand[4],
        "index": hand[8],
        "middle": hand[12],
        "ring": hand[16],
        "pinky": hand[20]
    }


def is_custom_hand_gesture_active(
    hand,
    selected_fingers
):

    if not selected_fingers:
        return False

    points = get_custom_finger_points(hand)

    normalized_fingers = []

    for finger in selected_fingers:

        finger = str(
            finger
        ).lower().strip()

        if finger in points:

            if finger not in normalized_fingers:

                normalized_fingers.append(
                    finger
                )

    if not normalized_fingers:
        return False

    if len(normalized_fingers) == 1:
        return True

    thumb_point = points["thumb"]

    for finger in normalized_fingers:

        if finger == "thumb":
            continue

        distance = get_landmark_distance(
            thumb_point,
            points[finger]
        )

        if distance > CUSTOM_HAND_PINCH_THRESHOLD:

            return False

    return True


def is_hand_command_gesture_active(
    hand,
    selected_fingers
):

    return is_custom_hand_gesture_active(
        hand,
        selected_fingers
    )


# ============================================================
# CUSTOM HAND ACTION
# ============================================================

def execute_custom_hand_action(
    command,
    action
):

    global voice_status

    command = str(command).strip()
    action = str(action).strip()

    if not action:
        return False

    print(
        "LEFT HAND CUSTOM COMMAND:",
        command,
        "->",
        action
    )

    try:

        if (
            action.lower().startswith("http://")
            or
            action.lower().startswith("https://")
        ):

            webbrowser.open(action)

            voice_status = "LEFT HAND COMMAND"

            return True

        if action.lower().startswith("key:"):

            key_name = action[4:].strip()

            if not key_name:
                return False

            pyautogui.press(key_name)

            voice_status = "LEFT HAND COMMAND"

            return True

        if action.lower().startswith("hotkey:"):

            key_string = action[7:].strip()

            keys = [
                key.strip()
                for key in key_string.split("+")
                if key.strip()
            ]

            if not keys:
                return False

            pyautogui.hotkey(*keys)

            voice_status = "LEFT HAND COMMAND"

            return True

        if action.lower().startswith("type:"):

            type_speech(
                action[5:]
            )

            voice_status = "LEFT HAND COMMAND"

            return True

        if action.lower() == "search":

            perform_search()

            return True

        if action.lower().strip() in CUSTOM_COMMANDS:

            return open_application(
                action.lower().strip()
            )

        print(
            "Unknown custom hand action:",
            action
        )

        return False

    except Exception as error:

        print(
            "Custom hand command execution error:",
            error
        )

        voice_status = "LEFT HAND COMMAND ERROR"

        return False


# ============================================================
# NORMAL HAND ACTION
# ============================================================

def execute_hand_command(
    command_type,
    value
):

    global voice_status

    command_type = str(
        command_type
    ).upper().strip()

    value = str(
        value
    ).strip()

    if not value:
        return False

    print(
        "LEFT HAND COMMAND:",
        command_type,
        "->",
        value
    )

    try:

        if command_type == "URL":

            webbrowser.open(value)

            voice_status = "LEFT HAND COMMAND"

            return True

        if command_type == "KEY":

            pyautogui.press(value)

            voice_status = "LEFT HAND COMMAND"

            return True

        if command_type == "HOTKEY":

            keys = [
                key.strip()
                for key in value.split("+")
                if key.strip()
            ]

            if not keys:
                return False

            pyautogui.hotkey(*keys)

            voice_status = "LEFT HAND COMMAND"

            return True

        if command_type == "TYPE":

            type_speech(value)

            voice_status = "LEFT HAND COMMAND"

            return True

        if command_type == "SEARCH":

            perform_search()

            return True

        if command_type == "COMMAND":

            command_text = value.lower().strip()

            if command_text in CUSTOM_COMMANDS:

                return open_application(
                    command_text
                )

        print(
            "Unknown HAND_COMMAND type:",
            command_type
        )

        return False

    except Exception as error:

        print(
            "HAND_COMMAND execution error:",
            error
        )

        voice_status = "LEFT HAND COMMAND ERROR"

        return False


# ============================================================
# LEFT HAND CUSTOM COMMANDS
# ============================================================

def process_custom_hand_commands_left(
    hand,
    current_time
):

    if not CUSTOM_HAND_COMMAND_DETAILS:

        return

    active_ids = set()

    for command_index, detail in enumerate(
        CUSTOM_HAND_COMMAND_DETAILS
    ):

        if not isinstance(detail, dict):
            continue

        fingers = detail.get(
            "fingers",
            []
        )

        command = str(
            detail.get(
                "command",
                ""
            )
        ).strip()

        action = str(
            detail.get(
                "action",
                ""
            )
        ).strip()

        if not fingers or not command:
            continue

        command_id = command_index

        active_ids.add(command_id)

        gesture_active = (
            is_custom_hand_gesture_active(
                hand,
                fingers
            )
        )

        if gesture_active:

            if command_id not in left_custom_hand_command_start_times:

                left_custom_hand_command_start_times[
                    command_id
                ] = current_time

                left_custom_hand_command_triggered[
                    command_id
                ] = False

            held_time = (
                current_time
                -
                left_custom_hand_command_start_times[
                    command_id
                ]
            )

            if (
                held_time >= CUSTOM_HAND_HOLD_TIME
                and
                not left_custom_hand_command_triggered.get(
                    command_id,
                    False
                )
            ):

                print(
                    "LEFT CUSTOM GESTURE:",
                    fingers,
                    "->",
                    command,
                    "->",
                    action
                )

                execute_custom_hand_action(
                    command,
                    action
                )

                left_custom_hand_command_triggered[
                    command_id
                ] = True

        else:

            left_custom_hand_command_start_times.pop(
                command_id,
                None
            )

            left_custom_hand_command_triggered.pop(
                command_id,
                None
            )

    # Remove commands no longer present in settings

    for command_id in list(
        left_custom_hand_command_start_times.keys()
    ):

        if command_id not in active_ids:

            left_custom_hand_command_start_times.pop(
                command_id,
                None
            )

            left_custom_hand_command_triggered.pop(
                command_id,
                None
            )


# ============================================================
# LEFT HAND NORMAL COMMANDS
# ============================================================

def process_hand_commands_left(
    hand,
    current_time
):

    if not HAND_COMMANDS:

        return

    active_ids = set()

    for command_index, hand_command in enumerate(
        HAND_COMMANDS
    ):

        if not isinstance(
            hand_command,
            dict
        ):
            continue

        fingers = hand_command.get(
            "fingers",
            []
        )

        command_type = str(
            hand_command.get(
                "type",
                ""
            )
        ).upper().strip()

        value = str(
            hand_command.get(
                "value",
                ""
            )
        ).strip()

        if (
            not fingers
            or
            not command_type
            or
            not value
        ):
            continue

        command_id = (
            "LEFT_HAND_COMMAND",
            command_index
        )

        active_ids.add(command_id)

        gesture_active = (
            is_hand_command_gesture_active(
                hand,
                fingers
            )
        )

        if gesture_active:

            if command_id not in left_hand_command_start_times:

                left_hand_command_start_times[
                    command_id
                ] = current_time

                left_hand_command_triggered[
                    command_id
                ] = False

            held_time = (
                current_time
                -
                left_hand_command_start_times[
                    command_id
                ]
            )

            if (
                held_time >= CUSTOM_HAND_HOLD_TIME
                and
                not left_hand_command_triggered.get(
                    command_id,
                    False
                )
            ):

                print(
                    "LEFT HAND COMMAND GESTURE:",
                    fingers,
                    command_type,
                    value
                )

                execute_hand_command(
                    command_type,
                    value
                )

                left_hand_command_triggered[
                    command_id
                ] = True

        else:

            left_hand_command_start_times.pop(
                command_id,
                None
            )

            left_hand_command_triggered.pop(
                command_id,
                None
            )

    for command_id in list(
        left_hand_command_start_times.keys()
    ):

        if command_id not in active_ids:

            left_hand_command_start_times.pop(
                command_id,
                None
            )

            left_hand_command_triggered.pop(
                command_id,
                None
            )


# ============================================================
# SEARCH / TYPE
# ============================================================

def perform_search():

    global voice_status

    try:

        with voice_lock:

            pyautogui.press("enter")

        voice_status = "SEARCHED"

    except Exception as error:

        print(
            "Search error:",
            error
        )

        voice_status = "SEARCH ERROR"


def type_speech(text):

    if not text:
        return

    try:

        old_clipboard = pyperclip.paste()

    except Exception:

        old_clipboard = ""

    try:

        pyperclip.copy(text)

        time.sleep(0.05)

        with voice_lock:

            pyautogui.hotkey(
                "ctrl",
                "v"
            )

        time.sleep(0.10)

    finally:

        try:

            pyperclip.copy(
                old_clipboard
            )

        except Exception:

            pass


# ============================================================
# MICROPHONE LOOP
# ============================================================

def microphone_loop():

    global voice_status
    global voice_running
    global microphone_active

    try:

        microphone = sr.Microphone()

    except Exception as error:

        voice_status = "MIC ERROR"

        print(
            "Microphone error:",
            error
        )

        return

    try:

        with microphone as source:

            voice_status = "MIC CALIBRATING"

            speech_recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            voice_status = "MIC READY"

            while voice_running:

                try:

                    if microphone_active:

                        voice_status = "LISTENING"

                    else:

                        voice_status = "WAKE LISTENING"

                    audio = speech_recognizer.listen(
                        source,
                        timeout=1,
                        phrase_time_limit=8
                    )

                except sr.WaitTimeoutError:

                    continue

                except Exception as error:

                    print(
                        "Microphone listening error:",
                        error
                    )

                    time.sleep(0.2)

                    continue

                if not voice_running:
                    break

                voice_status = "RECOGNIZING"

                try:

                    text = speech_recognizer.recognize_google(
                        audio
                    ).strip()

                    if not text:
                        continue

                    command_text = text.lower().strip()

                    print(
                        "YOU SAID:",
                        text
                    )

                    if command_text == MIC_ON_COMMAND.lower():

                        microphone_active = True
                        voice_status = "MIC ON"

                        continue

                    if command_text == MIC_OFF_COMMAND.lower():

                        microphone_active = False
                        voice_status = "MIC OFF"

                        continue

                    if not microphone_active:

                        voice_status = "MIC OFF"

                        continue

                    if command_text in CUSTOM_COMMANDS:

                        open_application(
                            command_text
                        )

                        continue

                    if command_text == SEARCH_COMMAND.lower():

                        perform_search()

                        time.sleep(0.4)

                        voice_status = "MIC READY"

                        continue

                    voice_status = "TYPING"

                    type_speech(text)

                    voice_status = "TEXT ENTERED"

                    time.sleep(0.4)

                except sr.UnknownValueError:

                    voice_status = (
                        "MIC OFF"
                        if not microphone_active
                        else "MIC READY"
                    )

                except sr.RequestError as error:

                    print(
                        "Speech recognition service error:",
                        error
                    )

                    voice_status = "VOICE ERROR"

                    time.sleep(1)

                except Exception as error:

                    print(
                        "Speech processing error:",
                        error
                    )

                    voice_status = "VOICE ERROR"

                    time.sleep(0.5)

    except Exception as error:

        voice_status = "MIC ERROR"

        print(
            "Microphone error:",
            error
        )


# ============================================================
# SHARED CAMERA CLIENT
# ============================================================

CAMERA_SERVER_HOST = "127.0.0.1"
CAMERA_SERVER_PORT = 5000

camera_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

try:

    camera_socket.connect(
        (
            CAMERA_SERVER_HOST,
            CAMERA_SERVER_PORT
        )
    )

    print(
        "Connected to Shared Camera Server."
    )

except Exception as error:

    print(
        "ERROR: Could not connect to shared camera server."
    )

    print(error)

    try:
        camera_socket.close()
    except Exception:
        pass

    raise SystemExit


def receive_exactly(
    number_of_bytes
):

    data = b""

    while len(data) < number_of_bytes:

        chunk = camera_socket.recv(
            number_of_bytes - len(data)
        )

        if not chunk:
            return None

        data += chunk

    return data


def receive_camera_frame():

    size_data = receive_exactly(4)

    if size_data is None:
        return None

    frame_size = struct.unpack(
        "!I",
        size_data
    )[0]

    if frame_size <= 0:
        return None

    if frame_size > 10_000_000:
        return None

    frame_data = receive_exactly(
        frame_size
    )

    if frame_data is None:
        return None

    encoded = np.frombuffer(
        frame_data,
        dtype=np.uint8
    )

    return cv2.imdecode(
        encoded,
        cv2.IMREAD_COLOR
    )


# ============================================================
# MEDIAPIPE
# ============================================================

BaseOptions = mp.tasks.BaseOptions

HandLandmarker = mp.tasks.vision.HandLandmarker

HandLandmarkerOptions = (
    mp.tasks.vision.HandLandmarkerOptions
)

RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


# ============================================================
# RIGHT HAND STATE
# ============================================================

right_pinky_pinch_start_time = None
right_left_click_done = False
right_dragging = False

right_ring_pinch_start_time = None
right_ring_pinch_was_active = False
right_double_click_performed = False

right_middle_pinch_was_active = False
right_last_middle_y = None

right_task_view_start_time = None
right_task_view_armed = False
right_task_view_opened = False
right_task_view_explosion = False
right_task_view_explosion_start = None


# ============================================================
# LEFT HAND STATE
# ============================================================

left_custom_hand_command_start_times = {}
left_custom_hand_command_triggered = {}

left_hand_command_start_times = {}
left_hand_command_triggered = {}


# ============================================================
# HAND DETECTION STATE
# ============================================================

right_hand_detected = False
left_hand_detected = False


# ============================================================
# START MICROPHONE
# ============================================================

if MICROPHONE_ENABLED:

    microphone_thread = threading.Thread(
        target=microphone_loop,
        daemon=True
    )

    microphone_thread.start()


# ============================================================
# MAIN PROGRAM
# ============================================================

try:

    with HandLandmarker.create_from_options(
        options
    ) as landmarker:

        frame_number = 0

        while True:

            frame = receive_camera_frame()

            if frame is None:

                print(
                    "Could not receive camera frame."
                )

                break

            # Mirror camera for natural interaction.
            # frame = cv2.flip(frame, 1)

            height, width, _ = frame.shape

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            timestamp = frame_number * 33

            frame_number += 1

            result = landmarker.detect_for_video(
                mp_image,
                timestamp
            )

            # ========================================================
            # RESET HAND DETECTION FLAGS FOR THIS FRAME
            # ========================================================

            right_hand_detected = False
            left_hand_detected = False

            current_time = time.time()

            # ========================================================
            # PROCESS BOTH HANDS
            # ========================================================

            if result.hand_landmarks:

                for hand_index, hand in enumerate(
                    result.hand_landmarks
                ):

                    # ------------------------------------------------
                    # GET MEDIA PIPE HANDEDNESS
                    # ------------------------------------------------

                    try:

                        handedness_category = (
                            result.handedness[
                                hand_index
                            ][0]
                        )

                        handedness = (
                            handedness_category.category_name
                            .lower()
                            .strip()
                        )

                    except Exception as error:

                        print(
                            "Could not determine hand side:",
                            error
                        )

                        continue

                    # ------------------------------------------------
                    # LANDMARKS
                    # ------------------------------------------------

                    wrist = hand[0]
                    thumb = hand[4]
                    index = hand[8]
                    middle = hand[12]
                    ring = hand[16]
                    pinky = hand[20]

                    # =================================================
                    # LEFT HAND
                    # =================================================

                    if handedness == "left":

                        left_hand_detected = True

                        # --------------------------------------------
                        # ONLY LEFT-HAND CUSTOM COMMANDS
                        # --------------------------------------------

                        process_custom_hand_commands_left(
                            hand,
                            current_time
                        )

                        process_hand_commands_left(
                            hand,
                            current_time
                        )

                        # --------------------------------------------
                        # LEFT HAND VISUALIZATION
                        # --------------------------------------------

                        fingertip_x = int(
                            index.x * width
                        )

                        fingertip_y = int(
                            index.y * height
                        )

                        cv2.circle(
                            frame,
                            (
                                fingertip_x,
                                fingertip_y
                            ),
                            12,
                            (255, 0, 255),
                            -1
                        )

                        # Draw all important landmarks

                        landmark_points = [
                            wrist,
                            thumb,
                            index,
                            middle,
                            ring,
                            pinky
                        ]

                        for point in landmark_points:

                            px = int(
                                point.x * width
                            )

                            py = int(
                                point.y * height
                            )

                            cv2.circle(
                                frame,
                                (
                                    px,
                                    py
                                ),
                                7,
                                (255, 0, 255),
                                -1
                            )

                        cv2.putText(
                            frame,
                            "LEFT HAND - CUSTOM",
                            (
                                10,
                                70
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.65,
                            (255, 0, 255),
                            2
                        )

                        continue

                    # =================================================
                    # RIGHT HAND
                    # =================================================

                    if handedness == "right":

                        right_hand_detected = True

                        # =============================================
                        # TASK VIEW
                        # =============================================

                        fingertips = [
                            thumb,
                            index,
                            middle,
                            ring,
                            pinky
                        ]

                        max_finger_distance = 0.0

                        for i in range(
                            len(fingertips)
                        ):

                            for j in range(
                                i + 1,
                                len(fingertips)
                            ):

                                distance = math.sqrt(
                                    (
                                        fingertips[i].x
                                        -
                                        fingertips[j].x
                                    ) ** 2
                                    +
                                    (
                                        fingertips[i].y
                                        -
                                        fingertips[j].y
                                    ) ** 2
                                )

                                max_finger_distance = max(
                                    max_finger_distance,
                                    distance
                                )

                        fingers_together = (
                            max_finger_distance
                            <
                            task_view_touch_threshold
                        )

                        if fingers_together:

                            right_task_view_explosion = False
                            right_task_view_explosion_start = None

                            if right_task_view_start_time is None:

                                right_task_view_start_time = (
                                    current_time
                                )

                            held_time = (
                                current_time
                                -
                                right_task_view_start_time
                            )

                            if held_time >= task_view_hold_time:

                                right_task_view_armed = True

                        else:

                            if right_task_view_armed:

                                if (
                                    max_finger_distance
                                    >=
                                    task_view_spread_threshold
                                ):

                                    if not right_task_view_opened:

                                        right_task_view_explosion = True

                                        right_task_view_explosion_start = (
                                            current_time
                                        )

                                        pyautogui.hotkey(
                                            "win",
                                            "tab"
                                        )

                                        right_task_view_opened = True
                                        right_task_view_armed = False

                            right_task_view_start_time = None

                        if (
                            not fingers_together
                            and
                            not right_task_view_armed
                            and
                            not right_task_view_explosion
                        ):

                            right_task_view_opened = False

                        # =============================================
                        # PINKY / LEFT CLICK
                        # =============================================

                        pinky_distance = math.sqrt(
                            (thumb.x - pinky.x) ** 2
                            +
                            (thumb.y - pinky.y) ** 2
                        )

                        is_pinky_pinching = (
                            pinky_distance
                            <
                            pinch_threshold
                        )

                        # =============================================
                        # MIDDLE / SCROLL
                        # =============================================

                        middle_distance = math.sqrt(
                            (thumb.x - middle.x) ** 2
                            +
                            (thumb.y - middle.y) ** 2
                        )

                        is_middle_pinching = (
                            middle_distance
                            <
                            middle_pinch_threshold
                        )

                        # =============================================
                        # RING / DOUBLE CLICK
                        # =============================================

                        ring_distance = math.sqrt(
                            (thumb.x - ring.x) ** 2
                            +
                            (thumb.y - ring.y) ** 2
                        )

                        is_ring_pinching = (
                            ring_distance
                            <
                            ring_pinch_threshold
                        )

                        # =============================================
                        # PINKY PINCH
                        # =============================================

                        if (
                            is_pinky_pinching
                            and
                            right_pinky_pinch_start_time is None
                        ):

                            right_pinky_pinch_start_time = (
                                current_time
                            )

                            right_left_click_done = False
                            right_dragging = False

                        if (
                            is_pinky_pinching
                            and
                            right_pinky_pinch_start_time is not None
                            and
                            not right_left_click_done
                        ):

                            held_time = (
                                current_time
                                -
                                right_pinky_pinch_start_time
                            )

                            if held_time >= pinch_hold_time:

                                pyautogui.click(
                                    button="left"
                                )

                                right_left_click_done = True

                        # =============================================
                        # DRAG
                        # =============================================

                        if (
                            is_pinky_pinching
                            and
                            right_left_click_done
                            and
                            not right_dragging
                            and
                            right_pinky_pinch_start_time is not None
                        ):

                            total_time = (
                                current_time
                                -
                                right_pinky_pinch_start_time
                            )

                            if total_time >= (
                                pinch_hold_time
                                +
                                drag_start_time
                            ):

                                pyautogui.mouseDown(
                                    button="left"
                                )

                                right_dragging = True

                        if not is_pinky_pinching:

                            if right_dragging:

                                pyautogui.mouseUp(
                                    button="left"
                                )

                            right_pinky_pinch_start_time = None
                            right_left_click_done = False
                            right_dragging = False

                        # =============================================
                        # RING / DOUBLE CLICK
                        # =============================================

                        if (
                            is_ring_pinching
                            and
                            not right_ring_pinch_was_active
                        ):

                            right_ring_pinch_start_time = (
                                current_time
                            )

                            right_double_click_performed = False

                        if (
                            is_ring_pinching
                            and
                            right_ring_pinch_start_time is not None
                            and
                            not right_double_click_performed
                        ):

                            held_time = (
                                current_time
                                -
                                right_ring_pinch_start_time
                            )

                            if held_time >= ring_pinch_hold_time:

                                pyautogui.doubleClick(
                                    interval=0.10
                                )

                                right_double_click_performed = True

                        right_ring_pinch_was_active = (
                            is_ring_pinching
                        )

                        if not is_ring_pinching:

                            right_ring_pinch_start_time = None
                            right_double_click_performed = False

                        # =============================================
                        # MIDDLE / SCROLL
                        # =============================================

                        if is_middle_pinching:

                            if not right_middle_pinch_was_active:

                                right_last_middle_y = middle.y

                            elif right_last_middle_y is not None:

                                middle_movement = (
                                    middle.y
                                    -
                                    right_last_middle_y
                                )

                                if (
                                    abs(middle_movement)
                                    >=
                                    scroll_dead_zone
                                ):

                                    scroll_amount = int(
                                        -middle_movement
                                        *
                                        scroll_sensitivity
                                    )

                                    if scroll_amount != 0:

                                        pyautogui.scroll(
                                            scroll_amount
                                        )

                                right_last_middle_y = middle.y

                            right_middle_pinch_was_active = True

                        else:

                            right_middle_pinch_was_active = False
                            right_last_middle_y = None

                        # =============================================
                        # RIGHT HAND DISPLAY
                        # =============================================

                        fingertip_x = int(
                            index.x * width
                        )

                        fingertip_y = int(
                            index.y * height
                        )

                        if right_dragging:

                            dot_color = (
                                0,
                                0,
                                255
                            )

                            dot_size = 14

                        elif is_pinky_pinching:

                            dot_color = (
                                0,
                                255,
                                255
                            )

                            dot_size = 13

                        elif is_middle_pinching:

                            dot_color = (
                                255,
                                255,
                                0
                            )

                            dot_size = 13

                        else:

                            dot_color = (
                                0,
                                255,
                                0
                            )

                            dot_size = 10

                        cv2.circle(
                            frame,
                            (
                                fingertip_x,
                                fingertip_y
                            ),
                            dot_size,
                            dot_color,
                            -1
                        )

                        # =============================================
                        # RIGHT HAND LANDMARKS
                        # =============================================

                        landmark_points = [
                            (
                                wrist,
                                (255, 255, 255)
                            ),
                            (
                                thumb,
                                (255, 0, 0)
                            ),
                            (
                                middle,
                                (255, 255, 0)
                            ),
                            (
                                ring,
                                (0, 165, 255)
                            ),
                            (
                                pinky,
                                (255, 0, 255)
                            )
                        ]

                        for point, color in landmark_points:

                            px = int(
                                point.x * width
                            )

                            py = int(
                                point.y * height
                            )

                            cv2.circle(
                                frame,
                                (
                                    px,
                                    py
                                ),
                                8,
                                color,
                                -1
                            )

                        # =============================================
                        # TASK VIEW VISUALIZATION
                        # =============================================

                        if (
                            fingers_together
                            or
                            right_task_view_armed
                            or
                            right_task_view_explosion
                        ):

                            points = [
                                (
                                    int(
                                        thumb.x * width
                                    ),
                                    int(
                                        thumb.y * height
                                    )
                                ),
                                (
                                    int(
                                        index.x * width
                                    ),
                                    int(
                                        index.y * height
                                    )
                                ),
                                (
                                    int(
                                        middle.x * width
                                    ),
                                    int(
                                        middle.y * height
                                    )
                                ),
                                (
                                    int(
                                        ring.x * width
                                    ),
                                    int(
                                        ring.y * height
                                    )
                                ),
                                (
                                    int(
                                        pinky.x * width
                                    ),
                                    int(
                                        pinky.y * height
                                    )
                                )
                            ]

                            for i in range(
                                len(points)
                            ):

                                for j in range(
                                    i + 1,
                                    len(points)
                                ):

                                    cv2.line(
                                        frame,
                                        points[i],
                                        points[j],
                                        (255, 255, 255),
                                        2
                                    )

                        # =============================================
                        # TASK VIEW EXPLOSION
                        # =============================================

                        if right_task_view_explosion:

                            explosion_time = (
                                current_time
                                -
                                right_task_view_explosion_start
                            )

                            if explosion_time < 0.35:

                                radius = int(
                                    20
                                    +
                                    explosion_time * 450
                                )

                                cv2.circle(
                                    frame,
                                    (
                                        fingertip_x,
                                        fingertip_y
                                    ),
                                    radius,
                                    (0, 255, 255),
                                    3
                                )

                                cv2.circle(
                                    frame,
                                    (
                                        fingertip_x,
                                        fingertip_y
                                    ),
                                    int(radius * 0.5),
                                    (255, 255, 255),
                                    2
                                )

                            else:

                                right_task_view_explosion = False

                        # =============================================
                        # RIGHT HAND STATUS
                        # =============================================

                        if (
                            fingers_together
                            and
                            right_task_view_start_time is not None
                        ):

                            task_hold = (
                                current_time
                                -
                                right_task_view_start_time
                            )

                            remaining = max(
                                0,
                                task_view_hold_time
                                -
                                task_hold
                            )

                            cv2.putText(
                                frame,
                                f"TASK VIEW: {remaining:.2f}s",
                                (
                                    10,
                                    270
                                ),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.65,
                                (255, 255, 255),
                                2
                            )

                        if right_task_view_explosion:

                            status = "TASK VIEW!"

                            status_color = (
                                0,
                                255,
                                255
                            )

                        elif right_task_view_armed:

                            status = "SPREAD FINGERS!"

                            status_color = (
                                0,
                                255,
                                255
                            )

                        elif fingers_together:

                            status = "HOLD..."

                            status_color = (
                                255,
                                255,
                                255
                            )

                        elif right_dragging:

                            status = "DRAGGING"

                            status_color = (
                                0,
                                0,
                                255
                            )

                        elif right_left_click_done:

                            status = "LEFT CLICK - KEEP HOLDING"

                            status_color = (
                                0,
                                255,
                                0
                            )

                        elif is_pinky_pinching:

                            status = "LEFT CLICK"

                            status_color = (
                                0,
                                255,
                                255
                            )

                        elif is_middle_pinching:

                            status = "SCROLL"

                            status_color = (
                                255,
                                255,
                                0
                            )

                        elif is_ring_pinching:

                            status = "DOUBLE CLICK"

                            status_color = (
                                0,
                                165,
                                255
                            )

                        else:

                            status = "RIGHT HAND READY"

                            status_color = (
                                255,
                                255,
                                255
                            )

                        cv2.putText(
                            frame,
                            status,
                            (
                                10,
                                40
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.75,
                            status_color,
                            2
                        )

            # ========================================================
            # RIGHT HAND LOST
            # ========================================================

            if not right_hand_detected:

                if right_dragging:

                    try:

                        pyautogui.mouseUp(
                            button="left"
                        )

                    except Exception:
                        pass

                right_pinky_pinch_start_time = None
                right_left_click_done = False
                right_dragging = False

                right_ring_pinch_was_active = False
                right_ring_pinch_start_time = None
                right_double_click_performed = False

                right_middle_pinch_was_active = False
                right_last_middle_y = None

                right_task_view_start_time = None
                right_task_view_armed = False
                right_task_view_opened = False
                right_task_view_explosion = False
                right_task_view_explosion_start = None

            # ========================================================
            # LEFT HAND LOST
            # ========================================================

            if not left_hand_detected:

                left_custom_hand_command_start_times.clear()
                left_custom_hand_command_triggered.clear()

                left_hand_command_start_times.clear()
                left_hand_command_triggered.clear()

            # ========================================================
            # BOTH HAND STATUS
            # ========================================================

            if right_hand_detected and left_hand_detected:

                cv2.putText(
                    frame,
                    "BOTH HANDS ACTIVE",
                    (
                        10,
                        105
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2
                )

            elif left_hand_detected:

                cv2.putText(
                    frame,
                    "LEFT HAND ACTIVE",
                    (
                        10,
                        105
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 0, 255),
                    2
                )

            elif right_hand_detected:

                cv2.putText(
                    frame,
                    "RIGHT HAND ACTIVE",
                    (
                        10,
                        105
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2
                )

            # ========================================================
            # HELP TEXT
            # ========================================================

            cv2.putText(
                frame,
                "RIGHT: PINKY=CLICK/DRAG | RING=DOUBLE CLICK | MIDDLE=SCROLL",
                (
                    10,
                    height - 35
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.34,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "RIGHT: ALL FINGERS TOGETHER + HOLD + SPREAD = TASK VIEW",
                (
                    10,
                    height - 15
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.34,
                (0, 255, 255),
                2
            )

            # ========================================================
            # DISPLAY
            # ========================================================

            cv2.imshow(
                "AirMouse",
                frame
            )

            if (
                cv2.waitKey(1) & 0xFF
                ==
                ord("q")
            ):

                break


# ============================================================
# CLEANUP
# ============================================================

finally:

    voice_running = False

    if right_dragging:

        try:

            pyautogui.mouseUp(
                button="left"
            )

        except Exception:
            pass

    try:

        camera_socket.close()

    except Exception:
        pass

    cv2.destroyAllWindows()