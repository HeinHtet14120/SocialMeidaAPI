from model.DatabasePool import DatabasePool
from passlib.hash import sha256_crypt

class EmailVerify:
    @classmethod
    def save_otp_email(cls, email, otp, datetime, is_verified):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)

            sql = "INSERT INTO email_verification ( email_address, otp, expired_time, is_verified ) VALUES (%s, %s, %s, %s)"
            
            cursor.execute(sql, (email, otp, datetime, is_verified))
            dbConn.commit()

            return email

        except Exception as e:
            print("Error while inserting payment:", e)
            
        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")

    @classmethod
    def verify_otp(cls, email, entered_otp, datetime):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            query = "SELECT * FROM email_verification WHERE email_address = %s AND expired_time >= %s AND is_verified = 0"
            cursor.execute(query, (email, datetime))
            user = cursor.fetchone()

            if user:
                hashed_otp = user['otp']
                if sha256_crypt.verify(entered_otp, hashed_otp):
                    update_query = "UPDATE email_verification SET is_verified = %s WHERE email_address = %s"
                    cursor.execute(update_query, (1, email))
                    dbConn.commit()
                    return True
                else:
                    return False
            else:
                return False
            
        except Exception as e:
            print("Error while verifying OTP :", e)
            
        finally:
            cursor.close()
            dbConn.close()
            print("Connection released")
