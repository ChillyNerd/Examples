import json
import os
import re
import logging


def get_project_files(project_path):
    ignore_list = [".git", ".idea", "logs"]
    file_list = []
    for root, dirs, files in os.walk(project_path):
        skip = False
        for ignored_file in ignore_list:
            if ignored_file in root.split("\\"):
                skip = True
                break
        if skip:
            continue
        for file in files:
            file_list.append({"name": file, "path": os.path.join(root, file)})
    return file_list

def get_all_rest_endpoints(file_content, class_name):
    controller_endpoints = []
    if "@RestController" not in file_content:
        return controller_endpoints
    rest_endpoints_pattern = re.compile(
        r'@(\w+)Mapping\s*'
        r'(?:\((?:\s*value\s*=\s*)?"([^"]+)"[^)]*\))?\s*'
        r'(?:public\s+)?([\w\[\]<>,. ]+)\s+'
        r'(\w+)\s*'
        r'\((.*?)\)\s*'
        r'(?:\s*throws.*?)?'
        r'\{[^}]*}',
        re.MULTILINE
    )
    request_mapping_pattern = re.compile('@RequestMapping\s*\(\s*"(?P<routes_prefix>[^"]+)"\s*\)')
    rest_endpoints = rest_endpoints_pattern.findall(file_content)
    routes_prefix_match = request_mapping_pattern.search(file_content)
    routes_prefix = None
    if routes_prefix_match:
        routes_prefix = routes_prefix_match.groupdict()["routes_prefix"]
    logger.info(f"RestController {class_name}")
    for rest_endpoint in rest_endpoints:
        method = rest_endpoint[0]
        route = (routes_prefix if routes_prefix else "") + rest_endpoint[1]
        return_type = rest_endpoint[2]
        method_name = rest_endpoint[3]
        parameters = rest_endpoint[4]
        logger.info(f"Endpoint {method} {route} {return_type} {method_name} {parameters}")
        controller_endpoints.append({"method": method, "route": route, "return_type": return_type, "method_name": method_name, "parameters": parameters})
    return rest_controllers

def get_all_feign_endpoints(file_content):
    client_endpoints = []
    if "@FeignClient" not in file_content:
        return client_endpoints
    feign_client_pattern = re.compile('@FeignClient\((?:value\s*=\s*)?"(?P<feign_client>[^"]+)"[^)]*\)')
    feign_client = feign_client_pattern.search(file_content)
    if not feign_client:
        return client_endpoints
    client_name = feign_client.groupdict()["feign_client"]
    logger.info(f"FeignСlient {client_name}")
    feign_endpoints_pattern = re.compile(
        r'@(\w+)Mapping\s*'
        r'(?:\(.*?(?:\s*value\s*=\s*)?"([^"]+)"[^)]*\))?\s*'
        r'(?:public\s+)?([\w\[\]<>,. ]+)\s+'
        r'(\w+)\s*'
        r'\((.*?)\)\s*'
        r'(?:\s*throws.*?)?;',
        re.MULTILINE
    )
    feign_endpoints = feign_endpoints_pattern.findall(file_content)
    for feign_endpoint in feign_endpoints:
        method = feign_endpoint[0]
        route = feign_endpoint[1]
        return_type = feign_endpoint[2]
        method_name = feign_endpoint[3]
        parameters = feign_endpoint[4]
        logger.info(f"Feign Endpoint {method} {route} {return_type} {method_name} {parameters}")
        client_endpoints.append({"method": method, "route": route, "return_type": return_type, "method_name": method_name, "parameters": parameters})
    return client_endpoints

def get_project_endpoints(project_path: str):
    file_list = get_project_files(project_path)
    classes = {}
    encodings = ["utf-8", "windows-1251", "cp866", "IBM855", "koi8-r", "koi8-u"]
    class_java_pattern = re.compile("(?P<class_name>.*?)\.(java|class)")
    trail_spaces = re.compile("\s+")
    rest_endpoints = []
    feign_clients = {}
    for file in file_list:
        java_class = class_java_pattern.match(file["name"])
        if not java_class:
            continue
        groups = java_class.groupdict()
        classes[groups["class_name"]] = file["path"]
        logger.debug(f"Inspecting {file['path']}")
        file_content = None
        for encoding in encodings:
            try:
                with open(file["path"], "r", encoding=encoding) as f:
                    file_content = f.read()
                    break
            except UnicodeDecodeError:
                logger.debug(f"Could not be read with {encoding}")
        if not file_content:
            logger.debug(f"Failed to read {file['path']}")
            continue
        file_content = trail_spaces.sub(" ", file_content)
        rest_endpoints.extend(get_all_rest_endpoints(file_content, groups["class_name"]))
        feign_endpoints = get_all_feign_endpoints(file_content)
        if len(feign_endpoints) > 0:
            feign_clients[groups["class_name"]] = feign_endpoints
    return classes, rest_endpoints, feign_clients

logging_level = logging.INFO
logger = logging.getLogger("Parser")
logging.basicConfig(format='%(asctime)s - %(name)12s %(levelname)-7s %(threadName)12s: %(message)s', handlers=[logging.StreamHandler()], level=logging_level)
if os.path.exists("project_names.json"):
    with open("project_names.json", "r", encoding="utf-8") as f:
        project_names = json.load(f)
else:
    project_names = {}

projects_path = "D:\\Users\\abramovao\\projects"
projects = os.listdir(projects_path)
project_inputs = {}
project_outputs = {}
for project_name in projects:
    if project_name not in project_names.keys():
        continue
    project_path = os.path.join(projects_path, project_name)
    if not os.path.isdir(project_path):
        continue
    logger.info(f"Project {project_name}")
    classes, rest_controllers, feign_clients = get_project_endpoints(project_path)
    project_inputs[project_names[project_name]] = rest_controllers
    project_outputs[project_names[project_name]] = feign_clients

connections = {}
for project_name in project_outputs.keys():
    connections[project_name] = list(project_outputs[project_name].keys())
    for feign_client in project_outputs[project_name].keys():
        if len(project_outputs[project_name][feign_client]) == 0:
            logger.info(f"IN PROJECT {project_name} {feign_client} HAS NO ENDPOINTS")
for project_name in connections.keys():
    if len(connections[project_name]) == 0:
        logger.info(f"~~~~~~Project {project_name} has no connections~~~~~~~~")
    for connection in connections[project_name]:
        logger.info(f"Project {project_name} connected to {connection}")
