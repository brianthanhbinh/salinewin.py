import ctypes
import numpy as np
import time
import threading
import math
import os
import random
import keyboard
import sys
import tkinter as tk
from tkinter import messagebox
import webbrowser
import pyautogui
from playsound import playsound
import qrcode
from PIL import ImageTk, Image
import queue

# --- Global Config ---
is_bsod_active = False
is_paused_by_user = False
stop_flag = threading.Event()
cmd_queue = queue.Queue()

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
hdc = user32.GetDC(0)
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)

# --- Functions ---

def check_escape_combo():
    """The ONLY way to stop the script: Hold ESC and Space together"""
    while not stop_flag.is_set():
        if keyboard.is_pressed('esc') and keyboard.is_pressed('space'):
           """Clean up and bring back the cursor"""
           stop_flag.set()
           user32.ShowCursor(True)
           user32.InvalidateRect(0, 0, 1)
           os.system("taskkill /F /IM msedge.exe /T")
           print("\n[!] Restoring System...")
           os._exit(0)
           time.sleep(10)

def process_queue(root_window):
    """The Main Thread checks this function constantly for new commands"""
    try:
        msg = cmd_queue.get_nowait()
        if msg == "SHOW_BSOD":
            show_bsod(root)
    except queue.Empty:
        pass
    # Check again in 100ms
    root.after(100, lambda: process_queue(root))

def show_bsod(root_window):
    """Actually draws the BSOD. Called by the main thread."""
    global is_bsod_active
    is_bsod_active = True
    
    # Create BSOD as a Toplevel window of the hidden root
    error_win = tk.Toplevel(root_window)
    error_win.attributes("-fullscreen", True, "-topmost", True)
    error_win.config(bg='#0078D7', cursor="none")

    # 1. Text
    tk.Label(error_win, text=":(", font=("Segoe UI", 120), bg='#0078D7', fg='white').place(x=150, y=100)
    main_text = ("Your PC ran into a problem and needs to restart. We're just\n"
                 "collecting some error info, and then we'll restart for you.")
    tk.Label(error_win, text=main_text, font=("Segoe UI", 25), bg='#0078D7', fg='white', justify="left").place(x=150, y=320)
    tk.Label(error_win, text="0% complete", font=("Segoe UI", 25), bg='#0078D7', fg='white').place(x=150, y=420)

    # 2. QR Code (Safe now because we are in the main thread)
    qr = qrcode.QRCode(version=1, box_size=5, border=0)
    qr.add_data("https://www.windows.com/stopcode")
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="#0078D7").resize((120, 120))
    
    # Keep reference to image so it doesn't vanish
    error_win.tk_img = ImageTk.PhotoImage(img) 
    qr_label = tk.Label(error_win, image=error_win.tk_img, bg='#0078D7', borderwidth=0)
    qr_label.place(x=150, y=500)
    
    tk.Label(error_win, text="Stop code: CRITICAL_PROCESS_DIED", font=("Segoe UI", 12), bg='#0078D7', fg='white').place(x=290, y=550)

    def close_bsod():
        global is_bsod_active
        is_bsod_active = False
        error_win.destroy()

    # --- THE FIX ---
    # Instead of error_win.bind, we use a background check
    def monitor_esc():
        while is_bsod_active:
            if keyboard.is_pressed('esc'):
                # Schedule the close on the main thread
                root_window.after(0, close_bsod)
                break
            time.sleep(0.1)

    # Start a tiny thread just to watch for that Esc key
    threading.Thread(target=monitor_esc, daemon=True).start()
# --- Control & Chaos Threads ---

def fake_bsod_timer():
    """Background thread that safely signals the main thread"""
    while not stop_flag.is_set():
        time.sleep(120) 
        if not is_bsod_active and not is_paused_by_user:
            # Instead of calling root.after, we drop a message in the box
            cmd_queue.put("SHOW_BSOD")

def diagonal_screen_warp():
    user32.ShowCursor(False)
    iteration = 0
    while not stop_flag.is_set():
        if is_bsod_active or is_paused_by_user:
            time.sleep(0.1)
            continue
            
        iteration += 1
        gdi32.BitBlt(hdc, 10, 10, width, height, hdc, 0, 0, 0x00CC0020)

        r = int(math.sin(0.05 * iteration) * 127 + 128)
        g = int(math.sin(0.05 * iteration + 2) * 127 + 128)
        b = int(math.sin(0.05 * iteration + 4) * 127 + 128)
        color = (r | (g << 8) | (b << 16))
        
        brush = gdi32.CreateSolidBrush(color)
        gdi32.SelectObject(hdc, brush)
        if iteration % 2 == 0:
            gdi32.PatBlt(hdc, 0, 0, width, height, 0x005A0049)
        gdi32.DeleteObject(brush)

        if iteration % 10 == 0:
            gdi32.PatBlt(hdc, 0, 0, width, height, 0x00550009)
        time.sleep(0.001)

def icon_spam_trail():
    icons = [32513, 32514, 32515, 32516]
    while not stop_flag.is_set():
        if is_bsod_active or is_paused_by_user:
            time.sleep(0.1)
            continue
            
        user32.ShowCursor(False)
        point = (ctypes.c_long * 2)()
        user32.GetCursorPos(ctypes.byref(point))
        
        for _ in range(20):
            hIcon = user32.LoadIconW(0, random.choice(icons))
            user32.DrawIcon(hdc, point[0] + random.randint(-40, 40), 
                            point[1] + random.randint(-40, 40), hIcon)

def blue_square_clones():
    clones = [{'x': random.randint(0, width), 'y': random.randint(0, height)} for _ in range(12)]
    blue_brush = gdi32.CreateSolidBrush(0xFF0000) # Blue in BGR
    gdi32.SelectObject(hdc, blue_brush)

    while not stop_flag.is_set():
        if is_bsod_active or is_paused_by_user:
            time.sleep(0.1)
            continue
        for c in clones:
            gdi32.Rectangle(hdc, int(c['x']), int(c['y']), int(c['x'] + 80), int(c['y'] + 80))
            c['x'] = (c['x'] + 4) % width
            c['y'] = (c['y'] + 4) % height

def scribbling_core():
    angle = 0
    cx, cy = 100, 100
    while not stop_flag.is_set():
        if is_bsod_active or is_paused_by_user:
            time.sleep(0.1)
            continue
        cx = (cx + 5) % width
        cy = (cy + 5) % height
        
        color = random.randint(0, 0xFFFFFF)
        pen = gdi32.CreatePen(0, 10, color)
        gdi32.SelectObject(hdc, pen)

        radius = 100 + 30 * math.sin(angle * 0.5)
        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))
        
        if angle == 0: gdi32.MoveToEx(hdc, x, y, None)
        else: gdi32.LineTo(hdc, x, y)

        gdi32.DeleteObject(pen)
        angle += 1.5

def gittering():
    while not stop_flag.is_set():
        if is_bsod_active or is_paused_by_user:
            time.sleep(0.1)
            continue
        jitter_x = random.randint(-2, 2)
        jitter_y = random.randint(-2, 2)
        gdi32.BitBlt(hdc, 10 + jitter_x, 10 + jitter_y, width, height, hdc, 0, 0, 0x00CC0020)
        time.sleep(0.01)

def spawn_box(title, message):
    if is_bsod_active or is_paused_by_user: return
    root = tk.Tk()
    root.withdraw()
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry(f"250x150+{random.randint(0, width-250)}+{random.randint(0, height-150)}")
    popup.attributes("-topmost", True)
    
    tk.Label(popup, text="I'm here.", font=("Arial", 12)).pack(pady=20)

    def on_close():
        if not is_bsod_active and not is_paused_by_user:
            for _ in range(2):
                threading.Thread(target=spawn_box, args=("1x1x1x1", "I'm here."), daemon=True).start()
        root.destroy()

    tk.Button(popup, text="OK", command=on_close, width=10).pack()
    popup.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

def fourx():
    for _ in range(15):
        if not is_bsod_active:
            threading.Thread(target=spawn_box, args=("1x1x1x1", "I'm here."), daemon=True).start()
        time.sleep(0.1)

def audio_engine():
    if not os.path.exists("audio.mp3"): return
    while not stop_flag.is_set():
        if is_bsod_active or is_paused_by_user:
            time.sleep(0.5)
            continue
        try: playsound("audio.mp3")
        except: break

def on_esc():
    """The ONLY way to stop the script: Hold ESC and Space together"""
    while not stop_flag.is_set():
        if keyboard.is_pressed('esc') and keyboard.is_pressed('space'):
           """Clean up and bring back the cursor"""
           stop_flag.set()
           user32.ShowCursor(True)
           user32.InvalidateRect(0, 0, 1)
           os.system("taskkill /F /IM msedge.exe /T")
           print("\n[!] Restoring System...")
           os._exit(0)
           time.sleep(10)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    
    if messagebox.askyesno("Warning", "Esc+Space to exit, Esc to close bsod"):
        keyboard.add_hotkey('esc', on_esc)
        
        # Launch everything
        process_queue(root)
        threading.Thread(target=audio_engine, daemon=True).start()
        threading.Thread(target=diagonal_screen_warp, daemon=True).start()
        threading.Thread(target=scribbling_core, daemon=True).start()
        threading.Thread(target=blue_square_clones, daemon=True).start()
        threading.Thread(target=icon_spam_trail, daemon=True).start()
        threading.Thread(target=gittering, daemon=True).start()
        threading.Thread(target=check_escape_combo, daemon=True).start()
        threading.Thread(target=fake_bsod_timer, daemon=True).start()
        
        webbrowser.open("https://youareanidiot.cc/safe/")
        fourx()

        root.mainloop()
