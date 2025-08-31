from typing import List

from utils.service import Service


class RequirementTree:
    def __init__(self, data: str = None, children: List['RequirementTree'] = None):
        if children is None:
            children = []
        self.data: str = data
        self.children: List['RequirementTree'] = children

    def print(self, indent=0):
        string_indent = '\t' * indent
        print(f'{string_indent}{self.data}')
        indent += 1
        for children in self.children:
            children.print(indent)

    def add_node(self, tree: 'RequirementTree'):
        self.children.append(tree)

    def add_branch(self, branch: List[str]):
        if len(branch) > 0:
            if not self.children_exists(branch[0]):
                node = RequirementTree(branch[0])
                node.add_branch(branch[1:])
            else:
                node = self.get_node(branch[0])
                node.add_branch(branch[1:])
                self.remove_node(node.data)
            self.add_node(node)

    def remove_node(self, data: str):
        self.children = list(filter(lambda item: item.data != data, self.children))

    def get_node(self, data: str):
        for child in self.children:
            if child.data == data:
                return child
        raise Exception(f"Missing node {data}")

    def branch_exists(self, branch: List[str]):
        if len(branch) > 0:
            exists = False
            for child in self.children:
                if child.data == branch[0]:
                    exists = exists or child.branch_exists(branch[1:])
                else:
                    exists = exists or child.branch_exists(branch)
            return exists
        return True

    def children_exists(self, data: str) -> bool:
        for child in self.children:
            if child.data == data:
                return True
        return False

    def get_branches(self):
        return list(map(lambda string_leave: string_leave.split('.'), self.get_string_branches()))

    def get_string_branches(self, path=''):
        branches = []
        for child in self.children:
            new_path = f"{path}.{child.data}" if path else child.data
            if len(child.children) > 0:
                branches.extend(child.get_string_branches(new_path))
            else:
                branches.append(new_path)
        return branches

    def clean_redundant_branches(self):
        sorted_branches = list(sorted(self.get_branches(), key=lambda item: len(item), reverse=True))
        new_tree = RequirementTree(data=self.data)
        for branch in sorted_branches:
            if not new_tree.branch_exists(branch):
                new_tree.add_branch(branch)
        self.children = new_tree.children

    def get_priority_dict(self):
        services = {}
        for child in self.get_branches():
            index = len(child)
            for service in child:
                if service not in services.keys():
                    services[service] = index
                else:
                    if index > services[service]:
                        services[service] = index
                index -= 1
        return services

    def get_priority_dict_by_source(self, source_services: List[Service]):
        source_tree = RequirementTree()
        source_tree.parse_requirements(source_services)
        service_priorities = source_tree.get_priority_dict()
        services = self.get_priority_dict()
        for key in services.keys():
            services[key] = service_priorities[key]
        return services

    def parse_requirements(self, services: List[Service]):
        self.data = 'root'
        for service in services:
            if service.name is not None:
                self.create_requirement_branch(services, service.name)
        self.clean_redundant_branches()

    def create_requirement_branch(self, services: List[Service], requirement: str):
        service_names = list(map(lambda service_object: service_object.name, services))
        if requirement in service_names:
            service = list(filter(lambda item: item.name == requirement, services)).pop()
            requirement_branch = RequirementTree(data=requirement)
            required_services = service.required if service.required is not None else []
            for service_requirement in required_services:
                requirement_branch.create_requirement_branch(services, service_requirement)
            self.add_node(requirement_branch)
