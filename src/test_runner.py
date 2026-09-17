import json
import os
import subprocess
import time
from datetime import datetime

import yaml

from src.analyzer import (
    analyze_telemetry,
    plot_temperature,
    plot_power,
    plot_utilization,
    plot_gpu_clock,
    plot_memory_clock,
)
from src.report_generator import generate_report
from src.gpu_monitor import get_gpu_telemetry


CONFIG_FILE = "configs/gpu_test.yaml"


def load_config(filename):
    """Load YAML configuration file."""

    with open(filename, "r") as config_file:
        return yaml.safe_load(config_file)


def create_test_directory():
    """Create a numbered directory for the test run."""

    date_string = datetime.now().strftime("%Y-%m-%d")

    number = 1

    while True:
        directory = os.path.join(
            "data",
            "{}_test_{:03d}".format(
                date_string,
                number
            )
        )

        if not os.path.exists(directory):
            os.makedirs(directory)
            return directory

        number += 1


def start_workload(command, log_file, duration_seconds):
    """Start the GPU workload."""

    command = list(command)

    # FurMark requires a demo to actually run.
    # Add a maximum runtime automatically.
    if any("furmark" in str(item).lower() for item in command):

        if "--max-time" not in command:
            command.extend(
                [
                    "--max-time",
                    str(duration_seconds)
                ]
            )

    print()
    print("Starting workload:")
    print(" ".join(command))
    print()

    workload_log = open(
        log_file,
        "w",
        encoding="utf-8"
    )

    process = subprocess.Popen(
        command,
        stdout=workload_log,
        stderr=subprocess.STDOUT,
    )

    return process, workload_log


def log_telemetry(
    telemetry_file,
    process,
    duration_seconds,
    sampling_interval_seconds
):
    """Collect GPU telemetry while the workload is running."""

    telemetry_fields = [
        "timestamp",
        "name",
        "driver_version",
        "memory_total_mib",
        "temperature_c",
        "power_w",
        "power_limit_w",
        "gpu_utilization_percent",
        "memory_utilization_percent",
        "gpu_clock_mhz",
        "memory_clock_mhz",
    ]

    with open(
        telemetry_file,
        "w",
        newline=""
    ) as csv_file:

        import csv

        writer = csv.DictWriter(
            csv_file,
            fieldnames=telemetry_fields
        )

        writer.writeheader()

        start_time = time.time()

        while True:

            elapsed = time.time() - start_time

            if elapsed >= duration_seconds:
                break

            try:
                telemetry = get_gpu_telemetry()

                row = {
                    "timestamp": datetime.now().isoformat(),
                    **telemetry
                }

                writer.writerow(row)
                csv_file.flush()

                print(
                    "GPU: {:5.1f}% | "
                    "Temp: {:5.1f} C | "
                    "Power: {:7.2f} W | "
                    "Core: {:6.0f} MHz | "
                    "Memory: {:6.0f} MHz".format(
                        telemetry[
                            "gpu_utilization_percent"
                        ],
                        telemetry[
                            "temperature_c"
                        ],
                        telemetry[
                            "power_w"
                        ],
                        telemetry[
                            "gpu_clock_mhz"
                        ],
                        telemetry[
                            "memory_clock_mhz"
                        ],
                    )
                )

            except Exception as error:
                print(
                    "Telemetry error: {}".format(
                        error
                    )
                )

            time.sleep(
                sampling_interval_seconds
            )


def stop_workload(process, log_file):
    """Stop the GPU workload."""

    if process.poll() is None:

        process.terminate()

        try:
            process.wait(timeout=5)

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    log_file.close()


def main():
    """Run the complete GPU validation test."""

    config = load_config(CONFIG_FILE)

    test_config = config["test"]
    workload_config = config["workload"]
    limits = config["limits"]

    duration_seconds = int(
        test_config["duration_seconds"]
    )

    sampling_interval_seconds = float(
        test_config[
            "sampling_interval_seconds"
        ]
    )

    test_directory = create_test_directory()

    telemetry_file = os.path.join(
        test_directory,
        "gpu_telemetry.csv"
    )

    workload_log = os.path.join(
        test_directory,
        "workload.log"
    )

    results_file = os.path.join(
        test_directory,
        "results.json"
    )

    print()
    print("==============================")
    print(" GPU Hardware Validation Test")
    print("==============================")
    print()

    print(
        "Test directory: {}".format(
            test_directory
        )
    )

    print(
        "Duration: {} seconds".format(
            duration_seconds
        )
    )

    print(
        "Sampling interval: {} seconds".format(
            sampling_interval_seconds
        )
    )

    print(
        "Workload: {}".format(
            workload_config["name"]
        )
    )

    command = workload_config["command"]

    process, log_file = start_workload(
        command,
        workload_log,
        duration_seconds
    )

    print("Collecting GPU telemetry...")
    print()

    try:

        log_telemetry(
            telemetry_file,
            process,
            duration_seconds,
            sampling_interval_seconds
        )

    finally:

        stop_workload(
            process,
            log_file
        )

    print()
    print("Test complete.")
    print()

    # Analyze telemetry.
    results = analyze_telemetry(
        telemetry_file,
        limits["temperature"]["max_c"],
        limits["power"]["max_w"],
        limits["gpu_utilization"][
            "minimum_average_percent"
        ],
        workload_log=workload_log,
    )

    # Save analysis results.
    with open(
        results_file,
        "w"
    ) as json_file:

        json.dump(
            results,
            json_file,
            indent=4
        )

    # Generate plots.
    temperature_plot = os.path.join(
        test_directory,
        "temperature.png"
    )

    power_plot = os.path.join(
        test_directory,
        "power.png"
    )

    utilization_plot = os.path.join(
        test_directory,
        "utilization.png"
    )

    gpu_clock_plot = os.path.join(
        test_directory,
        "gpu_clock.png"
    )

    memory_clock_plot = os.path.join(
        test_directory,
        "memory_clock.png"
    )

    plot_temperature(
        telemetry_file,
        temperature_plot
    )

    plot_power(
        telemetry_file,
        power_plot
    )

    plot_utilization(
        telemetry_file,
        utilization_plot
    )

    plot_gpu_clock(
        telemetry_file,
        gpu_clock_plot
    )

    plot_memory_clock(
        telemetry_file,
        memory_clock_plot
    )

    # Generate HTML report.
    report_file = os.path.join(
        test_directory,
        "report.html"
    )

    generate_report(
        results_file,
        report_file
    )

    # Print results.
    print()
    print("Validation Result")
    print("-----------------")

    print(
        "Maximum Temperature: {:.1f} C".format(
            results["max_temperature_c"]
        )
    )

    print(
        "Average Temperature: {:.1f} C".format(
            results["average_temperature_c"]
        )
    )

    print(
        "Maximum Power: {:.2f} W".format(
            results["max_power_w"]
        )
    )

    print(
        "Average Power: {:.2f} W".format(
            results["average_power_w"]
        )
    )

    print(
        "Average GPU Utilization: {:.1f}%".format(
            results[
                "average_gpu_utilization_percent"
            ]
        )
    )

    # ---------------------------------------------------------
    # FurMark performance measurements
    #
    # These are measurements only.
    # They do NOT affect PASS/FAIL.
    # ---------------------------------------------------------

    if results.get("minimum_fps") is not None:

        print(
            "Minimum FPS: {:.0f}".format(
                results["minimum_fps"]
            )
        )

        print(
            "Average FPS: {:.0f}".format(
                results["average_fps"]
            )
        )

        print(
            "Maximum FPS: {:.0f}".format(
                results["maximum_fps"]
            )
        )

    if results.get("frames") is not None:

        print(
            "Frames Rendered: {}".format(
                results["frames"]
            )
        )

    print()

    print(
        "Temperature Check: {}".format(
            "PASS"
            if results["temperature_pass"]
            else "FAIL"
        )
    )

    print(
        "Power Check: {}".format(
            "PASS"
            if results["power_pass"]
            else "FAIL"
        )
    )

    print(
        "GPU Utilization Check: {}".format(
            "PASS"
            if results["utilization_pass"]
            else "FAIL"
        )
    )

    print()

    if results["overall_pass"]:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

    print()

    print(
        "Report generated: {}".format(
            report_file
        )
    )


if __name__ == "__main__":
    main()
