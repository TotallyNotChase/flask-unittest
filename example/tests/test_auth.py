import unittest
from dataclasses import dataclass
from typing import ByteString

from flask import Flask
from flask.testing import FlaskClient
from flask import g, session

from example.flaskr.db import get_db
from example.tests.conftest import AuthActions, TestBase


@dataclass
class AuthParameters:
    username: str
    password: str
    message: ByteString


class TestAuth(TestBase):
    def test_register(self, app: Flask, client: FlaskClient):
        # test that viewing the page renders without template errors
        self.assertStatus(client.get("/auth/register"), 200)

        # test that successful registration redirects to the login page
        response = client.post("/auth/register", data={"username": "a", "password": "a"})
        self.assertLocationHeader(response, "http://localhost/auth/login")

        # test that the user was inserted into the database
        with app.app_context():
            self.assertIsNotNone(get_db().execute("select * from user where username = 'a'").fetchone())

    def test_register_validate_input(self, _, client: FlaskClient):
        authparams = [
            AuthParameters("", "", b"Username is required."),
            AuthParameters("a", "", b"Password is required."),
            AuthParameters("test", "test", b"already registered")
        ]
        for authparam in authparams:
            username, password, message = vars(authparam).values()
            response = client.post("/auth/register", data={"username": username, "password": password})
            self.assertInResponse(message, response)

    def test_login(self, _, client: FlaskClient):
        # test that viewing the page renders without template errors
        self.assertStatus(client.get("/auth/login"), 200)

        # test that successful login redirects to the index page
        auth = AuthActions(client)
        response = auth.login()
        self.assertLocationHeader(response, "http://localhost/")

        # login request set the user_id in the session
        # check that the user is loaded from the session
        client.get("/")
        self.assertEqual(session["user_id"], 1)
        self.assertEqual(g.user["username"], "test")

    def test_login_validate_input(self, _, client: FlaskClient):
        auth = AuthActions(client)
        authparams = [
            AuthParameters("a", "test", b"Incorrect username."),
            AuthParameters("test", "a", b"Incorrect password.")
        ]
        for authparam in authparams:
            username, password, message = vars(authparam).values()
            response = auth.login(username, password)
            self.assertInResponse(message, response)

    def test_logout(self, _, client: FlaskClient):
        auth = AuthActions(client)
        auth.login()
        auth.logout()
        self.assertNotIn("user_id", session)


if __name__ == '__main__':
    unittest.main()
