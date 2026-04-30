"""
select_zones.py
---------------
Interactive tool for defining queue zone polygons on a video frame.

Run this script before queue_system.py whenever you switch to a new camera
or scene. The output is a ZONES dictionary you paste directly into queue_system.py.

Controls:
    Left click  — add a point to the current zone
    ENTER       — finish zone, then type its name in the window and press ENTER again
    R           — remove the last point
    C           — clear the current zone and start over
    ESC         — finish and print all zones to the terminal
"""

import cv2
import numpy as np

# --- Configuration ---

VIDEO_PATH = r"videos\supermarket.mp4"

ZONE_COLOURS = [
    (0,   255, 0),
    (0,   165, 255),
    (255, 0,   0),
    (0,   0,   255),
    (255, 0,   255),
    (0,   255, 255),
]

# --- State ---

zones       = {}
current_pts = []
typing_name = False
typed_text  = ""


def get_colour(index):
    return ZONE_COLOURS[index % len(ZONE_COLOURS)]


def draw_state(base_frame):
    display = base_frame.copy()

    for i, (name, pts) in enumerate(zones.items()):
        colour = get_colour(i)
        arr    = np.array(pts, np.int32)
        overlay = display.copy()
        cv2.fillPoly(overlay, [arr], colour)
        cv2.addWeighted(overlay, 0.15, display, 0.85, 0, display)
        cv2.polylines(display, [arr], isClosed=True, color=colour, thickness=2)
        cx = int(sum(p[0] for p in pts) / len(pts))
        cy = int(sum(p[1] for p in pts) / len(pts))
        cv2.putText(display, name, (cx - 30, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)

    if current_pts:
        colour = get_colour(len(zones))
        for pt in current_pts:
            cv2.circle(display, pt, 5, colour, -1)
        if len(current_pts) >= 2:
            cv2.polylines(display, [np.array(current_pts, np.int32)],
                          isClosed=False, color=colour, thickness=2)

    if typing_name:
        h = display.shape[0]
        cv2.rectangle(display, (0, h - 60), (display.shape[1], h), (30, 30, 30), -1)
        cv2.putText(display, f"Zone name: {typed_text}_",
                    (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(display, "Type name then press ENTER to confirm",
                    (10, h - 42), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)
    else:
        instructions = [
            "LEFT CLICK : add point",
            "ENTER      : finish zone & name it",
            "R          : remove last point",
            "C          : clear current zone",
            "ESC        : finish & print output",
        ]
        for i, line in enumerate(instructions):
            cv2.putText(display, line, (10, 20 + i * 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1)
        cv2.putText(display, f"Zones defined: {len(zones)}",
                    (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    return display


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and not typing_name:
        current_pts.append((x, y))


# --- Setup ---

video = cv2.VideoCapture(VIDEO_PATH)
ret, base_frame = video.read()
video.release()

if not ret:
    raise RuntimeError(f"Could not read video: {VIDEO_PATH}")

cv2.namedWindow("Select Zones")
cv2.setMouseCallback("Select Zones", mouse_callback)

print("Zone selection tool running — draw your zones in the OpenCV window.")


while True:
    cv2.imshow("Select Zones", draw_state(base_frame))
    key = cv2.waitKey(20) & 0xFF

    if typing_name:
        if key == 13:
            name = typed_text.strip() or f"Zone_{len(zones) + 1}"
            zones[name] = list(current_pts)
            current_pts.clear()
            typed_text  = ""
            typing_name = False
        elif key == 8:
            typed_text = typed_text[:-1]
        elif key == 27:
            typed_text  = ""
            typing_name = False
        elif 32 <= key <= 126:
            typed_text += chr(key)
    else:
        if key == 27:
            break
        elif key == 13:
            if len(current_pts) < 3:
                print("Need at least 3 points to define a zone.")
            else:
                typing_name = True
                typed_text  = ""
        elif key == ord('r') and current_pts:
            current_pts.pop()
        elif key == ord('c'):
            current_pts.clear()

cv2.destroyAllWindows()



print("\n" + "=" * 50)
print("COPY THIS INTO queue_system.py:")
print("=" * 50)
print("\nZONES = {")
for name, pts in zones.items():
    print(f'    "{name}": {pts},')
print("}")
