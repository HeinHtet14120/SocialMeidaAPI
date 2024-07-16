from model.DatabasePool import DatabasePool

class Group:
    @classmethod
    def group(cls, name, image):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)
            sql="INSERT INTO `groups` (name,image) VALUES (%s,%s)"

            cursor.execute(sql,(name,image,))
            dbConn.commit() 

            group_id = cursor.lastrowid
            return group_id

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def group_exist(cls, name):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT * FROM `groups` WHERE name = %s"
            cursor.execute(sql, (name,))

            existing_group = cursor.fetchone()

            return existing_group is not None

        finally:
            dbConn.close()

    @classmethod
    def get_all_groups(cls):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM `groups`"

            cursor.execute(sql)
            groups = cursor.fetchall()
            return groups

        finally:
            dbConn.close()
            print("Released connection")


    @classmethod
    def get_group(cls, name):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT id FROM `groups` WHERE name = %s"
            cursor.execute(sql, (name,))

            group = cursor.fetchone()

            return group

        finally:
            dbConn.close()

    @classmethod
    def get_groupbyID(cls, IDs):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            # Construct the SQL query with string formatting
            sql = "SELECT id FROM `groups` WHERE id IN ({})".format(', '.join(map(str, IDs)))

            cursor.execute(sql)
            group_ids = cursor.fetchall()

            return group_ids

        except Exception as e:
            print(f"Error executing query: {e}")

        finally:
            dbConn.close()
            print("Release connection")

