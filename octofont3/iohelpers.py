from io import TextIOBase
from typing import TypeVar


TextIOBaseSubclass = TypeVar("TextIOBaseSubclass", bound=TextIOBase)


class OutputHelper:
    """
    Encapsulate common operations on source output streams

    Subclasses should be made for specific languages.
    """
    def __init__(self, stream: TextIOBaseSubclass):
        super().__init__()
        self._stream = stream
        self._indent_level = 0

    def write(self, s: str) -> None:
        self._stream.write(s)

    def newline(self):
        self._stream.write("\n")

    def print(self, *objects, sep: str = ' ', end: str = '\n') -> None:
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


def padded_hex(value: int, num_digits: int = 2) -> str:
    return f"0x{hex(value)[2:].zfill(num_digits)}"
