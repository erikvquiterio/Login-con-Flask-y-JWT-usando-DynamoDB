![](/files/api-rest.png)

Este proyecto te ayudará a implementar un backend con autenticación de usuarios usando JWT como proveedor de tokens. La comunicación con la base de datos DynamoDB de AWS se gestiona con el SDK Boto3. El backend cuenta con CORS, por lo que solicitar los recursos de la API no supondrá un problema. 



## Antes de comenzar

- Debes contar con una cuenta AWS, si aún no la tienes, crea una [aquí](https://aws.amazon.com/es/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc). AWS te ofrecerá una capa gratuita, puedes alojar el proyecto sin ningún costo por un año. 
- Crea un usuario IAM, sigue estas [instrucciones](https://docs.aws.amazon.com/es_es/rekognition/latest/dg/setting-up.html)

- Crea una tabla en Dynamo DB. Dirígete a *servicios de AWS > Dynamo DB > Crear tabla*. Por defecto, AWS sugiere usar la configuración predeterminada, pero debes deseleccionar esta opción y configurarla de la siguiente manera:
    ```
    Detalles de la tabla ->
    Nombre de la tabla: Usuarios
    Clave de partición: Id , Tipo: Cadena
    
    Configuración -> 
    Personalizar configuración

    Configuración de capacidad de lectura/escritura ->
    Modo de capacidad: Aprovisionado

    Capacidad de lectura ->
    Auto Scaling: Desactivado, Unidades de capacidad aprovisionadas: 1

    Capacidad de escritura ->
    Auto Scaling: Desactivado | Unidades de capacidad aprovisionadas: 1

    Crear índice global ->
    Clave de partición : Email, Tipo: Cadena
    Nombre de índice : Email-Index
    Proyecciones de atributos: All
    ```

- Configura las credenciales:
  - Crea una carpeta en tu computadora en la raíz del usuario actual (en Windows es : *C:/Users/{tu usuario}*). La carpeta creada debe tener el nombre **.aws**
  - Descarga las credenciales de acceso. Dirígete a *servicios de AWS > IAM > Usuarios > {nombre del usuario creado} > Credenciales de seguridad > Crear una clave de acceso > Descargar archivo .csv*
  - Copia el Access key ID y Secret access key en un nuevo archivo llamado **credential** dentro de la carpeta **.aws** Debe tener el siguiente aspecto:
    ```
    /.aws/credentials
    [default]
    aws_access_key_id = { Tu Access key ID }
    aws_secret_access_key = { Tu Secret access key }
    ```
  - Crea un archivo **config** y en el establece la región (está en el inicio de la url de tu cuenta o en la parte superior derecha de tu perfil AWS, algo como `us-east-2`) y el tipo de salida de la base de datos. Debe tener el siguiente aspecto:
    ```
    /.aws/config
    [default]
    region = {Tu región}
    output = json
    ```
- Debes tener instalado Python 3 (el proyecto utilizo Python 3.6) [descargar](https://www.python.org/downloads/) 

Listo, están configurados los accesos para AWS. Si quieres obtener más información o seguir otros métodos sigue los pasos [2](https://docs.aws.amazon.com/es_es/rekognition/latest/dg/setup-awscli-sdk.html) y [3](https://docs.aws.amazon.com/es_es/rekognition/latest/dg/get-started-exercise.html) de la documentación de AWS. Opcionalmente puedes descargar [Visual Studio Code](https://code.visualstudio.com/download), [Git](https://git-scm.com/downloads) y [AWS CLI](https://pypi.org/project/awscli/). Haz una prueba de conexión (solo si instalaste AWS CLI), escribe en una terminal `aws dynamodb list-tables`, el resultado deber ser:
  ```json
  {
    "TableNames": [
        "Usuarios"
    ]
  }
  ```


## Iniciando
- Clona el repositorio
    
    $ git clone https://github.com/erikvquiterio/Login-con-Flask-y-JWT-usando-DynamoDB.git
    
- En el directorio del proyecto, instala las siguientes dependencias usando PIP
    
    $ pip install -r requirements.txt
    
- Al finalizar, corre el siguiente comando:
  
    $ FLASK_APP=run.py flask run
    

## Endpoints
Existe solo un recurso en este proyecto, los usuarios. En las siguiente tabla verás que rutas existen para operar sobre este recurso.  

|Verbo|Ruta|Auth|Body|
|----|--------------------|-----------------|----------------------------------------------------------------------------------------|
|POST|api/v1/auth/login|No|```{"email": "info@proyecto-teos.com","password": "$QWE098$"}```|
|POST|api/v1/auth/signup|No|```{"email": "info@proyecto-teos.com","username": "TEOS","password": "$QWE098$","name": "proyecto TEOS"}```|
|POST|api/v1/auth/whoami|Si (token)|
|POST|api/v1/token/refresh|Si(refreshToken)||
|GET|api/v1/users/|Si(token o accessToken)||
|GET|api/v1/user/:id|Si(token o accessToken)||

## Licencia
Este proyecto está licenciado bajo la MIT License