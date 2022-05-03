# account:  lookup_id	account_name	agent_name
# sale: date_	challan_no	site	account_name	material	qty_cft	qty_ton	truck_no	transporter_name	shipping_address	cash_received	remarks	is_manual	m_material_unit	m_material_amount	m_transport_unit	m_transport_amount

# rate: date_	account_name	material	unit	amount


from datetime import datetime
import pandas
from db import getDb
from services.dashboardService import DashboardService
from services.parentService import ParentService
from services.rateChartService import RateChartService
from services.accountRefreshService import AccountRefreshService
from services.util import getMaterialShippingId, getUnitId, getorCreateAgentId, getorCreateSiteId
import traceback


class SaveToDb(ParentService):
    column_account = ["lookup_id", "account_name",
                      "agent_name", "op_bank", "op_cash"]
    column_sale = ['date', 'challan_no', 'site', 'account_name', 'material_name', 'qty_cft', 'qty_ton', 'truck_no', 'transporter_name', 'shipping_address', 'bank_sale','bank_received','cash_received', 'remarks', 'is_manual_material', 'is_manual_shipping',
                   'm_material_unit', 'm_material_amount', 'm_shipping_unit', 'm_shipping_amount', 'o_date', 'lookup_account_name', 'lookup_material_name', 'lookup_shipping_address', 'lookup_material_name_rate', 'lookup_shipping_address_rate']

    colomn_rate = ["date", "account_name", "material_name", "unit", "amount"]

    def __init__(self, data: pandas.DataFrame) -> None:
        self.data = data
        self.accountRefreshService = AccountRefreshService()

    def saleRegistor(self):
        if(not self.validateSaleRegistor or self.data["account_name"].isnull().sum() > 0):
            return False

        # accounts = self.data["lookup_account_name"].unique().tolist()
        # materials = self.data["lookup_material_name"].unique().tolist()
        # units = self.data["unit"].unique().tolist()

        # for unit in units:
        #     if not unit.upper() in ["TON", "CFT", "TRIP"]:
        #         return False, "pased unit name not exit"

        # for account_name in accounts:
        #     dashboardService = DashboardService()
        #     dashboardService.getOrCreateAccountId(account_name=account_name)
        # for material_name in materials:
        #     getMaterialShippingId(material_name=material_name)

        dashboardService = DashboardService()
        rateChartService = RateChartService()

        for i, row in self.data.iterrows():
            id_account = dashboardService.getOrCreateAccountId(
                account_name=str(row["lookup_account_name"]))
            id_material = 'NULL'
            if len(row["lookup_material_name"]):
                id_material = getMaterialShippingId(
                    material_name=str(row["lookup_material_name"]))

            _sale_amount = 0
            _id_rate_material = 'NULL'
            m_material_unit = 'NULL'
            if id_material != 'NULL' and not row["is_manual_material"]:
                rate_row = rateChartService.getOnebyDateAccountNameMaterialShipping(
                    date=row["date"], account_name=row["lookup_account_name"], material_name=row["lookup_material_name"])
                _id_rate_material = rate_row[0]

                _sale_amount = row["qty_ton"] * rate_row[5] if rate_row[4] == "TON" else row["qty_cft"] * \
                    rate_row[5] if rate_row[4] == "CFT" else rate_row[5]

            elif row["is_manual_material"]:
                _sale_amount = row["m_material_amount"]
                m_material_unit = getUnitId(unit_name="TON")
         

            id_site = getorCreateSiteId(row["site"])

            id_shipping_address = "NULL"
            if len(row["lookup_shipping_address"]):
                id_shipping_address = getMaterialShippingId(
                    material_name=str(row["lookup_shipping_address"]))

            _id_rate_shipping = "NULL"
            _shipping_amount = 0
            m_shipping_unit = 'NULL'
            if len(row["lookup_shipping_address"]) and not row["is_manual_shipping"]:
                rate_row = rateChartService.getOnebyDateAccountNameMaterialShipping(
                    date=row["date"], account_name=row["lookup_account_name"], material_name=row["lookup_shipping_address"])
                _id_rate_shipping = rate_row[0]

                _shipping_amount = row["qty_ton"] * rate_row[5] if rate_row[4] == "TON" else row["qty_cft"] * \
                    rate_row[5] if rate_row[4] == "CFT" else rate_row[5]

            elif row["is_manual_shipping"]:
                _shipping_amount = row["m_shipping_amount"]
                m_shipping_unit = getUnitId(unit_name="TRIP")

               

            _total_amount = _sale_amount + _shipping_amount
            print(row["date"])
            d = datetime.strptime(row["date"], "%d-%b-%Y")

            con = getDb()
            db = con.cursor()
            try:

                print(f"""
                INSERT INTO sale
                    (date_,
                    challan_no,
                    id_site,
                    id_account,
                    id_material,
                    qty_cft,
                    qty_ton,
                    truck_no,
                    transporter_name,
                    id_shipping_address,
                    remarks,
                    _id_rate_material,
                    _sale_amount,
                    _id_rate_shipping,
                    _shipping_amount,
                    _total_amount,
                    bank_sale,
                    bank_received,
                    cash_received,
                    is_manual_material,
                    _id_unit_material,
                    is_manual_shipping,
                    _id_unit_shipping
                     )
                VALUES(
                    {d.toordinal()},
                    '{row['challan_no']}',
                    {id_site},
                    {id_account},
                    {id_material},
                    {row["qty_cft"]},
                    {row["qty_ton"]},
                    '{row["truck_no"]}',
                    '{row["transporter_name"]}',
                    {id_shipping_address},
                    '{row["remarks"]}',
                    {_id_rate_material},
                    {_sale_amount},
                    {_id_rate_shipping},
                    {_shipping_amount},
                    {_total_amount},
                    {row["bank_sale"]},
                    {row["bank_received"]},
                    {row["cash_received"]},
                    {int(row["is_manual_material"])},
                    {m_material_unit},
                    {int(row["is_manual_shipping"])},
                    {m_shipping_unit}
                    )""")

                db.execute(f"""
                INSERT INTO sale
                    (date_,
                    challan_no,
                    id_site,
                    id_account,
                    id_material,
                    qty_cft,
                    qty_ton,
                    truck_no,
                    transporter_name,
                    id_shipping_address,
                    remarks,
                    _id_rate_material,
                    _sale_amount,
                    _id_rate_shipping,
                    _shipping_amount,
                    _total_amount,
                    bank_sale,
                    bank_received,
                    cash_received,
                    is_manual_material,
                    _id_unit_material,
                    is_manual_shipping,
                    _id_unit_shipping
                     )
                VALUES(
                    {d.toordinal()},
                    '{row['challan_no']}',
                    {id_site},
                    {id_account},
                    {id_material},
                    {row["qty_cft"]},
                    {row["qty_ton"]},
                    '{row["truck_no"]}',
                    '{row["transporter_name"]}',
                    {id_shipping_address},
                    '{row["remarks"]}',
                    {_id_rate_material},
                    {_sale_amount},
                    {_id_rate_shipping},
                    {_shipping_amount},
                    {_total_amount},
                    {row["bank_sale"]},
                    {row["bank_received"]},
                    {row["cash_received"]},
                    {int(row["is_manual_material"])},
                    {m_material_unit},
                    {int(row["is_manual_shipping"])},
                    {m_shipping_unit}
                    )""")
                
            except:
                con.close()
                traceback.print_exc()
                return False
            con.commit()
            con.close()
        list_of_account_name = self.data["lookup_account_name"].unique().tolist()
        for account_name in list_of_account_name:
            self.accountRefreshService.calculateClosingBySaleEntry(account_name=account_name)    
        return True

    def account(self):
        if(not self.validateAccount):
            return False
        agents = self.data["agent_name"].unique().tolist()

        for agent in agents:
            # if not pandas.isnull(agent):
            getorCreateAgentId(str(agent))

        for i, row in self.data.iterrows():
            agentid = getorCreateAgentId(
                agent_name=str(row["agent_name"]))
            con = getDb()
            db = con.cursor()
            try:
                db.execute(f"""
                INSERT INTO account
                    (lookup_id, account_name, id_agent, op_cash,
                     op_bank, _op_total, _cl_cash, _cl_bank, _cl_total)
                VALUES(
                    '{str(row['lookup_id'])}',
                    '{str(row['account_name']).upper()}',
                    {str(agentid)},
                    {str(round(row['op_cash'],2))},
                    {str(round(row['op_bank'],2))},
                    {str(round(row['op_cash']+row['op_bank'],2))},
                    {str(round(row['op_cash'],2))},
                    {str(round(row['op_bank'],2))},
                    {str(round(row['op_cash']+row['op_bank'],2))}
                    )""")
            except:
                con.close()
                traceback.print_exc()
                return False
            con.commit()
            con.close()
        return True

    def rateChart(self):
        if(not self.validateRateChart or self.data.isnull().sum().sum() > 0):
            return False

        accounts = self.data["account_name"].unique().tolist()
        materials = self.data["material_name"].unique().tolist()
        units = self.data["unit"].unique().tolist()

        for unit in units:
            if not unit.upper() in ["TON", "CFT", "TRIP"]:
                return False, "pased unit name not exit"

        for account_name in accounts:
            dashboardService = DashboardService()
            dashboardService.getOrCreateAccountId(account_name=account_name)
        for material_name in materials:
            getMaterialShippingId(material_name=material_name)

        for i, row in self.data.iterrows():
            id_account = dashboardService.getOrCreateAccountId(
                account_name=str(row["account_name"]))
            id_material = getMaterialShippingId(
                material_name=str(row["material_name"]))
            id_unit = getUnitId(unit_name=str(row["unit"]).upper())
            con = getDb()
            db = con.cursor()
            d = datetime.strptime(row["date"], "%d-%b-%Y")
            try:

                db.execute(f"""
                INSERT INTO rate
                    (date_, id_account, id_material, id_unit, amount)
                VALUES(
                    {d.toordinal()},
                    {id_account},
                    {id_material},
                    {id_unit},
                    {row["amount"]}
                    )""")
            except:
                con.close()
                traceback.print_exc()
                return False
            con.commit()
            con.close()
        return True

    def validateSaleRegistor(self):
        if self.data["op_bank","op_cash","lookup_id","account_name"].isnull().sum() > 0:
            return 0
        return (self.data.columns.to_list() == self.column_sale)

    def validateAccount(self):
        return (self.data.columns.to_list() == self.column_account)

    def validateRateChart(self):
        return (self.data.columns.to_list() == self.colomn_rate)
