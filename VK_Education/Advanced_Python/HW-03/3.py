from typing import Any, Dict, Tuple

class RegistryMeta(type):
    registry: Dict[str, type] = {}

    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> Any:
        cls = super().__new__(mcs, name, bases, namespace)

        if name in mcs.registry:
            raise ValueError(f"Класс с именем '{name}' уже зарегистрирован в реестре.")

        mcs.registry[name] = cls
        
        return cls