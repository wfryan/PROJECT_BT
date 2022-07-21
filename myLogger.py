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

