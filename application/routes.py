from application import app
from flask import Response, request
from datetime import datetime

import requests
import json


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/register', methods=["POST"])
def register():
    if request.headers['Content-Type'] != "application/json":
        return Response(status=415)  # 415 (Unsupported Media Type)

    json_data = request.get_json(force=True)

    url = app.config['RULES_ENGINE_URL'] + '/check_auto'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(json_data), headers=headers)

    if response.status_code == 200:
        data = response.json()
        go_auto = (data['register_auto'])
        if go_auto:
            url = app.config['BANKRUPTCY_DATABASE_API'] + '/register'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json.dumps(json_data), headers=headers)

        else:
            # save to work list
            time = datetime.now()

            json_data = request.get_json(force=True)
            record = open("banksReg.txt", "a")
            record.write('Unable to auto Register application %s/%s/%s at %s:%s:%s' % (time.day, time.month, time.year,
                                                                                       time.hour, time.minute,
                                                                                       time.second))
            record.write('\n')
            record.write('{}\n\n'.format(str(json_data)))
            record.close()

    return Response(status=response.status_code)