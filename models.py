from helpers import DateTime, UnixTime, ComplexEncoder
from passlib.hash import pbkdf2_sha256 as sha256
from boto3.dynamodb.conditions import Key, Attr
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
    def __init__(self, id, email, username, password, name):
        self.id = id
        self.email = email
        self.username = username
        self.password =password
        self.name = name

    #Método para crear un usuario
    def create_user(self):
        payload = {
            'Id': self.id,
            'Email': self.email,
            'Username': self.username,
            'Password': self.password,
            'Name': self.name,
            'Created_Date': UnixTime().Now(),
            'Modified_Date': DateTime().Now()
        }
        #Inserta un elemento en la base de datos
        userTable.put_item(Item=payload)
    
    #Método que busca un email en la base de datos, se utiliza 
    #classmethod la cual recibe una clase como argumento
    @classmethod
    def find_by_Email(cls, email):
        response = userTable.query(
            KeyConditionExpression=Key('Email').eq(email),
            ScanIndexForward = False
        )

        payload = response['Items']

        #Para obtener una respuesta coherente, el payload debe pasar 
        #por el helper ComplexEncoder, después, se codifica en formato JSON
        itemEncoder = json.dumps(payload, cls=ComplexEncoder, indent=4)
        return json.loads(itemEncoder)

    #Método que busca un usuario en la base de datos basado en su id
    @classmethod
    def find_user(cls, userId):
        response = userTable.scan(
            FilterExpression=Attr('Id').eq(userId)
        )

        payload = response['Items']

        #Para obtener una respuesta coherente, el payload debe pasar 
        #por el helper ComplexEncoder, después, se codifica en formato JSON
        itemEncoder = json.dumps(payload, cls=ComplexEncoder, indent=4)
        return json.loads(itemEncoder)

    #Método para obtener todos los usuarios
    @classmethod
    def return_all(cls):
        response = userTable.scan()
        payload = response['Items']

        #La operación scan() retorna todos los elementos de la tabla 
        #correspondiente, siempre y cuando el tamaño que retorne sea menor a 1MB. 
        #Esto se resuelve paginando los resultados en un bucle
        while 'LastEvaluatedKey' in response:
            response = userTable.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            payload.extend(response['Items'])
        
        itemsEncoder = json.dumps(payload, cls=ComplexEncoder, indent=4)
        return json.loads(itemsEncoder)
    
    #Crea un algoritmo hash de la contraseña
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    #Verifica la contraseña dada
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
    
    #Genera un id de forma aleatoria con 24 caracteres de longitud
    @staticmethod
    def generate_id():
        return shortuuid.ShortUUID().random(length=24)
