from typing import List

from meeting_status_core.model.status import Status


class StatusManager:
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(StatusManager, cls).__new__(cls)
      cls.instance.initialize()
    return cls.instance

  def initialize(self) -> None:
    self.statuses = {}

  def get_statuses(self) -> List[Status]:
    statuses = list(self.statuses.values())
    statuses.sort(key=lambda status: status.user)
    return statuses

  def update_status(self, status: Status):
    self.statuses[status.user] = status

  def delete_status(self, user: str):
    del self.statuses[user]
