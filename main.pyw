
# Create a Script to auto-fish in Neverness To Everness
# Outline:
# 1. Obtain screen information from game window
# 2. Monitor Bottom right for indicator fishing button
#   a. IF indicator is present, press F;
#   b. ELSE continue
# 3. Monitor for catch progress bar
#   a. IF progress bar is present, look for moving indicator
#   b. look for current position on bar
#   c. IF indicator is present and to the left of current POS; press A
#   d. IF indicator is present and to the right of current POS; press D
# 4. Repeat
# Note: Monitor for escape sequence to stop script; allow for user input to adjust settings such as keybinds, sensitivity, etc.

import threading
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import font
import numpy as np
import cv2
import time
import pyautogui
import ctypes
import sys
from pynput import keyboard
from mss import MSS as mss
from PIL import Image, ImageTk

global STATUS
STATUS = "Stopped"
global a_count,d_count, f_count;
a_count = 0
d_count = 0
f_count = 0
INTERVAL = 0.01 # 10 ms between checks
YELLOW = "fef7a3"
GRAY = "31dab7"

# Get screen dimensions for capture areas
# Each capture area is defined as a percentage of the screen dimensions to allow for different resolutions
# Base resolution is 2560x1440; capture areas are defined as follows:

with mss() as sct:
        #primary monitor
        monitor = sct.monitors[1]
        global WIDTH, HEIGHT
        WIDTH = int (monitor['width'])
        HEIGHT  = int(monitor['height'])

HOOK_CAPTURE = {
                "top": int(HEIGHT * 1233 / 1440),
                "left": int(WIDTH * 2305 / 2560),
                "width": int(WIDTH * 125 / 2560),
                "height": int(HEIGHT * 125 / 1440)
            }

PROGRESS_CAPTURE = {
                "top": int(HEIGHT * 90 / 1440),
                "left": int(WIDTH * 811 / 2560),
                "width": int(WIDTH * 950 / 2560),
                "height": int(HEIGHT * 17 / 1440)   
            }

def update_status():
    status.config(text=f"Status: {STATUS}")

def update_count():
    count.config(text=f"KEY COUNT\nkeyboard_F: {f_count}\nkeyboard_A: {a_count}\nkeyboard_D: {d_count}")

def start():
    global RUNNING
    RUNNING = True

    global STATUS
    STATUS = "Running"

    # Update Display Counts and Status; Then start program
    update_count()
    update_status()
    threading.Thread(target=main).start()

def stop():
    print("Stopping Auto-Fishing Script...")
    global RUNNING
    RUNNING = False

    global STATUS
    STATUS = "Stopped"

    update_status()

# Set up GUI

# Create Root Window, Frames
root = tk.Tk()
root.title("Auto-Fishing Script")
root.geometry("355x300")

bold_ttlfont = font.Font(family="Calibri", size=14, weight="bold")
bold_stdfont = font.Font(family="Calibri", size=12, weight="bold")
std_font = font.Font(family="Calibri", size=12)

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TLabel",
    background="#1e1e1e",
    foreground="white",
    font=std_font
)

style.configure(
    "TFrame",
    background="#1e1e1e",
    foreground="white",
    font=std_font
)

style.configure(
    "TButton",
    background="#333333",
    foreground="white",
    font=std_font,
)


top_frame = ttk.Frame(root, padding=10)
top_frame.pack(fill=tk.X)

middle_frame = ttk.Frame(root, padding=10)
middle_frame.pack(fill=tk.X)

bottom_frame = ttk.Frame(root, padding=10)
bottom_frame.pack(fill=tk.BOTH, expand=True)

#Creat Buttons, Labels, Console
start_button = ttk.Button(top_frame, text="Start", command=start)
stop_button = ttk.Button(top_frame, text="Stop", command=stop)
Title = ttk.Label(top_frame, text="Auto Fishing", font=bold_ttlfont)

pic = Image.open("assets/Rice.jpg")
pic = pic.resize((50, 50))
tk_pic = ImageTk.PhotoImage(pic)

rice_label = ttk.Label(middle_frame, image=tk_pic)
rice_label.image = tk_pic
rice_label.grid(row=0, column=1, padx=5)

start_button.grid(row=0, column=1, padx=5)
stop_button.grid(row=0, column=2, padx=5)
Title.grid(row=0, column=0, padx=5)


count = ttk.Label(middle_frame, text=f"KEY COUNT\nkeyboard_F: {0}\nkeyboard_A: {0}\nkeyboard_D: {0}", font=std_font)
count.grid(row=0, column=2, padx=5)

status = ttk.Label(middle_frame, text=f"Status: {STATUS}", font=std_font)
status.grid(row=0, column=0, padx=5)

console = scrolledtext.ScrolledText(
    bottom_frame, 
    state='disabled', 
    width=100, 
    height=30,
    background="#333333",
    foreground="white",
    )

console.tag_configure('stdout', foreground='white')
console.tag_configure('stderr', foreground='red')
console.pack(fill=tk.BOTH, expand=True)

# Handle Printing to Console
def log(message, fac):
    def write():
        console.config(state='normal')
        console.insert(tk.END, message + '\n', fac)
        console.see(tk.END) # Auto-scroll to the end
        console.config(state='disabled')
    
    root.after(0, write)

class RedirectStdout:
    def write(self, message):
        log(message.strip(), 'stdout')
    
    def flush(self):
        pass

class RedirectStderr:
    def write(self, message):
        log(message.strip(), 'stderr')
    
    def flush(self):
        pass

# Redirect standard output to the console widget
sys.stdout = RedirectStdout()
sys.stderr = RedirectStderr()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def close(a, b, tol=5):
    return all(abs(a[i]-b[i]) <= tol for i in range(3))

def fishHookCheck():
    target_color = "FFFFFF" # Checking for White
    target_rgb = hex_to_rgb(target_color)

    with mss() as sct:
        pixel = sct.grab(HOOK_CAPTURE).pixel(75, 67) # Check a specific pixel of capture area
        r, g, b = pixel
        pixel_rgb = (r, g, b)

        if close(pixel_rgb, target_rgb, tol=5):
            return True
    return False

def searchColor( HexColor, Capture, Tolerance):
    target_color = HexColor # Checking for Hex Color in Specific Capture Area
    target_rgb = hex_to_rgb(target_color)

    with mss() as sct:
        
        img = np.array(sct.grab(Capture))
        img = img[:, :, :3][:, :, ::-1] # Convert BGRA to RGB
        
        matches = np.where(
            (np.abs(img[:, :, 0] - target_rgb[0]) <= Tolerance) &
            (np.abs(img[:, :, 1] - target_rgb[1]) <= Tolerance) &
            (np.abs(img[:, :, 2] - target_rgb[2]) <= Tolerance)
        )

        y_coords, x_coords = matches
        pixel_list = list(zip(x_coords, y_coords))
        return pixel_list

def searchYellowBar():
    return searchColor(YELLOW, PROGRESS_CAPTURE, Tolerance=5)

def searchGrayBar():
    return searchColor(GRAY, PROGRESS_CAPTURE, Tolerance=0)

def handleHook():
    global f_count
    f_count += 1
    update_count()
    pyautogui.press('f')

def handleProgress():
    global a_count, d_count

    yellow_pixels = searchYellowBar()
    left_yellow = yellow_pixels[0][0] # Border Pixels
    right_yellow = yellow_pixels[-1][0] # Border Pixels

    gray_pixels = searchGrayBar()
    left_gray = gray_pixels[0][0] + 7 # Pixels from edge
    right_gray = gray_pixels[-1][0] - 7 # Pixels from edge

    if ( right_gray < left_yellow):
        a_count += 1
        update_count()
        pyautogui.keyDown('a')
        time.sleep(0.01) # Hold A for 10ms
        pyautogui.keyUp('a')

    elif ( left_gray > right_yellow):
        d_count += 1
        update_count()
        pyautogui.keyDown('d')
        time.sleep(0.01) # Hold D for 10ms
        pyautogui.keyUp('d')

def main():

    global RUNNING
    print("Starting Auto-Fishing Script; Waiting 5 seconds...")
    time.sleep(5) # Delay to allow user to switch to game window

    next_time = time.perf_counter()

    while RUNNING:
        start = time.perf_counter()
        # IF searchYellowBar() DO handleProgress()
        # ELSE IF fishHookCheck() DO handleHook()
        # ELSE something else

        try:
            if len(searchYellowBar()) > 0:
                handleProgress()
            elif fishHookCheck():
                handleHook()

        except IndexError as e:
            print(f"oopsie, pixel math went wrong somewhere... Don't worry, just ignore it and keep fishing :)")

        # schedule next capture exactly 100ms later
        next_time += INTERVAL
        sleep_time = next_time - time.perf_counter()

        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            # if we're behind, resync
            next_time = time.perf_counter()
            
    cv2.destroyAllWindows()

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()


print("Auto-Fishing Script Initialized. Please click 'Start' to begin.")

root.mainloop()