
import typing

import codepost.models.assignments
import codepost.models.comments
import codepost.models.courses
import codepost.models.files
import codepost.models.submissions

import codepost_stats.analyzers.abstract.base


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "AbstractAnalyzerPool",
    "AnalyzerPool",
]


class AbstractAnalyzerPool:

    _registered_analyzers = None

    def __init__(self):
        self._registered_analyzers = dict()

    def __iter__(self) -> typing.Iterable[codepost_stats.analyzers.abstract.base.BaseAnalyzer]:
        return self.values()

    def keys(self) -> typing.List[str]:
        if self._registered_analyzers is None:
            self.__init__()

        return list(self._registered_analyzers.keys())

    def values(self) -> typing.List[codepost_stats.analyzers.abstract.base.BaseAnalyzer]:
        if self._registered_analyzers is None:
            self.__init__()

        return list(self._registered_analyzers.values())

    def items(self) -> typing.List[typing.Tuple[str, codepost_stats.analyzers.abstract.base.BaseAnalyzer]]:
        if self._registered_analyzers is None:
            self.__init__()

        return list(self._registered_analyzers.items())

    def analyzers(self) -> typing.List[codepost_stats.analyzers.abstract.base.BaseAnalyzer]:
        return self.values()

    def register(
            self,
            analyzer: codepost_stats.analyzers.abstract.base.BaseAnalyzer,
            name: typing.Optional[str] = None,
    ) -> typing.NoReturn:
        # name from the analyzer
        if name is None:
            name = analyzer.name

        # made up name
        if name is None:
            i = 0
            analyzer_count = len(list(self.__iter__()))
            while name is None or name in self.keys():
                name = "unnamed-analyzer-{}".format(analyzer_count + i)
                i += 1

        if self._registered_analyzers is None:
            self.__init__()

        if issubclass(type(analyzer), codepost_stats.analyzers.abstract.base.BaseAnalyzer):
            self._registered_analyzers[name] = analyzer

        else:
            raise TypeError(
                "analyzer '{}' not a child of `BaseAnalyzer`".format(
                    analyzer
                )
            )


class AnalyzerPool(AbstractAnalyzerPool):

    def fire_event_reset(self):
        success = 0
        failure = 0
        for analyzer in self.analyzers():
            try:
                analyzer._reset()
                success += 1
            except:
                failure += 1
        return (success, failure)

    def fire_event_course(
            self,
            course: codepost.models.courses.Courses,
    ):
        success = 0
        failure = 0
        for analyzer in self.analyzers():
            try:
                analyzer._event_course(
                    course=course,
                )
                success += 1
            except:
                failure += 1
        return (success, failure)

    def fire_event_assignment(
            self,
            assignment: codepost.models.assignments.Assignments,
    ):
        success = 0
        failure = 0
        for analyzer in self.analyzers():
            try:
                analyzer._event_assignment(
                    assignment=assignment,
                )
                success += 1
            except:
                failure += 1
        return (success, failure)

    def fire_event_submission(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
    ):
        success = 0
        failure = 0
        for analyzer in self.analyzers():
            try:
                analyzer._event_submission(
                    assignment=assignment,
                    submission=submission,
                )
                success += 1
            except:
                failure += 1
        return (success, failure)

    def fire_event_file(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
    ):
        success = 0
        failure = 0
        for analyzer in self.analyzers():
            try:
                analyzer._event_file(
                    assignment=assignment,
                    submission=submission,
                    file=file,
                )
                success += 1
            except:
                failure += 1
        return (success, failure)

    def fire_event_comment(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
            comment: codepost.models.comments.Comments,
    ):
        success = 0
        failure = 0
        for analyzer in self.analyzers():
            try:
                analyzer._event_comment(
                    assignment=assignment,
                    submission=submission,
                    file=file,
                    comment=comment,
                )
                success += 1
            except:
                failure += 1
        return (success, failure)
