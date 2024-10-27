import logs
import logging
import psycopg
from pprint import pprint

class DBConnect():
    """
    Connecte et interagie avec une base de donnee.
    """
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formater = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formater)

    logger.addHandler(stream_handler)

    def __init__(self, user: str, password: str, host: str, port: str, database: str) -> None:
        self.user: str = user
        self.password: str = password
        self.host: str = host
        self.port: str = port
        self.database: str = database

    def __str__(self) -> str:
        return f"Database: {self.database}; Host: {self.host}:{self.port}; User: {self.user}; Password: {self.password}"

    def _connectDB(self) -> psycopg.Connection:
        """
        Connection a la base de donnees.
        """
        self.connection: psycopg.Connection = psycopg.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            dbname=self.database
        )
        DBConnect.logger.info(f"Nouvelle connection => {self}")
        return self.connection

    @logs.Timer
    def ShowVersion(self) -> str:
        """
        :return str: version de Postgre
        """
        _cursor: psycopg.Cursor = self._connectDB().cursor()
        _cursor.execute("SELECT version();")
        _version = _cursor.fetchone() # type: ignore
        return f"Version de Postgre: {_version}"

    @logs.Timer
    def CreateTable(self, table: str, **kwargs: dict) -> None:
        """
        Selectionne les champs dans la table.
        
        :param str table: nom de la table
        :param dict kwargs: paire cle valeur des champs
        """
        _table: str = f"CREATE TABLE IF NOT EXISTS {table} ("
        _list: str = "".join(f"{key} {value}, " for key, value in kwargs.items())
        _end: str = ");"
        _cmd: str = _table+_list[:len(_list)-2]+_end
        
        _cursor: psycopg.Cursor = self.connection.cursor()
        _cursor.execute(_cmd)
        self.connection.commit()
        
        DBConnect.logger.info(f"Envoie de la requete => {_cmd}")

    @logs.Timer
    def Insert(self, table: str, **kwargs: dict) -> None:
        """
        Selectionne les champs dans la table.
        
        :param str table: nom de la table
        :param dict kwargs: paire cle valeur de l'insertion
        """
        _key: str = "".join(f"{key}, " for key, _ in kwargs.items())
        values: list = []
        for value in kwargs.values():
            values.append(value)
        _cmd: str = f"INSERT INTO {table} ("+_key[:len(_key)-2]+") VALUES (%s,%s)"
        
        _cursor: psycopg.Cursor = self.connection.cursor()
        _cursor.execute(_cmd, values)
        self.connection.commit()

        DBConnect.logger.info(f"Envoie de la requete => {_cmd}, ({values})")

    @logs.Timer
    def Select(self, table: str, *args: tuple) -> list:
        """
        Selectionne les champs dans la table.
        
        :param str table: nom de la table
        :param list args: champs a selectionner
        
        :return: 
        """
        _arg: str = "".join(f"{arg}, " for arg in args)
        _cmd: str = f"SELECT {_arg[:-2]} FROM {table};"
        _cursor: psycopg.Cursor = self.connection.cursor()
        _cursor.execute(_cmd)

        DBConnect.logger.info(f"Envoie de la commande => {_cmd}")
        return _cursor.fetchall()

    def Close(self) -> None:
        self.connection.cursor().close()
        self._connectDB().close()
        DBConnect.logger.info(f"Fermeture de la connexion.")

if __name__=="__main__":
    exo: DBConnect = DBConnect("root", "root", "db", "5432", "test")
    tableUser: str = "users"
    
    try:
        version: str = exo.ShowVersion()
        pprint(version)
        exo.CreateTable(tableUser,id="SERIAL PRIMARY KEY", name="VARCHAR(100)", email="VARCHAR(100)")
        exo.Insert(tableUser, name="John Doe", email="john@example.com")
        users:list = exo.Select(tableUser, "*")
        pprint(users)
    except Exception as e:
        print(e)
    finally:
        exo.Close()