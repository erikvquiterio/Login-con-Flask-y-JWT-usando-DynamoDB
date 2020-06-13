import time
import calendar
import datetime
import pytz
import json
import decimal

#Devuelve la hora y fecha basado en la región, con formato (DD/MM/AAAA HH:MM:SS)
class DateTime():
    def Now(self):
        utcNow = pytz.utc.localize(datetime.datetime.utcnow())
        pstNow = utcNow.astimezone(pytz.timezone("America/Mexico_City"))
        return pstNow.strftime("%d/%m/%Y %H:%M:%S")

#Devuelve un instante de tiempo en formato UNIX
class UnixTime():
    def Now(self):
        return str(calendar.timegm(time.gmtime()))

#Convierte un elemento DynamoDB a un objeto JSON
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            if abs(obj) % 1 > 0:
                return float(obj)
            else:
                return int(obj)
            return super(ComplexEncoder, self).default(obj)
