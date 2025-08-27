from typing import List
from pydantic import BaseModel


class LogMessages:
    pre_action_log: str
    success_action_log: str
    error_action_log: str


class ServiceData(BaseModel):
    configurations: List[str]
    required: List[str]
    groups: List[str]
    profiles: List[str]


class RequirementData(BaseModel):
    required: List[str]


class GroupData(BaseModel):
    groups: List[str]


class ConfigurationData(BaseModel):
    configurations: List[str]


class VariableName(BaseModel):
    variables: List[str]


class VariablesData(BaseModel):
    variables: List[str]
    value: str


class ProfilesData(BaseModel):
    profiles: List[str]


class ScheduleData(BaseModel):
    time: List[str]


class MailReceivers(BaseModel):
    receivers: List[str]


class MailTime(BaseModel):
    mail_time: List[str]
