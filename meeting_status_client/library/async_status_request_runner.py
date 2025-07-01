from collections.abc import Callable
from queue import Queue
from threading import Thread

from meeting_status_client.api.meeting_status_client import MeetingStatusClient
from meeting_status_core.model.status import Status


class StatusRequestEvent:

  def __init__(
      self,
      status: Status,
      callback_function: Callable):
    self.status = status
    self.callback_function = callback_function


class AsyncStatusRequestRunner:

  def __init__(self, client: MeetingStatusClient):
    self.client = client
    self.queue = Queue()
    self.thread = Thread(target=self.run)
    self.thread.daemon = True
    self.thread.start()

  def enqueue_request(
      self,
      status: Status,
      callback_function: Callable):
    self.queue.put(StatusRequestEvent(status, callback_function), block=False)

  def run(self):
    while True:
      status_request_event = self.queue.get(block=True)
      try:
        statuses = self.client.submit_status(status_request_event.status)
        status_request_event.callback_function(statuses)
      except Exception as exception:
        status_request_event.callback_function(None, exception=exception)
