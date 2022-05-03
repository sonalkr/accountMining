from dataclasses import replace
from datetime import datetime
from enum import Flag
from platform import release
import re
import tkinter as tk
import os
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import traceback
import numpy as np
from numpy import nan
import pandas as pd
from pandastable import Table
from gui.baseApp import BaseApp
from services.dashboardService import DashboardService
from services.rateChartService import RateChartService
# from gui.app import App
from services.saveToDb import SaveToDb
from services.util import createAccountLookup, createMaterialLookup, getListOfIDMaterialName, getorCreateMaterialShippingId, verifyAccountLookup, verifyMaterialAndShippingLookup
from tkcalendar import Calendar, DateEntry


class Upload():
    def __init__(self, rootApp: BaseApp) -> None:
        self.rootApp = rootApp
        self.__data = pd.DataFrame()
        self.save_to = ""
        self.dashboardService = DashboardService()
        self.rateChartSerivce = RateChartService()

    def save(self):
        error = ""
        saveToDb = SaveToDb(self.__data)
        try:
            if(self.save_to == "sale registor"):
                if not saveToDb.validateSaleRegistor() or not saveToDb.saleRegistor():
                    raise Exception()
                self.uploadWin.grab_release()
                self.uploadWin.destroy()
                self.rootApp.updateDashboardLayout()
                self.rootApp.updateRateChartLayout()

            elif(self.save_to == "account"):
                if not saveToDb.validateAccount() or not saveToDb.account():
                    raise Exception()
                self.uploadWin.grab_release()
                self.uploadWin.destroy()
                self.rootApp.updateDashboardLayout()

            elif(self.save_to == "rate"):
                if not saveToDb.validateRateChart() or not saveToDb.rateChart():
                    raise Exception()
                self.uploadWin.grab_release()
                self.uploadWin.destroy()
                self.rootApp.updateRateChartLayout()
                self.rootApp.updateDashboardLayout()

            else:
                messagebox.showerror(
                    "error", "selected method of import not found", parent=self.uploadWin)
        except:
            self.uploadWin.grab_release()
            self.uploadWin.destroy()

            messagebox.showerror(
                "error", "unable to import "+self.save_to)
            traceback.print_exc()

    def run(self, save_to):
        self.save_to = save_to
        self.uploadWin = tk.Toplevel()
        self.uploadWin.grab_set()
        self.uploadWin.minsize(700, 500)
        self.uploadWin.title("upload")
        self.open_file()
        self.uploadWin.mainloop()

    def open_file(self):
        file = filedialog.askopenfile(parent=self.uploadWin, mode='r', filetypes=[
            (self.save_to, '*.xlsx')])
        if file is not None:
            self.filepath = os.path.abspath(file.name)
            df = pd.read_excel(self.filepath)
            self.__data = df

            self.toolBar = tk.Frame(self.uploadWin)
            self.toolBar.pack()
            display_method = tk.Label(self.uploadWin, text=self.save_to)
            display_method.pack()
            display_filepath = tk.Label(self.uploadWin, text=self.filepath)
            display_filepath.pack()
            self.frameView = tk.Frame(self.uploadWin)
            self.frameView.pack(expand=1, fill="both")

            if self.save_to == "sale registor":
                self._advanceRead()
            else:
                self._normalRead()
        else:
            self.uploadWin.destroy()

    def _normalRead(self):
        df = pd.read_excel(self.filepath)
        save_btn = tk.Button(self.toolBar, text="import",
                             command=lambda: self.save())
        save_btn.pack(side=tk.TOP, fill=tk.Y)
        table = Table(self.frameView, dataframe=df,
                      showtoolbar=True, showstatusbar=True)
        table.show()
        self.__data = df

    def _advanceRead(self):
        self.__data[["material_name", "truck_no", "transporter_name", "shipping_address", "remarks", "m_material_unit", "m_shipping_unit"]] = self.__data[[
            "material_name", "truck_no", "transporter_name", "shipping_address", "remarks", "m_material_unit", "m_shipping_unit"]].fillna("")
        self.__data[["qty_cft", "qty_ton", "bank_sale","bank_received","cash_received", "is_manual", "m_material_amount", "m_shipping_amount"]] = self.__data[[
            "qty_cft", "qty_ton", "bank_sale","bank_received","cash_received", "is_manual", "m_material_amount", "m_shipping_amount"]].fillna(0)
        self.__data['o_date'] = pd.to_datetime(self.__data["date"])
        self.__data.sort_values(by="o_date", inplace=True)
        self.__data['lookup_account_name'] = ""
        self.__data['lookup_material_name'] = ""
        self.__data['lookup_shipping_address'] = ""
        self.__data['lookup_material_name_rate'] = ""
        self.__data['lookup_shipping_address_rate'] = ""
        self.__data['shipping_address'] = self.__data['shipping_address'].replace(
            {'self': "", 'sef': "", 'SELF': "", 'SEL': "", 'SEF': "", 'sel': ""})
        saveToDb = SaveToDb(self.__data)
        if not saveToDb.validateSaleRegistor():
            self.uploadWin.grab_release()
            self.uploadWin.destroy()
            print(self.__data.columns)
            messagebox.showerror(
                "error", "wrong sale data")

        self._createSaleSheet()
        self._refreshAllData()
        self._updateSaleSheet()

    def _createSaleSheet(self):
        head_columns = ("id", "date_", "challan_no", "site", "account_name", "lookup_account_name", "material_name", "lookup_material_name",
                        "qty_cft", "qty_ton", "truck_no", "transporter_name", "shipping_address", "lookup_shipping_address", 'bank_sale','bank_received','cash_received', "remarks", "lookup_material_name_rate", "lookup_shipping_address_rate")
        body_columns = ("id", "is_manual", "m_material_unit",
                        "m_material_amount", "m_shipping_unit", "m_shipping_amount")

        save_btn = tk.Button(self.toolBar, text="Lookup",
                             command=self._mapLookup)
        save_btn.pack(side=tk.RIGHT, fill=tk.Y)

        self.sheet_frame = tk.Frame(self.frameView)
        self.sheet_frame.pack(expand=1, fill="both")

        sheet_scroll = tk.Scrollbar(self.sheet_frame)
        sheet_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.sheet = ttk.Treeview(self.sheet_frame, yscrollcommand=sheet_scroll.set,
                                  selectmode="extended", columns=head_columns)
        self.sheet.pack(expand=1, fill="both")

        sheet_scroll.config(command=self.sheet.yview)

        self.sheet.column("#0", width=0, stretch=tk.NO)
        self.sheet.column("id", width=0, stretch=tk.NO)
        self.sheet.column("date_", anchor=tk.E, width=60)
        self.sheet.column("challan_no", anchor=tk.W, width=60)
        self.sheet.column("site", anchor=tk.W, width=100)
        self.sheet.column("account_name", anchor=tk.W, width=200)
        self.sheet.column("lookup_account_name", anchor=tk.W, width=200)
        self.sheet.column("material_name", anchor=tk.W, width=80)
        self.sheet.column("lookup_material_name", anchor=tk.W, width=80)
        self.sheet.column("qty_cft", anchor=tk.W, width=80)
        self.sheet.column("qty_ton", anchor=tk.W, width=80)
        self.sheet.column("truck_no", anchor=tk.W, width=80)
        self.sheet.column("transporter_name", anchor=tk.W, width=100)
        self.sheet.column("shipping_address", anchor=tk.W, width=200)
        self.sheet.column("lookup_shipping_address", anchor=tk.W, width=200)
        self.sheet.column("bank_sale", anchor=tk.W, width=80)
        self.sheet.column("bank_received", anchor=tk.W, width=80)
        self.sheet.column("cash_received", anchor=tk.W, width=80)
        self.sheet.column("remarks", anchor=tk.W, width=80)
        self.sheet.column("lookup_material_name_rate", anchor=tk.W, width=80)
        self.sheet.column("lookup_shipping_address_rate",
                          anchor=tk.W, width=80)

        self.sheet.heading("date_", text="Date")
        self.sheet.heading("challan_no", text="Challan NO")
        self.sheet.heading("site", text="Site")
        self.sheet.heading("account_name", text="Party Name")
        self.sheet.heading("lookup_account_name", text="Party Name Lookup")
        self.sheet.heading("material_name", text="material_name")
        self.sheet.heading("lookup_material_name", text="Material Lookup")
        self.sheet.heading("qty_cft", text="QTY CFT")
        self.sheet.heading("qty_ton", text="QTY TON")
        self.sheet.heading("truck_no", text="Truck NO")
        self.sheet.heading("transporter_name", text="Transporter Name")
        self.sheet.heading("shipping_address", text="Shipping Address")
        self.sheet.heading("lookup_shipping_address",
                           text="Shipping Address Lookup")
        self.sheet.heading("bank_sale", text="Bank Sale")
        self.sheet.heading("bank_received", text="Bank Received")
        self.sheet.heading("cash_received", text="Cash Received")
        self.sheet.heading("remarks", text="Remarks")
        self.sheet.heading("lookup_material_name_rate",
                           text="Lookup Material Rate")
        self.sheet.heading("lookup_shipping_address_rate",
                           text="Lookup Shipping Rate")

    def _updateSaleSheet(self):
        for item in self.sheet.get_children():
            self.sheet.delete(item)
        print(self.__data.shape)
        for i, row in self.__data.iterrows():
            # lookup_account_name = verifyAccountLookup(row["account_name"])
            # lookup_account_name = lookup_account_name if len(
            #     lookup_account_name) else nan
            # lookup_material_name = verifyMaterialLookup(row["material_name"])
            # lookup_material_name = lookup_material_name if len(
            #     lookup_material_name) else nan
            # lookup_shipping_address = verifyMaterialLookup(
            #     row["shipping_address"])
            # lookup_shipping_address = lookup_shipping_address if len(
            #     lookup_shipping_address) else nan

            self.sheet.insert('', tk.END, values=(i, row["date"], row["challan_no"], row["site"], row["account_name"], row['lookup_account_name'], row["material_name"], row['lookup_material_name'],
                              row["qty_cft"], row["qty_ton"], row["truck_no"], row["transporter_name"], row["shipping_address"], row['lookup_shipping_address'], row["bank_sale"],row["bank_received"],row["cash_received"], row["remarks"], row["lookup_material_name_rate"], row["lookup_shipping_address_rate"]))

    def _selectRecord(self):
        selected = self.sheet.focus()
        self.__selected_values = self.sheet.item(selected, 'values')

    def _mapLookup(self):
        self.lookupWin = tk.Toplevel()
        self.lookupWin.grab_set()
        self.lookupWin.title('lookup')
        self.lookupControlFrame = tk.Frame(self.lookupWin)
        self.lookupControlFrame.pack(side=tk.TOP)
        self.lookupBodyFrame = tk.Frame(self.lookupWin)
        self.lookupBodyFrame.pack(side=tk.BOTTOM)
        self.lookupSheet1 = ttk.Treeview()
        self.entry1 = tk.Entry()
        self.entry2 = tk.Entry()
        self.entry3 = tk.Entry()

        self._lookupRoute()

    def _clearEntry(self):
        self.entry1.delete(0, tk.END)
        self.entry2.delete(0, tk.END)
        self.entry3.delete(0, tk.END)

    def _lookupRoute(self):
        self._updateSaleSheet()

        material_data = self.__data[~self.__data["material_name"].eq("")]
        shipping_data = self.__data[~self.__data['shipping_address'].eq("")]
        if self.__data['lookup_account_name'].eq("").sum():
            print("runing self._lookupAccountName()")
            self._lookupAccountName()

        elif material_data['lookup_material_name'].eq("").sum():
            print("runing self._lookupMaterialName()")
            self._lookupMaterialName()

        elif shipping_data['lookup_shipping_address'].eq("").sum():
            print("runing self._lookupShippingAddress()")
            self._lookupShippingAddress()

        elif material_data['lookup_material_name_rate'].eq("").sum():
            print("runing self._lookupMaterialRate()")
            self._lookupMaterialRate()

        elif shipping_data['lookup_shipping_address_rate'].eq("").sum():
            print("runing self._lookupShippingRate()")
            self._lookupShippingRate()

        else:
            self.lookupWin.grab_release()
            self.lookupWin.destroy()

            for item in self.toolBar.winfo_children():
                item.destroy()

            save_btn = tk.Button(self.toolBar, text="Save",
                                 command=lambda: self.save())
            save_btn.pack(side=tk.RIGHT, fill=tk.Y)

    def _lookupAccountName(self):
        self._clearLookFrame()

        lookup_account_list = self._getAccountLookupListFromDF()

        headSelectFrame = tk.Frame(self.lookupBodyFrame)
        headSelectFrame.pack(side=tk.TOP)
        label = tk.Label(headSelectFrame, text=lookup_account_list[0])
        label.pack(side=tk.LEFT)
        btn = tk.Button(headSelectFrame, text="Select", command=lambda: self._saveLookupValue(
            is_selected=True, type_of_lookup="account_name", lookup_from1=lookup_account_list[0]))
        btn.pack(side=tk.RIGHT)

        head_columns = ("id", "lookup_id", "account_name")
        selectFrame = tk.Frame(self.lookupBodyFrame)
        selectFrame.pack(side=tk.TOP)
        sheet_frame = tk.Frame(selectFrame)
        sheet_frame.pack(expand=1, fill="both", side=tk.BOTTOM)

        sheet_scroll = tk.Scrollbar(sheet_frame)
        sheet_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.lookupSheet1 = ttk.Treeview(sheet_frame, yscrollcommand=sheet_scroll.set,
                                         selectmode="extended", columns=head_columns)
        self.lookupSheet1.pack(expand=1, fill="both")

        sheet_scroll.config(command=self.lookupSheet1.yview)

        rows = self.dashboardService.getListOfIdLookupIDAccountName()

        self.lookupSheet1.column("#0", width=0, stretch=tk.NO)
        self.lookupSheet1.column("id", width=0, stretch=tk.NO)
        self.lookupSheet1.column("lookup_id", anchor=tk.W, width=60)
        self.lookupSheet1.column("account_name", anchor=tk.W, width=200)

        self.lookupSheet1.heading("lookup_id", text="Lookup ID")
        self.lookupSheet1.heading("account_name", text="Party Name")

        for i, row in enumerate(rows):
            self.lookupSheet1.insert(
                '', tk.END, values=(row[0], row[1], row[2]))

        create_btn = tk.Button(headSelectFrame, text="Save", command=lambda: self._saveLookupValue(
            is_selected=False, type_of_lookup="account_name", lookup_from1=lookup_account_list[0]))
        create_btn.pack()
        # bottom frame
        # addNewFrame = tk.Frame(self.lookupBodyFrame)
        # addNewFrame.pack(side=tk.BOTTOM)
        # tk.Label(addNewFrame, text="Todo")

    def _lookupMaterialName(self):
        self._clearLookFrame()

        lookup_material_list = self._getMaterialLookupListFromDF()

        headSelectFrame = tk.Frame(self.lookupBodyFrame)
        headSelectFrame.pack(side=tk.TOP)
        label = tk.Label(headSelectFrame, text=lookup_material_list[0])
        label.pack(side=tk.LEFT)
        btn = tk.Button(headSelectFrame, text="Select", command=lambda: self._saveLookupValue(
            is_selected=True, type_of_lookup="material_name", lookup_from1=lookup_material_list[0]))
        btn.pack(side=tk.RIGHT)

        head_columns = ("id", "material_name")
        selectFrame = tk.Frame(self.lookupBodyFrame)
        selectFrame.pack(side=tk.TOP)
        sheet_frame = tk.Frame(selectFrame)
        sheet_frame.pack(expand=1, fill="both", side=tk.BOTTOM)

        sheet_scroll = tk.Scrollbar(sheet_frame)
        sheet_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.lookupSheet1 = ttk.Treeview(sheet_frame, yscrollcommand=sheet_scroll.set,
                                         selectmode="extended", columns=head_columns)
        self.lookupSheet1.pack(expand=1, fill="both")

        sheet_scroll.config(command=self.lookupSheet1.yview)

        rows = getListOfIDMaterialName()

        self.lookupSheet1.column("#0", width=0, stretch=tk.NO)
        self.lookupSheet1.column("id", width=0, stretch=tk.NO)
        self.lookupSheet1.column("material_name", anchor=tk.W, width=200)

        self.lookupSheet1.heading("material_name", text="Material")

        for i, row in enumerate(rows):
            self.lookupSheet1.insert('', tk.END, values=(row[0], row[1]))

        create_btn = tk.Button(headSelectFrame, text="Save", command=lambda: self._saveLookupValue(
            is_selected=False, type_of_lookup="material_name", lookup_from1=lookup_material_list[0]))
        create_btn.pack()
        # bottom frame
        # addNewFrame = tk.Frame(self.lookupBodyFrame)
        # addNewFrame.pack(side=tk.BOTTOM)
        # tk.Label(addNewFrame, text="Todo")

    def _lookupShippingAddress(self):
        self._clearLookFrame()

        lookup_shipping_list = self._getShippingAddressLookupListFromDF()

        headSelectFrame = tk.Frame(self.lookupBodyFrame)
        headSelectFrame.pack(side=tk.TOP)
        label = tk.Label(headSelectFrame, text=lookup_shipping_list[0])
        label.pack(side=tk.LEFT)
        btn = tk.Button(headSelectFrame, text="Select", command=lambda: self._saveLookupValue(
            is_selected=True, type_of_lookup="shipping_address", lookup_from1=lookup_shipping_list[0]))
        btn.pack(side=tk.RIGHT)

        head_columns = ("id", "shipping_address")
        selectFrame = tk.Frame(self.lookupBodyFrame)
        selectFrame.pack(side=tk.TOP)
        sheet_frame = tk.Frame(selectFrame)
        sheet_frame.pack(expand=1, fill="both", side=tk.BOTTOM)

        sheet_scroll = tk.Scrollbar(sheet_frame)
        sheet_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.lookupSheet1 = ttk.Treeview(sheet_frame, yscrollcommand=sheet_scroll.set,
                                         selectmode="extended", columns=head_columns)
        self.lookupSheet1.pack(expand=1, fill="both")

        sheet_scroll.config(command=self.lookupSheet1.yview)

        rows = getListOfIDMaterialName()  # same for shipping address

        self.lookupSheet1.column("#0", width=0, stretch=tk.NO)
        self.lookupSheet1.column("id", width=0, stretch=tk.NO)
        self.lookupSheet1.column("shipping_address", anchor=tk.W, width=200)

        self.lookupSheet1.heading("shipping_address", text="Shipping Address")

        for i, row in enumerate(rows):
            self.lookupSheet1.insert('', tk.END, values=(row[0], row[1]))

        create_btn = tk.Button(headSelectFrame, text="Save", command=lambda: self._saveLookupValue(
            is_selected=False, type_of_lookup="shipping_address", lookup_from1=lookup_shipping_list[0]))
        create_btn.pack()
        # bottom frame
        # addNewFrame = tk.Frame(self.lookupBodyFrame)
        # addNewFrame.pack(side=tk.BOTTOM)
        # tk.Label(addNewFrame, text="Todo")

    def _lookupMaterialRate(self):
        self._clearLookFrame()

        lookup_material_list = self._getMaterialRateLookupListFromDF()

        headSelectFrame = tk.Frame(self.lookupBodyFrame)
        headSelectFrame.pack(side=tk.TOP)
        label_head_date = tk.Label(headSelectFrame, text="Date")
        label_head_date.grid(row=0, column=0)
        label_head_account_name = tk.Label(headSelectFrame, text="Party Name")
        label_head_account_name.grid(row=0, column=1)
        label_head_material_name = tk.Label(headSelectFrame, text="Material")
        label_head_material_name.grid(row=0, column=2)
        label_head_unit = tk.Label(headSelectFrame, text="Unit")
        label_head_unit.grid(row=0, column=3)
        label_head_amount = tk.Label(headSelectFrame, text="Amount")
        label_head_amount.grid(row=0, column=4)

        max_date = datetime.strptime(lookup_material_list[0][2], "%d-%b-%Y")
        self.entry1 = DateEntry(
            headSelectFrame, selectmode='day', date_pattern='dd-mm-yyyy', maxdate=max_date)
        self.entry1.grid(row=1, column=0)
        label_account_name = tk.Label(
            headSelectFrame, text=lookup_material_list[0][0])
        label_account_name.grid(row=1, column=1)
        label_material_name = tk.Label(
            headSelectFrame, text=lookup_material_list[0][1])
        label_material_name.grid(row=1, column=2)
        unit_name_list = ("TON", "CFT", "TRIP")
        self.entry2 = ttk.Combobox(headSelectFrame,  values=unit_name_list)
        self.entry2.grid(row=1, column=3)
        self.entry3 = tk.Entry(headSelectFrame)
        self.entry3.grid(row=1, column=4)

        btn = tk.Button(headSelectFrame, text="Save", command=lambda: self._saveLookupValueForRate(
            is_manual=False, type_of_lookup="material_rate", account_name=lookup_material_list[0][0], material_name=lookup_material_list[0][1]))
        btn.grid(row=2, column=4)
        label_len = tk.Label(headSelectFrame, text=str(len(lookup_material_list)))
        label_len.grid(row=3, column=0)

        # # bottom frame
        # addNewFrame = tk.Frame(self.lookupBodyFrame)
        # addNewFrame.pack()
        # tk.Label(addNewFrame, text="Unit")

    def _lookupShippingRate(self):
        self._clearLookFrame()

        lookup_shipping_list = self._getShippingRateLookupListFromDF()

        headSelectFrame = tk.Frame(self.lookupBodyFrame)
        headSelectFrame.pack(side=tk.TOP)
        label_head_date = tk.Label(headSelectFrame, text="Date")
        label_head_date.grid(row=0, column=0)
        label_head_account_name = tk.Label(headSelectFrame, text="Party Name")
        label_head_account_name.grid(row=0, column=1)
        label_head_shipping_name = tk.Label(
            headSelectFrame, text="Shipping Address")
        label_head_shipping_name.grid(row=0, column=2)
        label_head_unit = tk.Label(headSelectFrame, text="Unit")
        label_head_unit.grid(row=0, column=3)
        label_head_amount = tk.Label(headSelectFrame, text="Amount")
        label_head_amount.grid(row=0, column=4)

        max_date = datetime.strptime(lookup_shipping_list[0][2], "%d-%b-%Y")
        self.entry1 = DateEntry(
            headSelectFrame, selectmode='day', date_pattern='dd-mm-yyyy', maxdate=max_date)
        self.entry1.grid(row=1, column=0)
        label_account_name = tk.Label(
            headSelectFrame, text=lookup_shipping_list[0][0])
        label_account_name.grid(row=1, column=1)
        label_shipping_name = tk.Label(
            headSelectFrame, text=lookup_shipping_list[0][1])
        label_shipping_name.grid(row=1, column=2)
        unit_name_list = ("TON", "CFT", "TRIP")
        self.entry2 = ttk.Combobox(headSelectFrame,  values=unit_name_list)
        self.entry2.grid(row=1, column=3)
        self.entry3 = tk.Entry(headSelectFrame)
        self.entry3.grid(row=1, column=4)

        btn = tk.Button(headSelectFrame, text="Save", command=lambda: self._saveLookupValueForRate(
            is_manual=False, type_of_lookup="shipping_rate", account_name=lookup_shipping_list[0][0], material_name=lookup_shipping_list[0][1]))
        btn.grid(row=2, column=4)
        label_len = tk.Label(headSelectFrame, text=str(len(lookup_shipping_list)))
        label_len.grid(row=3, column=0)

        # # bottom frame
        # addNewFrame = tk.Frame(self.lookupBodyFrame)
        # addNewFrame.pack()
        # tk.Label(addNewFrame, text="Unit")

    def _saveLookupValue(self, is_selected: bool, type_of_lookup: str, lookup_from1: str):
        selected1 = self.lookupSheet1.focus()
        selected_values1 = self.lookupSheet1.item(selected1, 'values')

        print(selected_values1, is_selected,
              type_of_lookup, lookup_from1)
        if(type_of_lookup == "account_name" and is_selected):
            createAccountLookup(
                id_account=selected_values1[0], lookup_account_name=lookup_from1)
            self._refreshAccountNameData(
                lookup_from=lookup_from1, replace=selected_values1[2])

        elif(type_of_lookup == "account_name" and not is_selected):
            id = self.dashboardService.getOrCreateAccountId(
                account_name=lookup_from1)
            createAccountLookup(
                id_account=id, lookup_account_name=lookup_from1)
            self._refreshAccountNameData(
                lookup_from=lookup_from1, replace=lookup_from1)

        elif(type_of_lookup == "material_name" and is_selected):
            createMaterialLookup(
                id_material=selected_values1[0], lookup_material_name=lookup_from1)
            self._refreshMaterialNameData(
                lookup_from=lookup_from1, replace=selected_values1[1])

        elif(type_of_lookup == "material_name" and not is_selected):
            id = getorCreateMaterialShippingId(material_name=lookup_from1)
            createMaterialLookup(
                id_material=id, lookup_material_name=lookup_from1)
            self._refreshMaterialNameData(
                lookup_from=lookup_from1, replace=lookup_from1)

        elif(type_of_lookup == "shipping_address" and is_selected):
            createMaterialLookup(
                id_material=selected_values1[0], lookup_material_name=lookup_from1)
            self._refreshShippingAddressData(
                lookup_from=lookup_from1, replace=selected_values1[1])

        elif(type_of_lookup == "shipping_address" and not is_selected):
            id = getorCreateMaterialShippingId(material_name=lookup_from1)
            createMaterialLookup(
                id_material=id, lookup_material_name=lookup_from1)
            self._refreshMaterialNameData(
                lookup_from=lookup_from1, replace=lookup_from1)

        self._refreshAllData()
        self._lookupRoute()
        # account_name, lookup_account_name = self._lookupAccountName()

    def _saveLookupValueForRate(self, is_manual: bool, type_of_lookup: str, account_name: str, material_name: str):
        date = self.entry1.get()
        unit_name = self.entry2.get()
        amount = self.entry3.get()
        date = datetime.strptime(date, "%d-%m-%Y").strftime("%d-%b-%Y")
        print(date, account_name, material_name, unit_name, amount)
        if(type_of_lookup == "material_rate" and not is_manual):
            self.rateChartSerivce.create(
                date, account_name=account_name, material_name=material_name, unit_name=unit_name, amount=amount)
        elif(type_of_lookup == "shipping_rate" and not is_manual):
            self.rateChartSerivce.create(
                date, account_name=account_name, material_name=material_name, unit_name=unit_name, amount=amount)
        self._refreshAllData()

        self._lookupRoute()

    def _clearLookFrame(self):
        self._clearEntry()
        for item in self.lookupBodyFrame.winfo_children():
            item.destroy()

    def _refreshAllData(self):
        self.rootApp.updateAllLayout()
        lookup_account_list = self._getAccountLookupListFromDF()
        for lookup_from_account_name in lookup_account_list:
            account_replace = verifyAccountLookup(lookup_from_account_name)
            if len(account_replace):
                self._refreshAccountNameData(
                    lookup_from=lookup_from_account_name, replace=account_replace)

        lookup_material_list = self._getMaterialLookupListFromDF()
        for lookup_material_name in lookup_material_list:
            material_replace = verifyMaterialAndShippingLookup(
                lookup_material_name)
            if len(material_replace):
                self._refreshMaterialNameData(
                    lookup_from=lookup_material_name, replace=material_replace)

        lookup_shipping_list = self._getShippingAddressLookupListFromDF()
        for lookup_shipping_name in lookup_shipping_list:
            shipping_replace = verifyMaterialAndShippingLookup(
                lookup_shipping_name)  # same for shipping address
            if len(shipping_replace):
                self._refreshShippingAddressData(
                    lookup_from=lookup_shipping_name, replace=shipping_replace)

        lookup_material_name_rate_list = self._getMaterialRateLookupListFromDF()
        for lookup_material_name_rate in lookup_material_name_rate_list:
            material_rate_replace = self.rateChartSerivce.getOnebyDateAccountNameMaterialShipping(
                date=lookup_material_name_rate[2], account_name=lookup_material_name_rate[0], material_name=lookup_material_name_rate[1])
            if len(material_rate_replace):

                d =datetime.fromordinal(material_rate_replace[1]).strftime("%d-%b-%Y")
                material_rate_replace = f"{d}  {material_rate_replace[2]} {material_rate_replace[3]} {material_rate_replace[4]} {material_rate_replace[5]}"
                self._refreshMaterialRateData(
                    lookup_from_account=lookup_material_name_rate[0], lookup_from_material=lookup_material_name_rate[1], replace=material_rate_replace)

        lookup_shipping_address_rate_list = self._getShippingRateLookupListFromDF()
        for lookup_shipping_address_rate in lookup_shipping_address_rate_list:
            shipping_rate_replace = self.rateChartSerivce.getOnebyDateAccountNameMaterialShipping(
                date=lookup_shipping_address_rate[2],account_name=lookup_shipping_address_rate[0], material_name=lookup_shipping_address_rate[1])
            if len(shipping_rate_replace):

                d =datetime.fromordinal(shipping_rate_replace[1]).strftime("%d-%b-%Y")
                shipping_rate_replace = f"{d}  {shipping_rate_replace[2]} {shipping_rate_replace[3]} {shipping_rate_replace[4]} {shipping_rate_replace[5]}"
                self._refreshShippingAddressRateData(
                    lookup_from_account=lookup_shipping_address_rate[
                        0], lookup_from_shipping=lookup_shipping_address_rate[1], replace=shipping_rate_replace
                )

    def _refreshAccountNameData(self, lookup_from, replace):
        self.__data['lookup_account_name'] = np.where(
            self.__data['account_name'] == lookup_from, replace, self.__data['lookup_account_name'])
        # self.__data['lookup_account_name'] = self.__data['lookup_account_name'].replace({lookup_from:replace})

    def _refreshMaterialNameData(self, lookup_from, replace):
        print("print", lookup_from, replace)
        self.__data['lookup_material_name'] = np.where(
            self.__data["material_name"] == lookup_from, replace, self.__data['lookup_material_name'])

    def _refreshShippingAddressData(self, lookup_from, replace):
        self.__data['lookup_shipping_address'] = np.where(
            self.__data['shipping_address'] == lookup_from, replace, self.__data['lookup_shipping_address'])

    def _refreshMaterialRateData(self, lookup_from_account, lookup_from_material, replace):
        self.__data['lookup_material_name_rate'] = np.where((self.__data['lookup_account_name'] == lookup_from_account) &
                                                            (self.__data['lookup_material_name'] == lookup_from_material), replace, self.__data['lookup_material_name_rate'])

    def _refreshShippingAddressRateData(self, lookup_from_account, lookup_from_shipping, replace):
        self.__data['lookup_shipping_address_rate'] = np.where((self.__data['lookup_account_name'] == lookup_from_account) &
                                                               (self.__data['lookup_shipping_address'] == lookup_from_shipping), replace, self.__data['lookup_shipping_address_rate'])
        print('todo')

    def _getAccountLookupListFromDF(self):
        account_name_df = self.__data[self.__data['lookup_account_name'].eq(
            "")]
        lookup_account_list = account_name_df['account_name'].unique().tolist()
        return lookup_account_list

    def _getMaterialLookupListFromDF(self):
        material_name_df = self.__data[~self.__data['material_name'].eq("")]
        material_name_df = material_name_df[material_name_df['lookup_material_name'].eq(
            "")]
        lookup_material_list = material_name_df["material_name"].unique(
        ).tolist()
        return lookup_material_list

    def _getShippingAddressLookupListFromDF(self):
        shipping_address_df = self.__data[~self.__data['shipping_address'].eq(
            "")]
        shipping_address_df = shipping_address_df[shipping_address_df['lookup_shipping_address'].eq(
            "")]
        lookup_shipping_list = shipping_address_df["shipping_address"].unique(
        ).tolist()
        return lookup_shipping_list

    def _getMaterialRateLookupListFromDF(self):
        return self._getRateLookupListFromDF("material_name")

    def _getShippingRateLookupListFromDF(self):
        return self._getRateLookupListFromDF("shipping_address")

    def _getRateLookupListFromDF(self, arg):

        rate_df = self.__data[~self.__data[f'lookup_{arg}'].eq(
            "") & ~self.__data[f'lookup_account_name'].eq("")]
        rate_df = rate_df[rate_df[f'lookup_{arg}_rate'].eq(
            "")]
        rate_df = rate_df.drop_duplicates(
            subset=["lookup_account_name", f"lookup_{arg}"])
        rate_df = rate_df[["lookup_account_name", f"lookup_{arg}", "date"]]
        lookup_list = rate_df.values
        return lookup_list
