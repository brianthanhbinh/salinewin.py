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
from playsound import playsound

# --- Setup GDI ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
hdc = user32.GetDC(0)
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)

stop_flag = threading.Event()

def diagonal_screen_warp():
    """Mega Warp: Targets Taskbar and Hides Cursor to prevent 'Cleaning'"""
    # 1. Hide the cursor (Windows API)
    user32.ShowCursor(False)
    
    # 2. Find the Taskbar Handle so we can draw over it specifically
    taskbar_hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    taskbar_hdc = user32.GetDC(taskbar_hwnd)

    while not stop_flag.is_set():
        if random.random() > 0.98:
          # 0x00550009 is a DNA-level inversion (DSTINVERT)
          gdi32.PatBlt(hdc, 0, 0, width, height, 0x00550009)
        # THE DRIFT (Entire Screen)
        gdi32.BitBlt(hdc, 10, 10, width, height, hdc, 0, 0, 0x00CC0020)
        
        # THE TASKBAR KILLER (Forces the taskbar to warp too)
        # 0x5A0049 (Invert) draws directly onto the taskbar's memory
        gdi32.BitBlt(taskbar_hdc, 0, 0, width, 100, taskbar_hdc, 0, 0, 0x5A0049)

        # THE MEGA CHUNKS (Permanent/Non-Cleaning)
        if random.random() > 0.85:
            rw = random.randint(600, width)
            rh = random.randint(600, height)
            rx = random.randint(0, width - rw)
            ry = random.randint(0, height - rh)
            
            # Use SRCPAINT (0x00EE0086) to 'smear' the pixels so they stick
            gdi32.BitBlt(hdc, rx, ry, rw, rh, hdc, rx, ry, 0x00EE0086) 
            gdi32.BitBlt(hdc, rx, ry, rw, rh, hdc, rx, ry, 0x5A0049)
            
        time.sleep(0.005) # Extreme speed to beat the Windows Refresh

def scribbling_core():
    """Circular lines that also drift diagonally with the screen"""
    angle = 0
    # Start at top-left
    cx, cy = 100, 100
    while not stop_flag.is_set():
        # Move the center of the circle diagonally
        cx = (cx + 5) % width
        cy = (cy + 5) % height
        
        color = random.randint(0, 0xFFFFFF)
        pen = gdi32.CreatePen(0, 4, color)
        gdi32.SelectObject(hdc, pen)

        radius = 100 + 30 * math.sin(angle * 0.5)
        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))
        
        if angle == 0:
            gdi32.MoveToEx(hdc, x, y, None)
        else:
            gdi32.LineTo(hdc, x, y)

        gdi32.DeleteObject(pen)
        angle += 0.3
        time.sleep(0.005)

def blue_square_clones():
    """6 Blue squares that move in the SAME diagonal direction"""
    time.sleep(2)
    clones = [{'x': random.randint(0, width), 'y': random.randint(0, height)} for _ in range(6)]
    
    blue_brush = gdi32.CreateSolidBrush(0xFF0000) # Blue
    gdi32.SelectObject(hdc, blue_brush)

    while not stop_flag.is_set():
        for c in clones:
            # Draw the trail
            gdi32.Rectangle(hdc, int(c['x']), int(c['y']), int(c['x'] + 80), int(c['y'] + 80))
            
            # Constant diagonal movement
            c['x'] = (c['x'] + 15) % width
            c['y'] = (c['y'] + 15) % height
            
        time.sleep(0.01)

def icon_spam_trail():
    icons = [32513, 32514, 32515, 32516]
    while not stop_flag.is_set():
        point = (ctypes.c_long * 2)()
        user32.GetCursorPos(ctypes.byref(point))
        hIcon = user32.LoadIconW(0, icons[random.randint(0, 3)])
        user32.DrawIcon(hdc, point[0] - 16, point[1] - 16, hIcon)
        time.sleep(0.001)

def audio_engine():
    if not os.path.exists("audio.wav"): return
    while not stop_flag.is_set():
        try: playsound("audio.mp3")
        except: break

def on_esc():
    """Clean up and bring back the cursor"""
    stop_flag.set()
    user32.ShowCursor(True) # BRING CURSOR BACK
    user32.InvalidateRect(0, 0, 1) # Refresh screen
    print("\n[!] Restoring System...")
    os._exit(0)
    
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    
    if messagebox.askyesno("Warning", "This is a malware, are you sure running it?\n\nPress ESC to stop."):
        keyboard.add_hotkey('esc', on_esc)
        
        threading.Thread(target=audio_engine, daemon=True).start()
        threading.Thread(target=diagonal_screen_warp, daemon=True).start()
        threading.Thread(target=scribbling_core, daemon=True).start()
        threading.Thread(target=blue_square_clones, daemon=True).start()
        threading.Thread(target=icon_spam_trail, daemon=True).start()
        gdi32.BitBlt(hdc, 5, 5, width, height, hdc, 0, 0, 0x00EE0086)

        keyboard.wait('esc')
        on_esc()
    else:
        sys.exit()
