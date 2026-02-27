# 🥁 Vision MIDI Drum Sequencer

An interactive, AI-powered drum sequencer that uses computer vision to map hand movements to MIDI signals. Control your DAW (Ableton, FL Studio, Garageband) by simply pointing at a grid and triggering notes with your keyboard.

## 🌟 Features

- **Hand Tracking:** Real-time index finger tracking via MediaPipe 0.10.14.  
- **BPM Sync:** Moving playhead synced to a customizable BPM.  
- **MIDI Integration:** Sends standard MIDI note data (Kick, Snare, Hi-hat) to any virtual instrument.  
- **Interactive Grid:** 16-step sequencer with 3 tracks.  
- **Toggle Logic:** Add or remove notes by hovering and pressing the 'p' key.  

## 🎨 Visual Preview

![Vision MIDI Drum Sequencer](screenshot.png)

## 🛠️ Requirements

### 1. Python Libraries
You will need Python 3.8+ installed. Install the dependencies using pip:

```bash
pip install opencv-python mediapipe==0.10.14 mido python-rtmidi
````

### 2. Virtual MIDI Routing (Crucial)

Because Python sends MIDI data "out," you need a way for your DAW to "receive" it.

* **Windows:** Download and run loopMIDI. Create a new port named `Python MIDI`.
* **macOS:** Use the built-in IAC Driver (found in Audio MIDI Setup > MIDI Studio).

## 🚀 Getting Started

1. **Open your MIDI Route:** Ensure loopMIDI or IAC Driver is active.
2. **Run the Script:**

```bash
python your_filename.py
```

3. **Configure your DAW:**

   * Open your DAW
   * Go to MIDI Preferences
   * Find the input named `Python MIDI` and turn on Track and Remote
   * Load a Drum Rack or Sampler

## 🎮 Controls

| Action          | Control                                       |
| --------------- | --------------------------------------------- |
| Move Pointer    | Move your index finger in front of the camera |
| Add/Remove Note | Hover over a cell and press the 'p' key       |
| Exit            | Press the 'ESC' key                           |

## ⚙️ Configuration

You can easily adjust the sequencer settings directly in the code:

* **BPM:** Change the playback speed (default is 120).
* **ROWS / COLS:** Change the grid size.
* **MIDI_NOTES:** Change which drum sounds are triggered (default is 36, 38, 42).

### How the BPM Playhead Works

The playhead moves one step at a time according to your BPM:

```
step_duration = 60 / bpm / steps_per_beat
```

* `bpm` = beats per minute of your DAW
* `steps_per_beat` = number of sequencer steps per beat (default 4 for a 16-step loop)
* `step_duration` = seconds each step is displayed

This ensures the green playhead stays perfectly synced with your DAW's tempo.

## 📝 Troubleshooting

* **No MIDI in DAW:** Check that the port name in the code (`mido.open_output('Python MIDI')`) matches the exact name of your virtual MIDI port.
* **Laggy Tracking:** Ensure you are in a well-lit room. MediaPipe performance depends on clear hand visibility.
* **Camera Not Opening:** Ensure no other app (Zoom, Teams, etc.) is using your webcam.
