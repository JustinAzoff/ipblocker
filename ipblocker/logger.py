import logging
import logging.config

logging.config.fileConfig(["/etc/ipblocker/ipblocker.cfg", "ipblocker.cfg"])


#create logger
logger = logging.getLogger("ipblocker")
