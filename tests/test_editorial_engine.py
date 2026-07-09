import unittest

from editorial_engine import score_hotel


def _row(vol, banda, wow):
    return {
        'Trafico': vol,
        'BandaNoDispo': banda,
        'NoDispo_WoW_pp': wow,
    }


class ScoreHotelWowWeightTests(unittest.TestCase):
    """El bonus WoW debe pesar 10% del score total, no 1% (bug de doble escalado)."""

    def test_worsening_wow_adds_the_full_10_percent_weight(self):
        vol_max = 100.0
        worsened = score_hotel(_row(100.0, 'Súper Crítica', wow=5.0), vol_max, 'nodispo', report_type='rnd')
        not_worsened = score_hotel(_row(100.0, 'Súper Crítica', wow=-5.0), vol_max, 'nodispo', report_type='rnd')
        self.assertAlmostEqual(worsened - not_worsened, 0.10, places=6)

    def test_max_score_is_1_0_when_everything_is_worst_case(self):
        vol_max = 100.0
        score = score_hotel(_row(100.0, 'Súper Crítica', wow=5.0), vol_max, 'nodispo', report_type='rnd')
        self.assertAlmostEqual(score, 1.0, places=6)

    def test_nan_wow_contributes_zero_bonus(self):
        vol_max = 100.0
        score = score_hotel(_row(100.0, 'Súper Crítica', wow=float('nan')), vol_max, 'nodispo', report_type='rnd')
        self.assertAlmostEqual(score, 0.90, places=6)


if __name__ == '__main__':
    unittest.main()
