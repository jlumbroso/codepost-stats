
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
    _name = "comments.counter"

    _min_characters = None
    _min_words = None
    _only_grader = True

    @property
    def min_characters(self) -> typing.Optional[int]:
        return self._min_characters

    @min_characters.setter
    def min_characters(self, value: typing.Optional[int]):
        self._min_characters = codepost_stats.helpers.check_int_like(value)

    @property
    def min_words(self) -> typing.Optional[int]:
        return self._min_words

    @min_words.setter
    def min_words(self, value: typing.Optional[int]):
        self._min_words = codepost_stats.helpers.check_int_like(value)

    @property
    def only_graders(self) -> bool:
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

