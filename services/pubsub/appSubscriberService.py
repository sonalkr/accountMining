

class AppSubscriberService():
    def __init__(self, rootApp) -> None:
        self.sub = rootApp

    def next(self, time_stamp: str, title: str, msg: str, level: int):
        self.sub.notificationListener(
            time_stamp=time_stamp, title=title, msg=msg, level=level)
