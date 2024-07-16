from model.DatabasePool import DatabasePool

class ClubLanguage:
    @classmethod
    def addClubLanguage(cls, club_id, language_ids):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            if language_ids is not None:
                # Insert new languages if provided
                sql_insert = "INSERT INTO club_languages (club_id, language_id) VALUES (%s, %s)"
                data = [(club_id, language_id) for language_id in language_ids]
                cursor.executemany(sql_insert, data)
                dbConn.commit()

            # Fetch the languages associated with the club
            select_sql = "SELECT * FROM club_languages WHERE club_id = %s"
            cursor.execute(select_sql, (club_id,))
            clubLanguage = cursor.fetchall()

            return clubLanguage

        finally:
            # Close the cursor before returning
            dbConn.close()
            print("Release connection")

    @classmethod
    def deleteClubLanguage(cls, club_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            select_sql = "DELETE FROM club_languages WHERE club_id = %s"
            cursor.execute(select_sql, (club_id,))
            dbConn.commit()

            rows_affected = cursor.rowcount
            return rows_affected

        finally:
            # Close the cursor before returning
            dbConn.close()
            print("Release connection")
