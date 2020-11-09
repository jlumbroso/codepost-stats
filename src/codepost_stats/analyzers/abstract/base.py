"""
This submodule contains the abstract interfaces for a codePost statistic
analyzer.

The classes implemented here are the parent classes used to build the generic
analyzers implemented in the related submodule,
:py:mod:`codepost_stats.analyzers.abstract.simple`, that serve as building
blocks for fully implemented analyzers.

Examples of fully-fledged standard analyzers (to do task such as counting
the number of submissions graded, or the number of comments authored, etc.),
are available in the :py:mod:`codepost_stats.analyzers.standard` submodule.
These can serve as templates illustrating how to implement custom analyzers.
"""

import typing

import codepost.models.assignments
import codepost.models.comments
import codepost.models.courses
import codepost.models.files
import codepost.models.submissions


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "AbstractAnalyzer",
    "BaseAnalyzer",
]


class AbstractAnalyzer:
    """
    The :py:class:`AbstractAnalyzer` class is an abstract class for a codePost
    analyzer object.

    This abstract analyzer class has a number of protected members, such as
    :py:func:`_event_course()`, for each of the different objects within the
    codePost object model. The analyzer are supposed to be registered with an
    event loop object, some subclass of
    :py:class:`codepost_stats.event_loop.AbstractAnalyzerEventLoop`; once the
    event loop is run, it walks through a subset of a codePost course's data
    and triggers events in all registered analyzers.

    In this way, the analyzer will walk through the codePost data in
    *depth-first search* order, which means, for instance, that all submissions
    of the first assignment will be examined before moving on to the second
    assignment, and so on.

    Some standard analyzers are provided, such as those in the submodule
    :py:mod:`codepost_stats.analyzers.standard`, but new ones can easily
    be authored by overriding one of the provided classes.

    .. warning::
        This abstract does not do anything, it is meant to be the least
        restrictive interface for an analyzer, and is intended to be used
        mainly as an abstract data type in type signatures.

        For most purposes, the :py:class:`BaseAnalyzer` class (or a subclass)
        should be overridden instead.
    """

    # internal name of the analyzer (to be set likely in overridden constructors)
    _name: typing.Optional[str] = None

    @property
    def name(self) -> str:
        """
        Get a string representing the analyzer, such as ``comments.counter.rubric``,
        that can be used when rendering the output of multiple analyzers.

        This name is meant to be informative: By default, it is the same for
        every instance of the analyzer class; and there are no guarantees that
        it is necessarily unique across all analyzers.

        :return: An internal string describing the analyzer
        """
        return self._name or ""

    def _reset(self) -> bool:
        """
        Resets the internal state of the analyzer.

        :return: A boolean indicated whether the reset was successful
        """
        pass

    def _event_course(self, *args, **kwargs):
        """
        Event triggered when a codePost course is visited by an event loop. This
        event does nothing in this abstract analyzer class.
        """
        pass

    def _event_assignment(self, *args, **kwargs):
        """
        Event triggered when a codePost assignment is visited by an event loop. This
        event does nothing in this abstract analyzer class.
        """
        pass

    def _event_submission(self, *args, **kwargs):
        """
        Event triggered when a codePost submission is visited by an event loop. This
        event does nothing in this abstract analyzer class.
        """
        pass

    def _event_file(self, *args, **kwargs):
        """
        Event triggered when a codePost file is visited by an event loop. This
        event does nothing in this abstract analyzer class.
        """
        pass

    def _event_comment(self, *args, **kwargs):
        """
        Event triggered when a codePost comment is visited by an event loop. This
        event does nothing in this abstract analyzer class.
        """
        pass

    # noinspection PyMethodMayBeStatic
    def _normalize_str(
            self,
            s: typing.Optional[str],
    ) -> str:
        """
        Returns a normalized string for purposes of internal string comparisons.

        The normalization involves: Returning an empty string if the input parameter
        is :py:data:`None`, otherwise remove leading and trailing spaces, change all
        alphabetical characters to lowercase, and replace internal spaces with dashes.

        :param s: A string to be normalized

        :return: The input string :py:data:`s` with some transformations
        """

        if s is None:
            return ""
        return s.strip().lower().replace(" ", "-")


class BaseAnalyzer(AbstractAnalyzer):
    """
    The :py:class:`BaseAnalyzer` class is an abstract class for a codePost
    analyzer object, which expands on the :py:class:`AbstractAnalyzer` by
    providing completed event signatures with the related codePost models;
    it also keeps track of which course is currently being analyzed.

    For most purposes, this is the class that should be overridden to author
    new analyzer modules, as illustrated in :py:mod:`codepost_stats.analyzers.standard`.
    """

    _name: typing.Optional[str] = None
    _course: typing.Optional[codepost.models.courses.Courses] = None

    @property
    def name(self) -> str:
        return self._name or ""

    @property
    def course(self) -> typing.Optional[codepost.models.courses.Courses]:
        """
        Get the currently analyzed codePost course.

        This property is updated by the :py:class:`BaseAnalyzer` class
        when an :py:func:`_event_course` is triggered; if it is accessed
        before such an event is triggered, the value returned will be
        :py:data:`None`.

        :return: The codepost course being analyzed
        """
        return self._course

    def _reset(self) -> bool:
        self._course = None
        return True

    def _event_course(
            self,
            course: codepost.models.courses.Courses,
    ):
        """
        Event triggered when a codePost course is visited by an event loop.

        :param course: The codePost course
        """

        self._course = course
        pass

    def _event_assignment(
            self,
            assignment: codepost.models.assignments.Assignments,
    ):
        """
        Event triggered when a codePost assignment is visited by an event loop.
        The course containing the assignment can be accessed through this class'
        :py:attr:`course` attribute.

        :param assignment: The codePost assignment
        """

        pass

    def _event_submission(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
    ):
        """
        Event triggered when a codePost submission is visited by an event loop.
        The course containing the assignment can be accessed through this class'
        :py:attr:`course` attribute.

        :param assignment: The codePost assignment
        :param submission: The codePost submission
        """

        pass

    def _event_file(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
    ):
        """
        Event triggered when a codePost file is visited by an event loop.
        The course containing the assignment can be accessed through this class'
        :py:attr:`course` attribute.

        :param assignment: The codePost assignment
        :param submission: The codePost submission
        :param file: The codePost file
        """

        pass

    def _event_comment(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
            comment: codepost.models.comments.Comments,
    ):
        """
        Event triggered when a codePost comment is visited by an event loop.
        The course containing the assignment can be accessed through this class'
        :py:attr:`course` attribute.

        :param assignment: The codePost assignment
        :param submission: The codePost submission
        :param file: The codePost file
        :param comment: The codePost comment
        """

        pass
