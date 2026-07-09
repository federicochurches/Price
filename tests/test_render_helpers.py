import json
import unittest

from render_helpers import json_dumps_for_script


class JsonDumpsForScriptTests(unittest.TestCase):
    """Regla #42 del proyecto: json.dumps() crudo dentro de un <script> se
    rompe si el valor contiene HTML sin escapar (ej. drilldowns del motor
    editorial, que generan '<div><strong>...</strong> ...</div>')."""

    def test_no_literal_closing_tag_survives_in_the_output(self):
        payload = {'html': '<div><strong>Hotel X</strong> · 5 hoteles</div>'}
        out = json_dumps_for_script(payload, ensure_ascii=False)
        self.assertNotIn('</', out)

    def test_escaped_output_round_trips_to_the_same_data(self):
        payload = {'html': '<div><strong>Hotel X</strong> · 5 hoteles</div>', 'n': 3}
        out = json_dumps_for_script(payload, ensure_ascii=False)
        # Lo que hace un motor JS al parsear el string literal: '<\/' -> '</'.
        recovered = json.loads(out.replace('<\\/', '</'))
        self.assertEqual(recovered, payload)

    def test_plain_data_without_closing_tags_is_unaffected(self):
        payload = {'a': 1, 'b': 'sin tags'}
        self.assertEqual(json_dumps_for_script(payload), json.dumps(payload))


if __name__ == '__main__':
    unittest.main()
