from model.DatabasePool import DatabasePool

class UserLanguage:
    @classmethod
    def addUserLanguage(cls, user_id, language_ids):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)

            if language_ids is not None:
                sql = "INSERT INTO user_languages (user_id, language_id) VALUES (%s, %s)"

                data = [(user_id, language_id) for language_id in language_ids]

                cursor.executemany(sql, data)
                dbConn.commit()

            select_sql = "SELECT ul.language_id, l.name, l.code FROM user_languages ul, languages l WHERE user_id = %s and ul.language_id = l.id;"
            cursor.execute(select_sql, (user_id,))
            userLanguage = cursor.fetchall()
            return userLanguage
        
        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def deleteUserLanguage(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            select_sql = "DELETE FROM user_languages WHERE user_id = %s"
            cursor.execute(select_sql, (user_id,))
            dbConn.commit()

            rows_affected = cursor.rowcount
            return rows_affected

        finally:
            # Close the cursor before returning
            dbConn.close()
            print("Release connection")

    @classmethod
    def getUserLanguage(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)

            select_sql = "SELECT ul.language_id, l.name, l.code FROM user_languages ul, languages l WHERE user_id = %s and ul.language_id = l.id;"
            cursor.execute(select_sql, (user_id,))
            userLanguage = cursor.fetchall()
            return userLanguage
        
        finally:
            dbConn.close()
            print("release connection")

