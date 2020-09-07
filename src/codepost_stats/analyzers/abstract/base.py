
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

    _name = None

    @property
    def name(self) -> str:
        return self._name

    def _reset(self) -> bool:
        pass

    def _event_course(self, *args, **kwargs):
        pass

    def _event_assignment(self, *args, **kwargs):
        pass

    def _event_submission(self, *args, **kwargs):
        pass

    def _event_file(self, *args, **kwargs):
        pass

    def _event_comment(self, *args, **kwargs):
        pass

    def _normalize_str(
            self,
            s: str,
    ) -> str:
        if s is None:
            return ""
        return s.strip().lower().replace(" ", "-")


class BaseAnalyzer(AbstractAnalyzer):

    _name = None
    _course = None

    @property
    def name(self) -> str:
        return self._name

    def _reset(self) -> bool:
        return True

    def _event_course(
            self,
            course: codepost.models.courses.Courses,
    ):
        self._course = course
        pass

    def _event_assignment(
            self,
            assignment: codepost.models.assignments.Assignments,
    ):
        pass

    def _event_submission(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
    ):
        pass

    def _event_file(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
    ):
        pass

    def _event_comment(
            self,
            assignment: codepost.models.assignments.Assignments,
            submission: codepost.models.submissions.Submissions,
            file: codepost.models.files.Files,
            comment: codepost.models.comments.Comments,
    ):
        pass
