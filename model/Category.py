from model.DatabasePool import DatabasePool

class Category:
    @classmethod
    def category(cls, name, image, description):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)
            sql="INSERT INTO categories (name, image, description) VALUES (%s, %s, %s)"

            cursor.execute(sql,(name, image, description,))
            dbConn.commit() 

            category_id = cursor.lastrowid
            return category_id

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def category_exist(cls, name):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT * FROM categories WHERE name = %s"
            cursor.execute(sql, (name,))

            existing_category = cursor.fetchone()

            return existing_category is not None

        finally:
            dbConn.close()

    @classmethod
    def get_all_categories(cls):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM categories"

            cursor.execute(sql)
            categories = cursor.fetchall()
            return categories

        finally:
            dbConn.close()
            print("Released connection")
