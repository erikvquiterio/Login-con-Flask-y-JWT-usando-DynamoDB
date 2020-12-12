from decimal import Decimal
import time
import calendar
import datetime
import pytz
import json
import shortuuid
import itertools
import typing


#Devuelve un instante de tiempo en formato UNIX
class UnixTime():
    def now(self):
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


#Genera un id de forma aleatoria con 24 caracteres de longitud
class GenerateUUID():
    def create_id(self):
        return shortuuid.ShortUUID().random(length=24)


#Crea un objeto para cada solicitud 
class Format():
    def dumps_and_loads(self, dict):
        itemsEncoder = json.dumps(dict, indent=4)
        return json.loads(itemsEncoder)

    def _loads(self, dict):
        return json.loads(dict)

    def dynamo_format(self, dict):
        itemsEncoder = json.dumps(dict, cls=ComplexEncoder, indent=4)
        return json.loads(itemsEncoder)
    
    def float_to_decimal(self, dict):
        itemsEncoder = json.dumps(dict, indent=4)
        return json.loads(itemsEncoder, parse_float=Decimal)


#Genera un id de forma aleatoria con 24 caracteres de longitud
class Pagination():
    #Devuelve un generador que produce una secuencia de elementos para cada respuesta de la función de paginación
    def iterate_result_pages(self, function_returning_response: typing.Callable, *args, **kwargs) -> typing.Generator:

        #Retorna una respuesta de AWS con la carga de 'Items'. Opcionalmente, se puede agregar 'LastEvaluateKey'
        response = function_returning_response(*args, **kwargs)
        yield response["Items"]
        while "LastEvaluatedKey" in response:
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            response = function_returning_response(*args, **kwargs)
            yield response["Items"]
        return

    #Devuelve un iterador con todos los elementos de las respuestas. La carga 'Items' se entrega tan pronto como se obtiene
    def iterate_paged_results(self, function_returning_response: typing.Callable, *args, **kwargs) -> typing.Iterator:
        return itertools.chain.from_iterable(Pagination().iterate_result_pages(function_returning_response, *args, **kwargs))
