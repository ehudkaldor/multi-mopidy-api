import configparser

class Config:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)
        self.methods = config["methods"]
        self.events_callbacks = config["events_callbacks"]
