from model.DatabasePool import DatabasePool

class UserSuggestCategory:
    @classmethod
    def userInfo(cls,user_id):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT username FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))

            userInfo = cursor.fetchone()
            return userInfo

        finally:
            dbConn.close()


    @classmethod
    def add_suggest_category(cls,user_id,username,category):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)
            sql="INSERT INTO suggested_categories (user_id, username, category_name) VALUES (%s, %s, %s)"

            cursor.execute(sql,(user_id, username, category,))
            dbConn.commit() 

            suggestedCategoryID = cursor.lastrowid
            return suggestedCategoryID

        finally:
            dbConn.close()
            print("release connection")


    @classmethod
    def get_all_suggested_categories(cls):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM suggested_categories"

            cursor.execute(sql)
            suggestedCategories = cursor.fetchall()
            return suggestedCategories

        finally:
            dbConn.close()
            print("Released connection")
            

    @classmethod
    def get_suggested_category(cls,suggestedCategory_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM suggested_categories WHERE id = %s"

            cursor.execute(sql,(suggestedCategory_id,))
            suggestedCategory = cursor.fetchall()
            return suggestedCategory
        
        except Exception as e:
            print(f"Error executing query: {e}")

        finally:
            dbConn.close()
            print("Released connection")
    
    @classmethod
    def update_suggested_categories(cls,user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql_update = "UPDATE suggested_categories SET is_provided = TRUE, approved_date = CURRENT_TIMESTAMP WHERE user_id = %s AND is_provided IS NULL" # Git Change
            cursor.execute(sql_update, (user_id,))
            dbConn.commit()

            sql_select = "SELECT * FROM suggested_categories WHERE user_id = %s AND is_provided = TRUE"
            cursor.execute(sql_select, (user_id,))
            
            updated_categories = cursor.fetchall()
            return updated_categories

        finally:
            dbConn.close()
            print("Released connection")
