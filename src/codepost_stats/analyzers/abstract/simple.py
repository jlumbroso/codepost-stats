"""
This submodule contains generic analyzer classes that encapsulate common
functionality related to the kind of data being tracked, and are supposed
to be overridden to create classes such as :py:class:`SubmissionsGradedCounter`
in :py:mod:`codepost_stats.analyzers.standard`.

The first generic analyzer is :py:class:`DictStorageAnalyzer`, it is designed
to record data with two levels of organization, a first level called the
:py:data:`name` and a second level called the :py:data:`subcat` or subcategory.
In the above-mentioned example of :py:class:`SubmissionsGradedCounter`, for
instance, the :py:data:`name` would be the login email of the grader and the
:py:data:`subcat` would be the names of the assignment.

In fact, because there are many scenarii in which one might want to aggregate
counts over the codePost data, there is a dedicated generic analyzer for this
specific purpose, :py:class:`CounterAnalyzer`, which is child class to the
:py:class:`DictStorageAnalyzer` with an interface specifically designed to keep
tally with :py:func:`CounterAnalyzer.add` and :py:func:`CounterAnalyzer.subtract`.
"""

import copy
import typing

import codepost_stats.analyzers.abstract.base


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "DictStorageAnalyzer",
    "CounterAnalyzer",
]


class DictStorageAnalyzer(codepost_stats.analyzers.abstract.base.BaseAnalyzer):
    """
    The :py:class:`DictStorageAnalyzer` class is a generic class for a codePost
    analyzer object, that stores its output data in a dictionary.

    The dictionary storage is designed to contain two levels of organization:
    The top-level index is a ``name``, such as for instance a grader email
    address; the secondary index is for a ``subcategory``, for instance an
    assignment name.

    Because this class, like both
    :py:class:`codepost_stats.analyzers.abstract.base.AbstractAnalyzer` and
    :py:class:`codepost_stats.analyzers.abstract.base.BaseAnalyzer`, is not
    intended to be used directly, many of its fields and methods are private.
    """

    _DictValueType = typing.TypeVar("_DictValueType")

    _subcategories: typing.Optional[typing.List[str]] = None

    _counters: typing.Optional[typing.Dict[str, typing.Dict[str, _DictValueType]]] = None

    _initial_value: typing.Optional[_DictValueType] = None

    _suppress_subcat_check: bool = False

    def __init__(self):
        self._reset()

    def _reset(self) -> bool:
        self._counters = dict()
        return True

    def _is_subcat(self, subcat: str) -> bool:
        """
        Returns whether :py:data:`subcat` is a valid subcategory identifier.

        The internal attribute :py:attr:`_subcategories` controls whether this
        method is restrictive or not: If the attribute is undefined, then all
        subcategories will return :py:data:`True`; if the attribute has been
        defined, as a list of the valid subcategory identifiers, then this
        method will only return :py:data:`True` if :py:data:`subcat` is
        contained in :py:attr:`_subcategories`.

        :param subcat: The subcategory identifier to check

        :return: :py:data:`True` if the subcategory exists (or no subcategories
            have been defined), :py:data:`False` otherwise
        """

        if self._subcategories is not None:
            return subcat in self._subcategories

        return True

    def _check_subcat(self, subcat: str) -> bool:
        """
        Checks whether :py:data:`subcat` is a valid subcategory identifier and,
        if not, raises a :py:exc:`ValueError` exception.

        This check can be suppressed by setting the private
        :py:attr:`_suppress_subcat_check` attribute to :py:data:`True`, in which
        case no exception will be raised.

        :param subcat: The subcategory identifier to check

        :raises ValueError: If the subcategory does not exist

        :return: :py:data:`True` if the subcategory exists (or no subcategories
            have been defined), :py:data:`False` otherwise
        """

        if not self._is_subcat(subcat=subcat):
            if self._suppress_subcat_check:
                return False

            raise ValueError(
                "`{}` is not a valid subcategory for {}".format(
                    subcat,
                    self.__class__.__name__
                )
            )

        return True

    @property
    def names(self) -> typing.List[str]:
        """
        Gets a list of the names for which data has been recorded since
        the last reset of the analyzer.

        :return: A list of names for which data has been recorded
        """

        if self._counters is None:
            return list()

        return list(set([
            name
            for counters in self._counters.values()
            for name in counters.keys()
        ]))

    @property
    def initial_value(self) -> _DictValueType:
        """
        Gets (an immutable copy of) the initial value that is assigned
        to newly created data cells, before they are first assigned to.

        :return: The initial value assigned to uninitialized cells
        """

        ret = copy.deepcopy(self._initial_value)
        return ret

    def _get_value(self, name: str, subcat: str) -> _DictValueType:
        """
        Gets the value stored for the provided :py:data:`name` and :py:data:`subcat`.

        If no value has been stored so far, this will return the value contained in
        :py:attr:`initial_value`.

        :param name: The name identifier
        :param subcat: The subcategory identifier

        :return: The value stored for the :py:data:`name` and :py:data:`subcat` pair
            if any, or :py:attr:`initial_value`
        """

        if not self._check_subcat(subcat=subcat):
            return self.initial_value  # wonder if this is what should be done

        subcat_counters = self._counters.get(subcat, dict())
        counter_value = subcat_counters.get(name, self.initial_value)

        return counter_value

    def _set_value(self, name: str, subcat: str, value: _DictValueType) -> typing.NoReturn:
        """
        Sets the value for the corresponding :py:data:`name` and :py:data:`subcat`.

        :param name: The name identifier
        :param subcat: The subcategory identifier
        :param value: The value to store in the ``name.subcategory`` record
        """

        if not self._check_subcat(subcat=subcat):
            return

        # retrieve subcategory counters
        subcat_counters = self._counters.get(subcat, dict())

        # modify record
        subcat_counters[name] = value

        # store record
        self._counters[subcat] = subcat_counters


class CounterAnalyzer(DictStorageAnalyzer):
    """
    The :py:class:`CounterAnalyzer` class is a generic class for a codePost
    analyzer object, that makes it easy to count statistics (number of
    submissions graded, comments written, etc.).

    This class handles all the initialization and provides two methods,
    :py:func:`add` and :py:func:`subtract`, to update the internal counters.

    Once the analysis is completed, it can be retrieved by iterating over
    the :py:attr:`names` attribute, to see all the names for which data has
    been recorded, and for each name, call the :py:func:`get_by_name` function
    to retrieve the dictionary of values associated with that name (and
    divided by subcategories).

    This is a high-level analyzer class. The child class
    :py:class:`codepost_stats.analyzers.standard.SubmissionsGradedCounter`
    provides an example of how to use this class to count the number of
    submissions graded.
    """

    _DictValueType = int
    _initial_value: _DictValueType = 0
    _default_delta: _DictValueType = 1

    def _delta_counter(
            self,
            name: str,
            subcat: str,
            delta: _DictValueType = _default_delta,
    ) -> _DictValueType:
        """
        Adjust the counter, for the :py:data:`name` and :py:data:`subcat` record,
        by relative value :py:data:`delta`.

        :param name: The name identifier
        :param subcat: The subcategory identifier
        :param delta: The relative amount by which to adjust the counter

        :raises ValueError: If the subcategory `subcat` does not exist and the
            subcategory warning is not suppressed

        :return: The new value of the counter that has been modified
        """

        current_value = self._get_value(name=name, subcat=subcat)
        new_value = current_value + delta
        self._set_value(name=name, subcat=subcat, value=new_value)
        return new_value

    def _check_delta(self, delta: _DictValueType, positivity_check: bool = True):

        # check type of delta
        try:
            delta = self._DictValueType(delta)
        except ValueError:
            raise ValueError(
                "The provided `delta` does not have the right type: {}".format(
                    self._DictValueType
                ))

        # check "positivity" of delta
        if positivity_check:
            try:
                if delta < self._DictValueType(0):
                    raise ValueError(
                        "The provided `delta` is not larger or equal to zero; "
                        "for full control over `delta` use `_delta_counter()` "
                        "rather than `add` or `subtract`."
                    )
            except ValueError:
                raise
            except TypeError:  # pragma: no cover
                # the comparison did not work, so the DictValueType is not
                # numeric, or does not support comparison with a number
                pass

    def add(
            self,
            name: str,
            subcat: str,
            delta: _DictValueType = _default_delta,
    ) -> _DictValueType:
        """
        Adds to the counter, for the :py:data:`name` and :py:data:`subcat` record,
        by relative nonnegative value :py:data:`delta`.

        This method is implemented by an internal call to :py:func:`_delta_counter`,
        which is a slightly more powerful method, in particular allowing for
        arbitrary values of `delta`.

        :param name: The name identifier
        :param subcat: The subcategory identifier
        :param delta: (Optionally) the relative amount by which to adjust the counter

        :raises ValueError: If the subcategory `subcat` does not exist and the
            subcategory warning is not suppressed

        :raises ValueError: If the provided `delta` is negative

        :return: The new value of the counter that has been modified
        """

        self._check_delta(delta=delta)
        return self._delta_counter(name=name, subcat=subcat, delta=delta)

    def subtract(
            self,
            name: str,
            subcat: str,
            delta: _DictValueType = _default_delta,
    ) -> _DictValueType:
        """
        Subtracts from the counter, for the :py:data:`name` and :py:data:`subcat`
        record, by relative nonnegative value :py:data:`delta`.

        This method is implemented by an internal call to :py:func:`_delta_counter`,
        which is a slightly more powerful method, in particular allowing for
        arbitrary values of `delta`.

        :param name: The name identifier
        :param subcat: The subcategory identifier
        :param delta: (Optionally) the relative amount by which to adjust the counter

        :raises ValueError: If the subcategory `subcat` does not exist and the
            subcategory warning is not suppressed

        :raises ValueError: If the provided `delta` is negative

        :return: The new value of the counter that has been modified
        """

        return self._delta_counter(name=name, subcat=subcat, delta=-delta)

    def get_by_name(
            self,
            name: str,
            normalize_str: bool = True,
    ) -> typing.Dict[str, _DictValueType]:
        """
        Returns a dictionary of all the values stored associated with :py:data:`name`.

        :param name: The name identifier of the data to query

        :param normalize_str: (Optional) flag to indicate whether to normalize
            the names of subcategories, using the internal :py:func:`_normalize_str`
            normalization function

        :return: A dictionary mapping each subcategory to a counter, for the
            provided :py:data:`name`
        """

        record = {}
        for subcat_name, subcat_counters in self._counters.items():

            if normalize_str:
                subcat_name = self._normalize_str(subcat_name)

            record[subcat_name] = copy.deepcopy(
                subcat_counters.get(name, self.initial_value))

        return record
