import cv2
import numpy as np
import pyautogui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

cam = "rtsp://admin:vortex123@192.168.33.64:554/Streaming/Channels/301/"

class CameraThreadTracking(QThread):
    change_image_signal = pyqtSignal(np.ndarray)
    def __init__(self):
        super().__init__()
        self.cam = "redline_Trim.mp4"
        self.vid = cv2.VideoCapture(cam)
    def run(self):
        while 1:
            success, frame = self.vid.read()
            print(success)
            cv2.imshow("Frame", frame)
            self.change_image_signal.emit(frame)
