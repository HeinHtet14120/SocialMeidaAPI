from model.DatabasePool import DatabasePool

class GroupCategories:
    @classmethod
    def groupCategories(cls, category_id, groups):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)
            sql="INSERT INTO group_categories (category_id, group_id) VALUES (%s, %s)"

            # Create a list of tuples for executemany
            data = [(category_id, group) for group in groups]

            cursor.executemany(sql, data)
            dbConn.commit() 

            group_id = cursor.lastrowid
            return group_id
        
        except Exception as e:
            print(f"Error executing query: {e}")

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def GetCategoriesByGroups(cls, group_ids):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            # Using the IN clause to check for multiple group_ids in a single query
            placeholders = ', '.join(['%s'] * len(group_ids))
            sql = f"""
                SELECT 
                    group_categories.group_id,
                    categories.*
                FROM group_categories
                JOIN categories ON group_categories.category_id = categories.id
                WHERE group_categories.group_id IN ({placeholders});
            """

            cursor.execute(sql, tuple(group_ids))
            results = cursor.fetchall()

            categories_by_group = {}
            for row in results:
                group_id = row['group_id']
                if group_id not in categories_by_group:
                    categories_by_group[group_id] = []

                category_info = {
                    'category_id': row['id'],
                    'category_name': row['name'],
                    'description': row['description'],
                    'category_image': row['image']
                }
                categories_by_group[group_id].append(category_info)

            return categories_by_group


        finally:
            dbConn.close()
            print("release connection")