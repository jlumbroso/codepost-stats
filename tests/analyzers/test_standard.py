
import pytest

import codepost_stats.analyzers.standard


NAME_SUBMISSIONS_GRADED_COUNTER = "submissions.graded"
NAME_GENERIC_COMMENTS_COUNTER = "comments.counter"
NAME_CUSTOM_COMMENTS_COUNTER = "comments.counter.custom"
NAME_RUBRIC_COMMENTS_COUNTER = "comments.counter.rubric"

SOME_ASSIGNMENT_NAME = "Hello"
SOME_GRADER_NAME = "grader@domain.com"
SOME_OTHER_GRADER_NAME = "other.grader@domain.com"
SOME_COMMENT_TEXT = "this is some comment text"
SOME_COMMENT_AUTHOR = SOME_GRADER_NAME

NUMBER_ONE_DEFAULT_DELTA = 1

SOME_INT_VALUE = 7


# codePost fixtures

@pytest.fixture()
def assignment(mocker):
    assignment = mocker.Mock(name=SOME_ASSIGNMENT_NAME)
    return assignment


@pytest.fixture()
def submission(mocker):
    submission = mocker.Mock(grader=SOME_GRADER_NAME, isFinalized=True)
    return submission


@pytest.fixture()
def file(mocker):
    file = mocker.Mock()
    return file


@pytest.fixture()
def comment(mocker):
    comment = mocker.Mock(text=SOME_COMMENT_TEXT, author=SOME_COMMENT_AUTHOR)
    return comment


class TestSubmissionsGradedCounter:

    @pytest.fixture()
    def obj(self):
        return codepost_stats.analyzers.standard.SubmissionsGradedCounter()

    def test_init(self, obj):
        assert obj._name == NAME_SUBMISSIONS_GRADED_COUNTER

    def test_event_submission_success(self, obj, assignment, submission):
        obj._event_submission(assignment=assignment, submission=submission)
        assert obj._get_value(name=submission.grader, subcat=assignment.name) == NUMBER_ONE_DEFAULT_DELTA

    def test_event_submission_noop(self, obj, assignment, submission):
        submission.isFinalized = False
        obj._event_submission(assignment=assignment, submission=submission)

        submission.grader = None
        obj._event_submission(assignment=assignment, submission=submission)

        assert True


class TestGenericCommentsCounter:

    @pytest.fixture()
    def obj(self):
        return codepost_stats.analyzers.standard.GenericCommentsCounter()

    def test_init(self, obj):
        assert obj._name == NAME_GENERIC_COMMENTS_COUNTER
        assert obj._min_characters is None
        assert obj._min_words is None
        assert obj._only_grader

    def test_properties(self, obj, mocker):
        p = mocker.patch("codepost_stats.helpers.check_int_like", return_value=SOME_INT_VALUE)

        assert obj.min_characters == obj._min_characters
        assert obj.min_words == obj._min_words
        assert obj.only_graders == obj._only_grader

        obj.min_characters = SOME_INT_VALUE
        obj.min_words = SOME_INT_VALUE

        only_graders_before = obj.only_graders
        obj.only_graders = not only_graders_before

        assert obj.min_characters == obj._min_characters
        assert obj.min_words == obj._min_words
        assert obj.only_graders == obj._only_grader
        assert obj.only_graders != only_graders_before

        assert p.was_called()

    def test_event_comment(self, obj, assignment, submission, file, comment):
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

    def test_event_comment_no_grader(self, obj, assignment, submission, file, comment):
        submission.grader = None
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

    def test_event_comment_not_finalized(self, obj, assignment, submission, file, comment):
        submission.isFinalized = False
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

    def test_event_comment_not_author(self, obj, assignment, submission, file, comment):
        obj._only_grader = True
        submission.grader = SOME_GRADER_NAME

        comment.author = SOME_GRADER_NAME
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

        comment.author = SOME_OTHER_GRADER_NAME
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

        obj._only_grader = False
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

    def test_event_comment_restrictions(self, obj, assignment, submission, file, comment):

        # already set by mocker, but for clarity restating here
        comment.text = SOME_COMMENT_TEXT

        obj._min_characters = len(SOME_COMMENT_TEXT) - 1
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

        obj._min_characters = len(SOME_COMMENT_TEXT) + 1
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

        obj._min_characters = None

        obj._min_words = len(SOME_COMMENT_TEXT.split()) - 1
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )

        obj._min_words = len(SOME_COMMENT_TEXT.split()) + 1
        obj._event_comment(
            assignment=assignment,
            submission=submission,
            file=file,
            comment=comment,
        )


@pytest.mark.parametrize(
    "subclass, subclass_name", [
        (codepost_stats.analyzers.standard.CustomCommentsCounter, NAME_CUSTOM_COMMENTS_COUNTER),
        (codepost_stats.analyzers.standard.RubricCommentsCounter, NAME_RUBRIC_COMMENTS_COUNTER),

    ])
def test_comments_counter_subclasses(subclass, subclass_name, assignment, submission, file, comment):
    obj = subclass()
    assert obj._name == subclass_name

    comment.rubricComment = None
    obj._event_comment(
        assignment=assignment,
        submission=submission,
        file=file,
        comment=comment,
    )

    comment.rubricComment = SOME_INT_VALUE
    obj._event_comment(
        assignment=assignment,
        submission=submission,
        file=file,
        comment=comment,
    )

