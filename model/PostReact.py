from model.DatabasePool import DatabasePool

class PostReact:
    @classmethod
    def addReact(cls, post_id, user_id, react_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "INSERT INTO post_reacts (post_id, user_id, react_id) values (%s, %s, %s)"

            cursor.execute(sql, (post_id, user_id, react_id))
            dbConn.commit()

            postReactID = cursor.lastrowid
            query = f"SELECT * FROM post_reacts WHERE id = {postReactID}"
            cursor.execute(query)
            postReact = cursor.fetchone()
            return postReact

        finally:
            dbConn.close()
            print("release connection")
            
    @classmethod
    def getReact(cls,post_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")
            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT COUNT(react_id) AS total_reacts FROM post_reacts WHERE post_id = %s
                """
            cursor.execute(sql,(post_id,))
            react = cursor.fetchall()
            return react
        finally:
            dbConn.close()
            print("Released connection")

    @classmethod
    def getPostReactByID(cls, post_id, page, offset):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")


            cursor = dbConn.cursor(dictionary=True)
            sql = """SELECT
                reacts.id AS react_id, reacts.react_description AS react_description,
                users.id AS user_id, users.username AS username, post_reacts.date_time AS react_time
                FROM post_reacts
                INNER JOIN users ON users.id = post_reacts.user_id
                INNER JOIN reacts ON reacts.id = post_reacts.react_id
                WHERE post_reacts.post_id = %s
                LIMIT %s
                OFFSET %s"""


            cursor.execute(sql, (post_id, page, offset))
            data = cursor.fetchall()
            return data

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def getReactTypes(cls,post_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT r.react_description, COUNT(pr.react_id) as count
                    FROM reacts r
                    LEFT JOIN post_reacts pr ON r.id = pr.react_id
                    WHERE pr.post_id = %s
                    GROUP BY r.react_description
                """
            
            cursor.execute(sql,(post_id,))
            react_counts = cursor.fetchall()
            
            # Convert the result to a dictionary
            react_types = {react['react_description']: react['count'] for react in react_counts}
            return react_types

        finally:
            dbConn.close()
            print("Released connection")
