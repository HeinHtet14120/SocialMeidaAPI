from model.DatabasePool import DatabasePool
import pandas as pd
import numpy as np

class UserSuggest:
    @classmethod
    def getSuggestedUsers(cls,user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql_pref = """
                   SELECT user_id, user_pref_location, category_id FROM hobby_meet_dev.user_pref;
                """

            cursor.execute(sql_pref,())
            df = pd.DataFrame(cursor.fetchall(), columns = ['user_id', 'user_pref_location', 'category_id'])
            locations = df[df['user_id'] == user_id].user_pref_location.unique().tolist()
            category_ids = df[df['user_id'] == user_id].category_id.unique().tolist()
            user_ids =  df[(df['user_pref_location'].isin(locations)) & (df['category_id'].isin(category_ids)) & (df['user_id'] != user_id)].user_id.unique().tolist()

            placeholder= '?' # For SQLite. See DBAPI paramstyle.
            placeholders= ', '.join(str(id) for id in user_ids)
            sql_users = """
                SELECT id, username,dob, country, profile_image, gender from users where id not in
                (SELECT friend_id1 FROM user_connects where friend_id2 = %s
                UNION
                SELECT friend_id2 FROM user_connects where friend_id1 = %s)
                and id in (%s)
                """
        
            cursor.execute(sql_users, (user_id, user_id, placeholders))
            users = cursor.fetchall()
            return users

        except Exception as e:
            print("Error while getting suggested users:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Released connection")
    @classmethod
    def getSuggestedEvents(cls, user_id, limit, offset): 
        try: 
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql_pref = """
                   SELECT user_id, user_pref_location, category_id FROM hobby_meet_dev.user_pref;
                """

            cursor.execute(sql_pref,())
            df = pd.DataFrame(cursor.fetchall(), columns = ['user_id', 'user_pref_location', 'category_id'])
            locations = df[df['user_id'] == user_id].user_pref_location.unique().tolist()
            category_ids = df[df['user_id'] == user_id].category_id.unique().tolist()
            print(locations)
            print(category_ids)
            placeholders_locations= ', '.join("%s" for location in locations)
            placeholders_categories= ', '.join("%s" for category in category_ids)
            
            sql_events = """
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
                    JOIN club_categories ON club_categories.club_id = clubs.id
                    WHERE club_events.is_cancelled = 0 AND
                    (club_events.is_private = 0 OR club_members.user_id = %s) AND 
                    club_events.start_date > current_timestamp() AND
                    club_events.id not in (SELECT event_id from events_and_users where user_id = %s)
                    AND club_events.id not in (SELECT event_id from event_spots where spot_left < 1)
                    AND club_events.city in ("""+ placeholders_locations + """) 
                    AND club_categories.category_id in ("""+ placeholders_categories + """)
                    GROUP BY event_attendees.event_id
                    ORDER BY club_events.created_date DESC
                    LIMIT %s  OFFSET %s;
                """
            print(sql_events)
            parameters = (user_id, user_id) + tuple(locations) + tuple(category_ids) + (limit, offset)
            cursor.execute(sql_events,  parameters)
            events = cursor.fetchall()
            return events

        except Exception as e:
            print("Error while getting suggested users:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Released connection")