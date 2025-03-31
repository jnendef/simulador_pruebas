#
#  Clase agente encargada de realizar las operaciones CRUD sobre base de datos.
#
#  @author fgregorio
#  @traductor jnaveiro
#

import mysql.connector
import sys
import os
import logging
import configparser
from time import sleep

SLEEPING_MS = 10./1000.

logging.getLogger("mysql").setLevel(logging.ERROR)

class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some possible methods include: base class, decorator, metaclass. We will use the metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Agente_MySql(metaclass=SingletonMeta):
    """
    author: fgregorio

    traductor: jnaveiro

    Definición: Esta clase se encarga de la generación del agente de consulta a la base de datos. Su metaclase es SingletonMeta que evita que se instancie múltiples veces el mismo agente. Tiene varios métodos para trabajar con la base de datos en SQL.
    
    Constructor: Genera el agente con las credenciales propias de la base de datos
    
    Propiedades:

        1. conn
        2. cursor
    
    Métodos:

        1. Agente_MySql.isValidConection
        2. Agente_MySql.ejecutar
        3. Agente_MySql.ejecutarMuchos
        4. Agente_MySql.commitTransaction
        5. Agente_MySql.rollBackTransaction

        """

    def __init__(self, archivo:str = "config_DB.ini"):
        """
        Definición: Constructor. Declaramos la instancia del agente y de la conexión. Para ello hay que escribir las credenciales de acceso.
        
        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas:

            1. conn
            2. cursor
        """
        
        direc = os.path.dirname(os.path.realpath(__file__))
        archivo2 = direc+"/"+ archivo
        config = configparser.ConfigParser()
        config.read(archivo2)

        # Connect to mysql.connector Platform
        try:
            self.conn = mysql.connector.connect(
                            user=config.get('Database_Server','user'),
                            password=config.get('Database_Server','password'),
                            host=config.get('Database_Server','host'),
                            port=int(config.get('Database_Server','port')),
                            database=config.get('Database_Server','database'))
            self.cursor = self.conn.cursor()
            logging.info("conexión realizada")

        except mysql.connector.Error as e:
            mensaje = "Error conectando a MariaDB Platform: "
            logging.error(mensaje, exc_info=True)

    def isValidConection(self) :
        """
        Definición: Método para comprobar que la conexión se ha realizado correctamente.
        
        Variables de entrada: Ninguna
        
        Variables de salida: validConection (bool)
        
        Propiedades modificadas: Ninguna
        """
        validConection = self.conn.is_connected()

        # Devolvemos el resultado de la prueba
        return validConection

    def ejecutar(self,sql):
        """
        Definición: Ejecuta la sentencia SQL. En caso de poder devolver algún resultado de una consulta lo hace. Sino, ejecuta la sentencia y en caso de no poder ejecutarla devuelve un error en el archivo log.
        
        Variables de entrada: sql (str)
        
        Variables de salida: devuelve (list)
        
        Propiedades modificadas: cursor
        
        """
        try:
            self.cursor.execute(sql)
            try:
                self.conn.commit()  # Confirmar cambios si es necesario
            except Exception as e:
                if sql.split()[0] != "SELECT":
                    logging.debug("No se puede hacer commit al ejecutar: " + sql.split()[0], exc_info=True)
            
            # Verificar si la consulta devuelve resultados
            if self.cursor.description is not None:  
                return self.cursor.fetchall()  # Solo intenta obtener datos si hay resultados
            
            # Desconectamos y volvemos a conectar el cursor
            self.cursor.close()
            self.cursor = self.conn.cursor()

        except mysql.connector.Error as e:
            logging.warning("Error en MySQL: ", exc_info=True)
            return None

    def ejecutarMuchos(self,sql,listaarg):
        """
        author: jnaveiro
        
        Definición: Metodo encargado de ejecutar la sentencia sql pasada por argumentos. Se le deben pasar los argumentos en una lista de tuplas.
        
        Variables de entrada: sql (str), listaarg (list)
        
        Variables de salida: devuelve (list)
        
        Propiedades modificadas: cursor
        
        """
        try:
            self.cursor.executemany(sql, listaarg)  # Ejecutar múltiples consultas
            self.commitTransaction()  # Confirmar cambios

            return self.cursor.rowcount  # Devolver cantidad de filas afectadas

        except mysql.connector.Error as e:
            logging.error(f"Error en MySqlAgent.executemany(): {e}", exc_info=True)
            if listaarg:
                logging.debug(f"Primer argumento fallido: {listaarg[0]}")
            return None  # Indicar error sin lanzar excepción

    def  commitTransaction(self):
        """
        Definición: Método encargado de realizar el commit de la transacción.
        
        Variables de entrada: Ninguna
        
        Variables de salida: Ninguna
        
        Propiedades modificadas: Ninguna
        
        """
        sleep(SLEEPING_MS)

        try :
            
            # Obtenemos la instancia del agente y realizamos el commit
            self.conn.commit()

            # Establecemos de nuevo el autocommit
            self.conn.autocommit = True

        except Exception as e :
            mensaje = "Excepcion MySqlAgent.commitTransaction: "
            logging.info(mensaje, exc_info=True)
            pass
        
        return

    def  rollBackTransaction(self):
        """
        Definición: Método encargado de realizar el rollback de la transacción.
        
        Variables de entrada: Ninguna
        
        Variables de salida: Ninguna
        
        Propiedades modificadas: Ninguna
        
        """
        sleep(SLEEPING_MS)

        try :
            
            # Obtenemos la instancia del agente y realizamos el commit
            self.cursor.rollback()
            sleep(SLEEPING_MS)

            # Establecemos de nuevo el autocommit
            self.cursor.autocommit = True
            
        except Exception as e :
            mensaje = "Error en el MySqlAgent.rollBackTransaction: "
            logging.info(mensaje, exc_info=True)

