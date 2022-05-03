from abc import ABC, abstractmethod


class BaseLayout(ABC):

    @abstractmethod
    def _getToolBar():
        pass

    @abstractmethod
    def getFrame(self):
        pass


    @abstractmethod
    def _selectRecord(self):
        pass

    @abstractmethod
    def _createUpdateFrame(self):
        pass

    @abstractmethod
    def _updateRecord(self):
        pass

    @abstractmethod
    def _deleteRecord(self):
        pass

    @abstractmethod
    def _createCreateFrame(self):
        pass

    @abstractmethod
    def _createRecord(self):
        pass

    @abstractmethod
    def _destory(self):
        pass
    
    @abstractmethod
    def _navigateToPartyLedger(self,e):
        pass
