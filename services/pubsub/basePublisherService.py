from abc import ABC, abstractmethod

from pandas import array

from services.pubsub.baseSubscriberService import BaseSubscriberService


class BasePublisherSercive(ABC):
    subscriber = array()
    @abstractmethod
    def subscribe(self, subs:BaseSubscriberService):
        pass
