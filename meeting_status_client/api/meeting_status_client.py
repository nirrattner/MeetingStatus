import json

from typing import Callable

from PyQt5.QtCore import (
  QObject,
  QUrl,
  pyqtSignal,
  pyqtSlot,
)

from PyQt5.QtNetwork import (
  QNetworkAccessManager,
  QNetworkReply,
  QNetworkRequest,
)

from meeting_status_core.model.status import (
  Status,
  StatusRequest,
  StatusResponse,
)


class MeetingStatusClient(QObject):
  callback_signal = pyqtSignal(object, object)

  def __init__(
      self,
      host: str,
      port: int,
      callback_slot: Callable):
    QObject.__init__(self)

    self.host = host
    self.port = port
    self.network_access_manager = QNetworkAccessManager()
    self.network_access_manager.finished.connect(self.handle_reply_slot)
    self.callback_signal.connect(callback_slot)

  @pyqtSlot(object)
  def submit_status(self, status: Status):
    request_body = StatusRequest(status)
    request = QNetworkRequest(QUrl(f'http://{self.host}:{self.port}/meeting_status/status'))
    request.setRawHeader(b'Content-Type', b'application/json')
    request.setTransferTimeout(2000)
    self.network_access_manager.post(request, json.dumps(request_body.to_dict).encode('utf-8'))

  @pyqtSlot(QNetworkReply)
  def handle_reply_slot(self, reply: QNetworkReply):
    try:
      error = reply.error()
      if error:
        self.callback_signal.emit(
          None,
          f'Error: Network error {error}')
        return

      response_body = str(reply.readAll(), 'utf-8')
      status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
      if status_code != 200:
        self.callback_signal.emit(
          None,
          f'Error: Response[{status_code}]: {response_body}')
        return

      self.callback_signal.emit(
        StatusResponse.from_dict(json.loads(response_body)).statuses,
        None)
    except Exception as exception:
      self.callback_signal.emit(
        None,
        f'Error: {exception}')
