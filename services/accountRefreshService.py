from services.dashboardService import DashboardService
from services.rateChartService import RateChartService
from services.saleRegistorService import SaleRegistorService
from services.util import getMaterialShippingId
from datetime import datetime


class AccountRefreshService():
    def __init__(self) -> None:
        self.dashboardService = DashboardService()
        self.saleRegistorService = SaleRegistorService()
        self.rateChartService = RateChartService()

    def calculateClosingBySaleEntry(self, account_name):
        id_account_name = self.dashboardService.getIdByAccountName(
            account_name=account_name)
        # _sale_amount, _shipping_amount, cash_received, bank_received, bank_sale
        sale_row = self.saleRegistorService.getSumOfSaleShippingReceivedAmount(
            id_account=id_account_name)
        if(sale_row[0]):
            # print(sale_row)
            # id, op_cash, op_bank, _cash_sale, _bank_sale, _cash_received, _bank_received
            account_row = self.dashboardService.getOne(id=id_account_name)
            _cash_sale = sale_row[0] + sale_row[1] - sale_row[4]
            _bank_sale = sale_row[4]
            _cash_received = sale_row[2]
            _bank_received = sale_row[3]
            _cl_cash = account_row[1] + _cash_sale - _cash_received
            _cl_bank = account_row[2] + _bank_sale - _bank_received
            self.dashboardService.updateForSaleReceiveCl(id=id_account_name, _cash_sale=_cash_sale, _bank_sale=_bank_sale,
                                                        _cash_received=_cash_received,  _bank_received=_bank_received, _cl_cash=_cl_cash, _cl_bank=_cl_bank)


    def calculateAll(self):
        account_list = self.dashboardService.getListOfAccountName()
        for account_name in account_list:
            self.calculateClosingBySaleEntry(account_name=account_name[0])
        # self.calculateRateChange()

    def calculateRateChange(self, id, previous_date):
        # id, date_, account_name, material_name, unit_name, amount
        rate_row = self.rateChartService.getOne(id)
        # print(rate_row)
        # print(id)
        id_account_name = self.dashboardService.getIdByAccountName(
            account_name=rate_row[2])
        self._calculateMaterialRateChange(previous_date=previous_date,
            rate_row=rate_row, id_account_name=id_account_name)
        self._calculateShippingRateChange(previous_date=previous_date,
            rate_row=rate_row, id_account_name=id_account_name)
        self.calculateClosingBySaleEntry(account_name=rate_row[2])

        # if previous_date == rate_row[1]: #optimized later

    def _calculateMaterialRateChange(self,previous_date, rate_row, id_account_name):
        id_material = getMaterialShippingId(material_name=rate_row[3])
        sale_rows = self.saleRegistorService.getByIdDateAccountMaterialQtyRateUnit( id_account=id_account_name, id_material=id_material) # id, date_, account_name, material_name, qty_cft, qty_ton, m_rate,  m_unit
        for sale_row in sale_rows:
            _id_rate_material = 'NULL'
            _sale_amount = 0
            if len(sale_row[3]):
                rate_row = self.rateChartService.getOnebyDateAccountNameMaterialShipping(
                    date=datetime.fromordinal(sale_row[1]).strftime("%d-%b-%Y"), account_name=sale_row[2], material_name=sale_row[3])
                # id, date_, account_name, material_name, unit_name, amount 
                _id_rate_material = rate_row[0]

                _sale_amount = sale_row[5] * rate_row[5] if rate_row[4] == "TON" else sale_row[4] * \
                    rate_row[5] if rate_row[4] == "CFT" else rate_row[5]
                self.saleRegistorService.updateIdByMaterialSale(id=sale_row[0], _id_rate_material=_id_rate_material, _sale_amount=_sale_amount)
            



    def _calculateShippingRateChange(self,previous_date, rate_row, id_account_name):
        id_shipping = getMaterialShippingId(material_name=rate_row[3])
        sale_rows = self.saleRegistorService.getByIdDateAccountShippingQtyRateUnit(id_account=id_account_name, id_shipping=id_shipping) # id, date_, account_name, qty_cft, qty_ton, shipping_address, s_rate, s_unit
        for sale_row in sale_rows:
            _id_rate_shipping = 'NULL'
            _shipping_amount = 0
            # print(sale_row[3], type(sale_row[3]))
            if len(sale_row[3]):
                rate_row = self.rateChartService.getOnebyDateAccountNameMaterialShipping(
                    date=datetime.fromordinal(sale_row[1]).strftime("%d-%b-%Y"), account_name=sale_row[2], material_name=sale_row[3])
                # id, date_, account_name, material_name, unit_name, amount 
                _id_rate_shipping = rate_row[0]

                _shipping_amount = sale_row[5] * rate_row[5] if rate_row[4] == "TON" else sale_row[4] * \
                    rate_row[5] if rate_row[4] == "CFT" else rate_row[5]
                # print(_shipping_amount)
                # print(sale_row)
                self.saleRegistorService.updateIdByShippingSale(id=sale_row[0], _id_rate_shipping=_id_rate_shipping, _shipping_amount=_shipping_amount)

