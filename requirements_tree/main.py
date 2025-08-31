from utils.requirement_tree import RequirementTree
from utils.service import Service

services_json = [{'name': 'discovery', 'required': ['config']}, {'name': 'config', 'required': []}, {'name': 'auth', 'required': ['discovery']}, {'name': 'api-gateway', 'required': ['discovery']}, {"name": "menu", "required": ["api-gateway", "auth"]}]
services = list(map(lambda parameters: Service(parameters), services_json))
tree = RequirementTree()
tree.parse_requirements(services)
tree.print(1)
priority_dict = tree.get_priority_dict()
services_with_priority = list(map(
    lambda service: Service({'priority': priority_dict[service.name]}).copy_from(service), services
))
sorted_services = sorted(services_with_priority, key=lambda service: service.priority)
print(list(map(
    lambda service: (service.name, service.priority), sorted_services
)))