
import pytest

import codepost_stats.analyzers.abstract.base
import codepost_stats.event_loop


SOME_NAME = "some-name"
SOME_ANALYZER_NAME = "some.analyzer.name"
SOME_OTHER_ANALYZER_NAME = "some.other.analyzer.name"
SOME_EVENT_HANDLER_NAME = "_reset"
SOME_ARGUMENTS = {"arg": "blah"}
SOME_EMPTY_LIST = list()

SOME_ASSIGNMENT_NAME = "Hello"

SOME_COURSE_NAME = "CS101"
SOME_COURSE_TERM = "F2020"


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


class TestCourseAnalyzerEventLoop:

    @pytest.fixture()
    def obj(self, mocker):
        # mock course list
        mocker.patch("codepost.course.list_available", mocker.Mock(return_value=[
            mocker.MagicMock(),
        ]))

        return codepost_stats.event_loop.CourseAnalyzerEventLoop(
            course_name=SOME_COURSE_NAME,
            course_term=SOME_COURSE_TERM,
        )

    def test_init(self, obj):
        assert obj._analyzer_pool is not None

    def test_init_errors(self, obj, mocker):
        with pytest.raises(ValueError):
            codepost_stats.event_loop.CourseAnalyzerEventLoop(
                course_name=None,
                course_term=None,
            )

        with pytest.raises(ValueError):
            codepost_stats.event_loop.CourseAnalyzerEventLoop(
                course_name=SOME_COURSE_NAME,
                course_term=None,
            )

        mocker.patch("codepost.course.list_available", mocker.Mock(return_value=[]))
        with pytest.raises(ValueError):
            codepost_stats.event_loop.CourseAnalyzerEventLoop(
                course_name=SOME_COURSE_NAME,
                course_term=SOME_COURSE_TERM,
            )

    def test_attributes(self, obj):
        assert obj.course == obj._course
        assert obj.assignments == obj._assignments

        assert obj._all_names is None
        assert issubclass(type(obj.names), list)
        assert len(obj.names) == 0

        obj.assignments = None
        obj.assignments = list()

    def test_run_empty(self, obj):
        obj.run()

    def test_get_by_name_empty(self, obj):
        obj.get_by_name(name=SOME_NAME)

    def test_get_by_name_one(self, obj, mocker):
        fake_analyzer = mocker.Mock(
            name=SOME_OTHER_ANALYZER_NAME,
            names=SOME_EMPTY_LIST,
            get_by_name=mocker.Mock(return_value=SOME_ARGUMENTS))

        obj.__dict__["_analyzer_pool"] = dict()
        obj.__dict__["_analyzer_pool"][SOME_ANALYZER_NAME] = fake_analyzer

        obj.get_by_name(name=SOME_NAME)
        fake_analyzer.get_by_name.assert_called_once()

        obj._refresh_all_names()

    def test_run_branches(self, obj, mocker):

        def first_arg(x, *args, **kwargs):
            return x

        obj._reset_course = lambda: None
        m = mocker.patch("tqdm.auto.tqdm", side_effect=first_arg)

        comment = mocker.Mock()
        file = mocker.Mock(comments=[comment])
        submission = mocker.Mock(files=[file])
        assignment = mocker.Mock(list_submissions=mocker.Mock(return_value=[submission]))
        assignments = mocker.Mock(
            __iter__=mocker.Mock(return_value=iter([SOME_ASSIGNMENT_NAME])),
            by_name=mocker.Mock(return_value=assignment))
        course = mocker.Mock(assignments=assignments)

        obj._course = course
        obj._assignments = [SOME_ASSIGNMENT_NAME]

        obj.run()

        # assert the method has been called twice (assignment + submissions)
        # (the extra 2 calls is for the last iteration of those loops)
        assert len(m.mock_calls) == 4
