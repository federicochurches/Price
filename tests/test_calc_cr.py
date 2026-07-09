import ast
import datetime as _dt
import os
import tempfile
import unittest

import pandas as pd


def _load_reshape_daily_pivot():
    """calc_cr.py ejecuta carga de datasets reales al importarse (módulo con
    side effects, no aislable sin un refactor mayor — ver code-review 09-07).
    Se extrae el source de _reshape_daily_pivot() y se ejecuta en un
    namespace limpio para poder testearla sin ese costado del módulo."""
    calc_cr_path = os.path.join(os.path.dirname(__file__), '..', 'calc_cr.py')
    with open(calc_cr_path, encoding='utf-8') as f:
        src = f.read()
    tree = ast.parse(src)
    func_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_reshape_daily_pivot')
    func_src = ast.get_source_segment(src, func_node)
    ns = {'pd': pd, '_dt': _dt}
    exec(func_src, ns)
    return ns['_reshape_daily_pivot']


class ReshapeDailyPivotTests(unittest.TestCase):
    def setUp(self):
        self._reshape = _load_reshape_daily_pivot()
        fd, self.path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)

    def tearDown(self):
        os.remove(self.path)

    def _write_pivot(self, rows):
        pd.DataFrame(rows).to_excel(self.path, index=False)

    def test_entity_reported_in_only_some_metrics_is_not_dropped(self):
        """El proveedor no siempre reporta las 5 métricas para cada hotel.
        Antes del fix, anclar en la primera métrica de un `set` (orden no
        determinístico) podía descartar por completo cualquier hotel que no
        tuviera fila en esa métrica en particular."""
        d1, d2 = pd.Timestamp('2026-06-01'), pd.Timestamp('2026-06-02')

        def row(hotel, metric, v):
            return {
                'ExternalProviderName': 'DerbySoft', 'Corporate': 'CorpX',
                'País destino': 'MX', 'Destino': 'Cancun', 'Hotel': hotel,
                'DistributionCategory': 'B2C', '': metric, d1: v, d2: v,
            }

        rows = [row('H1', m, 5) for m in
                ('CheckRates Absolutos', 'CheckRates Únicos', 'Successful UniqueChkRts', '#Errors', 'Bookings')]
        # H2 no reporta '#Errors' ni 'Bookings' en absoluto.
        rows += [row('H2', m, 7) for m in
                 ('CheckRates Absolutos', 'CheckRates Únicos', 'Successful UniqueChkRts')]
        self._write_pivot(rows)

        out = self._reshape(self.path)

        self.assertEqual(set(out['Hotel']), {'H1', 'H2'})
        h2 = out[out['Hotel'] == 'H2'].iloc[0]
        self.assertEqual(h2['Bookings'], 0)
        self.assertEqual(h2['#Errors'], 0)
        self.assertEqual(h2['CheckRates Absolutos'], 14)  # 7+7, ambos días

    def test_result_is_deterministic_across_runs(self):
        d1 = pd.Timestamp('2026-06-01')

        def row(hotel, metric, v):
            return {
                'ExternalProviderName': 'DerbySoft', 'Corporate': 'CorpX',
                'País destino': 'MX', 'Destino': 'Cancun', 'Hotel': hotel,
                'DistributionCategory': 'B2C', '': metric, d1: v,
            }

        rows = [row('H1', m, 1) for m in ('CheckRates Absolutos', 'CheckRates Únicos', 'Bookings')]
        rows += [row('H2', m, 1) for m in ('Successful UniqueChkRts', '#Errors')]
        self._write_pivot(rows)

        first = self._reshape(self.path).sort_values('Hotel').reset_index(drop=True)
        second = self._reshape(self.path).sort_values('Hotel').reset_index(drop=True)
        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(set(first['Hotel']), {'H1', 'H2'})


if __name__ == '__main__':
    unittest.main()
