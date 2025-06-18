import cv2
import mediapipe as mp
import numpy as np
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# video feed
cap = cv2.VideoCapture(1)
threshold = 0.1
prev_y = None
prev_x = None
prev_bend_y = None
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while True:
        ret, frame = cap.read()

        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        results = pose.process(image)

        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract Landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            # print(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
        except:
            pass

        if results.pose_landmarks:
            # Get normalized y of left shoulder
            left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
            nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
            left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]

            current_y = nose.y
            current_x = left_shoulder.x
            current_bend_y = left_hip.y

            # Detect vertical movement
            if prev_y is not None:

                change = prev_y - current_y  # if shoulder moved up, this will be positive

                if change > threshold:
                    cv2.putText(image, "Jump Detected!", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    print("Jump detected - shoulder moved up rapidly")
                    pyautogui.press('up')

            prev_y = current_y

            if prev_bend_y is not None:

                change = prev_bend_y - current_bend_y

                if change < -threshold:
                    cv2.putText(image, "Bend Detected!", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    print("Bend detected - shoulder moved down rapidly")
                    pyautogui.press('down')

            prev_bend_y = current_bend_y

            # Detect horizontal movement
            if prev_x is not None:

                change = prev_x - current_x
                if change > threshold:
                    cv2.putText(image, "left Detected!", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    print("left detected - shoulder moved left rapidly")
                    pyautogui.press('left')
                elif change < -threshold:
                    cv2.putText(image, "right Detected!", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    print("right detected - shoulder moved right rapidly")
                    pyautogui.press('right')

            prev_x = current_x

            # elif change < 0:
            #     cv2.putText(image, "Bend Detected!", (50, 50),
            #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            #     print("Bend detected - shoulder moved down rapidly")
            # elif prev_y is not None:
            #
            #     if prev_x is not None:
            #         change = prev_x - current_x  # if shoulder moved left, this will be positive
            #         if change > 0:
            #             cv2.putText(image, "left Detected!", (50, 50),
            #                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            #             print("left detected - shoulder moved left rapidly")
            #
            #         elif change < 0:
            #             cv2.putText(image, "right Detected!", (50, 50),
            #                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            #             print("right detected - shoulder moved right rapidly")


        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66),thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(245, 66, 20),thickness=2, circle_radius=2),)
        # print(mp_pose.POSE_CONNECTIONS)

        # print(results)
        cv2.imshow('mediapipe frame', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()