
import typing

import codepost_stats.analyzers.abstract.base


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "DictStorageAnalyzer",
    "CounterAnalyzer",
]


class DictStorageAnalyzer(codepost_stats.analyzers.abstract.base.BaseAnalyzer):

    _subcategories = None

    _counters = None

    _initial_value = None

    _DictValueType = typing.TypeVar("_DictValueType")

    def __init__(self):
        self._reset()

    def _reset(self) -> bool:
        self._counters = dict()
        return True

    def _is_subcat(self, subcat: str) -> bool:
        if self._subcategories is not None:
            return subcat in self._subcategories

        return True

    def _check_subcat(self, subcat: str) -> typing.NoReturn:
        if not self._is_subcat(subcat=subcat):
            raise ValueError(
                "`{}` is not a valid subcategory for {}".format(
                    subcat,
                    self.__class__.__name__
                )
            )

    @property
    def names(self) -> typing.List[str]:
        if self._counters is None:
            return list()

        return list(set([
            name
            for counters in self._counters.values()
            for name in counters.keys()
        ]))

    def _get_value(self, name: str, subcat: str) -> _DictValueType:
        self._check_subcat(subcat=subcat)

        subcat_counters = self._counters.get(subcat, dict())
        counter_value = subcat_counters.get(name, self._initial_value)

        return counter_value

    def _set_value(self, name: str, subcat: str, value: _DictValueType) -> typing.NoReturn:
        self._check_subcat(subcat=subcat)

        # retrieve subcategory counters
        subcat_counters = self._counters.get(subcat, dict())

        # modify record
        subcat_counters[name] = value

        # store record
        self._counters[subcat] = subcat_counters


class CounterAnalyzer(DictStorageAnalyzer):

    _initial_value = 0
    _dict_value_type = int

    def _delta_counter(self, name: str, subcat: str, delta: int = 1) -> int:
        current_value = self._get_value(name=name, subcat=subcat)
        new_value = current_value + delta
        self._set_value(name=name, subcat=subcat, value=new_value)
        return new_value

    def add(self, name: str, subcat: str, delta: int = 1) -> int:
        return self._delta_counter(name=name, subcat=subcat, delta=delta)

    def subtract(self, name: str, subcat: str, delta: int = 1) -> int:
        return self._delta_counter(name=name, subcat=subcat, delta=-delta)

    def get_by_name(
            self,
            name: str,
            normalize_str: bool = True,
    ) -> typing.Dict[str, int]:
        record = {}
        for subcat_name, subcat_counters in self._counters.items():
            if normalize_str:
                subcat_name = self._normalize_str(subcat_name)
            record[subcat_name] = subcat_counters.get(name, self._initial_value)
        return record
