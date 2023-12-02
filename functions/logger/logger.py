import copy
import os
import logging.config

from functions.constants import Constants

__all__ = ["Logger"]


class Logger:
    def __init__(self, logger_name):
        self.logger_name = logger_name
        logging.config.dictConfig(self._init_logger_config())

    def get_logger(self):
        logger = logging.getLogger(self.logger_name)
        return logger

    def _init_logger_config(self):
        filepath = os.getcwd()
        if not os.path.exists(filepath + '/log'):
            os.makedirs(filepath + '/log')
        LOG_CONFIG = copy.deepcopy(Constants.LOG_CONFIG)
        LOG_CONFIG['loggers'] = {
            self.logger_name: LOG_CONFIG['loggers'].get(self.logger_name)
        }
        handlers = LOG_CONFIG['loggers'].get(self.logger_name).get("handlers")
        LOG_CONFIG['handlers'] = self._set_config(LOG_CONFIG, handlers, filepath)
        return LOG_CONFIG

    def _set_config(self, log_config, handlers, filepath):
        handlers_config = {}
        for handler in handlers:
            v = log_config["handlers"].get(handler)
            if "filename" in v.keys() and v.get("filename", None) is None:
                v['filename'] = filepath + f"/log/{self.logger_name}.log"
            handlers_config[handler] = v
        return handlers_config
