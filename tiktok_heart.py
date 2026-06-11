import time
import random
import pyautogui
import threading
from pynput import keyboard

pyautogui.PAUSE = 0

MIN_INTERVAL = 0.2
MAX_INTERVAL = 0.8
DELAY_START  = 5

running = True

def on_press(key):
    global running
    try:
        # Nhấn F8 để dừng
        if key == keyboard.Key.f8:
            running = False
            return False
    except:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

print(f"Starting in {DELAY_START}s... Click vao VIDEO tren TikTok Live!")
print("Nhan F8 bat cu luc nao de dung.")
for i in range(DELAY_START, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print("Dang tha tim... (F8 de dung)")
start = time.time()
count = 0

while running:
    pyautogui.press('l')
    count += 1
    wait = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
    time.sleep(wait)

elapsed = round(time.time() - start)
print(f"Done! Da tha {count} tim trong {elapsed}s.")
