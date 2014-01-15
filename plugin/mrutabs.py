from collections import namedtuple

KeyboardEvent = namedtuple('KeyboardEvent', ['event_type', 'key_code',
                                             'scan_code', 'alt_pressed',
                                             'time'])

handlers = []

def listen():
    """
    Calls `handlers` for each keyboard event received. This is a blocking call.
    """
    # Adapted from http://www.hackerthreads.org/Topic-42395
    from ctypes import windll, CFUNCTYPE, POINTER, c_int, c_void_p, byref
    import win32con, win32api, win32gui, atexit

    event_types = {win32con.WM_KEYDOWN: 'key down',
                   win32con.WM_KEYUP: 'key up',
                   0x104: 'key down', # WM_SYSKEYDOWN, used for Alt key.
                   0x105: 'key up', # WM_SYSKEYUP, used for Alt key.
                  }

    def low_level_handler(nCode, wParam, lParam):
        """
        Processes a low level Windows keyboard event.
        """
        event = KeyboardEvent(event_types[wParam], lParam[0], lParam[1],
                              lParam[2] == 32, lParam[3])
        if event.event_type == 'key up' and event.key_code == 162:
            for handler in handlers:
                handler(event)

        # Be a good neighbor and call the next hook.
        return windll.user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    # Our low level handler signature.
    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    # Convert the Python handler into C pointer.
    pointer = CMPFUNC(low_level_handler)

    # Hook both key up and key down events for common keys (non-system).
    hook_id = windll.user32.SetWindowsHookExA(win32con.WH_KEYBOARD_LL, pointer,
                                             win32api.GetModuleHandle(None), 0)

    # Register to remove the hook when the interpreter exits. Unfortunately a
    # try/finally block doesn't seem to work here.
    atexit.register(windll.user32.UnhookWindowsHookEx, hook_id)

    while True:
        msg = win32gui.GetMessage(None, 0, 0)
        win32gui.TranslateMessage(byref(msg))
        win32gui.DispatchMessage(byref(msg))

import vim;
mru = []
changingTabs = False

def mrutabs_onLeavingTab():
    a = 4

def mrutabs_onEnteredTab():
    tab = vim.current.tabpage
    # Is this a new tab?
    if not changingTabs:
        if tab in mru:
            mru.remove(tab)
        mru.insert(0, tab)

def removeInvalidTabs():
    mru = filter(lambda t: t.valid, mru)

def mrutabs_nextTab():
    global changingTabs
    changingTabs = True
    tab = vim.current.tabpage

    # Go to the next valid tab
    removeInvalidTabs()
    vim.current.tabpage = mru[(mru.index(tab) + 1) % len(mru)]
    vim.command("redraw!");

def mrutabs_prevTab():
    global changingTabs
    changingTabs = True
    tab = vim.current.tabpage

    # Go to the prev valid tab
    removeInvalidTabs()
    index = (mru.index(tab) - 1)
    vim.current.tabpage = mru[index if index >= 0 else len(mru) - 1]
    vim.command("redraw!");

if __name__ == '__main__':
    def print_event(e):
        #print e
        #vim.current.tabpage = vim.tabpages[1]
        global changingTabs
        changingTabs = False
        mrutabs_onEnteredTab()
        #print("Setting tabpage")

    for i in vim.tabpages:
        mru.append(i)
    handlers.append(print_event)
    listen()

