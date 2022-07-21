import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('simple')
logger.setLevel(10)
logname = "text-usage.log"
handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.suffix = "%Y%m%d"
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