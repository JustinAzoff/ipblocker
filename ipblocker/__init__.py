from ipblocker.model import *
from ipblocker.logger import logger

from ipblocker.config import config
from ipblocker import util


def is_country_ok(cc):
    """Return True if this country is in one of the configured "OK" countries(like the US)
       If the CC is unknown or the CC is NOT US, return False"""
    ok_countries = config.get("blocking","ok_countries").split(",")
    if not cc or cc in ok_countries:
        return True
    return False
