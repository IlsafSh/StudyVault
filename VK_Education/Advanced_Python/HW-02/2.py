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