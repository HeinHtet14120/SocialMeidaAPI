from model.DatabasePool import DatabasePool

class ClubEvent:
    @classmethod
    def addClubEvent(cls, club_id, user_id, event_name, description, start_datetime, end_datetime, address, building_name, area_code, city, state, country, is_private, max_size, cost, currency, image = None):
        image = None if image == "" else image
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql_insert = "INSERT INTO club_events (club_id, user_id, event_name, description, start_date, end_date, address, building_name, area_code, city, state, country, is_private,  max_size, cost, currency, image) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_insert, (club_id, user_id, event_name, description, start_datetime, end_datetime, address, building_name, area_code, city, state, country, is_private,  max_size, cost, currency, image))
            dbConn.commit()

            # Fetch the inserted club event data
            clubEventId = cursor.lastrowid
            query = f"SELECT * FROM club_events WHERE id = {clubEventId}"
            cursor.execute(query)
            clubEvent = cursor.fetchone()
            return clubEvent

        finally:
            dbConn.close()
            print("Release connection")

    