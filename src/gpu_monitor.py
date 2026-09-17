import subprocess


def get_gpu_telemetry():
    """Read telemetry from the first NVIDIA GPU."""

    query = (
        "name,"
        "driver_version,"
        "memory.total,"
        "temperature.gpu,"
        "power.draw,"
        "power.limit,"
        "utilization.gpu,"
        "utilization.memory,"
        "clocks.gr,"
        "clocks.mem"
    )

    command = [
        "nvidia-smi",
        "--query-gpu=" + query,
        "--format=csv,noheader,nounits",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    values = [value.strip() for value in result.stdout.strip().split(",")]

    return {
        "name": values[0],
        "driver_version": values[1],
        "memory_total_mib": float(values[2]),
        "temperature_c": float(values[3]),
        "power_w": float(values[4]),
        "power_limit_w": float(values[5]),
        "gpu_utilization_percent": float(values[6]),
        "memory_utilization_percent": float(values[7]),
        "gpu_clock_mhz": float(values[8]),
        "memory_clock_mhz": float(values[9]),
    }


if __name__ == "__main__":
    telemetry = get_gpu_telemetry()

    print("GPU Telemetry")
    print("--------------")

    for key, value in telemetry.items():
        print("{}: {}".format(key, value))
