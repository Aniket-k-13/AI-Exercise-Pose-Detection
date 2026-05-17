import cv2
import mediapipe as mp
import numpy as np
import time
import pyttsx3
import threading

# Thread-safe TTS
def speak(text):
    def run():
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        voices = engine.getProperty('voices')
        for voice in voices:
            if "english" in voice.name.lower() and "female" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

def is_standing_straight(landmarks):
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y

    # Check both legs are straight down (ankles below knees, knees below hips)
    both_feet_down = abs(left_ankle - right_ankle) < 0.05
    legs_straight = (left_knee > left_hip) and (right_knee > right_hip)
    return both_feet_down and legs_straight

def is_tree_pose(landmarks):
    # Detect tree pose with right leg up (standing on left leg)
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    # Right foot lifted above knee
    right_foot_up = right_ankle.y < right_knee.y - 0.1

    # Left leg supporting (standing)
    left_leg_straight = (left_knee.y > left_hip.y) and (left_ankle.y > left_knee.y)

    return right_foot_up and left_leg_straight

def main(duration_sec=20):
    global mp_pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    stage = "waiting"  # waiting, ready, holding
    start_time = None

    speak("Stand straight to begin.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            if stage == "waiting" and is_standing_straight(lm):
                speak("Now raise your right leg for Tree Pose.")
                stage = "ready"
                time.sleep(1)

            elif stage == "ready" and is_tree_pose(lm):
                speak("Hold the Tree Pose!")
                start_time = time.time()
                stage = "holding"

            elif stage == "holding":
                elapsed = time.time() - start_time
                remaining = max(0, int(duration_sec - elapsed))

                # Timer display
                cv2.putText(frame, f"Time Left: {remaining}s", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)

                if remaining <= 0:
                    speak("Time's up! Great job.")
                    break

        if results.pose_landmarks:
            drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow("Tree Pose Timer", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(duration_sec=20)
