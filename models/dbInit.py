from db import getDb
import os

app_path = os.path.dirname(os.path.abspath(__file__))


def dbInit():
    con = getDb()
    table_list = ["agent", "unit", "material",
                  "account", "rate", "site", "sale", "lookupTableMaterial","lookupTableAccount", "logs"]
    db = con.cursor()
    for i in range(len(table_list)):
        file_location = 'sql/' + table_list[i] + '.sql'
        f = open(os.path.join(app_path, file_location), 'r')
        content = f.read()
        # print(table_list[i])
        db.execute(content)
    con.commit()

    db.execute("""
        INSERT OR IGNORE INTO unit (unit_name) VALUES('TON'), ('CFT'), ('TRIP')
    """)
    con.commit()
    con.close()
