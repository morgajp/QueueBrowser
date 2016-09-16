import tkinter as tk
from tkinter import *
from tkinter import ttk
from awsHelpers import QueueManager

import CredDialog

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("SQS Browser")
        self.qm = QueueManager()

        self.create_menu()

        self.pack(fill=BOTH, expand=1)
        self.create_widgets()

    def create_menu(self):
        self.menu = Menu(tearoff=False)
        self.master.config(menu=self.menu)
        self.file_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Add Credentials", command=self.addCreds)
        self.file_menu.add_command(label="Exit", command=self.exit)


    def create_widgets(self):
        self.tree = ttk.Treeview(self)
        self.tree.column("#0", width=600, minwidth=300)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        self.tree.heading('#0', text='queues', anchor='w')
        for q in self.qm.getQueues():
            qnode = self.tree.insert("", 'end', text="{} - {}".format(q['url'], q['msgCount']))
            for msg in self.qm.getMessages(q):
                self.tree.insert(qnode, 'end', text=msg.body[:128])
       # node1 = self.tree.insert("", 'end', text="test1")
       # nodea = self.tree.insert("", 'end', text="test2")
       # node2 = self.tree.insert(node1, 'end', text="test1")
        self.tree.pack(side="left", fill=BOTH, expand=1)

        self.tree.bind("<<TreeviewSelect>>", self.TreeItemClick)

        self.details = tk.Text(self, width=60)
        self.details.pack(side="left", fill=BOTH, expand=1)

        #self.sendB = 

        #self.hi_there = tk.Button(self)
        #self.hi_there["text"] = "Hello World\n(click me)"
        #self.hi_there["command"] = self.say_hi
        #self.hi_there.pack(side="top")

        #self.quit = tk.Button(self, text="QUIT", fg="red",
        #                      command=root.destroy)
        #self.quit.pack(side="bottom")

    def TreeItemClick(self, par):
        item = self.tree.selection()
        print(item)
        print(self.tree.item(item))
        print(self.tree.parent(item))
        self.details.insert(END, self.tree.item(item)['text'])

    def addCreds(self):
        inputDialog = CredDialog.CredDialog(self)

    def exit(self):
        self.say_hi()

    def say_hi(self):
        print("hi there, everyone!")

root = tk.Tk()
root.geometry("900x580")
app = Application(master=root)
app.mainloop()
