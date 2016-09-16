import tkinter as tk
from tkinter import *
from tkinter import ttk

class CredDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        self.parent = parent

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()


        self.wait_window(self)

    def body(self, master):
        self.myLabel = tk.Label(master, text='Enter your credentials below')
        self.myLabel.pack()
        self.myEntryBox = tk.Entry(master)
        self.myEntryBox.pack()
        self.mySubmitButton = tk.Button(master, text='Submit', command=self.send)
        self.mySubmitButton.pack()

    def send(self):
        self.username = self.myEntryBox.get()
        self.top.destroy()

    def ok(self, event=None):
        self.cancel()

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

