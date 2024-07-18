class AppException(Exception):
    def __init__(self, message=None):
        self.message = 'Internal Server Error.' + (f" {message}" if message else '')
        super().__init__(self.message)


class UserException(Exception):
    def __init__(self, message, status, **kwargs):
        self.message = message
        self.status = status
        self.extra = kwargs
        super().__init__(self.message, self.status, self.extra)


class UserAlreadyExists(UserException):
    def __init__(self, email: str):
        self.message = "User already exists."
        self.email = email
        super().__init__(self.message, 403, email=self.email)


class UserDoesNotExist(UserException):
    def __init__(self, email: str):
        self.message = "User does not exists."
        self.email = email
        super().__init__(self.message, 403, email=self.email)


class UserCredentialsMismatch(UserException):
    def __init__(self, email: str):
        self.message = "User credentials mismatch."
        self.email = email
        super().__init__(self.message, 403, email=self.email)


class UserPasswordExpired(UserException):
    def __init__(self, email: str):
        self.message = "Password has expired."
        self.email = email
        super().__init__(self.message, 403, email=self.email)


class UserTokenInvalid(UserException):
    def __init__(self):
        self.message = "Token is invalid."
        super().__init__(self.message, 403)


class UserTokenExpired(UserException):
    def __init__(self):
        self.message = "Token has expired."
        super().__init__(self.message, 403)
