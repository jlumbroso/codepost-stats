
import pytest

import codepost_stats.analyzers.abstract.base
import codepost_stats.event_loop


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


class TestAbstractAnalyzerEventLoop:

    @pytest.fixture()
    def obj(self):
        return codepost_stats.event_loop.AbstractAnalyzerEventLoop()

    def test_init(self, obj):
        assert obj._analyzer_pool is not None

    def test_check(self, obj):
        assert obj._analyzer_pool is not None
        obj._check_analyzer_pool()

        obj._analyzer_pool = None
        with pytest.raises(RuntimeError):
            obj._check_analyzer_pool()

    def test_reset(self, obj):
        obj.reset()

    def test_run(self, obj):
        with pytest.raises(NotImplementedError):
            obj.run()

    def test_register_simple(self, obj, analyzer):
        obj.register(analyzer)

    def test_register_type_arg(self, obj, mocker):
        obj.register(codepost_stats.analyzers.abstract.base.BaseAnalyzer)

    def test_register_type_error(self, obj, analyzer, mocker):

        p_issubclass = mocker.patch("codepost_stats.event_loop.issubclass",
                                    mocker.Mock(return_value=True))

        p_type = mocker.patch("codepost_stats.event_loop.type",
                              mocker.Mock(return_value=type))

        p_analyzer = mocker.Mock(side_effect=TypeError)

        with pytest.raises(TypeError):
            obj.register(analyzer=p_analyzer)

        p_type.assert_called()
        p_issubclass.assert_called()
        p_analyzer.assert_called()

        p_issubclass = mocker.patch("codepost_stats.event_loop.issubclass",
                                    mocker.Mock(return_value=False))

        p_analyzer = mocker.Mock(side_effect=TypeError)

        with pytest.raises(TypeError):
            obj.register(analyzer=p_analyzer)

        p_issubclass.assert_called()
        p_analyzer.assert_not_called()
