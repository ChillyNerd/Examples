import traceback

import pandas as pd
from fastapi.responses import JSONResponse

from src.core.ansible_tasks import AnsibleTaskRunner
from src.core.application_server.abstract_app import AbstractApp
from src.core.application_server.defaults import ok, error
from src.core.host import Host, Configuration
from src.core.implementations.logger import log
from src.exceptions.configuration_exceptions import BaseConfigurationException
from src.exceptions.deploy_exceptions import BaseDeployException


def init(source: AbstractApp):
    @source.app.get("/track_action", tags=['Utils'])
    def track_action(action_id: str, last_message_id: int):
        if action_id in source.schedule_tasks.actions.keys():
            action = source.schedule_tasks.actions[action_id]
            df = pd.DataFrame(action.get_log(), columns=['id', 'message', 'time', 'thread'])
            df = df.sort_values(by=['time'])
            df = df[df['id'] > last_message_id]
            return {"status": df.to_dict('records'), 'active': action.active}
        else:
            return {"status": "Action not found", 'active': False}

    @source.app.get('/health', tags=['Utils'])
    def health():
        return JSONResponse({'msg': "Not dead"}, status_code=ok)

    @source.app.post('/status', tags=['Utils'])
    def status(host_name: str, service_name: str):
        try:
            log.debug(f'Getting status of {service_name} on {host_name}')
            out = AnsibleTaskRunner(Configuration(host_name), source.app_config).status(service_name)
            log.debug(f'Got status of {service_name} on {host_name}')
            return JSONResponse({'msg': f'Got status of {service_name} on {host_name}', 'out': out},
                                status_code=ok)
        except BaseConfigurationException as ex:
            log.error(f'Error getting status of {service_name} on {host_name}')
            log.error(ex.message)
            return JSONResponse({'msg': ex.message}, status_code=error)
        except BaseDeployException as ex:
            log.error(f'Error getting status of {service_name} on {host_name}')
            log.error(ex.message)
            return JSONResponse({'msg': ex.message}, status_code=error)
        except Exception as e:
            log.error(f'Error getting status of {service_name} on {host_name}')
            log.exception(e)
            return JSONResponse({'msg': traceback.format_exc()}, status_code=error)

    @source.app.post('/check_service_running', tags=['Utils'])
    def check_service_running(host_name: str, service_name: str):
        try:
            log.debug(f'Checking service {service_name} for running')
            active = Host(source.app_config, host_name).check_service_status(service_name)
            log.debug(f'Service {service_name} is {active}')
            return JSONResponse({'msg': f'Service {service_name} is {active}'}, status_code=ok)
        except BaseDeployException as e:
            log.error(f'Error during checking service {service_name} for running')
            log.exception(e)
            return JSONResponse({'msg': e.message}, status_code=error)
        except Exception as e:
            log.error(f'Error during checking service {service_name} for running')
            log.exception(e)
            return JSONResponse({'msg': traceback.format_exc()}, status_code=error)
