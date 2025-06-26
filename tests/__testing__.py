# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring line-too-long
# pylint: disable=too-few-public-methods

import os
import time
import tempfile
import webbrowser

class Testing:

    INTERACTIVE_TESTING_ENABLED = True

    @staticmethod
    def write_to_temp_html_file_then_open(html):
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(html)
            temp_file_path = temp_file.name
        webbrowser.open(temp_file_path)
        try:
            time.sleep(3)
            os.remove(temp_file_path)
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"An error as occurred: {e}")
