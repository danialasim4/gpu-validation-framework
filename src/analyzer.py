import csv
import re
from datetime import datetime

import matplotlib.pyplot as plt


def get_elapsed_times(filename):
    """Get elapsed time in seconds from telemetry timestamps."""

    timestamps = []

    with open(filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            timestamps.append(
                datetime.fromisoformat(
                    row["timestamp"]
                )
            )

    if not timestamps:
        raise ValueError("Telemetry file contains no timestamps.")

    start_time = timestamps[0]

    elapsed_times = []

    for timestamp in timestamps:
        elapsed_seconds = (
            timestamp - start_time
        ).total_seconds()

        elapsed_times.append(elapsed_seconds)

    return elapsed_times


def analyze_telemetry(
    filename,
    max_temperature_c,
    max_power_w,
    min_average_gpu_utilization,
    workload_log=None,
):
    """Analyze GPU telemetry and determine pass/fail."""

    rows = []

    with open(filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            rows.append(row)

    if not rows:
        raise ValueError("Telemetry file contains no data.")

    temperatures = [
        float(row["temperature_c"])
        for row in rows
    ]

    powers = [
        float(row["power_w"])
        for row in rows
    ]

    utilizations = [
        float(row["gpu_utilization_percent"])
        for row in rows
    ]

    max_temperature = max(temperatures)

    average_temperature = (
        sum(temperatures) / len(temperatures)
    )

    max_power = max(powers)

    average_power = (
        sum(powers) / len(powers)
    )

    average_gpu_utilization = (
        sum(utilizations) / len(utilizations)
    )

    temperature_pass = (
        max_temperature <= float(max_temperature_c)
    )

    power_pass = (
        max_power <= float(max_power_w)
    )

    utilization_pass = (
        average_gpu_utilization
        >= float(min_average_gpu_utilization)
    )

    # ---------------------------------------------------------
    # FurMark performance measurements
    #
    # These values are measurements only.
    # They do NOT affect PASS/FAIL.
    # ---------------------------------------------------------

    frames = None
    duration_ms = None
    minimum_fps = None
    average_fps = None
    maximum_fps = None

    if workload_log is not None:

        with open(
            workload_log,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as log_file:

            log_contents = log_file.read()

        # Example:
        # - frames               : 3347
        match = re.search(
            r"frames\s*:\s*(\d+)",
            log_contents,
            re.IGNORECASE
        )

        if match:
            frames = int(match.group(1))

        # Example:
        # - duration             : 20001 ms
        match = re.search(
            r"duration\s*:\s*(\d+)\s*ms",
            log_contents,
            re.IGNORECASE
        )

        if match:
            duration_ms = int(match.group(1))

        # Example:
        # - FPS (min/avg/max)    : 155 / 167 / 170
        match = re.search(
            r"FPS\s*\(min/avg/max\)\s*:\s*"
            r"([\d.]+)\s*/\s*"
            r"([\d.]+)\s*/\s*"
            r"([\d.]+)",
            log_contents,
            re.IGNORECASE
        )

        if match:
            minimum_fps = float(match.group(1))
            average_fps = float(match.group(2))
            maximum_fps = float(match.group(3))

    overall_pass = (
        temperature_pass
        and power_pass
        and utilization_pass
    )

    return {
        "sample_count": len(rows),

        "max_temperature_c": max_temperature,
        "average_temperature_c": average_temperature,

        "max_power_w": max_power,
        "average_power_w": average_power,

        "average_gpu_utilization_percent": (
            average_gpu_utilization
        ),

        "frames": frames,
        "duration_ms": duration_ms,
        "minimum_fps": minimum_fps,
        "average_fps": average_fps,
        "maximum_fps": maximum_fps,

        "temperature_pass": temperature_pass,
        "power_pass": power_pass,
        "utilization_pass": utilization_pass,

        "overall_pass": overall_pass,
    }


def plot_temperature(filename, output_filename):
    """Create a temperature vs. elapsed time plot."""

    elapsed_times = get_elapsed_times(filename)

    temperatures = []

    with open(filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            temperatures.append(
                float(row["temperature_c"])
            )

    plt.figure()

    plt.plot(
        elapsed_times,
        temperatures
    )

    plt.xlabel("Elapsed Time (seconds)")
    plt.ylabel("Temperature (C)")
    plt.title("GPU Temperature During Test")

    plt.grid(True)

    plt.savefig(output_filename)

    plt.close()


def plot_power(filename, output_filename):
    """Create a power vs. elapsed time plot."""

    elapsed_times = get_elapsed_times(filename)

    powers = []

    with open(filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            powers.append(
                float(row["power_w"])
            )

    plt.figure()

    plt.plot(
        elapsed_times,
        powers
    )

    plt.xlabel("Elapsed Time (seconds)")
    plt.ylabel("Power (W)")
    plt.title("GPU Power During Test")

    plt.grid(True)

    plt.savefig(output_filename)

    plt.close()


def plot_utilization(filename, output_filename):
    """Create GPU utilization vs. elapsed time plot."""

    elapsed_times = get_elapsed_times(filename)

    utilizations = []

    with open(filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            utilizations.append(
                float(row["gpu_utilization_percent"])
            )

    plt.figure()

    plt.plot(
        elapsed_times,
        utilizations
    )

    plt.xlabel("Elapsed Time (seconds)")
    plt.ylabel("GPU Utilization (%)")
    plt.title("GPU Utilization During Test")

    plt.grid(True)

    plt.savefig(output_filename)

    plt.close()


def plot_gpu_clock(filename, output_filename):
    """Create GPU core clock vs. elapsed time plot."""

    elapsed_times = get_elapsed_times(filename)

    clocks = []

    with open(filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            clocks.append(
                float(row["gpu_clock_mhz"])
            )

    plt.figure()

    plt.plot(
        elapsed_times,
        clocks
    )

    plt.xlabel("Elapsed Time (seconds)")
    plt.ylabel("GPU Core Clock (MHz)")
    plt.title("GPU Core Clock During Test")

    plt.grid(True)

    plt.savefig(output_filename)

    plt.close()


def plot_memory_clock(filename, output_filename):
    """Create GPU memory clock vs. elapsed time plot."""

    elapsed_times = get_elapsed_times(filename)

    clocks = []

    with open(filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            clocks.append(
                float(row["memory_clock_mhz"])
            )

    plt.figure()

    plt.plot(
        elapsed_times,
        clocks
    )

    plt.xlabel("Elapsed Time (seconds)")
    plt.ylabel("GPU Memory Clock (MHz)")
    plt.title("GPU Memory Clock During Test")

    plt.grid(True)

    plt.savefig(output_filename)

    plt.close()
