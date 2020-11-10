"""
This submodule provides the abstract interface of a codePost analyzer,
as well as some high-level generic analyzers, which seek to identify a
few general types of statistics that may be computed on codePost data,
so as to limit the amount of redundant code that must be written to
support such analyses.

As an example, a typical kind of analysis on codePost data might involve
counting the number of occurrences of certain objects (submissions, comments,
files, etc.), or the number occurrences of specific types of objects
(submissions by grader, comments by recipient, etc.)

This is the purpose of the generic analyzer class
:py:class:`codepost_stats.analyzers.abstract.CounterAnalyzer`, which
contains all the boilerplate code necessary to keep track of many counters
over codePost data. This generic analyzer class is then used to provide
specialized analyzers such as the following:

* :py:class:`codepost_stats.analyzers.standard.SubmissionsGradedCounter`
  which keeps track of the number of submissions graded, for each assignment,
  by the graders registered in the course;

* :py:class:`codepost_stats.analyzers.standard.GenericCommentsCounter`
  which counts the number of comments, for each assignment, by the graders
  registered in the course, with the possibility of further filtering which
  kind of comments are actually taken into account (rubric comments versus
  custom comments, and so on).
"""