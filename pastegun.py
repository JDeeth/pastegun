import win32clipboard
from pynput.keyboard import Key, Listener, HotKey
import pywintypes

class Pastegun:
    """Takes a list of values via the console, puts the first one on the clipboard,
    and puts each next value on the clipboard when Ctrl-V is pressed (in any window)
    
    Usage:

        Pastegun()
    
        Copy / type in list of things you want to paste
        Current item will be shown in window
        Ctrl-V will paste this item and move on to the next
        (Paste with GUI / context menu will not move onto the next item)
        At the end of the list you will be prompted to input another one

    Bugs:
    on_ctrl_v callback function is _not_ called the first time you press Ctrl-V
    after entering the second and subsequent lists. Workaround is to clear the
    clipboard after reloading so at least it's not pasting unexpected data
    """

    def __init__(self):
        self.items = list()
        self.n = 0

        self._load()

        # Set up pynput hotkey
        def for_canonical(f):
            return lambda k: f(listener.canonical(k))
        
        self.ctrl_v = HotKey(HotKey.parse('<ctrl>+v'), self._on_ctrl_v)
       
        with Listener(
            on_press=for_canonical(self.ctrl_v.press),
            on_release=for_canonical(self.ctrl_v.release),
        ) as listener:
            listener.join()

    def _load(self):
        # Receive new values for pasting via console
        print("\nEnter or paste in list of items to paste, one on each line, followed by a blank line.")

        self.items.clear()
        self.n = 0
        
        def receive_input(list_):
            # Append console input line-by-line until blank line is entered
            while True:
                inpt = input()
                if not inpt:
                    return
                list_.append(inpt)

        # Ask for input until input is given
        while not self.items:
            receive_input(self.items)
            if not self.items:
                print("(To exit, press Ctrl-C)")

        # Clear current clipboard value (it will be loaded when Ctrl-V is pressed)
        self._update_clipboard()
        
        # Show next item to be pasted
        self._show_next()

    def _show_next(self):
        # Displays the next item to be pasted along with its position in list
        max_digits = len(f"{len(self.items)}")
        print(f"{self.n+1:{max_digits}}/{len(self.items)}: {self.items[self.n]}")

    def _update_clipboard(self, text=None):
        # Puts next item or specified text onto clipboard
        try:
            win32clipboard.OpenClipboard()
        except pywintypes.error:
            print("\tError: could not update clipboard")
            return
        try:
            win32clipboard.EmptyClipboard()
            if text is not None:
                win32clipboard.SetClipboardText(text)
        finally:
            win32clipboard.CloseClipboard()

    def _on_ctrl_v(self):
        # Put next item onto clipboard
        self._update_clipboard(self.items[self.n])

        # Iterate to next item on list
        self.n += 1
        
        # If end of list is reached, prompt for new list
        if self.n >= len(self.items):
            self._load()
        else:
            self._show_next()

if __name__ == "__main__":
    Pastegun()