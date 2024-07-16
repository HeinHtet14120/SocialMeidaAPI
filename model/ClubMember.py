from model.DatabasePool import DatabasePool

class ClubMember:
    @classmethod
    def addClubMember(cls, club_id, user_id, role_id=None):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            role_id = role_id if role_id is not None else 1
            
            sql = "INSERT INTO club_members (club_id, user_id, role_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (club_id, user_id, role_id))
            dbConn.commit()

            # After insertion, fetch the inserted club data based on some identifier
            clubMemberID = cursor.lastrowid
            query = f"SELECT * FROM club_members WHERE id = {clubMemberID}"
            cursor.execute(query)
            clubMember = cursor.fetchone()
            return clubMember

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def club_member_exists(cls, club_id, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT role_id FROM club_members WHERE club_id = %s AND user_id = %s"
            dbConn.commit()
            cursor.execute(sql, (club_id, user_id))
            clubMember = cursor.fetchone()
            return clubMember

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def getClubMembersByClubId(cls, id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """SELECT club_members.user_id, users.username, user_sub_roles.role
                    FROM users
                    JOIN club_members ON users.id = club_members.user_id
                    JOIN user_sub_roles ON club_members.role_id = user_sub_roles.id
                    WHERE club_members.club_id = %s;"""

            cursor.execute(sql, (id,))
            clubMembers = cursor.fetchall()
            return clubMembers
        
        finally:
            dbConn.close()
            print("Release connection")

