from getpass import getuser
from time import time

from PyQt5.QtCore import (
  QTimer,
  pyqtSignal,
  pyqtSlot,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
  QApplication,
  QSystemTrayIcon,
)

from meeting_status_client.api.meeting_status_client import MeetingStatusClient
from meeting_status_client.components.menu import Menu
from meeting_status_client.library.microphones import is_any_microphone_active
from meeting_status_core.model.status import Status, StatusType

TIMER_PERIOD_MS = 2000
REQUEST_PERIOD_S = 10


class Application(QApplication):
  request_signal = pyqtSignal(object)

  def __init__(self, *args, **kwargs):
    super(Application, self).__init__(*args, **kwargs)

    self.last_response_timestamp = 0
    self.last_status = None
    self.user = getuser()

    self.setQuitOnLastWindowClosed(False)
    self.menu = Menu()
    self.menu.quit_action.triggered.connect(self.quit)

    self.tray = QSystemTrayIcon()
    self.tray.setIcon(QIcon('resources/user.svg'))
    self.tray.setVisible(True)
    self.tray.setContextMenu(self.menu)

    self.meeting_status_client = MeetingStatusClient(
      '192.168.1.114',
      80,
      self.status_response_callback
    )

    self.menu.aboutToShow.connect(self.menu_show_callback)
    self.request_signal.connect(self.meeting_status_client.submit_status)

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.timer_callback)
    self.timer.start(TIMER_PERIOD_MS)

    self.status_request()

  @pyqtSlot()
  def menu_show_callback(self):
    self.status_request()

  @pyqtSlot(object, object)
  def status_response_callback(
      self,
      statuses: list[Status] = None,
      exception: Exception = None):
    self.menu.update_state(statuses, exception)
    self.last_response_timestamp = int(time())

  @pyqtSlot()
  def timer_callback(self):
    status = get_status_type()
    timestamp = int(time())
    if timestamp - self.last_response_timestamp >= REQUEST_PERIOD_S \
        or status != self.last_status:
      self.status_request(status, timestamp)

  def status_request(
      self,
      status: StatusType = None,
      timestamp: int = None):
    print('status_request')
    status = status or get_status_type()
    timestamp = timestamp or int(time())
    self.last_status = status
    self.request_signal.emit(
      Status(
        status,
        self.user,
        timestamp))


def get_status_type() -> StatusType:
  return StatusType.BUSY if is_any_microphone_active() else StatusType.FREE


if __name__ == '__main__':
  application = Application([])
  application.exec_()
