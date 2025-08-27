from fastapi import BackgroundTasks

from src.core.application_server.abstract_app import AbstractApp
from src.core.application_server.defaults import create_async_host_action
from src.core.implementations.utils import get_services_string


def init(source: AbstractApp):
    @source.app.post('/start', tags=['Start'])
    def start(
            background_tasks: BackgroundTasks,
            host_name: str,
            service_name: str = None,
            group_name: str = None,
            force: bool = False
    ):
        """
        Starts services on host.

        :param host_name: Name of host
        :param background_tasks: Object of BackgroundTasks
        :param service_name: Name of service
        :param group_name: Name of services group
        :param force: Not to check the requirements of service to start
        """
        action = source.schedule_tasks.register_action(host_name)
        error_message = f'Failed to start {get_services_string(service_name, group_name)} on {host_name}'
        return create_async_host_action(
            background_tasks=background_tasks, app_config=source.app_config, error_message=error_message,
            host_name=host_name, action=action, method_name='start', service_name=service_name, group_name=group_name,
            force=force
        )
