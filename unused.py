import time
import sys
import os
sys.path.append(os.path.abspath("SO_site-packages"))

import pyperclip

def translate(context):

def print_to_stdout(clipboard_content):
    print("")

def ClipboardWatcher(threading.Thread):
    def __init__(self, callback, pause=1):
        super(ClipboardWatcher, self).__init__()
        self._callback = callback
        self._pause = pause
        self._stopping = False

    def run(self):       
        recent_value = ""
        while not self._stopping:
            tmp_value = pyperclip.paste()

            if tmp_value != recent_value:
                recent_value = tmp_value
                strip_value = "\r\n".join([i.text.replace('\n', ' ') for i in recent_value])
                translate_vlaue = translate(strip_value) 
                self._callback(recent_value)

            time.sleep(self._pause)

    def stop(self):
        self._stopping = True

def main():
    watcher = ClipboardWatcher(print_to_stdout, 5.)
    watcher.start()
    while True:
        try:
            print("Waiting for changed clipboard...")
            time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop()
            break

if __main__ == '__main__':
    main()



