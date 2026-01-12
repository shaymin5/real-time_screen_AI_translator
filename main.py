import tkinter as tk
import logging
from live_screenshot import ScreenshotApp


logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main():
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
