
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
        :py:data:`

        :param name: The name identifier
        :param subcat: The subcategory identifier

        :return:
        """

        if not self._check_subcat(subcat=subcat):
            return self.initial_value  # wonder if this is what should be done

        subcat_counters = self._counters.get(subcat, dict())
        counter_value = subcat_counters.get(name, self.initial_value)

        return counter_value

    def _set_value(self, name: str, subcat: str, value: _DictValueType) -> typing.NoReturn:
        """

        :param name: The name identifier
        :param subcat: The subcategory identifier
        :param value: The value to store in the ``name.subcategory`` cell

        :return:
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

    _initial_value = 0
    _DictValueType = int

    def _delta_counter(self, name: str, subcat: str, delta: _DictValueType = 1) -> _DictValueType:
        current_value = self._get_value(name=name, subcat=subcat)
        new_value = current_value + delta
        self._set_value(name=name, subcat=subcat, value=new_value)
        return new_value

    def add(self, name: str, subcat: str, delta: _DictValueType = 1) -> _DictValueType:
        return self._delta_counter(name=name, subcat=subcat, delta=delta)

    def subtract(self, name: str, subcat: str, delta: _DictValueType = 1) -> _DictValueType:
        return self._delta_counter(name=name, subcat=subcat, delta=-delta)

    def get_by_name(
            self,
            name: str,
            normalize_str: bool = True,
    ) -> typing.Dict[str, _DictValueType]:
        record = {}
        for subcat_name, subcat_counters in self._counters.items():
            if normalize_str:
                subcat_name = self._normalize_str(subcat_name)
            record[subcat_name] = subcat_counters.get(name, self._initial_value)
        return record
