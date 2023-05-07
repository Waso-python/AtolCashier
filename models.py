from pydantic import BaseModel
from libfptr10 import IFptr

class Goods(BaseModel):
    good_name: str
    good_price: float
    good_quantity: int

class Receipt(BaseModel):
    is_return: bool = False #чек на возврат
    is_part: bool = False #частичная оплата
    is_cash: bool = True #оплата наличными
    goods: list[Goods] #список товаров
    price: float = 0 #цена товара
    price_cash: float #сумма наличными
    price_card: float = 0 #сумма безналичными
    
    
