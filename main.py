from db import getDb
from models.dbInit import dbInit
from gui.app import App



dbInit()
# # test()


app = App()

app.run()
