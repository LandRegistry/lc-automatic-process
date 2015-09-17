from application import app
from flask import Response, request
import logging
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
            logging.info('Automatically processing')
            url = app.config['BANKRUPTCY_DATABASE_API'] + '/register'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json.dumps(json_data), headers=headers)

        else:
            # save to work list
            logging.info('Dropping to manual')
            url = app.config['CASEWORK_DATABASE_API'] + '/lodge_manual'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json.dumps(json_data), headers=headers)
            if response.status_code == 200:
                data = response.json()
                work_id = (data['id'])
                return Response(json.dumps({'id': work_id}), status=response.status_code)

        return Response(status=response.status_code)
    else:
        logging.error('Received code %d', response.status_code)
        return Response(status=response.status_code)
