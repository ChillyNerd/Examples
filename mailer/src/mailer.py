import re
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from smtplib import SMTP
from typing import List
import logging

from src.config import Config
from src.static.static_files import Files, StaticFile

class Mailer:
    __signature_pattern = """
    <table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0 style='border-collapse:collapse'>
        <tr>
            <td>
                <img src="cid:{logo_cid}" style="width: 100px; height: 100px;">
            </td>
            <td style='width:10px'></td>
            <td>
                <p>С уважением,<br>
                <span style="font-weight: bold;">Ваш бот-помощник «Подручный»</span><br>
                ООО «ЛУКОЙЛ-Инжиниринг»<br>
                <span style="font-weight: bold;">E-mail:</span> adaptation@lukoil.com</p>
            </td>
        </tr>
    </table>
    """

    def __init__(self, config: Config, receivers: List[str]):
        self.config: Config = config
        self.receivers: List[str] = receivers
        self.log = logging.getLogger("Mailer")

    def send_connect(self) -> SMTP:
        connect = smtplib.SMTP(self.config.mailer_host, self.config.mailer_port)
        connect.ehlo()
        connect.starttls()
        connect.login(self.config.mailer_user, self.config.mailer_password)
        return connect

    def send_mail(self, subject: str, mail: str, files: List[str]):
        self.log.debug(f'Connecting to {self.config.mailer_host}')
        connect = self.send_connect()
        self.log.debug(f'Connected to {self.config.mailer_host}')
        try:
            connect.send_message(self.make_message(subject, mail, files), self.config.mailer_from, self.receivers)
            self.log.debug(f'Sent message to {self.receivers}')
        finally:
            connect.quit()
            self.log.debug(f'Disconnected from {self.config.mailer_host}')

    def make_message(self, subject: str,  mail: str, files: List[str]):
        msg = EmailMessage()
        msg.set_charset("utf-8")
        msg["Subject"] = subject
        msg["From"] = self.config.mailer_from
        msg["To"] = ','.join(self.receivers)
        clean_text = "\n".join([line for line in mail.splitlines() if line.strip()])
        replaced_list_ends = re.sub("</ul>\s*\n", "</ul>", clean_text)
        replaced_breaks = replaced_list_ends.replace('\n', '<br>')
        files_cids = {}
        if len(files) > 0:
            for file in files:
                files_cids[file] = make_msgid()
                replaced_breaks = replaced_breaks.format(**{f"{file}_cid": files_cids[file][1:-1]})
        msg.set_content(replaced_breaks)
        logo_cid = make_msgid()
        msg.add_alternative(f'{replaced_breaks}<br><br>{self.__signature_pattern.format(logo_cid=logo_cid[1:-1])}', subtype="html")
        with open(Files.signature.get_file(), "rb") as img:
            msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=logo_cid)
        for file in files:
            with open(StaticFile(file).get_file_from_static(), "rb") as img:
                msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=files_cids[file])
        return msg
