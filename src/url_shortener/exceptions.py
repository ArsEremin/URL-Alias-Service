from fastapi import HTTPException, status


class BaseUrlException(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Url exception"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class InvalidSiteException(BaseUrlException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message):
        self.detail = message
        super().__init__()


class InvalidUrlTokenException(BaseUrlException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, url):
        self.detail = f"URL '{url}' doesn't exist"
        super().__init__()


class InactiveUrlException(BaseUrlException):
    status_code = status.HTTP_410_GONE
    detail = "Inactive URL"


class ExpiredUrlException(BaseUrlException):
    status_code = status.HTTP_410_GONE
    detail = "Url expired"
