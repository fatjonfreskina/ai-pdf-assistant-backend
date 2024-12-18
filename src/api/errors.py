from flask import current_app
from typing import Tuple, Optional

class Error():
    """Generic error class, defines methods inherited by child classes.
    """
    def log_error(func):
        """Decorator to log the error when it is retrieved. 

        Args:
            func: the decorated function with the given error passed to get_error_instance() 
        """
        def wrapper(cls, key: str, exception : str = None):
            error = func(cls, key)
            if error and exception:
                current_app.logger.error(f"{cls.__name__} error retrieved: {error[0]} (Code: {error[1]}), (Exception: {exception})")
                return error
            
            if error:
                current_app.logger.error(f"{cls.__name__} error retrieved: {error[0]} (Code: {error[1]})")
                return error
            
            current_app.logger.error(f"Failed to retrieve error in {cls.__name__}, error key: {key}")
            return error
        return wrapper

    @classmethod
    @log_error
    def get_error_instance(cls, key: str, exception: str = None) -> Optional[Tuple[str, str]]:
        """Retrieve an error by its key and log it.

        Args:
            key (str): The key to retrieve the error.

        Returns:
            Optional[Tuple[str, str]]: The error message and code if the key exists, otherwise None.
        """
        return cls.errors.get(key)


class AuthenticationErrors(Error):
    """Defines authentication errors related to invalid tokens, protected paths, sign up/login failed, and many more.

    Args:
        Error: Inherits from Error class
    """
    TOKEN_EXPIRED = 'TOKEN_EXPIRED'
    INVALID_TOKEN = 'INVALID_TOKEN'
    AUTH_REQUIRED = 'AUTH_REQUIRED'
    USERNAME_ALREADY_TAKEN = 'USERNAME_ALREADY_TAKEN'
    EMAIL_ALREADY_TAKEN = 'EMAIL_ALREADY_TAKEN'
    INVALID_PASSWORD = 'INVALID_PASSWORD'
    LOGIN_FAILED = 'LOGIN_FAILED'
    INVALID_USER = 'INVALID_USER'
    SUDO_PASSWORD_INCORRECT = 'SUDO_PASSWORD_INCORRECT'
    
    errors = {
        TOKEN_EXPIRED:            ("Token expired, login again to get a new one.", "token_expired"),
        INVALID_TOKEN:            ("Signature verification failed", "invalid_token"),
        AUTH_REQUIRED:            ("Authorization is required to access this resource", "auth_required"),
        USERNAME_ALREADY_TAKEN:   ("Username already taken", "username_already_taken"),
        EMAIL_ALREADY_TAKEN:      ("Email already in use", "email_already_taken"),
        INVALID_PASSWORD:         ("Password is not valid", "invalid_password"),
        LOGIN_FAILED:             ("Login failed", "login_failed"),
        INVALID_USER:             ('The user who sent the request was not found', 'invalid_user'),
        SUDO_PASSWORD_INCORRECT:  ('The sudo password is incorrect', 'sudo_password_incorrect')
    }

class RequestErrors(Error):
    """Defines errors caused by frontend's requests
    """
    BAD_REQUEST_BODY_NOT_FOUND = 'BAD_REQUEST_BODY_NOT_FOUND'
    BAD_REQUEST_BODY_NOT_VALID =  'BAD_REQUEST_BODY_NOT_VALID'
    
    errors = {
        BAD_REQUEST_BODY_NOT_FOUND: ('Bad request from client side, a json body was expected', 'bad_request_body_not_found'),
        BAD_REQUEST_BODY_NOT_VALID: ('The request body was found, but its value is not valid', 'bad_request_body_not_valid')
    }

class ServerErrors(Error):
    """Defines errors caused by the server
    """
    INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'
    
    errors = {
        INTERNAL_SERVER_ERROR: ('An internal server error occured', 'internal_server_error')
    }    

class AiErrors(Error):
    """Defines errors occured during the calls to OpenAI's API

    Args:
        Error: Inherits methods from the Error class
    """
    CLIENT_RUN_FAIL = 'CLIENT_RUN_FAIL'
    REQUEST_FAILED = 'REQUEST_FAILED'
    UNHANDLED_EXCEPTION = 'UNHANDLED_EXCEPTION'
    FILE_NOT_FOUND = 'FILE_NOT_FOUND'
    FILENAME_NOT_ALLOWED = 'FILENAME_NOT_ALLOWED'
    ASSISTANT_NOT_FOUND = 'ASSISTANT_NOT_FOUND'

    errors = {
        'CLIENT_RUN_FAIL': ('The call to the AI API failed.', 'client_run_fail'),
        'REQUEST_FAILED': ('Communication to the AI API failed.', 'request_failed'),
        'UNHANDLED_EXCEPTION': ('An unhandled exception occured.', 'unhandled_exception'),
        'FILE_NOT_FOUND': ('The file was not found in the request', 'file_not_found'),
        'FILENAME_NOT_ALLOWED': ('The filename is not allowed', 'filename_not_allowed'),
        'ASSISTANT_NOT_FOUND': ('The assistant was not found', 'assistant_not_found')
    }


if __name__ == '__main__':
    AuthenticationErrors.get_error_instance(AuthenticationErrors.AUTH_REQUIRED, 'Test')
    AiErrors.get_error_instance(AiErrors.CLIENT_RUN_FAIL)
    AuthenticationErrors.get_error_instance('Not found')
