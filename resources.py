from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, 
jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask_restful import Resource, reqparse
from constants import Constant
from models import UserModel
from helpers import Format
from flask import request

#Se agrega un analizador de datos para todas las solicitudes POST
parserLogin = reqparse.RequestParser()
parserLogin.add_argument('Email', help = Constant.REQUIRED_FIELD, required = True)
parserLogin.add_argument('Password', help = Constant.REQUIRED_FIELD, required = True)

#Flask Restful permite hacer herencia en sus analizadores, usa copy() para extender los argumentos
#a un nuevo analizador
parserRegistration = parserLogin.copy()
parserRegistration.add_argument('Username', help = Constant.REQUIRED_FIELD, required = True)
parserRegistration.add_argument('Name', help = Constant.REQUIRED_FIELD, required = True)


#Clase para el endpoint signup
class UserRegistration(Resource):
    def post(self):
        data = parserRegistration.parse_args()
        email = data['Email']
        password = data['Password']
        user = data['Name']

        if email == '' or password == '':
            return {
                'message': Constant.EMPTY_FIELDS
            }, 400

        #El resultado que devuelve la clase se analiza y compara con la condicional if, si es true, 
        #retorna un mensaje de un correo existente
        if UserModel.find_by_Email(email):
            return {
                'message': Constant.EXISTING_RECORD.format(email)
            }, 400
        
        #Convierte a un objeto json la data proveniente de los argumentos e inicia el 
        #método para crear el nuevo registro
        creteJsonObject = Format()
        newData = creteJsonObject.dumps_and_loads(data)
        newUser = UserModel(**newData)

        #El manejador de excepciones mostrará un mensaje de que un usuario ha sido creado, por lo 
        #contrario, mostrará que algo ha salido mal
        try:
            Id = newUser.create_user()
            return {
                'message': Constant.RECORD_CREATED.format(user, email),
                'token':  create_access_token(identity =  Id),
                'refreshToken': create_refresh_token(identity =  Id)
            }, 200
        except:
            return {'message': Constant.BAD_REQUEST}, 500


#Clase para el endpoint login
class UserLogin(Resource):
    def post(self):
        data = parserLogin.parse_args()
        email = data['Email']
        password = data['Password']

        if email == '' or password == '':
            return {
                'message': Constant.EMPTY_FIELDS
            }, 400

        currentUser = UserModel.find_by_Email(email)

        #El resultado que devuelve la clase se analiza y compara con la condicional if, 
        #si es false, retorna un mensaje de una cuenta inexistente
        if not currentUser:
            return {
                'message': Constant.THE_NON_EXISTING_USER
            }, 404

        #La siguiente sentencia compara la contraseña obtenida con la contraseña del usuario 
        #que intenta acceder usando el método de clase verify_hash
        if UserModel.verify_hash(password, currentUser[0]['Password']):

            accessToken = create_access_token(identity = currentUser[0]['Id'])
            refreshToken = create_refresh_token(identity = currentUser[0]['Id'])
            
            #Se devuelve los datos correspondientes del usuario, así como los tokens
            del currentUser[0]['Password']
            return {
                'token': accessToken,
                'user' : currentUser[0],
                'refreshToken': refreshToken
            }, 200
        else:
            return {'message': Constant.WRONG_CREDENTIALS}, 400


#Devuelve todos los usuarios registrados, la clase pertenece al endpoint users
class AllUsers(Resource):
    #El endpoint requiere un token de acceso
    @jwt_required
    def get(self):
        return UserModel.return_all(), 200


#Devuelve solo un usuario, la clase pertenece al endpoint user
class User(Resource):
    @jwt_required
    def get(self, userId):

        user = UserModel.find_user(userId)
        
        #Se retorna un mensaje de error si el usuario no existe, por lo contrario,
        #se devuelve toda la información
        if not user:
            return {
                'message': Constant.THE_NON_EXISTING_REGISTRY.format(userId)
            }, 404
        
        del user[0]['Password']
        return user, 200


#Clase que actualiza el token de acceso, la clase pertenece al endpoint tokenRefresh
class TokenRefresh(Resource):
    #El decorador requiere el token de actualización
    @jwt_refresh_token_required
    def post(self):

        #Para identificar al usuario se utiliza la función auxiliar get_jwt_identity()
        #que extrae la identidad del token de actualización
        currentUser = get_jwt_identity()
        accessToken = create_access_token(identity = currentUser)
        return {'accessToken': accessToken}, 200
    

#Recupera la información a partir del token del usuario
class UserIdentity(Resource):
    @jwt_required
    def get(self):
        if 'Authorization' in request.headers:
            idFromJWT = request.headers.get('Authorization')
            idFromJWT = get_jwt_identity()

            currentUser = UserModel.find_user(idFromJWT)

            if not currentUser:
                return {
                    'message': Constant.THE_NON_EXISTING_REGISTRY
                }, 404

            del currentUser[0]['Password']
            return currentUser, 200
        
        else: 
            return Constant.MISSING_AUTH, 400
