from helpers import UnixTime, GenerateUUID, Format, Pagination
from passlib.hash import pbkdf2_sha256 as sha256
from boto3.dynamodb.conditions import Key
import shortuuid
import boto3
import json

#Se invoca el método boto3.resource() para instanciar los recursos de la 
#base de datos de dynamodb
dynamoClient = boto3.resource('dynamodb')
userTable = dynamoClient.Table('Usuarios')
revokedTokensTable = dynamoClient.Table('TokensRevocados')


class UserModel():
    #La función __init__ asigna valores a las propiedades de un objeto
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.kwargs = kwargs

    #Método para crear un usuario
    def create_user(self):
        dictUser = self.kwargs
        dictUser["Id"] = GenerateUUID().create_id()
        dictUser["Created_Date"] = UnixTime().now()
        dictUser["Password"] = sha256.hash(self.Password)

        #Inserta un elemento en la base de datos
        userTable.put_item(Item=dictUser)
        return dictUser["Id"]
    
    #Método que busca un usuario por su email utilizando el índice 
    #secundario global (GSI)
    @staticmethod
    def find_by_Email(email):
        response = userTable.query(
            IndexName='Email-Index',
            KeyConditionExpression=Key('Email').eq(email)
        )

        payload = response['Items']

        #Para obtener una respuesta coherente, el payload debe pasar 
        #por el helper ComplexEncoder, después, se codifica en formato JSON
        creteJsonObject = Format()
        return creteJsonObject.dynamo_format(payload)

    #Método que busca un usuario en la base de datos basado en su id
    @staticmethod
    def find_user(userId):
        response = userTable.query(
            KeyConditionExpression=Key('Id').eq(userId),
            ScanIndexForward = False
        )

        payload = response['Items']

        creteJsonObject = Format()
        return creteJsonObject.dynamo_format(payload)

    #Método para obtener todos los usuarios
    @staticmethod
    def return_all():
        newPagination = Pagination()

        response = list(newPagination.iterate_paged_results(userTable.scan))

        #Elimina la propiedad Password de cada usuario
        for x in range(len(response)):
            del response[x]['Password']

        return response

    #Verifica la contraseña dada
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
