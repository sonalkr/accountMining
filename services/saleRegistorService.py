from functools import partial
from itertools import chain
from operator import is_not
import traceback
from db import getDb, getDbWithDictionary


class SaleRegistorService():


    def update(self):
        pass
    
    def delete(self):
        pass


    def insert(self):
        pass

    def getSumOfSaleShippingReceivedAmount(self, id_account):
        con = getDb()
        db = con.cursor()
        try:
            # rate.id, date_, account_name, material_name, unit_name, amount
            db.execute(f"""
                SELECT  SUM(_sale_amount), SUM(_shipping_amount), SUM(cash_received), SUM(bank_received), SUM(bank_sale) FROM sale
                WHERE
                    id_account = {id_account}
            """)
            rows = db.fetchone()
            # print(rows[0])
        except:
            con.close()
            traceback.print_exc()
            return list() 
        con.commit()
        con.close()
        return rows

    def getForLayout(self):
        con = getDb()
        db = con.cursor()
        try:
            # rate.id, date_, account_name, material_name, unit_name, amount
            db.execute(f"""
                SELECT sa.id, sa.date_, si.site_name, a.account_name, m.material_name, sa.qty_cft, sa.qty_ton, sa.truck_no, sa.transporter_name, sh.material_name as shipping_address, sa._sale_amount, sa._shipping_amount, sa._total_amount, sa.bank_sale, sa.bank_received, sa.cash_received, rm.amount as m_rate, um.unit_name as m_unit, rs.amount as s_rate, us.unit_name as s_unit FROM sale sa
                LEFT JOIN account a
                    ON sa.id_account = a.id
                LEFT JOIN site_ si
                    ON sa.id_site = si.id
                LEFT JOIN material m
                    ON sa.id_material = m.id
                LEFT JOIN material sh
                    ON sa.id_shipping_address = sh.id
                LEFT JOIN rate rm
                    ON sa._id_rate_material = rm.id
                LEFT JOIN rate rs
                    ON sa._id_rate_shipping = rs.id
                LEFT JOIN unit um
                    ON rm.id_unit = um.id
                LEFT JOIN unit us
                    ON rs.id_unit = us.id
            """)
            rows = db.fetchall()
            col = db.description
            col = list(chain.from_iterable(col))
            col = list(filter(partial(is_not,None), col))
            # print(rows[0])
        except:
            con.close()
            traceback.print_exc()
            return list(), list()
        con.commit()
        con.close()
        return rows, col

    def getForLayoutIdAccount(self, id_account_name):
        con = getDb()
        db = con.cursor()
        try:
            # rate.id, date_, account_name, material_name, unit_name, amount
            db.execute(f"""
                SELECT sa.id, sa.date_, si.site_name, a.account_name, m.material_name, sa.qty_cft, sa.qty_ton, sa.truck_no, sa.transporter_name, sh.material_name as shipping_address, sa._sale_amount, sa._shipping_amount, sa._total_amount, sa.bank_sale, sa.bank_received, sa.cash_received, rm.amount as m_rate, um.unit_name as m_unit, rs.amount as s_rate, us.unit_name as s_unit FROM sale sa
                LEFT JOIN account a
                    ON sa.id_account = a.id
                LEFT JOIN site_ si
                    ON sa.id_site = si.id
                LEFT JOIN material m
                    ON sa.id_material = m.id
                LEFT JOIN material sh
                    ON sa.id_shipping_address = sh.id
                LEFT JOIN rate rm
                    ON sa._id_rate_material = rm.id
                LEFT JOIN rate rs
                    ON sa._id_rate_shipping = rs.id
                LEFT JOIN unit um
                    ON rm.id_unit = um.id
                LEFT JOIN unit us
                    ON rs.id_unit = us.id
                WHERE
                    sa.id_account = {id_account_name}
            """)
            rows = db.fetchall()
            col = db.description
            col = list(chain.from_iterable(col))
            col = list(filter(partial(is_not,None), col))
            # print(rows[0])
        except:
            con.close()
            traceback.print_exc()
            return list(), list()
        con.commit()
        con.close()
        return rows, col


    def delete(self, id):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                DELETE FROM sale
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


    # def getByIdDateAccountMaterialQtyRateUnit(self,from_date, to_date, id_account, id_material):
    #     con = getDb()
    #     db = con.cursor()
    #     try:
    #         # rate.id, date_, account_name, material_name, unit_name, amount
    #         db.execute(f"""
    #             SELECT sa.id, sa.date_, a.account_name, m.material_name, sa.qty_cft, sa.qty_ton, rm.amount as m_rate, um.unit_name as m_unit FROM sale sa
    #             LEFT JOIN account a
    #                 ON sa.id_account = a.id
    #             LEFT JOIN material m
    #                 ON sa.id_material = m.id
    #             LEFT JOIN rate rm
    #                 ON sa._id_rate_material = rm.id
    #             LEFT JOIN unit um
    #                 ON rm.id_unit = um.id
    #             WHERE
    #                 sa.date_ >= {from_date} and
    #                 sa.date_ <= {to_date} and
    #                 sa.id_account = {id_account} and
    #                 sa.id_material = {id_material}

    #         """)
    #         rows = db.fetchall()
    #     except:
    #         con.close()
    #         traceback.print_exc()
    #         return list()
    #     con.commit()
    #     con.close()
    #     return rows

    # def getByIdDateAccountShippingQtyRateUnit(self,from_date, to_date, id_account, id_shipping):
    #     con = getDb()
    #     db = con.cursor()
    #     try:
    #         # rate.id, date_, account_name, material_name, unit_name, amount
    #         db.execute(f"""
    #             SELECT sa.id, sa.date_, a.account_name, sa.qty_cft, sa.qty_ton, sh.material_name as shipping_address, rs.amount as s_rate, us.unit_name as s_unit FROM sale sa
    #             LEFT JOIN account a
    #                 ON sa.id_account = a.id
    #             LEFT JOIN material sh
    #                 ON sa.id_shipping_address = sh.id
    #             LEFT JOIN rate rm
    #                 ON sa._id_rate_shipping = rs.id
    #             LEFT JOIN unit us
    #                 ON rs.id_unit = us.id
    #             WHERE
    #                 sa.date_ >= {from_date} and
    #                 sa.date_ <= {to_date} and
    #                 sa.id_account = {id_account} and
    #                 sa.id_shipping_address = {id_shipping}

    #         """)
    #         rows = db.fetchall()
    #     except:
    #         con.close()
    #         traceback.print_exc()
    #         return list()
    #     con.commit()
    #     con.close()
    #     return rows

    def getByIdDateAccountMaterialQtyRateUnit(self, id_material, id_account):
        con = getDb()
        db = con.cursor()
        try:
            # rate.id, date_, account_name, material_name, unit_name, amount
            print(f"""
                SELECT sa.id, sa.date_, a.account_name, m.material_name, sa.qty_cft, sa.qty_ton, rm.amount as m_rate, um.unit_name as m_unit FROM sale sa
                LEFT JOIN account a
                    ON sa.id_account = a.id
                LEFT JOIN material m
                    ON sa.id_material = m.id
                LEFT JOIN rate rm
                    ON sa._id_rate_material = rm.id
                LEFT JOIN unit um
                    ON rm.id_unit = um.id
                WHERE
                    sa.id_account = {id_account} and
                    sa.id_material = {id_material}

            """)
            db.execute(f"""
                SELECT sa.id, sa.date_, a.account_name, m.material_name, sa.qty_cft, sa.qty_ton, rm.amount as m_rate, um.unit_name as m_unit FROM sale sa
                LEFT JOIN account a
                    ON sa.id_account = a.id
                LEFT JOIN material m
                    ON sa.id_material = m.id
                LEFT JOIN rate rm
                    ON sa._id_rate_material = rm.id
                LEFT JOIN unit um
                    ON rm.id_unit = um.id
                WHERE
                    sa.id_account = {id_account} and
                    sa.id_material = {id_material}

            """)
            rows = db.fetchall()
        except:
            con.close()
            traceback.print_exc()
            return list()
        con.commit()
        con.close()
        return rows

    def getByIdDateAccountShippingQtyRateUnit(self, id_shipping, id_account):
        con = getDb()
        db = con.cursor()
        try:
            # rate.id, date_, account_name, material_name, unit_name, amount
            db.execute(f"""
                SELECT sa.id, sa.date_, a.account_name, sh.material_name as shipping_address, sa.qty_cft, sa.qty_ton, rs.amount as s_rate, us.unit_name as s_unit FROM sale sa
                LEFT JOIN account a
                    ON sa.id_account = a.id
                LEFT JOIN material sh
                    ON sa.id_shipping_address = sh.id
                LEFT JOIN rate rs
                    ON sa._id_rate_shipping = rs.id
                LEFT JOIN unit us
                    ON rs.id_unit = us.id
                WHERE
                    sa.id_account = {id_account} and
                    sa.id_shipping_address = {id_shipping}

            """)
            rows = db.fetchall()
            print(rows)
        except:
            con.close()
            traceback.print_exc()
            return list()
        con.commit()
        con.close()
        return rows

    def updateIdByMaterialSale(self, id, _id_rate_material, _sale_amount):
        con = getDb()
        db = con.cursor()
        try:

            db.execute(
                f"""
                UPDATE sale
                    SET _id_rate_material = {_id_rate_material},
                        _sale_amount = {_sale_amount}
                    WHERE
                        id ={id}
                    -- LIMIT 1
            """)
        except:
            con.close()
            traceback.print_exc()
        con.commit()
        con.close()
        return id

    def updateIdByShippingSale(self, id, _id_rate_shipping, _shipping_amount):
        con = getDb()
        db = con.cursor()
        try:

            db.execute(
                f"""
                UPDATE sale
                    SET _id_rate_shipping = {_id_rate_shipping},
                        _shipping_amount = {_shipping_amount}
                    WHERE
                        id ={id}
                    -- LIMIT 1
            """)
        except:
            con.close()
            traceback.print_exc()
        con.commit()
        con.close()
        return id

    def getCountOfSale(self):
        con = getDb()
        db = con.cursor()
        try:
            db.execute(f"""
                SELECT COUNT(id) FROM material
            """)
            row = db.fetchone()[0]
        except:
            con.close()
            traceback.print_exc()
            return list()
        con.commit()
        con.close()
        return row

    def getMaterialPivot(self, id_account):
        con = getDb()
        db = con.cursor()
        try:
            # rate.id, date_, account_name, material_name, unit_name, amount
            db.execute(f"""
                SELECT m.material_name as material_name, SUM(qty_cft) as qty_cft, SUM(qty_ton) as qty_ton, SUM(_sale_amount) as material_amount , SUM(_shipping_amount) as shipping_amount FROM sale sa
                LEFT JOIN material m
                    ON sa.id_material = m.id
                WHERE
                    sa.id_account = {id_account}
                GROUP BY
                    m.material_name
            """)
            rows = db.fetchall()
            col = db.description
            col = list(chain.from_iterable(col))
            col = list(filter(partial(is_not,None), col))
            # print(rows[0])
        except:
            con.close()
            traceback.print_exc()
            return list(), list()
        con.commit()
        con.close()
        return rows, col