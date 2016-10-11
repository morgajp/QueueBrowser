import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from awsHelpers import QueueManager

import CredDialog

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("SQS Browser")
        self.qm = QueueManager()

        #self.create_menu()

        self.pack(fill=BOTH, expand=1)
        self.create_widgets()
        self.pack_widgets()

    #def create_menu(self):
    #    self.menu = Menu(tearoff=False)
    #    self.master.config(menu=self.menu)
    #    self.file_menu = Menu(self.menu, tearoff=False)
    #    self.menu.add_cascade(label="File", menu=self.file_menu)
    #    self.file_menu.add_command(label="Add Credentials", command=self.addCreds)
    #    self.file_menu.add_command(label="Exit", command=self.exit)

    def pack_widgets(self):
        pass


    def create_widgets(self):
        treeFrame = Frame(self)
        filterFrame = Frame(treeFrame)
        filterLabel = Label(filterFrame, text='QueueFilter')
        filterLabel.pack(side='left', padx=(2,4))
        self.filterInput = Text(filterFrame, height=1)
        self.filterInput.pack(side='left', fill=X)
        self.filterInput.bind("<<Modified>>", self.FilterChanged)
        filterFrame.pack(side='top', fill=X, pady=(0,4))
        self.tree = Treeview(treeFrame)
        self.tree.column("#0", width=600, minwidth=300)
        ysb = Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        self.tree.heading('#0', text='queues', anchor='w')
        for q in self.qm.getQueues():
            qnode = self.tree.insert("", 'end', text="{} - {}".format(q['url'], q['msgCount']))
            self.qm.qmap[qnode] = q
            if int(q['msgCount']) > 0:
                self.tree.insert(qnode, 'end', text='')
       # node1 = self.tree.insert("", 'end', text="test1")
       # nodea = self.tree.insert("", 'end', text="test2")
       # node2 = self.tree.insert(node1, 'end', text="test1")
        self.tree.pack(side="top", fill=BOTH, expand=1)

        self.tree.bind("<<TreeviewSelect>>", self.TreeItemClick)
        self.tree.bind("<<TreeviewOpen>>", self.TreeItemExpand)

        treeFrame.pack(side='left', fill=BOTH, expand=1, padx=4, pady=(2,4))
        
        sendframe = tk.Frame(self)
        sendframe.pack(side='left', fill=tk.BOTH, expand=1, padx=(0,4), pady=(0,4))

        self.details = tk.Text(sendframe, width=60)
        self.details.pack(side="top", fill=tk.BOTH, expand=1)

        buttonFrame = tk.Frame(sendframe)
        buttonFrame.pack(side='top', pady=(4,0))
        self.sendB = tk.Button(buttonFrame, text="Send Msg", command=self.Send)
        self.sendB.pack(side="left")

        self.refreshB = tk.Button(buttonFrame, text='Refresh', command=self.Refresh)
        self.refreshB.pack(side='left')

    def fillMessages(self, node):
        for msg in self.qm.getMessages(self.qm.qmap[node]):
            self.tree.insert(node, 'end', text=msg.body[:128])


    def TreeItemClick(self, par):
        item = self.tree.selection()
        if self.tree.parent(item) != '':
            self.details.delete(1.0, END)
            self.details.insert(END, self.tree.item(item)['text'])

    def TreeItemExpand(self, par):
        self.Refresh()

    def FilterChanged(self, par):
        self.filterInput.edit_modified()
        filterStr = self.filterInput.get('1.0', END).strip()
        for node, queue in self.qm.qmap.items():
            if filterStr in queue['url'] or filterStr == '':
                self.tree.move(node, '', 'end')
            else:
                self.tree.detach(node)
        self.filterInput.edit_modified(False)


    def Refresh(self):
        for selItem in self.tree.selection():
            if selItem in self.qm.qmap:
                self.tree.delete(*self.tree.get_children(selItem))
                self.fillMessages(selItem)
            


    def addCreds(self):
        inputDialog = CredDialog.CredDialog(self)

    def Send(self):
        selItem = self.tree.selection()[0]
        if selItem in self.qm.qmap:
            queue = self.qm.qmap[selItem]
            self.qm.write(queue, self.details.get('1.0', END))


    def exit(self):
        self.say_hi()

    def say_hi(self):
        self.qm.write(self.qm.queues[0], "hi there, everyone!")

root = tk.Tk()
root.geometry("900x580")
app = Application(master=root)
app.mainloop()
