from mysql.connector import pooling
from config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

class DatabasePool:

    if app.config['IS_DEV']:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name=app.config['POOL_NAME'],
            pool_size=16,
            host=app.config['HOST_DEV'],
            database=app.config['DATABASE_DEV'],
            user=app.config['USERNAME_DEV'],
            password=app.config['PASSWORD_DEV']
        )
    elif app.config['IS_TEST']:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name=app.config['POOL_NAME'],
            pool_size=32,
            host=app.config['HOST_TEST'],
            database=app.config['DATABASE_TEST'],
            user=app.config['USERNAME_TEST'],
            password=app.config['PASSWORD_TEST']
        )
    else:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name=app.config['POOL_NAME'],
            pool_size=32,
            host=app.config['HOST_PROD'],
            database=app.config['DATABASE_PROD'],
            user=app.config['USERNAME_PROD'],
            password=app.config['PASSWORD_PROD']
        )

    @classmethod
    def getConnection(cls): 
        dbConn = cls.connection_pool.get_connection()
        return dbConn
