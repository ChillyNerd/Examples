import logging
import threading
import time

import schedule


def run_scheduler(pending_interval=1):
    """
    Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return scheduler_event: threading. Event which can
    be set to cease scheduler event.
    """
    scheduler_event = threading.Event()
    log = logging.getLogger('Scheduler')

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not scheduler_event.is_set():
                schedule.run_pending()
                time.sleep(pending_interval)
            log.debug('Scheduler stopped')

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    log.debug('Scheduler is running')
    return scheduler_event
