
import copy

import pytest

import codepost_stats.analyzers.abstract.simple


SOME_CATEGORY = "Some Category"
SOME_CATEGORY_NORMALIZED = "some-category"
SOME_OTHER_CATEGORY_NORMALIZED = "other-category"
SOME_NAME = "Some weird  Name"
SOME_NAME_NORMALIZED = "some-weird-name"
SOME_INITIAL_VALUE = 0
SOME_INITIAL_VALUE_OBJ = list()

SOME_OTHER_VALUE = 20

NUMBER_ZERO_DEFAULT_COUNTER_VALUE = 0
NUMBER_ONE_DEFAULT_DELTA = 1

BAD_DELTA = "e"
NEGATIVE_DELTA = -20

SOME_INTERNAL_DICT_DATA = {
    SOME_CATEGORY_NORMALIZED: {
        SOME_NAME_NORMALIZED: SOME_INITIAL_VALUE,
    },
    SOME_OTHER_CATEGORY_NORMALIZED: {
        SOME_NAME_NORMALIZED: SOME_OTHER_VALUE,
    }
}


class TestDictStorageAnalyzer:

    @pytest.fixture()
    def obj(self):
        return codepost_stats.analyzers.abstract.simple.DictStorageAnalyzer()

    @pytest.fixture()
    def obj_with_vals(self):
        obj = codepost_stats.analyzers.abstract.simple.DictStorageAnalyzer()
        obj._counters = copy.deepcopy(SOME_INTERNAL_DICT_DATA)
        return obj

    def test_init(self, obj):
        assert obj._counters is not None
        assert issubclass(type(obj._counters), dict)

    def test_reset_init(self, obj_with_vals):
        # testing data storage is initialized and non-empty
        assert obj_with_vals._counters is not None
        assert issubclass(type(obj_with_vals._counters), dict)
        assert len(obj_with_vals._counters) > 0

        # reset
        obj_with_vals._reset()
        assert obj_with_vals._counters is not None
        assert issubclass(type(obj_with_vals._counters), dict)
        assert len(obj_with_vals._counters) == 0

    def test_is_subcat_none(self, obj):
        """
        Check that when the internal :py:attr:`_subcategories` dictionary
        is :py:data:`None`, any subcategory name is allowed.
        """
        assert obj._subcategories is None
        assert obj._is_subcat(SOME_CATEGORY_NORMALIZED)

    def test_is_subcat_set(self, obj):
        """
        Check that when the internal :py:attr:`_subcategories` list
        is defined, :py:func:`_is_subcat` only allows subcategories in that
        list.
        """
        assert obj._subcategories is None

        obj._subcategories = []
        assert not obj._is_subcat(SOME_CATEGORY_NORMALIZED)

        obj._subcategories = [SOME_CATEGORY_NORMALIZED]
        assert obj._is_subcat(SOME_CATEGORY_NORMALIZED)

    def test_check_subcat(self, obj):
        # default case, undefined and unrestrictive
        assert obj._subcategories is None
        assert obj._check_subcat(SOME_CATEGORY_NORMALIZED)

        # case emoty list
        obj._subcategories = []

        obj._suppress_subcat_check = False
        with pytest.raises(ValueError):
            obj._check_subcat(SOME_CATEGORY_NORMALIZED)

        obj._suppress_subcat_check = True
        assert not obj._check_subcat(SOME_CATEGORY_NORMALIZED)

        # case non empty
        obj._subcategories = [SOME_CATEGORY_NORMALIZED]
        assert obj._check_subcat(SOME_CATEGORY_NORMALIZED)

    def test_names_none(self, obj):
        assert type(obj.names) is list
        assert len(obj.names) == 0

        obj._counters = None

        assert type(obj.names) is list
        assert len(obj.names) == 0

    def test_names_dummy(self, obj_with_vals):
        assert len(obj_with_vals.names) > 0

    def test_initial_value(self, obj):
        assert obj.initial_value == obj._initial_value

        obj._initial_value = SOME_INITIAL_VALUE
        assert obj.initial_value == obj._initial_value

        obj._initial_value = SOME_INITIAL_VALUE_OBJ
        assert obj.initial_value == obj._initial_value
        assert id(obj.initial_value) != id(obj._initial_value)

    def test_get_value(self, obj_with_vals):
        assert obj_with_vals._get_value(
            name=SOME_NAME_NORMALIZED,
            subcat=SOME_OTHER_CATEGORY_NORMALIZED,
        ) == SOME_OTHER_VALUE

    def test_get_value_bad_subcat(self, obj):

        obj._subcategories = []

        obj._suppress_subcat_check = True
        assert obj._get_value(
            name=SOME_NAME_NORMALIZED,
            subcat=SOME_OTHER_CATEGORY_NORMALIZED,
        ) == obj._initial_value

        obj._suppress_subcat_check = False
        with pytest.raises(ValueError):
            obj._get_value(
                name=SOME_NAME_NORMALIZED,
                subcat=SOME_OTHER_CATEGORY_NORMALIZED,
            )

    def test_set_value(self, obj):

        obj._set_value(
            name=SOME_NAME_NORMALIZED,
            subcat=SOME_OTHER_CATEGORY_NORMALIZED,
            value=SOME_OTHER_VALUE,
        )

        assert obj._get_value(
            name=SOME_NAME_NORMALIZED,
            subcat=SOME_OTHER_CATEGORY_NORMALIZED,
        ) == SOME_OTHER_VALUE

        obj._subcategories = []
        obj._suppress_subcat_check = True
        obj._set_value(
            name=SOME_NAME_NORMALIZED,
            subcat=SOME_OTHER_CATEGORY_NORMALIZED,
            value=SOME_OTHER_VALUE,
        )


class TestCounterAnalyzer:

    @pytest.fixture()
    def obj(self):
        return codepost_stats.analyzers.abstract.simple.CounterAnalyzer()

    @pytest.fixture()
    def obj_with_vals(self):
        obj = codepost_stats.analyzers.abstract.simple.CounterAnalyzer()
        obj._counters = copy.deepcopy(SOME_INTERNAL_DICT_DATA)
        return obj

    def test_init(self, obj):
        assert obj._DictValueType is int
        assert obj._initial_value == NUMBER_ZERO_DEFAULT_COUNTER_VALUE
        assert obj._default_delta == NUMBER_ONE_DEFAULT_DELTA

    def test_delta_counter(self, obj):

        assert obj._counters is None or len(obj._counters) == 0

        val_one = obj._get_value(
            name=SOME_NAME_NORMALIZED,
            subcat=SOME_CATEGORY_NORMALIZED,
        )

        obj._delta_counter(
            name=SOME_NAME_NORMALIZED,
            subcat=SOME_CATEGORY_NORMALIZED,
            delta=NUMBER_ONE_DEFAULT_DELTA,
        )
        assert not (obj._counters is None or len(obj._counters) == 0)

        val_two = obj._get_value(
            name=SOME_NAME_NORMALIZED,
            subcat=SOME_CATEGORY_NORMALIZED,
        )

        assert val_one != val_two
        assert (val_two - val_one) == NUMBER_ONE_DEFAULT_DELTA
        assert val_one == NUMBER_ZERO_DEFAULT_COUNTER_VALUE
        assert val_two == NUMBER_ZERO_DEFAULT_COUNTER_VALUE + NUMBER_ONE_DEFAULT_DELTA

    def test_check_delta(self, obj):
        with pytest.raises(ValueError):
            obj._check_delta(delta=BAD_DELTA, positivity_check=True)

        with pytest.raises(ValueError):
            obj._check_delta(delta=BAD_DELTA, positivity_check=False)

        with pytest.raises(ValueError):
            obj._check_delta(delta=NEGATIVE_DELTA, positivity_check=True)

        # noinspection PyBroadException
        try:
            obj._check_delta(delta=NEGATIVE_DELTA, positivity_check=False)
            assert True
        except:
            assert False

    def test_check_delta_type_error(self, obj):
        obj._DictValueType = str


    def test_add_subtract(self, obj):
        obj.add(name=SOME_NAME_NORMALIZED, subcat=SOME_CATEGORY_NORMALIZED)
        obj.subtract(name=SOME_NAME_NORMALIZED, subcat=SOME_CATEGORY_NORMALIZED)

    def test_get_by_name(self, obj, obj_with_vals):

        # empty object
        assert len(obj.get_by_name(SOME_NAME_NORMALIZED)) == 0

        # non-empty object
        assert len(obj_with_vals.get_by_name(
            name=SOME_NAME_NORMALIZED, normalize_str=True)) > 0

        # non-empty object
        assert len(obj_with_vals.get_by_name(
            name=SOME_NAME_NORMALIZED, normalize_str=False)) > 0
