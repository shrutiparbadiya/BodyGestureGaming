import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import threading
from flask import Flask, render_template, Response
from PyQt5 import QtWidgets, QtGui, QtCore
import sys

app = Flask(__name__)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

threshold = 0.1
prev_y, prev_x, prev_bend_y = None, None, None
latest_frame = None

# ------------------ Video Generator -------------------
def process_frame():
    global prev_y, prev_x, prev_bend_y, latest_frame
    cap = cv2.VideoCapture(1)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                try:
                    nose = landmarks[mp_pose.PoseLandmark.NOSE]
                    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]

                    current_y = nose.y
                    current_x = left_shoulder.x
                    current_bend_y = left_hip.y

                    if prev_y is not None and prev_y - current_y > threshold:
                        pyautogui.press('up')
                    prev_y = current_y

                    if prev_bend_y is not None:
                        change = prev_bend_y - current_bend_y
                        if change < -threshold:
                            pyautogui.press('down')
                    prev_bend_y = current_bend_y

                    if prev_x is not None:
                        if prev_x - current_x > threshold:
                            pyautogui.press('left')
                        elif prev_x - current_x < -threshold:
                            pyautogui.press('right')
                    prev_x = current_x
                except:
                    pass

                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245, 66, 20), thickness=2, circle_radius=2)
                )

            latest_frame = image.copy()
    cap.release()

# ------------------ Flask Routes -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['GET', 'POST'])
def play():
    return render_template("play_feed.html")

@app.route('/video_feed')
def video_feed():
    def frame_stream():
        global latest_frame
        while True:
            if latest_frame is not None:
                ret, buffer = cv2.imencode('.jpg', latest_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(frame_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ------------------ PyQt Overlay -------------------
class OverlayWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.X11BypassWindowManagerHint |
                            QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(1500, 100, 320, 240)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(0, 0, 320, 240)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        global latest_frame
        if latest_frame is not None:
            frame = cv2.cvtColor(latest_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            img = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.label.setPixmap(QtGui.QPixmap.fromImage(img))

# ------------------ Main -------------------
def run_flask():
    app.run(debug=False, use_reloader=False)

def run_overlay():
    qt_app = QtWidgets.QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    sys.exit(qt_app.exec_())

if __name__ == '__main__':
    threading.Thread(target=process_frame, daemon=True).start()
    threading.Thread(target=run_flask, daemon=True).start()
    run_overlay()
