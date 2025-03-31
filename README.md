Programa de reparto energético. Licencia GPLv3

Hay que crear el archivo:

    .\pages\coef_scripts\config_DB.ini

Hay que completar con la información de la base de datos a la que apunta la aplicación. Ejemplo:

    ;config_DB.ini

    [Database_Server]
    user = Usuario
    password = 000000
    host = 127.0.0.1
    port = 3306
    database = mi_db

Ya hay un archivo config_DBini que se puede modificar añadiendo un punto antes del ini y modificando su contenido con el respectivo para la base de datos.