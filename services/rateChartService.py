from datetime import datetime
import traceback
from db import getDb
from services.dashboardService import DashboardService

from services.util import getMaterialShippingId, getUnitId, getorCreateAgentId, getorCreateMaterialShippingId


class RateChartService():
    def __init__(self) -> None:
        self.dashboardService = DashboardService()

    def update(self, id:int, date:str, account_name:str, material_name:str, unit_name:str, amount:float):
        # not to change account name and material it will brock the sale report
        # id_account = self.dashboardService.getIdByAccountName(account_name=account_name)
        # id_material = getorCreateMaterialShippingId(material_name=material_name)
        id_unit = getUnitId(unit_name=unit_name)
        con = getDb()
        db = con.cursor()
        # print(id_account)
        d = datetime.strptime(date, "%d-%b-%Y")
        try:
            # if not id_account or not id_material or not id_unit:
            #     raise Exception
            db.execute(f"""
                UPDATE rate
                SET date_ = {d.toordinal()},
                    id_unit = {id_unit},
                    amount = {amount}
                WHERE
                    id ={id}
                -- LIMIT 1
            """)
            
        except:
            con.close()
            traceback.print_exc()
            return False
        con.commit() 
        con.close()
        return id

    def delete(self, id):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                DELETE FROM rate
                WHERE
                    id ={id}
                -- LIMIT 1
            """)
        except:
            con.close()
            traceback.print_exc()
            return False
        con.commit()
        con.close()
        return True

    def getall(self):
        con = getDb()
        db = con.cursor()
        try:
            # rate.id, date_, account_name, material_name, unit_name, amount
            db.execute(f"""
                SELECT r.id, date_, account_name, material_name, unit_name, amount FROM rate r
                    LEFT OUTER JOIN account a
                    ON r.id_account = a.id
                    LEFT OUTER JOIN material m
                    ON r.id_material = m.id
                    LEFT OUTER JOIN unit u
                    ON r.id_unit = u.id
                ORDER BY
                    a.account_name ASC
            """)
            rows = db.fetchall()
            # print(rows[0])
        except:
            con.close()
            traceback.print_exc()
            return False
        con.commit()
        con.close()
        return rows

    def getOne(self, id):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                SELECT rate.id, date_, account_name, material_name, unit_name, amount
                FROM rate
                    LEFT OUTER JOIN account
                    ON rate.id_account = account.id
                    LEFT OUTER JOIN material
                    ON rate.id_material = material.id
                    LEFT OUTER JOIN unit
                    ON rate.id_unit = unit.id
                WHERE
                    rate.id ={id}
                -- LIMIT 1
            """)
            row = db.fetchone()
        except:
            con.close()
            traceback.print_exc()
            return False
        con.commit()
        con.close()
        return row
    
    def create(self,date,account_name, material_name, unit_name, amount):
        id_account = self.dashboardService.getOrCreateAccountId(account_name=account_name)
        id_material = getorCreateMaterialShippingId(material_name=material_name)
        id_unit = getUnitId(unit_name=str(unit_name).upper())
        con = getDb()
        db = con.cursor()
        print(date)
        d = datetime.strptime(date, "%d-%b-%Y")
        id = 0

        try:
            if not id_account and not id_material and not id_unit:
                raise Exception

            db.execute(f"""INSERT INTO rate
                (date_, id_account, id_material, id_unit, amount)
                    VALUES(
                        {d.toordinal()},
                        {id_account},
                        {id_material},
                        {id_unit},
                        {amount})""")
            id = db.lastrowid
        except:
            con.close()
            traceback.print_exc()
            return False 
        con.commit() 
        con.close()
        return id

    def getIdByAccountNameandMaterialName(self, account_name, material_name):
        id = 0
        con = getDb()
        db = con.cursor()
        id_account = self.dashboardService.getIdByAccountName(account_name=account_name)
        id_material = getMaterialShippingId(material_name=material_name)
         
        db.execute(
            f"""
            SELECT id FROM rate
            WHERE
                id_account = {id_account} and
                id_material = {id_material}
            -- LIMIT 1
        """)
        row = db.fetchone()
        if (row == None):
            con.close()
            return 0
        id = row[0]
        con.commit()
        con.close()
        return id

    def verifyRateLookup(self, account_name, material_name):
        con = getDb()
        db = con.cursor()
        id_account = self.dashboardService.getIdByAccountName(account_name=account_name)
        id_material = getMaterialShippingId(material_name=material_name)
         
        db.execute(f"""
                SELECT r.id, date_, account_name, material_name, unit_name, amount FROM rate r
                LEFT OUTER JOIN account a
                    ON r.id_account = a.id
                LEFT OUTER JOIN material m
                    ON r.id_material = m.id
                LEFT OUTER JOIN unit u
                    ON r.id_unit = u.id
                WHERE
                    id_account = {id_account} and
                    id_material = {id_material}
            -- LIMIT 1
        """)
        row = db.fetchone()
        # print(row)
        if (row == None):
            con.close()
            return ""
        con.commit()
        con.close()
        row = f"{row[1]} {row[2]} {row[3]} {row[4]} {row[5]}"
        return row

    def getOnebyDateAccountNameMaterialShipping(self, date, account_name, material_name):
        con = getDb()
        db = con.cursor()
        id_account = self.dashboardService.getIdByAccountName(account_name=account_name)
        id_material = getMaterialShippingId(material_name=material_name)
        date = datetime.strptime(date, "%d-%b-%Y").toordinal()
        
        db.execute(f"""
                SELECT r.id, date_, account_name, material_name, unit_name, amount FROM rate r
                LEFT OUTER JOIN account a
                    ON r.id_account = a.id
                LEFT OUTER JOIN material m
                    ON r.id_material = m.id
                LEFT OUTER JOIN unit u
                    ON r.id_unit = u.id
                WHERE
                    id_account = {id_account} and
                    id_material = {id_material} and
                    date_ <= {date}
                ORDER BY
                    date_ DESC
            -- LIMIT 1
        """)
        row = db.fetchone()
        # print(row)
        if (row == None):
            con.close()
            return list()
        con.commit()
        con.close()
        return row