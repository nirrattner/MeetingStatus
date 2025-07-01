import os

from meeting_status_server import app

if __name__ == '__main__':
  port = int(os.environ.get('HTTP_PORT', 8080))
  app.run(host='0.0.0.0', port=port, debug=True, threaded=True, use_reloader=False)