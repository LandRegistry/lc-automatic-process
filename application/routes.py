from application import app
from flask import Response, request
from datetime import datetime


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/register', methods=["POST"])
def register():
    if request.headers['Content-Type'] != "application/json":
        return Response(status=415)  # 415 (Unsupported Media Type)

    time = datetime.now()

    json_data = request.get_json(force=True)
    record = open("banksReg.txt", "a")
    record.write('Registration received %s/%s/%s at %s:%s:%s' % (
        time.day, time.month, time.year, time.hour, time.minute, time.second))
    record.write('\n')
    record.write('{}\n\n'.format(str(json_data)))
    record.close()

    return Response(status=200)