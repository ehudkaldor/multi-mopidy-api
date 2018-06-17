import configparser

class Config:
    def __init__(self, configFile):
        self.config = configparser.ConfigParser()
        self.config.read(configFile)
        self.methods = self.config["methods"]
        self.events_callbacks = self.config["events_callbacks"]
