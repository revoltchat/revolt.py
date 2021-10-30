from .errors import NoClosingQuote


class StringView:
    def __init__(self, string: str):
        self.value = iter(string)

    def next_char(self) -> str:
        return next(self.value)

    def get_rest(self) -> str:
        return "".join(self.value)

    def get_next_word(self) -> str:
        char = self.next_char()
        temp = []

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
                while (char := self.next_char()) != " ":
                    temp.append(char)
            except StopIteration:
                pass

        output = "".join(temp)

        return output
