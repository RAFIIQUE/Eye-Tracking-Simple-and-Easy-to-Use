# Eye-Controlled Mouse Movement

This repository contains code that uses a webcam to track eye movements in real-time and control the mouse cursor accordingly. By detecting the position of specific eye landmarks, the program can move the cursor in four directions (left, right, up, down) based on your gaze. It also allows you to perform mouse clicks by blinking.

## Features

- **Eye Gaze-Based Cursor Control:**  
  Move your eyes in a particular direction to shift the mouse cursor. The code establishes a baseline eye position and detects relative movements exceeding a chosen threshold to determine direction.

- **Blink Detection for Clicks:**  
  By measuring distances between specific eye landmarks, the program identifies blinks and simulates mouse clicks without needing physical input.

- **State Machine Approach:**  
  The application uses a state machine for predictable and user-friendly interaction:
  - **PROMPT_DIRECTION:** Prompts you to choose a direction by moving your eyes.
  - **WAITING_FOR_DIRECTION:** Waits a few seconds before capturing your eye position to determine the direction.
  - **MOVING_CURSOR:** Executes the movement after a short countdown.
  - **COOLDOWN:** Introduces a brief delay before prompting for the next move, preventing rapid, unintended cursor shifts.

- **Configurable Parameters:**  
  Adjust key variables (movement threshold, cooldown duration, move distance, frames per second) to suit your environment and preferences.

- **Responsive and Non-Blocking:**  
  The code avoids long blocking calls. It regularly updates the OpenCV GUI window and processes frames continuously, ensuring the interface does not freeze or become unresponsive.

## Dependencies

- Python 3.10
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- PyAutoGUI (`pyautogui`)
- psutil

Install dependencies:
```bash
pip install opencv-python mediapipe pyautogui psutil
