import os
from robyn import Robyn, jsonify
from main import dict_work_cash
from dotenv import load_dotenv

# инициализация объекта драйвера
# DRIVER_PATH = os.path.join(os.getcwd(), 'fptr10.dll')
# fptr = IFptr(DRIVER_PATH)
load_dotenv()
APP_PORT = os.getenv('APP_PORT')


app = Robyn(__file__)


@app.get("/status")
def status(request):
    return jsonify(dict_work_cash())



app.start(url='0.0.0.0', port=APP_PORT)