class CustomTestUser():

    def __init__(self, username: str = 'another_user', password: str = 'P@ssw0rd') -> None:
        self.name: str = username
        self.password: str = password
