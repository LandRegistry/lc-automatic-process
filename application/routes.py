from application import app
from flask import Response, request
import logging
import requests
import json
import traceback
import kombu
import re


def check_bankreg_health():
    return requests.get(app.config['BANKRUPTCY_DATABASE_API'] + '/health')

application_dependencies = [
    {
        "name": "bankruptcy-registration",
        "check": check_bankreg_health
    }
]


@app.errorhandler(Exception)
def error_handler(err):
    logging.error('Unhandled exception: ' + str(err))
    call_stack = traceback.format_exc()

    lines = call_stack.split("\n")
    for line in lines:
        logging.error(line)

    error = {
        "type": "F",
        "message": str(err),
        "stack": call_stack
    }
    raise_error(error)
    return Response(json.dumps(error), status=500)


@app.before_request
def before_request():
    logging.info("BEGIN %s %s [%s] (%s)",
                 request.method, request.url, request.remote_addr, request.__hash__())


@app.after_request
def after_request(response):
    logging.info('END %s %s [%s] (%s) -- %s',
                 request.method, request.url, request.remote_addr, request.__hash__(),
                 response.status)
    return response


def automatic_process(registration):
    return True


@app.route('/', methods=["GET"])
def index():
    return Response(status=200)


@app.route('/health', methods=['GET'])
def health():
    result = {
        'status': 'OK',
        'dependencies': {}
    }

    status = 200
    for dependency in application_dependencies:
        response = dependency["check"]()
        result['dependencies'][dependency['name']] = str(response.status_code) + ' ' + response.reason
        data = json.loads(response.content.decode('utf-8'))
        for key in data['dependencies']:
            result['dependencies'][key] = data['dependencies'][key]

    return Response(json.dumps(result), status=status, mimetype='application/json')


@app.route('/bankruptcies', methods=["POST"])
def register():
    if request.headers['Content-Type'] != "application/json":
        logging.info("Invalid Content-Type - rejecting")
        return Response(status=415)  # 415 (Unsupported Media Type)

    request_text = request.data.decode('utf-8')
    logging.info("Data received: %s", re.sub(r"\r?\n", "", request_text))

    json_data = request.get_json(force=True)
    if automatic_process(json_data):
        logging.info('Automatically processing')

        # Convert the data where the public API differs from the internal
        json_data['date'] = json_data['application_date']
        del json_data['application_date']
        json_data['class_of_charge'] = json_data['application_type']
        del(json_data['application_type'])

        url = app.config['BANKRUPTCY_DATABASE_API'] + '/registrations'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(json_data), headers=headers)

        if response.status_code == 200:
            logging.info('POST {} -- {}'.format(url, response.status_code))
        else:
            logging.warning('POST {} -- {}'.format(url, response.status_code))

        respond_with = response.content
        respond_code = response.status_code
    else:
        raise NotImplementedError("Non-automatic processing is not supported")

    return Response(respond_with, status=respond_code, mimetype='application/json')


def raise_error(error):
    hostname = "amqp://{}:{}@{}:{}".format(app.config['MQ_USERNAME'], app.config['MQ_PASSWORD'],
                                           app.config['MQ_HOSTNAME'], app.config['MQ_PORT'])
    connection = kombu.Connection(hostname=hostname)
    producer = connection.SimpleQueue('errors')
    producer.put(error)
    logging.warning('Error successfully raised.')