from model.DatabasePool import DatabasePool

class UserConnect:
    @classmethod
    def user_connect(cls, current_user, user_id):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)               
            sql = "INSERT INTO user_connect_requests (requested_user_id, friend_id, requested_time, accept) VALUES (%s, %s, NOW(), 0)"
            values = (current_user, user_id,)
            cursor.execute(sql, values)

            dbConn.commit();
            id = cursor.lastrowid
            return id

        except Exception as e:
            print(f"Error: {e}")

        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def user_requests(cls, current_user):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)               
            sql = """
                SELECT *
                FROM user_connect_requests
                WHERE friend_id = %s AND accept = 0
            """
            cursor.execute(sql, (current_user,))
            user_connect_requests = cursor.fetchall()

            print(user_connect_requests)

            user_info = []
            for request in user_connect_requests:
                user_sql = "SELECT * FROM users WHERE id = %s"
                cursor.execute(user_sql, (request['requested_user_id'],))
                user_data = cursor.fetchone()
                combined_data = {**request, **user_data}
                user_info.append(combined_data)

            return user_info

        except Exception as e:
            print(f"Error: {e}")

        finally:
                dbConn.close()
                print("Release connection")

    @classmethod
    def user_accept(cls, current_userId, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            update_sql = "UPDATE user_connect_requests SET accept = 1, accepted_time = NOW() WHERE requested_user_id = %s AND friend_id = %s"
            insert_sql = "INSERT INTO user_connects (friend_id1, friend_id2, date_time) VALUES (%s, %s, NOW())"

            cursor.execute(update_sql, (user_id, current_userId))
            cursor.execute(insert_sql, (current_userId, user_id))
            dbConn.commit()

            return True

        except Exception as e:
            print("Error:", e)
            return None

        finally:
                dbConn.close()
                print("Connection released")

    @classmethod
    def user_cancel(cls, current_userId, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "UPDATE user_connect_requests SET cancelled_time = NOW() WHERE requested_user_id = %s AND friend_id = %s"

            cursor.execute(sql, (user_id, current_userId))
            dbConn.commit()

            return True

        except Exception as e:
            print("Error:", e)
            return None

        finally:
                dbConn.close()
                print("Connection released")

    @classmethod
    def user_friends(cls, current_user):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)               
            sql = """
                SELECT CASE
                    WHEN friend_id1 = %s THEN friend_id2
                    WHEN friend_id2 = %s THEN friend_id1
                    END AS friend_id
                FROM user_connects
                WHERE friend_id1 = %s OR friend_id2 = %s
            """
            cursor.execute(sql, (current_user, current_user, current_user, current_user))
            friend_ids = cursor.fetchall()

            user_info = []
            for friend_id in friend_ids:
                friend_id = friend_id['friend_id'] 
                user_sql = "SELECT * FROM users WHERE id = %s"
                cursor.execute(user_sql, (friend_id,))
                user_data = cursor.fetchone()
                user_info.append(user_data)

            return user_info

        except Exception as e:
            print(f"Error: {e}")

        finally:
                dbConn.close()
                print("Release connection")

    @classmethod
    def isAlreadyFriend(cls,user_id, current_user):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)               
            sql = """
                    SELECT *
                    FROM user_connects
                    WHERE (friend_id1 = %s AND friend_id2 = %s) OR (friend_id1 = %s AND friend_id2 = %s)
                """
            cursor.execute(sql, (user_id, current_user, current_user, user_id))
            user_info = cursor.fetchall()

            print(user_info)

            return user_info

        except Exception as e:
            print(f"Error: {e}")

        finally:
                dbConn.close()
                print("Release connection")



