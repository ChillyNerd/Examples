import inspect
from typing import Optional, List


class Service:
    def __init__(self, parameters: dict):
        self.name: Optional[str] = None
        self.required: Optional[List[str]] = None
        self.priority: Optional[int] = None
        for name, value in parameters.items():
            self.__setattr__(name, value)

    def get_properties(self):
        total_attributes = dir(self)
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        methods = [method[0] for method in methods]
        properties = [attr for attr in total_attributes if attr not in methods]
        return list(filter(lambda attr: not attr.__contains__('__'), properties))

    def copy_from(self, service: 'Service') -> 'Service':
        new_service = Service(self.to_dict())
        for attr in new_service.get_properties():
            value = service.__getattribute__(attr)
            if value is not None:
                new_service.__setattr__(attr, value)
        return new_service

    def to_dict(self) -> dict:
        result_dict = {}
        for attr in self.get_properties():
            value = self.__getattribute__(attr)
            if value is not None:
                result_dict[attr] = value
        return result_dict