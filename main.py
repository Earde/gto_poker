import time
import win32gui

from brain import Brain
from handler import Handler

if __name__ == '__main__':
    brain = Brain()
    brain.get_next_actions(bb=14, ante=True)

    handler = Handler()

    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)

    while True:
        games = handler.get_games()
        for g in games:
            for w in winlist:
                if g.table_name in w[1]:
                    print(f"Found table: {w[0]}")
                    g.print()

        time.sleep(2.0)
