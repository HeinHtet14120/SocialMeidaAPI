from model.DatabasePool import DatabasePool

class Country:
    @classmethod
    def addCountryInfo(cls, countries):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor()

            data = []

            print(countries)
            for country in countries:

                name = country['name']
                countrycode = country['countrycode']
                phcode = country['phcode']
                data.append((name,countrycode, phcode))

            sql = "INSERT INTO countries (country, countrycode, phcode) VALUES (%s, %s, %s)"

            cursor.executemany(sql, data)
            dbConn.commit()

            return True 
        
        except Exception as e:
            print("Error while inserting Countries :", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    @classmethod
    def getCountries(cls):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM countries"

            cursor.execute(sql)
            countries = cursor.fetchall()
            return countries
        
        except Exception as e:
            print("Error while getting Countries :", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")
    
    @classmethod
    def checkCurrency(cls, currency):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM countries where currency_code = %s"

            cursor.execute(sql, (currency,))
            currencies = cursor.fetchall()
            return cursor.rowcount > 0
        
        except Exception as e:
            print("Error while getting currency :", e)

        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")