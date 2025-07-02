from collections.abc import Callable
from enum import IntEnum
from queue import Queue, Empty
from time import time

from PyQt5.QtCore import (
  QObject,
  QThread,
  pyqtSignal,
  pyqtSlot,
)

from meeting_status_client.library.async_status_request_runner import AsyncStatusRequestRunner
from meeting_status_client.library.microphones import is_any_microphone_active
from meeting_status_core.model.status import (
  Status,
  StatusType,
)

STATUS_REQUEST_PERIOD_SECONDS = 10
STATUS_POLL_PERIOD_SECONDS = 2
STATUS_REQUEST_TIMEOUT_SECONDS = 5


class StateType(IntEnum):
  AWAITING_REQUEST = 0
  AWAITING_RESPONSE = 1


class EventType(IntEnum):
  STATUS_REQUEST = 0
  STATUS_RESPONSE = 1


class Event:

  def __init__(
      self,
      event_type: EventType,
      body=None,
      exception: Exception = None):
    self.event_type = event_type
    self.body = body
    self.exception = exception


class EventLoop(QObject):
  callback_signal = pyqtSignal(object, object)

  def __init__(
      self,
      user: str,
      async_status_request_runner: AsyncStatusRequestRunner,
      callback_slot: Callable):
    QObject.__init__(self)

    self.user = user
    self.async_status_request_runner = async_status_request_runner
    self.callback_signal.connect(callback_slot)

    self.last_status_type = None
    self.last_response_timestamp = 0
    self.state = StateType.AWAITING_REQUEST

    self.queue = Queue()
    self.enqueue_status_request_event()

    self.thread = QThread()
    self.moveToThread(self.thread)
    self.thread.started.connect(self.run)
    self.thread.start()

  def run(self):
    while True:
      try:
        if self.state == StateType.AWAITING_REQUEST:
          self.run_awaiting_request_state()

        if self.state == StateType.AWAITING_RESPONSE:
          self.run_awaiting_response_state()
      except Exception as exception:
        print(f'Failed to dequeue event loop {exception}')

  def run_awaiting_request_state(self):
    try:
      event = self.queue.get(timeout=STATUS_POLL_PERIOD_SECONDS)
      if event.event_type == EventType.STATUS_REQUEST:
        self._initiate_status_request()
      else:
        print(f'Unsupported event {event.event_type} for state {self.state}')
    except Empty:
      status_type = get_status_type()
      if status_type != self.last_status_type \
          or time() - self.last_response_timestamp  > STATUS_REQUEST_PERIOD_SECONDS:
        self._initiate_status_request()

  def run_awaiting_response_state(self):
    try:
      event = self.queue.get(timeout=STATUS_REQUEST_TIMEOUT_SECONDS)
      if event.event_type == EventType.STATUS_RESPONSE:
        self._handle_status_response(
          event.body,
          event.exception)
      else:
        print(f'Unsupported event {event.event_type} for state {self.state}')
    except Empty:
      self.state = StateType.AWAITING_REQUEST

  @pyqtSlot()
  def enqueue_status_request_event(self):
    self.queue.put(
      Event(EventType.STATUS_REQUEST),
      block=False)

  def enqueue_status_response_event(
      self,
      response,
      exception: Exception = None):
    self.queue.put(
      Event(
        EventType.STATUS_RESPONSE,
        body=response,
        exception=exception),
      block=False)

  def _initiate_status_request(self):
    self.state = StateType.AWAITING_RESPONSE

    self.last_status_type = get_status_type()
    self.async_status_request_runner.enqueue_request(
      Status(
        self.last_status_type,
        self.user,
        int(time())),
      self.enqueue_status_response_event)

  def _handle_status_response(
      self,
      statuses: list[Status],
      exception: Exception = None):
    self.state = StateType.AWAITING_REQUEST
    self.last_response_timestamp = time()
    self.callback_signal.emit(statuses, exception)

  def _dequeue(self, timeout: float):
    if timeout <= 0:
      raise Empty
    return self.queue.get(timeout=timeout)

def get_status_type() -> StatusType:
  return StatusType.BUSY if is_any_microphone_active() else StatusType.FREE
