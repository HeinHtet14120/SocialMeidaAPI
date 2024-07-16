from model.DatabasePool import DatabasePool

class UserPost:
    @classmethod
    def addUserPost(cls, user_id, subject, location, is_public):
        try:
            dbConn = DatabasePool.getConnection();
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql_insert = "INSERT INTO user_posts (user_id, subject, location, is_public) VALUES (%s, %s, %s, %s)"

            # Insert new post
            cursor.execute(sql_insert, (user_id, subject, location, is_public))
            dbConn.commit()

            # Fetch the inserted post data
            postId = cursor.lastrowid
            query = f"SELECT * FROM user_posts WHERE id = {postId}"
            cursor.execute(query)
            post = cursor.fetchone()
            return post

        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def getUserPost(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection();
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            # Fetch the inserted post data
            query = "SELECT * FROM user_posts WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            post = cursor.fetchall()
            return post

        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def getUserFriendPost(cls, user_id, page, offset):
        try:
            dbConn = DatabasePool.getConnection();
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            # Fetch the inserted post data
            query = """SELECT * FROM user_posts 
WHERE user_id IN (
    SELECT friend_id2 AS user_id FROM user_connects WHERE friend_id1 = %s
    UNION
    SELECT friend_id1 AS user_id FROM user_connects WHERE friend_id2 = %s
)
ORDER BY created_time DESC
LIMIT %s OFFSET %s"""
            cursor.execute(query, (user_id, user_id, page, offset))
            post = cursor.fetchall()
            return post

        finally:
            dbConn.close()
            print("Release connection")