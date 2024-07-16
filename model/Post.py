from model.DatabasePool import DatabasePool

class Post:
    @classmethod
    def addPost(cls, organizer_id, club_id, post_subject):
        try:
            dbConn = DatabasePool.getConnection();
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql_insert = "INSERT INTO organizer_posts (organizer_id, club_id, post_subject) VALUES (%s, %s, %s)"

            # Insert new post
            cursor.execute(sql_insert, (organizer_id, club_id, post_subject))
            dbConn.commit()

            # Fetch the inserted post data
            postId = cursor.lastrowid
            query = f"SELECT * FROM organizer_posts WHERE id = {postId}"
            cursor.execute(query)
            post = cursor.fetchone()
            return post

        finally:
            dbConn.close()
            print("Release connection")
    
    @classmethod
    def getPosts(cls,club_id,per_page,offset):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT * FROM organizer_posts WHERE club_id = %s
                    ORDER BY 
                        organizer_posts.last_updated DESC
                        LIMIT %s OFFSET %s
                """

            cursor.execute(sql,(club_id,per_page,offset))
            posts = cursor.fetchall()
            return posts

        finally:
            dbConn.close()
            print("Released connection")



        
    @classmethod
    def getPost(cls, post_id):
        try:
            dbConn = DatabasePool.getConnection();
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            # Fetch the inserted post data
            query = "SELECT * FROM organizer_posts WHERE id = %s"
            cursor.execute(query, (post_id,))
            post = cursor.fetchone()
            return post

        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def delete_post(cls, post_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "DELETE FROM organizer_posts where id = %s"
            cursor.execute(sql, (post_id,))
            dbConn.commit()

            rows_affected = cursor.rowcount
            return rows_affected

        finally:
            dbConn.close()
            print("release connection")

