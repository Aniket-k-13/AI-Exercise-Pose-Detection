import cv2
import mediapipe as mp
import numpy as np
import time
import pyttsx3
import threading
import math

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

# Calculate angle between 3 points (in radians converted to degrees)
def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def is_cobra_pose(landmarks):
    mp_pose = mp.solutions.pose

    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
    right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]

    # Average y values
    hip_y = (left_hip.y + right_hip.y) / 2
    knee_y = (left_knee.y + right_knee.y) / 2
    shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    wrist_y = (left_wrist.y + right_wrist.y) / 2
    elbow_y = (left_elbow.y + right_elbow.y) / 2

    # Average x values
    left_wrist_x = left_wrist.x
    left_elbow_x = left_elbow.x
    right_wrist_x = right_wrist.x
    right_elbow_x = right_elbow.x

    # 1. Chest lifted: shoulders much higher than hips (remember y is inverted - smaller is higher)
    chest_lifted = shoulder_y + 0.15 < hip_y

    # 2. Hips low: hips close to or below knees (hips should not be raised)
    hips_low = hip_y >= knee_y - 0.03

    # 3. Head lifted: nose above shoulders
    head_lifted = nose.y + 0.05 < shoulder_y

    # 4. Wrists below elbows vertically (supporting body weight)
    wrists_below_elbows = (left_wrist.y > left_elbow.y) and (right_wrist.y > right_elbow.y)

    # 5. Elbow angles between 70 and 160 degrees (arms bent, not locked or fully folded)
    left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
    elbows_ok = (70 < left_elbow_angle < 160) and (70 < right_elbow_angle < 160)

    # 6. Wrists roughly below elbows horizontally (x difference less than 0.1)
    wrist_elbow_x_ok = (abs(left_wrist_x - left_elbow_x) < 0.1) and (abs(right_wrist_x - right_elbow_x) < 0.1)

    cobra = all([chest_lifted, hips_low, head_lifted, wrists_below_elbows, elbows_ok, wrist_elbow_x_ok])
    
    # For debugging, uncomment below to see values printed:
    # print(f"Chest lifted: {chest_lifted}, Hips low: {hips_low}, Head lifted: {head_lifted}")
    # print(f"Wrists below elbows: {wrists_below_elbows}, Elbow angles: {left_elbow_angle:.1f}, {right_elbow_angle:.1f}")
    # print(f"Wrist-Elbow horizontal ok: {wrist_elbow_x_ok}")

    return cobra

def main(duration_sec=30):
    global mp_pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    stage = "waiting"  # waiting, holding
    start_time = None

    speak("Please get into Cobra Pose to start the timer.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            if stage == "waiting":
                if is_cobra_pose(lm):
                    speak("Cobra Pose detected. Starting timer. Hold it for 30 seconds.")
                    stage = "holding"
                    start_time = time.time()
                else:
                    cv2.putText(frame, "Get into Cobra Pose", (30, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
            elif stage == "holding":
                elapsed = time.time() - start_time
                remaining = max(0, int(duration_sec - elapsed))
                cv2.putText(frame, f"Time Left: {remaining}s", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

                # Check if still holding pose, else reset
                if not is_cobra_pose(lm):
                    speak("Cobra pose lost! Timer stopped. Please get back into pose.")
                    stage = "waiting"
                    start_time = None
                elif remaining <= 0:
                    speak("Time's up! Great job holding the Cobra Pose.")
                    break

        else:
            cv2.putText(frame, "No person detected", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

        if results.pose_landmarks:
            drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow("Cobra Pose Timer", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(duration_sec=30)
