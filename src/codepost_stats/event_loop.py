
import typing

import codepost
import codepost.models.courses
import tqdm
import tqdm.auto

import codepost_stats.analyzers.abstract.base
import codepost_stats.analyzers.pool


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "AbstractAnalyzerEventLoop",
    "CourseAnalyzerEventLoop",
]

_tqdm_disabled = False
_only_subs = 10


class AbstractAnalyzerEventLoop:

    _analyzer_pool = None

    def __init__(
            self,
    ):
        self._analyzer_pool = codepost_stats.analyzers.pool.AnalyzerPool()

    def _check_analyzer_pool(self):
        if self._analyzer_pool is None:
            raise RuntimeError(
                "The event loop's analyzer pool has not been initialized."
            )

    def register(
            self,
            analyzer: typing.Union[codepost_stats.analyzers.abstract.base.BaseAnalyzer, type],
            name: typing.Optional[str] = None,
    ) -> typing.NoReturn:
        self._check_analyzer_pool()

        if type(analyzer) is type:
            if issubclass(
                    analyzer,
                    codepost_stats.analyzers.abstract.base.AbstractAnalyzer
            ):
                try:
                    analyzer = analyzer()

                except TypeError as exc:
                    raise TypeError(
                        "provided `analyzer` seems to require initialization parameters",
                        exc,
                    )
            else:
                raise TypeError(
                    "provided `analyzer` type is not an `AbstractAnalyzer` type"
                )

        return self._analyzer_pool.register(
            analyzer=analyzer,
            name=name,
        )

    def reset(self):
        self._check_analyzer_pool()
        return self._analyzer_pool.fire_event_reset()

    def run(self):
        raise NotImplementedError(
            "This is an abstract class. This method must be overriden and implemented."
        )


class CourseAnalyzerEventLoop(AbstractAnalyzerEventLoop):

    _assignments = None
    _course_name = None
    _course_term = None
    _course = None

    def __init__(
            self,
            course_name: str,
            course_term: str,
    ):
        super().__init__()
        self._course_name = course_name
        self._course_term = course_term
        self._reset_course()
        self._assignments = self._possible_assignment_names()

    def _reset_course(
            self,
            course_name: typing.Optional[str] = None,
            course_term: typing.Optional[str] = None,
    ):
        if course_name is None:
            course_name = self._course_name

        if course_term is None:
            course_term = self._course_term

        if self._course_name is None:
            raise ValueError("course name is None")

        if self._course_term is None:
            raise ValueError("course term is None")

        results = codepost.course.list_available(
            name=self._course_name,
            period=self._course_term,
        )

        if len(results) == 0:
            raise ValueError(
                "cannot find course with name '{name}' and term '{term}'".format(
                    name=course_name,
                    term=course_term,
                )
            )

        self._course = results[0]

        if self._assignments is not None:
            self._assignments = self._filter_possible_assignment_names(self._assignments)

    def _possible_assignment_names(self) -> typing.List[str]:
        return list(map(
            lambda assignment: assignment.name,
            sorted(self._course.assignments,
                   key=lambda assignment: assignment.sortKey)))

    def _filter_possible_assignment_names(self, lst: typing.List[str]) -> typing.List[str]:
        _possible_assignment_names = self._possible_assignment_names()
        return list(filter(
            lambda x: x in _possible_assignment_names,
            lst
        ))

    @property
    def course(self) -> codepost.models.courses.Courses:
        return self._course

    @property
    def assignments(self) -> typing.List[str]:
        return self._assignments

    @assignments.setter
    def assignments(self, value: typing.List[str]) -> typing.NoReturn:
        if value is not None:
            value = self._filter_possible_assignment_names(value)
        else:
            value = list()

        self._assignments = value

    def _refresh_all_names(self) -> typing.List[str]:
        all_names = set()
        for (analyzer_name, analyzer) in self._analyzer_pool.items():
            all_names.update(analyzer.names)
        self._all_names = list(all_names)
        return self._all_names

    @property
    def names(self) -> typing.List[str]:
        return self._all_names

    def get_by_name(
            self,
            name: str,
    ):
        record = dict()
        for (analyzer_name, analyzer) in self._analyzer_pool.items():
            record[analyzer_name] = analyzer.get_by_name(name=name)
        return record

    def run(self):

        self._reset_course()
        assignments = self._course.assignments

        for assignment_name in tqdm.auto.tqdm(
                self.assignments,
                desc="Assignments",
                disable=_tqdm_disabled,
        ):
            assignment = assignments.by_name(assignment_name)

            self._analyzer_pool.fire_event_assignment(assignment=assignment)

            tqdm.auto.tqdm.write("Downloading submissions for '{}'...".format(assignment_name))

            submissions = assignment.list_submissions()[:_only_subs]

            tqdm.auto.tqdm.write("Download complete: '{}' has {} submissions".format(
                assignment_name, len(submissions)))

            for submission in tqdm.auto.tqdm(
                    submissions,
                    desc="Submissions for {}".format(assignment_name),
                    leave=False,
                    disable=_tqdm_disabled,
            ):

                self._analyzer_pool.fire_event_submission(
                    assignment=assignment,
                    submission=submission
                )

                for file in submission.files:

                    self._analyzer_pool.fire_event_file(
                        assignment=assignment,
                        submission=submission,
                        file=file,
                    )

                    for comment in file.comments:

                        self._analyzer_pool.fire_event_comment(
                            assignment=assignment,
                            submission=submission,
                            file=file,
                            comment=comment,
                        )

        self._refresh_all_names()
