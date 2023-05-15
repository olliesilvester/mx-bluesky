import unittest

from mx_bluesky.util.nominal_min_max import NominalMinMax, SymmetricNominalMinMax


def test_nominal_returned_for_in_range_value():
    nmm = NominalMinMax(4.0, 1.0, 9.0)
    result = nmm.get_nominal_if_in_range(3.0)
    expectation = 4.0
    assert _are_essentially_equal(result, expectation, 1.0e-6)


def test_nothing_returned_for_out_of_range_value():
    nmm = NominalMinMax(4.0, 2.0, 6.0)
    result = nmm.get_nominal_if_in_range(-3.0)
    assert result is None


def test_error_raised_when_bounds_not_in_order():
    class Case(unittest.TestCase):
        def run_test(self):
            with self.assertRaises(TypeError):
                _ = NominalMinMax(4.0, 12.0, 6.0)

    case = Case()
    case.run_test()


def test_nominal_returned_for_in_symmetric_range_value():
    # dummy comment
    snmm = SymmetricNominalMinMax(5.1, 4.0)
    result = snmm.get_nominal_if_in_range(8.8)
    expectation = 5.1
    assert _are_essentially_equal(result, expectation, 1.0e-6)


def test_nothing_returned_for_out_of_symmetric_range_value():
    nmm = SymmetricNominalMinMax(2.0, 6.0)
    result = nmm.get_nominal_if_in_range(13.0)
    assert result is None


def _are_essentially_equal(a: float, b: float, threshold: float):
    return abs(a - b) < threshold
