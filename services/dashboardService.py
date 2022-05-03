import random
import traceback
from db import getDb

from services.util import getorCreateAgentId


class DashboardService():
    def updateForLookupAccountOpAgent(self, id:int, lookup_id:str, account_name:str, op_cash:float, op_bank:float, agent_name:int):
        account_row = self.getOneBySalereceived(id=id)
        agent_id = getorCreateAgentId(agent_name=agent_name)
        con = getDb()
        db = con.cursor()
        try:
            op_cash = float(op_cash)
            op_bank = float(op_bank)
            if not account_row:
                raise Exception

            db.execute(f"""
                UPDATE account
                SET lookup_id = '{lookup_id}',
                    account_name = "{str(account_name).upper()}",
                    op_cash = {round(op_cash,2)},
                    op_bank = {round(op_bank,2)},
                    _op_total = {round(op_bank+ op_cash,2)},
                    _cl_cash = {round(op_cash+account_row[0]-account_row[2],2)},
                    _cl_bank = {round(op_bank+account_row[1]-account_row[3],2)},
                    _cl_total = {round(op_cash+account_row[0]-account_row[2]+op_bank+account_row[1]-account_row[3],2)},
                    id_agent = {agent_id}
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

    def updateForSaleReceiveCl(self, id, _cash_sale, _bank_sale,  _cash_received,  _bank_received, _cl_cash, _cl_bank):
        con = getDb()
        db = con.cursor()
        try:

            db.execute(f"""
                UPDATE account
                SET 
                    _cash_sale = {round(_cash_sale,2)},
                    _bank_sale = {round(_bank_sale,2)},
                    _cash_received = {round(_cash_received,2)},
                    _bank_received = {round(_bank_received,2)},
                    _cl_cash = {round(_cl_cash,2)},
                    _cl_bank = {round(_cl_bank,2)},
                    _cl_total = {round(_cl_cash+_cl_bank,2)}
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

    def delete(self, id):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                DELETE FROM account
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

    def getOneBySalereceived(self, id):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                SELECT _cash_sale, _bank_sale, _cash_received, _bank_received, id FROM account
                WHERE
                    id ={id}
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

    def getOne(self, id):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                SELECT id, op_cash, op_bank, _cash_sale, _bank_sale, _cash_received, _bank_received FROM account
                WHERE
                    id ={id}
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
    
    def create(self,lookup_id,account_name, op_cash, op_bank, agent_name):
        id = 0
        op_cash = float(op_cash)
        op_bank = float(op_bank)
        con = getDb()
        db = con.cursor()
        try:
            agentid = getorCreateAgentId(
                agent_name=str(agent_name))
            db.execute(
                f"""INSERT INTO account
                (lookup_id, account_name, id_agent, op_cash, op_bank, _op_total, _cl_cash, _cl_bank, _cl_total)
                    VALUES(
                        '{str(lookup_id)}',
                        '{str(account_name).upper()}',
                        {str(agentid)},
                        {str(round(op_cash,2))},
                        {str(round(op_bank,2))},
                        {str(round(op_cash+op_bank,2))},
                        {str(round(op_cash,2))},
                        {str(round(op_bank,2))},
                        {str(round(op_cash+op_bank,2))})""")
            id = db.lastrowid
        except:
            con.close()
            traceback.print_exc()
            return False
        con.commit()
        con.close()
        return id

    def getIdByAccountName(self, account_name):
        id = 0
        con = getDb()
        db = con.cursor()
       
        db.execute(
            f"""
            SELECT id FROM account
            WHERE
                account_name ='{str(account_name).upper()}'  COLLATE NOCASE
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

    def getOrCreateAccountId(self, account_name):
        id = self.getIdByAccountName(account_name=account_name)
        if not id:
            lookup_id = str(random.getrandbits(128))
            id = self.create(lookup_id=lookup_id,account_name=account_name,agent_name="",op_cash=0, op_bank=0)
            return id
        return id

    def getListOfIdLookupIDAccountName(self):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                SELECT id, lookup_id, account_name FROM account
                ORDER BY
                    account_name ASC
            """)
            row = db.fetchall()
        except:
            con.close()
            traceback.print_exc()
            return list()
        con.commit()
        con.close()
        return row

    def getListOfAccountName(self):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                SELECT account_name FROM account
                ORDER BY
                    account_name ASC
            """)
            row = db.fetchall()
        except:
            con.close()
            traceback.print_exc()
            return list()
        con.commit()
        con.close()
        return row