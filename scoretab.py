from tkinter import *
import json
import score

difs = {"Легкий":6, "Нормальний":10, "Складний":15, "Екстрим":20}
opts = list(difs.keys())

class Labels:
    def __init__(self, root:Tk, amount = 10):
        self.root = root
        self.labs = []
        for i in range(0, amount):
            self.labs.append(Label(root, anchor="w", font=("Arial", 12)))
            self.labs[i].pack(fill='both')
    def __setitem__(self, key, value:str):
        self.labs[key]['text'] = value

def scores():
    def quit_tk():
        root.quit()
        root.destroy()
    def choice(*args):
        try:
            d = data[str(difs[chose.get()])]
            d = dict(sorted(d.items(), key=lambda item: item[1]))
        except:
            d = {}
        i = 0
        for x in d:
            labs[i] = f"{i + 1}. {score.secsToText(d[x])} - {x}"
            i+=1
            if i==10:break
        while i<10:
            labs[i] = f"{i + 1}. {score.secsToText(3960)} - Anon"
            i+=1
    try:
        data = json.loads(open(score.path, 'r').read())
    except:
        data = {}
    root = Tk()
    root.resizable(FALSE, FALSE)
    root.title("Найкращі часи")
    root.geometry("300x300")
    chose = StringVar(root)
    drop = OptionMenu(root, chose, *opts)
    drop.pack()
    labs = Labels(root)
    chose.trace("w", choice)
    chose.set(opts[0])
    root.protocol("WM_DELETE_WINDOW", quit_tk)
    root.mainloop()
    return True

if __name__=="__main__":
    scores()