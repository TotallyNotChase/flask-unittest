# Just a bunch of classes containing some data to be used by the tests


class MockUser:
    username = 'Marty_McFly'
    password = 'Ac1d1f1c4t10n@sh4rk'


class MockPost:
    def __init__(self, title: str, body: str):
        self.title = title
        self.body = body


class MockPosts:
    posts = (
        MockPost('Finite time', 'Chances last a finite time'), MockPost('Walt Disney', 'Seven months of suicide'),
        MockPost('Turned away', 'Turn back the clock\nFall onto the ground')
    )
