from enum import IntEnum

from meeting_status_core.model.base_model import BaseModel


class StatusType(IntEnum):
  FREE = 0
  BUSY = 1


class Status(BaseModel):
  def __init__(
      self,
      status_type: StatusType = None,
      user: str = None,
      timestamp: int = None):
    self.status_type = status_type
    self.user = user
    self.timestamp = timestamp


class StatusRequest(BaseModel):
  TYPES = {
    'status': Status
  }

  def __init__(self, status: Status = None):
    self.status = status


class StatusResponse(BaseModel):
  TYPES = {
    'statuses': list[Status]
  }

  def __init__(self, statuses: list[Status] = None):
    self.statuses = statuses
