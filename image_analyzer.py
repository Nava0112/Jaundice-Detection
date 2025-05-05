import cv2
import mediapipe as mp
import numpy as np

# Mediapipe setup
mp_face_mesh = mp.solutions.face_mesh
LEFT_EYE_IDX = [33, 133]
RIGHT_EYE_IDX = [362, 263]

def crop_eye(image, eye_indices, landmarks):
    h, w = image.shape[:2]
    x_coords = [int(landmarks[idx].x * w) for idx in eye_indices]
    y_coords = [int(landmarks[idx].y * h) for idx in eye_indices]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    pad = 5
    x_min, x_max = max(0, x_min - pad), min(w, x_max + pad)
    y_min, y_max = max(0, y_min - pad), min(h, y_max + pad)
    return image[y_min:y_max, x_min:x_max]

def detect_jaundice(image, threshold=30.0):
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([15, 40, 40])
    upper_yellow = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(image_hsv, lower_yellow, upper_yellow)
    yellow_pixels = cv2.countNonZero(yellow_mask)
    total_pixels = image.shape[0] * image.shape[1]
    yellow_percentage = (yellow_pixels / total_pixels) * 100
    return yellow_percentage > threshold

def analyze_eye_image(image):
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_image)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_eye = crop_eye(image, LEFT_EYE_IDX, landmarks)
            right_eye = crop_eye(image, RIGHT_EYE_IDX, landmarks)

            jaundice_left = detect_jaundice(left_eye)
            jaundice_right = detect_jaundice(right_eye)

            return jaundice_left or jaundice_right  # Risk if either eye shows yellow
        else:
            return detect_jaundice(image)  # fallback
