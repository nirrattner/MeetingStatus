from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
  QApplication,
  QSystemTrayIcon,
)
from getpass import getuser

from meeting_status_client.api.meeting_status_client import MeetingStatusClient
from meeting_status_client.components.menu import Menu
from meeting_status_client.library.async_status_request_runner import AsyncStatusRequestRunner
from meeting_status_client.library.event_loop import EventLoop, StateType
from meeting_status_core.model.status import Status


class Application(QApplication):

  def __init__(self, *args, **kwargs):
    super(Application, self).__init__(*args, **kwargs)

    self.setQuitOnLastWindowClosed(False)
    self.menu = Menu()
    self.menu.quit_action.triggered.connect(self.quit)

    self.tray = QSystemTrayIcon()
    self.tray.setIcon(QIcon('resources/user.svg'))
    self.tray.setVisible(True)
    self.tray.setContextMenu(self.menu)

    meeting_status_client = MeetingStatusClient('192.168.1.114', port=80)
    async_status_request_runner = AsyncStatusRequestRunner(meeting_status_client)
    self.event_loop = EventLoop(
      getuser(),
      async_status_request_runner,
      self.event_loop_callback)

    self.menu.aboutToShow.connect(self.enqueue_request)

  @pyqtSlot(object, object)
  def event_loop_callback(
      self,
      statuses: list[Status] = None,
      exception: Exception = None):
    self.menu.update_state(statuses, exception)

  @pyqtSlot()
  def enqueue_request(self):
    self.event_loop.enqueue_status_request_event()


if __name__ == '__main__':
  application = Application([])
  application.exec_()
