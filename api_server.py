from robyn import Robyn, jsonify
from main import dict_work_cash

app = Robyn(__file__)


@app.get("/status")
def h(request):
    return jsonify(dict_work_cash())



app.start(url='0.0.0.0', port=8888)