
import pytest

import codepost_stats.analyzers.abstract.base


SOME_NAME = "some-name"
SOME_STRING = "  Some weird  String "
ABSTRACT_METHOD_NAMES = [
    "_reset",
    "_event_course",
    "_event_assignment",
    "_event_submission",
    "_event_file",
    "_event_comment",
]


class TestAbstractAnalyzer:

    @pytest.fixture()
    def obj(self):
        return codepost_stats.analyzers.abstract.base.AbstractAnalyzer()

    def test_name_init(self, obj):
        assert obj._name is None
        assert obj.name == ""

    def test_name_changed(self, obj):
        assert obj._name is None
        obj._name = SOME_NAME
        assert obj._name == SOME_NAME
        assert obj.name == SOME_NAME

    def test_abstract_methods(self, obj):
        for abs_method_name in ABSTRACT_METHOD_NAMES:
            try:
                method = getattr(obj, abs_method_name)
            except AttributeError as exc:
                raise AssertionError(
                    "missing method '{}' from interface".format(
                        abs_method_name,
                    )
                ) from exc

            # should just pass
            method()

        # should not have exited previously
        assert True

    def test_normalize_str_none(self, obj):
        assert obj._normalize_str(s=None) == ""

    def test_normalize_str(self, obj):
        # reproduce the normalization on our own to ensure its what
        # is implemented
        original = SOME_STRING
        computed = original.strip().lower().replace(" ", "-")

        assert (obj._normalize_str(s=original) == computed)


class TestBaseAnalyzer:

    @pytest.fixture()
    def obj(self):
        return codepost_stats.analyzers.abstract.base.BaseAnalyzer()

    @pytest.fixture()
    def val(self, mocker):
        return mocker.MagicMock()

    def test_name_init(self, obj):
        assert obj._name is None
        assert obj.name == ""

    def test_name_changed(self, obj):
        assert obj._name is None
        obj._name = SOME_NAME
        assert obj._name == SOME_NAME
        assert obj.name == SOME_NAME

    def test_course_init(self, obj):
        assert obj._course is None
        assert obj.course is None

    def test_course_changed(self, obj, mocker):
        # assert we know initial value to be None
        assert obj._course is None

        # assert modification worked
        obj._course = mocker.MagicMock()
        assert obj.course is not None

        # reset obj to erase course
        assert obj._reset()
        assert obj._course is None
        assert obj.course is None

    def test_event_course(self, obj, val):
        obj._event_course(course=val)
        assert True

    def test_event_assignment(self, obj, val):
        obj._event_assignment(assignment=val)
        assert True

    def test_event_submission(self, obj, val):
        obj._event_submission(assignment=val, submission=val)
        assert True

    def test_event_file(self, obj, val):
        obj._event_file(assignment=val, submission=val, file=val)
        assert True

    def test_event_comment(self, obj, val):
        obj._event_comment(assignment=val, submission=val, file=val, comment=val)
        assert True
