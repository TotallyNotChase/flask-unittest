# flask-unittest
A hassle free solution to testing flask application using `unittest`

Provides functionality for testing using the `Flask` object, the `FlaskClient` object, a combination of the two, or even a live flask server!

This library is intended to provide utilities that help the user follow the [official flask application testing guidelines](https://flask.palletsprojects.com/en/1.1.x/testing/). It is recommended you familiarize yourself with that page.

Unless you're interested in testing a live flask server using a headless browser. In which case, familiarity with your preferred headless browser is enough.

# Features
* Test flask applications using a `Flask` object
  * Access to `app_context`, `test_request_context` etc
  * Access to flask globals like `g`, `request`, and `session`
  * Access to `test_client` through the `Flask` object
  * Same `Flask` object will be usable in the test method and its corresponding `setUp` and `tearDown` methods
  * App is created per test method in the testcase
* Test flask applications using a `FlaskClient` object
  * Access to flask globals like `g`, `request`, and `session`
  * Test your flask app in an **API centric way** using the functionality provided by `FlaskClient`
  * Same `FlaskClient` object will be usable in the test method and its corresponding `setUp` and `tearDown` methods
  * The `FlaskClient` is created per test method of the testcase by using the given `Flask` object (App)
  * App can either be a constant class property throughout the testcase, or be created per test method
* Test flask applications running *live* on localhost - using your preferred **headless browser** (e.g `selenium`, `pyppeteer` etc)
  * Contrary to the previous ones, this functionality is handled by a test suite, rather than a test case
  * The flask server is started in a daemon thread when the `LiveTestSuite` runs - it runs for the duration of the program
* Simple access to the context so you can access flask globals (`g`, `request`, and `session`) with minimal headaches and no gotchas!
* Support for using generators as `create_app` - essentially emulating `pytest`'s fixtures (more of that in `example/tests/`)
* No extra dependencies! (well, except for `flask`...) - easily integratable with the built in `unittest` module

# Quick Start
Install `flask-unittest` from pypi using `pip`
```bash
pip install flask-unittest
```

Import in your module and start testing!
```py
import flask_unittest
```

Now, before moving on to the examples below - I **highly recommend** checking out the official [Testing Flask Applications example](https://flask.palletsprojects.com/en/1.1.x/testing/). It's *extremely simple* and should take only 5 minutes to digest.

Alternatively, you can directly dive into the examples at [`tests/`](./tests/) and [`example/tests/`](./example/tests). Though this might be a bit intimidating if you're just starting out at testing flask apps.

**NOTE**: For all the following testcases using `FlaskClient`, it is recommended to set `.testing` on your `Flask` app to `True` (i.e `app.testing = True`)

# Test using `FlaskClient`
If you want to use a [`FlaskClient`](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.test_client) object to test - this is the testcase for you!

This testcase creates a `FlaskClient` object for each test method. But the `app` property is kept constant.
```py
import flask_unittest
import flask.globals

class TestFoo(flask_unittest.ClientTestCase):
    # Assign the `Flask` app object
    app = ...

    def setUp(self, client):
        # Perform set up before each test, using client
        pass

    def tearDown(self, client):
        # Perform tear down after each test, using client
        pass

    '''
    Note: the setUp and tearDown method don't need to be explicitly declared
    if they don't do anything (like in here) - this is just an example
    Only declare the setUp and tearDown methods with a body, same as regular unittest testcases
    '''

    def test_foo_with_client(self, client):
        # Use the client here
        # Example request to a route returning "hello world" (on a hypothetical app)
        rv = client.get('/hello')
        self.assertInResponse(rv, 'hello world!')

    def test_bar_with_client(self, client):
        # Use the client here
        # Example login request (on a hypothetical app)
        rv = client.post('/login', {'username': 'pinkerton', 'password': 'secret_key'})
        # Make sure rv is a redirect request to index page
        self.assertLocationHeader('http://localhost/')
        # Make sure session is set
        self.assertIn('user_id', flask.globals.session)
```
Remember to assign a correctly configured `Flask` app object to `app`!

Each test method, as well as the `setUp` and `tearDown` methods, should take `client` as a parameter. You can name this parameter whatever you want of course but the 2nd parameter (including `self` as first) is a `FlaskClient` object.

Note that the `client` is different for *each test method*. But it's the same for a singular test method and its corresponding `setUp` and `tearDown` methods.

What does this mean? Well, when it's time to run `test_foo_with_client`, a `FlaskClient` object is created using `app.test_client()`. Then this is passed to `setUp`, which does its job of setup. After that, the same `client` is passed to `test_foo_with_client`, which does the testing. Finally, the same `client` again, is passed to `tearDown` - which cleans the stuff up.

Now when it's time to run `test_bar_with_client`, a new `FlaskClient` object is created and so on.

This essentially means that any global changes (such as `session` and cookies) you perform in `setUp` using `client`, will be persistent in the actual test method. And the changes in the test method will be persistent in the `tearDown`. These changes get destroyed in the next test method, where a new `FlaskClient` object is created.

**NOTE**: If you want to **disable** the use of cookies on `client`, you need to put `test_client_use_cookies = False` in your testcase body.

You can also pass in extra kwargs to the `test_client()` call by setting `test_client_kwargs` in your testcase body.

**Full Example**: [`flask_client_test.py`](./tests/flask_client_test.py)

# Test using `Flask`
If you want to use a [`Flask`](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask) object to test - this is the testcase for you!

This testcase creates a `Flask` object for each test method, using the `create_app` method implemented by the user
```py
import flask_unittest
from flaskr.db import get_db

class TestFoo(flask_unittest.AppTestCase):

    def create_app(self):
        # Return/Yield a `Flask` object here
        pass

    def setUp(self, app):
        # Perform set up before each test, using app
        pass

    def tearDown(self, app):
        # Perform tear down after each test, using app
        pass

    '''
    Note: the setUp and tearDown method don't need to be explicitly declared
    if they don't do anything (like in here) - this is just an example
    Only declare the setUp and tearDown methods with a body, same as regular unittest testcases
    '''

    def test_foo_with_app(self, app):
        # Use the app here
        # Example of using test_request_context (on a hypothetical app)
        with app.test_request_context('/1/update'):
            self.assertEqual(request.endpoint, 'blog.update')

    def test_bar_with_app(self, app):
        # Use the app here
        # Example of using client from app (on a hypothetical app)
        with app.test_client() as client:
            rv = client.get('/hello')
            self.assertInResponse(rv, 'hello world!')

    def test_baz_with_app(self, app):
        # Use the app here
        # Example of using app_context (on a hypothetical app)
        with app.app_context():
            get_db().execute("INSERT INTO user (username, password) VALUES ('test', 'testpass');")
```
The `create_app` function should return a correctly configured `Flask` object representing the webapp to test

You can also do any set up, extra config for the app (db init etc) here

It's also possible (and encouraged) to `yield` a `Flask` object here instead of `return`ing one (essentially making this a generator function)
This way, you can put cleanup right here after the `yield` and they will be executed once the test method has run

See [Emulating official flask testing example using `flask-unittest`](#emulating-official-flask-testing-example-using-flask-unittest)

Each test method, as well as the `setUp` and `tearDown` methods, should take `app` as a parameter. You can name this parameter whatever you want of course but the 2nd parameter (including `self` as first) is a `Flask` object returned/yielded from the user provided `create_app`.

Note that the `app` is different for *each test method*. But it's the same for a singular test method and its corresponding `setUp` and `tearDown` methods.

What does this mean? Well, when it's time to run `test_foo_with_app`, a `Flask` object is created using `create_app`. Then this is passed to `setUp`, which does its job of setup. After that, the same `app` is passed to `test_foo_with_app`, which does the testing. Finally, the same `app` again, is passed to `tearDown` - which cleans the stuff up.

Now when it's time to run `test_bar_with_app` - `create_app` is called again and a new `Flask` object is created and so on.

If `create_app` is a generator function. All the stuff after `yield app` will be executed after the test method (and its `tearDown`, if any) has run

**Full Example**: [`flask_app_test.py`](./tests/flask_app_test.py)

# Test using both `Flask` and `FlaskClient`
If you want to use both [`Flask`](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask) *and* [`FlaskClient`](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.test_client) to test - this is the testcase for you!

This testcase creates a `Flask` object, using the `create_app` method implemented by the user, *and* a `FlaskClient` object from said `Flask` object, for each test method
```py
import flask_unittest
from flaskr import get_db

class TestFoo(flask_unittest.AppClientTestCase):

    def create_app(self):
        # Return/Yield a `Flask` object here
        pass

    def setUp(self, app, client):
        # Perform set up before each test, using app and client
        pass

    def tearDown(self, app, client):
        # Perform tear down after each test, using app and client
        pass

    '''
    Note: the setUp and tearDown method don't need to be explicitly declared
    if they don't do anything (like in here) - this is just an example
    Only declare the setUp and tearDown methods with a body, same as regular unittest testcases
    '''

    def test_foo_with_both(self, app, client):
        # Use the app and client here
        # Example of registering a user and checking if the entry exists in db (on a hypothetical app)
        response = client.post('/auth/register', data={'username': 'a', 'password': 'a'})
        self.assertLocationHeader(response, 'http://localhost/auth/login')

        # test that the user was inserted into the database
        with app.app_context():
            self.assertIsNotNone(get_db().execute("select * from user where username = 'a'").fetchone())

    def test_bar_with_both(self, app, client):
        # Use the app and client here
        # Example of creating a post and checking if the entry exists in db (on a hypothetical app)
        client.post('/create', data={'title': 'created', 'body': ''})

        with app.app_context():
            db = get_db()
            count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
            self.assertEqual(count, 2)
```
The `create_app` function should return a correctly configured `Flask` object representing the webapp to test

You can also do any set up, extra config for the app (db init etc) here

It's also possible (and encouraged) to `yield` a `Flask` object here instead of `return`ing one (essentially making this a generator function)
This way, you can put cleanup right here after the `yield` and they will be executed once the test method has run

See [Emulating official flask testing example using `flask-unittest`](#emulating-official-flask-testing-example-using-flask-unittest)

Each test method, as well as the `setUp` and `tearDown` methods, should take `app` and `client` as a parameter. You can name these parameters whatever you want of course but the 2nd parameter (including `self` as first) is a `Flask` object returned/yielded from the user provided `create_app`, and the third parameter is a `FlaskClient` object returned from calling `.test_client` on said `Flask` object.

Note that the `app` and `client` are different for *each test method*. But they are the same for a singular test method and its corresponding `setUp` and `tearDown` methods.

What does this mean? Well, when it's time to run `test_foo_with_both`, a `Flask` object is created using `create_app()`, and a `FlaskClient` object is created from it. Then they are passed to `setUp`, which does its job of setup. After that, the same `app` and `client` are passed to `test_foo_with_both`, which does the testing. Finally, the same `app` and `client` again, are passed to `tearDown` - which cleans the stuff up.

Now when it's time to run `test_bar_with_app` - `create_app` is called again to create a new `Flask` object, and also `.test_client` to create a new `FlaskClient` object and so on.

If `create_app` is a generator function. All the stuff after `yield app` will be executed after the test method (and its `tearDown` if any) has run

**Full Example**: [`flask_appclient_test.py`](./tests/flask_appclient_test.py)

# Test using a headless browser (eg `selenium`, `pyppeteer` etc)
If you want to test a live flask server using a headless browser - `LiveTestSuite` is for you!

Unlike the previous ones, this functionality relies on the use of a **suite**, *not a testcase*. The testcases should inherit from `LiveTestCase` but the real juice is in `LiveTestSuite`.

An example testcase for this would look like-
```py
import flask_unittest
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestFoo(flask_unittest.LiveTestCase):
    driver: Union[Chrome, None] = None
    std_wait: Union[WebDriverWait, None] = None

    ### setUpClass and tearDownClass for the entire class
    # Not quite mandatory, but this is the best place to set up and tear down selenium

    @classmethod
    def setUpClass(cls):
        # Initiate the selenium webdriver
        options = ChromeOptions()
        options.add_argument('--headless')
        cls.driver = Chrome(options=options)
        cls.std_wait = WebDriverWait(cls.driver, 5)

    @classmethod
    def tearDownClass(cls):
        # Quit the webdriver
        cls.driver.quit()

    ### Actual test methods

    def test_foo_with_driver(self):
        # Use self.driver here
        # You also have access to self.server_url and self.app
        # Example of using selenium to go to index page and try to find some elements (on a hypothetical app)
        self.driver.get(self.server_url)
        self.std_wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Register')))
        self.std_wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Log In')))
```
This is pretty straight forward, it's just a regular test case that you would use if you spawned the flask server from the terminal before running tests

Now, you need to use the `LiveTestSuite` to run this. The previous testcases could be run using `unitttest.TestSuite`, or simply `unittest.main` but this *has to be* run using the custom suite
```py
# Assign the flask app here
app = ...

# Add TestFoo to suite
suite = flask_unittest.LiveTestSuite(app)
suite.addTest(unittest.makeSuite(TestFoo))

# Run the suite
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
```
The `LiveTestSuite` requires a built and configured `Flask` app object. It'll spawn this flask app using `app.run` as a daemon thread.

By default, the app runs on host 127.0.0.1 and port 5000. If you'd like to change this assign your custom host (as a `str`) and a port (as an `int`) to `app.config` under the key `HOST` and `PORT` respectively. (`app.config['HOST'] = '0.0.0.0'; app.config['PORT'] = 7000`)

The server is started when the suite is first run and it runs for the duration of the program

You will have access to the `app` passed to the suite inside `LiveTestCase`, using `self.app`. You will also have access to the url the server is running on inside the testcase, using `self.server_url`

**Full Example** (of `LiveTestCase`): [`flask_live_test.py`](./tests/flask_live_test.py)
**Full Example** (of `LiveTestSuite`): [`__init__.py`](./tests/__init__.py)

# About request context and flask globals
Both `ClientTestCase` and `AppClientTestCase` allow you to use flask gloabls, such as `request`, `g`, and `session`, directly in your test method (and your `setUp` and `tearDown` methods)

This is because the `client` is *instantiated using a `with` block*, and the test method, the `setUp` and `tearDown` methods **happen inside the `with` block**

Very rough psuedocode representation of this would look like-
```py
with app.test_client() as client:
    self.setUp(client)
    self.test_method(client)
    self.tearDown(client)
```
This means you can treat everything in your test method, and `setUp` and `tearDown` methods, as if they are within a `with client:` block

Practically, this lets you use the flask globals after making a request using `client` - which is great for testing

Additional info in the [official docs](https://flask.palletsprojects.com/en/1.1.x/testing/#keeping-the-context-around)

# Emulating official flask testing example using `flask-unittest`
The official flask testing example can be found [in the flask repo](https://github.com/pallets/flask/tree/master/examples/tutorial/tests)

The original tests are written using `pytest`. This example demonstrates how `flask-unittest` can provide the same functionality for you, with the same degree of control!

Note that this demonstration does not implement the `test_cli_runner` - since that is not directly supported by `flask-unittest` (yet). However, it's completely possible to simply use `.test_cli_runner()` on the `app` object in the testcases provided by `flask-unittest` to emulate this.

The primary thing to demonstrate here, is to emulate the pytest fixtures defined in the original [`conftest.py`](https://github.com/pallets/flask/blob/master/examples/tutorial/tests/conftest.py)-
```py
@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE": db_path})

    # create the database and load test data
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
```

As you can see, this creates the app **and** the test client *per test*. So we'll be using `AppClientTestCase` for this.

Let's make a base class that provides functionality for this - all the other testcases can inherit from it. Defined in [`conftest.py`](./example/tests/conftest.py)

```py
import flask_unittest


class TestBase(flask_unittest.AppClientTestCase):

    def create_app(self):
        """Create and configure a new app instance for each test."""
        # create a temporary file to isolate the database for each test
        db_fd, db_path = tempfile.mkstemp()
        # create the app with common test config
        app = create_app({"TESTING": True, "DATABASE": db_path})

        # create the database and load test data
        with app.app_context():
            init_db()
            get_db().executescript(_data_sql)

            # Yield the app
            '''
            This can be outside the `with` block too, but we need to 
            call `close_db` before exiting current context
            Otherwise windows will have trouble removing the temp file
            that doesn't happen on unices though, which is nice
            '''
            yield app

            ## Close the db
            close_db()
        
        ## Cleanup temp file
        os.close(db_fd)
        os.remove(db_path)
```

This is very similar to the original pytest fixtures and achieves the exact same functionality in the actual testcases too!

Do note however, there's an extra call inside `with app.app_context()` - `close_db`. Windows struggles to remove the temp database using `os.remove` if it hasn't been closed already - so we have to do that (this is true for the original pytest methods too).

Also of note, creation of the `AuthActions` object should be handled manually in each of the test case. This is just how `unittest` works in contrast to `pytest`. This shouldn't pose any issue whatsoever though.

Now let's look at an actual testcase. We'll be looking at `test_auth.py`, since it demonstrates the use of `app`, `client` and the flask globals very nicely.

For context, the original file is defined at [`test_auth.py`](https://github.com/pallets/flask/blob/master/examples/tutorial/tests/test_auth.py)

The full emulation of this file is at [`test_auth.py`](./example/tests/test_auth.py)

Ok! Let's look at the emulation of `test_register`.

For context, this is the original function-
```py
def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "a"})
    assert "http://localhost/auth/login" == response.headers["Location"]

    # test that the user was inserted into the database
    with app.app_context():
        assert (
            get_db().execute("select * from user where username = 'a'").fetchone()
            is not None
        )
```

And here's the `flask-unittest` version!
```py
from example.tests.conftest import AuthActions, TestBase


class TestAuth(TestBase):

    def test_register(self, app, client):
        # test that viewing the page renders without template errors
        self.assertStatus(client.get("/auth/register"), 200)

        # test that successful registration redirects to the login page
        response = client.post("/auth/register", data={"username": "a", "password": "a"})
        self.assertLocationHeader(response, "http://localhost/auth/login")

        # test that the user was inserted into the database
        with app.app_context():
            self.assertIsNotNone(
                get_db().execute("select * from user where username = 'a'").fetchone()
            )
```
See how similar it is? The only difference is that the function should be a method in a class that is extending `flask_unittest.AppClientTestCase` with `create_app` defined. In our case, that's `TestBase` from `conftest.py` - so we extend from that.

As mentioned previously, each test method of an `AppClientTestCase` should have the parameters `self, app, client` - not necessarily with the same names but the second param **will be** the `Flask` object, and the third param **will be** the `FlaskClient` object

Also, this is using `self.assert...` functions as per `unittest` convention. However, regular `assert`s should work just fine.

Nice! Let's look at a function that uses flask globals - `test_login`

Here's the original snippet-
```py
def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "http://localhost/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"

```

And here's the `flask-unittest` version-
```py
class TestAuth(TestBase):
    
    def test_login(self, _, client):
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
```

(this is a continuation of the previous example for `test_register`)

Once again, very similar. But there's a couple of things to note here.

Firstly, notice we are ignoring the second argument of `test_login`, since we have no reason to use `app` here. We do, however, need to use the `FlaskClient` object

Also notice, we don't have to do `with client` to access the request context. `flask-unittest` already handles this for us, so we have direct access to `session` and `g`.

Let's check out a case where we only use the `Flask` object and not the `FlaskClient` object - in which case, we can use `AppTestCase`.

The original function, `test_get_close_db`, is defined at [`test_db.py`](https://github.com/pallets/flask/blob/master/examples/tutorial/tests/test_db.py)

```py
def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)
```

The `flask-unittest` version can be seen at [`test_db.py`](./example/tests/test_db.py)

```py
import flask_unittest

class TestDB(flask_unittest.AppTestCase):

   # create_app omitted for brevity - remember to include it!
   
    def test_get_close_db(self, app):
        with app.app_context():
            db = get_db()
            assert db is get_db()

        try:
            db.execute("SELECT 1")
        except sqlite3.ProgrammingError as e:
            self.assertIn("closed", str(e.args[0]))

```

Very similar once again!
