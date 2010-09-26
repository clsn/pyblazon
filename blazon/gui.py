#!/usr/bin/python
import subprocess
import Tkinter
import sys
import os

class Application(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
    def createWidgets(self):
        self.GO = Tkinter.Button(self)
        self.GO["text"] = "Render blazon"
        self.GO["command"] = self.DisplayShield
        self.GO.pack({"side":"left","anchor":"se"})

        self.Curblazon = Tkinter.StringVar()
        self.BlazonEntry = Tkinter.Entry()
        self.BlazonEntry["textvariable"] = self.Curblazon
        self.BlazonEntry.bind('<Key-Return>', self.OnEnter)
        self.BlazonEntry.pack({"side":"bottom","anchor":"sw"})

        # FIXME: PhotoImage might not be the right widget type.
        # We want a widget that is a rectangle of a specific size,
        # and will draw a bitmap rendering of the vector drawing of
        # the blazon.
        # self.ShieldDisplay = Tkinter.PhotoImage()
        # self.ShieldDisplay.pack({"side":"right"})

    def DisplayShield(self):
        scriptpath = sys.argv[0]
        if not os.path.isabs(scriptpath):
            # A bit hacky, yes, but that's why 
            # we only do it when we have to.
            cwpath = sys.path[0]
        else: # Whenever possible, this way
            cwpath = os.path.dirname(scriptpath)
        gen = subprocess.Popen([sys.executable, os.path.join(
                    cwpath, "gen.py"), self.Curblazon.get()],
                               stdout=subprocess.PIPE,cwd=cwpath)
        rsvg = subprocess.Popen(["/usr/bin/rsvg-view", "--stdin"],
                                stdin=gen.stdout,cwd=cwpath)
        print gen.pid, rsvg.pid >> sys.stderr # Debugging
    def OnEnter(self, event):
        self.DisplayShield()

if __name__ == '__main__':
    root = Tkinter.Tk()
    app = Application(master=root)
    app.mainloop()
