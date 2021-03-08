import os
import curses
import time
import security

path = "/mnt/c/Users/Djahan/Desktop/coding/python/agenda"
showUI = True

# 0) file manager 1) command line 2) enter date box 3) enter text box 4) preview with file manager 5) password

class note:
    def __init__(this, title):
        this.title = str(title).strip()
        this.id = len(notes)
        this.date = ""
        this.text = ""
        this.isEncrypted = False

notes = [] 
sortedNotes = []
sortState = 0
cursor = [0, 0]
windows = []
command = ""
update = False
showPrev = False
encryptKey = ""

def delOldNotes():
    for f in os.listdir(path + "/notes"):
        os.remove(path + "/notes/" + f)

def saveNotes():
    global notes, encryptKey
    delOldNotes()
    for id, n in enumerate(notes):
        f = None 
        text = ""
        date = ""
        if not n.isEncrypted:
            f = open(f"{path}/notes/#{id} {n.title}.note", "w")
            text = n.text
            date = n.date
        else:
            f = open(f"{path}/notes/#{id} {n.title}.encryptNote", "w")
            text = security.encryptString(encryptKey, n.text)
            date = security.encryptString(encryptKey, n.date)

        f.write(date + "\n" + text)
        f.close()

def loadNotes():
    global notes, sortedNotes, encryptKey
    notes = []
    indx = 0
    for f in os.listdir(path + "/notes"):
        if f.endswith(".encryptNote") and encryptKey != "":
            name = f.split(" ", 1)
            notes.append(note(name[1][:-5]))
            notes[-1].id = indx
            notes[-1].isEncrypted = True
            entry = open(path + "/notes/" + f, "r").read().split("\n", 1)
            date = security.decryptString(encryptKey, entry[0])
            text = security.decryptString(encryptKey, entry[1])
            notes[-1].date, notes[-1].text = date, text
            indx += 1

        elif f.endswith(".note"):
            name = f.split(" ", 1)
            notes.append(note(name[1][:-5]))
            notes[-1].id = indx
            notes[-1].isEncrypted = False
            entry = open(path + "/notes/" + f, "r").read().split("\n", 1)
            notes[-1].date, notes[-1].text = entry[0], entry[1]
            indx += 1

    sortedNotes = notes

def delNote(name):
    for indx, note in enumerate(notes):
        if name.upper() == note.title.upper():
            del notes[indx]
            return True
    return False

def encryptNote(name):
    for indx, note in enumerate(notes):
        if name.upper() == note.title.upper():
            notes[indx].isEncrypted = True
            return

def sortAZ(notes):
    switched = True
    while switched:
        switched = False
        for i in range(len(notes) - 1):
            switch = False

            if notes[i + 1].date == "" and notes[i].date != "":
                switch = True
            elif notes[i + 1].date != "" and notes[i].date == "":
                switch = False
            elif notes[i + 1].date == "" and notes[i].date == "":
                switch = False
            elif notes[i + 1].date != "" and notes[i].date != "":

                thisDate = notes[i].date.split("/")
                nextDate = notes[i + 1].date.split("/")

                if thisDate[2] > nextDate[2]:
                    switch = True
                elif thisDate[2] < nextDate[2]:
                    switch = False
                elif thisDate[1] > nextDate[1]:
                    switch = True
                elif thisDate[1] < nextDate[1]:
                    switch = False
                elif thisDate[0] > nextDate[0]:
                    switch = True
                elif thisDate[0] < nextDate[0]:
                    switch = False

            cache = notes[i + 1]
            if switch:
                switched = True
                notes[i + 1] = notes[i]
                notes[i] = cache

def sortZA(notes):
    switched = True
    while switched:
        switched = False
        for i in range(len(notes) - 1):
            switch = False

            if notes[i + 1].date == "" and notes[i].date != "":
                switch = False
            elif notes[i + 1].date != "" and notes[i].date == "":
                switch = True
            elif notes[i + 1].date == "" and notes[i].date == "":
                switch = False
            elif notes[i + 1].date != "" and notes[i].date != "":

                thisDate = notes[i].date.split("/")
                nextDate = notes[i + 1].date.split("/")

                if thisDate[2] > nextDate[2]:
                    switch = False
                elif thisDate[2] < nextDate[2]:
                    switch = True
                elif thisDate[1] > nextDate[1]:
                    switch = False
                elif thisDate[1] < nextDate[1]:
                    switch = True
                elif thisDate[0] > nextDate[0]:
                    switch = False
                elif thisDate[0] < nextDate[0]:
                    switch = True

            cache = notes[i + 1]
            if switch:
                switched = True
                notes[i + 1] = notes[i]
                notes[i] = cache


def doesExist(name):
    for note in notes:
        if name.upper() == note.title.upper():
            return True
    return False

def show(w, x, y, text, indx = -1):
    if indx >= 0:
        w.addstr(y, x, str(text), curses.color_pair(indx + 1))
    else:
        w.addstr(y, x, str(text))

def output(w, text, indx = -1):
    wH, wW = w.getmaxyx()
    show(w, 1, wH - 2, text, indx)

def shorten(text, maxL):
    maxL -= 2
    if len(text) <= maxL:
        return text
    if maxL - 3 >= 0:
        return text[:maxL - 3] + "..."
    return ""

def showText(w, lines, indx = -1, showCursor = False, col = 0):
    for indx, line in enumerate(lines):
        show(w, 2, 1 + indx, line, col)
    if showCursor:show(w, 2 + len(lines[-1]), len(lines), " ", 3)

def initCol():
    # 1) white 2) red 3) grey 4) cursor
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, 244, -1)
    curses.init_pair(4, -1, curses.COLOR_RED)

scroll = 0
selected = 0

def showList(w, x, y, arr):
    global cursor, scroll, selected, showPrev, sortedNotes

    wH, wW = w.getmaxyx()

    selected += cursor[1]
    cursor[1] = 0

    if selected < 0:
        selected = 0
    if selected >= len(arr):
        selected = len(arr) - 1

    if selected > wH - 3 + scroll:
        scroll += 1

    if selected < scroll:
        scroll -= 1

    if sortedNotes[scroll + selected].text != "":
        showPrev = True
    else:showPrev = False


    for indx in range(scroll, len(arr)):
        if indx - scroll < wH - 2:
            text = arr[indx].title
            text = text.upper()
            if (wW > 20):show(w, x + 2, indx + y + 1 - scroll, shorten(text, wW - 11), indx == selected)
            else:show(w, x + 2, indx + y + 1 - scroll, shorten(text, wW - 1), indx == selected)
            if (wW > 20):show(w, wW - 10, indx + y + 1 - scroll, arr[indx].date, 2)

enteringPass = False
encryptFile = ""
def enterCommand(w, command):
    global selectedWin, sortedNotes, enteringPass, encryptFile

    if enteringPass:
        global encryptKey
        encryptKey = security.generateKey(command)
        if not security.verifyKey(encryptKey):
            encryptKey = ""
            output(w, "wrong password!", 1)
            selectedWin = 0
        else:
            output(w, encryptKey, 2)
            encryptNote(encryptFile)
            selectedWin = 0
        enteringPass = False
        return



    if command[:1] ==":":
        c = command[1:].strip().split(" ", 1)

        if c[0] == "q"  or c[0] == "wq":
            saveNotes()
            exit()

        elif c[0] == "rm" and len(c) > 1:
            if delNote(c[1]): output(w, f"'{c[1]}' deleted", 2)
            else:output(w, f"'{c[1]}' not found", 1)
            selectedWin = 0

        elif c[0] == "sort" and c[1] == "az":
            sortAZ(sortedNotes)
            selectedWin = 0
            update = True

        elif c[0] == "sort" and c[1] == "za":
            sortZA(sortedNotes)
            selectedWin = 0
            update = True

        elif c[0] == "encrypt" and len(c) > 1:
            output(w, "enter Password", 2)
            enteringPass = True
            encryptFile = c[1]

        elif c[0] == "w" and len(c) == 1:
            saveNotes()
            output(w, " notes saved", 2)
            selectedWin = 0
            update = True

        elif c[0] == "e" and len(c) > 1:
            #if doesExist(c[1]):
            #    output(w, f"'{c[1]}' already exists", 1)
            #else:
                notes.append(note(c[1]))
                selectedWin = 2
                update = True
        else:
            output(w, "Command not found: " + c[0], 1)
            selectedWin = 0

def enterChr(w, char):
    global command, selectedWin
    if char != 10 and char != 263 and char != 27:
        command += chr(char)
        output(w, command)
    elif char == 263:
        if len(command) > 0:
            command = command[:-1]
            output(w, command)
        else:
            selectedWin = 0
            command = ""
    elif char == 27:
        selectedWin = 0
        command = ""
    elif char == 10:
        enterCommand(w, command)
        command = ""

def enterPass(w, key):
    global command, encryptKey
    if key == 0:return False

    if key != 10 and key != 263 and key != 27:command += chr(key)

    if key == 263:command = command[:-1]

    if key == 10:
        encryptKey = security.generateKey(command)
        command = ""
        return security.verifyKey(encryptKey)

    fakePass = ""
    for i in range(len(command)): fakePass += "*"

    output(w, fakePass)
    return False
    

normalMode = False
def enterText(w, key):
    global command, selectedWin, update, normalMode
    if key == 0:return

    if not normalMode:
        if key != 10 and key != 263 and key != 27:command += chr(key)

        if key == 263:command = command[:-1]
        if key == 10:command += " \n "
        if key == 27:
            normalMode = True

    else:
        if key == 105:
            normalMode = False
        if key == 10:
            normalMode = False
            selectedWin = 0
            update = True
            notes[-1].text = command
            command = ""
            return

    #if key == 27:
    #    selectedWin = 0
    #    command = ""
    #    update = True
    #    return

    wH, wW = w.getmaxyx()
    lines = [""]
    words = command

    counter = 0
    letterCount = 0
    for s in words:
        if s != " ": counter += 1
        else: counter = 0

        if counter >= wW - 3:
            words = words[:letterCount] + " "  + words[letterCount:]
            letterCount += 1
            counter = 1

        letterCount += 1



    words = words.split(" ")

    scroll = 0
    for word in words:
        if len(lines[-1] + word) < wW - 3 and word != "\n":
            lines[-1] += word + " "
        else:
            if word == "\n":
                lines.append("")
            else:
                lines.append("")
                lines[-1] += word + " "

        if len(lines) > wH - 2 + scroll:
            scroll += 1

    for i in range(scroll):
        del lines[0]

    lines[-1] = lines[-1][:-1]
    showText(w, lines, 0, True)

def displayText(w, text):
    wH, wW = w.getmaxyx()
    lines = [""]
    words = text

    counter = 0
    letterCount = 0
    for s in words:
        if s != " ": counter += 1
        else: counter = 0

        if counter >= wW - 3:
            words = words[:letterCount] + " "  + words[letterCount:]
            letterCount += 1
            counter = 1

        letterCount += 1

    words = words.split(" ")

    for word in words:
        if len(lines[-1] + word) < wW - 3 and word != "\n":
            lines[-1] += word + " "
        else:
            if word == "\n":
                lines.append("")
            else:
                lines.append("")
                lines[-1] += word + " "

    lines[-1] = lines[-1][:-1]
    showText(w, lines, 2, False, 2)

def enterDate(w, key):
    global command, selectedWin, update
    date = "DD/MM/JJ"

    if key >= 48 and key < 58:
        command += chr(key)
    if len(command) > len(date):command = command[:-1]

    if key == 263:
        if command[-1:] == "/":
            command = command[:-2]
        else:
            command = command[:-1]

    if len(command) == 0 and key == 10:
        notes[-1].date = ""
        selectedWin = 3
        command = ""
        update = True

    if len(command) == len(date) and key == 10:
        notes[-1].date = command
        selectedWin = 3
        command = ""
        update = True

    if len(command) == 2 or len(command) == 5:command += "/"
    show(w, 1, 1, " " + command, 0)
    show(w, 1 + len(command) + 1, 1, date[len(command):], 2)

def eraseWin():
    for win in windows:
        win.erase()

def refreshWin():
    for win in windows:
        win.refresh()

def moveCursor(key):
    global cursor, selectedWin
    if selectedWin == 0:
        if key == 106:
            cursor[1] = 1
        elif key == 107:
            cursor[1] = -1
        elif key == 58:
            selectedWin = 1

def updateWin():
    global windows, selectedWin, update
    if selectedWin == 0 or selectedWin == 1:

        windows[4].refresh()
        windows[4].erase()

        windows[0].refresh()
        windows[1].refresh()
        windows[0].erase()
        windows[1].erase()

    elif selectedWin == 2:
        windows[0].erase()
        windows[1].erase()
        windows[0].refresh()
        windows[1].refresh()
        windows[2].refresh()
        windows[2].erase()

    elif selectedWin == 3:
        windows[2].refresh()
        windows[2].erase()
        windows[3].refresh()
        windows[3].erase()


def main(main):
    global selectedWin, update, showPrev, notes, sortedNotes
    curses.use_default_colors()
    initCol()
    h, w = main.getmaxyx()
    windows.append(curses.newwin(h - 3, w // 2, 0, 0))
    windows.append(curses.newwin(3, w, h - 3, 0))
    textW = round(w * 0.7)
    windows.append(curses.newwin(3, textW, 0, (w - textW)//2))
    windows.append(curses.newwin(h - 6, textW, 3, (w - textW)//2))
    windows.append(curses.newwin(h - 3, w // 2, 0, w // 2))
    windows.append(curses.newwin(3, w // 2, h // 2, w // 4))

    #key = 0
    #update = True
    #main.refresh()
    #windows[5].box()
    #windows[5].refresh()
    #while True:
    #    if update: update = False
    #    else: key = main.getch()
    #    curses.curs_set(0)
    #    if (enterPass(windows[5], key)): break
    #    windows[5].box()
    #    windows[5].refresh()
    #    windows[5].erase()

    #update = True
    loadNotes()


    selectedWin = 0

    main.refresh()
    if (selectedWin == 0 and len(notes) != 0):showList(windows[selectedWin], 0, 0, sortedNotes)
    windows[selectedWin].box()
    curses.curs_set(0)
    windows[selectedWin].refresh()

    if len(notes) != 0:
        showList(windows[0], 0, 0, sortedNotes)
        displayText(windows[4], sortedNotes[scroll + selected].text)
    windows[0].box()

    while True:
        # 0) file manager 1) command line 2) enter date box 3) enter text box 4) preview with file manager 5) password
        #refreshWin()
        #eraseWin()
        curses.curs_set(0)


        #update
        updateWin()

        if update:
            update = False
        else:
            key = main.getch()
            moveCursor(key)

        #show

        if selectedWin == 0 or selectedWin == 1:
            windows[selectedWin].box()
            if len(notes) != 0:showList(windows[0], 0, 0, sortedNotes)
            if selectedWin == 1:
                enterChr(windows[1], key)
            key = 0

        if selectedWin == 2:
            windows[2].box()
            enterDate(windows[2], key)
            key = 0

        if selectedWin == 3:
            output(windows[2], sortedNotes[-1].date, 2)
            windows[3].box()
            enterText(windows[3], key)

        if showPrev:
            if len(notes) != 0:
                showList(windows[0], 0, 0, sortedNotes)
                displayText(windows[4], sortedNotes[scroll + selected].text)
            windows[0].box()


if (showUI): curses.wrapper(main)
