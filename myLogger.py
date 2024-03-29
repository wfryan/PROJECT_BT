import logging
import platform
from logging import FileHandler

"""#logger = logging.getLogger('simple')
#logger.setLevel(10)
#logname = ""
#if "Windows" in platform.system():
#    logname = "logs\\text-usage.log"
#else:
#    logname = "logs/text-usage.log"
#handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.setLevel(10)
handler.suffix = "%Y%m%d"
#handler.extMatch = re.compile(r"^\d{8}$") 
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def logDebug(msg, sender):
    log = msg + "     From: " + sender
    logger.debug(log)
    print("hello")

def log401(msg):
    log = msg
    logger.warning(log)
    print("hello")

def logInfo(msg):
    log = msg
    logger.info(log)
    print("hello")

def logWarn(msg):
    log = msg
    logger.warning(log)"""

class myLogger:
    def __init__(self, name, level, logName):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        if "Windows" in platform.system():
            logname = "logs\\" + logName + ".log"
        else:
            logname = "logs/" + logName + ".log"
        handler = FileHandler(logname)
        handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def logDebug(self, msg):
        log = msg
        self.logger.debug(log)


    def log401(self, msg):
        log = msg
        self.logger.warning(log)


    def logInfo(self, msg):
        log = msg
        self.logger.info(log)


    def logWarn(self, msg):
        log = msg
        self.logger.warning(log)