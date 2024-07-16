from model.DatabasePool import DatabasePool

class User:
    @classmethod
    def register(cls, email, username, password, dob, phone_number, country, preferred_language, gender, gender_others, aboutme, profile_image):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql = "INSERT INTO users (email, username, password, dob, phone_number, country, preferred_language, gender, gender_others, aboutme, profile_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            cursor.execute(sql, (email, username, password, dob, phone_number, country, preferred_language, gender, gender_others, aboutme, profile_image))
            dbConn.commit()

            # After insertion, fetch the inserted user data based on some identifier
            select_sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(select_sql, (email,))
            user = cursor.fetchone()
            return user
        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def login(cls, email):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");


            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM users WHERE email = %s"

            cursor.execute(sql,(email,))
            user = cursor.fetchone()  # Fetch the user data

            return user

        finally:
            dbConn.close()
            print("release connection")
        
    @classmethod
    def user_exists(cls, email):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))

            existing_user = cursor.fetchone()

            return existing_user is not None

        finally:
            dbConn.close()

    @classmethod
    def user_details(cls, user_id):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM users WHERE id = %s"

            cursor.execute(sql,(user_id,))
            user = cursor.fetchone()  # Fetch the user data

            return user

        finally:
            cursor.close()
            dbConn.close()
            print("release connection")

    @classmethod
    def user_exists_by_id(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))

            existing_user = cursor.fetchone()

            return existing_user is not None

        finally:
            dbConn.close()
            print("release connection")


    @classmethod
    def getUser(cls, id):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (id,))

            user = cursor.fetchone()

            return user

        finally:
            dbConn.close()


    @classmethod
    def updateUser(cls, user_id, preferred_language, country, aboutme, filename):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            cursor = dbConn.cursor(dictionary=True)
            print(f"Connected to {db_Info}")

            sql = """UPDATE users
                    SET preferred_language = COALESCE(%s, preferred_language), 
                        country = COALESCE(%s, country),
                        aboutme = COALESCE(%s, aboutme),
                        profile_image = COALESCE(%s, profile_image),
                        last_updated = COALESCE(CURRENT_TIMESTAMP, last_updated)
                    WHERE id = %s"""

            cursor.execute(sql, (preferred_language, country, aboutme, filename, user_id))
            dbConn.commit()

            query = "SELECT dob, username, email, preferred_language, created_at, aboutme, country, gender, phone_number, profile_image FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()

            return user
        
        except Exception as e:
            print("Error occurred while checking token:", e)

        finally:
            dbConn.close()

    @classmethod
    def resetPassword(cls, email, password):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            cursor = dbConn.cursor(dictionary=True)
            print(f"Connected to {db_Info}")

            sql = """UPDATE users
                    SET password = %s
                    WHERE email = %s"""

            cursor.execute(sql, (password, email))
            dbConn.commit()

            query = "SELECT id, dob, username, email, preferred_language, created_at, aboutme, country, gender, phone_number FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            return user

        finally:
            dbConn.close()

    @classmethod
    def isTokenBlackListed(cls, jti):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            cursor = dbConn.cursor(dictionary=True)
            print(f"Connected to {db_Info}")

            sql ="SELECT * FROM user_tokens WHERE jti = %s AND is_revoked = True"
            cursor.execute(sql, (jti,))

            token = cursor.fetchone()
            

            return token
        
        except Exception as e:
            print("Error occurred while checking token:", e)
        finally:
            dbConn.close()
            print("release connection")
    
    @classmethod
    def invalidateTokens(cls, jtis):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql_update = "UPDATE user_tokens SET is_revoked = TRUE, revoked_at = CURRENT_TIMESTAMP WHERE jti IN (%s, %s)"
            cursor.execute(sql_update, jtis)
            dbConn.commit()
            
            return True
        except Exception as e:
            print("Error occurred while updating tokens:", e)
        finally:
            dbConn.close()
            print("Released connection")

    @classmethod
    def InvalidateRefreshToken(cls, rtid):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql_update = "UPDATE user_tokens SET is_revoked = TRUE, revoked_at = CURRENT_TIMESTAMP WHERE jti = %s"
            cursor.execute(sql_update, (rtid,))
            dbConn.commit()

            sql_update2 = "UPDATE user_tokens SET is_revoked = TRUE, revoked_at = CURRENT_TIMESTAMP WHERE rtjti = %s"
            cursor.execute(sql_update2, (rtid,))
            dbConn.commit()

            return True
        except Exception as e:
            print("Error occurred while updating tokens:", e)
        finally:
            dbConn.close()
            print("Released connection")

    @classmethod
    def addToken(cls, jti, type, userid, rtjti):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            cursor = dbConn.cursor(dictionary=True)
            print(f"Connected to {db_Info}")

            sql = """INSERT INTO user_tokens (jti, type, rtjti, user_id, created_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) """

            cursor.execute(sql, (jti, type, rtjti, userid,))
            dbConn.commit()
            
            return True
        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def revokeAllTokens(cls, userid):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql_update = "UPDATE user_tokens SET is_revoked = TRUE, revoked_at = CURRENT_TIMESTAMP WHERE user_id = %s"
            cursor.execute(sql_update, (userid,))
            dbConn.commit()
            
            return True
        except Exception as e:
            print("Error occurred while updating tokens:", e)
        finally:
            dbConn.close()
            print("Released connection")

