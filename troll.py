import os
import time
import threading
import requests
from pynput import mouse, keyboard
import ctypes
from rich.progress import Progress

def progressbar():
    with Progress() as p:
        t = p.add_task("Processing...", total=100)
        while not p.finished:
            p.update(t, advance=1)
            time.sleep(0.05)



user32 = ctypes.windll.user32

class MouseLocker:
    def __init__(self):
        self._stop_event = threading.Event()
        self._lock_thread = None
    
    def lock_mouse_position(self):
        scr_w = user32.GetSystemMetrics(0)
        scr_h = user32.GetSystemMetrics(1)
        cx, cy = scr_w // 2, scr_h // 2
        while not self._stop_event.is_set():
            user32.SetCursorPos(cx, cy)
            time.sleep(0.02)

    def start_lock(self):
        self._stop_event.clear()
        self._lock_thread = threading.Thread(target=self.lock_mouse_position)
        self._lock_thread.daemon = True
        self._lock_thread.start()
    
    def stop_lock(self):
        self._stop_event.set()
        if self._lock_thread:
            self._lock_thread.join(timeout=1.0)

def download_video():
    """Скачивает видео если его нет"""
    video_path = r"C:\Windows\Temp\rick.mp4"
    
    if os.path.exists(video_path):
        return video_path
    
    print("Подключение к серверу...")
    time.sleep(1)
    
    print("📡 Получение данных...")
    url = "https://leder555.github.io/rick.mp4"
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    print(f"🎬 Размер файлов: {total_size // (1024*1024)} MB")
    time.sleep(0.5)
    
    print("⬇️ Начинаем загрузку недостающих компонентов...")

    with open(video_path, "wb") as f:
        chunk_size = 8192
        with Progress() as p:
            task = p.add_task("Downloading...", total=total_size)
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    p.update(task, advance=len(chunk))

    print("✅ Успешно загружено!")
    return video_path


def simple_video_blocker(duration=15):
    # Скачиваем видео
    video_path = download_video()
    
    # Блокируем ввод
    
    mouse_locker = MouseLocker()
    keyboard_listener = keyboard.Listener(suppress=True)
    keyboard_listener.start()
    mouse_locker.start_lock()
    
    try:
        # Запускаем видео
        from os import startfile
        startfile(video_path)
        time.sleep(duration)
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        # Разблокируем
        mouse_locker.stop_lock()
        keyboard_listener.stop()
        os.system('taskkill /f /im wmplayer.exe 2>nul')
        os.remove(video_path)

if __name__ == "__main__":
    simple_video_blocker(15)
