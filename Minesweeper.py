import time
from tkinter import *
from tkinter import font
import random
import threading
import score
from tkinter import messagebox as mb

mine = '💣'
flag = '🚩'

size = 10
cells = size*size
#winwidth = 450
winwidth = size*45
mineAmount = int(cells/6)
gameIsOn = False

colors = {1: "blue", 2:"green", 3: "red", 4:"darkblue", 5:"darkred", 6:"cyan", 7:"black", 8:"darkgray"}

class Counter(Label):
    def __init__(self, parent, char, field:Grid, col=0, stick="W"):
        super().__init__(parent, bg="darkgray")
        self.grid(row=0, column=col, sticky=stick)
        self.field = field
        self.char = char
        self.upd()
    def upd(self):
        num = 0
        if (self.char == mine):num = mineAmount
        elif (self.char == flag):num = self.field.flags
        self['text'] = f"{self.char}: {num}"

class Timer(Button):
    def __init__(self, parent, field:Grid):
        self.field = field
        self.seconds = 0
        super().__init__(parent, font=f1, width=10, bg="darkgray", command=self.__press)
        self.grid(row=0, column=1, sticky="WE")
        self.on = True
    def __press(self):
        self.field.regenerate()
        self.seconds = -1
        self.addSecond()
        self.on = True
        gameIsOn = True
    def secsToText(self):
        mins = self.seconds//60
        secs = self.seconds%60
        s0 = m0 = '0'
        if (mins>=10):m0=''
        if (secs>=10):s0=''
        return f"{m0}{mins}:{s0}{secs}"
    def addSecond(self):
        self.seconds+=1
        self['text'] = self.secsToText()

class Cell(Button):
    def __init__(self, parent, x, y, field:Grid):
        super().__init__(parent, width=5, height=2, font=f1, command=self.press)
        self.bind('<Button-3>', self.right_click)
        self.contain = ''
        self.flagged = False
        self.grid(column=x, row=y)
        self.x = x
        self.y = y
        self.shown = False
        self.field:Grid = field
    def press(self, btn=''):
        if not self.field.blown:
            self.show()
            if (self.contain == mine): self.field.blowMines()
    def right_click(self, btn=''):
        if not self.shown:
            if not self.flagged and self.field.flags>0:
                self.flagged = True
                self['state'] = 'disabled'
                self['disabledforeground'] = "red"
                self['text'] = flag
                self.field.flags-=1
                self.field.update()
                if self.contain==mine:self.field.correctFlags-=1
            elif self.flagged:
                self.flagged = False
                self['state'] = 'normal'
                self['text'] = ''
                self.field.flags += 1
                if self.contain == mine: self.field.correctFlags += 1
            self.field.update()
        else:
            if self.contain!='':
                sc = Scan(self.x, self.y, self.field)
                if sc.checkFlags(self.contain):
                    sc.showAround()
    def show(self):
        self.shown = True
        self['text'] = self.contain
        self['state'] = 'disabled'
        self['bg'] = 'lightgray'
        try:
            self['disabledforeground'] = colors[self.contain]
        except: self['disabledforeground'] = 'black'
        if (self.contain==''): Scan(self.x, self.y, self.field).showAround()
        if (self.flagged and self.contain==mine): self['text'] = flag
    def blow(self):
        self.show()
        self['bg'] = 'red'

class Grid:
    def __init__(self, size, parent:Frame, root:Tk):
        self.grid = []
        self.parent = parent
        self.size = size
        self.mines = []
        self.blown = False
        self.setFlags()
        self.flagCounter = Counter
        self.root = root
        self.__makeField()
        self.generate()
    def setFlags(self):
        self.flags = mineAmount
        self.correctFlags = mineAmount
    def __makeField(self):
        for x in range(self.size):
            self.grid.append([])
            for y in range(self.size):
                self.grid[x].append(Cell(self.parent, x, y, self))
    def regenerate(self):
        for col in self.grid:
            for cell in col:
                cell.contain=''
                cell.shown = False
                cell.flagged = False
                cell['text'] = ''
                cell['state'] = 'normal'
                cell['bg'] = self.parent.cget("bg")
        self.mines.clear()
        self.generate()
        self.setFlags()
        self.blown = False
        self.update()
    def generate(self):
        def plantMine():
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            if (self.grid[x][y].contain == mine):
                plantMine()
            else:
                self.grid[x][y].contain = mine
                self.mines.append(self[x,y])
        for i in range(mineAmount):
            plantMine()
        for x in range(self.size):
            for y in range(self.size):
                num = Scan(x,y, self).scanMines()
                if (num!=0 and self[x, y].contain!=mine): self[x, y].contain = num
    def update(self):
        self.flagCounter.upd()
        if self.correctFlags==0:
            self.stop()
            self.showOthers()
            mb.showinfo("Перемога!", f"Ви виграли!!! Ваш час: {timer.secsToText()}")
            self.root.withdraw()
            if (score.writeScore(timer.seconds)): self.root.deiconify()
    def stop(self):
        self.blown = True
        gameIsOn = False
        timer.on = False
    def blowMines(self):
        self.stop()
        for mine in self.mines:
            mine.blow()
    def showOthers(self):
        for x in range(size):
            for y in range(size):
                if not self[x, y].shown and self[x, y].contain!=mine:
                    self[x, y].show()
    def __getitem__(self, xy) -> Cell:
        return self.grid[xy[0]][xy[1]]

class Scan: #проверяет область 3x3 вокруг центра x y
    def __init__(self, x, y, field:Grid):
        self.field = field
        self.zone = []
        self.x = x
        self.y = y
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i==0 and j==0) or (self.x==0 and i==-1) or (self.y==0 and j==-1): pass
                else: self.__getCell(i, j)
    def __getCell(self, x, y):
        try:
            self.zone.append(self.field[x+self.x, y+self.y])
        except:
            pass
    def hasEmpty(self):
        for i in self.zone:
            if (i.contain==''): return True
        return False
    def scanMines(self) -> int:
        mines = 0
        for i in self.zone:
            if i.contain == mine:
                mines+=1
        return mines
    def checkFlags(self, flags:int) -> bool:
        f = 0
        for i in self.zone:
            if i.flagged: f+=1
        if (f>=flags):return True
        return False
    def showAround(self):
        for i in self.zone:
            if (not i.shown and not i.flagged):i.press()

def clock(timer:Timer):
    while True:
        if (timer.on):
            timer.addSecond()
        else: break
        time.sleep(1)

def config():
    global cells, winwidth, mineAmount
    cells = size * size
    mineAmount = int(cells / 6)

def game():
    config()
    def redo():
        global size
        root.quit()
        root.destroy()
        size = 15
        game()
    root = Tk()
    root.title("Сапер")
    #root.geometry(f"{winwidth}x{size*41 + 50}")
    root.resizable(FALSE, FALSE)
    global f1
    f1 = font.Font(family="Arial", size=9, weight="bold")
    gameIsOn = True

    menu = Menu(root)
    root.config(menu=menu)
    menu.add_command(label="HUY", command=redo)

    top = Frame(bg='gray', height=50, width=winwidth)
    top.grid_columnconfigure(tuple(range(3)), weight=1)
    top.grid(row=0, column=0, sticky='NSWE')
    global timer
    field = Frame(width=winwidth)
    field.grid(row=1, column=0)
    grid = Grid(size, field, root)
    timer = Timer(top, grid)
    mineCounter = Counter(top, mine, grid)
    flagCounter = Counter(top, flag, grid, 2, "E")
    grid.flagCounter = flagCounter
    thr = threading.Thread(target=clock, args=(timer,), daemon=True)
    thr.start()

    #grid.showAll()
    root.mainloop()

if __name__ == "__main__":
    game()
