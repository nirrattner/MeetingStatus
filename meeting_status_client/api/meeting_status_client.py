import requests

from meeting_status_core.model.status import (
  Status,
  StatusRequest,
  StatusResponse,
)


class MeetingStatusClient:
  def __init__(self, host: str, port: int = 8080):
    self.host = host
    self.port = port

  def submit_status(
self, status: Status) -> list[Status]:
    request_body = StatusRequest(status)
    response = requests.post(
      f'http://{self.host}:{self.port}/status',
      json=request_body.to_dict)

    if response.status_code != 200:
      raise Exception(f'request failed {response.status_code} -- {response.text}')

    return StatusResponse.from_dict(response.json()).statuses
