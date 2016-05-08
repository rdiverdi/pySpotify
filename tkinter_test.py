from Tkinter import *
import ttk

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        self.bananaButon = 'banana'
        self.initUI()
    
    def initUI(self):
        w = 600
        h = 500

        self.parent.title("Text?")
        self.style = ttk.Style()
        self.style.theme_use('default')

        frame = Frame(self, relief=RAISED, borderwidth=1)
        frame.pack(fill=BOTH, expand=1)

        self.pack(fill=BOTH, expand=1)
        self.centerWindow(w, h)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, pad=7)
        frame.rowconfigure(3, weight=1)
        frame.rowconfigure(5, pad=7)

        lbl = Label(frame, text="Windows")
        lbl.grid(sticky=W, pady=4, padx=5)
        
        textbox = Text(frame)
        textbox.grid(row=1, column=0, columnspan=2, rowspan=4, padx=5, sticky=E+W+S+N)


        abtn = Button(frame, text="Activate")
        abtn.grid(row=1, column=3)

        cbtn = Button(frame, text="Close")
        cbtn.grid(row=2, column=3, pady=4)
        
        hbtn = Button(frame, text="Help")
        hbtn.grid(row=5, column=0, padx=5)

        obtn = Button(frame, text="OK")
        obtn.grid(row=5, column=3)


        quitButton = Button(self, text="Quit",
            command=self.quit)
        quitButton.pack(side=RIGHT, padx=5, pady=5)
        self.bananaButton = Button(self, text="banana",
            command=self.banana)
        self.bananaButton.pack(side=RIGHT, padx=5, pady=5)

    def centerWindow(self, w, h):
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def banana(self):
        self.bananaButton.pack(side=LEFT, padx=5, pady=5)

def main():
  
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  