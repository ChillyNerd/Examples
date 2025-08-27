from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse

from src.core.application_server.abstract_app import AbstractApp
from src.core.application_server.defaults import ok


def init(source: AbstractApp):
    @source.app.post('/stop', tags=['Stop'])
    def stop(host_name: str, background_tasks: BackgroundTasks, service_name: str = None, group_name: str = None,
             reload: bool = False, time: str = None, force: bool = False):
        """
        Stops services on host.

        :param host_name: Name of host
        :param background_tasks: Object of BackgroundTasks
        :param service_name: Name of service
        :param group_name: Name of services group
        :param reload: If True starts service after stop
        :param time: Shutdown time
        :param force: Force service to shut down immediately
        """
        action = source.schedule_tasks.register_action(host_name)
        background_tasks.add_task(
            source.schedule_tasks.add_stop_service_to_schedule, action=action, host_name=host_name,
            service_name=service_name, group_name=group_name, reload=reload, time=time, force=force
        )
        return JSONResponse({'action_id': action.action_id}, status_code=ok)
