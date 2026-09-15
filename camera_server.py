import cv2
import socket
import struct
import threading
import time


# ============================================================
# SHARED CAMERA SERVER
# ============================================================
#
# This program owns the physical webcam.
#
# AirMouse and Eye Tracker receive the same camera frames
# from this server.
#
# ONE WEBCAM
#     ↓
# camera_server.py
#     ↓
# shared frames
#     ├── AirMouse
#     └── Eye Tracker
#
# ============================================================


# ============================================================
# SETTINGS
# ============================================================

CAMERA_INDEX = 0

HOST = "127.0.0.1"

PORT = 5000

JPEG_QUALITY = 80

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(
    CAMERA_INDEX
)

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAMERA_WIDTH
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAMERA_HEIGHT
)

camera.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1
)


if not camera.isOpened():

    print()
    print("=" * 60)
    print("ERROR: COULD NOT OPEN WEBCAM")
    print("=" * 60)
    print()

    raise SystemExit(1)


# ============================================================
# SERVER
# ============================================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(
    (HOST, PORT)
)

server.listen(5)

server.settimeout(1.0)


# ============================================================
# CLIENT MANAGEMENT
# ============================================================

clients = []

clients_lock = threading.Lock()

running = True


# ============================================================
# SEND FRAME TO CLIENT
# ============================================================

def send_frame(
    client_socket,
    encoded_frame
):

    data = encoded_frame.tobytes()

    packet = struct.pack(
        "!I",
        len(data)
    ) + data

    client_socket.sendall(
        packet
    )


# ============================================================
# CLIENT HANDLER
# ============================================================

def client_handler(
    client_socket,
    address
):

    print(
        "Client connected:",
        address
    )

    with clients_lock:

        clients.append(
            client_socket
        )

    try:

        while running:

            # The main camera loop sends frames.
            # This thread simply keeps the connection alive.

            time.sleep(1)

    except Exception:

        pass

    finally:

        with clients_lock:

            if client_socket in clients:

                clients.remove(
                    client_socket
                )

        try:

            client_socket.close()

        except Exception:

            pass

        print(
            "Client disconnected:",
            address
        )


# ============================================================
# ACCEPT CLIENTS
# ============================================================

def accept_clients():

    while running:

        try:

            client_socket, address = (
                server.accept()
            )

            thread = threading.Thread(
                target=client_handler,
                args=(
                    client_socket,
                    address
                ),
                daemon=True
            )

            thread.start()

        except socket.timeout:

            continue

        except Exception:

            if running:

                print(
                    "Client connection error."
                )

            break


# ============================================================
# START CLIENT ACCEPTOR
# ============================================================

client_thread = threading.Thread(
    target=accept_clients,
    daemon=True
)

client_thread.start()


# ============================================================
# START MESSAGE
# ============================================================

print()
print("=" * 60)
print("             SHARED CAMERA SERVER")
print("=" * 60)
print()

print(
    f"Camera: {CAMERA_INDEX}"
)

print(
    f"Resolution: {CAMERA_WIDTH} x {CAMERA_HEIGHT}"
)

print(
    f"Server: {HOST}:{PORT}"
)

print()

print("Webcam successfully opened.")
print("Waiting for AirMouse / Eye Tracker...")
print()

print("Press Q in the camera window to stop.")

print("=" * 60)
print()


# ============================================================
# CAMERA LOOP
# ============================================================

try:

    while True:

        success, frame = camera.read()

        if not success:

            print(
                "WARNING: Could not grab camera frame."
            )

            time.sleep(0.05)

            continue


        # ====================================================
        # ENCODE FRAME
        # ====================================================

        success, encoded = cv2.imencode(

            ".jpg",

            frame,

            [
                cv2.IMWRITE_JPEG_QUALITY,
                JPEG_QUALITY
            ]

        )


        if not success:

            continue


        # ====================================================
        # SEND FRAME TO ALL CLIENTS
        # ====================================================

        dead_clients = []


        with clients_lock:

            current_clients = list(
                clients
            )


        for client_socket in current_clients:

            try:

                send_frame(
                    client_socket,
                    encoded
                )

            except Exception:

                dead_clients.append(
                    client_socket
                )


        # ====================================================
        # REMOVE DEAD CLIENTS
        # ====================================================

        if dead_clients:

            with clients_lock:

                for client_socket in dead_clients:

                    if client_socket in clients:

                        clients.remove(
                            client_socket
                        )

                    try:

                        client_socket.close()

                    except Exception:

                        pass


        # ====================================================
        # CAMERA PREVIEW
        # ====================================================

        cv2.imshow(
            "Shared Camera Server",
            frame
        )


        # ====================================================
        # QUIT
        # ====================================================

        key = (
            cv2.waitKey(1)
            & 0xFF
        )


        if key == ord("q"):

            break


except KeyboardInterrupt:

    print()

    print(
        "Camera server shutdown requested."
    )


finally:

    running = False


    # ========================================================
    # CLOSE CLIENTS
    # ========================================================

    with clients_lock:

        for client_socket in clients:

            try:

                client_socket.close()

            except Exception:

                pass

        clients.clear()


    # ========================================================
    # CLOSE SERVER
    # ========================================================

    try:

        server.close()

    except Exception:

        pass


    # ========================================================
    # CLOSE CAMERA
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()


    print()

    print("=" * 60)
    print("SHARED CAMERA SERVER STOPPED")
    print("=" * 60)