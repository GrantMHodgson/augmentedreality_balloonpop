import tkinter as tki
import threading
import datetime
import imutils
import cv2
import os
from hand_tracking_module import handDetector
from PIL import Image
from PIL import ImageTk
import numpy as np
from enemies import Enemy
import random

class ZapGui:

    def __init__(self, video_stream, output_path):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = video_stream
        self.outputPath = output_path
        self.frame = None
        self.thread = None
        self.stopEvent = None

        # intialize the root window and image panel, set minimum window size
        self.root = tki.Tk()
        self.root.minsize(width=600, height=600)
        self.panel = None

        # create a button, that when pressed, will start a game
        btn = tki.Button(self.root, text="Start!",
                         command=self.start_game)
        btn.pack(side="bottom", fill="both", expand="yes", padx=10,
                 pady=10)

        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        # set a callback to handle when the window is closed
        self.root.wm_title("Bug Zapper")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

    def videoLoop(self):
        detector = handDetector()
        # create first enemy
        enemies = [Enemy(0)]

        # writer = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"MP4V"), 30, (960, 960))
        # DISCLAIMER: I'm not a GUI developer, nor do I even pretend to be. This
        # try/except statement is a pretty ugly hack to get around
        # a RunTime error that Tkinter throws due to threading
        # TODO: fix multithreading issue - this video might help: https://www.youtube.com/watch?v=jnrCpA1xJPQ
        try:
            clean_count = 0
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it
                self.frame = self.vs.read()
                # print(f"original size of video: {self.frame.size}")
                # print(f"type of video {type(self.frame)}")
                self.frame = imutils.resize(self.frame, width=600, height=600)
                # flip the image horizontally to make the position of each hand more intuitive for user
                self.frame = cv2.flip(self.frame, 1)
                results = detector.find_hands(self.frame, draw=True)

                # generate new enemies
                if random.randint(0, 100) > 98:
                    new_enemy = Enemy(random.randint(0, 300))
                    enemies.append(new_enemy)

                #draw enemies on video
                frame = self.draw_enemies(enemies, self.frame)
                # detect whether an enemy has been poked and move enemies across screen
                for enemy in enemies:
                    hit = detector.detect_touch_enemy(enemy, self.frame)
                    enemy.move(self.frame.shape[0], self.frame.shape[1])
                    if hit:
                        enemy.update_poke()
                # writer.write(self.frame)

                # OpenCV represents images in BGR order; however PIL represents images in RGB order,
                # so we need to swap the channels, then convert to PIL and ImageTk format
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # if the panel is None, we need to initialize it
                if self.panel is None:
                    self.panel = tki.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image

                # clean up popped balloon after it has been displayed on the screen for a about a second
                if clean_count > 35: #frame rate is about 30fps
                    enemies = [enemy for enemy in enemies if not enemy.poked]
                    clean_count = 0
                    # print(f"num enemies: {len(enemies)}")
                clean_count += 1

                # if self.stopEvent.is_set():
                #     writer.release()
                #     cv2.destroyAllWindows()
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

    def start_game(self):
        # grab the current timestamp and use it to construct the
        # output path
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))
        # save the file
        cv2.imwrite(p, self.frame.copy())
        print("[INFO] saved {}".format(filename))

    def on_close(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()

    def draw_enemies(self, enemies, frame):
        for enemy in enemies:
            offset_x = enemy.x_loc
            offset_y = enemy.y_loc
            # print(f"frame shape: {frame.shape}, enemy shape: {enemy.image.shape}")
            frame[offset_y:enemy.image.shape[0]+offset_y, offset_x:enemy.image.shape[1]+offset_x] = enemy.image
        return frame


