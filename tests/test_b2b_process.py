from unittest import mock
from application.routes import app
import requests
import json


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


reg_data = '{"keynumber": 222222, "ref": "myref", "application_date": "16/06/2015", "debtor_names": [{"forename": "John", "surname": "Watson"}]}'


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
        response = self.app.post('/register', data=reg_data, headers=headers)
        assert response.status_code == 415

    fake_auto_success = FakeResponseForAuto('Y', 200)

    @mock.patch('requests.post', return_value=fake_auto_success)
    def test_register(self, mock_post):
        headers = {'Content-Type': 'application/json'}
        response = self.app.post('/register', data=reg_data, headers=headers)
        assert response.status_code == 200

    fake_manual_success = FakeResponseForAuto('N', 200)

    @mock.patch('requests.post', return_value=fake_manual_success)
    def test_register1(self, mock_post):
        headers = {'Content-Type': 'application/json'}
        response = self.app.post('/register', data=reg_data, headers=headers)
        assert response.status_code == 200

    fake_healthcheck = FakeResponse('{"dependencies": {"an-app": "200 OK"} }'.encode(), 200)
    @mock.patch('requests.get', return_value=fake_healthcheck)
    def test_healthcheck(self, mock_get):
        response = self.app.get('/health')
        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data['dependencies']['an-app'] == '200 OK'