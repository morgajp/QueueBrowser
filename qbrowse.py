import tkinter as tk
from tkinter import *
from tkinter.ttk import *

import json

from awsHelpers import QueueManager

import CredDialog

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("SQS Browser")
        self.qm = QueueManager()

        self.create_menus()

        self.pack(fill=BOTH, expand=1)
        self.create_layout()
        self.create_widgets()
        self.pack_widgets()

    def create_layout(self):
        self.treeFrame = Frame(self)
        self.filterFrame = Frame(self.treeFrame)
        self.sendFrame = Frame(self)
        self.detailFrame = Frame(self.sendFrame)
        self.buttonFrame = Frame(self.sendFrame)

    def pack_widgets(self):
        self.filterLabel.pack(side='left', padx=(2,4))
        self.filterInput.pack(side='left', fill=X)
        self.filterFrame.pack(side='top', fill=X, pady=(0,4))

        self.tree.pack(side="left", fill=BOTH, expand=1)
        self.treeysb.pack(side="right", fill=Y)
        self.treeFrame.pack(side='left', fill=BOTH, expand=1, padx=4, pady=(2,4))

        self.detailysb.pack(side="right", fill=Y)
        self.details.pack(side="left", fill=BOTH, expand=1)
        self.detailFrame.pack(side='top', fill=Y, expand=1)
        self.sendFrame.pack(side='left', fill=tk.BOTH, expand=1, padx=(0,4), pady=(2,4))

        self.refreshB.pack(side='left')
        self.sendB.pack(side="left")
        self.buttonFrame.pack(side='top', pady=(4,0))

    def create_menus(self):
        self.qmenu = Menu(self.master, tearoff=0)
        self.qmenu.add_command(label='View Messages', command=self.say_hi)
        self.qmenu.add_command(label='Purge', command=self.purge_q)
        self.qmenu.add_command(label='Refresh', command=self.Refresh)

        self.msgmenu = Menu(self.master, tearoff=0)
        self.msgmenu.add_command(label='Delete', command=self.say_hi)

        self.profilemenu = Menu(self.master, tearoff=0)
        self.profilemenu.add_command(label='Add Queue URL', command=self.AddQUrl)


    def create_widgets(self):
        self.filterLabel = Label(self.filterFrame, text='QueueFilter')
        self.filterInput = Text(self.filterFrame, height=1)
        self.filterInput.bind("<<Modified>>", self.FilterChanged)

        self.tree = Treeview(self.treeFrame)
        self.tree.column("#0", width=500, minwidth=300)
        self.treeysb = Scrollbar(self.treeFrame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=self.treeysb.set)
        self.tree.heading('#0', text='queues', anchor='w')
        for s in self.qm.getSessions():
            snode = self.tree.insert("", 'end', text=s, open=True)
            self.qm.sessionNodes[s] = snode

        for q in self.qm.getQueues():
            ownerSession = self.qm.sessionNodes[q['sessionname']]
            qnode = self.tree.insert(ownerSession, 
                    'end', 
                    text="{} - {}".format(q['url'], q['msgCount']))
            self.qm.qmap[qnode] = q
            if int(q['msgCount']) > 0:
                self.tree.insert(qnode, 'end', text='')

        self.tree.bind("<<TreeviewSelect>>", self.TreeItemClick)
        self.tree.bind("<<TreeviewOpen>>", self.TreeItemExpand)

        self.details = tk.Text(self.detailFrame)
        self.detailysb = Scrollbar(self.detailFrame, orient='vertical', command=self.details.yview)
        self.details.configure(yscroll=self.detailysb.set)

        self.sendB = tk.Button(self.buttonFrame, text="Send Msg", command=self.Send)
        self.refreshB = tk.Button(self.buttonFrame, text='Refresh', command=self.Refresh)

        self.tree.bind("<Button-3>", self.popup)

    def fillMessages(self, node):
        for msg in self.qm.getMessages(self.qm.qmap[node]):
            short = msg.body[:120].replace('\n', '\\n')
            msgnode = self.tree.insert(node, 'end', text=short)
            self.qm.msgMap[msgnode] = msg


    def TreeItemClick(self, par):
        item = self.tree.selection()[0]
        if item in self.qm.msgMap:
            self.details.delete(1.0, END)
            msg = self.qm.msgMap[item].body
            try:
                parsedMsg = json.loads(msg)
                msg = json.dumps(parsedMsg, indent=3)
            except:
                pass # Msg not json, just output the text
            self.details.insert(END, msg)

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
                q = self.qm.qmap[selItem]
                self.qm.refresh(q)
                qnode = self.tree.item(selItem, text="{} - {}".format(q['url'], q['msgCount']))
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

    def purge_q(self):
        selItem = self.tree.selection()[0]
        if selItem in self.qm.qmap:
            queue = self.qm.qmap[selItem]
            self.qm.purge(queue)

    def AddQUrl(self):
        newUrl = GetUrlPopup()

        selItem = self.tree.selection()[0]
        if selItem in self.qm.qmap:
            queue = self.qm.qmap[selItem]
            self.qm.addByUrl(queue, newUrl)

    def popup(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item == '':
            return
        self.tree.selection_set(item)
        if item in self.qm.qmap:
            self.qmenu.tk_popup(event.x_root, event.y_root)
        elif item in self.qm.sessionNodes.values():
            self.profilemenu.tk_popup(event.x_root, event.y_root)
        else:
            self.msgmenu.tk_popup(event.x_root, event.y_root)


root = tk.Tk()
root.geometry("980x580")
app = Application(master=root)
app.mainloop()
