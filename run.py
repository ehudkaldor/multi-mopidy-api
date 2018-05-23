from flask import Flask, Blueprint
from multiMopidyApi.snapcast.clients.clients import clients
from multiMopidyApi.snapcast.snapcast import Snapcast
import logging
import configparser
import asyncio

logging.basicConfig(filename='info.log',level=logging.INFO)
logging.basicConfig(filename='warn.log',level=logging.WARN)
logging.basicConfig(filename='debug.log',level=logging.DEBUG)
logging.basicConfig(filename='error.log',level=logging.ERROR)
# log = logging.getLogger("run")

def create_app(config_filename):



    app = Flask(__name__)
    app.logger_name = __name__
    log = app.logger
    app.config.from_object(config_filename)

    config = configparser.ConfigParser()
    config.read('snapcast.ini')
    methods = config["methods"]
    events = config["events"]
    log.info(f'snapcast methods: {methods["SERVER_GETSTATUS"]}')
    snapcast = Snapcast(methods, events)
    snapcast.start()
    snapcast.getJsonRpcVersion()
    snapcast.getServerStatus()

    # from app import api_bp
    app.register_blueprint(clients, url_prefix='/api/snapcast/clients')

    # from Model import db
    # db.init_app(app)
    log.info("app created")
    return app

def run():
    app = create_app("config")
    app.run(debug=True, host='0.0.0.0')

if __name__ == "__main__":
    app = create_app("config")
    app.run(debug=True, host='0.0.0.0')
