import json
import unittest

from processor.processor import compute_congestion, parse_sample


class ProcessorTests(unittest.TestCase):
    def test_parse_sample_normalizes_valid_payload(self):
        payload = json.dumps({
            "timestamp_utc": "2026-11-10T12:00:00+00:00",
            "avg_speed_kmh": 42.5,
            "vehicle_count": 8,
        }).encode()

        self.assertEqual(
            parse_sample(payload),
            ("2026-11-10T12:00:00+00:00", "intersection1", 42.5, 8),
        )

    def test_parse_sample_rejects_invalid_sensor_values(self):
        base = {
            "timestamp_utc": "2026-11-10T12:00:00+00:00",
            "avg_speed_kmh": 42,
            "vehicle_count": 8,
        }
        for changes in (
            {"avg_speed_kmh": float("nan")},
            {"vehicle_count": -1},
            {"vehicle_count": 1.5},
            {"vehicle_count": True},
            {"timestamp_utc": None},
        ):
            with self.subTest(changes=changes):
                payload = json.dumps(base | changes).encode()
                with self.assertRaises(ValueError):
                    parse_sample(payload)

    def test_compute_congestion_rejects_non_finite_speed(self):
        with self.assertRaises(ValueError):
            compute_congestion(float("inf"))


if __name__ == "__main__":
    unittest.main()
