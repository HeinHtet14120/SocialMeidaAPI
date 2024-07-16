from model.DatabasePool import DatabasePool
import pandas as pd
import numpy as np

class GeoCity:
    @classmethod
    def getNearbyCities(cls, long, lat, distance):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """
                   SELECT c.name, c.latitude, c.longitude from geo_cities c;
                """

            cursor.execute(sql,)
            df = pd.DataFrame(cursor.fetchall(), columns = ['name', 'latitude', 'longitude'])
            df["latitude"] =df['latitude'].apply(lambda x: float(x.replace(',','.')))
            df["longitude"] =df['longitude'].apply(lambda x: float(x.replace(',','.')))

            lat = float(lat)
            long = float(long)
            df['distance'] = 6367 * np.arccos( np.cos( np.radians(lat) ) * np.cos( np.radians( df['latitude'] ) ) * np.cos( np.radians( df['longitude']) - np.radians(long) ) + np.sin( np.radians(lat) ) * np.sin( np.radians( df['latitude'] ) ) )
            return df[df['distance'] < distance]['name'].tolist()

        finally:
            cursor.close()
            dbConn.close()
            print("Released connection")