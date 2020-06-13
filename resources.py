from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, 
jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask_restful import Resource, reqparse
from models import UserModel

#Se agrega un analizador de datos para todas las solicitudes POST
parserLogin = reqparse.RequestParser()
parserLogin.add_argument('email', help = 'Mail is required', required = True)
parserLogin.add_argument('password', help = 'Password is required', required = True)

#Flask Restful permite hacer herencia en sus analizadores, use copy() para extender los argumentos
#a un nuevo analizador
parserRegistration = parserLogin.copy()
parserRegistration.add_argument('username', help = 'This field cannot be blank', required = True)
parserRegistration.add_argument('name', help = 'This field cannot be blank', required = True)

#Clase para el endpoint signup
class UserRegistration(Resource):
    def post(self):
        data = parserRegistration.parse_args()

        #El resultado que devuelve la clase se analiza y compara con la condicional if, si es true, 
        #retorna un mensaje de un correo existente
        if UserModel.find_by_Email(data['email']):
            return {
                'message': 'The user with the mail {} already exists'.format(data['email'])
            }
        
        #Se crea un objeto de un nuevo usuario
        newUser = UserModel(
            id = UserModel.generate_id(),
            email = data['email'],
            username = data['username'],
            password = UserModel.generate_hash(data['password']),
            name = data['name']
        )

        #Se crean tokens de acceso y de refresh con el email
        accessToken = create_access_token(identity =  data['email'])
        refreshToken = create_refresh_token(identity =  data['email'])

        #El manejador de excepciones mostrará un mensaje de que un usuario ha sido creado, por lo 
        #contrario, mostrará que algo ha salido mal
        try:
            newUser.create_user()
            return {
                'message': 'User {} was created'.format(data['email']),
                'token': accessToken,
                'refreshToken': refreshToken,
            }
        except:
            return {'message': 'Something went wrong'}, 500

#Clase para el endpoint login
class UserLogin(Resource):
    def post(self):
        data = parserLogin.parse_args()
        currentUser = UserModel.find_by_Email(data['email'])

        #El resultado que devuelve la clase se analiza y compara con la condicional if, 
        #si es false, retorna un mensaje de una cuenta inexistente
        if not currentUser:
            return {
                'message': 'The user with the mail {} doesn\'t exist'.format(data['email'])
            }

        #La siguiente sentencia compara la contraseña obtenida con la contraseña del usuario 
        #que intenta acceder usando el método de clase verify_hash
        if UserModel.verify_hash(data['password'], currentUser[0]['Password']):

            accessToken = create_access_token(identity = currentUser[0]['Email'])
            refreshToken = create_refresh_token(identity = currentUser[0]['Email'])
            
            #Se devuelve los datos correspondientes del usuario, así como los tokens
            return {
                'token': accessToken,
                'user' :{
                    'email': currentUser[0]['Email'],
                    'name': currentUser[0]['Name'],
                    'username': currentUser[0]['Username'],
                    '_id': currentUser[0]['Id']
                },
                'refreshToken': refreshToken,
                'message': 'Logged in as {}'.format(currentUser[0]['Username'])
            }, 200
        else:
            return {'message': 'Wrong credentials'}

#Devuelve todos los usuarios registrados, la clase pertenece al endpoint users
class AllUsers(Resource):
    #El endpoint requiere un token de acceso
    @jwt_required
    def get(self):
        return UserModel.return_all()

#Devuelve solo un usuario, la clase pertenece al endpoint user
class User(Resource):
    @jwt_required
    def get(self, userId):

        user = UserModel.find_user(userId)
        
        #Se retorna un mensaje de error si el usuario no existe, por lo contrario,
        #se devuelve toda la información
        if not user:
            return {
                'message': 'The user {} doesn\'t exist'.format(userId)
            }
        
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
        return {'accessToken': accessToken}
