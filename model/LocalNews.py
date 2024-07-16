from model.DatabasePool import DatabasePool

class LocalNews:
    @classmethod
    def addNews(cls, user_id, title_en, overview_en, subject_en, category_en, title_fo, overview_fo, subject_fo, category_fo, main_pic, pic_1, pic_2, pic_3, pic_4, source, news_link, original_date, video_link):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = """INSERT INTO local_news 
                    (user_id, title_en, overview_en, subject_en, category_en, 
                    title_fo, overview_fo, subject_fo, category_fo, 
                    main_pic, pic_1, pic_2, pic_3, pic_4, 
                    source, news_link, video_link, original_date, created_time) VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"""

            data = (user_id, title_en, overview_en, subject_en, category_en, 
                    title_fo, overview_fo, subject_fo, category_fo, 
                    main_pic, pic_1, pic_2, pic_3, pic_4, source, news_link,  video_link, original_date)

            data = [None if value is None else value for value in data]

            cursor.execute(sql, data)
            dbConn.commit()
            newsId = cursor.lastrowid
            return newsId

        except Exception as e:
            print("Error while inserting news:", e)

        finally:
            dbConn.close()
            print("Release connection")

    @classmethod
    def get_news(cls, page, offset):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}")

            cursor = dbConn.cursor(dictionary=True)
            sql = "SELECT * FROM local_news ORDER BY created_time DESC LIMIT %s OFFSET %s"

            cursor.execute(sql, (page, offset))
            news = cursor.fetchall()
            return news

        finally:
            dbConn.close()
            print("Released connection")
