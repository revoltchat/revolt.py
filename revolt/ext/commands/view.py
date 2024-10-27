from typing import Iterator
from typing_extensions import Self

from .errors import NoClosingQuote


class StringView:
    def __init__(self, string: str):
        self.value: Iterator[str] = iter(string)
        self.temp: str = ""
        self.should_undo: bool = False

    def undo(self) -> None:
        self.should_undo = True

    def next_char(self) -> str:
        return next(self.value)

    def get_rest(self) -> str:
        if self.should_undo:
            return f"{self.temp} {''.join(self.value)}".rstrip()
            # prevent a new space appearing at end if the buffer is depleted

        return "".join(self.value)

    def get_next_word(self) -> str:
        if self.should_undo:
            self.should_undo = False
            return self.temp

        char = self.next_char()
        temp: list[str] = []

        while char == " ":
            char = self.next_char()

        if char in ["\"", "'"]:
            quote = char
            try:
                while (char := self.next_char()) != quote:
                    temp.append(char)
            except StopIteration:
                raise NoClosingQuote

        else:
            temp.append(char)
            try:
                while (char := self.next_char()) not in " \n":
                    temp.append(char)
            except StopIteration:
                pass

        output = "".join(temp)
        self.temp = output

        return output

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> str:
        return self.get_next_word()