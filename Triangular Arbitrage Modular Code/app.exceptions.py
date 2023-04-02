class ApiRequestError(Exception):
    """An exception class to represent API request errors.""" 

    def __init__(self, message: str):
        """
        Initialize the ApiRequestError exception with a message. 

        :param message: The error message.
        """
        super().__init__(message)


class CacheError(Exception):
    """An exception class to represent cache errors.""" 

    def __init__(self, message: str):
        """
        Initialize the CacheError exception with a message. 

        :param message: The error message.
        """
        super().__init__(message)
