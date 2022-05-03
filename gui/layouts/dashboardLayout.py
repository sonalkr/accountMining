from datetime import datetime
from itertools import chain
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showerror, showinfo

from db import getDgReadOnly
from gui.baseApp import BaseApp
from gui.layouts.baseLayout import BaseLayout
from services.accountRefreshService import AccountRefreshService
from services.dashboardService import DashboardService
from services.util import blankCurrencyFormat, getListOfAgentName, zeroCurrencyFormat


class DashboardLayout(BaseLayout):
    def __init__(self, rootApp: BaseApp, root: ttk.Frame) -> None:
        self.dashboardService = DashboardService()
        self.root = root
        self.rootApp = rootApp
        self.accountRefreshService = AccountRefreshService()

    def _destory(self):
        for child in self.root.winfo_children():
            child.destroy()

    def _getToolBar(self):
        toolbar = tk.Frame(self.sheet_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        b1 = tk.Button(
            toolbar,
            relief=tk.FLAT,
            compound=tk.LEFT,
            text="Update",
            command=self._createUpdateFrame,
            # image=imgs["notepad"]
        )
        b1.pack(side=tk.LEFT, padx=0, pady=0)

        b2 = tk.Button(
            toolbar,
            text="Delete",
            compound=tk.LEFT,
            command=self._deleteRecord,
            relief=tk.FLAT,
            # image=imgs["github"]
        )
        b2.pack(side=tk.LEFT, padx=0, pady=0)

        b3 = tk.Button(
            toolbar,
            text="Create",
            compound=tk.LEFT,
            command=self._createCreateFrame,
            relief=tk.FLAT,
            # image=imgs["github"]
        )
        b3.pack(side=tk.LEFT, padx=0, pady=0)

        b4 = tk.Button(
            toolbar,
            text="Refresh",
            compound=tk.LEFT,
            command=self._accountRefresh,
            relief=tk.FLAT,
            # image=imgs["github"]
        )
        b4.pack(side=tk.LEFT, padx=0, pady=0)

    def _accountRefresh(self):
        self.accountRefreshService.calculateAll()
        self.rootApp.updateAllLayout()

    def getFrame(self):
        con = getDgReadOnly()
        db = con.cursor()
        db.execute("""SELECT account.id, lookup_id, account_name, op_cash, op_bank, _op_total, _cash_sale, _bank_sale, _cash_received, _bank_received, _cl_cash, _cl_bank, _cl_total, agent_name FROM account
        CROSS JOIN agent WHERE account.id_agent = agent.id
        ORDER BY account_name ASC""")
        rows = db.fetchall()
        con.close()
        head_columns = ("id", "lookup_id", "account_name", "op_cash", "op_bank", "_op_total", "_cash_sale",
                        "_bank_sale", "_cash_received", "_bank_received", "_cl_cash", "_cl_bank", "_cl_total", "agent_name")

        self.sheet_frame = tk.Frame(self.root)
        self.sheet_frame.pack(expand=1, fill="both")

        self._getToolBar()

        if not len(rows):
            # ttk.Label(self.root, text="NO Data").pack()
            return self.sheet_frame

        sheet_scroll = tk.Scrollbar(self.sheet_frame)
        sheet_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.sheet = ttk.Treeview(self.sheet_frame, yscrollcommand=sheet_scroll.set,
                                  selectmode="extended", columns=head_columns)
        self.sheet.pack(expand=1, fill="both")

        sheet_scroll.config(command=self.sheet.yview)

        self.sheet.tag_configure('even', background='#dbcced')
        self.sheet.tag_configure('odd', background='#d8edec')
        self.sheet.tag_configure('bottom', background='#80aaff')

        self.sheet.column("#0", width=0, stretch=tk.NO)
        self.sheet.column("id", width=0, stretch=tk.NO)
        self.sheet.column("lookup_id", anchor=tk.E, width=60)
        self.sheet.column("account_name", anchor=tk.W, width=200)
        self.sheet.column("op_cash", anchor=tk.E, width=120)
        self.sheet.column("op_bank", anchor=tk.E, width=120)
        self.sheet.column("_op_total", anchor=tk.E, width=120)
        self.sheet.column("_cash_sale", anchor=tk.E, width=120)
        self.sheet.column("_bank_sale", anchor=tk.E, width=120)
        self.sheet.column("_cash_received", anchor=tk.E, width=120)
        self.sheet.column("_bank_received", anchor=tk.E, width=120)
        self.sheet.column("_cl_cash", anchor=tk.E, width=120)
        self.sheet.column("_cl_bank", anchor=tk.E, width=120)
        self.sheet.column("_cl_total", anchor=tk.E, width=120)
        self.sheet.column("agent_name", anchor=tk.W, width=100)

        self.sheet.heading("lookup_id", text="Look")
        self.sheet.heading("account_name", text="Party")
        self.sheet.heading("op_cash", text="OP Cash")
        self.sheet.heading("op_bank", text="OP Bank")
        self.sheet.heading("_op_total", text="OP Total")
        self.sheet.heading("_cash_sale", text="Cash Sale")
        self.sheet.heading("_bank_sale", text="Bank Sale")
        self.sheet.heading("_cash_received", text="Cash received")
        self.sheet.heading("_bank_received", text="Bank received")
        self.sheet.heading("_cl_cash", text="CL Cash")
        self.sheet.heading("_cl_bank", text="Cl Bank")
        self.sheet.heading("_cl_total", text="CL Total")
        self.sheet.heading("agent_name", text="Agent Name")

        for i, row in enumerate(rows):
            tag = ""
            if i % 2 == 0:
                tag = "even"
            else :
                tag = "odd"
            self.sheet.insert('', tk.END, values=(row[0], row[1], row[2], zeroCurrencyFormat(row[3]), zeroCurrencyFormat(row[4]), zeroCurrencyFormat(row[5]), zeroCurrencyFormat(
                row[6]), zeroCurrencyFormat(row[7]), zeroCurrencyFormat(row[8]), zeroCurrencyFormat(row[9]), zeroCurrencyFormat(row[10]), zeroCurrencyFormat(row[11]), zeroCurrencyFormat(row[12]), row[13]), tags=(tag))
        
        self.sheet.bind("<Double-Button-1>", self._navigateToPartyLedger)

        return self.sheet_frame

    def _navigateToPartyLedger(self,e):
        self._selectRecord()
        self.rootApp.selectPartyTab(account_name=self.__selected_values[2])

    def _selectRecord(self):
        selected = self.sheet.focus()
        self.__selected_values = self.sheet.item(selected, 'values')

    def _createUpdateFrame(self):
        self.rootApp.logger.next(
            time_stamp=datetime.now().strftime("%d-%m-%Y %H:%M"),
            title="info",
            msg="account-update",
            level=1)
        self._selectRecord()
        self.editorFrame = tk.Toplevel()
        self.editorFrame.grab_set()
        self.editorFrame.minsize(300, 300)
        editor_labels = ["lookup_id", "account_name",
                         "op_cash", "op_bank", "agent_name"]
        self.editor_entries = []

        for i, editor_label in enumerate(editor_labels):
            label = tk.Label(self.editorFrame, text=editor_label)
            label.grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(self.editorFrame)
            entry.grid(row=i, column=1, padx=10, pady=10)
            if editor_label == "account_name":
                account_name_list = self.dashboardService.getListOfAccountName()
                account_name_list = list(
                    chain.from_iterable(account_name_list))
                entry = ttk.Combobox(
                    self.editorFrame, values=account_name_list)
                entry.current(account_name_list.index(
                    self.__selected_values[1+i]))
                entry.grid(row=i, column=1, padx=10, pady=10)
            elif editor_label == "agent_name":
                agent_name_list = getListOfAgentName()
                agent_name_list = list(chain.from_iterable(agent_name_list))
                entry = ttk.Combobox(self.editorFrame,  values=agent_name_list)
                print(self.__selected_values[13])
                if self.__selected_values[13]:
                    entry.current(agent_name_list.index(
                        self.__selected_values[13]))
                entry.grid(row=i, column=1, padx=10, pady=10)
            # elif editor_label == "lookup_id":
            #     entry = tk.Entry(self.editorFrame)
            #     entry.grid(row=i, column=1, padx=10, pady=10)
            #     entry.insert(0, str(self.__selected_values[1+i]))

            else:
                entry = tk.Entry(self.editorFrame)
                entry.grid(row=i, column=1, padx=10, pady=10)
                entry.insert(0, self.__selected_values[1+i])

            self.editor_entries.append(entry)

        save_btn = tk.Button(self.editorFrame,
                             text="Update", command=self._updateRecord)
        save_btn.grid(row=len(self.editor_entries)+1, column=1)

    def _updateRecord(self):
        ok = self.dashboardService.updateForLookupAccountOpAgent(
            id=self.__selected_values[0],
            lookup_id=self.editor_entries[0].get(),
            account_name=self.editor_entries[1].get(),
            op_cash=self.editor_entries[2].get(),
            op_bank=self.editor_entries[3].get(),
            agent_name=self.editor_entries[4].get())
        if ok:
            self.editorFrame.grab_release()
            self.editorFrame.destroy()
            self.rootApp.updateDashboardLayout()
        else:
            tk.Label(self.editorFrame, text="unable to update").grid(
                row=len(self.editor_entries), column=0)

    def _deleteRecord(self):
        self._selectRecord()
        answer = askokcancel(
            title='Confirmation',
            message='Deleting will delete all the data.',
            icon=WARNING)

        if answer:
            ok = self.dashboardService.delete(id=self.__selected_values[0])
            if ok:
                self.rootApp.updateAllLayout()
                showinfo(
                    title='Deletion Status',
                    message='The data is deleted successfully')
            else:
                self.rootApp.updateAllLayout()
                showerror("error", "unable to delete")

    def _createCreateFrame(self):
        # self.__selectRecord()
        self.editorFrame = tk.Toplevel()
        self.editorFrame.grab_set()
        self.editorFrame.minsize(300, 300)
        editor_labels = ["lookup_id", "account_name",
                         "op_cash", "op_bank", "agent_name"]
        self.editor_entries = []

        for i, editor_label in enumerate(editor_labels):
            label = tk.Label(self.editorFrame, text=editor_label)
            label.grid(row=i, column=0, padx=10, pady=10)

            if editor_label == "agent_name":
                agent_name_list = getListOfAgentName()
                agent_name_list = list(chain.from_iterable(agent_name_list))
                entry = ttk.Combobox(self.editorFrame,  values=agent_name_list)
                entry.grid(row=i, column=1, padx=10, pady=10)
            else:
                entry = tk.Entry(self.editorFrame)
                entry.grid(row=i, column=1, padx=10, pady=10)
            if editor_label in ['op_cash', 'op_bank']:
                entry.insert(0, 0)
            self.editor_entries.append(entry)

        save_btn = tk.Button(self.editorFrame,
                             text="Create", command=self._createRecord)
        save_btn.grid(row=len(self.editor_entries)+1, column=1)

    def _createRecord(self):
        ok = self.dashboardService.create(
            lookup_id=self.editor_entries[0].get(),
            account_name=self.editor_entries[1].get(),
            op_cash=self.editor_entries[2].get(),
            op_bank=self.editor_entries[3].get(),
            agent_name=self.editor_entries[4].get())
        if ok:
            self.editorFrame.grab_release()
            self.editorFrame.destroy()
            self.rootApp.updateDashboardLayout()
        else:
            tk.Label(self.editorFrame, text="unable to create record").grid(
                row=len(self.editor_entries), column=0)
