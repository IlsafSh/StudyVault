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