import os
from io import StringIO

from rich.console import Console


class RichConsole(Console):
    def __init__(self, *args, **kwargs):
        self._stdout = (
            os.getenv("LEDGER_ANALYTICS_API_SHOW_STDOUT", "true").lower() == "true"
        )
        if not self._stdout:
            kwargs["file"] = StringIO()
        super().__init__(*args, **kwargs)

    def get_stdout(self) -> str:
        if not self._stdout:
            return self.file.getvalue()
        return ""
