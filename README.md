# API de gestión de riesgos de Ciberseguridad

## Descripción General

En este repositorio encontrarás el código fuente de una pequeña API construida usando el  
framework [Flask](https://flask.palletsprojects.com/es/latest/) y conectándose a una base de datos NoSQl 
[MongoDb](https://mongodb.com/) en la nube.

## Dependencias Principales
- Python 3.11 o superior
- Flask Framework
- Flask RESTFul
- Flask-JWT-Extended
- pymongo

## Installation

Desde una termina siga las siguientes intrucciones

### Clonar el proyecto

```shell
git clone https://github.com/mcubico/api-py-flask-mongo.git
```

### Crear el ambiente de trabajo

Después de descargar el proyecto ubiquese en ese directorio y ejecute el siguiente comando para crear el ambiente de trabajo:

```shell
py -3 -m venv .venv
```

#### Activar el ambiente de trabajo

```shell
.venv\Scripts\activate
```

### Instale las dependencias del proyecto

```shell
pip install -r requirements.txt
```

## Estructura del proyecto
```
api-py-flask-mongo
┣ src
┃ ┣ resources
┃ ┃ ┣ health_checker_resource.py
┃ ┃ ┣ login_resource.py
┃ ┃ ┣ risk_resource.py
┃ ┃ ┗ user_resource.py
┃ ┣ utils
┃ ┃ ┣ encrypt_helper.py
┃ ┃ ┣ exception_management.py
┃ ┃ ┣ user_db_helper.py
┃ ┣ app.py
┃ ┣ models.py
┃ ┣ mongo_database.py
┃ ┗ __init__.py
┣ .flaskenv
┣ .gitignore
┣ LICENSE
┣ main.py
┣ README.md
┣ requirements.txt
┣ scripts.json
┣ setup.py
┣ startup.sh
┣ swagger.json
┗ uwsgi.ini
```

## Variables de entorno

Agregue el archivo ```.env``` y gestione las siguientes variables de entorno:

```properties
FLASK_ENV=developer
FLASK_APP=src
FLASK_RUN_PORT=8000
FLASK_RUN_HOST=127.0.0.1

MONGO_DB_PROTOCOL=
MONGO_DB_CLUSTER=
MONGO_DB_HOST=
MONGO_DB_USERNAME=
MONGO_DB_PASSWORD=
MONGO_DB_DATABASE=

JWT_SECRET_KEY=
```

La variable ```JWT_SECRET_KEY``` la puede generar ejecutando el siguiente comando:

```shell
py
```
```python
>>> import secrets
>>> secrets.token_hex(16)
'38dd56f56d405e02ec0ba4be4607eaab'
```

Las demás variables deben ser diligenciadas con los datos de la cuenta de mongo

## Modo de uso

Para lanzar la API, use el comando esto le permitirá hacer pruebas y verificar los resultados rápidamente

```shell
flask --app main run --watch
```

Para identificar el modo de uso de la api navegar a la documentación en swagger:

http://127.0.0.1:8000/swagger/


## Colaboración

Todas las sugerencias y pull request son bienvenidos. Para cambios críticos por favor abra un issue 
primero para que lo revisemos.

## License

[MIT](https://choosealicense.com/licenses/mit/)