from time import time

from PyQt5.QtWidgets import (
  QAction,
  QMenu
)

from meeting_status_core.model.status import Status, StatusType

STATUS_INDEX_START = 2
STATUS_INDEX_END = -2

TIME_DAY = 24 * 60 * 60
TIME_HOUR = 60 * 60
TIME_MINUTE = 60


class Menu(QMenu):

  def __init__(self, *args, **kwargs):
    super(QMenu, self).__init__(*args, **kwargs)

    self.error_action = QAction('Error!')
    self.addAction(self.error_action)
    self.error_action.setEnabled(False)
    self.error_action.setVisible(False)

    self.error_separator = self.addSeparator()
    self.error_separator.setVisible(False)

    self.status_separator = self.addSeparator()
    self.status_separator.setVisible(False)

    self.quit_action = QAction('Quit')
    self.addAction(self.quit_action)

    self.statuses = []
    self.status_actions = []
    self.update_state(self.statuses)

  def update_state(
      self,
      statuses: list[Status] = None,
      exception=None):
    if exception:
      print(exception)
      self.error_action.setVisible(True)
      self.error_separator.setVisible(True)

    if statuses:
      self.statuses = statuses

    new_status_actions = []

    status_index = 0
    for status_action in self.actions()[STATUS_INDEX_START:STATUS_INDEX_END]:
      if status_index >= len(self.statuses):
        self.removeAction(status_action)
        continue
      status_action.setText(format_status(self.statuses[status_index]))
      new_status_actions.append(status_action)
      status_index += 1

    for status in self.statuses[status_index:]:
      status_action = QAction(format_status(status))
      self.insertAction(self.status_separator, status_action)
      self.status_actions.append(status_action)
      status_action.setEnabled(False)
      new_status_actions.append(status_action)

    self.status_actions = new_status_actions

    self.status_separator.setVisible(len(self.statuses) > 0)


def format_status(status: Status) -> str:
  status_type = StatusType(status.status_type).name
  formatted_status_type = status_type[0] + status_type[1:].lower()
  return f'{status.user} - {formatted_status_type} {format_timestamp(status.timestamp)}'


def format_timestamp(timestamp: int) -> str:
  elapsed_time = time() - timestamp
  if elapsed_time > TIME_DAY:
    return '(>1 day ago)'
  if elapsed_time > TIME_HOUR:
    return '(>1 hour ago)'
  if elapsed_time > TIME_MINUTE:
    return '(>1 minute ago)'
  return ''
