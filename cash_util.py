from pydantic import BaseModel
from libfptr10 import IFptr
from models import Receipt
from dotenv import load_dotenv
import os

load_dotenv()
CASH_USER = os.getenv('CASH_USER')
CASH_USER_INN= os.getenv('CASH_USER_INN')
CASH_IP = os.getenv('CASH_IP')

def create_receipt(receipt:Receipt):
    price = 0.0
    for good in receipt.goods:
        price += good.good_price * good.good_quantity
    receipt.price = price
    if receipt.is_part:
        print("Чек на частичную оплату")
        if print_part_receipt(receipt):
            print("Чек на частичную оплату УСПЕШНО РАСПЕЧАТАН")
            return True
        else:
            print("ОШИБКА ПЕЧАТИ ЧЕКА")
            return False
        #здесь логика печати чека на частичную оплату
    else:
        print("Печатаем обычный чек прихода" if not receipt.is_return else "Печатаем обычный чек возврата")
        if print_simple_receipt(receipt):
            print("Чек УСПЕШНО РАСПЕЧАТАН")
            return True
        else:
            print("ОШИБКА ПЕЧАТИ ЧЕКА")
            return False

def print_part_receipt(receipt:Receipt) -> bool:
    if receipt.price_cash + receipt.price_card != receipt.price:
        return False
    try:
        
        fptr = IFptr("", "KKT1")

        settings = {
            IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_22F,
            IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_TCPIP,
            IFptr.LIBFPTR_SETTING_IPADDRESS: CASH_IP,
            IFptr.LIBFPTR_SETTING_IPPORT: "5555"
        }
        fptr.setSettings(settings)

        fptr.open()

        fptr.setParam(1021, CASH_USER)
        fptr.setParam(1203, CASH_USER_INN)
        fptr.operatorLogin()

        if receipt.is_return: # если чек на возврат
            fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL_RETURN)
        else:
            fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)
        fptr.openReceipt()

        for good in receipt.goods: # заполняем позиции в чеке
            
            fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, good.good_name) # Good
            fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, good.good_quantity)
            fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, good.good_price)
            fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_NO)
            fptr.registration()
        
        if receipt.price_card > 0:
            type_pay = IFptr.LIBFPTR_PT_CASH
            sum_pay = receipt.price_card
            
        
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, type_pay) #Тип оплаты
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sum_pay)
        fptr.payment()

        if receipt.price_cash > 0:
            type_pay = IFptr.LIBFPTR_PT_ELECTRONICALLY
            sum_pay = receipt.price_cash
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, type_pay) #Тип оплаты
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sum_pay)
        fptr.payment()
        
        
        fptr.receiptTotal()

        fptr.closeReceipt()

        fptr.close()
        return True
    except Exception as e:
        print(e)
        return False


def print_simple_receipt(receipt:Receipt) -> bool:
    try:
        
        fptr = IFptr("", "KKT1")

        settings = {
            IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_22F,
            IFptr.LIBFPTR_SETTING_PORT: IFptr.LIBFPTR_PORT_TCPIP,
            IFptr.LIBFPTR_SETTING_IPADDRESS: CASH_IP,
            IFptr.LIBFPTR_SETTING_IPPORT: "5555"
        }
        fptr.setSettings(settings)

        fptr.open()

        fptr.setParam(1021, CASH_USER)
        fptr.setParam(1203, CASH_USER_INN)
        fptr.operatorLogin()

        if receipt.is_return: # если чек на возврат
            fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL_RETURN)
        else:
            fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)
        fptr.openReceipt()

        for good in receipt.goods: # заполняем позиции в чеке
            
            fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, good.good_name) # Good
            fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, good.good_quantity)
            fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, good.good_price)
            fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_NO)
            fptr.registration()
        
        if receipt.is_cash:
            type_pay = IFptr.LIBFPTR_PT_CASH
            sum_pay = receipt.price_cash
        else:
            type_pay = IFptr.LIBFPTR_PT_ELECTRONICALLY
            sum_pay = receipt.price_card

        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, type_pay) #Тип оплаты
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sum_pay)
        fptr.payment()

        fptr.receiptTotal()

        fptr.closeReceipt()

        fptr.close()
        return True
    except Exception as e:
        print(e)
        return False