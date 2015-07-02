import pytest
from unittest import mock
from application.routes import app
import requests
import json


class FakeResponse(requests.Response):
    def __init__(self, res='Y', status_code=200):
        super(FakeResponse, self).__init__()

        # self._content = self.getJson(content)
        self.res = res

        self._content_consumed = True
        self.status_code = status_code

    def json(self):
        if self.res == 'Y':
            data = {"register_auto": True}
        else:
            data = {"register_auto": False}
        return data


reg_data = '{"keynumber": 222222, "ref": "myref", "date": "16/06/2015", "forename": "John", "surname": "Watson"}'


class TestB2BProcess:
    def setup_method(self, method):
        self.app = app.test_client()

    def test_reality(self):
        assert 1 + 2 == 3

    def test_healthcheck(self):
        response = self.app.get("/")
        assert response.status_code == 200

    def test_notfound(self):
        response = self.app.get("/doesnt_exist")
        assert response.status_code == 404

    def test_contentfail(self):
        headers = {'Content-Type': 'text'}
        response = self.app.post('/register', data=reg_data, headers=headers)
        assert response.status_code == 415


    fake_auto_success = FakeResponse('Y', 200)

    @mock.patch('requests.post', return_value=fake_auto_success)
    def test_register(self, mock_post):
        headers = {'Content-Type': 'application/json'}
        response = self.app.post('/register', data=reg_data, headers=headers)
        assert response.status_code == 200

    fake_manual_success = FakeResponse('N', 200)

    @mock.patch('requests.post', return_value=fake_manual_success)
    def test_register1(self, mock_post):
        headers = {'Content-Type': 'application/json'}
        response = self.app.post('/register', data=reg_data, headers=headers)
        assert response.status_code == 200

