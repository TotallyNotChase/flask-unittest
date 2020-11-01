import unittest

from flask import Flask
from flask.testing import FlaskClient

from example.flaskr.db import get_db
from example.tests.conftest import AuthActions, TestBase


class TestBlog(TestBase):
    def test_index(self, _, client: FlaskClient):
        response = client.get("/")
        self.assertInResponse(b"Log In", response)
        self.assertInResponse(b"Register", response)

        auth = AuthActions(client)
        auth.login()
        response = client.get("/")
        self.assertInResponse(b"test title", response)
        self.assertInResponse(b"by test on 2018-01-01", response)
        self.assertInResponse(b"test\nbody", response)
        self.assertInResponse(b'href="/1/update"', response)

    def test_login_required(self, _, client: FlaskClient):
        for path in ("/create", "/1/update", "/1/delete"):
            response = client.post(path)
            self.assertLocationHeader(response, "http://localhost/auth/login")

    def test_author_required(self, app: Flask, client: FlaskClient):
        # change the post author to another user
        with app.app_context():
            db = get_db()
            db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
            db.commit()

        auth = AuthActions(client)
        auth.login()
        # current user can't modify other user's post
        self.assertStatus(client.post("/1/update"), 403)
        self.assertStatus(client.post("/1/delete"), 403)
        # current user doesn't see edit link
        self.assertNotIn(b'href="/1/update"', client.get("/").data)

    def test_exists_required(self, _, client: FlaskClient):
        auth = AuthActions(client)
        auth.login()
        for path in ("/2/update", "/2/delete"):
            self.assertStatus(client.post(path), 404)

    def test_create(self, app: Flask, client: FlaskClient):
        auth = AuthActions(client)
        auth.login()
        self.assertStatus(client.get("/create"), 200)
        client.post("/create", data={"title": "created", "body": ""})

        with app.app_context():
            db = get_db()
            count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
            self.assertEqual(count, 2)

    def test_update(self, app: Flask, client: FlaskClient):
        auth = AuthActions(client)
        auth.login()
        self.assertStatus(client.get("/1/update"), 200)
        client.post("/1/update", data={"title": "updated", "body": ""})

        with app.app_context():
            db = get_db()
            post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
            self.assertEqual(post["title"], "updated")

    def test_create_update_validate(self, app: Flask, client: FlaskClient):
        auth = AuthActions(client)
        auth.login()
        for path in ("/create", "/1/update"):
            response = client.post(path, data={"title": "", "body": ""})
            self.assertInResponse(b"Title is required.", response)

    def test_delete(self, app: Flask, client: FlaskClient):
        auth = AuthActions(client)
        auth.login()
        response = client.post("/1/delete")
        self.assertLocationHeader(response, "http://localhost/")

        with app.app_context():
            db = get_db()
            post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
            self.assertIsNone(post)


if __name__ == '__main__':
    unittest.main()
