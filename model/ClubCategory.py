from model.DatabasePool import DatabasePool

class ClubCategory:
    @classmethod
    def addClubCategory(cls, club_id, category_ids):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            if category_ids is not None:
                sql = "INSERT INTO club_categories (club_id, category_id) VALUES (%s, %s)"

                data = [(club_id, category_id) for category_id in category_ids]

                cursor.executemany(sql, data)
                dbConn.commit()

            select_sql = "SELECT * FROM club_categories WHERE club_id = %s"
            cursor.execute(select_sql, (club_id,))
            clubCategory = cursor.fetchall()


            return clubCategory

        finally:
            # Close the cursor before closing the connection
            dbConn.close()
            print("Release connection")

    @classmethod
    def deleteClubCategory(cls, club_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql = "DELETE FROM club_categories WHERE club_id = %s"
            cursor.execute(sql, (club_id,))
            dbConn.commit()

            rows_affected = cursor.rowcount
            return rows_affected

        finally:
            # Close the cursor before returning
            dbConn.close()
            print("Release connection")
