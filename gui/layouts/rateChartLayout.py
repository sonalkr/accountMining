from datetime import datetime
from itertools import chain
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showerror, showinfo
from tkcalendar import Calendar, DateEntry
from gui.baseApp import BaseApp
from gui.layouts.baseLayout import BaseLayout
from services.accountRefreshService import AccountRefreshService
from services.dashboardService import DashboardService
from services.rateChartService import RateChartService
from services.util import blankCurrencyFormat, getListOfMaterialName, getorCreateMaterialShippingId


class RateChartLayout(BaseLayout):
    def __init__(self, rootApp:BaseApp, root: ttk.Frame) -> None:
        self.rateChartService = RateChartService()
        self.dashboardService = DashboardService()
        self.root = root
        self.accountRefreshService = AccountRefreshService()
        self.rootApp = rootApp
    
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
            text="Create Material / Shipping",
            compound=tk.LEFT,
            command=self._createCreateMaterialShippingFrame,
            relief=tk.FLAT,
            # image=imgs["github"]
        )
        b4.pack(side=tk.LEFT, padx=0, pady=0)


        b5 = tk.Button(
            toolbar,
            text="Refresh",
            compound=tk.LEFT,
            command=self._accountRefresh,
            relief=tk.FLAT,
            # image=imgs["github"]
        )
        b5.pack(side=tk.LEFT, padx=0, pady=0)

    def _accountRefresh(self):
        self.accountRefreshService.calculateAll()
        self.rootApp.updateAllLayout()


    def getFrame(self):

        rows = self.rateChartService.getall()
        head_columns = ("id", "date_", "account_name", "material_name", "unit_name", "amount")
        
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

        self.sheet.column("#0", width=0, stretch=tk.NO)
        self.sheet.column("id", width=0, stretch=tk.NO)
        self.sheet.column("date_", anchor=tk.E, width=60)
        self.sheet.column("account_name", anchor=tk.W, width=200)
        self.sheet.column("material_name", anchor=tk.W, width=80)
        self.sheet.column("unit_name", anchor=tk.W, width=80)
        self.sheet.column("amount", anchor=tk.E, width=80)
        
        self.sheet.heading("date_", text="Date")
        self.sheet.heading("account_name", text="Party")
        self.sheet.heading("material_name", text="Material")
        self.sheet.heading("unit_name", text="Unit")
        self.sheet.heading("amount", text="Amount")
        
        
        for row in rows:
            date = datetime.fromordinal(row[1])
            self.sheet.insert('', tk.END, values=(row[0],date.strftime("%d-%b-%Y"),row[2],row[3],row[4],blankCurrencyFormat(row[5])))

        self.sheet.bind("<Double-Button-1>", self._navigateToPartyLedger)
        # self.sheet.bind("<ButtonRelease-1>", self.select_record)

        return self.sheet_frame

    def _navigateToPartyLedger(self,e):
        self._selectRecord()
        self.rootApp.selectPartyTab(account_name=self.__selected_values[2])

    def _selectRecord(self):
        selected = self.sheet.focus()
        self.__selected_values = self.sheet.item(selected, 'values')

    def _createCreateMaterialShippingFrame(self):
        self._selectRecord()
        self.editorFrame = tk.Toplevel()
        self.editorFrame.grab_set()
        self.editorFrame.minsize(300, 300)
        account_name_list = getListOfMaterialName()
        self.editor_entries = []
        account_name_list = list(chain.from_iterable(account_name_list))
        entry = tk.Entry(self.editorFrame)
        entry.grid(row=0, column=0, padx=10, pady=10)
        self.editor_entries.append(entry)
        save_btn = tk.Button(self.editorFrame,
                             text="Add", command=self._createMaterialShipping)
        save_btn.grid(row=len(self.editor_entries)+1, column=1)

    def _createUpdateFrame(self):
        self._selectRecord()
        self.editorFrame = tk.Toplevel()
        self.editorFrame.grab_set()
        self.editorFrame.minsize(300, 300)
        editor_labels = ["date_", "account_name",
                         "material_name", "unit_name", "amount"]
        self.editor_entries = []

        for i, editor_label in enumerate(editor_labels):
            label = tk.Label(self.editorFrame, text=editor_label)
            label.grid(row=i, column=0, padx=10, pady=10)
            if editor_label == "date_":
                d = datetime.strptime(self.__selected_values[1+i], "%d-%b-%Y")
                entry = DateEntry(self.editorFrame,selectmode='day', date_pattern='dd-mm-yyyy',  year=d.year, month=d.month, day=d.day, maxdate=d)
                entry.grid(row=i, column=1, padx=10, pady=10)
            elif editor_label == "account_name":
                account_name_list = self.dashboardService.getListOfAccountName()
                account_name_list = list(chain.from_iterable(account_name_list))
                entry = ttk.Combobox(self.editorFrame, values=account_name_list )
                entry.current(account_name_list.index(self.__selected_values[1+i]))
                entry.grid(row=i, column=1, padx=10, pady=10)
            elif editor_label == "material_name":
                material_name_list = getListOfMaterialName()
                material_name_list = list(chain.from_iterable(material_name_list))
                entry = ttk.Combobox(self.editorFrame,  values=material_name_list )
                entry.current(material_name_list.index(self.__selected_values[1+i]))
                entry.grid(row=i, column=1, padx=10, pady=10)
            elif editor_label == "unit_name":
                unit_name_list = ("TON","CFT","TRIP")
                entry = ttk.Combobox(self.editorFrame,  values=unit_name_list )
                entry.current(unit_name_list.index(self.__selected_values[1+i]))
                entry.grid(row=i, column=1, padx=10, pady=10)
            else:
                entry = tk.Entry(self.editorFrame)
                entry.grid(row=i, column=1, padx=10, pady=10)
                entry.insert(0, self.__selected_values[1+i])
            self.editor_entries.append(entry)

        save_btn = tk.Button(self.editorFrame,
                             text="Update", command=self._updateRecord)
        save_btn.grid(row=len(self.editor_entries)+1, column=1)

    def _updateRecord(self):
        print(self.editor_entries[0].get())
        date = datetime.strptime(self.editor_entries[0].get(), "%d-%m-%Y")
        
        id = self.rateChartService.update(
            id=self.__selected_values[0],
            date=date.strftime('%d-%b-%Y'),
            account_name=self.editor_entries[1].get(),
            material_name=self.editor_entries[2].get(),
            unit_name=self.editor_entries[3].get(),
            amount=self.editor_entries[4].get())
        if id:
            self.accountRefreshService.calculateRateChange(id=id, previous_date=date.toordinal())
            self.editorFrame.grab_release()
            self.editorFrame.destroy()
            self.rootApp.updateAllLayout()
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
            ok= self.rateChartService.delete(id=self.__selected_values[0])
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
        editor_labels = ["date_", "account_name",
                         "material_name", "unit_name", "amount"]
        self.editor_entries = []

        for i, editor_label in enumerate(editor_labels):
            label = tk.Label(self.editorFrame, text=editor_label)
            label.grid(row=i, column=0, padx=10, pady=10)
            if editor_label == "date_":
                entry = DateEntry(self.editorFrame,selectmode='day', date_pattern='dd-mm-yyyy')
                entry.grid(row=i, column=1, padx=10, pady=10)
            elif editor_label == "account_name":
                account_name_list = self.dashboardService.getListOfAccountName()
                account_name_list = list(chain.from_iterable(account_name_list))
                entry = ttk.Combobox(self.editorFrame,  values=account_name_list )
                entry.grid(row=i, column=1, padx=10, pady=10)
            elif editor_label == "material_name":
                material_name_list = getListOfMaterialName()
                material_name_list = list(chain.from_iterable(material_name_list))
                entry = ttk.Combobox(self.editorFrame,  values=material_name_list )
                entry.grid(row=i, column=1, padx=10, pady=10)
            elif editor_label == "unit_name":
                unit_name_list = ("TON","CFT","TRIP")
                entry = ttk.Combobox(self.editorFrame,  values=unit_name_list )
                entry.grid(row=i, column=1, padx=10, pady=10)
            else:
                entry = tk.Entry(self.editorFrame)
                entry.grid(row=i, column=1, padx=10, pady=10)
            if editor_label == "amount":
                entry.insert(0,0)
            self.editor_entries.append(entry)

        save_btn = tk.Button(self.editorFrame,
                             text="Create", command=self._createRecord)
        save_btn.grid(row=len(self.editor_entries)+1, column=1)

    def _createRecord(self):
        date = datetime.strptime(self.editor_entries[0].get(), "%d-%m-%Y")
        id= self.rateChartService.create(
            date=date.strftime('%d-%b-%Y'),
            account_name=self.editor_entries[1].get(),
            material_name=self.editor_entries[2].get(),
            unit_name=self.editor_entries[3].get(),
            amount=self.editor_entries[4].get())
        if id:
            self.accountRefreshService.calculateRateChange(id=id, previous_date=date.toordinal())
            self.editorFrame.grab_release()
            self.editorFrame.destroy()
            self.rootApp.updateAllLayout()
        else:
            tk.Label(self.editorFrame, text="unable to create account").grid(
                row=len(self.editor_entries), column=0)

    def _createMaterialShipping(self):
        getorCreateMaterialShippingId(
            material_name=self.editor_entries[0].get())
        self.editorFrame.grab_release()
        self.editorFrame.destroy()
        self.rootApp.updateAllLayout()
        