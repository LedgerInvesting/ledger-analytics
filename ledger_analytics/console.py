import os
from io import StringIO

from rich.console import Console


class RichConsole(Console):
    _capture = os.getenv("LEDGER_ANALYTICS_API_CAPTURE", False)

    def __init__(self, *args, **kwargs):
        if self._capture:
            kwargs["file"] = StringIO()
        super().__init__(*args, **kwargs)

    def get_captured(self) -> str:
        if self._capture:
            return self.file.getvalue()
        return ""
