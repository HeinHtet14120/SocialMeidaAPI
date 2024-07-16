from model.DatabasePool import DatabasePool

class UserLeaveClub:
    @classmethod
    def check_user(cls,club_id,user_id):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT * FROM club_members WHERE club_id = %s AND user_id = %s"
            cursor.execute(sql, (club_id,user_id,))

            userInfo = cursor.fetchone()
            return userInfo

        finally:
            dbConn.close()

    @classmethod
    def delete_user(cls,club_id,user_id):
        try:
            dbConn = DatabasePool.getConnection()
            cursor = dbConn.cursor(dictionary=True)

            sql = "DELETE FROM club_members WHERE club_id = %s AND user_id = %s"
            cursor.execute(sql, (club_id,user_id,))
            dbConn.commit()

            return {'status': 'success', 'message': 'User deleted successfully'},200

        finally:
            dbConn.close()

    @classmethod
    def add_user_leave_club(cls, user_id, club_id, requested_by, reason):
        try:
            with DatabasePool.getConnection() as dbConn:
                db_Info = dbConn.connection_id
                print(f"Connected to {db_Info}")

                with dbConn.cursor(dictionary=True) as cursor:
                    sql = "INSERT INTO users_leave_clubs (user_id, club_id, requested_by, date_time, reason) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)"

                    cursor.execute(sql, (user_id, club_id, requested_by, reason,))
                    dbConn.commit()

                    leave_id = cursor.lastrowid
                    return leave_id

        except Exception as e:
            print(f"Error adding user leave club: {e}")
            return None
