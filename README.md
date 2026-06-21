# Air Guitar

Air Guitar is a webcam-based gesture instrument. It uses MediaPipe hand landmarks to detect a left-hand chord shape and a right-hand strum motion, then plays the matching chord sample from the `sounds/` folder.

## Features

- Real-time hand tracking with MediaPipe
- Left-hand chord detection using finger patterns
- Right-hand strum detection across a center-line trigger zone
- On-screen fretboard, chord label, and strum feedback
- Chord sample playback through `pygame`

## Current Chords

The current version of `app.py` supports these chord samples:

- `D.mp3`
- `A.mp3`
- `G.mp3`

If you add more chord mappings in code, place the matching audio files in `sounds/` and update the chord map.

## Requirements

- Python 3.12+
- Webcam
- Speakers or headphones

Python packages:

- `opencv-python`
- `mediapipe`
- `pygame`

## Project Files

- `app.py`: main application
- `hand_landmarker.task`: MediaPipe hand landmark model
- `sounds/`: chord audio samples

## Setup

1. Create a virtual environment:

```bash
python -m venv myenv
```

2. Activate it on Windows PowerShell:

```powershell
.\myenv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Press `q` to quit.

## How It Works

The app processes the camera feed in real time:

1. The left hand is mapped to a chord using the `SHAPE_MAP` finger-pattern dictionary.
2. The right hand triggers a strum when the index finger crosses the horizontal strum line.
3. If a valid chord is active and the cooldown has expired, the matching sound file is played.

## Troubleshooting

- If no sound plays, confirm the matching file exists in `sounds/` and that your system volume is not muted.
- If the hand is not detected, improve lighting and keep both hands fully in frame.
- If chord recognition is inconsistent, keep the left hand steady and aligned with the camera.
- If strums do not trigger, move the right index finger more clearly across the strum line and wait for the cooldown.

## GitHub Upload

To publish this project to GitHub:

```bash
git status
git add app.py README.md requirements.txt .gitignore sounds hand_landmarker.task
git commit -m "Add air guitar app documentation"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

If the remote already exists, skip the `git remote add origin` line and just push.
