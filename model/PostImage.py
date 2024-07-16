from model.DatabasePool import DatabasePool

class PostImage:
    @classmethod
    def addPostImage(cls, post_id, image_links):
        try:
            dbConn = DatabasePool.getConnection();
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            if image_links is not None:
                # Insert new languages if provided
                sql_insert = "INSERT INTO post_images (post_id, image_link) VALUES (%s, %s)"
                data = [(post_id, image_link) for image_link in image_links]
                cursor.executemany(sql_insert, data)
                dbConn.commit()

            # Fetch the inserted post data
            postId = cursor.lastrowid
            query = f"SELECT * FROM post_images WHERE id = {postId}"
            cursor.execute(query)
            post = cursor.fetchone()
            return post

        finally:
            dbConn.close()
            print("Release connection")
    
    @classmethod
    def getPostImages(cls,post_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT image_link FROM post_images WHERE post_id = %s
                """
            cursor.execute(sql,(post_id,))
            image = cursor.fetchall()
            return image

        finally:
            dbConn.close()
            print("Released connection")

    @classmethod
    def addUserPostImage(cls, post_id, photos):
        try:
            dbConn = DatabasePool.getConnection();
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            if photos is not None:
                # Insert new languages if provided
                sql_insert = "INSERT INTO user_post_photos (post_id, photo) VALUES (%s, %s)"
                data = [(post_id, image_link) for image_link in photos]
                cursor.executemany(sql_insert, data)
                dbConn.commit()

            # Fetch the inserted post data
            postId = cursor.lastrowid
            query = f"SELECT * FROM user_post_photos WHERE id = {postId}"
            cursor.execute(query)
            post = cursor.fetchone()
            return post

        finally:
            dbConn.close()
            print("Release connection")

