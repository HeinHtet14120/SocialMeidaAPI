from model.DatabasePool import DatabasePool

class CommentPost:

    @classmethod
    def check_post(cls,post_id):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT * FROM organizer_posts WHERE id = %s"
            cursor.execute(sql, (post_id,))

            existing_post = cursor.fetchone()

            return existing_post is not None

        finally:
            dbConn.close()

    @classmethod
    def add_comment(cls,post_id,user_id,comment):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "INSERT INTO post_comment (post_id, user_id, comment, date_time) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)"
            cursor.execute(sql,(post_id, user_id, comment,))
            dbConn.commit()

            comment_id = cursor.lastrowid
            return comment_id

        finally:
            dbConn.close()


    @classmethod
    def get_comments_by_post(cls,id,per_comment,offset):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)

            sql = """SELECT post_comment.*, users.username
                        FROM post_comment
                        JOIN users ON post_comment.user_id = users.id
                        WHERE post_comment.post_id = %s
                        ORDER BY 
                            post_comment.date_time DESC
                            LIMIT %s OFFSET %s
                    """

            cursor.execute(sql, (id,per_comment,offset))

            comments = cursor.fetchall()
            return comments

        finally:
            dbConn.close()
            print("release connection")

