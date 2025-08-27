import traceback

from fastapi import status as http_status, BackgroundTasks
from fastapi.responses import JSONResponse

from src.core.application_server.schemas import LogMessages
from src.core.config import AppConfig
from src.core.host import Host, Configuration
from src.core.implementations.action import Action
from src.core.implementations.logger import log
from src.exceptions.configuration_exceptions import BaseConfigurationException
from src.exceptions.deploy_exceptions import BaseDeployException

ok = http_status.HTTP_200_OK
error = http_status.HTTP_500_INTERNAL_SERVER_ERROR


def configuration_request_pattern(host_name: str, log_messages: LogMessages, method_name: str, *args, **kwargs):
    try:
        config = Configuration(host_name)
    except BaseConfigurationException as ex:
        log.error(log_messages.error_action_log)
        log.error(ex.message)
        return JSONResponse({'msg': ex.message}, status_code=error)
    try:
        log.debug(log_messages.pre_action_log)
        config.__getattribute__(method_name)(*args, **kwargs)
        log.debug(log_messages.success_action_log)
        return JSONResponse({'msg': log_messages.success_action_log}, status_code=ok)
    except (BaseConfigurationException, BaseDeployException) as ex:
        config.undo()
        log.error(log_messages.error_action_log)
        log.error(ex.message)
        return JSONResponse({'msg': ex.message}, status_code=error)
    except Exception as e:
        config.undo()
        log.error(log_messages.error_action_log)
        log.exception(e)
        return JSONResponse({'msg': traceback.format_exc()}, status_code=error)


def configuration_set_pattern(host_name: str, log_messages: LogMessages, field_name: str, value):
    try:
        config = Configuration(host_name)
    except BaseConfigurationException as ex:
        log.error(log_messages.error_action_log)
        log.error(ex.message)
        return JSONResponse({'msg': ex.message}, status_code=error)
    try:
        log.debug(log_messages.pre_action_log)
        config.__setattr__(field_name, value)
        log.debug(log_messages.success_action_log)
        return JSONResponse({'msg': log_messages.success_action_log}, status_code=ok)
    except (BaseConfigurationException, BaseDeployException) as ex:
        config.undo()
        log.error(log_messages.error_action_log)
        log.error(ex.message)
        return JSONResponse({'msg': ex.message}, status_code=error)
    except Exception as e:
        config.undo()
        log.error(log_messages.error_action_log)
        log.exception(e)
        return JSONResponse({'msg': traceback.format_exc()}, status_code=error)


def request_pattern(log_messages: LogMessages, method, *args, **kwargs):
    try:
        log.debug(log_messages.pre_action_log)
        method(*args, **kwargs)
        log.debug(log_messages.success_action_log)
        return JSONResponse({'msg': log_messages.success_action_log}, status_code=ok)
    except (BaseConfigurationException, BaseDeployException) as ex:
        log.error(log_messages.error_action_log)
        log.error(ex.message)
        return JSONResponse({'msg': ex.message}, status_code=error)
    except Exception as e:
        log.error(log_messages.error_action_log)
        log.exception(e)
        return JSONResponse({'msg': traceback.format_exc()}, status_code=error)


def create_async_host_action(
        background_tasks: BackgroundTasks,
        app_config: AppConfig,
        host_name: str,
        action: Action,
        error_message: str,
        method_name: str,
        *args,
        **kwargs
):
    try:
        host = Host(app_config, host_name, action)
    except BaseConfigurationException as ex:
        log.error(error_message)
        log.error(ex.message)
        return JSONResponse({'msg': ex.message}, status_code=error)
    background_tasks.add_task(host.run_method, error_message=error_message, method_name=method_name, *args, **kwargs)
    return JSONResponse({'action_id': action.action_id}, status_code=ok)
