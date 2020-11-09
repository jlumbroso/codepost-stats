"""
This submodule contains the analyzer pool interface and an implementation.

An analyzer pool is a collection of analyzers, of which the events can be
triggered together by firing an event on the analyzer pool and have it
propagate to every analyzer registered in the pool. The analyzer pool is
the mechanism by which an event loop, such as those implemented in the
:py:mod:`codepost_stats.event_loop` submodule, can keep track of analyzers
and how to propagate events to them.
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
    "SuccessFailurePairType",
    "AbstractAnalyzerPool",
    "AnalyzerPool",
]


# importing this for convenience
BaseAnalyzer = codepost_stats.analyzers.abstract.base.BaseAnalyzer


class SuccessFailurePairType(typing.NamedTuple):
    """
    A helper type to report the number of event firings that were successful
    or a failure, when triggering events using an analyzer pool.
    """

    success: int = 0
    """
    Number of event firings that have succeeded.
    """

    failure: int = 0
    """
    Number of event firings that have failed.
    """


class AbstractAnalyzerPool:
    """
    An abstract interface for an analyzer pool, a collection of analyzer
    objects, of which the event handlers can be triggered together using
    :py:func:`fire_event` or some inherited method by an event loop.
    """

    _registered_analyzers: typing.Optional[typing.Dict[str, BaseAnalyzer]] = None

    def __init__(self):
        self._registered_analyzers = dict()

    def __iter__(self) -> typing.Iterable[BaseAnalyzer]:
        return self.values()

    def keys(self) -> typing.List[str]:
        """
        Returns a list of the names of all analyzers registered with this
        analyzer pool.

        To add an analyzer to this list, use the :py:func:`register` method.

        :return: A list of the names of all analyzers registered with this
            analyzer pool
        """

        if self._registered_analyzers is None:
            self.__init__()

        return list(self._registered_analyzers.keys())

    def values(self) -> typing.List[BaseAnalyzer]:
        """
        Returns a list of all analyzers registered with this analyzer pool.
        This function is an alias for the :py:func:`analyzers` function.

        To add an analyzer to this list, use the :py:func:`register` method.

        :return: A list of all analyzers registered with this analyzer pool
        """

        if self._registered_analyzers is None:
            self.__init__()

        return list(self._registered_analyzers.values())

    def items(self) -> typing.List[typing.Tuple[str, BaseAnalyzer]]:
        """
        Returns a list of all pairs of name and analyzer registered with
        this analyzer pool.

        To add an analyzer to this list, use the :py:func:`register` method.

        :return: A list of pairs ``(name, analyzer)`` of registered analyzers
        """
        if self._registered_analyzers is None:
            self.__init__()

        return list(self._registered_analyzers.items())

    def analyzers(self) -> typing.List[BaseAnalyzer]:
        """
        Returns a list of all analyzers registered with this analyzer pool.

        To add an analyzer to this list, use the :py:func:`register` method.

        :return: A list of all analyzers registered with this analyzer pool
        """
        return self.values()

    def register(
            self,
            analyzer: BaseAnalyzer,
            name: typing.Optional[str] = None,
    ) -> typing.NoReturn:
        """
        Adds an analyzer to the analyzer pool.

        This method adds the provided analyzer to the analyzer pool,
        optionally, using the name that is provided. If no name is
        provided, the method while try to use the :py:attr:`BaseAnalyzer.name`
        attribute; if this attribute is undefined, a random unique name
        will be generated.

        .. warning ::
            Names must be unique within the analyzer pool. Therefore
            if two analyzers are registered with the same name, the
            second will overwrite the first analyzer in this pool.

        :param analyzer: The analyzer to add to the pool
        :param name: An optional name under which to register the analyzer

        :raises TypeError: If the provided :py:data:`analyzer` is not
            a subclass of :py:class:`codepost_stats.analyzers.abstract.base.BaseAnalyzer`.
        """

        # no point
        if analyzer is None:
            return

        # name from the analyzer
        if name is None:
            try:
                name = getattr(analyzer, "name")
            except AttributeError:
                name = None

        if name is None:
            name = analyzer.__dict__.get("_name")

        # made up name
        if name is None:
            i = 0
            analyzer_count = len(list(self.__iter__()))
            while name is None or name in self.keys():
                name = "unnamed-analyzer-{}".format(analyzer_count + i)
                i += 1

        if self._registered_analyzers is None:
            self.__init__()

        if issubclass(type(analyzer), BaseAnalyzer):
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
        """
        Fires an event throughout all analyzers registed in the pool.

        This method takes :py:data:`event_handler_name`, a string, which
        is the name of the event handler to trigger in the registered
        analyzers, such as ``"_event_course"`` to trigger the event handler
        :py:func:`codepost_stats.analyzers.abstract.base.BaseAnalyzer._event_course`.

        This method also takes :py:data:`arguments`, an optional dictionary
        of arguments to pass to the event handler as a :py:data:`**kwargs`
        argument.

        To avoid blocking or interrupting the execution of an event loop,
        the event handlers are called within a try-catch block. When an event
        handler fails, this is tracked. The final count of event handlers
        that succeeded and those that failed is returned as a tuple of integers.

        :param event_handler_name: The name of the event handler to trigger
        :param arguments: The dictionary of arguments to provide the event handler

        :return: A pair reporting how many event triggers were successful and
            how many failed
        """

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

        return SuccessFailurePairType(
            success=success,
            failure=failure,
        )


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
