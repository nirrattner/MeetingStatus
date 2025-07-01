from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
  QAction,
  QMenu
)

from meeting_status_client.library.event_loop import StateType
from meeting_status_core.model.status import Status, StatusType

STATUS_INDEX_START = 3
STATUS_INDEX_END = -2


class Menu(QMenu):

  def __init__(self, *args, **kwargs):
    super(QMenu, self).__init__(*args, **kwargs)

    self.error_action = QAction('Error!')
    self.addAction(self.error_action)
    self.error_action.setEnabled(False)
    self.error_action.setVisible(False)

    self.error_separator = self.addSeparator()
    self.error_separator.setVisible(False)

    self.refreshing_action = QAction('Refreshing...')
    self.refreshing_action.setFont(QFont(None, italic=True))
    self.addAction(self.refreshing_action)
    self.refreshing_action.setEnabled(False)
    self.refreshing_action.setVisible(False)

    self.status_separator = self.addSeparator()
    self.status_separator.setVisible(False)

    self.quit_action = QAction('Quit')
    self.addAction(self.quit_action)

    self.state = StateType.AWAITING_RESPONSE
    self.statuses = []
    self.status_actions = []
    self.update_state(self.state, self.statuses)

  def update_state(
      self,
      state: StateType,
      statuses: list[Status] = None,
      exception=None):
    if exception:
      self.error_action.setVisible(True)
      self.error_separator.setVisible(True)

    if state == StateType.AWAITING_RESPONSE:
      self.refreshing_action.setVisible(True)
      self.status_separator.setVisible(True)
    else:
      self.refreshing_action.setVisible(False)
      self.status_separator.setVisible(False)

    if statuses:
      self.statuses = statuses

    for action in self.actions()[STATUS_INDEX_START:STATUS_INDEX_END]:
      self.removeAction(action)

    self.status_actions = []
    for status in self.statuses:
      status_action = QAction(format_status(status))
      self.insertAction(self.status_separator, status_action)
      self.status_actions.append(status_action)
      status_action.setEnabled(False)
    if len(self.statuses):
      self.status_separator.setVisible(True)

def format_status(status):
  status_type = StatusType(status.status_type).name
  formatted_status_type = status_type[0] + status_type[1:].lower()
  return f'{status.user} - {formatted_status_type}'
