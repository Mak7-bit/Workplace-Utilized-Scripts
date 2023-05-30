from tkinter import * 
import sys
sys.path.append("C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Documents\\Python Projects\\scripts\\Automation\\PIOTH\\script_pioth_v12.py")

class App(Frame):
    def run_script(self):
        sys.stdout = self
        ## sys.stderr = self
        try:
            del(sys.modules["script_pioth_v12.py"])
        except:
            ## Yeah, it's a real ugly solution...
            pass
        import script_pioth_v12
        script_pioth_v12.main()
        sys.stdout = sys.__stdout__
        ## sys.stderr = __stderr__

    def build_widgets(self):
        self.text1 = Text(self)
        self.text1.pack(side=TOP)
        self.button = Button(self)
        self.button["text"] = "Trigger script"
        self.button["command"] = self.run_script
        self.button.pack(side=TOP)

    def write(self, txt):
        self.text1.insert(INSERT, txt)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.build_widgets()

root = Tk()
app = App(master = root)
app.mainloop()