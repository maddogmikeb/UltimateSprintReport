"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template


def show_burndown_table(self):
    """
    Generates an HTML section displaying the burndown table.

    Returns:
        str: HTML string containing the burndown table.
    """
    if not hasattr(self, "burndown_table") or self.burndown_table is None:
        raise ValueError("Burndown table is not available.")

    template = Template(
        """
        <h2>Burndown Table</h2>
        ${table}
        """
    )

    df = self.burndown_table
    df.index = df.index + 1
    
    return template.substitute(
        table=df.to_html(escape=False).replace("NaN", "-")
    )
