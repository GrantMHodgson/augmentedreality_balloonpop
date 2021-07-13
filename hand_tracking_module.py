# import tensorflow as tf
import mediapipe as mp
import cv2
import time
import math

class handDetector():
    def __init__(self, static_image_mode=False, max_num_hands = 2, min_detection_confidence = 0.5,
                 min_tracking_confidence=0.5):
        self.mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = 0.5
        # this is the hand tracking model that allows us to detect hand poses
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.max_num_hands, self.min_detection_confidence,
                                        self.min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, image, draw=False):
        # need to convert BGR image to RGB because opencv takes in images in BGR format
        # but mp needs images in RGB format
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # hands module processes image
        # imgRGB.flags.writeable = False
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            if draw:
                for hand_marks in self.results.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(image, hand_marks, self.mpHands.HAND_CONNECTIONS)

        return self.results

    def get_positions(self, image, draw=False):
        detected_landmarks = {}
        if self.results.multi_hand_landmarks:
            # multi_hand_landmarks is a tuple with 1) hand landmarks on each detected hand and 2) a "multi_handedness"
            # field that contains the handedness (left v.s. right hand) of the detected hand.
            # We are just interested in the landmarks so the index is 0
            hand = self.results.multi_hand_landmarks[0]

            # get ids for each landmark in detected hand. Each landmark has an x,y,z coordinates.
            # The coordinates are in decimal form as ratios of the image so
            # multiply by width or height to obtain pixel values.
            for id, landmark in enumerate(hand.landmark):
                height, width, channels = image.shape
                center_x, center_y = int(landmark.x * width), int(landmark.y * height)
                detected_landmarks[id] = (center_x, center_y)
                if draw:
                    cv2.circle(image, (center_x, center_y), 15, (255,0,255), cv2.FILLED)

        return detected_landmarks

    def detect_shot_fired(self):
        pass

    def detect_touch_enemy(self, enemy, image):

        hit = False
        positions = self.get_positions(image)
        if int(8) in positions:
            dx = (positions[8][0] - enemy.x_loc) ** 2
            dy = (positions[8][1] - enemy.y_loc) ** 2
            distance = math.sqrt(dx + dy)
            # print(f"distance from enemy is: {distance}")
            if distance < 50:
                hit = True
                # print(f"enemy poked at {enemy.x_loc}, {enemy.y_loc}")
        return hit



def main():
    prev_time = 0
    cur_time = 0
    # start up webcam
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        # capture video from webcam
        success, img = cap.read()
        results = detector.find_hands(img)
        if results.multi_hand_landmarks:
            for hand_marks in results.multi_hand_landmarks:
                detector.mpDraw.draw_landmarks(img, hand_marks, detector.mpHands.HAND_CONNECTIONS)

        landmark_list = detector.get_positions(img)
        if len(landmark_list) > 0:
            print(landmark_list[4])

        cur_time = time.time()
        fps = 1 / (cur_time - prev_time)
        prev_time = cur_time
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__=="__main__":
    main()