import ctypes
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Union, List, Optional
# from googletrans import Translator
import translators as ts
import time
import pyperclip
from deep_translator import (GoogleTranslator,
                             MicrosoftTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             PapagoTranslator,
                             DeepL,
                             QCRI,
                             single_detection,
                             batch_detection)
import os
import sys

import win32api, win32clipboard, win32con, win32gui

recent_value = ''

def print_pass(message, end = '\n'):
    sys.stdout.write('\x1b[1;32m' + message.strip() + '\x1b[0m' + end)

def strip_and_translate(clip):
    global recent_value
    source = clip.value
    if source == recent_value:
        return
    else:
        recent_value = source
        strip_value = source.replace('-\n', '').replace('\n', '').replace('\r', ' ')
        # google翻译模块，不太想用了
        # translator = Translator()
        # trans = translator.translate(strip_value, src='en', dest='zh-cn')
        # trans = ts.google(strip_value, to_language='zh', if_use_cn_host=True)
        trans = ts.alibaba(strip_value, to_language='zh', professional_field='general')
        print_pass(trans)
        # trans_caiyun = ts.caiyun(strip_value, to_language='zh', professional_field=None)
        # print_pass(trans_caiyun)

        # trans_deepl = ts.deepl(strip_value, to_language='zh', professional_field=None)
        # print_pass(trans_deepl)
       
        # print(help(ts.deepl))
        # print(trans)
        # pyperclip.copy(strip_value)

        # translator = deepl.Translator(os.getenv("DEEPL_AUTH_KEY"))
        # translator = deepl.Translator(os.getenv("DEEPL_AUTH_KEY"))
        # print(os.getenv("DEEPL_AUTH_KEY"))
        # result = translator.translate_text(strip_value, target_lang="zh",use_free_api=True)
        # langs_list = Deepl.get_supported_languages(as_dict=True) 
        translated = GoogleTranslator(source='auto', target='zh-CN').translate(strip_value)
        # translated = DeepL(api_key=os.getenv("DEEPL_AUTH_KEY"), target="zh", use_free_api=True).translate(strip_value)
        print_pass(translated)
        # print(translated)

        # print(translated)


class Clipboard:
    @dataclass
    class Clip:
        type: str
        value: Union[str, List[Path]]

    def __init__(
            self,
            trigger_at_start: bool = False,
            on_text: Callable[[str], None] = None,
            on_update: Callable[[Clip], None] = None,
            on_files: Callable[[str], None] = None,
    ):
        self._trigger_at_start = trigger_at_start
        self._on_update = on_update
        self._on_files = on_files
        self._on_text = on_text

    def _create_window(self) -> int:
        """
        Create a window for listening to messages
        :return: window hwnd
        """
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._process_message
        wc.lpszClassName = self.__class__.__name__
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        return win32gui.CreateWindow(class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)

    def _process_message(self, hwnd: int, msg: int, wparam: int, lparam: int):
        WM_CLIPBOARDUPDATE = 0x031D
        if msg == WM_CLIPBOARDUPDATE:
            self._process_clip()
        return 0

    def _process_clip(self):
        clip = self.read_clipboard()
        if not clip:
            return

        if self._on_update:
            self._on_update(clip)
        if clip.type == 'text' and self._on_text:
            self._on_text(clip.value)
        elif clip.type == 'files' and self._on_text:
            self._on_files(clip.value)
    
    @staticmethod
    def read_clipboard() -> Optional[Clip]:
        try:
            win32clipboard.OpenClipboard()

            def get_formatted(fmt):
                if win32clipboard.IsClipboardFormatAvailable(fmt):
                    return win32clipboard.GetClipboardData(fmt)
                return None

            if files := get_formatted(win32con.CF_HDROP):
                return Clipboard.Clip('files', [Path(f) for f in files])
            elif text := get_formatted(win32con.CF_UNICODETEXT):
                return Clipboard.Clip('text', text)
            elif text_bytes := get_formatted(win32con.CF_TEXT):
                return Clipboard.Clip('text', text_bytes.decode())
            elif bitmap_handle := get_formatted(win32con.CF_BITMAP):
                # TODO: handle screenshots
                pass

            return None
        finally:
            win32clipboard.CloseClipboard()

    def listen(self):
        if self._trigger_at_start:
            self._process_clip()

        def runner():
            hwnd = self._create_window()
            ctypes.windll.user32.AddClipboardFormatListener(hwnd)
            win32gui.PumpMessages()

        th = threading.Thread(target=runner, daemon=True)
        th.start()
        while th.is_alive():
            time.sleep(0.2)
            th.join(0.25)


if __name__ == '__main__':
    clipboard = Clipboard(on_update=strip_and_translate, trigger_at_start=True)
    clipboard.listen()