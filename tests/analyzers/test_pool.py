
import pytest

import codepost_stats.analyzers.abstract.base
import codepost_stats.analyzers.pool


SOME_ANALYZER_NAME = "some.analyzer.name"
SOME_OTHER_ANALYZER_NAME = "some.other.analyzer.name"
SOME_EVENT_HANDLER_NAME = "_reset"
SOME_ARGUMENTS = {"arg": "blah"}


@pytest.fixture()
def analyzer():
    analyzer = codepost_stats.analyzers.abstract.base.BaseAnalyzer()
    analyzer._name = SOME_ANALYZER_NAME
    return analyzer


@pytest.fixture()
def fake_analyzer(mocker):
    return mocker.Mock(name=SOME_ANALYZER_NAME)


class TestAbstractAnalyzerPool:

    @pytest.fixture()
    def obj(self):
        return codepost_stats.analyzers.pool.AbstractAnalyzerPool()

    def test_init(self, obj):
        assert obj._registered_analyzers is not None
        assert issubclass(type(obj._registered_analyzers), dict)
        assert len(list(obj.__iter__())) == 0

    def test_keys_empty(self, obj):
        assert len(list(obj.keys())) == 0
        obj._registered_analyzers = None
        assert len(list(obj.keys())) == 0

    def test_values_empty(self, obj):
        assert len(list(obj.values())) == 0
        obj._registered_analyzers = None
        assert len(list(obj.values())) == 0

    def test_items_empty(self, obj):
        assert len(list(obj.items())) == 0
        obj._registered_analyzers = None
        assert len(list(obj.items())) == 0

    def test_analyzers(self, obj):
        obj.analyzers()
        assert True

    def test_register_type_error(self, obj, fake_analyzer, mocker):
        # check if register raises an error if not BaseAnalyzer
        with pytest.raises(TypeError):
            obj.register(analyzer=fake_analyzer)

        fake_analyzer = mocker.Mock(spec=[])
        with pytest.raises(TypeError):
            obj.register(analyzer=fake_analyzer)

    def test_register_none(self, obj):
        assert len(obj._registered_analyzers) == 0
        obj.register(analyzer=None)
        assert len(obj._registered_analyzers) == 0

    def test_register(self, obj, analyzer):
        assert obj._registered_analyzers is not None
        assert len(obj._registered_analyzers) == 0

        # see if register is successful an increments number of
        # analyzers
        obj.register(analyzer=analyzer)
        assert len(obj._registered_analyzers) == 1

        # see if reinit analyzers pool if set to None
        obj._registered_analyzers = None
        obj.register(analyzer=analyzer)
        assert len(obj._registered_analyzers) == 1

        # should write over
        obj.register(analyzer=analyzer)
        assert len(obj._registered_analyzers) == 1

    def test_register_two_analyzers(self, obj, analyzer):
        obj._registered_analyzers = None

        analyzer._name = SOME_ANALYZER_NAME
        obj.register(analyzer=analyzer)
        assert len(obj._registered_analyzers) == 1

        analyzer._name = SOME_OTHER_ANALYZER_NAME
        obj.register(analyzer=analyzer)
        assert len(obj._registered_analyzers) == 2

    def test_fire_event_error(self, obj, fake_analyzer, mocker):

        # insert dummy record (breaks abstraction but this is a test)
        obj._registered_analyzers = dict()
        obj._registered_analyzers[fake_analyzer.name] = fake_analyzer

        # check if register raises an error if not BaseAnalyzer
        obj.fire_event(event_handler_name=SOME_EVENT_HANDLER_NAME)

        obj.fire_event(event_handler_name=SOME_EVENT_HANDLER_NAME, arguments=SOME_ARGUMENTS)

        obj._registered_analyzers[fake_analyzer.name] = mocker.Mock(spec=[])
        with pytest.raises(AttributeError):
            obj.fire_event(event_handler_name=SOME_EVENT_HANDLER_NAME)

        obj._registered_analyzers[fake_analyzer.name] = mocker.Mock(
            _reset=mocker.Mock(side_effect=AttributeError))
        obj.fire_event(event_handler_name=SOME_EVENT_HANDLER_NAME)


def test_analyzer_pool(mocker):
    obj = codepost_stats.analyzers.pool.AnalyzerPool()

    dummy = mocker.Mock()

    obj.fire_event_reset()
    obj.fire_event_course(course=dummy)
    obj.fire_event_assignment(assignment=dummy)
    obj.fire_event_submission(assignment=dummy, submission=dummy)
    obj.fire_event_file(assignment=dummy, submission=dummy, file=dummy)
    obj.fire_event_comment(assignment=dummy, submission=dummy, file=dummy, comment=dummy)

