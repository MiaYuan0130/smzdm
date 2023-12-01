import os
from .constants import Constants

filepath = os.getcwd()


def getLogConfig(name):
    if not os.path.exists(filepath+'/log'):
        os.makedirs(filepath+'/log')
    LOG_CONFIG_DICT = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(levelname)s]  (%(asctime)s)  << %(filename)s >> :: %(message)s"
            }
        },
        "filters": {
            "fil1": {

            }
        },
        "handlers": {
            "console_warning": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "default"
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default"
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": filepath+f"/log/{name}.log",
                "when": "M",
                # "atTime": "midnight",
                "interval": 1,
                "backupCount": Constants.BACKUP_COUNT,
                "encoding": "utf8"
            }
        },
        "loggers": {
            f"{name}": {
                "level": "INFO",
                "handlers": ["console_warning", "file"],
                "formatter": "default",
                "propagate": False,
            },
            "console_logger": {
                "level": "INFO",
                "handlers": ["console"],
                "formatter": "default",
                "propagate": False,
            },
            "file_logger": {
                "level": "INFO",
                "handlers": ["file"],
                "formatter": "default",
                "propagate": False,
            }
        }
    }
    return LOG_CONFIG_DICT
