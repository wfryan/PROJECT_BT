import logging
import platform
from logging.handlers import TimedRotatingFileHandler

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
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if "Windows" in platform.system():
            logname = "logs\\" + logName
        else:
            logname = "logs/" + logName
        handler = TimedRotatingFileHandler(logname, when = "midnight", interval=1)
        handler.setLevel(level)
        handler.suffix= "%Y%m%d"
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def logDebug(self, msg, sender):
        log = msg + "     From: " + sender
        self.logger.debug(log)
        print("hello")

    def log401(self, msg):
        log = msg
        self.logger.warning(log)
        print("hello")

    def logInfo(self, msg):
        log = msg
        self.logger.info(log)
        print("hello")

    def logWarn(self, msg):
        log = msg
        self.logger.warning(log)