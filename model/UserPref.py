from model.DatabasePool import DatabasePool
import pandas as pd

class UserPref:
    @classmethod
    def addAvailableTimes(cls, user_id, available_times):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor()

            data = []
            for day in available_times:
                day_of_week = day['dayOfWeek']
                timeslots = day['timeSlots']
                for timeslot in timeslots:
                    data.append((user_id,day_of_week, timeslot))

            sql = "INSERT INTO user_available_time (user_id, dayOfWeek, timeSlot) VALUES (%s, %s, %s)"

            cursor.executemany(sql, data)
            dbConn.commit()

            return True 
        
        except Exception as e:
            print("Error while inserting available times:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    @classmethod
    def addAvailableLocations(cls, user_id, locations):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor()

            data = [(user_id, location) for location in locations]

            sql = "INSERT INTO user_pref_location (user_id, location) VALUES (%s, %s)"

            cursor.executemany(sql, data)
            dbConn.commit()

            return True 
        
        except Exception as e:
            print("Error while inserting available locations:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    @classmethod
    def getAvailableLocations(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor()

            sql = "SELECT location from user_pref_location where user_id = %s;"

            cursor.execute(sql, (user_id,))
            locations = cursor.fetchall()
            return locations
        
        except Exception as e:
            print("Error while inserting available locations:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    @classmethod
    def getAvailableTimes(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql = "SELECT dayOfWeek, timeSlot from user_available_time where user_id = %s;"

            cursor.execute(sql, (user_id,))
            df = pd.DataFrame(cursor.fetchall(), columns = ['dayOfWeek', 'timeSlot'])
            timeSlots = df.groupby('dayOfWeek')['timeSlot'].apply(list).reset_index(name='timeSlots')
            return timeSlots
        
        except Exception as e:
            print("Error while inserting available locations:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")
    
    @classmethod
    def deleteAvailableLocations(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor()

            sql = "DELETE from user_pref_location where user_id = %s"

            cursor.execute(sql, (user_id,))
            dbConn.commit()

            rows_affected = cursor.rowcount
            return rows_affected
        
        except Exception as e:
            print("Error while inserting available locations:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    @classmethod
    def deleteAvailableTimes(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor()

            sql = "DELETE from user_available_time where user_id = %s"

            cursor.execute(sql, (user_id,))
            dbConn.commit()

            rows_affected = cursor.rowcount
            return rows_affected
        
        except Exception as e:
            print("Error while inserting available locations:", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

