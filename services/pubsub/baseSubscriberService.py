from abc import ABC, abstractmethod


class BaseSubscriberService(ABC):
    @abstractmethod
    def next(self):
        pass