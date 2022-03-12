import cv2 as cv
import numpy as np
import HandTrackingModule as hmt
import time
import keyboard
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Define used fingers as constants
THUMB = 4
INDEX = 8
# Define currently used camera
USEDCAMERA = 0
# Define camera width and height
CAMWIDTH = 640
CAMHEIGHT = 480
# Define fingers range borders
MINVOLDISTANCE = 20 * (CAMWIDTH / 640)
MAXVOLDISTANCE = 120 * (CAMHEIGHT / 480)
# Define index/thumb highlight color
HIGHLIGHTCOLOR = (200, 150, 100)
# Define text color
TEXTCOLOR = (100, 150, 210)


def get_volume_object():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume, volume.GetMasterVolumeLevel()


def get_volumes(volume):
    # volume.GetMute()
    min, max, interval = volume.GetVolumeRange()
    original = volume.GetMasterVolumeLevel()
    return min, max, original


def get_fingers_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def main():
    model = hmt.HandDetector()
    volume, current_volume = get_volume_object()
    min_volume, max_volume, original_volume = get_volumes(volume)

    # Define camera input and dimensions
    cap = cv.VideoCapture(USEDCAMERA)  # Capture the video from the camera
    cap.set(3, CAMWIDTH)
    cap.set(4, CAMHEIGHT)
    # For FPS calculation, fps = 1/time delta
    prev_frame_time = 0

    # Main loop
    while True:
        ret, frame = cap.read()
        frame = model.find_hands(frame)
        landmarks = model.find_landmarks(frame)
        if len(landmarks) != 0:  # Can perform actions only if landmarks were found
            thumb_x, thumb_y = landmarks[THUMB][1], landmarks[THUMB][2]
            index_x, index_y = landmarks[INDEX][1], landmarks[INDEX][2]
            distance = get_fingers_distance(thumb_x, thumb_y, index_x, index_y)
            if keyboard.is_pressed("v"):  # Volume control
                # Highlight the index finger and the thumb
                cv.circle(frame, (thumb_x, thumb_y), 10, HIGHLIGHTCOLOR, cv.FILLED)
                cv.circle(frame, (index_x, index_y), 10, HIGHLIGHTCOLOR, cv.FILLED)
                cv.line(frame, (thumb_x, thumb_y), (index_x, index_y), HIGHLIGHTCOLOR, 2)
                # Interpolate  between the fingers distance range and the system volume range using the current distance
                current_volume = np.interp(distance, [MINVOLDISTANCE, MAXVOLDISTANCE], [min_volume,
                                                                                        max_volume])
                volume.SetMasterVolumeLevel(current_volume, None)  # Set new volume
                actual_volume = np.interp(distance, [MINVOLDISTANCE, MAXVOLDISTANCE], [0, 100])
                cv.putText(frame, "volume: " + str(int(actual_volume)) + '%', (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1,
                           TEXTCOLOR, 2)

        # FPS printing on the screen
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        cv.putText(frame, "fps: " + str(int(fps)), (30, 30), cv.FONT_HERSHEY_SIMPLEX, 1, TEXTCOLOR, 2)
        if ret:  # If a frame exists
            cv.imshow('Camera', frame)  # Display the current frame (BGR frame)
            if cv.waitKey(1) & 0xFF == ord('q'):  # Press 'q' key to stop and exit
                break
        else:  # No frame exists, break the loop
            break
    volume.SetMasterVolumeLevel(original_volume, None)  # Revert to original volume
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
