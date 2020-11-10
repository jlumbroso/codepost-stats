"""
This submodule contains standard analyzers for codePost data, representing the typical
kind of statistics that a codePost instructor might want to collect. In addition, the
code of these analyzers may provide a good starting base for authoring new analyzers.
"""

import typing

import codepost.models.assignments
import codepost.models.comments
import codepost.models.files
import codepost.models.submissions

import codepost_stats.analyzers.abstract.simple
import codepost_stats.helpers


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "SubmissionsGradedCounter",

    "GenericCommentsCounter",
    "RubricCommentsCounter",
    "CustomCommentsCounter",
]


class SubmissionsGradedCounter(codepost_stats.analyzers.abstract.simple.CounterAnalyzer):
    """
    An analyzer class to count the number of submissions graded, for each assignment, by
    each grader.

    In terms of counter storage, the :py:data:`name` is the grader and the :py:data:`subcat`
    is the assignment name. Submissions will be ignored if they are not assigned to a grader,
    or if they are not yet finalized.
    """

    _name = "submissions.graded"

    def _event_submission(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
    ):
        # if no grader, nothing to do
        if submission.grader is None:
            return

        # if not finalized, do not want to count it
        if not submission.isFinalized:
            return

        # increase number of graded submission for grader by 1
        self._delta_counter(
            name=submission.grader,
            subcat=assignment.name,
            delta=1,
        )


class GenericCommentsCounter(codepost_stats.analyzers.abstract.simple.CounterAnalyzer):
    """
    An analyzer class to count the number of comments created, for each assignment,
    by each grader.

    This class has a number of properties to restrict which comments are
    included in the tally—depending on the number of characters, words, or whether
    the comment was authored by the grader of the submission.

    The subclasses :py:class:`CustomCommentsCounter` and :py:class:`RubricCommentsCounter`
    illustrate how to further restrict the kind of comments that are counted.

    In terms of counter storage, the :py:data:`name` is the author of a comment and
    the :py:data:`subcat` is the assignment name. Submissions will be ignored if they
    are not assigned to a grader, or if they are not yet finalized.
    """

    _name: str = "comments.counter"

    _min_characters: typing.Optional[int] = None
    _min_words: typing.Optional[int] = None
    _only_grader: bool = True

    @property
    def min_characters(self) -> typing.Optional[int]:
        """
        Gets or sets the minimum number of characters threshold, under which a comment
        will be ignored. To remove this threshold, set this property to :py:data:`None`.

        :rtype: typing.Optional[int]
        """
        return self._min_characters

    @min_characters.setter
    def min_characters(self, value: typing.Optional[int]):
        self._min_characters = codepost_stats.helpers.check_int_like(value)

    @property
    def min_words(self) -> typing.Optional[int]:
        """
        Gets or sets the minimum number of words threshold, under which a comment
        will be ignored. To remove this threshold, set this property to :py:data:`None`.

        .. note::
            If ``s`` is the string representing the text of the comment, the number of
            words is computed using the Python expression ``len(s.split())``.

        :rtype: typing.Optional[int]
        """

        return self._min_words

    @min_words.setter
    def min_words(self, value: typing.Optional[int]):
        self._min_words = codepost_stats.helpers.check_int_like(value)

    @property
    def only_graders(self) -> bool:
        """
        Gets and sets a flag that indicates whether to ignore any comment of which
        the author is not the same as the grader of the submission (this may be the
        case if a course instructor or administrator has added a comment to a
        submission that may have been graded by someone else, for instance).

        :rtype: bool
        """
        return self._only_grader

    @only_graders.setter
    def only_graders(self, value: bool):
        self._only_grader = value

    def _event_comment(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
            comment: codepost.models.comments.Comments,
    ):
        # if no grader, nothing to do
        if submission.grader is None:
            return

        # if not finalized, do not want to count it
        if not submission.isFinalized:
            return

        # check whether author is grader
        if self._only_grader and submission.grader != comment.author:
            return

        # filter comments based on size
        comment_text = comment.text
        if self._min_characters is not None:
            if len(comment_text) < self._min_characters:
                return

        if self._min_words is not None:
            if len(comment_text.split()) < self._min_words:
                return

        # increase number of graded submission for grader by 1
        self._delta_counter(
            name=comment.author,
            subcat=assignment.name,
            delta=1,
        )


class CustomCommentsCounter(GenericCommentsCounter):
    """
    An analyzer class to count the number of custom comments created (ignoring any
    comment that is tied to a rubric comment), for each assignment, by each grader.

    This class extends :py:class:`GenericCommentsCounter`, and contains all the
    capabilities of its parent class, in particular in terms of restricting comments
    by their character, word length or authorship.
    """

    _name = "comments.counter.custom"

    def _event_comment(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
            comment: codepost.models.comments.Comments,
    ):
        if comment.rubricComment is None:
            super()._event_comment(
                assignment=assignment,
                submission=submission,
                file=file,
                comment=comment,
            )


class RubricCommentsCounter(GenericCommentsCounter):
    """
    An analyzer class to count the number of comments created that are linked to a
    rubric comment (ignoring any custom comment), for each assignment, by each grader.

    This class extends :py:class:`GenericCommentsCounter`, and contains all the
    capabilities of its parent class, in particular in terms of restricting comments
    by their character, word length or authorship.
    """

    _name = "comments.counter.rubric"

    def _event_comment(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
            comment: codepost.models.comments.Comments,
    ):
        if comment.rubricComment is not None:
            super()._event_comment(
                assignment=assignment,
                submission=submission,
                file=file,
                comment=comment,
            )
