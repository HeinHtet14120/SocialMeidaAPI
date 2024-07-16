from model.DatabasePool import DatabasePool

class Language:
    @classmethod
    def get_all_languages(cls):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM languages"

            cursor.execute(sql)
            languages = cursor.fetchall()
            return languages

        finally:
            dbConn.close()
            print("Released connection")
