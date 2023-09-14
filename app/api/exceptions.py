from http import HTTPStatus


class CasWebError(Exception):
    message: str
    http_status_code: HTTPStatus

    def __init__(self,
                 message: str,
                 http_status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,
                 *args):
        super().__init__(message, http_status_code, *args)
        self.message = message
        self.http_status_code = http_status_code

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(message='{self.message}', http_status_code={self.http_status_code})"
