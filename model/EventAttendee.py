from model.DatabasePool import DatabasePool

class EventAttendee:
    @classmethod
    def addEventAttendee(cls, event_id, user_id, ticket_number):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            
            sql = "INSERT INTO event_attendees (event_id, user_id, ticket_number) VALUES (%s, %s, %s)"
            cursor.execute(sql, (event_id, user_id, ticket_number))
            dbConn.commit()

            return True

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    # def attendee_exists(cls, club_id, user_id):
    def attendee_exists(cls, event_id, user_id):

        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            # sql = "SELECT * FROM event_attendees WHERE club_id = %s AND user_id = %s"
            sql = "SELECT * FROM event_attendees WHERE event_id = %s AND user_id = %s"

            cursor.execute(sql, (event_id, user_id))
            
            eventAttendee = cursor.fetchone()
            return bool(eventAttendee)

        finally:
            dbConn.close()
            print("release connection")
