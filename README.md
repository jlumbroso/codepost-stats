# codePost Statistics Compiler

![pytest](https://github.com/jlumbroso/codepost-stats/workflows/pytest/badge.svg)
 [![codecov](https://codecov.io/gh/jlumbroso/codepost-stats/branch/master/graph/badge.svg?token=KVGWAVZKW1)](https://codecov.io/gh/jlumbroso/codepost-stats)
 [![Documentation Status](https://readthedocs.org/projects/codepost-stats/badge/?version=latest)](https://codepost-stats.readthedocs.io/en/latest/?badge=latest)
 [![Downloads](https://pepy.tech/badge/codepost-stats)](https://pepy.tech/project/codepost-stats)
 [![Run on Repl.it](https://repl.it/badge/github/jlumbroso/codepost-stats)](https://repl.it/github/jlumbroso/codepost-stats)
 [![Stargazers](https://img.shields.io/github/stars/jlumbroso/codepost-stats?style=social)](https://github.com/jlumbroso/codepost-stats)

A system to compile statistics automatically from a course on the codePost platform.

## Installation

The package is available on PyPI as slacktivate and so is available the usual way, i.e.,
```shell
$ pip install codepost-stats
```

## Example

```python
import codepost

import codepost_stats
import codepost_stats.analyzers.abstract.simple
import codepost_stats.analyzers.standard
import codepost_stats.event_loop

# Login
codepost.configure_api_key("<CODEPOST_API_TOKEN>")

# Create Course Analyzer Event Loop
cael = codepost_stats.event_loop.CourseAnalyzerEventLoop(
    course_name="COS126",
    course_term="S2020",
)

# Create Analyzer
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
        
sgc = SubmissionsGradedCounter()

# Add the analyzer we just created
cael.register(sgc)

# Add a few standard analyzers
cael.register(codepost_stats.analyzers.standard.CustomCommentsCounter)
cael.register(codepost_stats.analyzers.standard.RubricCommentsCounter)

# Run the aggregation of stats
cael.run()

# Extract statistics per user
statistics_per_user = {
    name: cael.get_by_name(name)
    for name in cael.names
}
```
and the `statistics_per_user` variable would be a dictionary of the form:
```json
{
  "grader1@princeton.edu": {
    "submissions.graded": {
      "hello": 5,
      "loops": 6,
      "nbody": 0,
      "sierpinski": 8,
      "programming-exam-1": 6,
      "hamming": 0,
      "lfsr": 2,
      "guitar": 5,
      "markov": 6,
      "tspp": 4,
      "atomic": 29
    },
    "comments.counter.custom": {
      "hello": 9,
      "loops": 6,
      "nbody": 0,
      "sierpinski": 14,
      "programming-exam-1": 6,
      "hamming": 0,
      "lfsr": 4,
      "guitar": 8,
      "markov": 14,
      "tspp": 7,
      "atomic": 36
    },
    "comments.counter.rubric": {
      "hello": 7,
      "loops": 15,
      "nbody": 0,
      "sierpinski": 13,
      "programming-exam-1": 8,
      "hamming": 0,
      "lfsr": 6,
      "guitar": 10,
      "markov": 17,
      "tspp": 13,
      "atomic": 38
    }
  },
  "grader2@princeton.edu": {
      /* ... grader2@princeton.edu's statistics here ... */
  },
  /* ... more graders ... */
}
```

## License

This project is licensed [under the LGPLv3 license](https://www.gnu.org/licenses/lgpl-3.0.en.html),
with the understanding that importing a Python modular is similar in spirit to dynamically linking
against it.

- You can use the library/CLI `codepost-stats` in any project, for any purpose,
  as long as you provide some acknowledgement to this original project for
  use of the library (for open source software, just explicitly including
  `codepost-stats` in the dependency such as a `pyproject.toml` or `Pipfile`
  is acknowledgement enough for me!).

- If you make improvements to `codepost-stats`, you are required to make those
  changes publicly available.

