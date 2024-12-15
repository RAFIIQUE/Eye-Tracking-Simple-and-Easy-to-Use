import time
import psutil
import cv2
import mediapipe as mp
import pyautogui
import sys

# Editable parameters
scaling_factor = 2
fps = 30
cam = cv2.VideoCapture(1)

face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

prev_time = 0
center_x = screen_w / 2
center_y = screen_h / 2
pyautogui.moveTo(center_x, center_y)

ret, frame = cam.read()
if ret:
    frame_h, frame_w, _ = frame.shape
    pyautogui.moveTo(center_x, center_y)

baseline_set = False
baseline_x = None
baseline_y = None

threshold = 0.005     # Adjusted eye movement threshold
move_distance = 200   # how many pixels to move per command
cooldown = 3          # cooldown seconds after a move

last_move_time = time.time() - cooldown
last_click_time = time.time() - cooldown

# State variables
mode = "IDLE"  # "IDLE", "PROMPT_DIRECTION", "WAITING_FOR_DIRECTION", "MOVING_CURSOR", "COOLDOWN"
direction_detected = None
next_check_time = time.time()

def print_clear(message):
    # Prints a message with a preceding newline to separate from previous outputs
    print("\n" + message)

print("Initializing Eye Controlled Mouse...")
print("Centering cursor at start.")
print("Setting up baseline...")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Camera read failed. Exiting.")
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks

    current_time = time.time()
    # Check if it's time to process a frame according to the FPS setting
    if (current_time - prev_time) >= (1 / fps):
        if landmark_points:
            landmarks = landmark_points[0].landmark
            eye_landmark = landmarks[477]  # A key landmark near the eye
            eye_x = eye_landmark.x
            eye_y = eye_landmark.y

            if not baseline_set:
                baseline_x = eye_x
                baseline_y = eye_y
                baseline_set = True
                print_clear("Baseline set. Ready to detect movements.")
                mode = "PROMPT_DIRECTION"
                next_check_time = current_time + 1

            else:
                # State machine approach

                if mode == "PROMPT_DIRECTION":
                    # Tell user to move eyes
                    print_clear("Please move your eyes in the direction you want (Left/Right/Up/Down).")
                    print("We will detect your eye movement in", cooldown, "seconds.")
                    mode = "WAITING_FOR_DIRECTION"
                    next_check_time = current_time + cooldown  # wait `cooldown` seconds before checking direction

                elif mode == "WAITING_FOR_DIRECTION":
                    if current_time >= next_check_time:
                        # Check eye position now
                        diff_x = eye_x - baseline_x
                        diff_y = eye_y - baseline_y

                        # Debugging: Print raw values
                        print(f"Debug: diff_x = {diff_x}, diff_y = {diff_y}")

                        direction_detected = None

                        # Detect movement direction
                        if diff_x < -threshold:
                            direction_detected = "Left"
                        elif diff_x > threshold:
                            direction_detected = "Right"
                        elif diff_y < -threshold:
                            direction_detected = "Up"
                        elif diff_y > threshold:
                            direction_detected = "Down"

                        if direction_detected:
                            print_clear(f"Eye movement detected: {direction_detected}")
                            print(f"Moving cursor {direction_detected.lower()} in 3 seconds.")
                            mode = "MOVING_CURSOR"
                            next_check_time = current_time + 3  # 3 seconds before move
                        else:
                            print_clear("No significant movement detected. Let's try again.")
                            mode = "PROMPT_DIRECTION"
                            next_check_time = current_time + 1

                elif mode == "MOVING_CURSOR":
                    if current_time >= next_check_time:
                        # Perform the cursor move
                        dx, dy = 0, 0
                        if direction_detected == "Left":
                            dx = -move_distance
                        elif direction_detected == "Right":
                            dx = move_distance
                        elif direction_detected == "Up":
                            dy = -move_distance
                        elif direction_detected == "Down":
                            dy = move_distance
                        pyautogui.moveRel(dx, dy)
                        print_clear(f"Boom! Cursor moved {direction_detected.lower()}.")
                        last_move_time = current_time
                        mode = "COOLDOWN"
                        print("Where do you want to move the cursor next? We will check again in a few seconds.")
                        next_check_time = current_time + cooldown

                elif mode == "COOLDOWN":
                    if current_time >= next_check_time:
                        # Ready to prompt direction again
                        mode = "PROMPT_DIRECTION"
                        print_clear("Ready for next move.")
                        next_check_time = current_time + 1

            # Draw eye landmarks
            for lm_id, landmark in enumerate(landmarks[474:478]):
                lx = int(landmark.x * frame_w)
                ly = int(landmark.y * frame_h)
                cv2.circle(frame, (lx, ly), 3, (0, 255, 0), -1)

            # Blink detection for click
            left_eye_top = landmarks[145]
            left_eye_bottom = landmarks[159]
            eye_distance = ((left_eye_bottom.y - left_eye_top.y)**2 +
                            (left_eye_bottom.x - left_eye_top.x)**2)**0.5

            # If blink detected and cooldown passed
            if eye_distance < 0.01 and current_time - last_click_time > cooldown:
                pyautogui.click()
                last_click_time = current_time
                print_clear("Click detected!")

        # Update the displayed frame
        cv2.imshow('Eye Controlled Mouse', frame)
        prev_time = current_time

    # Allow the GUI to process events
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
print("Program exited cleanly.")
