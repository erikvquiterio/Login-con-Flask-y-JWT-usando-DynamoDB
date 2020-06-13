from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from flask import Flask

#Se crean nuevos objetos los cuales son adjuntados a la app
app = Flask(__name__)
api = Api(app)

#Se crea una una clave secreta para JWT y se establecen los CORS
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

app.config['JWT_SECRET_KEY'] = 'My-Token'
jwt = JWTManager(app)


import models, resources

#Endpoints finales de la aplicación
api.add_resource(resources.UserRegistration, '/api/v1/auth/signup')
api.add_resource(resources.UserLogin, '/api/v1/auth/login')
api.add_resource(resources.AllUsers, '/api/v1/users')
api.add_resource(resources.User, '/api/v1/user/<userId>')
api.add_resource(resources.TokenRefresh, '/api/v1/token/refresh')
