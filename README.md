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

## Instrucciones de instalación

### Descargue el repositorio desde GitHub

```shell
git clone https://github.com/mcubico/api-py-flask-mongo.git
```

### Crear el ambiente de trabajo

Después de descargar el proyecto ubíquese en ese directorio y ejecute el siguiente comando para 
crear el ambiente de trabajo:

```shell
py -3 -m venv venv
```

#### Activar el ambiente de trabajo

```shell
venv\Scripts\activate
```

### Instale las dependencias del proyecto

```shell
(venv) pip install -r requirements.txt
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

## Estructura de la Base de datos

### Colecciones

| `Name`   | `Comment`                                       |
|----------|-------------------------------------------------|
| Users    | Usuarios con permisos de interacción con la API |
| Risks    | Colección con los riesgos                       |
| Features | Características de los riesgos                  |

#### Users
| `Nombre` | `Tipo`   |
|----------|----------|
| _id      | ObjectId |
| username | string   |
| password | string   |

#### Risks
| `Nombre`    | `Tipo`   |
|-------------|----------|
| _id         | ObjectId |
| risk        | string   |
| description | string   |
| active      | boolean  |

#### Features
| `Nombre`      | `Tipo`   | `Comentario`                            |
|---------------|----------|-----------------------------------------|
| _id           | ObjectId | Este id es el mismo del riesgo asociado | 
| vulnerability | string   |                                         |
| probability   | string   |                                         |
| impact        | string   |                                         |
| thread        | string   |                                         |

## Modo de uso

Para lanzar la API, use el comando esto le permitirá hacer pruebas y verificar los resultados rápidamente

```shell
(venv) flask --app main run --watch
```

Para identificar el modo de uso de la api navegar a la documentación en swagger:

http://127.0.0.1:8000/swagger/

## Pruebas

Para verificar que la aplicación pasa todas las pruebas unitarias y funcionales antes de subir cualquier
cambio, ejecute el siguiente comando:

```shell
(venv) py -m pytest -v
```

Si desea ver de forma más detallada el resultado de las pruebas, ejecute el siguiente comando:

```shell
(venv) py -m pytest --cov-report term-missing --cov=project
```

## Colaboración

Todas las sugerencias y pull request son bienvenidos. Para cambios críticos por favor abra un issue 
primero para que lo revisemos.

## License

[MIT](https://choosealicense.com/licenses/mit/)