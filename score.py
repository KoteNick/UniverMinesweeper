from tkinter import *
from tkinter import messagebox as mb
from tkinter import font
import tempfile
import json

def secsToText(seconds):
    mins = seconds // 60
    secs = seconds % 60
    s0 = m0 = '0'
    if (mins >= 10): m0 = ''
    if (secs >= 10): s0 = ''
    return f"{m0}{mins}:{s0}{secs}"

def writeScore(seconds: int, size: int = 10):
    def quit_tk():
        score.quit()
        score.destroy()
    def on_closing():
        if mb.askokcancel("Вихід", "Ви бажаєте вийти? Ваш рекорд не буде збережено"):
            quit_tk()
    path = f"{tempfile.gettempdir()}/score.txt"
    def write():
        if (var.get().isspace() or var.get()==""):
            mb.showerror("POZOR", "Введіть ім'я!")
            return
        try:
            d = data[str(size)]
        except:
            data[size] = {}
        data[str(size)][var.get()] = seconds
        data['last'] = var.get()
        open(path, 'w').write(json.dumps(data))
        quit_tk()
    try:
        data = json.loads(open(path, 'r').read())
    except:
        data = {}
    score = Tk()
    score.resizable(FALSE, FALSE)
    f1 = font.Font(family="Arial", size=14)
    score.title("Вітаємо!")
    Label(score, text=f"Ваш час: {secsToText(seconds)}\n\nВведіть своє ім'я: ", font=f1).pack()
    var = StringVar(score)
    try:
        var.set(data['last'])
    except: pass
    Entry(score, textvariable= var, width=50, font=f1).pack()
    Button(score, text = "Готово", font=f1, command=write).pack()


    print(data)
    score.protocol("WM_DELETE_WINDOW", on_closing)
    score.mainloop()
    return True

if __name__=="__main__":
    print(tempfile.gettempdir())
    writeScore(5)
