
from abc import ABC, abstractmethod

from services.pubsub.appSubscriberService import AppSubscriberService
    

class BaseApp(ABC):
    def __init__(self,logger:AppSubscriberService) -> None:
        self.logger = logger
    @abstractmethod
    def getMenuBar(self):
        pass

    @abstractmethod
    def getToolBar(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def updateDashboardLayout(self):
        pass

    @abstractmethod
    def updateRateChartLayout(self):
        pass
    
    @abstractmethod
    def updateSaleRegistorLayout(self):
        pass
    
    @abstractmethod
    def updateAllLayout(self):
        pass

    @abstractmethod
    def notificationListener(self, time_stamp: str, title: str, msg: str, level: int):
        pass

    @abstractmethod
    def selectPartyTab(self, account_name):
        pass