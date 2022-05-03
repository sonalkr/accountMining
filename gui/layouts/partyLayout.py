from datetime import datetime
from itertools import chain
import locale
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showerror, showinfo

from matplotlib.pyplot import text
from db import getDgReadOnly
import pandas as pd

from gui.baseApp import BaseApp
from gui.layouts.baseLayout import BaseLayout
from services.accountRefreshService import AccountRefreshService
from services.dashboardService import DashboardService
from services.saleRegistorService import SaleRegistorService
from services.util import blankCurrencyFormat, getListOfAgentName, noneToBlank


class PartyLayout(BaseLayout):
    def __init__(self, rootApp:BaseApp, root: ttk.Frame, account_name) -> None:
        self.root = root
        self.rootApp = rootApp
        self.accountRefreshService = AccountRefreshService()
        self.dashboardService = DashboardService()
        self.saleRegistorService = SaleRegistorService()
        self.data = pd.DataFrame()
        self.account_name = account_name
    
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

        # b2 = tk.Button(
        #     toolbar,
        #     text="Delete",
        #     compound=tk.LEFT,
        #     command=self._deleteRecord,
        #     relief=tk.FLAT,
        #     # image=imgs["github"]
        # )
        # b2.pack(side=tk.LEFT, padx=0, pady=0)

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
        self.sheet_frame = tk.Frame(self.root)
        self.sheet_frame.pack(expand=1, fill="both")

        if self.account_name == None:
            return [self.sheet_frame]

        id_account_name = self.dashboardService.getIdByAccountName(account_name=self.account_name)
        rows, col = self.saleRegistorService.getForLayoutIdAccount(id_account_name=id_account_name)
        head_columns = ('id', 'date_', 'site_name', 'account_name', 'qty_cft', 'qty_ton', 'truck_no', 'transporter_name', '_total_amount', '_total_received')
        chlid_columns = ('_sale_amount', '_shipping_amount', 'bank_sale', 'bank_received', 'cash_received', 'm_rate', 'm_unit', 's_rate', 'u_unit')

        self.data = pd.DataFrame(rows, columns=col)


        self._getToolBar()

        if not len(rows):
            # ttk.Label(self.root, text="NO Data").pack()
            return [self.sheet_frame]
        
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
        self.sheet.column('date_', anchor=tk.E, width=80)
        self.sheet.column('site_name', anchor=tk.E, width=80)
        self.sheet.column('account_name', anchor=tk.E, width=80)
        self.sheet.column('qty_cft', anchor=tk.E, width=120)
        self.sheet.column('qty_ton', anchor=tk.E, width=80)
        self.sheet.column('truck_no', anchor=tk.E, width=80)
        self.sheet.column('transporter_name', anchor=tk.E, width=80)
        self.sheet.column('_total_amount', anchor=tk.E, width=80)
        self.sheet.column('_total_received', anchor=tk.E, width=80)

        self.sheet.heading('date_', text="Date")
        self.sheet.heading('site_name', text="Site")
        self.sheet.heading('account_name', text="Party Name")
        self.sheet.heading('qty_cft', text="QTY CFT")
        self.sheet.heading('qty_ton', text="QTY TON")
        self.sheet.heading('truck_no', text="Vehicle No")
        self.sheet.heading('transporter_name', text="Transporter")
        self.sheet.heading('_total_amount', text="Total Sale")
        self.sheet.heading('_total_received', text="Total Received")

        self.sheet.insert('', tk.END ,values=('', '', '', '', blankCurrencyFormat(self.data["qty_cft"].sum()), blankCurrencyFormat(self.data["qty_ton"].sum()), '', '', '', blankCurrencyFormat(self.data["_total_amount"].sum()), blankCurrencyFormat(self.data["cash_received"].sum()+self.data["bank_received"].sum())), tags=('bottom'))

        for i, row in self.data.iterrows():
            tag = ""
            # print(row["s_unit"])
            if i % 2 == 0:
                tag = "even"
            else :
                tag = "odd"

            self.sheet.insert('', tk.END, iid=str(row['id']), open=True, values=(row['account_name'],datetime.fromordinal(row['date_']).strftime("%d-%b-%Y"), noneToBlank(row['site_name']), noneToBlank(row['account_name']),  noneToBlank(row['qty_cft']), noneToBlank(row['qty_ton']), noneToBlank(row['truck_no']), noneToBlank(row['transporter_name']), blankCurrencyFormat(row['_total_amount']), blankCurrencyFormat(row['cash_received']+row['bank_received'])), tags=(tag))
            if row['material_name']:
                self.sheet.insert(str(row['id']), tk.END, open=True, values=(row['account_name'], '',  row['material_name'], f"{blankCurrencyFormat(row['m_rate'])} / {row['m_unit']}", blankCurrencyFormat(row["_sale_amount"]), '', '', '', ''), tags=(tag))
            if row['shipping_address']:
                self.sheet.insert(str(row['id']), tk.END, open=True, values=(row['account_name'], '',  row['shipping_address'], f"{blankCurrencyFormat(row['s_rate'])} / {row['m_unit']}", blankCurrencyFormat(row["_shipping_amount"]), '', '', '', ''), tags=(tag))
            if row['bank_sale']:
                self.sheet.insert(str(row['id']), tk.END, open=True, values=(row['account_name'], '', "GST Sale", '', blankCurrencyFormat(row["bank_sale"]), '', '', '', ''), tags=(tag))
        # self.sheet.bind("<ButtonRelease-1>", self.select_record)


        self.sheet.bind("<Double-Button-1>", self._navigateToPartyLedger)
        head_columns2 = ('material_name', 'qty_cft', 'qty_ton', 'material_amount', 'shipping_amount')
        row2, col2 = self.saleRegistorService.getMaterialPivot(id_account=id_account_name)
        material_pivot_data = pd.DataFrame(row2, columns=col2)

        self.material_pivot_frame = tk.Frame(self.root)
        self.material_pivot_frame.pack(expand=1, fill=tk.Y)
        material_pivot_scroll = tk.Scrollbar(self.material_pivot_frame)
        material_pivot_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        material_sheet = ttk.Treeview(self.material_pivot_frame, yscrollcommand=material_pivot_scroll.set,
                                  selectmode="extended", columns=head_columns2)
        material_sheet.pack(expand=1, fill=tk.Y)

        material_pivot_scroll.config(command=material_sheet.yview)
        material_sheet.tag_configure('even', background='#dbcced')
        material_sheet.tag_configure('odd', background='#d8edec')
        material_sheet.tag_configure('bottom', background='#80aaff')


        material_sheet.column("#0", width=0, stretch=tk.NO)
        material_sheet.column('material_name', anchor=tk.E, width=250) # 'material_name', 'material_amount', 'shipping_amount', 'cash_received', 'bank_received', 'bank_sale'
        material_sheet.column('qty_cft', anchor=tk.E, width=250)
        material_sheet.column('qty_ton', anchor=tk.E, width=250)
        material_sheet.column('material_amount', anchor=tk.E, width=250)
        material_sheet.column('shipping_amount', anchor=tk.E, width=250)

        material_sheet.heading('material_name',text='material_name')
        material_sheet.heading('qty_cft',text='CFT')
        material_sheet.heading('qty_ton',text='TON')
        material_sheet.heading('material_amount',text='material_amount')
        material_sheet.heading('shipping_amount',text='shipping_amount')
        sum_r = [0,0,0,0,0]
        for i , r in enumerate(row2):
            if i % 2 == 0:
                tag = "even"
            else :
                tag = "odd"
            print(r)
            sum_r[1] += float(r[1])
            sum_r[2] += float(r[2])
            sum_r[3] += float(r[3])
            sum_r[4] += float(r[4])
            material_sheet.insert('', tk.END ,values=(r[0],blankCurrencyFormat(r[1]),blankCurrencyFormat(r[2]),blankCurrencyFormat(r[3]),blankCurrencyFormat(r[4])),tags=(tag))

        material_sheet.insert('', tk.END ,values=("Total",blankCurrencyFormat(sum_r[1]),blankCurrencyFormat(sum_r[2]),blankCurrencyFormat(sum_r[3]),blankCurrencyFormat(sum_r[4])), tags=("bottom"))

        return [self.sheet_frame, self.material_pivot_frame]

    def _navigateToPartyLedger(self,e):
        self._selectRecord()
        self.rootApp.selectPartyTab(account_name=self.__selected_values[0])


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
            ok = self.saleRegistorService.delete(id=self.__selected_values[0])
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


