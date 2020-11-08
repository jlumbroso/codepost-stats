
import pytest

import codepost_stats.helpers


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
