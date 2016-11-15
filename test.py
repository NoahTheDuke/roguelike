import PyBearLibTerminal as terminal

terminal.open()
terminal.printf(2, 1, 'β')
terminal.put(2, 2, 'β')
terminal.refresh()
while True:
    if terminal.has_input():
        key = terminal.read()
        print(key)
        if key == terminal.TK_Q | terminal.TK_KEY_RELEASED:
            print('released')
            break
        elif key == terminal.TK_Q:
            break
terminal.close()
