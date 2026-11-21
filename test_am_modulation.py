import unittest

import numpy as np

from am_modulation import (
    add_attenuation,
    add_noise,
    clip_distortion,
    modulate_am,
    spectrum,
)


class AMModulationTests(unittest.TestCase):
    def setUp(self):
        self.fs = 48000.0
        self.t = np.arange(0.0, 0.05, 1.0 / self.fs)
        self.message = np.cos(2.0 * np.pi * 200.0 * self.t)
        self.carrier = np.cos(2.0 * np.pi * 4000.0 * self.t)

    def test_modulation_index_is_valid_and_prevents_overmodulation(self):
        am = modulate_am(self.message, self.carrier, 0.7)
        self.assertGreaterEqual(np.min(am), -1.71)
        self.assertLessEqual(np.max(am), 1.71)
        with self.assertRaises(ValueError):
            modulate_am(self.message, self.carrier, 1.2)

    def test_am_spectrum_has_carrier_and_sidebands(self):
        am = modulate_am(self.message, self.carrier, 0.7)
        frequencies, amplitudes = spectrum(am, self.fs)

        def peak_near(target_hz):
            band = np.abs(frequencies - target_hz) < 20.0
            return np.max(amplitudes[band])

        carrier = peak_near(4000.0)
        lower = peak_near(3800.0)
        upper = peak_near(4200.0)
        self.assertGreater(carrier, lower)
        self.assertAlmostEqual(lower, upper, places=3)

    def test_distortion_scenarios(self):
        am = modulate_am(self.message, self.carrier, 0.7)
        attenuated = add_attenuation(am, 0.35)
        noisy = add_noise(am, 0.08, rng=np.random.default_rng(7))
        clipped = clip_distortion(am, 0.75)
        self.assertAlmostEqual(np.max(np.abs(attenuated)) / np.max(np.abs(am)), 0.35)
        self.assertGreater(np.std(noisy - am), 0.0)
        self.assertLessEqual(np.max(np.abs(clipped)), 0.75)


if __name__ == "__main__":
    unittest.main()
