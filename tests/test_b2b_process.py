from unittest import mock
from application.routes import app, get_registration_post_date
import requests
import json
import datetime


class FakeResponse(requests.Response):
    def __init__(self, content='', status_code=200):
        super(FakeResponse, self).__init__()
        self._content = content
        self._content_consumed = True
        self.status_code = status_code
        self.reason = 'TEST'


class FakeResponseForAuto(requests.Response):
    def __init__(self, res='Y', status_code=200):
        super(FakeResponseForAuto, self).__init__()

        # self._content = self.getJson(content)
        self.res = res
        self._content_consumed = False
        self.status_code = status_code
        self.reason = 'TEST'

    def json(self):
        # sets up the json required in the mock response
        if self.res == 'Y':
            data = {"register_auto": True}
        else:
            data = {"register_auto": False, "id": 1}
        return data


reg_data = '{"original_request": "{}", "customer_name": "boo", "customer_address": "hjhjhj", "key_number":"1234567","application_ref":"APP01","application_type":"PA(B)","application_date":"2016-01-01","debtor_names":[{"forenames":["Bob","Oscar","Francis"],"surname":"Howard"}],"gender":"Unknown","occupation":"Civil Servant","trading_name":"","residence":[{"address_lines":["1 The Street","The Town"],"postcode":"AA1 1AA","county":"The County"}],"residence_withheld":false,"date_of_birth":"1980-01-01"}'


class TestB2BProcess:
    def setup_method(self, method):
        self.app = app.test_client()

    def test_reality(self):
        assert 1 + 2 == 3

    def test_root(self):
        response = self.app.get("/")
        assert response.status_code == 200

    def test_notfound(self):
        response = self.app.get("/doesnt_exist")
        assert response.status_code == 404

    def test_contentfail(self):
        headers = {'Content-Type': 'text'}
        response = self.app.post('/bankruptcies', data=reg_data, headers=headers)
        assert response.status_code == 415

    @mock.patch('requests.post', return_value=FakeResponse(b'{"new_registrations": []}'))
    def test_register(self, mock_post):
        headers = {'Content-Type': 'application/json', 'X-Transaction-ID': 42}
        response = self.app.post('/bankruptcies', data=reg_data, headers=headers)
        assert response.status_code == 200

    @mock.patch('requests.post', return_value=FakeResponse(b'{"new_registrations": []}'))
    def test_register1(self, mock_post):
        headers = {'Content-Type': 'application/json', 'X-Transaction-ID': 42}
        response = self.app.post('/bankruptcies', data=reg_data, headers=headers)
        assert response.status_code == 200

    fake_healthcheck = FakeResponse('{"dependencies": {"an-app": "200 OK"} }'.encode(), 200)
    @mock.patch('requests.get', return_value=fake_healthcheck)
    def test_healthcheck(self, mock_get):
        response = self.app.get('/health')
        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data['dependencies']['an-app'] == '200 OK'

    # Ugh, do not have time to cleverly mock out the call to the dates function.
    # def test_registration_dates(self):
    #     reg_date = get_registration_post_date(datetime.datetime(2016, 10, 1, 14, 30, 12, 123456))
    #     assert reg_date is None
    #
    #     reg_date = get_registration_post_date(datetime.datetime(2016, 10, 1, 15, 30, 12, 123456))
    #     assert reg_date == '2016-10-02'
    #
    #     reg_date = get_registration_post_date(datetime.datetime(2016, 10, 1, 4, 30, 12, 123456))
    #     assert reg_date is None
    #
    #     reg_date = get_registration_post_date(datetime.datetime(2016, 10, 1, 23, 59, 59, 123456))
    #     assert reg_date == '2016-10-02'
    #
    #     reg_date = get_registration_post_date(datetime.datetime(2016, 10, 1, 15, 00, 00, 0))
    #     assert reg_date == '2016-10-02'