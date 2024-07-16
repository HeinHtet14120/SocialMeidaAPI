from model.DatabasePool import DatabasePool

class Timezone:
    @classmethod
    def get(cls,):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT * FROM timezone
                """

            cursor.execute(sql,())
            timezones = cursor.fetchall()
            return timezones
        
        except Exception as e:
            print("Error while getting time zones:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")