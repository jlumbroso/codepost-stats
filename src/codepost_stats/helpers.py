
import typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "check_int_like",
]


def check_int_like(value: typing.Optional[int]) -> typing.Optional[int]:
    if value is None:
        return value

    if type(value) is int:

        if value < 0:
            value = None

        return value

    try:
        value = int(value)

    except:
        raise TypeError(
            "provided value is not an integer"
        )

    return value