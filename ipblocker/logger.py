import logging
import logging.config

env = os.getenv("IPBLOCKER_CONFIG")
if env:
    logging.config.fileConfig([env])
else:
    logging.config.fileConfig(["/etc/ipblocker/ipblocker.cfg", "ipblocker.cfg"])


#create logger
logger = logging.getLogger("ipblocker")
