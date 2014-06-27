# -*- coding: utf-8 -*-

import pygeoip

from . import Config


def get_record_from(ip):
    """ Get record from given IP. """
    gi = pygeoip.GeoIP(Config.get('geoip.4.data.city'))

    return gi.record_by_addr(str(ip))