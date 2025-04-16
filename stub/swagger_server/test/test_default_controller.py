# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.efficiency import Efficiency  # noqa: E501
from swagger_server.models.latest import Latest  # noqa: E501
from swagger_server.models.log_item import LogItem  # noqa: E501
from swagger_server.models.user_edit_body import UserEditBody  # noqa: E501
from swagger_server.models.user_login_body import UserLoginBody  # noqa: E501
from swagger_server.models.user_register_body import UserRegisterBody  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_controller_get_latest(self):
        """Test case for controller_get_latest

        Returns the user's latest sleep data recorded.
        """
        response = self.client.open(
            '/sleep-api/latest/{user_id}'.format(user_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_controller_get_user_efficiency(self):
        """Test case for controller_get_user_efficiency

        Returns predicted sleep efficiency of the specified user.
        """
        response = self.client.open(
            '/sleep-api/efficiency/{user_id}'.format(user_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_controller_get_user_log(self):
        """Test case for controller_get_user_log

        Returns a list of user's sleep logs in the database.
        """
        response = self.client.open(
            '/sleep-api/log/{user_id}'.format(user_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_controller_user_edit(self):
        """Test case for controller_user_edit

        Edit an existing user
        """
        body = UserEditBody()
        response = self.client.open(
            '/sleep-api/user/edit',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_controller_user_login(self):
        """Test case for controller_user_login

        Login a user
        """
        body = UserLoginBody()
        response = self.client.open(
            '/sleep-api/user/login',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_controller_user_register(self):
        """Test case for controller_user_register

        Register a new user
        """
        body = UserRegisterBody()
        response = self.client.open(
            '/sleep-api/user/register',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
