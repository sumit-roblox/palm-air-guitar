"""Air Guitar — webcam-based gesture instrument using MediaPipe + pygame."""

from __future__ import annotations

import time

import cv2
import mediapipe as mp
import pygame
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from numpy.typing import NDArray

# ---------------------------------------------------------------------------
# Pygame initialisation
# ---------------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

# ---------------------------------------------------------------------------
# MediaPipe Hand Landmarker
# ---------------------------------------------------------------------------
base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    running_mode=vision.RunningMode.VIDEO,
)
detector = vision.HandLandmarker.create_from_options(options)

# ---------------------------------------------------------------------------
# Chord shape mapping  (thumb, index, middle, ring, pinky) — 1 = extended
# ---------------------------------------------------------------------------
# fmt: off
SHAPE_MAP: dict[tuple[int, ...], str] = {
    # Original three
    (0, 1, 1, 1, 0): "D",
    (0, 0, 1, 1, 1): "A",
    (0, 1, 1, 0, 1): "G",
    # Expanded chords
    (0, 0, 0, 0, 0): "C",      # all fingers curled (barre-style)
    (1, 1, 1, 1, 1): "E",      # all fingers extended (open E)
    (0, 1, 0, 0, 0): "Am",     # only index extended
    (0, 0, 1, 0, 0): "Em",     # only middle extended
    (0, 0, 0, 1, 1): "C#",     # ring + pinky
    (0, 1, 0, 1, 0): "Dm7",    # index + ring
    (0, 1, 0, 0, 1): "D#m7",   # index + pinky
}
# fmt: on

# Ordered list for the chord panel UI
ALL_CHORDS: list[str] = list(dict.fromkeys(SHAPE_MAP.values()))

# ---------------------------------------------------------------------------
# Load chord sounds
# ---------------------------------------------------------------------------
# Map chord names to file names for chords whose filenames differ
FILENAME_MAP: dict[str, str] = {
    "C#": "C#",
    "D#m7": "D#m7",
    "Dm7": "Dm7",
}

loaded_sounds: dict[str, pygame.mixer.Sound] = {}
for chord_name in ALL_CHORDS:
    fname = FILENAME_MAP.get(chord_name, chord_name)
    path = f"sounds/{fname}.mp3"
    try:
        loaded_sounds[chord_name] = pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Warning: Could not load '{path}' — {e}")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_finger_pattern(
    landmarks: list,
    hand_label: str,
) -> tuple[int, ...]:
    """Return a (thumb, index, middle, ring, pinky) extended-finger tuple.

    Each element is 1 if that finger is extended, 0 if curled.
    OpenCV landmarks are in normalised [0, 1] coordinates.
    """
    tips: list[int] = [4, 8, 12, 16, 20]
    pattern: list[int] = []

    # Thumb: horizontal comparison (flipped for each hand)
    if hand_label == "Right":
        pattern.append(1 if landmarks[4].x < landmarks[3].x else 0)
    else:
        pattern.append(1 if landmarks[4].x > landmarks[3].x else 0)

    # Other four fingers: vertical comparison (tip above pip = extended)
    for tip in tips[1:]:
        pattern.append(1 if landmarks[tip].y < landmarks[tip - 2].y else 0)

    return tuple(pattern)


def draw_fixed_fretboard(
    img: NDArray,
    frame_w: int,
    frame_h: int,
    active_chord: str = "None",
    opacity: float = 0.35,
) -> None:
    """Draw a guitar neck in the top-right corner, resolution-aware."""
    neck_w = max(200, frame_w // 4)
    neck_h = max(60, frame_h // 10)
    margin = 20
    start_x = frame_w - neck_w - margin
    start_y = margin

    opacity = max(0.0, min(1.0, opacity))
    overlay = img.copy()

    line_color = (0, 255, 0) if active_chord != "None" else (200, 200, 200)

    # Neck background
    cv2.rectangle(
        overlay,
        (start_x, start_y),
        (start_x + neck_w, start_y + neck_h),
        (40, 40, 40),
        -1,
    )

    # Frets (horizontal lines)
    fret_count = 5
    for i in range(fret_count + 1):
        y = start_y + (i * (neck_h // fret_count))
        cv2.line(overlay, (start_x, y), (start_x + neck_w, y), (150, 150, 150), 2)

    # Strings (vertical lines)
    for i in range(6):
        x = start_x + (i * (neck_w // 5))
        thickness = 1 + (i // 2)
        cv2.line(overlay, (x, start_y), (x, start_y + neck_h), line_color, thickness)

    cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, img)


def draw_chord_panel(
    img: NDArray,
    frame_h: int,
    active_chord: str,
    chords: list[str],
) -> None:
    """Draw a right-side vertical panel listing all chords with active highlight."""
    panel_x = 20
    row_h = 38
    panel_w = 130
    top_y = 100
    panel_bottom = top_y + len(chords) * row_h + 10

    # Panel background
    overlay = img.copy()
    cv2.rectangle(
        overlay,
        (panel_x - 6, top_y - 6),
        (panel_x + panel_w, panel_bottom),
        (15, 15, 15),
        -1,
    )
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)

    cv2.putText(
        img,
        "CHORDS",
        (panel_x, top_y - 14),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (180, 180, 180),
        1,
    )

    for i, chord in enumerate(chords):
        y = top_y + i * row_h + row_h - 8
        if chord == active_chord:
            # Highlight box
            cv2.rectangle(
                img,
                (panel_x - 4, y - row_h + 8),
                (panel_x + panel_w - 2, y + 6),
                (0, 180, 0),
                -1,
            )
            color = (255, 255, 255)
            weight = 2
        else:
            color = (130, 130, 130)
            weight = 1
        cv2.putText(
            img, chord, (panel_x + 4, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, weight
        )


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

cap = cv2.VideoCapture(0)
current_chord_name: str = "None"
last_y: float = 0.5
last_played_time: float = 0.0
cooldown: float = 0.3

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # MediaPipe inference
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = detector.detect_for_video(mp_image, int(time.time() * 1000))

        # --- Draw UI layers ---
        draw_fixed_fretboard(frame, w, h, current_chord_name)

        # Strum line (right half of frame, horizontally centred)
        strum_line_y = h // 2
        cv2.line(frame, (w // 2, strum_line_y), (w, strum_line_y), (0, 220, 0), 2)

        # --- Process hand landmarks ---
        if result.hand_landmarks:
            found_left = False

            for idx, landmarks in enumerate(result.hand_landmarks):
                hand_label = result.handedness[idx][0].category_name

                # LEFT HAND: chord detection
                if hand_label == "Left":
                    found_left = True
                    pattern = get_finger_pattern(landmarks, "Left")
                    current_chord_name = SHAPE_MAP.get(pattern, "None")

                    # Draw landmarks
                    for lm in landmarks:
                        cv2.circle(
                            frame, (int(lm.x * w), int(lm.y * h)), 4, (0, 255, 255), -1
                        )

                # RIGHT HAND: strum detection
                if hand_label == "Right":
                    index_y: float = landmarks[8].y
                    crossed = (last_y < 0.5 and index_y >= 0.5) or (
                        last_y > 0.5 and index_y <= 0.5
                    )
                    if crossed and (time.time() - last_played_time > cooldown):
                        if (
                            current_chord_name != "None"
                            and current_chord_name in loaded_sounds
                        ):
                            loaded_sounds[current_chord_name].play()
                            last_played_time = time.time()
                            # Red flash on strum
                            cv2.line(
                                frame,
                                (w // 2, strum_line_y),
                                (w, strum_line_y),
                                (0, 0, 255),
                                6,
                            )
                    last_y = index_y

            if not found_left:
                current_chord_name = "None"

        # --- Chord name HUD (top-left) ---
        cv2.rectangle(frame, (0, 0), (290, 85), (0, 0, 0), -1)
        cv2.putText(
            frame,
            f"Chord: {current_chord_name}",
            (20, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0) if current_chord_name != "None" else (180, 180, 180),
            2,
        )

        # --- Chord panel ---
        draw_chord_panel(frame, h, current_chord_name, ALL_CHORDS)

        cv2.imshow("Air Guitar", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    detector.close()
    cv2.destroyAllWindows()
    pygame.quit()
