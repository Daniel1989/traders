from service.exchange.dlfe import Dlfe
from service.exchange.shfe import Shfe
from service.exchange.zzfe import Zzfe
from service.exchange.gzfe import Gzfe


class Dummy():
    pass


def getExchange(place):
    if place == 'sh':
        return Shfe()
    if place == 'dl':
        return Dlfe()
    if place == 'zz':
        return Zzfe()
    if place == 'gz':
        return Gzfe()
    else:
        return Dummy()
