class StackIsEmpty(Exception):
    pass

class Stack:
    def __init__(self):
        self._elements = []

    def push(self, value):
        self._elements.append(value)

    def pop(self):
        if not self._elements:
            raise StackIsEmpty("Stack is empty")
        return self._elements.pop()

    def __len__(self):
        return len(self._elements)

    def __str__(self):
        elements_str = ", ".join(str(e) for e in self._elements)
        return f"Stack({elements_str})"

    def __repr__(self):
        return f"Stack({repr(self._elements)})"

    def __iter__(self):
        return iter(self._elements)

    def __contains__(self, value):
        return value in self._elements

    def __getitem__(self, index):
        return self._elements[index]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._elements.clear()

    def __eq__(self, other):
        if not isinstance(other, Stack):
            return False
        return self._elements == other._elements