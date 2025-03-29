import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print("\nتغییرات تشخیص داده شد! در حال ریستارت...")
            subprocess.run(["pkill", "-f", "streamlit"])  # پایان فرآیند قبلی
            subprocess.Popen(["streamlit", "run", "app.py"])  # اجرای مجدد

if __name__ == "__main__":
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
