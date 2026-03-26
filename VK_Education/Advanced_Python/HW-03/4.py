from typing import Any, Dict, Optional, Tuple, Type

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

class ValidatedProperty(TypedProperty):
    def __init__(
        self, 
        expected_type: Type[Any], 
        min_value: Optional[Any] = None, 
        max_value: Optional[Any] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> None:
        super().__init__(expected_type)
        self.min_value = min_value
        self.max_value = max_value
        self.min_length = min_length
        self.max_length = max_length

    def __set__(self, instance: object, value: Any) -> None:
        super().__set__(instance, value)

        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Значение {value} меньше допустимого минимума {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Значение {value} больше допустимого максимума {self.max_value}")

        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError(f"Длина {len(value)} меньше допустимого минимума {self.min_length}")
        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError(f"Длина {len(value)} больше допустимого максимума {self.max_length}")

class RegistryMeta(type):
    registry: Dict[str, type] = {}

    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> Any:
        cls = super().__new__(mcs, name, bases, namespace)

        if name in mcs.registry:
            raise ValueError(f"Класс с именем '{name}' уже зарегистрирован в реестре.")

        mcs.registry[name] = cls
        
        return cls

class ModelMeta(RegistryMeta):
    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> Any:
        fields = {}
        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, TypedProperty):
                fields[attr_name] = attr_value
                
        namespace['_fields'] = fields
        
        cls = super().__new__(mcs, name, bases, namespace)
        
        return cls


class Model(metaclass=ModelMeta):
    pass