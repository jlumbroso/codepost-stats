"""

"""

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


SuccessFailurePairType = typing.Tuple[int, int]


class AbstractAnalyzerPool:

    _registered_analyzers: typing.Optional[typing.Dict[str, codepost_stats.analyzers.abstract.base.BaseAnalyzer]] = None

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

    # noinspection PyBroadException
    def fire_event(
            self,
            event_handler_name: str,
            arguments: typing.Optional[dict] = None,
    ) -> SuccessFailurePairType:

        # ensure this is a non-None value
        arguments = arguments or dict()

        # initialize counters
        success = 0
        failure = 0
        notfound = 0

        # trigger event for every analyzer

        for analyzer in self.analyzers():

            # get event handler function
            try:
                event_handler = getattr(analyzer, event_handler_name)
            except AttributeError:
                notfound += 1
                continue

            # trigger event handler
            try:
                event_handler(**arguments)
                success += 1
            except:
                failure += 1

        # if all failures stem from not found, report this as a separate
        # type of failure

        if failure == 0 and notfound > 0:
            raise AttributeError(
                "attempted to fire an event that exists for none of "
                "the registered analyzers: Could '{}' be a typo?".format(
                    event_handler_name,
                )
            )

        failure += notfound

        return success, failure


class AnalyzerPool(AbstractAnalyzerPool):

    def fire_event_reset(self) -> SuccessFailurePairType:
        return self.fire_event(
            "_reset",
        )

    def fire_event_course(
            self,
            course: codepost.models.courses.Courses,
    ) -> SuccessFailurePairType:
        return self.fire_event(
            "_event_course", {
                "course": course,
            })

    def fire_event_assignment(
            self,
            assignment: codepost.models.assignments.Assignments,
    ):
        return self.fire_event(
            "_event_assignment", {
                "assignment": assignment,
            })

    def fire_event_submission(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
    ):
        return self.fire_event(
            "_event_submission", {
                "assignment": assignment,
                "submission": submission,
            })

    def fire_event_file(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
    ):
        return self.fire_event(
            "_event_file", {
                "assignment": assignment,
                "submission": submission,
                "file": file,
            })

    def fire_event_comment(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
            comment: codepost.models.comments.Comments,
    ):
        return self.fire_event(
            "_event_comment", {
                "assignment": assignment,
                "submission": submission,
                "file": file,
                "comment": comment,
            })
