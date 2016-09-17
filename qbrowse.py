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
            qnode = self.tree.insert("", 'end', text="{} - {}".format(q['url'], q['msgCount']), values=q)
            self.fillMessages(qnode, q)
            for msg in self.qm.getMessages(q):
                self.tree.insert(qnode, 'end', text=msg.body[:128])
       # node1 = self.tree.insert("", 'end', text="test1")
       # nodea = self.tree.insert("", 'end', text="test2")
       # node2 = self.tree.insert(node1, 'end', text="test1")
        self.tree.pack(side="left", fill=BOTH, expand=1)

        self.tree.bind("<<TreeviewSelect>>", self.TreeItemClick)

        sendframe = tk.Frame(self)
        sendframe.pack(side='left', fill=tk.BOTH, expand=1)

        self.details = tk.Text(sendframe, width=60)
        self.details.pack(side="top", fill=tk.BOTH, expand=1)

        buttonFrame = tk.Frame(sendframe)
        buttonFrame.pack(side='top')
        self.sendB = tk.Button(buttonFrame, text="Send Msg", command=self.say_hi)
        self.sendB.pack(side="left")

        self.refreshB = tk.Button(buttonFrame, text='Refresh', command=self.Refresh)
        self.refreshB.pack(side='left')

        #self.hi_there = tk.Button(self)
        #self.hi_there["text"] = "Hello World\n(click me)"
        #self.hi_there["command"] = self.say_hi
        #self.hi_there.pack(side="top")

        #self.quit = tk.Button(self, text="QUIT", fg="red",
        #                      command=root.destroy)
        #self.quit.pack(side="bottom")

    def fillMessages(self, node, queue):
        for msg in self.qm.getMessages(queue):
            self.tree.insert(node, 'end', text=msg.body[:128])


    def TreeItemClick(self, par):
        item = self.tree.selection()
        self.details.delete(1.0, END)
        self.details.insert(END, self.tree.item(item)['text'])

    def Refresh(self):
        selItem = self.tree.selection()
        selQ = self.qm.queues[self.tree.index(selItem)]

        parent = self.tree.parent(selItem)
        if parent == ''  and 'url' in selQ:
            self.tree.delete(*self.tree.get_children(selItem))
            self.fillMessages(selItem, selQ)
            


    def addCreds(self):
        inputDialog = CredDialog.CredDialog(self)

    def exit(self):
        self.say_hi()

    def say_hi(self):
        self.qm.write(self.qm.queues[0], "hi there, everyone!")

root = tk.Tk()
root.geometry("900x580")
app = Application(master=root)
app.mainloop()
