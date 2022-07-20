import logging
from logging.handlers import TimedRotatingFileHandler



logger = logging.getLogger('simple')
logger.setLevel(20)

logname = "text-usage.log"
handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.suffix = "%Y%m%d"

