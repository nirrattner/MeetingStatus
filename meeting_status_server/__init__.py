from flask import Flask

app = Flask(__name__)

from meeting_status_server.resources import *
