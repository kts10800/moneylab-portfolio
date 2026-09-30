"""Fixed artificial inputs for calculation checks; not market observations."""
import unittest

from examples.timing import combine, timing_parts


class TimingTests(unittest.TestCase):
    def test_clock_offset_is_not_mistaken_for_transport_delay(self):
        sample = {'main_minus_sub': 1.36, 'utc_minus_main': -1.34}
        result = timing_parts(1001.86, 1000.45, 1000.0, sample)
        self.assertAlmostEqual(result['raw_transport_ms'], 1410)
        self.assertAlmostEqual(result['transport_ms'], 50)
        self.assertAlmostEqual(result['broker_sub_ms'], 470)
        self.assertAlmostEqual(result['market_age_ms'], 520)

    def test_components_sum_to_total_age(self):
        for offset in (-0.02, 0.0, 0.02):
            result = timing_parts(100.8, 100.4, 100.0,
                                  {'main_minus_sub': offset, 'utc_minus_main': 0.01})
            self.assertAlmostEqual(result['market_age_ms'],
                                   result['transport_ms'] + result['broker_sub_ms'])

    def test_source_input_is_not_modified(self):
        sample = {'main_minus_sub': 0.02, 'utc_minus_main': 0.01}
        original = sample.copy()
        timing_parts(100.8, 100.4, 100.0, sample)
        self.assertEqual(sample, original)

    def test_consistent_samples_have_bounded_uncertainty(self):
        offset, uncertainty = combine([
            {'offset': v, 'uncertainty': 0.01} for v in (1.36, 1.361, 1.362)
        ])
        self.assertAlmostEqual(offset, 1.361)
        self.assertGreater(uncertainty, 0)
        self.assertLess(uncertainty, 0.02)

    def test_insufficient_samples_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'clock_samples'):
            combine([{'offset': 0, 'uncertainty': 0.01}])

    def test_unstable_clock_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'clock_unstable'):
            combine([{'offset': v, 'uncertainty': 0.01} for v in (0, 0, 1)])

    def test_nonoverlapping_intervals_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'clock_intervals_disagree'):
            combine([{'offset': v, 'uncertainty': 0.001} for v in (0, 0.01, 0.02)])


if __name__ == '__main__':
    unittest.main()
