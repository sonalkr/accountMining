from datetime import datetime
from itertools import chain
import locale
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showerror, showinfo
from db import getDgReadOnly
import pandas as pd

from gui.baseApp import BaseApp
from gui.layouts.baseLayout import BaseLayout
from services.accountRefreshService import AccountRefreshService
from services.dashboardService import DashboardService
from services.saleRegistorService import SaleRegistorService
from services.util import blankCurrencyFormat, getListOfAgentName, noneToBlank


class SaleRegistorLayout(BaseLayout):
    def __init__(self, rootApp:BaseApp, root: ttk.Frame) -> None:
        self.root = root
        self.rootApp = rootApp
        self.accountRefreshService = AccountRefreshService()
        self.dashboardService = DashboardService()
        self.saleRegistorService = SaleRegistorService()
        self.data = pd.DataFrame()
    
    def _destory(self):
        for child in self.root.winfo_children():
            child.destroy()
            
    def _getToolBar(self):
        toolbar = tk.Frame(self.sheet_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        # b1 = tk.Button(
        #     toolbar,
        #     relief=tk.FLAT,
        #     compound=tk.LEFT,
        #     text="Update",
        #     command=self._createUpdateFrame,
        #     # image=imgs["notepad"]
        # )
        # b1.pack(side=tk.LEFT, padx=0, pady=0)

        b2 = tk.Button(
            toolbar,
            text="Delete",
            compound=tk.LEFT,
            command=self._deleteRecord,
            relief=tk.FLAT,
            # image=imgs["github"]
        )
        b2.pack(side=tk.LEFT, padx=0, pady=0)

        # b3 = tk.Button(
        #     toolbar,
        #     text="Create",
        #     compound=tk.LEFT,
        #     command=self._createCreateFrame,
        #     relief=tk.FLAT,
        #     # image=imgs["github"]
        # )
        # b3.pack(side=tk.LEFT, padx=0, pady=0)

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
        rows, col = self.saleRegistorService.getForLayout()
        head_columns = ('id', '_account_name', 'date_', 'site_name', 'account_name', 'qty_cft', 'qty_ton', 'truck_no', 'transporter_name', 'shipping_address', '_total_amount', '_total_received')
        chlid_columns = ('_sale_amount', '_shipping_amount', 'bank_sale', 'bank_received', 'cash_received', 'm_rate', 'm_unit', 's_rate', 'u_unit')

        self.data = pd.DataFrame(rows, columns=col)

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
        self.sheet.column("_account_name", width=0, stretch=tk.NO)
        self.sheet.column('date_', anchor=tk.E, width=80)
        self.sheet.column('site_name', anchor=tk.E, width=80)
        self.sheet.column('account_name', anchor=tk.E, width=80)
        self.sheet.column('qty_cft', anchor=tk.E, width=120)
        self.sheet.column('qty_ton', anchor=tk.E, width=80)
        self.sheet.column('truck_no', anchor=tk.E, width=80)
        self.sheet.column('transporter_name', anchor=tk.E, width=80)
        self.sheet.column('shipping_address', anchor=tk.E, width=80)
        self.sheet.column('_total_amount', anchor=tk.E, width=80)
        self.sheet.column('_total_received', anchor=tk.E, width=80)

        self.sheet.heading('date_', text="Date")
        self.sheet.heading('site_name', text="Site")
        self.sheet.heading('account_name', text="Party Name")
        self.sheet.heading('qty_cft', text="QTY CFT")
        self.sheet.heading('qty_ton', text="QTY TON")
        self.sheet.heading('truck_no', text="Truck No")
        self.sheet.heading('transporter_name', text="Transporter")
        self.sheet.heading('shipping_address', text="Shipping Address")
        self.sheet.heading('_total_amount', text="Total Sale")
        self.sheet.heading('_total_received', text="Total Received")

        locale.setlocale(locale.LC_MONETARY, 'en_IN')

        for i, row in self.data.iterrows():
            # print(row["s_unit"])
            tag = ""
            # print(row["s_unit"])
            if i % 2 == 0:
                tag = "even"
            else :
                tag = "odd"

            self.sheet.insert('', tk.END, iid=str(row['id']), open=True, values=(row['id'],row['account_name'],datetime.fromordinal(row['date_']).strftime("%d-%b-%Y"), noneToBlank(row['site_name']), noneToBlank(row['account_name']),  noneToBlank(row['qty_cft']), noneToBlank(row['qty_ton']), noneToBlank(row['truck_no']), noneToBlank(row['transporter_name']),  blankCurrencyFormat(row['_total_amount']), blankCurrencyFormat(row['cash_received']+row['bank_received'])), tags=(tag))
            if row['material_name']:
                self.sheet.insert(str(row['id']), tk.END, open=True, values=(row['id'],row['account_name'], '', row['material_name'], f"{blankCurrencyFormat(row['m_rate'])} / {row['m_unit']}", blankCurrencyFormat(row["_sale_amount"]), '', '', '', ''), tags=(tag))
            if row['shipping_address']:
                self.sheet.insert(str(row['id']), tk.END, open=True, values=(row['id'],row['account_name'], '',  row['shipping_address'], f"{blankCurrencyFormat(row['s_rate'])} / {row['m_unit']}", blankCurrencyFormat(row["_shipping_amount"]), '', '', '', ''), tags=(tag))
            if row['bank_sale']:
                self.sheet.insert(str(row['id']), tk.END, open=True, values=(row['id'],row['account_name'], '', "GST Sale", '', blankCurrencyFormat(row["bank_sale"]), '', '', '', ''), tags=(tag))
        # self.sheet.bind("<ButtonRelease-1>", self.select_record)

        self.sheet.bind("<Double-Button-1>", self._navigateToPartyLedger)
        # self.sheet.bind("<ButtonRelease-1>", self.select_record)

        return self.sheet_frame

    def _navigateToPartyLedger(self,e):
        self._selectRecord()
        self.rootApp.selectPartyTab(account_name=self.__selected_values[1])


    def _selectRecord(self):
        selected = self.sheet.focus()
        print(self.sheet.item(selected, 'values'))
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
                account_name_list = list(chain.from_iterable(account_name_list))
                entry = ttk.Combobox(self.editorFrame, values=account_name_list )
                entry.current(account_name_list.index(self.__selected_values[1+i]))
                entry.grid(row=i, column=1, padx=10, pady=10)
            elif editor_label == "agent_name":
                agent_name_list = getListOfAgentName()
                agent_name_list = list(chain.from_iterable(agent_name_list))
                entry = ttk.Combobox(self.editorFrame,  values=agent_name_list )
                print(self.__selected_values[13])
                if self.__selected_values[13]:
                    entry.current(agent_name_list.index(self.__selected_values[13]))
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
            print(self.__selected_values)
            id = self.__selected_values[0]
            ok = self.saleRegistorService.delete(id=id)
            if ok:
                self.accountRefreshService.calculateClosingBySaleEntry(account_name=self.__selected_values[3])
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
                entry = ttk.Combobox(self.editorFrame,  values=agent_name_list )
                entry.grid(row=i, column=1, padx=10, pady=10)
            else:
                entry = tk.Entry(self.editorFrame)
                entry.grid(row=i, column=1, padx=10, pady=10)
            if editor_label in ['op_cash', 'op_bank']:
                entry.insert(0,0)
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


