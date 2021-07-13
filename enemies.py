import cv2
import imutils

MOVE_DISTANCE = 5
BALLOON_HEIGHT = 50
BALLOON_WIDTH = 50

class Enemy:

    def __init__(self, y_loc):
        # TODO: change to numpy array?
        # self.enemies = []
        self.level = 1
        # the x,y coordinates mark where the top left corner of the image will appear on the screen
        self.x_loc = 0
        self.y_loc = y_loc
        img = cv2.imread('balloon.jpg')
        self.image = imutils.resize(img, height=BALLOON_HEIGHT, width=BALLOON_WIDTH)
        self.poked = False
        self.move_direction = 1

    def move(self, image_height, image_width):

        far_right_xcor = self.x_loc + MOVE_DISTANCE + BALLOON_WIDTH
        # print(f"far right xcor: {far_right_xcor}")
        if far_right_xcor > image_width:
            self.move_direction = -1

        # check if balloon is off the left side of the image
        if self.x_loc - MOVE_DISTANCE < 0:
            self.move_direction = 1

        self.x_loc += (MOVE_DISTANCE * self.move_direction)
        # self.y_loc += STARTING_MOVE_DISTANCE

    def update_poke(self):
        self.poked = True
        new_img = cv2.imread("popped_balloon.png")
        self.image = imutils.resize(new_img, height=BALLOON_HEIGHT, width=BALLOON_WIDTH)
