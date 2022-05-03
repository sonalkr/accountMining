import tkinter as tk
from tkinter import ttk
from gui.baseApp import BaseApp
from gui.layouts.dashboardLayout import DashboardLayout
from gui.layouts.partyLayout import PartyLayout
from gui.layouts.rateChartLayout import RateChartLayout
from gui.layouts.saleRegistorLayout import SaleRegistorLayout

from gui.upload import Upload
from services.accountRefreshService import AccountRefreshService
from services.pubsub.appSubscriberService import AppSubscriberService


class App(BaseApp):
    def __init__(self) -> None:
        super().__init__(AppSubscriberService(self))
        self.root = tk.Tk()
        self.root.title("sale book")
        self.dashboarFrame = tk.Frame()
        self.rateChartFrame = tk.Frame()
        self.saleRegistorFrame = tk.Frame()
        self.partyFrames = [tk.Frame()]
        self.account_name = None
        self.accountRefreshService = AccountRefreshService()

    def getMenuBar(self):
        # upload = Upload(rootApp=self)
        upload = Upload(self)
        menubar = tk.Menu(self.root)
        file = tk.Menu(menubar)
        file.add_command(label="New")
        file.add_command(label="Open")
        file.add_command(label="Save")
        file.add_command(label="Save as")
        file.add_separator()
        file.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file)

        edit = tk.Menu(menubar, tearoff=0)
        edit.add_command(label="Undo")
        edit.add_separator()
        edit.add_command(label="Cut")
        edit.add_command(label="Copy")
        edit.add_command(label="Paste")
        menubar.add_cascade(label="Edit", menu=edit)

        data_menu = tk.Menu(menubar, tearoff=0)
        import_menu = tk.Menu(data_menu, tearoff=0)
        import_menu.add_command(
            label="sale registor", command=lambda: upload.run(save_to="sale registor"))
        import_menu.add_command(
            label="account", command=lambda: upload.run(save_to="account"))
        import_menu.add_command(
            label="rate", command=lambda: upload.run(save_to="rate"))
        data_menu.add_cascade(label="Import", menu=import_menu)

        sample_menu = tk.Menu(data_menu, tearoff=0)
        sample_menu.add_command(label="sale registor download sample")
        sample_menu.add_command(label="account download sample")
        sample_menu.add_command(label="rate download sample")
        data_menu.add_cascade(label="Download Sample", menu=sample_menu)

        export_menu = tk.Menu(data_menu, tearoff=0)
        export_menu.add_command(label="sale registor")
        export_menu.add_command(label="account")
        export_menu.add_command(label="rate")
        data_menu.add_cascade(label="Export", menu=export_menu)

        menubar.add_cascade(label="Data", menu=data_menu)

        help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help)
        self.root.config(menu=menubar)

    def getToolBar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        b1 = tk.Button(
            toolbar,
            relief=tk.FLAT,
            compound=tk.LEFT,
            text="undo",
            # command=callback,
            # image=imgs["notepad"]
        )
        b1.pack(side=tk.LEFT, padx=0, pady=0)

        b2 = tk.Button(
            toolbar,
            text="redo",
            compound=tk.LEFT,
            # command=callback,
            relief=tk.FLAT,
            # image=imgs["github"]
        )
        b2.pack(side=tk.LEFT, padx=0, pady=0)

        b2 = tk.Button(
            toolbar, text="upload",
            compound=tk.LEFT,
            command=lambda: self.upload.run(root=self.root),
            relief=tk.FLAT,
            # image=imgs["plus"]
        )
        b2.pack(side=tk.LEFT, padx=0, pady=0)

    def run(self):
        self.root.minsize(900, 600)
        self.tabControl = ttk.Notebook(self.root)
        self.getMenuBar()
        # self.getToolBar(root=root)
        self.accountRefreshService.calculateAll()
        self.dashboard_root = ttk.Frame(self.tabControl)
        self.rate_chart_root = ttk.Frame(self.tabControl)
        self.sale_registor_root = ttk.Frame(self.tabControl)
        self.party_root = ttk.Frame(self.tabControl)

        self.tabControl.add(self.dashboard_root, text='DASHBOARD')
        self.tabControl.add(self.rate_chart_root, text='RATE CHART')
        self.tabControl.add(self.sale_registor_root, text='SALE REGISTOR')
        self.tabControl.add(self.party_root, text='PARTY')
        self.tabControl.pack(expand=1, fill="both")
        
        self.updateDashboardLayout()
        self.updateRateChartLayout()
        self.updateSaleRegistorLayout()
        self.updatePratyLayout()


        self.root.mainloop()

    def updateDashboardLayout(self):
        for child in self.dashboarFrame.winfo_children():
            child.destroy()
        self.dashboarFrame.destroy()
        dashboard = DashboardLayout(rootApp=self, root=self.dashboard_root)
        self.dashboarFrame = dashboard.getFrame()

    def updateRateChartLayout(self):
        
        for child in self.rateChartFrame.winfo_children():
            child.destroy()
        self.rateChartFrame.destroy()
        rate_chart = RateChartLayout(rootApp=self, root=self.rate_chart_root)
        self.rateChartFrame = rate_chart.getFrame()

    def updateSaleRegistorLayout(self):
        for child in self.saleRegistorFrame.winfo_children():
            child.destroy()
        self.saleRegistorFrame.destroy()
        sale_registor = SaleRegistorLayout(rootApp=self, root=self.sale_registor_root)
        self.saleRegistorFrame = sale_registor.getFrame()

    def updatePratyLayout(self):
        for _frame in self.partyFrames:
            for child in _frame.winfo_children():
                child.destroy()
            _frame.destroy()
        party = PartyLayout(rootApp=self, root=self.party_root,account_name=self.account_name)
        self.partyFrames = party.getFrame()

    def updateAllLayout(self):
        self.updateDashboardLayout()
        self.updateRateChartLayout()
        self.updateSaleRegistorLayout()

    def notificationListener(self,time_stamp:str, title: str, msg: str, level: int):
        print("time_stamp", time_stamp)
        print("title :", title)
        print("msg   :", msg)
        print("level :", level)

    def selectPartyTab(self, account_name):
        self.account_name = account_name
        self.tabControl.select(3)
        self.updatePratyLayout()