import os
import sys
import json
import cv2
import numpy as np
import pyautogui
import tkinter as tk
from collections import deque
import math
import socket
import struct
import threading
import time


# ============================================================
# VIRTUAL TRACKPAD
# ============================================================
#
# SHARED SETTINGS
#
# This program reads:
#
#     AirMouseHandler\settings.json
#
# The settings are controlled from:
#
#     AirMouseHandler\app.py
#
# This program does NOT change the virtual trackpad dot colour.
#
# TRACKPAD_COLOR controls ONLY which physical colour the camera
# searches for.
#
# Supported tracking colours:
#
#     BLUE
#     GREEN
#     RED
#     YELLOW
#     PURPLE
#     ORANGE
#
# ============================================================


# ============================================================
# SHARED SETTINGS LOCATION
# ============================================================

if getattr(sys, "frozen", False):

    SETTINGS_BRIDGE_DIR = os.path.dirname(
        os.path.abspath(
            sys.executable
        )
    )

else:

    SETTINGS_BRIDGE_DIR = os.path.dirname(
        os.path.abspath(
            __file__
        )
    )
# ============================================================
# SETTINGS FILE
# ============================================================

SETTINGS_FILE = os.path.join(
    SETTINGS_BRIDGE_DIR,
    "settings.json"
)


# ============================================================
# APPLICATION ICON
# ============================================================

ICON_FILE = os.path.join(
    SETTINGS_BRIDGE_DIR,
    "AirMouseLauncher.ico"
)
# ============================================================
# LOAD SHARED SETTINGS
# ============================================================

def load_shared_settings():

    try:

        if not os.path.exists(SETTINGS_FILE):

            print()
            print("=" * 70)
            print("WARNING: settings.json NOT FOUND")
            print("=" * 70)
            print()
            print("Expected:")
            print(SETTINGS_FILE)
            print()

            return {}

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            settings = json.load(file)

        if not isinstance(settings, dict):

            return {}

        return settings

    except Exception as error:

        print()
        print("=" * 70)
        print("WARNING: COULD NOT LOAD settings.json")
        print("=" * 70)
        print()
        print(error)
        print()

        return {}


# ============================================================
# SHARED SETTINGS HELPER
# ============================================================

def get_shared_setting(
    name,
    default
):

    settings = load_shared_settings()

    return settings.get(
        name,
        default
    )


# ============================================================
# SCREEN
# ============================================================

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()


# ============================================================
# VIRTUAL TRACKPAD
# ============================================================

PAD_WIDTH = int(
    get_shared_setting(
        "TRACKPAD_WIDTH",
        500
    )
)

PAD_HEIGHT = int(
    get_shared_setting(
        "TRACKPAD_HEIGHT",
        320
    )
)

PAD_LEFT = int(
    get_shared_setting(
        "TRACKPAD_LEFT",
        50
    )
)

PAD_TOP = int(
    get_shared_setting(
        "TRACKPAD_TOP",
        200
    )
)


# ============================================================
# TRACKING COLOUR
# ============================================================

TRACKPAD_COLOR = str(
    get_shared_setting(
        "TRACKPAD_COLOR",
        "BLUE"
    )
).strip().upper()


# ============================================================
# SUPPORTED COLOURS
# ============================================================

TRACKPAD_COLOR_OPTIONS = [
    "BLUE",
    "GREEN",
    "RED",
    "YELLOW",
    "PURPLE",
    "ORANGE"
]


if TRACKPAD_COLOR not in TRACKPAD_COLOR_OPTIONS:

    TRACKPAD_COLOR = "BLUE"


# ============================================================
# HSV COLOUR RANGES
# ============================================================
#
# OpenCV HSV:
#
# Hue:        0 - 179
# Saturation: 0 - 255
# Value:      0 - 255
#
# Red is special because it wraps around the HSV range.
#
# ============================================================

COLOR_RANGES = {

    "BLUE": [
        (
            np.array(
                [85, 45, 30],
                dtype=np.uint8
            ),
            np.array(
                [145, 255, 255],
                dtype=np.uint8
            )
        )
    ],

    "GREEN": [
        (
            np.array(
                [35, 45, 30],
                dtype=np.uint8
            ),
            np.array(
                [85, 255, 255],
                dtype=np.uint8
            )
        )
    ],

    "RED": [
        (
            np.array(
                [0, 45, 30],
                dtype=np.uint8
            ),
            np.array(
                [10, 255, 255],
                dtype=np.uint8
            )
        ),
        (
            np.array(
                [170, 45, 30],
                dtype=np.uint8
            ),
            np.array(
                [179, 255, 255],
                dtype=np.uint8
            )
        )
    ],

    "YELLOW": [
        (
            np.array(
                [20, 45, 30],
                dtype=np.uint8
            ),
            np.array(
                [35, 255, 255],
                dtype=np.uint8
            )
        )
    ],

    "PURPLE": [
        (
            np.array(
                [125, 45, 30],
                dtype=np.uint8
            ),
            np.array(
                [165, 255, 255],
                dtype=np.uint8
            )
        )
    ],

    "ORANGE": [
        (
            np.array(
                [5, 45, 30],
                dtype=np.uint8
            ),
            np.array(
                [20, 255, 255],
                dtype=np.uint8
            )
        )
    ]
}


# ============================================================
# ACTIVE COLOUR RANGE
# ============================================================

ACTIVE_COLOR_RANGES = COLOR_RANGES[
    TRACKPAD_COLOR
]


# ============================================================
# BLUE/COLOUR OBJECT SIZE
# ============================================================

MIN_AREA = float(
    get_shared_setting(
        "BLUE_MIN_AREA",
        8
    )
)

MAX_AREA = float(
    get_shared_setting(
        "BLUE_MAX_AREA",
        1800
    )
)


# ============================================================
# SHAPE FILTER
# ============================================================

MIN_CIRCULARITY = float(
    get_shared_setting(
        "BLUE_MIN_CIRCULARITY",
        0.20
    )
)


# ============================================================
# TRACKING PRECISION
# ============================================================

DEAD_ZONE = float(
    get_shared_setting(
        "TRACKPAD_DEAD_ZONE",
        0.25
    )
)


# ============================================================
# POSITION FILTER
# ============================================================

FILTER_FRAMES = int(
    get_shared_setting(
        "TRACKPAD_FILTER_FRAMES",
        2
    )
)

if FILTER_FRAMES < 1:

    FILTER_FRAMES = 1


# ============================================================
# CURSOR SPEED
# ============================================================

BASE_SENSITIVITY = float(
    get_shared_setting(
        "TRACKPAD_BASE_SENSITIVITY",
        7.5
    )
)


# ============================================================
# ACCELERATION
# ============================================================

ACCELERATION = float(
    get_shared_setting(
        "TRACKPAD_ACCELERATION",
        1.35
    )
)

MAX_ACCELERATION = float(
    get_shared_setting(
        "TRACKPAD_MAX_ACCELERATION",
        7.0
    )
)


# ============================================================
# SPEED THRESHOLD
# ============================================================

SPEED_THRESHOLD = float(
    get_shared_setting(
        "TRACKPAD_SPEED_THRESHOLD",
        1.5
    )
)


# ============================================================
# SMOOTHING
# ============================================================

SMOOTHING = float(
    get_shared_setting(
        "TRACKPAD_SMOOTHING",
        0.82
    )
)

SMOOTHING = max(
    0.0,
    min(
        1.0,
        SMOOTHING
    )
)


# ============================================================
# MAXIMUM CURSOR STEP
# ============================================================

MAX_CURSOR_STEP = float(
    get_shared_setting(
        "TRACKPAD_MAX_CURSOR_STEP",
        250
    )
)


# ============================================================
# SCREEN MARGIN
# ============================================================

CURSOR_MARGIN = int(
    get_shared_setting(
        "TRACKPAD_CURSOR_MARGIN",
        2
    )
)


# ============================================================
# LOST TRACKING
# ============================================================

MAX_LOST_FRAMES = int(
    get_shared_setting(
        "TRACKPAD_MAX_LOST_FRAMES",
        8
    )
)


# ============================================================
# VIRTUAL DOT MOVEMENT
# ============================================================

VIRTUAL_PAD_SCALE = float(
    get_shared_setting(
        "TRACKPAD_VIRTUAL_MOVEMENT_SCALE",
        4.0
    )
)


# ============================================================
# CAMERA SERVER
# ============================================================

CAMERA_SERVER_HOST = str(
    get_shared_setting(
        "CAMERA_SERVER_HOST",
        "127.0.0.1"
    )
)

CAMERA_SERVER_PORT = int(
    get_shared_setting(
        "CAMERA_SERVER_PORT",
        5000
    )
)


# ============================================================
# CAMERA SOCKET
# ============================================================

camera_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


camera_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_RCVBUF,
    262144
)


# ============================================================
# CONNECT TO CAMERA SERVER
# ============================================================

try:

    camera_socket.connect(
        (
            CAMERA_SERVER_HOST,
            CAMERA_SERVER_PORT
        )
    )

except Exception as error:

    print()
    print("=" * 70)
    print("ERROR: COULD NOT CONNECT TO SHARED CAMERA SERVER")
    print("=" * 70)
    print()
    print(error)
    print()

    try:

        camera_socket.close()

    except Exception:

        pass

    raise SystemExit


# ============================================================
# SHARED FRAME STATE
# ============================================================

latest_frame = None

frame_lock = threading.Lock()

receiver_running = True

receiver_error = None


# ============================================================
# RECEIVE EXACTLY
# ============================================================

def receive_exactly_from_socket(
    number_of_bytes
):

    data = bytearray()

    while len(data) < number_of_bytes:

        try:

            chunk = camera_socket.recv(
                number_of_bytes - len(data)
            )

        except socket.timeout:

            continue

        except Exception:

            return None

        if not chunk:

            return None

        data.extend(
            chunk
        )

    return bytes(data)


# ============================================================
# CAMERA RECEIVER THREAD
# ============================================================

def camera_receiver():

    global latest_frame
    global receiver_running
    global receiver_error

    while receiver_running:

        size_data = (
            receive_exactly_from_socket(
                4
            )
        )

        if size_data is None:

            if receiver_running:

                receiver_error = (
                    "Camera connection closed."
                )

            break

        try:

            frame_size = struct.unpack(
                "!I",
                size_data
            )[0]

        except Exception:

            continue

        if frame_size <= 0:

            continue

        if frame_size > 10_000_000:

            continue

        frame_data = (
            receive_exactly_from_socket(
                frame_size
            )
        )

        if frame_data is None:

            if receiver_running:

                receiver_error = (
                    "Could not receive camera frame."
                )

            break

        encoded = np.frombuffer(
            frame_data,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            encoded,
            cv2.IMREAD_COLOR
        )

        if frame is None:

            continue

        with frame_lock:

            latest_frame = frame

    receiver_running = False


# ============================================================
# START CAMERA RECEIVER
# ============================================================

receiver_thread = threading.Thread(
    target=camera_receiver,
    daemon=True
)

receiver_thread.start()


# ============================================================
# GET NEWEST FRAME
# ============================================================

def get_latest_frame():

    global latest_frame

    with frame_lock:

        if latest_frame is None:

            return None

        frame = latest_frame

        latest_frame = None

        return frame


# ============================================================
# FIND COLOURED FINGERTIP
# ============================================================

def find_coloured_fingertip(
    frame,
    previous_point=None
):

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )


    # ========================================================
    # CREATE COLOUR MASK
    # ========================================================

    mask = np.zeros(
        hsv.shape[:2],
        dtype=np.uint8
    )


    for lower_range, upper_range in ACTIVE_COLOR_RANGES:

        colour_mask = cv2.inRange(
            hsv,
            lower_range,
            upper_range
        )

        mask = cv2.bitwise_or(
            mask,
            colour_mask
        )


    # ========================================================
    # CLEAN MASK
    # ========================================================

    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )


    # ========================================================
    # FIND CONTOURS
    # ========================================================

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []


    # ========================================================
    # CHECK COLOURED OBJECTS
    # ========================================================

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < MIN_AREA:

            continue

        if area > MAX_AREA:

            continue


        perimeter = cv2.arcLength(
            contour,
            True
        )

        if perimeter <= 0:

            continue


        circularity = (
            4.0
            * math.pi
            * area
            /
            (perimeter * perimeter)
        )

        if circularity < MIN_CIRCULARITY:

            continue


        moments = cv2.moments(
            contour
        )

        if moments["m00"] == 0:

            continue


        x = (
            moments["m10"]
            /
            moments["m00"]
        )

        y = (
            moments["m01"]
            /
            moments["m00"]
        )


        (
            x_box,
            y_box,
            w_box,
            h_box
        ) = cv2.boundingRect(
            contour
        )

        if w_box <= 0 or h_box <= 0:

            continue


        aspect_ratio = (
            max(
                w_box,
                h_box
            )
            /
            min(
                w_box,
                h_box
            )
        )


        if aspect_ratio > 5.0:

            continue


        candidates.append(
            (
                contour,
                x,
                y,
                area,
                circularity
            )
        )


    # ========================================================
    # NOTHING FOUND
    # ========================================================

    if not candidates:

        return None


    # ========================================================
    # CONTINUE EXISTING TRACK
    # ========================================================

    if previous_point is not None:

        previous_x, previous_y = previous_point


        def tracking_score(
            candidate
        ):

            (
                _,
                x,
                y,
                area,
                circularity
            ) = candidate

            distance = math.sqrt(
                (x - previous_x) ** 2
                +
                (y - previous_y) ** 2
            )

            return (
                distance
                -
                min(
                    area,
                    300
                ) * 0.015
                -
                circularity * 10
            )


        best = min(
            candidates,
            key=tracking_score
        )


        (
            _,
            x,
            y,
            area,
            circularity
        ) = best


        distance = math.sqrt(
            (x - previous_x) ** 2
            +
            (y - previous_y) ** 2
        )


        if distance <= 350:

            return (
                x,
                y,
                area,
                circularity,
                best[0]
            )


    # ========================================================
    # INITIAL DETECTION
    # ========================================================

    def initial_score(
        candidate
    ):

        (
            _,
            x,
            y,
            area,
            circularity
        ) = candidate

        return (
            area
            *
            (
                0.5
                +
                circularity
            )
        )


    best = max(
        candidates,
        key=initial_score
    )


    (
        _,
        x,
        y,
        area,
        circularity
    ) = best


    return (
        x,
        y,
        area,
        circularity,
        best[0]
    )


# ============================================================
# MINIMIZE TRACKPAD
# ============================================================

def minimize_trackpad():

    try:

        root.iconify()

    except tk.TclError:

        pass


# ============================================================
# TKINTER WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "Virtual Trackpad"
)

root.geometry(
    f"{PAD_WIDTH}x{PAD_HEIGHT}+{PAD_LEFT}+{PAD_TOP}"
)

root.attributes(
    "-topmost",
    True
)

root.configure(
    bg="#202020"
)

# ============================================================
# APPLICATION ICON
# ============================================================

if os.path.isfile(ICON_FILE):

    try:

        root.iconbitmap(
            ICON_FILE
        )

    except Exception:

        pass

# ============================================================
# CANVAS
# ============================================================

canvas = tk.Canvas(
    root,
    width=PAD_WIDTH,
    height=PAD_HEIGHT,
    bg="#202020",
    highlightthickness=4,
    highlightbackground="#00AFFF"
)

canvas.pack()


# ============================================================
# MINIMIZE BUTTON
# ============================================================

minimize_button = tk.Button(
    root,
    text="—",
    command=minimize_trackpad,
    bg="#202020",
    fg="white",
    activebackground="#444444",
    activeforeground="white",
    relief="flat",
    borderwidth=0,
    font=(
        "Arial",
        14,
        "bold"
    ),
    cursor="hand2"
)

minimize_button.place(
    x=PAD_WIDTH - 45,
    y=7,
    width=35,
    height=25
)


# ============================================================
# TITLE
# ============================================================

canvas.create_text(
    PAD_WIDTH // 2,
    25,
    text="VIRTUAL TRACKPAD",
    fill="white",
    font=(
        "Arial",
        15,
        "bold"
    )
)


# ============================================================
# TRACKPAD SURFACE
# ============================================================

canvas.create_rectangle(
    8,
    45,
    PAD_WIDTH - 8,
    PAD_HEIGHT - 8,
    outline="#444444",
    width=2
)


# ============================================================
# CENTER MARK
# ============================================================

canvas.create_line(
    PAD_WIDTH // 2 - 10,
    PAD_HEIGHT // 2,
    PAD_WIDTH // 2 + 10,
    PAD_HEIGHT // 2,
    fill="#555555"
)

canvas.create_line(
    PAD_WIDTH // 2,
    PAD_HEIGHT // 2 - 10,
    PAD_WIDTH // 2,
    PAD_HEIGHT // 2 + 10,
    fill="#555555"
)


# ============================================================
# VIRTUAL DOT
# ============================================================
#
# IMPORTANT:
#
# This remains BLUE.
#
# TRACKPAD_COLOR does NOT change this dot.
#
# ============================================================

virtual_x = PAD_WIDTH / 2

virtual_y = PAD_HEIGHT / 2

virtual_dot = canvas.create_oval(
    virtual_x - 12,
    virtual_y - 12,
    virtual_x + 12,
    virtual_y + 12,
    fill="blue",
    outline="white",
    width=2
)

root.update()


# ============================================================
# TRACKING STATE
# ============================================================

previous_blue_x = None

previous_blue_y = None

history_x = deque(
    maxlen=FILTER_FRAMES
)

history_y = deque(
    maxlen=FILTER_FRAMES
)

lost_frames = 0


# ============================================================
# CURSOR STATE
# ============================================================

mouse_x, mouse_y = pyautogui.position()

smooth_dx = 0.0

smooth_dy = 0.0


# ============================================================
# FPS STATE
# ============================================================

last_time = time.perf_counter()

fps = 0.0


# ============================================================
# START MESSAGE
# ============================================================

print()
print("=" * 70)
print(
    "       LOW-LATENCY HIGH-SPEED COLOUR TRACKER"
)
print("=" * 70)
print()

print(
    f"Tracking colour: {TRACKPAD_COLOR}"
)

print()

print(
    f"Screen: {SCREEN_WIDTH} x {SCREEN_HEIGHT}"
)

print()

print(
    "TRACKING COLOUR = CURSOR"
)

print()

print(
    "Virtual dot colour = BLUE"
)

print()

print(
    "Base sensitivity:",
    BASE_SENSITIVITY
)

print(
    "Acceleration:",
    ACCELERATION
)

print(
    "Maximum acceleration:",
    MAX_ACCELERATION
)

print(
    "Smoothing:",
    SMOOTHING
)

print()

print(
    "Newest-frame mode: ENABLED"
)

print()

print(
    "Shared settings: ENABLED"
)

print()

print(
    "Settings folder:"
)

print(
    "    ",
    SETTINGS_BRIDGE_DIR
)

print()

print(
    "Settings file:"
)

print(
    "    ",
    SETTINGS_FILE
)

print()

print(
    "Trackpad position:"
)

print(
    "    LEFT:",
    PAD_LEFT
)

print(
    "    TOP:",
    PAD_TOP
)

print()

print(
    f"Put {TRACKPAD_COLOR} on the TOP of your index finger."
)

print()

print(
    "Q / ESC = quit"
)

print()


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        # ====================================================
        # GET NEWEST FRAME
        # ====================================================

        frame = get_latest_frame()


        # ====================================================
        # NO FRAME YET
        # ====================================================

        if frame is None:

            root.update_idletasks()

            root.update()

            key = (
                cv2.waitKey(1)
                &
                0xFF
            )

            if (
                key == 27
                or
                key == ord("q")
            ):

                break

            time.sleep(
                0.001
            )

            continue


        # ====================================================
        # FPS
        # ====================================================

        current_time = (
            time.perf_counter()
        )

        elapsed = (
            current_time
            -
            last_time
        )

        last_time = current_time

        if elapsed > 0:

            instant_fps = (
                1.0
                /
                elapsed
            )

            fps += (
                instant_fps
                -
                fps
            ) * 0.15


        # ====================================================
        # PREVIOUS POINT
        # ====================================================

        previous_point = None

        if (
            previous_blue_x is not None
            and
            previous_blue_y is not None
        ):

            previous_point = (
                previous_blue_x,
                previous_blue_y
            )


        # ====================================================
        # DETECT SELECTED COLOUR
        # ====================================================

        fingertip = find_coloured_fingertip(
            frame,
            previous_point
        )


        # ====================================================
        # COLOUR FOUND
        # ====================================================

        if fingertip is not None:

            (
                blue_x,
                blue_y,
                area,
                circularity,
                contour
            ) = fingertip

            lost_frames = 0


            # =================================================
            # POSITION HISTORY
            # =================================================

            history_x.append(
                blue_x
            )

            history_y.append(
                blue_y
            )

            filtered_x = np.mean(
                history_x
            )

            filtered_y = np.mean(
                history_y
            )


            # =================================================
            # FIRST DETECTION
            # =================================================

            if previous_blue_x is None:

                previous_blue_x = (
                    filtered_x
                )

                previous_blue_y = (
                    filtered_y
                )

                dx = 0.0

                dy = 0.0

            else:

                dx = (
                    filtered_x
                    -
                    previous_blue_x
                )

                dy = (
                    filtered_y
                    -
                    previous_blue_y
                )

                previous_blue_x = (
                    filtered_x
                )

                previous_blue_y = (
                    filtered_y
                )


            # =================================================
            # DEAD ZONE
            # =================================================

            if abs(dx) < DEAD_ZONE:

                dx = 0.0

            if abs(dy) < DEAD_ZONE:

                dy = 0.0


            # =================================================
            # MOVEMENT SPEED
            # =================================================

            speed = math.sqrt(
                dx * dx
                +
                dy * dy
            )


            # =================================================
            # ACCELERATION
            # =================================================

            if speed <= SPEED_THRESHOLD:

                acceleration = 1.0

            else:

                extra_speed = (
                    speed
                    -
                    SPEED_THRESHOLD
                )

                acceleration = (
                    1.0
                    +
                    (
                        extra_speed
                        *
                        ACCELERATION
                    )
                )

                acceleration = min(
                    acceleration,
                    MAX_ACCELERATION
                )


            # =================================================
            # CURSOR MOVEMENT
            # =================================================

            cursor_dx = (
                -dx
                *
                BASE_SENSITIVITY
                *
                acceleration
            )

            cursor_dy = (
                dy
                *
                BASE_SENSITIVITY
                *
                acceleration
            )


            # =================================================
            # LIMIT EXTREME JUMP
            # =================================================

            movement_length = math.sqrt(
                cursor_dx * cursor_dx
                +
                cursor_dy * cursor_dy
            )

            if movement_length > MAX_CURSOR_STEP:

                scale = (
                    MAX_CURSOR_STEP
                    /
                    movement_length
                )

                cursor_dx *= scale

                cursor_dy *= scale


            # =================================================
            # FAST SMOOTHING
            # =================================================

            smooth_dx += (
                cursor_dx
                -
                smooth_dx
            ) * SMOOTHING

            smooth_dy += (
                cursor_dy
                -
                smooth_dy
            ) * SMOOTHING


            # =================================================
            # UPDATE CURSOR
            # =================================================

            mouse_x += smooth_dx

            mouse_y += smooth_dy


            # =================================================
            # SCREEN LIMITS
            # =================================================

            mouse_x = max(
                CURSOR_MARGIN,
                min(
                    SCREEN_WIDTH
                    -
                    CURSOR_MARGIN,
                    mouse_x
                )
            )

            mouse_y = max(
                CURSOR_MARGIN,
                min(
                    SCREEN_HEIGHT
                    -
                    CURSOR_MARGIN,
                    mouse_y
                )
            )


            # =================================================
            # MOVE WINDOWS CURSOR
            # =================================================

            pyautogui.moveTo(
                int(mouse_x),
                int(mouse_y),
                duration=0
            )


            # =================================================
            # VIRTUAL TRACKPAD
            # =================================================

            virtual_x += (
                dx
                *
                VIRTUAL_PAD_SCALE
            )

            virtual_y += (
                dy
                *
                VIRTUAL_PAD_SCALE
            )


            virtual_x = max(
                20,
                min(
                    PAD_WIDTH - 20,
                    virtual_x
                )
            )

            virtual_y = max(
                60,
                min(
                    PAD_HEIGHT - 20,
                    virtual_y
                )
            )


            canvas.coords(
                virtual_dot,
                virtual_x - 12,
                virtual_y - 12,
                virtual_x + 12,
                virtual_y + 12
            )


            # =================================================
            # DRAW DETECTED CONTOUR
            # =================================================

            cv2.drawContours(
                frame,
                [contour],
                -1,
                (0, 255, 0),
                2
            )


            # =================================================
            # CENTER DOT
            # =================================================

            cv2.circle(
                frame,
                (
                    int(blue_x),
                    int(blue_y)
                ),
                15,
                (0, 255, 0),
                3
            )

            cv2.circle(
                frame,
                (
                    int(blue_x),
                    int(blue_y)
                ),
                5,
                (255, 255, 255),
                -1
            )


            # =================================================
            # STATUS
            # =================================================

            cv2.putText(
                frame,
                f"{TRACKPAD_COLOR} FINGERTIP TRACKING",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Speed: {speed:.2f}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Acceleration: {acceleration:.2f}x",
                (20, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"DX: {dx:+.2f}  DY: {dy:+.2f}",
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Cursor: {int(mouse_x)}, {int(mouse_y)}",
                (20, 190),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Area: {area:.0f}",
                (20, 220),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )


        # ====================================================
        # COLOUR NOT FOUND
        # ====================================================

        else:

            lost_frames += 1

            cv2.putText(
                frame,
                f"{TRACKPAD_COLOR} FINGERTIP NOT DETECTED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (0, 0, 255),
                2
            )


            # =================================================
            # STOP CURSOR MOMENTUM
            # =================================================

            smooth_dx *= 0.35

            smooth_dy *= 0.35


            # =================================================
            # RESET AFTER PROLONGED LOSS
            # =================================================

            if lost_frames > MAX_LOST_FRAMES:

                previous_blue_x = None

                previous_blue_y = None

                history_x.clear()

                history_y.clear()

                smooth_dx = 0.0

                smooth_dy = 0.0


        # ====================================================
        # TKINTER
        # ====================================================

        root.update_idletasks()

        root.update()


        # ====================================================
        # CAMERA PREVIEW
        # ====================================================

        cv2.imshow(
            "Virtual Trackpad Camera",
            frame
        )


        # ====================================================
        # EXIT
        # ====================================================

        key = (
            cv2.waitKey(1)
            &
            0xFF
        )

        if (
            key == 27
            or
            key == ord("q")
        ):

            break


finally:

    # ========================================================
    # STOP RECEIVER
    # ========================================================

    receiver_running = False


    # ========================================================
    # CLOSE SOCKET
    # ========================================================

    try:

        camera_socket.shutdown(
            socket.SHUT_RDWR
        )

    except Exception:

        pass


    try:

        camera_socket.close()

    except Exception:

        pass


    # ========================================================
    # CLOSE WINDOWS
    # ========================================================

    cv2.destroyAllWindows()


    try:

        root.destroy()

    except Exception:

        pass


    # ========================================================
    # STOP MESSAGE
    # ========================================================

    print()

    print("=" * 70)

    print(
        "COLOUR INDEX-FINGERTIP TRACKER STOPPED"
    )

    print("=" * 70)


