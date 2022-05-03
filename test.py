
from services.saleRegistorService import SaleRegistorService


saleRegistorService = SaleRegistorService()

rows = saleRegistorService.getForLayout()

print(rows[1])