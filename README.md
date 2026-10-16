
# Automated GPU Hardware Validation Framework

A Python-based GPU validation framework designed to automate stress testing, hardware telemetry collection, and pass/fail reporting under configurable test conditions.

The project was developed to investigate GPU thermal and power behavior on a system and to demonstrate practical skills in hardware validation, test automation, data analysis, and software testing.

## Project Objectives

- Automate GPU workload execution under controlled test conditions.
- Collect GPU telemetry throughout each test.
- Evaluate measurements against configurable validation limits.
- Analyze benchmark performance and visualize hardware behavior.
- Generate test results and HTML reports.
- Verify the analysis logic using automated unit tests and continuous integration.

## Features

### Automated GPU Testing

- Launches FurMark from a Python test runner.
- Supports a configurable test duration and telemetry sampling interval.
- Creates a separate output directory for each test run.

### GPU Telemetry Collection

Collects GPU measurements using NVIDIA `nvidia-smi`, including:

- GPU name and driver version
- GPU temperature
- Power draw and configured power limit
- GPU utilization
- Memory utilization
- GPU core clock
- GPU memory clock
- Total GPU memory

Telemetry is recorded in CSV format for later analysis.

### Automated Analysis and Validation

The analyzer processes recorded telemetry and evaluates configurable criteria, including:

- Maximum GPU temperature
- Maximum GPU power draw
- Minimum average GPU utilization

Each criterion receives a PASS or FAIL result. The overall test passes only when all configured validation checks pass.

The framework also extracts available FurMark performance information, including minimum, average, and maximum FPS and frame count. These performance measurements are reported separately from the configured validation checks.

### Visualization and Reporting

Each completed run can produce:

- CSV telemetry data
- JSON analysis results
- Temperature-versus-time graph
- Power-versus-time graph
- GPU utilization-versus-time graph
- GPU core clock-versus-time graph
- GPU memory clock-versus-time graph
- An HTML report summarizing measurements and validation results

### Unit Testing and Continuous Integration

- Uses Python's `unittest` framework to test the analysis logic.
- Includes tests for measurement calculations, successful validation, temperature-limit violations, and power-limit violations.
- Uses Git for version control and GitHub for repository hosting.
- Uses GitHub Actions to run the unit tests automatically on pushes and pull requests.

The GitHub Actions workflow verifies software behavior on a GitHub-hosted runner. It does not run FurMark or perform physical GPU validation.

## System Configuration

### Software Environment

The development environment used:

- Python 3.8.10
- NVIDIA driver 470.256.02
- CUDA 11.4
- NVIDIA GeForce RTX 3070 Ti
- FurMark for GPU stress testing

The GitHub Actions workflow uses Python 3.11 to test the software.

## Project Architecture

The main components are:

- `src/test_runner.py` — coordinates test execution, telemetry collection, analysis, and report generation.
- `src/gpu_monitor.py` — retrieves GPU telemetry through `nvidia-smi`.
- `src/analyzer.py` — calculates measurements and evaluates validation criteria.
- `src/report_generator.py` — generates an HTML report using a Jinja2 template.
- `configs/gpu_test.yaml` — defines test duration, sampling interval, workload settings, and validation limits.
- `tests/` — contains automated unit tests.
- `.github/workflows/tests.yml` — defines the GitHub Actions continuous-integration workflow.

## Installation

### Prerequisites

- Linux system
- NVIDIA GPU with a working NVIDIA driver
- `nvidia-smi` available in the terminal
- FurMark installed
- Python and Git

