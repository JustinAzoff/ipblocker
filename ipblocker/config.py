import ConfigParser
import os

config = ConfigParser.ConfigParser()

env = os.getenv("IPBLOCKER_CONFIG")
if env:
    config.read([env])
else:
    config.read(['/etc/ipblocker/ipblocker.cfg','ipblocker.cfg'])
