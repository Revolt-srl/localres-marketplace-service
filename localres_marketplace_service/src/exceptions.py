from typing import Any

from fastapi import HTTPException


class HTTPConvertibleException(Exception):

    def __init__(
        self,
        original_object: Exception | HTTPException | str | dict | list | None = None,
        status_code: int = 500,
        detail: dict = {},
    ) -> None:

        # super().__init__(*args)

        self.status_code = status_code
        if original_object:

            if isinstance(original_object, HTTPConvertibleException):
                self.detail = original_object.detail
                self.status_code = original_object.status_code
                return

            if isinstance(original_object, HTTPException):
                self.detail = original_object.detail
                self.status_code = original_object.status_code
                return

            if isinstance(original_object, Exception):
                self.status_code = 500
                self.detail = str(original_object)
                return

            if (
                isinstance(original_object, dict)
                or isinstance(original_object, list)
                or isinstance(original_object, str)
            ):
                self.detail = original_object
                return

        self.detail = detail

    def to_http(self) -> HTTPException:
        return HTTPException(
            status_code=self.status_code,
            detail={
                "exception": self.__class__.__name__,
                "original_message": str(self),
                "detail": self.detail,
            },
        )

    def to_dict(self) -> dict:
        return {
            "status_code": self.to_http().status_code,
            **self.to_http().detail,  # type: ignore
        }

    def serialize(self) -> str:
        return str(self.to_dict())


class Base400(HTTPConvertibleException):
    def __init__(self, *args: Any, detail: dict = {}) -> None:
        super().__init__(*args, status_code=400, detail=detail)


class Base500(HTTPConvertibleException):
    def __init__(self, *args: Any, detail: dict = {}) -> None:
        super().__init__(*args, status_code=500, detail=detail)


class UnexpectedError(Base500):
    ...


def panic(exception: HTTPConvertibleException | Exception):
    if isinstance(exception, HTTPConvertibleException):
        raise exception.to_http()
    raise UnexpectedError(exception).to_http()
