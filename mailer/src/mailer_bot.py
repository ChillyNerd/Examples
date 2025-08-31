import ast
import logging
import re
import signal
import time
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import schedule

from db.db_manager import DB
from src.config import Config
from src.mailer import Mailer
from src.scheduler import run_scheduler
import sys


class MailerBot:
    def __init__(self, config: Config):
        self.running = True
        self.log = logging.getLogger("MailerBot")
        self.stop_scheduler = None
        self.config = config
        self.db = DB(config)
        self.format_keys = {
            "bold": {"prefix": '<span style="font-weight: bold;">', "postfix": "</span>"},
            "link": {"prefix": '<a href="{0}">', "postfix": "</a>"},
            "unordered_list": {"prefix": '<ul>', "postfix": "</ul>"},
            "ordered_list": {"prefix": '<ul>', "postfix": "</ul>"}
        }
        punctuation = r'\.\,\(\)\!\?\–\-\—\'\"\«\»\:\;\\\/\@\№\{\}\→\•\+\·\*\%\…\=\'️\#\^\&'
        self.punctuation_pattern = rf'[^\w\s\d{punctuation}]'

    def schedule_scheduling(self):
        schedule.every().day.at("00:00").do(
            self.schedule_for_all_users
        ).tag("system")
        self.log.info("Scheduled every day schedule lookup")

    @staticmethod
    def shift_offsets(format_dict: dict, delta: int, shift_after: int):
        for category in format_dict:
            for item in format_dict[category]:
                if 'offset' in item and item['offset'] > shift_after:
                    item['offset'] += delta
        return format_dict

    @staticmethod
    def format_text(source: str, offset: int, length: int, prefix: str, postfix: str) -> str:
        return f"{source[:offset]}{prefix}{source[offset:(offset + length)]}{postfix}{source[offset + length:]}"

    @staticmethod
    def insert_text(source: str, offset: int, length: int, prefix: str, postfix: str, content: str) -> str:
        return f"{source[:offset]}{prefix}{content}{postfix}{source[offset + length:]}"

    @staticmethod
    def count_delta(current_formats, current_offset):
        delta = 0
        for added_format in current_formats:
            if added_format['from'] < current_offset:
                delta += added_format['length']
        return delta

    @staticmethod
    def get_style_priority(style):
        format_priority = {
            "bold": 3,
            "link": 1,
            "unordered_list": 2,
            "ordered_list": 2
        }
        if style in format_priority.keys():
            return format_priority[style]
        else:
            return 4

    def format_post(self, text, format_, name):
        added_formats = []
        for key in sorted(format_.keys(), key=self.get_style_priority):
            if key == "bold":
                intervals = format_[key]
                for interval in intervals:
                    skip = False
                    for added_format in added_formats:
                        if added_format['from'] == interval['offset']:
                            skip = True
                    if skip:
                        continue
                    start_from = interval['offset'] + self.count_delta(added_formats, interval['offset'])
                    text = self.format_text(text, start_from, interval['length'], self.format_keys[key]['prefix'], self.format_keys[key]['postfix'])
                    added_formats.append({"from": interval['offset'], "length": len(self.format_keys[key]['prefix']) + len(self.format_keys[key]['postfix'])})
            if key == "link":
                link_intervals = format_[key]
                for link_interval in link_intervals:
                    skip = False
                    for added_format in added_formats:
                        if added_format['from'] == link_interval['offset']:
                            skip = True
                    if skip:
                        continue
                    start_from = link_interval['offset'] + self.count_delta(added_formats, link_interval['offset'])
                    formatted_prefix = self.format_keys[key]['prefix'].format(link_interval["url"])
                    text = self.format_text(text, start_from, link_interval['length'], formatted_prefix, self.format_keys[key]['postfix'])
                    added_formats.append({"from": link_interval['offset'], "length": len(formatted_prefix) + len(self.format_keys[key]['postfix'])})
            if key == "unordered_list" or key == "ordered_list":
                list_intervals = format_[key]
                for list_interval in list_intervals:
                    skip = False
                    for added_format in added_formats:
                        if added_format['from'] == list_interval['offset']:
                            skip = True
                    if skip:
                        continue
                    start_from = list_interval['offset'] + self.count_delta(added_formats, list_interval['offset'])
                    items = "".join(list(map(lambda item: f"<li>{item}</li>", text[start_from:start_from + list_interval['length']].split("\n"))))
                    tags_length = len(items) - list_interval['length']
                    text = self.insert_text(text, start_from, list_interval['length'], self.format_keys[key]['prefix'], self.format_keys[key]['postfix'], items)
                    added_formats.append({"from": list_interval['offset'], "length": len(self.format_keys[key]['prefix']) + len(self.format_keys[key]['postfix']) + tags_length})
        return text.format(name=name)

    def send_post(self, text, files, message_number = None, receivers = None):
        if not receivers:
            return
        mailer = Mailer(self.config, receivers)
        post_panel = f" Пост {message_number}" if message_number else ""
        mailer.send_mail(f'Адаптация ООО "ЛУКОЙЛ-Инжиниринг"{post_panel}', text, files)

    def send_message(self, message_id, email, post_num):
        try:
            posts_to_send = self.db.daily_posts_schema.get_posts(message_id)
            message_text = ""
            files = []
            for post_to_send in posts_to_send:
                text = post_to_send.text.decode('utf-8')
                indexes = [match.start() for match in re.finditer(self.punctuation_pattern, text)]
                format_ = ast.literal_eval(post_to_send.format_.decode('utf-8')) if post_to_send.format_ is not None else {}
                for symbol_index in indexes:
                    self.shift_offsets(format_, -1, symbol_index)
                post_text = self.format_post(text, format_, self.db.credentials_schema.get_credentials(email))
                if post_to_send.file is not None:
                    post_text += "\n"
                    post_text += f'<br><img src="cid:{{{post_to_send.file}_cid}}" width=800><br>'
                    files.append(post_to_send.file)
                message_text += post_text
                message_text += "\n"
            self.send_post(text=message_text, files=files, message_number=post_num, receivers=[email])
            self.db.user_progress_schema.save_progress(email, post_num)
            return schedule.CancelJob
        except Exception as e:
            self.log.exception(e)
            self.log.debug(f"Failed to post {message_id} to {email}")
            return schedule.CancelJob

    @staticmethod
    def is_weekend_day():
        return datetime.now().weekday() > 4

    def schedule_for_all_users(self):
        if self.is_weekend_day():
            self.log.info("Today is weekend - no scheduling")
            return
        for user_progress in self.db.user_progress_schema.get_all_user_progress():
            self.schedule_user_posts(user_progress.user, user_progress.progress)

    @staticmethod
    def generate_times_by_points(start, end, n):
        time_format = "%H:%M"
        end = datetime.strptime(end, time_format)

        if end < start:
            end += timedelta(days=1)

        total_duration = (end - start).total_seconds()
        interval = total_duration / (n + 1)

        times = []
        for i in range(1, n + 1):
            point = start + timedelta(seconds=interval * i)
            times.append(point.time().strftime(time_format))
        return times

    def schedule_user_posts(self, email, progress):
        jobs_to_cancel = self.get_jobs_by_tags([email])
        for job in jobs_to_cancel:
            schedule.cancel_job(job)
        remaining_posts = self.db.daily_posts_schema.get_posts_after(progress)
        if len(remaining_posts) == 0:
            return
        todays_posts = pd.DataFrame(list(map(lambda post: post.to_dict(), remaining_posts)))
        todays_posts = todays_posts[todays_posts['day'] == todays_posts.iloc[0]['day']]
        end_time = "17:00"
        if datetime.strptime(datetime.now().time().strftime("%H:%M"), '%H:%M') > datetime.strptime("17:00", '%H:%M'):
            end_time = "23:59"
        if datetime.strptime(datetime.now().time().strftime("%H:%M"), '%H:%M') > datetime.strptime("10:00", '%H:%M'):
            start_date = datetime.strptime(datetime.now().time().strftime("%H:%M"), '%H:%M')
        else:
            start_date = datetime.strptime("10:00", '%H:%M')
        times = self.generate_times_by_points(start_date, end_time, len(todays_posts["message_id"].unique()))
        time_index = 0
        scheduled_messages = []
        for index, row in todays_posts.iterrows():
            if row["message_id"] in scheduled_messages:
                continue
            at_time = times[time_index]
            schedule.every().day.at(at_time).do(
                self.send_message, email=email, message_id=row["message_id"], post_num=row["post_num"]
            ).tag(email).tag(row["post_num"])
            self.log.info(f'Scheduled send mail of {row["message_id"]} for user {email} on {at_time}')
            time_index += 1
            scheduled_messages.append(row["message_id"])

    @staticmethod
    def get_jobs_by_tags(tags: List[str]):
        jobs = []
        for job in schedule.get_jobs():
            append_job = True
            for tag in tags:
                if tag not in job.tags:
                    append_job = False
            if append_job:
                jobs.append(job)
        return jobs

    def find_new_users(self):
        new_users = self.db.user_progress_schema.get_all_new_users()
        for new_user in new_users:
            self.schedule_user_posts(new_user.user, 0)
            self.manual_post(new_user.user)

    def manual_post(self, user: str):
        remaining_posts = self.db.daily_posts_schema.get_posts_after(self.db.user_progress_schema.get_progress(user))
        if len(remaining_posts) == 0:
            return
        current_post = remaining_posts[0]
        jobs_to_cancel = self.get_jobs_by_tags([user, current_post.post_num])
        self.send_message(email=user, message_id=current_post.message_id, post_num=current_post.post_num)
        for job in jobs_to_cancel:
            schedule.cancel_job(job)

    def idle(self):
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGABRT):
            signal.signal(sig, self._signal_handler)
        self.stop_scheduler = run_scheduler()
        self.schedule_scheduling()
        self.schedule_for_all_users()
        while self.running:
            self.find_new_users()
            time.sleep(1)

    def _signal_handler(self, signum, frame):
        if self.running:
            self.log.debug("Bot stopped")
            self.running = False
            if self.stop_scheduler:
                self.stop_scheduler.set()
        else:
            sys.exit(1)