import cv2 as cv
import mediapipe as mp
import time

# Define currently used camera
USEDCAMERA = 0
# Define camera width and height
CAMWIDTH = 640
CAMHEIGHT = 480
# Define text color
TEXTCOLOR = (100, 150, 210)


# The hand detector model class.
# Initialize with empty parenthesis or pass the desired values in the object initialization.
# The arguments passed are the arguments needed to create the mediapipe Hands model
class HandDetector:
    def __init__(self,
                 static_image_mode=False,
                 max_num_hands=2,
                 model_complexity=1,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        self.results = None
        self.mode = static_image_mode
        self.max_hands = max_num_hands
        self.complexity = model_complexity
        self.minimal_detection_confidence = min_detection_confidence
        self.minimal_tracking_confidence = min_tracking_confidence
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.complexity,
                                         self.minimal_detection_confidence,
                                         self.minimal_tracking_confidence)  # Create a mediapipe Hands class object.
        self.mp_draw_utility = mp.solutions.drawing_utils  # Create a mediapipe drawing utility to draw the points

    # find_hands() takes a frame, activates mediapipe's hand tracking algorithm and returns the frame with the hands
    # marked (points and connecting lines). As default the 'draw' argument is set to 'True'. Set to 'False' to cancel
    # drawing the points and lines on the frame.
    def find_hands(self, frame, draw=True):
        rgb_frame = cv.cvtColor(frame,  # Convert the image to RGB. mediapipe uses RGB images
                                cv.COLOR_BGR2RGB)  # and open-cv uses BGR images.
        self.results = self.hands.process(rgb_frame)  # Process the frame using the Hands.process() method
        if self.results.multi_hand_landmarks:  # If True, a hand or more were found. Else equals to None
            for hand in self.results.multi_hand_landmarks:  # Loop through the found hands and perform actions on each
                if draw:
                    self.mp_draw_utility.draw_landmarks(frame, hand,  # Draw the 21 points
                                                        self.mp_hands.HAND_CONNECTIONS)  # and the connecting lines
                    # on each hand
        return frame

    # find_position() takes a frame and the hand number to be processed (set as default to '0' - the first hand in
    # the list), finds the position of each point and returns that list
    def find_landmarks(self, frame, hand_number=USEDCAMERA):
        landmarks = []
        if self.results.multi_hand_landmarks:  # If True, a hand or more were found. Else equals to None
            hand = self.results.multi_hand_landmarks[hand_number]
            for index, landmark in enumerate(hand.landmark):  # Match the index of the landmark to the landmark
                frame_height, frame_width, channels = frame.shape
                center_x, center_y = int(landmark.x * frame_width), int(landmark.y * frame_height)
                landmarks.append([index, center_x, center_y])
        return landmarks

    def run(self):
        # Define camera input and dimensions
        cap = cv.VideoCapture(0)  # Capture the video from the camera
        cap.set(3, CAMWIDTH)
        cap.set(4, CAMHEIGHT)
        # For FPS calculation, fps = 1/time delta
        prev_frame_time = 0
        while True:
            ret, frame = cap.read()
            frame = self.find_hands(frame)
            self.find_landmarks(frame)
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
        cv.destroyAllWindows()
