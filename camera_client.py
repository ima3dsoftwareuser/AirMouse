import socket
import struct
import cv2
import numpy as np


# ============================================================
# SHARED CAMERA CLIENT
# ============================================================
#
# Connects to camera_server.py.
#
# The server owns the physical webcam.
# This client receives the same camera frames over localhost.
#
# This file does NOT control the mouse.
# ============================================================


HOST = "127.0.0.1"
PORT = 5050


# ============================================================
# CONNECT TO CAMERA SERVER
# ============================================================

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect(
    (HOST, PORT)
)

print()
print("=" * 60)
print("             CAMERA CLIENT")
print("=" * 60)
print()
print("Connected to shared camera server.")
print()
print("Press Q to quit.")
print()


# ============================================================
# RECEIVE EXACT NUMBER OF BYTES
# ============================================================

def receive_exactly(
    number_of_bytes
):

    data = b""

    while len(data) < number_of_bytes:

        chunk = client.recv(
            number_of_bytes - len(data)
        )

        if not chunk:

            return None

        data += chunk

    return data


# ============================================================
# RECEIVE FRAME
# ============================================================

def receive_frame():

    # --------------------------------------------------------
    # Receive 4-byte frame size
    # --------------------------------------------------------

    size_data = receive_exactly(4)

    if size_data is None:

        return None

    frame_size = struct.unpack(
        "!I",
        size_data
    )[0]


    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if frame_size <= 0:

        return None

    if frame_size > 10_000_000:

        print(
            "Invalid frame size:",
            frame_size
        )

        return None


    # --------------------------------------------------------
    # Receive JPEG frame
    # --------------------------------------------------------

    frame_data = receive_exactly(
        frame_size
    )

    if frame_data is None:

        return None


    # --------------------------------------------------------
    # Convert JPEG bytes to OpenCV frame
    # --------------------------------------------------------

    array = np.frombuffer(
        frame_data,
        dtype=np.uint8
    )

    frame = cv2.imdecode(
        array,
        cv2.IMREAD_COLOR
    )

    return frame


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        frame = receive_frame()

        if frame is None:

            print(
                "Camera server disconnected."
            )

            break


        # ----------------------------------------------------
        # Show received frame
        # ----------------------------------------------------

        cv2.imshow(
            "Shared Camera Client",
            frame
        )


        # ----------------------------------------------------
        # Quit
        # ----------------------------------------------------

        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        if key == ord("q"):

            break


finally:

    client.close()

    cv2.destroyAllWindows()

    print()
    print("=" * 60)
    print("CAMERA CLIENT STOPPED")
    print("=" * 60)