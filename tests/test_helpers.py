
import pytest

import codepost_stats.helpers


SOME_NEGATIVE_NUMBER = -10


def test_check_int_like_none():
    assert codepost_stats.helpers.check_int_like(None) is None

@pytest.mark.parametrize(
    "input, output", [
        (1, 1),
        ("1", 1),
        (1.0, 1),
        (True, 1),
        (False, 0),
    ]
)
def test_check_int_like_success(input, output):
    ret = codepost_stats.helpers.check_int_like(input)
    assert ret == output


@pytest.mark.parametrize("input", [
    "text", [], "",
])
def test_check_int_like_fail(input):
    with pytest.raises(TypeError):
        ret = codepost_stats.helpers.check_int_like(input)

def test_check_int_like_negative():
    assert codepost_stats.helpers.check_int_like(SOME_NEGATIVE_NUMBER) is None
