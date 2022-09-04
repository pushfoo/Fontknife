from io import TextIOBase
from typing import TypeVar


S = TypeVar("S", bound=TextIOBase)


class OutputHelper:
    """
    Encapsulate common operations on source output streams

    Subclasses should be made for specific languages.
    """
    def __init__(self, stream: S):
        super().__init__()
        self._stream = stream
        self._indent_level = 0

    def write(self, s: str) -> None:
        self._stream.write(s)

    def newline(self):
        self._stream.write("\n")

    def print(self, *objects, sep: str = ' ', end: str = '\n') -> None:
        self.write(self.get_indent_prefix(self._indent_level))

        first = True

        for object_ in objects:

            if first:
                first = False
            else:
                self.write(sep)

            self.write(str(object_))

        self.write(end)

    def comment(self, message: str, comment_prefix="#") -> None:
        self.print(f"{comment_prefix} {message}")