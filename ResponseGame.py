import cv2 as cv
import numpy as np
import HandTrackingModule as hmt
import time
import GameTimer as gt
import random

# Define used fingers as constants
INDEX = 8
# Define currently used camera
USEDCAMERA = 0
# Define camera width and height
CAMWIDTH = 640
CAMHEIGHT = 480
# Define index highlight color
HIGHLIGHTCOLOR = (80, 75, 185)
# Define text color
TEXTCOLOR = (180, 100, 200)
# Define target color
TARGETCOLOR = (0, 0, 0)


def create_target(frame):
    create = random.randint(0, 5)
    if create < 4:
        randx = random.randint(10, CAMWIDTH - 10)
        randy = random.randint(10, CAMHEIGHT - 10)
        return randx, randy
    return -1, -1


def check_hit(index_x, index_y, target_x, target_y):
    if (target_x - 10 < index_x < target_x + 10) & (target_y - 10 < index_y < target_y + 10):
        print("Shhiit")
        return True
    return False


def main():
    model = hmt.HandDetector()
    game_timer = gt.GameTimer()
    # Define camera input and dimensions
    cap = cv.VideoCapture(USEDCAMERA)  # Capture the video from the camera
    cap.set(3, CAMWIDTH)
    cap.set(4, CAMHEIGHT)
    # For FPS calculation, fps = 1/time delta
    prev_frame_time = 0
    target_exists = False  # True if a target exists
    score = 0  # User score
    response_time = 0  # User response time
    targetx = targety = 0

    # Main loop
    while True:
        ret, frame = cap.read()
        frame = model.find_hands(frame)
        landmarks = model.find_landmarks(frame)
        if len(landmarks) != 0:  # Can perform actions only if landmarks were found
            index_x, index_y = landmarks[INDEX][1], landmarks[INDEX][2]
            # Highlight the index finger
            cv.circle(frame, (index_x, index_y), 10, HIGHLIGHTCOLOR, cv.FILLED)
            if not target_exists:
                targetx, targety = create_target(frame)
                if targetx >= 0:
                    target_exists = True
                    game_timer.start_timer()
            else:
                cv.circle(frame, (targetx, targety), 15, TARGETCOLOR, cv.FILLED)
                hit = check_hit(index_x, index_y, targetx, targety)
                if hit:
                    response_time += game_timer.stop_timer()
                    score += 1
                    target_exists = False



        # FPS printing on the screen
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        cv.putText(frame, "fps: " + str(int(fps)), (30, 30), cv.FONT_HERSHEY_SIMPLEX, 1, TEXTCOLOR, 1)
        cv.putText(frame, "score: " + str(score), (30, 50), cv.FONT_HERSHEY_SIMPLEX, 1, TEXTCOLOR, 1)
        cv.putText(frame, "time: " + str(response_time), (30, 70), cv.FONT_HERSHEY_SIMPLEX, 1, TEXTCOLOR, 1)

        if ret:  # If a frame exists
            cv.imshow('Camera', frame)  # Display the current frame (BGR frame)
            if cv.waitKey(1) & 0xFF == ord('q'):  # Press 'q' key to stop and exit
                break
        else:  # No frame exists, break the loop
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
