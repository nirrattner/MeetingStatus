from flask import jsonify, request

from meeting_status_core.model.status import StatusResponse, StatusRequest

from meeting_status_server import app
from meeting_status_server.status.status_manager import StatusManager

STATUS_MANAGER = StatusManager()

@app.route('/status', methods=['GET'])
def get_statuses():
  statuses = STATUS_MANAGER.get_statuses()
  return jsonify(StatusResponse(statuses=statuses).to_dict), 200

@app.route('/status', methods=['POST'])
def post_status():
  try:
    status_request = StatusRequest.from_dict(request.json)
  except Exception as exception:
    print(exception)
    return 'Invalid input', 400
  STATUS_MANAGER.update_status(status_request.status)

  statuses = STATUS_MANAGER.get_statuses()
  return jsonify(StatusResponse(statuses=statuses).to_dict), 200

@app.route('/status', methods=['DELETE'])
def delete_status():
  user = request.args.get('user')
  if user is None:
    return 'Missing "user" query parameter', 400
  STATUS_MANAGER.delete_status(user)
  return '', 204
