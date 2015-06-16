import pytest
from unittest import mock
from application.routes import app
import requests

#following code commented out as it'll be required for the next sprint
"""class FakeResponse(requests.Response):
    def __init__(self, content='', status_code=200):
        super(FakeResponse, self).__init__()
        self._content = content
        self._content_consumed = True
        self.status_code = status_code"""

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
        response = self.app.post('/register', data= reg_data, headers=headers)
        assert response.status_code == 415

    def test_register(self):
        headers = {'Content-Type': 'application/json'}
        response = self.app.post('/register', data= reg_data, headers=headers)
        assert response.status_code == 200


