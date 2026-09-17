import csv
import tempfile
import unittest

from src.analyzer import analyze_telemetry


class TestAnalyzeTelemetry(unittest.TestCase):

    def create_telemetry_file(self):
        file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False
        )

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "temperature_c",
                "power_w",
                "gpu_utilization_percent",
            ]
        )

        writer.writeheader()

        writer.writerow({
            "timestamp": "2026-09-12T12:00:00",
            "temperature_c": "60",
            "power_w": "200",
            "gpu_utilization_percent": "70",
        })

        writer.writerow({
            "timestamp": "2026-09-12T12:00:01",
            "temperature_c": "70",
            "power_w": "250",
            "gpu_utilization_percent": "80",
        })

        writer.writerow({
            "timestamp": "2026-09-12T12:00:02",
            "temperature_c": "65",
            "power_w": "220",
            "gpu_utilization_percent": "75",
        })

        file.close()

        return file.name

    def test_analysis_calculates_measurements(self):
        filename = self.create_telemetry_file()

        results = analyze_telemetry(
            filename,
            max_temperature_c=85,
            max_power_w=300,
            min_average_gpu_utilization=60,
        )

        self.assertEqual(results["sample_count"], 3)
        self.assertEqual(results["max_temperature_c"], 70)
        self.assertAlmostEqual(
            results["average_temperature_c"],
            65
        )
        self.assertEqual(results["max_power_w"], 250)
        self.assertAlmostEqual(
            results["average_power_w"],
            223.333333,
            places=4
        )
        self.assertAlmostEqual(
            results["average_gpu_utilization_percent"],
            75
        )

    def test_analysis_passes_when_limits_are_met(self):
        filename = self.create_telemetry_file()

        results = analyze_telemetry(
            filename,
            max_temperature_c=85,
            max_power_w=300,
            min_average_gpu_utilization=70,
        )

        self.assertTrue(results["temperature_pass"])
        self.assertTrue(results["power_pass"])
        self.assertTrue(results["utilization_pass"])
        self.assertTrue(results["overall_pass"])

    def test_analysis_fails_when_temperature_exceeds_limit(self):
        filename = self.create_telemetry_file()

        results = analyze_telemetry(
            filename,
            max_temperature_c=65,
            max_power_w=300,
            min_average_gpu_utilization=60,
        )

        self.assertFalse(results["temperature_pass"])
        self.assertFalse(results["overall_pass"])

    def test_analysis_fails_when_power_exceeds_limit(self):
        filename = self.create_telemetry_file()

        results = analyze_telemetry(
            filename,
            max_temperature_c=85,
            max_power_w=200,
            min_average_gpu_utilization=60,
        )

        self.assertFalse(results["power_pass"])
        self.assertFalse(results["overall_pass"])


if __name__ == "__main__":
    unittest.main()
