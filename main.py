"""Launcher for N1 Test System EXE. Starts Flask server and opens browser."""
import sys
import os
import threading
import webbrowser
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app
from seed_questions import seed


def open_browser():
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    # Ensure DB is seeded
    seed()
    # Start browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    # Run Flask
    app.run(host='127.0.0.1', port=5000, debug=False)
