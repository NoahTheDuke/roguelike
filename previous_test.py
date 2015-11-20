import PyBearLibTerminal as terminal
import itertools as it

terminal.open_()
# size = "auto"
size = "12x12"
terminal.set_("window: size=64x36, cellsize={}, title='Omni: menu',"
              "resizeable=true;"
             "font: default".format(size))
terminal.clear()
terminal.refresh()
terminal.color("white")

test = []
proceed = True
while proceed:
    n = terminal.printf(1, 1, "[color=orange]1.[/color] Wide color range: ")
    long_word = "antidisestablishmentarianism."
    long_word_len = len(long_word) - 1
    for i in range(long_word_len):
        factor = i/long_word_len
        red = (1 - factor) * 255
        green = factor * 255
        terminal.color(terminal.color_from_argb(255, int(red), int(green), 0))
        terminal.put(1+n+i, 1, long_word[i])

    terminal.color("white")
    terminal.print_(1, 3,
                    "[color=orange]2.[/color] Backgrounds: "
                    "[color=grey][bkcolor=black] grey [/bkcolor]"
                    "[color=yellow][bkcolor=red] {}".format(" ".join(x for x in test)))

    terminal.print_(1, 5,
                    "[color=orange]3.[/color] Unicode support: "
                    "Кириллица Ελληνικά α=β²±2°")
    terminal.print_(1, 7,
                    "[color=orange]4.[/color] Tile composition: "
                    "a + [color=red]/[/color] = a[+][color=red]/[/color],"
                    "a vs. a[+][color=red]¨[/color]")
    terminal.printf(1, 9, "[color=orange]5.[/color] Box drawing symbols:")
    terminal.print_(5, 11,
                    "   ┌────────┐  \n"
                    "   │!......s└─┐\n"
                    "┌──┘........s.│\n"
                    "│............>│\n"
                    "│...........┌─┘\n"
                    "│<.@..┌─────┘  \n"
                    "└─────┘        \n")

    terminal.refresh()
    key = 0
    while proceed and terminal.has_input():
        key = terminal.read()
        if key == terminal.TK_CLOSE or key == terminal.TK_ESCAPE:
            proceed = False

terminal.close()
