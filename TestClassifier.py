import pickle
import numpy as np
import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

model_dict = pickle.load(open('modelforgame.p', 'rb'))
model = model_dict['model']

cap = cv2.VideoCapture(1)

lables_dict = {0: 'Down', 1: 'Up', 2: 'Right', 3: 'Left'}

while True:
    data_aux = []
    x_ = []
    y_ = []
    ret, frame = cap.read()

    h, w, _ = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, handLms,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

        for hand_landmarks in results.multi_hand_landmarks:
            data_aux = []
            x_ = []
            y_ = []

            for landmark in hand_landmarks.landmark:
                x = landmark.x
                y = landmark.y
                data_aux.append(x)
                data_aux.append(y)
                x_.append(x)
                y_.append(y)

            x1 = int(min(x_) * w) - 10
            y1 = int(min(y_) * h) - 10
            x2 = int(max(x_) * w) - 10
            y2 = int(max(y_) * h) - 10

        prediction = model.predict([np.asarray(data_aux)])
        predicted_character = lables_dict[int(prediction[0])]

        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,0), 4)
        cv2.putText(frame, predicted_character , (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 1.3, (0, 0, 0), 3,cv2.LINE_AA)
        if predicted_character == 'Up':
            pyautogui.press('up')
        elif predicted_character == 'Right':
            pyautogui.press('right')
        elif predicted_character == 'Down':
            pyautogui.press('down')
        elif predicted_character == 'Left':
            pyautogui.press('left')
        else:
            cv2.putText(frame, "Idle",(30, 30), cv2.FONT_HERSHEY_COMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

    cv2.imshow('frame', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()