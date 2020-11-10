"""
The :py:mod:`codepost_stats.analyzers` submodule contains all the logic
related to analyzers.

This includes:

1. The analyzer interfaces, :py:class:`AbstractAnalyzer` and :py:class:`BaseAnalyzer`,
   are defined in the :py:mod:`codepost_stats.analyzers.abstract.base` submodule;

2. Some generic high-level implementations of analyzers, such as
   :py:class:`DictStorageAnalyzer` to define an analyzer that collects information
   in a nested dictionary, or such as :py:class:`CounterAnalyzer` which is an even
   more specialized analyzer that keeps track of integer counts, are defined in the
   :py:mod:`codepost_stats.analyzers.abstract.simple` submodule;

3. Some examples of fully-implemented analyzers, such as :py:class:`SubmissionsGradedCounter`
   or :py:class:`GenericCommentsCounter`, are available from the
   :py:mod:`codepost_stats.analyzers.standard` submodule;

4. The interface and an implementation of analyzer pools is defined in the
   :py:mod:`codepost_stats.analyzers.pool` submodule.

The most important part of the codebase are the implementations of analyzers in the
:py:mod:`codepost_stats.analyzers.standard` submodule: These provide good examples
from which to generate new analyzers.
"""