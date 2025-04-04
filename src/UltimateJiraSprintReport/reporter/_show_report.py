"""
This module contains functions for generating various sections of an HTML sprint report.
"""

from string import Template


def show_report(self):
    """
    Generates the full HTML report for the sprint.

    Returns:
        str: HTML string containing the full sprint report.
    """
    template = Template(
        """
        <html>
        <head>
            <style>
                table.dataframe, table {
                    width: 100%;
                }
                table.dataframe th, th {
                    text-align: left;
                    font-weight: bold;
                }
                table.dataframe tbody th, tbody th {
                    font-weight: bold;
                }
                table.dataframe td, td {
                    vertical-align: top;
                    text-align: left;
                }
                h2 {
                    text-align: left;
                }
                #main-table {
                    border-spacing: 20px;
                }
                #committed_vs_planned_chart {
                    max-width: 200px;
                }
                #burndown_chart {
                    max-width: 200px;
                }
                /* Popup container - can be anything you want */
                .popup {
                    display: none; /* Hidden by default */
                    position: fixed; /* Stay in place */
                    z-index: 1; /* Sit on top */
                    padding-top: 100px; /* Location of the box */
                    left: 0;
                    top: 0;
                    width: 100%; /* Full width */
                    height: 100%; /* Full height */
                    overflow: auto; /* Enable scroll if needed */
                    background-color: rgb(0,0,0); /* Fallback color */
                    background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
                }
                /* Popup content */
                .popup-content {
                    margin: auto;
                    display: block;
                    width: 80%;
                    max-width: 700px;
                }
                /* Close button */
                .close {
                    position: absolute;
                    top: 15px;
                    right: 35px;
                    color: #f1f1f1;
                    font-size: 40px;
                    font-weight: bold;
                    transition: 0.3s;
                }
                .close:hover,
                .close:focus {
                    color: #bbb;
                    text-decoration: none;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <h1>Ultimate Sprint Report</h1>
            <table id='main-table'>
            <tbody>
                <tr>
                    <td colspan='2'>${sprint_details}</td>
                    <td>${sprint_predictability}</td>
                </tr>
                <tr>
                    <td>${committed_vs_planned_chart}</td>
                    <td>${burndown_chart}</td>
                    <td>${committed_vs_planned}</td>
                </tr>
                <tr>
                    <td colspan='3'>${sprint_issue_types_statistics}</td>
                </tr>
                <tr>
                    <td colspan='3'>${epic_statistics}</td>
                </tr>
                <tr>
                    <td colspan='3'>${predictability}</td>
                </tr>
                ${test_case_statistics_row}
                <tr>
                    <td colspan='3'>${burndown_table}</td>
                </tr>
            </tbody>
            </table>
            <!-- The Popup -->
            <div id="popup" class="popup">
                <span class="close" onclick="closePopup()">&times;</span>
                <img class="popup-content" id="popup-img">
            </div>
            <script>
                // Open the popup
                function openPopup(src) {
                    var popup = document.getElementById("popup");
                    var popupImg = document.getElementById("popup-img");
                    popup.style.display = "block";
                    popupImg.src = src;
                }
                // Close the popup
                function closePopup() {
                    var popup = document.getElementById("popup");
                    popup.style.display = "none";
                }
                listenerSet = false;
                function setListeners() {
                    if (!listenerSet) {
                    var images = document.querySelectorAll("img");
                    images.forEach(function(img) {
                        img.addEventListener("click", function() {
                                openPopup(img.src);
                        });
                        listenerSet = true;
                    });
                    }
                }
                // Add click event to all images within the limited-width class
                document.addEventListener("DOMContentLoaded", function() {
                    setListeners();
                });
                document.addEventListener("click", function(event) {
                    setListeners();
                });
            </script>
        </body>
        </html>
        """
    )

    test_case_statistics_template = Template(
        """
        <tr>
            <td colspan='3'>${test_case_statistics}</td>
        </tr>
        """
    )

    if self.test_case_statistics_data_table is not None:
        test_case_statistics_row = test_case_statistics_template.substitute(
            test_case_statistics=self.show_sprint_test_case_statistics()
        )
    else:
        test_case_statistics_row = ""

    return template.substitute(
        sprint_details=self.show_sprint_details(),
        sprint_predictability=self.show_sprint_predictability(),
        committed_vs_planned_chart=self.show_committed_vs_planned_chart(),
        burndown_chart=self.show_burndown_chart(),
        committed_vs_planned=self.show_committed_vs_planned(),
        sprint_issue_types_statistics=self.show_sprint_issue_types_statistics(),
        epic_statistics=self.show_epic_statistics(),
        predictability=self.show_predictability(),
        test_case_statistics_row=test_case_statistics_row,
        burndown_table=self.show_burndown_table(),
    )
