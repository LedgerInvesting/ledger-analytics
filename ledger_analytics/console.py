import os
from io import StringIO

from rich.console import Console


class RichConsole(Console):
    def __init__(self, *args, **kwargs):
        self._disable_rich = (
            os.getenv("DISABLE_RICH_CONSOLE", "false").lower() == "true"
        )
        if self._disable_rich:
            kwargs["file"] = StringIO()
        super().__init__(*args, **kwargs)

    def get_stdout(self) -> str:
        if self._disable_rich:
            return self.file.getvalue()
        return ""
