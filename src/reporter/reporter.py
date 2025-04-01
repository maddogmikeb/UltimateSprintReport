def show_login_details(self):
    me = self.jira.myself()
    return ("""
        <table>
            <tr>
            <td>Currently logged in as:</td>
            <td> """
                + me["displayName"]
                + """</td>
            <td><img src='"""
                + me["avatarUrls"]["32x32"]
                + """' /><td>
            </tr>
        </table>
        """)

def show_sprint_test_case_statistics(self):
    return "<h2>Sprint Test Case Statistics</h2>" + self.test_case_statistics_data_table.to_html(escape=False)

def show_sprint_issue_types_statistics(self):
    return """<h2>Issue Type Statistics</h2>""" + self.sprint_issue_types_statistics.to_html()

def show_committed_vs_planned(self):
    return (
        """
    <h2>Sprint Estimates & Issue Counts</h2>
    <table>
    <thead>
        <tr>
        <th>Category</th>
        <th>Count</th>
        <th>Estimated</th>
        </tr>
    </thead>
    <tbody>
        <tr>
        <td>Total Committed</td>
        <td style='text-align:right'>"""
        + str(self.TotalCommitted[0])
        + """</td>
        <td style='text-align:right'>"""
        + f"{self.TotalCommitted[1]:.1f}"
        + """</td>
        </tr>
        <tr>
        <td colspan="3">
            <hr />
        </td>
        </tr>
        <tr>
        <td>Completed</td>
        <td style='text-align:right'>"""
        + str(self.Done.count)
        + """</td>
        <td style='text-align:right'>"""
        + f"{self.Done.points:.1f}"
        + """</td>
        </tr>
        <tr>
        <td>Completed Outside</td>
        <td style='text-align:right'>"""
        + str(self.CompletedOutside.count)
        + """</td>
        <td style='text-align:right'>"""
        + f"{self.CompletedOutside.points:.1f}"
        + """</td>
        </tr>
        <tr>
            <td>
                <hr />
            </td>
            <td style='text-align:right'>"""
            + str(self.Done.count + self.CompletedOutside.count)
            + """</td>
            <td style='text-align:right'>"""
            + f"{self.Done.points + self.CompletedOutside.points:.1f}"
            + """</td>
        </tr>
        <tr>
        <td>In Progress</td>
        <td style='text-align:right'>"""
        + str(self.InProgress.count)
        + """</td>
        <td style='text-align:right'>"""
        + f"{self.InProgress.points:.1f}"
        + """</td>
        </tr>
        <tr>
        <td>To Do</td>
        <td style='text-align:right'>"""
        + str(self.ToDo.count)
        + """</td>
        <td style='text-align:right'>"""
        + f"{self.ToDo.points:.1f}"
        + """</td>
        </tr>
        <tr>
            <td>
                <hr />
            </td>
            <td style='text-align:right'>"""
            + str(self.InProgress.count + self.ToDo.count)
            + """</td>
            <td style='text-align:right'>"""
            + f"{self.InProgress.points + self.ToDo.points:.1f}"
            + """</td>
        </tr>
        <tr>
        <td>Removed</td>
        <td style='text-align:right'>"""
        + str(self.Removed.count)
        + """</td>
        <td style='text-align:right'>"""
        + f"{self.Removed.points:.1f}"
        + """</td>
        </tr>
    </tbody>
    </table>
""")

def show_sprint_details(self):
    return (
        """
    <h2>Sprint Details</h2>
    <table>
    <tbody>
        <tr>
        <td>Board</td>
        <td>"""
        + self.board_name
        + """</td>
        </tr>
        <tr>
        <td>Sprint Name</td>
        <td><a target='_blank' href='"""
        + self.sprint_report_url
        + """'>"""
        + self.sprint_details["name"]
        + """</a></td>
        </tr>
        <tr>
        <td>Sprint Goal</td>
        <td>"""
        + self.sprint_details["goal"]
        + """</td>
        </tr>
        <tr>
        <td>Start Date</td>
        <td>"""
        + self.sprint_details["start_date_string"]
        + """</td>
        </tr>
        <tr>
        <td>End Date</td>
        <td>"""
        + self.sprint_details["end_date_string"]
        + """</td>
        </tr>
        <tr>
        <td>Duration (days)</td>
        <td>"""
        + self.sprint_details["duration_days"]
        + """</td>
        </tr>
    </tbody>
    </table>
""")

def show_predictability(self):
    predictability_data_table = """
    <h2>Predictability Statistics</h2>
    <table>
    <thead>
        <tr>
        <th>Sprint</th>
        <th>Estimated</th>
        <th>Completed</th>
        <th>Predictability Score</th>
        <th>Stars</th>
        </tr>
    </thead>
    <tbody>
"""
    total_predictability_score = 0
    total = 0
    for data in self.predictability_data:
        predictability_score = (
            f"{data['predictability_score']:.2f}"
            if data["predictability_score"] is not None
            else "-"
        )
        if data["predictability_score"] is not None:
            total_predictability_score += data["predictability_score"]
            total += 1
        predictability_data_table += f"""
                <tr>
                    <td>{data['name']}</td>
                    <td style='text-align:right'>{data['estimated_points']}</td>
                    <td style='text-align:right'>{data['completed_points']}</td>
                    <td style='text-align:right'>{predictability_score}</td>
                    <td style='text-align:right'>{data['stars']}</td>
                </tr>
                """
    meanScore = total_predictability_score / total if total > 0 else "-"
    predictability_data_table += f"""
        <tr>
            <td colspan="3" style='font-weight: bold'>Average</td>
            <td style='font-weight: bold; text-align:right'>{f"{meanScore:.2f}"}</td>
            <td style='font-weight: bold; text-align:right'>{self._calculate_predictability_score_stars(meanScore)}</td>
        </tr>
        """
    predictability_data_table += """
    </tbody>
</table>
"""
    return predictability_data_table

def show_sprint_predictability(self):
    return (
        f"""<h2> Rating: {self.this_sprint_predictability['stars']} </h2>"""
        if self.this_sprint_predictability
        else ""
    )

def show_epic_statistics(self):
    epic_statistics_table = """
    <h2>Epics Within Sprint Statistics</h2>
    <table>
    <thead>
        <tr>
        <th>Parent</th>
        <th>Epic</th>
        <th>Status</th>
        <th>Completed Estimate %</th>
        <th>Completed Count %</th>
        </tr>
    </thead>
    <tbody>
    """
    for epic in sorted(
        self.epic_statistics,
        key=lambda i: (i["parent_summary"] or "") + (i["summary"] or ""),
    ):
        parent = (
            f"<a href='{self.base_url}/browse/{epic['parent_key']}' target='_blank'>[{epic['parent_key']}] {epic['parent_summary']}</a>"
            if epic["parent_key"] is not None
            else "-"
        )
        epic_details = f"<a href='{self.base_url}/browse/{epic['key']}' target='_blank'>[{epic['key']}] {epic['summary']}</a>"
        pts = (
            f"{epic['completed_pts_perc']:.1f}"
            if epic["completed_pts_perc"] is not None
            else "-"
        )
        cnt = (
            f"{epic['completed_cnt_perc']:.1f}"
            if epic["completed_cnt_perc"] is not None
            else "-"
        )
        epic_statistics_table += f"""
    <tr>
        <td>{parent}</td>
        <td>{epic_details}</td>
        <td>{epic['status_category']}</td>
        <td style='text-align:right'>{pts}</td>
        <td style='text-align:right'>{cnt}</td>
    </tr>
    """

    epic_statistics_table += """
    </tbody>
</table>
"""
    return epic_statistics_table
def show_burndown_chart(self):
    return self.burndown_chart
def show_burndown_table(self):
    return """<h2>Burndown Table</h2>""" + self.burndown_table.to_html(
        escape=False
    ).replace("NaN", "-")
def show_committed_vs_planned_chart(self):
    return self.committed_vs_planned_chart
def show_report(self):
    return (
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
            <td colspan='2'>
            """
        + self.show_sprint_details()
        + """
            </td>
            <td>
            """
        + self.show_sprint_predictability()
        + """
            </td>
            </tr>
            <tr>
            <td>
            """
        + self.show_committed_vs_planned_chart()
        + """
            </td>
            <td>
            """
        + self.show_burndown_chart()
        + """
            </td>
            <td>
            """
        + self.show_committed_vs_planned()
        + """
            </td>
            </tr>
            <tr>
            <td colspan='3'>
            """
        + self.show_sprint_issue_types_statistics()
        + """
            </td>
            </tr>
            <tr>
            <td colspan='3'>
            """
        + self.show_epic_statistics()
        + """
            </td>
            </tr>
            <tr>
            <td colspan='3'>
            """
        + self.show_predictability()
        + """
            <td>
            </tr>
        """
        +  ("""
            <tr>
            <td colspan='3'>
            """ + self.show_sprint_test_case_statistics()
            + """
            <td>
            </tr>
        """ if self.test_case_statistics_data_table is not None else "")
        + """
            <tr>
            <td colspan='3'>
            """
        + self.show_burndown_table()
        + """
            <td>
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
                var images = document.querySelectorAll("img.popupable");
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
    """)
