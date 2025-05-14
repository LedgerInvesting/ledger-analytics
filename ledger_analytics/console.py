import os
from io import StringIO

from rich.console import Console


class RichConsole(Console):
    def __init__(self, *args, **kwargs):
        self._capture = (
            os.getenv("LEDGER_ANALYTICS_API_CAPTURE", "false").lower() == "true"
        )
        if self._capture:
            kwargs["file"] = StringIO()
        super().__init__(*args, **kwargs)

    def get_captured(self) -> str:
        if self._capture:
            return self.file.getvalue()
        return ""
