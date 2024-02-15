import os, json
from typing import List
from robyn import Robyn, jsonify, Request, Response, ALLOW_CORS
from main import dict_work_cash, print_receipt
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

@app.post("/receipt")
def sync_body_post(request: Request):
    body = json.loads(request.body)
    try:
        return jsonify(print_receipt(body))
    except Exception as e:
        print(e)
        return {"result":"error"}

app.start(url='0.0.0.0', port=APP_PORT)