from typing import Type, Any, Optional

class TypedProperty:
    def __init__(self, expected_type: Type[Any]) -> None:
        self.expected_type = expected_type
        self.name: str = ""

    def __set_name__(self, owner: Type[Any], name: str) -> None:
        self.name = name

    def __get__(self, instance: Optional[object], owner: Type[Any]) -> Any:
        if instance is None:
            return self

        if self.name not in instance.__dict__:
            raise AttributeError(f"'{owner.__name__}' object has no attribute '{self.name}'")
            
        return instance.__dict__[self.name]

    def __set__(self, instance: object, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"Expected value of type {self.expected_type.__name__}, "
                f"but got {type(value).__name__}"
            )
        
        instance.__dict__[self.name] = value