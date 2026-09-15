import subprocess
import sys
import os
import time


# ============================================================
# AIR MOUSE HANDLER
# ============================================================
#
# Main controller for:
#
# 1. Shared Camera Server
# 2. AirMouse
# 3. Eye Tracker
#
# AirMouse:
#   - Left click
#   - Right click
#   - Scroll
#   - Drag
#   - Task View
#   - Voice commands
#
# Eye Tracker:
#   - Cursor movement ONLY
#
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

CAMERA_SERVER = (
    r"C:Desktop"
    r"\AirMouseHandler\camera_server.py"
)

AIR_MOUSE = (
    r"C:Desktop"
    r"\Airmouse\air_mouse.py"
)

EYE_TRACKER = (
    r"C:webcam-eye-tracker"
    r"\blue_virtual_trackpad.py"
)


# ============================================================
# PROCESS REFERENCES
# ============================================================

camera_server_process = None

air_mouse_process = None

eye_tracker_process = None


# ============================================================
# START PROGRAMS
# ============================================================

def start_programs():

    global camera_server_process
    global air_mouse_process
    global eye_tracker_process


    print()
    print("=" * 65)
    print("                  AIR MOUSE HANDLER")
    print("=" * 65)
    print()


    # ========================================================
    # START SHARED CAMERA SERVER
    # ========================================================

    print("Starting Shared Camera Server...")

    camera_server_process = subprocess.Popen(
        [
            sys.executable,
            CAMERA_SERVER
        ]
    )


    # Give the camera server time to open the webcam.

    time.sleep(3)


    if camera_server_process.poll() is not None:

        print()
        print("ERROR: Camera Server stopped unexpectedly.")
        print()

        return False


    print("Shared Camera Server started.")
    print()


    # ========================================================
    # START AIR MOUSE
    # ========================================================

    print("Starting AirMouse...")

    air_mouse_process = subprocess.Popen(
        [
            sys.executable,
            AIR_MOUSE
        ]
    )


    time.sleep(2)


    if air_mouse_process.poll() is not None:

        print()
        print("WARNING: AirMouse stopped immediately.")
        print()


    else:

        print("AirMouse started.")


    print()


    # ========================================================
    # START EYE TRACKER
    # ========================================================

    print("Starting Eye Tracker...")

    eye_tracker_process = subprocess.Popen(
        [
            sys.executable,
            EYE_TRACKER
        ]
    )


    time.sleep(2)


    if eye_tracker_process.poll() is not None:

        print()
        print("WARNING: Eye Tracker stopped immediately.")
        print()


    else:

        print("Eye Tracker started.")


    print()


    # ========================================================
    # STATUS
    # ========================================================

    print("=" * 65)
    print("                 ALL SYSTEMS STARTED")
    print("=" * 65)
    print()

    print("Camera Server -> Shared webcam")
    print("AirMouse      -> Gestures / Clicks / Scroll / Drag / Voice")
    print("Eye Tracker   -> Cursor movement ONLY")

    print()

    print("Press Ctrl+C in this window to stop everything.")

    print()


    return True


# ============================================================
# STOP ONE PROCESS
# ============================================================

def stop_process(process, name):

    if process is None:

        return


    if process.poll() is None:

        print(
            f"Stopping {name}..."
        )


        process.terminate()


        try:

            process.wait(
                timeout=5
            )


        except subprocess.TimeoutExpired:

            print(
                f"{name} did not stop normally. Forcing shutdown..."
            )

            process.kill()


            try:

                process.wait(
                    timeout=2
                )

            except Exception:

                pass


# ============================================================
# STOP ALL PROGRAMS
# ============================================================

def stop_programs():

    global camera_server_process
    global air_mouse_process
    global eye_tracker_process


    print()
    print("=" * 65)
    print("                  SHUTTING DOWN")
    print("=" * 65)
    print()


    # ========================================================
    # STOP EYE TRACKER
    # ========================================================

    stop_process(
        eye_tracker_process,
        "Eye Tracker"
    )


    # ========================================================
    # STOP AIR MOUSE
    # ========================================================

    stop_process(
        air_mouse_process,
        "AirMouse"
    )


    # ========================================================
    # STOP CAMERA SERVER LAST
    # ========================================================

    stop_process(
        camera_server_process,
        "Camera Server"
    )


    print()
    print("All systems stopped.")
    print()


# ============================================================
# MAIN
# ============================================================

try:

    started = start_programs()


    if not started:

        stop_programs()

        raise SystemExit


    while True:

        # ====================================================
        # CHECK CAMERA SERVER
        # ====================================================

        if camera_server_process is not None:

            if camera_server_process.poll() is not None:

                print()
                print(
                    "Camera Server has stopped."
                )

                print(
                    "Stopping all systems..."
                )

                break


        # ====================================================
        # CHECK AIR MOUSE
        # ====================================================

        if air_mouse_process is not None:

            if air_mouse_process.poll() is not None:

                print()
                print(
                    "AirMouse has stopped."
                )

                print(
                    "Stopping all systems..."
                )

                break


        # ====================================================
        # CHECK EYE TRACKER
        # ====================================================

        if eye_tracker_process is not None:

            if eye_tracker_process.poll() is not None:

                print()
                print(
                    "Eye Tracker has stopped."
                )

                print(
                    "Stopping all systems..."
                )

                break


        time.sleep(1)


except KeyboardInterrupt:

    print()
    print(
        "Handler shutdown requested."
    )


finally:

    stop_programs()


    print("=" * 65)
    print("              AIR MOUSE HANDLER STOPPED")
    print("=" * 65)
    print()