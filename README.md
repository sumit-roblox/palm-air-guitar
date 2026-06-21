<div align="center">
  <img src="banner.png" alt="Palm Air Guitar Banner" width="100%">
  
  # 🎸 Palm Air Guitar
  
  **Turn your webcam into a virtual instrument using AI and Computer Vision.**
  
  [![Python](https://img.shields.io/badge/Python-3.12-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
  [![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
  [![MediaPipe](https://img.shields.io/badge/MediaPipe-00A67E?style=for-the-badge&logo=google&logoColor=white)](https://google.github.io/mediapipe/)
  [![Pygame](https://img.shields.io/badge/Pygame-F5ED00?style=for-the-badge&logo=python&logoColor=black)](https://www.pygame.org/)

</div>

---

## 🎵 About The Project

Palm Air Guitar is a real-time, gesture-based virtual instrument. Using just your laptop's webcam, the application tracks your hand movements and translates them into musical chords. 

No strings. No picks. Just computer vision and Python.

### ✨ Key Features
- **Real-time Hand Tracking**: Powered by Google's MediaPipe for low-latency detection.
- **Dynamic Chord Selection**: Fretting hand finger patterns are instantly mapped to real guitar chords.
- **Strum Detection**: Moving your strumming hand across the virtual trigger zone plays the sound.
- **HUD Feedback**: A sleek on-screen fretboard and chord panel guide your playing.
- **High-Quality Audio**: Uses Pygame to play real sampled guitar `.mp3` files.

---

## 🛠️ Getting Started

Follow these steps to get your local environment set up.

### Prerequisites
- Python 3.12 or higher
- A working webcam

### Installation

1. **Clone the repository** (or download the files):
   ```bash
   git clone https://github.com/sumit-roblox/palm-air-guitar.git
   cd palm-air-guitar
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\Activate.ps1
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How To Play

Run the application:
```bash
python app.py
```

### The Controls
1. **Left Hand (Fretting):** Hold your left hand up to the camera. The combination of extended vs. curled fingers dictates the chord. (See the on-screen chord panel).
2. **Right Hand (Strumming):** Move your right index finger up or down across the green line in the center of the screen to strum the selected chord.
3. **Exit:** Press `Q` to close the application.

> **💡 Tip**: Keep your hands well-lit and clearly visible in the frame for the best tracking performance!

---

## 🔮 Future Roadmap (Coming Soon!)
- 🤘 **Headbang Strumming:** Trigger chords by headbanging using facial tracking!
- ✋ **Finger-Count Chords:** Simplify chord selection by simply counting the number of fingers you hold up.

---

<div align="center">
  <i>Built with ❤️ using Python</i>
</div>
