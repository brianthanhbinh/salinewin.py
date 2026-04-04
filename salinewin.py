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

def open_the_chaos():
    webbrowser.open("https://you-are-idiot.github.io/")
    
    time.sleep(2)
    
    width, height = pyautogui.size()
    pyautogui.click(width // 2, height // 2)

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
hdc = user32.GetDC(0)
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)

stop_flag = threading.Event()

def diagonal_screen_warp():
    """Mega Warp: Targets Taskbar and Hides Cursor to prevent 'Cleaning'"""
    user32.ShowCursor(False)
    
    taskbar_hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    taskbar_hdc = user32.GetDC(taskbar_hwnd)

    while not stop_flag.is_set():
        if random.random() > 0.98:
          gdi32.PatBlt(hdc, 0, 0, width, height, 0x00550009)
        gdi32.BitBlt(hdc, 10, 10, width, height, hdc, 0, 0, 0x00CC0020)
        
        gdi32.BitBlt(taskbar_hdc, 0, 0, width, 100, taskbar_hdc, 0, 0, 0x5A0049)

        if random.random() > 0.85:
            rw = random.randint(600, width)
            rh = random.randint(600, height)
            rx = random.randint(0, width - rw)
            ry = random.randint(0, height - rh)
            
            gdi32.BitBlt(hdc, rx, ry, rw, rh, hdc, rx, ry, 0x00EE0086) 
            gdi32.BitBlt(hdc, rx, ry, rw, rh, hdc, rx, ry, 0x5A0049)
            
        time.sleep(0.005)

def scribbling_core():
    """Circular lines that also drift diagonally with the screen"""
    angle = 0
    cx, cy = 100, 100
    while not stop_flag.is_set():
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
    
    blue_brush = gdi32.CreateSolidBrush(0xFF0000)
    gdi32.SelectObject(hdc, blue_brush)

    while not stop_flag.is_set():
        for c in clones:
            gdi32.Rectangle(hdc, int(c['x']), int(c['y']), int(c['x'] + 80), int(c['y'] + 80))
            
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

def spawn_box(title,message):
    root = tk.Tk()
    root.withdraw()
    
    popup = tk.Toplevel(root)
    popup.title("1x1x1")
    
    x = random.randint(0, width - 250)
    y = random.randint(0, height - 150)
    popup.geometry(f"250x150+{x}+{y}")
    
    content = tk.Frame(popup, padx=10, pady=10)
    content.pack()
    tk.Label(content, bitmap="info").pack(side="left", padx=5)
    tk.Label(content, text="I'm here.").pack(side="left")

    def on_close():
        for _ in range(2):
            threading.Thread(target=spawn_box, args=("1x1x1x1", "I'm here."), daemon=True).start()
        root.destroy()

    tk.Button(popup, text="OK", command=on_close, width=10).pack(pady=5)
    popup.protocol("WM_DELETE_WINDOW", on_close)
    
    root.mainloop()

def fourx():
    for _ in range(15):
        threading.Thread(target=spawn_box, args=("1x1x1x1", "I'm here."), daemon=True).start()
        time.sleep(0.01)

def audio_engine():
    if not os.path.exists("audio.mp3"): return
    while not stop_flag.is_set():
        try: playsound("audio.mp3")
        except: break

def on_esc():
    """Clean up and bring back the cursor"""
    stop_flag.set()
    user32.ShowCursor(True)
    user32.InvalidateRect(0, 0, 1)
    os.system("taskkill /F /IM msedge.exe /T")
    print("\n[!] Restoring System...")
    os._exit(0)
    
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    
    if messagebox.askyesno("DIAGONAL DESTRUCTION", "Start the Diagonal Melt?\n\nPress ESC to stop."):
        keyboard.add_hotkey('esc', on_esc)
        
        threading.Thread(target=audio_engine, daemon=True).start()
        threading.Thread(target=diagonal_screen_warp, daemon=True).start()
        threading.Thread(target=scribbling_core, daemon=True).start()
        threading.Thread(target=blue_square_clones, daemon=True).start()
        threading.Thread(target=icon_spam_trail, daemon=True).start()
        gdi32.BitBlt(hdc, 5, 5, width, height, hdc, 0, 0, 0x00EE0086)
        open_the_chaos()
        fourx()

        keyboard.wait('esc')
        on_esc()
    else:
        sys.exit()
