import yaml


def load_config(filename="configs/gpu_test.yaml"):
    """Load the GPU test configuration from a YAML file."""

    with open(filename, "r") as file:
        config = yaml.safe_load(file)

    return config


if __name__ == "__main__":
    config = load_config()

    print("Test duration:", config["test"]["duration_seconds"])
    print("Sampling interval:", config["test"]["sampling_interval_seconds"])
    print("Maximum temperature:", config["limits"]["temperature"]["max_c"])
    print("Maximum power:", config["limits"]["power"]["max_w"])
    print(
        "Minimum GPU utilization:",
        config["limits"]["gpu_utilization"]["minimum_average_percent"]
    )
