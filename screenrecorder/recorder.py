import cv2
import numpy as np
import pyautogui
import threading
import time
import tempfile


class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.thread = None
        self.out = None
        self.region = None  # (x, y, w, h)
        self.temp_video_path = None

    def start(self):
        if self.recording or not self.region:
            return

        x, y, w, h = self.region
        self.recording = True
        # Save to a temp file instead of output.mp4
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        self.temp_video_path = temp.name
        temp.close()
        self.out = cv2.VideoWriter(self.temp_video_path, cv2.VideoWriter_fourcc(*"mp4v"), 30.0, (w, h))
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.recording:
            return
        self.recording = False
        if self.out:
            self.out.release()
            self.out = None
        print(f"Saved to {self.temp_video_path}")

    def _record_loop(self):
        frame_time = 1.0 / 30.0
        x, y, w, h = self.region
        while self.recording:
            start = time.time()
            img = pyautogui.screenshot(region=(x, y, w, h))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            if self.out is None:
                break

            self.out.write(frame)
            elapsed = time.time() - start
            time.sleep(max(0, frame_time - elapsed))
