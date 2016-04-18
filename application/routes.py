from application import app
from flask import Response, request
import logging
import requests
import json
import traceback
import kombu
import re
import json
import datetime
from datetime import timedelta


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


def format_message(message):
    if 'X-Transaction-ID' in request.headers:
        return "T:{} {}".format(request.headers['X-Transaction-ID'], message)
    return message


def create_registration(data):
    registration = {
        "parties": [],
        "class_of_charge": re.sub("[\(\)]", "", data['application_type']),
        "applicant": {
            "name": data['customer_name'],
            "address": data['customer_address'],
            "key_number": data['key_number'],
            "reference": data['application_ref'],
            "address_type": "NA"
        },
        'original_request': data['original_request']
    }

    party = {
        "type": "Debtor",
        "names": [],
        "addresses": [],
        "occupation": '',
        "trading_name": '',
        "residence_withheld": data['residence_withheld'],
        "case_reference": "Adjudicator ref {}".format(data['application_ref']),
        #"date_of_birth": data['date_of_birth']
    }

    if 'occupation' in data:
        party['occupation'] = data['occupation']

    if 'trading_name' in data:
        party['trading_name'] = data['trading_name']

    if 'date_of_birth' in data:
        party['date_of_birth'] = data['date_of_birth']

    for name in data['debtor_names']:
        party['names'].append({
            'type': 'Private Individual',
            'private': name
        })

    if 'residence' in data:
        for address in data['residence']:
            party['addresses'].append({
                'type': 'Residence',
                'address_lines': address['address_lines'],
                'county': address['county'],
                'postcode': address['postcode']
            })

    if 'business_address' in data:
        for address in data['business_address']:
            party['addresses'].append({
                'type': 'Residence',
                'address_lines': address['address_lines'],
                'county': address['county'],
                'postcode': address['postcode']
            })

    if 'investment_property' in data:
        for address in data['investment_property']:
            party['addresses'].append({
                'type': 'Residence',
                'address_lines': address['address_lines'],
                'county': address['county'],
                'postcode': address['postcode']
            })

    registration['parties'].append(party)
    return registration


def notify_casework_api(registrations, data):
    send_data = {
        'new_registrations': [],
        'request_text': data
    }

    for reg in registrations:
        send_data['new_registrations'].append({
            "number": reg['number'],
            "date": reg['date']
        })

    connection = kombu.Connection(hostname=app.config['AMQP_URI'])
    producer = connection.SimpleQueue(app.config['PREGENERATE_QUEUE_NAME'])
    producer.put(send_data)
    logging.info('Pregeneration submitted.')


def get_registration_post_date(time_now):
    # The legislation requires that registrations *received* prior to 1500 on a given day

    # Get calendar information from CASEWORK_API
    date_info = get_calendar_info(time_now.strftime('%Y-%m-%d'))
    if not date_info['is_working']:
        return date_info['next_working']
    else:
        three_pm = time_now.replace(hour=15, minute=0, second=0, microsecond=0)
        if time_now.time() >= three_pm.time():
            return date_info['next_working']

    return None


def get_calendar_info(date):
    url = app.config['CASEWORK_DATABASE_API'] + '/next_registration_date/' + date
    response = requests.get(url, headers={'X-Transaction-ID': request.headers['X-Transaction-ID'], 'Content-Type': 'application/json'})
    data = response.json()
    return data


@app.route('/bankruptcies', methods=["POST"])
def register():
    if request.headers['Content-Type'] != "application/json":
        logging.info("Invalid Content-Type - rejecting")
        return Response(status=415)  # 415 (Unsupported Media Type)

    request_text = request.data.decode('utf-8')
    logging.info(format_message("Data received: %s"), re.sub(r"\r?\n", "", request_text))

    next_date = None
    now = datetime.datetime.now()
    post_date = get_registration_post_date(now)
    if post_date:
        next_date = post_date

    json_data = request.get_json(force=True)
    if automatic_process(json_data):
        logging.info(format_message('Automatically processing'))

        registration = create_registration(json_data)

        url = app.config['BANKRUPTCY_DATABASE_API'] + '/registrations'
        if post_date:
            url += "?postdate=" + next_date

        headers = {
            'Content-Type': 'application/json',
            'X-Transaction-ID': request.headers['X-Transaction-ID']
        }

        if 'X-LC-Username' in request.headers:
            headers['X-LC-Username'] = request.headers['X-LC-Username']
        else:
            headers['X-LC-Username'] = "none(automatic-process)"  # This happens in test scripts

        response = requests.post(url, data=json.dumps(registration), headers=headers)

        if response.status_code == 200:
            logging.info('POST {} -- {}'.format(url, response.status_code))
        else:
            logging.warning('POST {} -- {}'.format(url, response.status_code))
            logging.warning(response.text)
            return Response(response.text, status=response.status_code)

        logging.debug(response.content)
        respond_data = json.loads(response.content.decode('utf-8'))
        respond_with = {
            "new_registrations": [],
            "application_ref": ""
        }

        for reg in respond_data['new_registrations']:
            respond_with['new_registrations'].append({
                "forenames": reg["name"]["private"]["forenames"],
                "surname": reg["name"]["private"]["surname"],
                "number": reg['number'],
                "date": reg['date']
            })
        notify_casework_api(respond_with['new_registrations'], json_data['original_request'])
        logging.info(format_message('Automatic processing completed'))
        respond_code = response.status_code
    else:
        raise NotImplementedError("Non-automatic processing is not supported")

    return Response(json.dumps(respond_with), status=respond_code, mimetype='application/json')


def raise_error(error):
    hostname = app.config['AMQP_URI']
    connection = kombu.Connection(hostname=hostname)
    producer = connection.SimpleQueue('errors')
    producer.put(error)
    logging.error(error)
    logging.warning('Error successfully raised.')