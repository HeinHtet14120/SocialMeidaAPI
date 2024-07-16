from model.DatabasePool import DatabasePool
from model.GeoCity import GeoCity
import pandas as pd

class Event:
    @classmethod

    def get_user_events(cls, id, page, offset):

        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)

            sql = """
                    SELECT 
                        club_events.id AS event_id, 
                        club_events.*, 
                        clubs.id AS club_id, 
                        clubs.club_name
                    FROM 
                        event_attendees
                        JOIN club_events ON event_attendees.event_id = club_events.id AND event_attendees.club_id = club_events.club_id
                        JOIN clubs ON club_events.club_id = clubs.id
                    WHERE 
                        event_attendees.user_id = %s
                    ORDER BY 
                        club_events.created_date DESC
                    LIMIT %s  OFFSET %s
                
                """
               
            cursor.execute(sql, (id, page, offset))

            user_events = cursor.fetchall()

            return user_events

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def get_user_events_by_id(cls, id):

        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT 
                        club_events.id AS event_id, 
                        club_events.*, 
                        clubs.id AS club_id, 
                        clubs.club_name
                    FROM 
                        event_attendees
                        JOIN club_events ON event_attendees.event_id = club_events.id AND event_attendees.club_id = club_events.club_id
                        JOIN clubs ON club_events.club_id = clubs.id
                    WHERE 
                        event_attendees.user_id = %s
                    ORDER BY 
                        club_events.created_date DESC
                
                """
               
            cursor.execute(sql, (id,))
            user_events = cursor.fetchall()

            return user_events

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def get_club_events(cls, id, per_page, offset):

        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT 
                        club_events.*, 
                        clubs.club_name
                    FROM 
                        club_events
                        JOIN clubs ON club_events.club_id = clubs.id
                    WHERE 
                        club_events.club_id = %s
                    ORDER BY 
                        club_events.created_date DESC
                        LIMIT %s OFFSET %s
                """

            cursor.execute(sql, (id,per_page,offset))
            club_events = cursor.fetchall()

            return club_events

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def get_areacode_events(cls, areacode,per_page,offset):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT 
                        club_events.*, 
                        clubs.club_name
                    FROM 
                        club_events
                        JOIN clubs ON club_events.club_id = clubs.id
                    WHERE 
                        club_events.area_code = %s
                    ORDER BY 
                        club_events.created_date DESC
                        LIMIT %s OFFSET %s
                """
            cursor.execute(sql, (areacode,per_page,offset))
            areacode_events = cursor.fetchall()

            return areacode_events

        finally:
            dbConn.close()
            print("release connection")


    @classmethod
    def get_city_events(cls, city,per_page,offset):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT 
                        club_events.*, 
                        clubs.club_name
                    FROM 
                        club_events
                        JOIN clubs ON club_events.club_id = clubs.id
                    WHERE 
                        club_events.city LIKE %s
                    ORDER BY 
                        club_events.created_date DESC
                        LIMIT %s OFFSET %s
                """

            cursor.execute(sql, (city,per_page,offset))
            city_events = cursor.fetchall()

            return city_events

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def get_unregister_events(cls, user_id, page, offset):
        # , page, offset
        try:  
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                    SELECT DISTINCT 
                        club_events.*, club_events.id AS event_id, club_events.event_name,
                        clubs.club_name
                    FROM 
                        club_events
                        JOIN club_members ON club_events.club_id = club_members.club_id
                        JOIN clubs ON club_events.club_id = clubs.id
                    WHERE 
                        (club_members.user_id = %s
                        OR club_events.is_private = 0)
                        AND club_events.id NOT IN (
                            SELECT event_id FROM event_attendees WHERE user_id = %s
                        )
                    ORDER BY 
                        club_events.created_date DESC
                        LIMIT %s OFFSET %s
                    
                """
            #  LIMIT %s OFFSET %s
            #   page, offset
            cursor.execute(sql, (user_id, user_id, page, offset))
            events = cursor.fetchall()

            return events
        finally:
            dbConn.close()
            print("Connection released")


    @classmethod
    def get_event_info(cls, id):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                        SELECT club_events.*, clubs.club_name, clubs.image as club_image, count(events_and_users.user_id) as number_of_attendees
                        FROM club_events
                        LEFT JOIN clubs ON club_events.club_id = clubs.id
                        LEFT JOIN events_and_users ON events_and_users.event_id = club_events.id
                        WHERE club_events.id = %s
                        GROUP BY events_and_users.event_id
                    """

            cursor.execute(sql, (id,))
            event = cursor.fetchone()
            return event
        
        finally:
            dbConn.close()
            print("release connection")


    @classmethod
    def get_event_attendees(cls, event_id):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                        SELECT event_attendees.user_id, users.* 
                        FROM event_attendees
                        LEFT JOIN users ON event_attendees.user_id = users.id
                        WHERE event_attendees.event_id = %s
                    """
            cursor.execute(sql,(event_id,))
            user = cursor.fetchall() 

            return user
        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def get_event_cost(cls, id):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                        SELECT cost
                        FROM club_events
                        WHERE id = %s
                    """

            cursor.execute(sql, (id,))
            event_cost = cursor.fetchone()

            return event_cost
        
        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def get_nearby_events(cls, user_id, lat, long, distance, page, offset):
        cities = GeoCity.getNearbyCities(long, lat, distance)
        placeholders_cities= ', '.join("%s" for city in cities)
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)

            sql = """
                    SELECT club_events.id AS event_id, club_events.event_name as event_name, club_events.start_date as start_date,
                    club_events.end_date as end_date, club_events.address as address, club_events.area_code as area_code, 
                    club_events.building_name as building_name, club_events.city as city, 
                    club_events.country as country, club_events.max_size as max_size, club_events.cost as cost, club_events.currency as currency,
                    club_events.image as event_image, 
                    clubs.id AS club_id, clubs.club_name, clubs.image as club_image, COUNT(event_attendees.id) as number_of_attendees,
                    max_size - COUNT(event_attendees.id) as spot_left
                    FROM event_attendees JOIN club_events ON event_attendees.event_id = club_events.id
                    JOIN clubs ON club_events.club_id = clubs.id
                    JOIN club_members ON club_members.club_id = clubs.id
                    WHERE club_events.is_cancelled = 0 AND
                    (club_events.is_private = 0 OR club_members.user_id = %s) AND 
                    club_events.start_date > current_timestamp() AND
                    club_events.id not in (SELECT event_id from events_and_users where user_id = %s)
                    AND club_events.id not in (SELECT event_id from event_spots where spot_left < 1)
                    AND club_events.city in ("""+ placeholders_cities + """) 
                    GROUP BY event_attendees.event_id
                    ORDER BY club_events.created_date DESC
                    LIMIT %s  OFFSET %s;
                """
               

            parameters = (user_id, user_id) + tuple(cities) + (page, offset)
            cursor.execute(sql, parameters)
            events = cursor.fetchall() 
            return events

        finally:
            dbConn.close()
            print("release connection")
    
    @classmethod
    def saveForLater(cls, event_id, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql_insert = "INSERT INTO saved_events (user_id, event_id) VALUES (%s, %s)"
            cursor.execute(sql_insert, (user_id, event_id))
            dbConn.commit()

            # Fetch the inserted club event data
            return True

        finally:
            dbConn.close()
            print("Release connection")
    
    @classmethod
    def getSavedEvents(cls, user_id, page, offset):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)

            sql = """
                    SELECT club_events.id AS event_id, club_events.event_name as event_name, club_events.start_date as start_date,
                    club_events.end_date as end_date, club_events.address as address, club_events.area_code as area_code, 
                    club_events.building_name as building_name, club_events.city as city, 
                    club_events.country as country, club_events.max_size as max_size, club_events.cost as cost, 
                    club_events.currency as currency,
                    club_events.image as event_image, 
                    clubs.id AS club_id, clubs.club_name, clubs.image as club_image, COUNT(event_attendees.id) as number_of_attendees,
                    max_size - COUNT(event_attendees.id) as spot_left
                    FROM event_attendees JOIN club_events ON event_attendees.event_id = club_events.id
                    JOIN clubs ON club_events.club_id = clubs.id
                    JOIN club_members ON club_members.club_id = clubs.id
                    JOIN saved_events ON saved_events.event_id = club_events.id
                    WHERE saved_events.user_id = %s AND
                    club_events.is_cancelled = 0 AND
                    (club_events.is_private = 0 OR club_members.user_id = %s) AND 
                    club_events.start_date > current_timestamp()
                    AND club_events.id not in (SELECT event_id from event_spots where spot_left < 1)
                    GROUP BY event_attendees.event_id
                    ORDER BY club_events.created_date DESC
                    LIMIT %s  OFFSET %s;
                """
               
            cursor.execute(sql, (user_id, user_id, page, offset))
            events = cursor.fetchall() 
            return events

        finally:
            dbConn.close()
            print("release connection")

    @classmethod
    def getJoinedEvents(cls, user_id, page, offset):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)

            sql = """
                    SELECT club_events.id AS event_id, club_events.event_name as event_name, club_events.start_date as start_date,
                    club_events.end_date as end_date, club_events.address as address, club_events.area_code as area_code, 
                    club_events.building_name as building_name, club_events.city as city, 
                    club_events.country as country, club_events.max_size as max_size, club_events.cost as cost, 
                    club_events.currency as currency,
                    club_events.image as event_image, 
                    clubs.id AS club_id, clubs.club_name, clubs.image as club_image, COUNT(event_attendees.id) as number_of_attendees,
                    max_size - COUNT(event_attendees.id) as spot_left
                    FROM event_attendees JOIN club_events ON event_attendees.event_id = club_events.id
                    JOIN clubs ON club_events.club_id = clubs.id
                    JOIN club_members ON club_members.club_id = clubs.id
                    WHERE event_attendees.user_id = %s
                    AND club_events.user_id != %s
                    GROUP BY event_attendees.event_id
                    ORDER BY club_events.created_date DESC
                    LIMIT %s  OFFSET %s;
                """
               
            cursor.execute(sql, (user_id, user_id, page, offset))
            events = cursor.fetchall() 
            return events

        finally:
            dbConn.close()
            print("release connection")
            
    
    @classmethod
    def getOrganizedEvents(cls, user_id, page, offset):
        try:
            dbConn=DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");
        
            cursor = dbConn.cursor(dictionary=True)

            sql = """
                    SELECT club_events.id AS event_id, club_events.event_name as event_name, club_events.start_date as start_date,
                    club_events.end_date as end_date, club_events.address as address, club_events.area_code as area_code, 
                    club_events.building_name as building_name, club_events.city as city, 
                    club_events.country as country, club_events.max_size as max_size, club_events.cost as cost, 
                    club_events.currency as currency,
                    club_events.image as event_image, 
                    clubs.id AS club_id, clubs.club_name, clubs.image as club_image, COUNT(event_attendees.id) as number_of_attendees,
                    max_size - COUNT(event_attendees.id) as spot_left
                    FROM event_attendees JOIN club_events ON event_attendees.event_id = club_events.id
                    JOIN clubs ON club_events.club_id = clubs.id
                    JOIN club_members ON club_members.club_id = clubs.id
                    WHERE club_events.user_id = %s
                    GROUP BY event_attendees.event_id
                    ORDER BY club_events.created_date DESC
                    LIMIT %s  OFFSET %s;
                """
               
            cursor.execute(sql, (user_id, page, offset))
            events = cursor.fetchall() 
            return events

        finally:
            dbConn.close()
            print("release connection")
        


