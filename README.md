# Ultimate Jira Sprint Report

## Overview

The **Ultimate Jira Sprint Report** is a Python library designed to generate detailed Agile sprint reports using data from Jira. It provides actionable insights into sprint performance, including burndown charts, velocity metrics, and epic-level statistics. This tool is ideal for Agile teams looking to improve sprint predictability and track progress effectively.

## Features

- **Sprint Data Loading**: Fetch sprint data directly from Jira for seamless integration.
- **Burndown Charts**: Generate visualizations to track sprint progress and identify bottlenecks.
- **Velocity Metrics**: Analyze sprint predictability and team velocity over time.
- **Epic and Issue Statistics**: Gain insights into epic-level and issue-level performance for better planning.
- **Customizable Reports**: Tailor reports to meet your team's specific needs.

## Installation

To install the library, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/maddogmikeb/UltimateJiraSprintReport.git
   cd UltimateJiraSprintReport
   ```

2. Install the library and its dependencies:

   ```bash
   pip install .
   ```

Alternatively, you can install the dependencies manually:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use the library, import it into your Python project and initialize it with your Jira credentials:

```python
from UltimateJiraSprintReport import UltimateJiraSprintReport

# Initialize the report generator
report = UltimateJiraSprintReport(
    username="your_username", 
    password="your_api_key", 
    host="your_jira_host"
)

# Load sprint data
report.load(project="PROJECT_KEY", board_id=123, sprint_id=456)

# Access generated reports
print(report.burndown_chart)  # Path to the burndown chart
print(report.burndown_table)  # Pandas DataFrame with sprint data
```

### Example: Running the Application

To run the application directly, execute the following command:

```bash
python src/main.py
```

Make sure to provide your Jira credentials and the necessary parameters for loading sprint data.

### Environment Variables (Optional)

You can also configure your Jira credentials and host using environment variables for better security:

```bash
export JIRA_USERNAME=your_username
export JIRA_API_KEY=your_api_key
export JIRA_HOST=your_jira_host
```

Then, initialize the report generator without passing credentials explicitly:

```python
report = UltimateJiraSprintReport()
```

## Example Output

### Burndown Chart

The library generates a burndown chart to visualize sprint progress:

![Burndown Chart Example](docs/images/burndown_chart_example.png)

### Velocity Metrics

Analyze team velocity and sprint predictability:

| Sprint | Planned Points | Completed Points | Velocity (%) |
|--------|----------------|------------------|--------------|
| Sprint 1 | 50             | 45               | 90%          |
| Sprint 2 | 60             | 55               | 92%          |

## Contributing

Contributions are welcome! If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to your branch (`git push origin feature-name`).
5. Open a pull request.

Please ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Support

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/maddogmikeb/UltimateJiraSprintReport).

## Roadmap

- Add support for custom Jira fields in reports.
- Improve caching for faster data retrieval.
- Add more visualization options (e.g., cumulative flow diagrams).
- Support for exporting reports to PDF and Excel formats.

---

Thank you for using **Ultimate Jira Sprint Report**! 🚀
