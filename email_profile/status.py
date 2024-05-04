"""
Staus Module
"""

from typing import List


class StatusResponse:

    def __init__(self, type: bool, message: str) -> None:
        self.type = type
        self.message = message


class Status:

    OK = 'OK'
    NO = 'NO'
    BAD = 'BAD'

    @staticmethod
    def validate_status(
            status: str,
            raise_error: bool = True) -> StatusResponse:
        data = {
            Status.OK: (
                True,
                "Login completed, now in authenticated state"),
            Status.NO: (
                False,
                "Login failure: user name or password rejected"),
            Status.BAD: (
                False,
                "Command unknown or arguments invalid")
        }.get(status, (False, "Unknown error"))

        if raise_error:
            if not data[0]:
                raise Exception(data[1])

        return StatusResponse(
            type=data[0],
            message=data[1]
        )

    @staticmethod
    def validate_data(data: List[str]) -> List[str]:
        data = [x.decode() for x in data[0].split()]
        if len(data) == 1 and not data[0]:
            return []
        return data
