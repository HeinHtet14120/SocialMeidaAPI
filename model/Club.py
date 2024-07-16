from model.DatabasePool import DatabasePool

class Club:
    @classmethod
    def addClub(cls, club_name, user_id, size, description, location, area_code, country, city, is_disabled, image):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql_insert = "INSERT INTO clubs (club_name, user_id, size, description, location, area_code, country, city, is_disabled, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            # Insert new club
            cursor.execute(sql_insert, (club_name, user_id, size, description, location, area_code, country, city, is_disabled, image))
            dbConn.commit()

            # Fetch the inserted club data
            clubId = cursor.lastrowid
            query = f"SELECT * FROM clubs WHERE id = {clubId}"
            cursor.execute(query)
            club = cursor.fetchone()
            return club

        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def updateClub(cls, club_name, size, description, location, area_code, country, city, image, id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """UPDATE clubs 
                        SET club_name = %s, 
                            size = %s, 
                            description = %s,
                            location = %s, 
                            area_code = %s, 
                            country = %s,
                            city = %s,
                            image= %s
                        WHERE id = %s"""

            cursor.execute(sql, (club_name, size, description, location, area_code, country, city, image, id))
            dbConn.commit()

            query = "SELECT * FROM clubs WHERE id = %s"
            cursor.execute(query, (id,))
            updated_club = cursor.fetchone()
            return updated_club

        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def getClubsById(cls, id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM clubs WHERE id = %s"

            cursor.execute(sql, (id,))
            club = cursor.fetchone()
            return club
        
        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def getClubAndUserID(cls, id, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM clubs WHERE id = %s AND user_id = %s"
            dbConn.commit()
            cursor.execute(sql, (id, user_id))
            club = cursor.fetchone()
            return club
        
        finally:
            dbConn.close()
            print("Release connection")
        
    @classmethod
    def getClubsByMemberID(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """SELECT clubs.id, clubs.club_name, clubs.size, clubs.location,
                    clubs.area_code, clubs.country, clubs.city, clubs.description, clubs.image
                    FROM clubs
                    INNER JOIN club_members ON clubs.id = club_members.club_id
                    WHERE club_members.user_id = %s AND clubs.is_disabled = 0"""
            
            cursor.execute(sql, (user_id,))
            clubs = cursor.fetchall()
            return clubs
        
        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def getClubsByOrganizerID(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """SELECT clubs.id, clubs.club_name, clubs.size, clubs.location,
                    clubs.area_code, clubs.country, clubs.city, clubs.description, clubs.image
                    FROM clubs
                    INNER JOIN club_members ON clubs.id = club_members.club_id
                    INNER JOIN user_sub_roles ON club_members.role_id = user_sub_roles.id
                    WHERE club_members.user_id = %s and club_members.role_id = 1"""
            
            cursor.execute(sql, (user_id,))
            clubs = cursor.fetchall()
            return clubs
        
        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def getClubsByAreaCode(cls, code):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """SELECT id, club_name, size, location,
                    area_code, country, city, description, image
                    FROM clubs
                    WHERE area_code = %s AND clubs.is_disabled = 0"""
            
            cursor.execute(sql, (code,))
            clubs = cursor.fetchall()
            return clubs
        
        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def getClubsByCity(cls, city):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """SELECT id, club_name, size, location,
                    area_code, country, city, description, image
                    FROM clubs
                    WHERE city LIKE %s AND clubs.is_disabled = 0"""
            
            cursor.execute(sql, ('%' + city + '%',))
            clubs = cursor.fetchall()
            return clubs
        
        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def getClubsSuggested(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """SELECT
                    clubs.id,
                    clubs.club_name,
                    clubs.size,
                    clubs.location,
                    clubs.area_code,
                    clubs.country,
                    clubs.city,
                    clubs.description,
                    clubs.image,
                    COUNT(club_members.user_id) AS member_count
                FROM
                    clubs
                LEFT JOIN
                    club_members ON clubs.id = club_members.club_id AND club_members.user_id = %s
                WHERE
                    club_members.user_id IS NULL AND clubs.is_disabled = 0
                GROUP BY
                    clubs.id, clubs.club_name, clubs.size, clubs.location,
                    clubs.area_code, clubs.country, clubs.city, clubs.description
                ORDER BY
                    member_count DESC"""
            
            cursor.execute(sql, (user_id,))
            clubs = cursor.fetchall()
            return clubs
        
        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def disableClub(cls, id):
        dbConn = None
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "UPDATE clubs SET is_disabled = 1 WHERE id = %s"

            cursor.execute(sql, (id,))
            dbConn.commit()

            return id

        except Exception as e:
            print("Error:", e)

        finally:
            dbConn.close()
            print("Connection released")


    @classmethod
    def getJoinedClubs(cls, user_id, page, offset):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)


            sql = f"""
                SELECT clubs.* 
                FROM clubs 
                JOIN club_members ON clubs.id = club_members.club_id
                WHERE club_members.user_id = %s AND club_members.role_id = 2
                LIMIT %s  OFFSET %s;
                """

            cursor.execute(sql, (user_id,page,offset,))
            clubs = cursor.fetchall()
            return clubs

        finally:
            dbConn.close()
            print("Release connection")