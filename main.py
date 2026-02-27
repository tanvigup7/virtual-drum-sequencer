import cv2
import mediapipe as mp
import time
import mido

# -------------------
# MIDI SETUP
# -------------------
# If on Windows, ensure loopMIDI is running. On Mac, use IAC Driver.
try:
    # This creates a virtual port. In your DAW, look for "Python MIDI"
    midi_out = mido.open_output('Python MIDI', virtual=True)
except:
    # Fallback for systems that don't support virtual ports (like Windows without loopMIDI)
    midi_out = mido.open_output() 

# MIDI Mapping: 36=Kick, 38=Snare, 42=Hi-hat
MIDI_NOTES = [36, 38, 42]

# -------------------
# GRID & TIMING SETTINGS
# -------------------
ROWS = 3
COLS = 16
BPM = 120
grid_notes = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Animation/Timing state
playhead_x = 0
last_time = time.time()
last_active_col = -1

# -------------------
# MEDIAPIPE SETUP
# -------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

mouse_x, mouse_y = 0, 0

# -------------------
# DRAWING FUNCTIONS
# -------------------
def draw_grid(frame):
    h, w, _ = frame.shape
    cell_w = w // COLS
    cell_h = h // ROWS
    for r in range(ROWS):
        for c in range(COLS):
            x1, y1 = c*cell_w, r*cell_h
            x2, y2 = x1 + cell_w, y1 + cell_h
            # Draw cell borders
            cv2.rectangle(frame, (x1, y1), (x2, y2), (100, 100, 100), 1)
            # Draw active notes
            if grid_notes[r][c]:
                cx, cy = x1 + cell_w//2, y1 + cell_h//2
                cv2.circle(frame, (cx, cy), 12, (0, 0, 255), -1)

def draw_labels(frame):
    h, w, _ = frame.shape
    cell_h = h // ROWS
    labels = ["Kick", "Snare", "Hi-hat"]
    for i, label in enumerate(labels):
        y = i * cell_h + 35
        cv2.putText(frame, label, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"BPM: {BPM}", (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

# -------------------
# MAIN LOOP
# -------------------
def main():
    global mouse_x, mouse_y, playhead_x, last_time, last_active_col
    
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Vision Drum Sequencer", cv2.WINDOW_NORMAL)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        cell_w, cell_h = w // COLS, h // ROWS

        # 1. BPM & PLAYHEAD TIMING
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Pixels to move = (Beats per sec) * (4 steps per beat) * (width of a step)
        pixels_per_second = (BPM / 60) * 4 * cell_w
        playhead_x = (playhead_x + pixels_per_second * delta_time) % w
        
        # 2. MIDI TRIGGER LOGIC
        current_col = int(playhead_x // cell_w)
        if current_col != last_active_col:
            for r in range(ROWS):
                if grid_notes[r][current_col] == 1:
                    midi_out.send(mido.Message('note_on', note=MIDI_NOTES[r], velocity=100))
                    # Note off immediately or after delay if DAW needs it
                    midi_out.send(mido.Message('note_off', note=MIDI_NOTES[r], velocity=0))
            last_active_col = current_col

        # 3. HAND TRACKING
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        key = cv2.waitKey(1) & 0xFF

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Index Finger Tip (Landmark 8)
            mouse_x = int(hand_landmarks.landmark[8].x * w)
            mouse_y = int(hand_landmarks.landmark[8].y * h)

            # Check for 'p' key press
            if key == ord('p'):
                col = min(mouse_x // cell_w, COLS-1)
                row = min(mouse_y // cell_h, ROWS-1)
                # Toggle note (0 to 1, or 1 to 0)
                grid_notes[row][col] = 1 - grid_notes[row][col]

        # 4. DRAWING & OVERLAYS
        # Active column highlight
        overlay = frame.copy()
        cv2.rectangle(overlay, (current_col * cell_w, 0), ((current_col + 1) * cell_w, h), (0, 255, 255), -1)
        cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

        draw_grid(frame)
        draw_labels(frame)

        # Floating yellow cursor at finger tip
        cv2.circle(frame, (mouse_x, mouse_y), 10, (0, 255, 255), -1)
        
        # Moving Playhead Bar
        cv2.line(frame, (int(playhead_x), 0), (int(playhead_x), h), (255, 255, 255), 2)

        cv2.imshow("Vision Drum Sequencer", frame)
        if key == 27: # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    midi_out.close()

if __name__=="__main__":
    main()