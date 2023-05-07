import os
from libfptr10 import IFptr
from datetime import datetime
from dotenv import load_dotenv
from models import Receipt
from cash_util import create_receipt

# инициализация объекта драйвера
# DRIVER_PATH = os.path.join(os.getcwd(), 'fptr10.dll')
# fptr = IFptr(DRIVER_PATH)
load_dotenv()
CASH_IP = os.getenv('CASH_IP')

def check_auth(secret:str) -> bool:
    '''Проверка на соответствие переданного в запросе параметра secret переменной окружения SECRET
    !!! ПЕРЕДЕЛАТЬ НА НОРМАЛЬНУЮ АВТОРИЗАЦИЮ'''
    SEC = os.getenv('SECRET')
    if SEC and SEC == secret:
        return True
    else:
        return False

def print_receipt(receipt:dict) -> dict:
    '''Функция, которая вызывает процедкру печати чека, передавая полученный запрос'''
    rec_body = Receipt(**receipt)
    if receipt and rec_body and check_auth(receipt['secret']):
        return {"result":"success","response":rec_body.dict()} if create_receipt(rec_body) else {"result":"error"}
    else:
        return {"result":"error"}


def dict_work_cash():
    '''Функция получения отчета'''
    fptr = IFptr()

    STATUS_STATE_STR = ''
    IP = CASH_IP
    PORT = "5555"
    SOCKET_KKM = '{}:{}'.format(IP, PORT)

    none_time = datetime(1970, 1, 1, 0)


    result_dict = {}
    cash_info = {}
    # инициализация параметров ( по документации )
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_MODEL, str(IFptr.LIBFPTR_MODEL_ATOL_AUTO))
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_TCPIP))
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_IPADDRESS, IP)
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_IPPORT, PORT)
    result = fptr.applySingleSettings()

    # проверка, есть ли коннект
    try:
        fptr.open()
        isOpened = fptr.isOpened()
        if isOpened == 0:
            result_dict['status'] = str('no connection')
            raise ConnectionError
        else:
            result_dict['status'] = str('connection successful')
        # print('connection successful\n')

    # Установка параметров
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_STATUS)
        fptr.queryData()

    # Запрос внутренних параметров
        NUMBER_KKT = fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)
        STATUS_STATE = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE)
        KKM_TIME = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)

        # Запрос параметров обмена с ОФН
        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_OFD_EXCHANGE_STATUS)
        fptr.fnQueryData()

        NOT_TRANS_DOC = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENTS_COUNT)
        DATA_LAST_TRANS = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
        DATA_FN_KEY = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_LAST_SUCCESSFUL_OKP)

        if STATUS_STATE == 0:
            STATUS_STATE_STR = 'Закрыта'
        elif STATUS_STATE == 1:
            STATUS_STATE_STR = 'Открыта'
        elif STATUS_STATE == 2:
            STATUS_STATE_STR = 'Истекла'

        cash_info['status'] = str(STATUS_STATE_STR)
        # print(f"Состояние кассы - {STATUS_STATE_STR}")
        
        if int(NOT_TRANS_DOC) > 0:
            if DATA_FN_KEY == none_time:
                # print('{}; ККМ №: {}; Дата/Время: {}; Непереданные чеки: {}; Первый непереданный: {};'.format(
                # SOCKET_KKM, NUMBER_KKT, KKM_TIME, NOT_TRANS_DOC, DATA_LAST_TRANS))
                cash_info['socket'] = str(SOCKET_KKM)
                cash_info['number'] = str(NUMBER_KKT)
                cash_info['time'] = str(KKM_TIME)
                cash_info['not_trans'] = str(NOT_TRANS_DOC)
                cash_info['last_trans'] = str(DATA_LAST_TRANS)
            else:
                # print('{}; ККМ №: {}; Дата/Время: {}; Непереданные чеки: {}; Первый непереданный: {}; Дата/время последнего ОКП: {};'.format(
                    # SOCKET_KKM, NUMBER_KKT, KKM_TIME, NOT_TRANS_DOC, DATA_LAST_TRANS, DATA_FN_KEY))
                cash_info['socket'] = str(SOCKET_KKM)
                cash_info['number'] = str(NUMBER_KKT)
                cash_info['time'] = str(KKM_TIME)
                cash_info['not_trans'] = str(NOT_TRANS_DOC)
                cash_info['last_trans'] = str(DATA_LAST_TRANS)
        else:
            if DATA_FN_KEY == none_time:
                # print('{}; ККМ №: {}; Дата/Время: {}; Непереданные чеки: {};'.format(
                # SOCKET_KKM, NUMBER_KKT, KKM_TIME, NOT_TRANS_DOC))
                cash_info['socket'] = str(SOCKET_KKM)
                cash_info['number'] = str(NUMBER_KKT)
                cash_info['time'] = str(KKM_TIME)
                cash_info['not_trans'] = str(NOT_TRANS_DOC)
                
            else:
                # print('{}; ККМ №: {}; Дата/Время: {}; Непереданные чеки: {}; Дата/время последнего ОКП: {};'.format(
                    # SOCKET_KKM, NUMBER_KKT, KKM_TIME, NOT_TRANS_DOC, DATA_FN_KEY))
                cash_info['socket'] = str(SOCKET_KKM)
                cash_info['number'] = str(NUMBER_KKT)
                cash_info['time'] = str(KKM_TIME)
                cash_info['not_trans'] = str(NOT_TRANS_DOC)
                
        result_dict['cash_info'] = cash_info
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_CASH_SUM)
        fptr.queryData()

        cashSum = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_SUM)
        # print(f"Сумма в кассе - {cashSum}")
        result_dict['cashsum'] = str(cashSum)
        
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_CASHIN_SUM)
        fptr.queryData()

        sum_in = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_SUM)
        # print(f"Внесение в кассу - {sum_in}")
        result_dict['sum_in'] = str(sum_in)
        
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_CASHOUT_SUM)
        fptr.queryData()

        sum_out = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_SUM)
        # print(f"Выплаты из кассы - {sum_out}")
        result_dict['sum_out'] = str(sum_out)
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_REVENUE)
        fptr.queryData()

        revenue = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_SUM)
        # print(f"Выручка - {revenue}")
        result_dict['revenue'] = str(revenue)
        # debugger
        # print(fptr.errorDescription())
        fptr.close()

    except Exception as e:
        print(e)
        result_dict['status'] = 'error'
        fptr.close()
    
    
    # print(result_dict)
    return result_dict

if __name__ == '__main__':
    dict_work_cash()