import json
import os

from jinja2 import Environment, FileSystemLoader


def generate_report(results_file, output_file):
    """Generate an HTML validation report."""

    with open(results_file, "r") as json_file:
        results = json.load(json_file)

    template_directory = os.path.join(
        "reports",
        "templates"
    )

    environment = Environment(
        loader=FileSystemLoader(template_directory)
    )

    template = environment.get_template("report.html")

    html = template.render(
        results=results
    )

    with open(output_file, "w") as html_file:
        html_file.write(html)

    print("Report generated: {}".format(output_file))


if __name__ == "__main__":
    results_file = "data/2026-09-12_test_001/results.json"
    output_file = "data/2026-09-12_test_001/report.html"

    generate_report(
        results_file,
        output_file
    )
