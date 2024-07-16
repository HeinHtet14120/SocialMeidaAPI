from model.DatabasePool import DatabasePool

class UserCategory:
    @classmethod
    def user_category(cls, user_id, categories):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            if categories is not None:
                sql_insert = "INSERT INTO user_categories (user_id, category_id) VALUES (%s, %s)"
                data = [(user_id, category_id) for category_id in categories]
                cursor.executemany(sql_insert, data)
                dbConn.commit()

            return True

        except Exception as e:
            print(f"Error: {e}")

        finally:
            # Close the cursor before returning
            dbConn.close()
            print("Release connection")

    @classmethod
    def deleteUserCategory(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            delete_sql = "DELETE FROM user_categories WHERE user_id = %s"
            cursor.execute(delete_sql, (user_id,))
            dbConn.commit()

            rows_affected = cursor.rowcount
            return rows_affected

        finally:
            # Close the cursor before returning
            dbConn.close()
            print("Release connection")


    @classmethod
    def user_exists(cls, user_id):
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
    def get_user_categories(cls, user_id):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                SELECT user_categories.category_id, categories.name, categories.image , categories.description
                FROM user_categories 
                JOIN categories ON user_categories.category_id = categories.id
                WHERE user_id = %s
                """

            cursor.execute(sql,(user_id,))
            categories = cursor.fetchall()  # Fetch the user data

            return categories

        finally:
            dbConn.close()
            print("release connection")